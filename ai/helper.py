import chromadb
from thefuzz import fuzz
from thefuzz import process
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from pathlib import Path
import os
import uuid
import json
from typing import List
from pydantic import BaseModel, Field
from thefuzz import fuzz
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def pdf_to_markdown(source: str):
    
    """
    Convert a PDF document into markdown text using Docling.

    Args:
        source (str): Path to the input PDF file.

    Returns:
        str: Extracted markdown-formatted text from the PDF.
    """
    
    converter = DocumentConverter()
    result = converter.convert(source)
    text = result.document.export_to_markdown()
    return text


def anonymizer(text: str):
    
    """
    Perform PII anonymization on input text using Presidio with a BERT-based NER model.

    The function detects entities such as PERSON, ORGANIZATION, EMAIL, etc.,
    replaces them with consistent placeholders (e.g., <PERSON_1>), and ensures
    similar entities are mapped to the same placeholder using fuzzy matching.

    Args:
        text (str): Raw contract text.

    Returns:
        Tuple[str, dict]:
            - Anonymized text with placeholders.
            - Mapping of original entity text to placeholders.
    """
  
    configuration = {
        "nlp_engine_name": "transformers",
        "models": [
            {
                "lang_code": "en",
                "model_name": {
                    "spacy": "en_core_web_sm",
                    "transformers": "dslim/bert-base-NER"
                }
            }
        ]
    }

    def find_similar_entity(entity_text, entity_map, threshold=80):
        choices = list(entity_map.keys())
        closest = process.extractOne(entity_text, choices)
        if closest and closest[1] > threshold:
            return closest[0]
        return None


    def remove_overlaps(results):
        results = sorted(results, key=lambda x: (x.start, -(x.end - x.start)))
        filtered = []

        for r in results:
            if not any(not (r.end <= f.start or r.start >= f.end) for f in filtered):
                filtered.append(r)

        return filtered


    def normalize_text(t):
        return t.strip().lower().replace(".", "")


    entity_types = [
        "CREDIT_CARD",
        "CRYPTO",
        "EMAIL_ADDRESS",
        "IBAN_CODE",
        "IP_ADDRESS",
        "MAC_ADDRESS",
        "NRP",
        "LOCATION",
        "PERSON",
        "PHONE_NUMBER",
        "MEDICAL_LICENSE",
        "URL",
        "ORGANIZATION"
    ]

    entity_counters = {}
    entity_map = {}


    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine = provider.create_engine()
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

    results = analyzer.analyze(text=text, language="en")

    results = remove_overlaps(results)

    results = sorted(results, key=lambda x: x.start, reverse=True)


    for r in results:
        if r.entity_type == "DATE_TIME" or r.score < 0.5:
            continue

        entity_text = text[r.start:r.end]
        entity_type = "UNCATEGORIZED_PII" if r.entity_type not in entity_types else r.entity_type

        similar = None
        similar = find_similar_entity(entity_text, entity_map)

        if similar:
            placeholder = entity_map[similar]
        else:
            if entity_type not in entity_counters:
                entity_counters[entity_type] = 0

            entity_counters[entity_type] += 1
            entity_map[entity_text] = f"<{entity_type}_{entity_counters[entity_type]}>"
            placeholder = entity_map[entity_text]

        text = text[:r.start] + placeholder + text[r.end:]

    reversed_map = {v: k for k, v in entity_map.items()}
    return text, reversed_map


def original_markdown_anonymized_map(source: str):
    original_markdown = pdf_to_markdown(source)
    anonymized_markdown, entity_map = anonymizer(original_markdown)
    return json.dumps({"pdf_text": original_markdown, "anonymized_text": anonymized_markdown, "entity_map": entity_map})

class Rule(BaseModel):
    '''
    Return dictionary for Rules with keys:
        -rule
        -risk_type
        -severity
        -clause_type
    '''
    rule: str = Field(
        description="A concise, generalized rule describing a risk pattern in contracts. It should follow a cause-effect format, e.g., 'Absence of liability cap increases financial risk exposure'."
    )
    risk_type: str = Field(
        description="Category of risk associated with the rule. Must be one of: legal, financial, compliance, operational, data, or termination."
    )
    severity: str = Field(
        description="Estimated impact level of the risk. Must be one of: low, medium, or high."
    )
    clause_type: str = Field(
        description="The type of contract clause the rule relates to, such as confidentiality, liability, termination, data_protection, intellectual_property, or general."
    )


class RulesList(BaseModel):
    '''
    Returns the list of Rules

    '''
    rules: List[Rule] = Field(
        description="List of Rules for each with; rule, risk_type, severity and clause_type"
    )




def extract_rules(contract):
    
    """
    Extract generalized legal risk rules from a contract using an LLM.

    The function uses a structured prompt with DeepSeek to generate reusable,
    abstracted rules categorized by risk type, severity, and clause type.

    Args:
        contract (str): Contract text (can be anonymized).

    Returns:
        List[Rule]: List of extracted structured Rule objects.
                    Returns an empty list if extraction fails.
    """
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=GROQ_API_KEY
    )
    
    prompt_to_rules = ChatPromptTemplate.from_messages([
        ("system", """You are a legal risk analysis expert.

            Your task is to extract GENERALIZED and REUSABLE, MOST IMPORTANT 5 risk rules from the given contract by the user at below.

            IMPORTANT INSTRUCTIONS:
            - Ignore all names, organizations, and identifiers (they may be PII anonymized for fullfil data privacy)
            - Focus ONLY on legal clauses, obligations, and conditions
            - Do NOT copy text directly — generalize the rule
            - Each rule must describe a cause → risk effect relationship
            - Keep rules concise (1 sentence each)
            - Avoid duplicates or very similar rules

            RISK TYPES (use ONLY these values):
            - legal
            - financial
            - compliance
            - operational
            - data
            - termination

            SEVERITY LEVELS:
            - low → minor impact
            - medium → moderate risk
            - high → significant legal/financial exposure

            CLAUSE TYPES (examples):
            - confidentiality
            - liability
            - termination
            - data_protection
            - intellectual_property
            - dispute_resolution
            - usage
            - general

            OUTPUT FORMAT:
            Return ONLY a valid JSON object in given format (structured llm output):

            DO NOT include:
            - explanations
            - markdown
            - extra text

            """),
        ("user", "CONTRACT: {contract}")

    ])

    # 🔥 Structured chain
    chain = prompt_to_rules | llm.with_structured_output(RulesList)

    try:
        response = chain.invoke({
            "contract": contract[:90000]
        })

        return response.rules

    except Exception as e:
        print("⚠️ Structured extraction failed:", e)
        return []



def deduplicate_rules(rules, threshold=75):
    
    """
    Remove duplicate or highly similar rules using fuzzy string matching.

    Rules are compared using token_set_ratio, and only unique rules above
    the similarity threshold are retained.

    Args:
        rules (List[Rule]): List of extracted rules.
        threshold (int, optional): Similarity threshold (0–100). Default is 75.

    Returns:
        List[Rule]: Deduplicated list of rules.
    """

    unique = []
    seen = []

    for r in rules:
        text = r.rule.lower()

        duplicate = False
        for s in seen:
            if fuzz.token_set_ratio(text, s) > threshold:
                duplicate = True
                break

        if not duplicate:
            unique.append(r)
            seen.append(text)

    return unique


def convert_to_documents(rules):

    """
    Convert Rule objects into LangChain Document format for vector storage.

    Each rule is stored as a document with associated metadata including
    risk type, severity, and clause type.

    Args:
        rules (List[Rule]): List of structured Rule objects.

    Returns:
        List[Document]: List of LangChain Document objects.
    """
    
    docs = []

    for r in rules:
        docs.append(
            Document(
                page_content=r.rule,
                metadata={
                    "type": "rule",
                    "risk_type": r.risk_type,
                    "severity": r.severity,
                    "clause_type": r.clause_type
                }
            )
        )

    return docs


def build_vectorstore(docs, db_path="./chroma_hemas"):
    
    """
    Build or update a persistent Chroma vector database with semantic deduplication.

    The function checks for existing similar rules using vector similarity before
    inserting new ones, preventing duplication at the semantic level.

    Args:
        docs (List[Document]): List of documents to store.
        db_path (str, optional): Path to persist the Chroma database.

    Returns:
        chromadb.Collection: The updated Chroma collection instance.
    """

    persist_dir = db_path
    os.makedirs(persist_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(name="check_collection")

    new_texts = []
    new_metas = []
    new_ids = []

    for d in docs:

        duplicate = False

        # 🔥 semantic dedup using Chroma
        if collection.count() > 0:
            results = collection.query(
                query_texts=[d.page_content],
                n_results=1
            )

            if "distances" in results and len(results["distances"][0]) > 0:
                distance = results["distances"][0][0]

                if distance < 0.6:   # 🔥 threshold
                    duplicate = True

        if not duplicate:
            new_texts.append(d.page_content)
            new_metas.append(d.metadata)
            new_ids.append(str(uuid.uuid4()))

    if len(new_texts) > 0:
        collection.add(
            ids=new_ids,
            documents=new_texts,
            metadatas=new_metas
        )
        print(f"✅ Added {len(new_texts)} new rules")
    else:
        print("⚠️ No new rules added (all duplicates)")

    return collection



def process_contract(text):
    
    """
    Build or update a persistent Chroma vector database with semantic deduplication.

    The function checks for existing similar rules using vector similarity before
    inserting new ones, preventing duplication at the semantic level.

    Args:
        docs (List[Document]): List of documents to store.
        db_path (str, optional): Path to persist the Chroma database.

    Returns:
        chromadb.Collection: The updated Chroma collection instance.
    """

    print("🔍 Extracting rules...")
    rules = extract_rules(text)

    print(f"Raw rules: {len(rules)}")

    rules = deduplicate_rules(rules)
    print(f"After deduplication: {len(rules)}")

    docs = convert_to_documents(rules)
    collection = build_vectorstore(docs)
    
    return collection



def feed_rules(docs_path: str):
    
    """
    Process multiple contract text files from a directory and populate the RAG database.

    Each file is read, anonymized, and passed through the rule extraction pipeline.

    Args:
        docs_path (str): Path to directory containing contract text files.

    Returns:
        None
    """
    
    directory_path = Path(docs_path)
    files_list = [entry.name for entry in directory_path.iterdir() if entry.is_file()]

    for i, file in enumerate(files_list):
        with open(f"{directory_path}/{file}", "r", encoding="utf-8") as f:
            text = f.read()
            anonymized_text = anonymizer(text)
            process_contract(anonymized_text)
            print("*"*30)
            print(f.name)
            print("\n")


def check_rules(db_path: str="./chroma_hemas"):
    
    """
    Process multiple contract text files from a directory and populate the RAG database.

    Each file is read, anonymized, and passed through the rule extraction pipeline.

    Args:
        docs_path (str): Path to directory containing contract text files.

    Returns:
        None
    """
    
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(name="check_collection")
    data = collection.get()
    docs = data["documents"]
    metas = data["metadatas"]

    for i in range(len(docs)):
        print(f"\nRule {i+1}:")
        print("Text:", docs[i])
        print("Metadata:", metas[i])



#SOURCE = "C:/Users/Lenovo/Downloads/Contracts_dataset_1/full_contract_pdf/Part_II/Hosting/CENTRACKINTERNATIONALINC_10_29_1999-EX-10.3-WEB SITE HOSTING AGREEMENT.PDF"

#print(original_markdown_anonymized_map(source=SOURCE))


        
        