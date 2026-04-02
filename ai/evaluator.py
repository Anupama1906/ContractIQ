import chromadb
from typing import TypedDict, Annotated, List, Dict
import operator
import os
import json
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_deepseek import ChatDeepSeek
<<<<<<< HEAD
from helper import anonymizer
from docling.document_converter import DocumentConverter

DEEPSEEK_API_KEY = 'sk-8e731aed93e94681809bc4eef201d8da'


PERSIST_DIR = r"/chroma_hemas"
=======
from helper import anonymizer, pdf_to_markdown
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

load_dotenv()


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


PERSIST_DIR = r"./chroma_hemas"
>>>>>>> senindu
COLLECTION_NAME = "check_collection"

class ContractState(TypedDict):
    text: str
    rules_context: str
    rules_by_type: Dict[str, str]
    comments: Annotated[List[BaseMessage], operator.add]

    legal_risk: float
    financial_risk: float
    compliance_risk: float
    operational_risk: float
    data_risk: float
    termination_risk: float

    final_score: float
    final_report: str


class LegalOut(BaseModel):
    comment: str = Field(description="Brief explanation of legal risks identified in the contract.")
    legal_risk: float = Field(description="Legal risk score between 0 and 1.")

class FinancialOut(BaseModel):
    comment: str = Field(description="Brief explanation of financial risks identified in the contract.")
    financial_risk: float = Field(description="Financial risk score between 0 and 1.")

class ComplianceOut(BaseModel):
    comment: str = Field(description="Brief explanation of compliance risks identified in the contract.")
    compliance_risk: float = Field(description="Compliance risk score between 0 and 1.")

class OperationalOut(BaseModel):
    comment: str = Field(description="Brief explanation of operational risks identified in the contract.")
    operational_risk: float = Field(description="Operational risk score between 0 and 1.")

class DataOut(BaseModel):
    comment: str = Field(description="Brief explanation of data/privacy risks identified in the contract.")
    data_risk: float = Field(description="Data risk score between 0 and 1.")

class TerminationOut(BaseModel):
    comment: str = Field(description="Brief explanation of termination/exit risks identified in the contract.")
    termination_risk: float = Field(description="Termination risk score between 0 and 1.")

class Summarizer(BaseModel):
    risk_analyzed_report: str = Field(description="Overall markdown risk report.")
    final_score: float = Field(description="Final aggregated risk score between 0 and 1.")


<<<<<<< HEAD
def evaluate_contract(source: str):
    SOURCE=source
    converter = DocumentConverter()
    result = converter.convert(SOURCE)
    text = result.document.export_to_markdown()


=======

def evaluate_contract_(source: str):
    
    """
    End-to-end pipeline to analyze a contract and generate a structured risk assessment.

    This function performs:
        1. PDF → markdown text conversion
        2. Text cleaning and normalization
        3. Retrieval of relevant risk rules from ChromaDB (RAG)
        4. Multi-agent risk evaluation using LangGraph
        5. Aggregation of results into a final risk score and report

    The pipeline produces a complete ContractState object containing:
        - extracted contract text (anonymized)
        - retrieved rule context
        - individual risk scores across multiple dimensions
        - aggregated final score and report

    Args:
        source (str): Path to the contract PDF file.

    Returns:
        ContractState: A dictionary-like object containing:
            - text (str): Anonymized contract text
            - rules_context (str): General retrieved rules
            - rules_by_type (Dict[str, str]): Rules grouped by risk category
            - comments (List[BaseMessage]): Explanations from each agent

            - legal_risk (float)
            - financial_risk (float)
            - compliance_risk (float)
            - operational_risk (float)
            - data_risk (float)
            - termination_risk (float)

            - final_score (float): Aggregated risk score (0 to 1)
            - final_report (str): Final generated risk analysis report
    """
    
    text = pdf_to_markdown(source)
    text = " ".join(text.split())
    
>>>>>>> senindu
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        api_key=DEEPSEEK_API_KEY
    )


    def format_rules(result):
<<<<<<< HEAD
=======
        
        """
        Format retrieved vector database results into a readable rule string.

        Converts documents and metadata into structured text that can be
        passed to LLM agents as contextual input.

        Args:
            result (dict): Output from ChromaDB query containing documents and metadata.

        Returns:
            str: Formatted string of rules with associated metadata.
        """
        
>>>>>>> senindu
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]

        formatted = []
        for d, m in zip(docs, metas):
            formatted.append(
                f"rule: {d}\n"
                f"risk_type: {m.get('risk_type')}\n"
                f"severity: {m.get('severity')}\n"
                f"clause_type: {m.get('clause_type')}\n"
            )
        return "\n".join(formatted)


    def retrieve_rules(state: ContractState):
<<<<<<< HEAD
=======
        
        """
        Retrieve relevant rules from the vector database for the given contract.

        Performs:
            - General rule retrieval (top-k similar rules)
            - Risk-type specific retrieval (legal, financial, etc.)

        Args:
            state (ContractState): Current graph state containing contract text.

        Returns:
            dict:
                - rules_context (str): General retrieved rules
                - rules_by_type (dict): Rules grouped by risk type
        """
        
>>>>>>> senindu
        query = state["text"]

        general = collection.query(
            query_texts=[query],
<<<<<<< HEAD
            n_results=8
=======
            n_results=5
>>>>>>> senindu
        )
        rules_context = format_rules(general)

        rules_by_type = {}
        for risk in ["legal", "financial", "compliance", "operational", "data", "termination"]:
            try:
                result = collection.query(
                    query_texts=[query],
<<<<<<< HEAD
                    n_results=5,
=======
                    n_results=3,
>>>>>>> senindu
                    where={"risk_type": risk}
                )
                rules_by_type[risk] = format_rules(result)
            except Exception:
                rules_by_type[risk] = ""

        return {
            "rules_context": rules_context,
            "rules_by_type": rules_by_type
        }


    def legal_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are a legal risk expert.

<<<<<<< HEAD
    Use retrieved structured rules:
    - Focus on risk_type = legal
    - Use severity to weigh importance
    - Use clause_type for context
    - Compare retrieved rules against the contract

    Return:
    - legal_risk (0 to 1)
    - short explanation
    """),
=======
            IMPORTANT CONTEXT CHECK:
            - Legal risk is ALWAYS applicable
            - But severity must depend on:
            - ambiguity
            - conflicting clauses
            - missing critical terms

            Do NOT exaggerate:
            - minor ambiguity ≠ high risk

            Return:
            - legal_risk (0 to 1)
            - explanation grounded in clauses
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(LegalOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("legal", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "legal_risk": result.legal_risk,
            "comments": [HumanMessage(content=f"[LEGAL] {result.comment}")]
        }


    def financial_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
<<<<<<< HEAD
            ("system",
            """You are a financial risk expert.

    Use retrieved structured rules:
    - Focus on risk_type = financial
    - Use severity to weigh importance
    - Look for payment, penalties, pricing, liability exposure

    Return:
    - financial_risk (0 to 1)
    - short explanation
    """),
=======
           ("system",
            """You are a financial risk expert.

            IMPORTANT CONTEXT CHECK:
            - Only assign HIGH risk if financial exposure is clearly harmful
            - Standard pricing/royalties ≠ high risk automatically

            Focus on:
            - penalties
            - liability exposure
            - payment uncertainty

            Return:
            - financial_risk (0 to 1)
            - explanation with justification
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(FinancialOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("financial", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "financial_risk": result.financial_risk,
            "comments": [HumanMessage(content=f"[FINANCIAL] {result.comment}")]
        }


    def compliance_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are a compliance risk expert.

<<<<<<< HEAD
    Use retrieved structured rules:
    - Focus on risk_type = compliance
    - Use severity to weigh importance
    - Look for regulatory duties, confidentiality, privacy, and governance obligations

    Return:
    - compliance_risk (0 to 1)
    - short explanation
    """),
=======
            IMPORTANT CONTEXT CHECK:
            - Determine if regulatory/compliance obligations are relevant
            - If contract is purely commercial (no regulated domain) → assign LOW score

            Only evaluate compliance risk IF:
            - legal/regulatory obligations exist
            - licensing, governance, or regulatory constraints exist

            Avoid:
            - assuming compliance risk without evidence

            Return:
            - compliance_risk (0 to 1)
            - explanation with applicability reasoning
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(ComplianceOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("compliance", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "compliance_risk": result.compliance_risk,
            "comments": [HumanMessage(content=f"[COMPLIANCE] {result.comment}")]
        }


    def operational_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are an operational risk expert.

<<<<<<< HEAD
    Use retrieved structured rules:
    - Focus on risk_type = operational
    - Use severity to weigh importance
    - Look for delivery risk, performance obligations, dependencies, SLAs, service interruptions

    Return:
    - operational_risk (0 to 1)
    - short explanation
    """),
=======
            IMPORTANT CONTEXT CHECK:
            - Only flag operational risk if execution depends on uncertain conditions

            Look for:
            - vague obligations
            - dependencies (marketing, third parties)
            - unclear deliverables

            Return:
            - operational_risk (0 to 1)
            - explanation
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(OperationalOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("operational", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "operational_risk": result.operational_risk,
            "comments": [HumanMessage(content=f"[OPERATIONAL] {result.comment}")]
        }


    def data_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are a data protection and privacy risk expert.

<<<<<<< HEAD
    Use retrieved structured rules:
    - Focus on risk_type = data
    - Use severity to weigh importance
    - Look for personal data handling, privacy, confidentiality, breach, retention, access control

    Return:
    - data_risk (0 to 1)
    - short explanation
    """),
=======
            IMPORTANT CONTEXT CHECK:
            - First determine if the contract involves personal data, customer data, or system/data access
            - If NO → data risk is NOT APPLICABLE → assign LOW score (0–0.2)
            - Do NOT flag missing data clauses if data is not involved

            Only evaluate risk IF:
            - personal data is processed
            - customer/user data is handled
            - system/database access is granted

            Use retrieved structured rules:
            - Focus on risk_type = data
            - Use severity to weigh importance

            Return:
            - data_risk (0 to 1)
            - explanation including:
            - whether data risk is applicable
            - justification
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(DataOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("data", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "data_risk": result.data_risk,
            "comments": [HumanMessage(content=f"[DATA] {result.comment}")]
        }


    def termination_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
            """You are a termination risk expert.

<<<<<<< HEAD
    Use retrieved structured rules:
    - Focus on risk_type = termination
    - Use severity to weigh importance
    - Look for exit clauses, termination rights, notice periods, renewal lock-ins, penalties

    Return:
    - termination_risk (0 to 1)
    - short explanation
    """),
=======
            IMPORTANT CONTEXT CHECK:
            - Termination risk is relevant in most contracts
            - But HIGH risk only if:
            - unfair termination rights
            - very short cure periods
            - heavy penalties

            Return:
            - termination_risk (0 to 1)
            - explanation
            """),
>>>>>>> senindu
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])

        chain = prompt | llm.with_structured_output(TerminationOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("termination", state["rules_context"]),
            "contract": state["text"]
        })

        return {
            "termination_risk": result.termination_risk,
            "comments": [HumanMessage(content=f"[TERMINATION] {result.comment}")]
        }


    def evaluator(state: ContractState):
<<<<<<< HEAD
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a contract risk evaluator."),
=======
        
        """
        Aggregate individual risk scores and generate a final risk report.

        Uses an LLM to:
            - Summarize agent comments
            - Combine risk scores
            - Produce a final structured report

        Args:
            state (ContractState): Current state containing all risk scores and comments.

        Returns:
            dict:
                - final_score (float): Aggregated risk score (0 to 1)
                - final_report (str): Generated risk analysis report
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a contract risk evaluator. 
             DO NOT EXAGGERATE.
             Do NOT assign HIGH risk unless:
            - clause creates financial loss OR
            - legal enforceability issue OR
            - operational failure risk"""),
>>>>>>> senindu
            ("user",
            """COMMENTS:
            {comments}

            RISK SCORES:
            {risk}

            Generate:
            - final report (100–200 words)
            - final_score (0 to 1)
            """)
        ])

        chain = prompt | llm.with_structured_output(Summarizer)

        risk_json = json.dumps({
            "legal_risk": state["legal_risk"],
            "financial_risk": state["financial_risk"],
            "compliance_risk": state["compliance_risk"],
            "operational_risk": state["operational_risk"],
            "data_risk": state["data_risk"],
            "termination_risk": state["termination_risk"]
        }, indent=2)

        result = chain.invoke({
            "comments": state["comments"],
            "risk": risk_json
        })

        return {
            "final_score": result.final_score,
            "final_report": result.risk_analyzed_report
        }


    graph = StateGraph(ContractState)

    graph.add_node("retrieve", retrieve_rules)
    graph.add_node("legal", legal_agent)
    graph.add_node("financial", financial_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("operational", operational_agent)
    graph.add_node("data", data_agent)
    graph.add_node("termination", termination_agent)
    graph.add_node("evaluate", evaluator)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "legal")
    graph.add_edge("legal", "financial")
    graph.add_edge("financial", "compliance")
    graph.add_edge("compliance", "operational")
    graph.add_edge("operational", "data")
    graph.add_edge("data", "termination")
    graph.add_edge("termination", "evaluate")
    graph.add_edge("evaluate", END)

    app = graph.compile()

<<<<<<< HEAD
    anonymized_text = anonymizer(text)
    anonymized_text = text
=======
    anonymized_text, entity_map = anonymizer(text)
>>>>>>> senindu

    final = app.invoke({
        "text": anonymized_text,
        "rules_context": "",
        "rules_by_type": {},
        "comments": [],
        "legal_risk": 0.0,
        "financial_risk": 0.0,
        "compliance_risk": 0.0,
        "operational_risk": 0.0,
        "data_risk": 0.0,
        "termination_risk": 0.0,
        "final_score": 0.0,
        "final_report": ""
    })

    print("=" * 50)
    print(final["final_report"])
    print("=" * 50)
<<<<<<< HEAD
    print("FINAL SCORE:", final["final_score"])
    
    
    
SOURCE = "C:/Users/Lenovo/Downloads/Contracts_dataset_1/full_contract_pdf/Part_II/Hosting/CENTRACKINTERNATIONALINC_10_29_1999-EX-10.3-WEB SITE HOSTING AGREEMENT.PDF"
    
evaluate_contract(SOURCE)
=======
    print("FINAL RISK SCORE:", final["final_score"])
    
    return final
    
    
def evaluate_contract(source: str):
    """
    End-to-end pipeline to analyze a contract and generate a structured risk assessment.

    Returns:
        ContractState: Final merged state after streaming execution.
    """

    # -----------------------------
    # 1. LOAD + CLEAN TEXT
    # -----------------------------
    text = pdf_to_markdown(source)
    text = " ".join(text.split())

    anonymized_text, entity_map = anonymizer(text)

    # -----------------------------
    # 2. LOAD VECTOR DB
    # -----------------------------
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    # -----------------------------
    # 3. INIT LLM
    # -----------------------------
    llm = ChatDeepSeek(
        model="deepseek-chat",
        temperature=0,
        api_key=DEEPSEEK_API_KEY
    )

    # -----------------------------
    # 4. HELPERS
    # -----------------------------
    def format_rules(result):
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]

        formatted = []
        for d, m in zip(docs, metas):
            formatted.append(
                f"rule: {d}\n"
                f"risk_type: {m.get('risk_type')}\n"
                f"severity: {m.get('severity')}\n"
                f"clause_type: {m.get('clause_type')}\n"
            )
        return "\n".join(formatted)

    def retrieve_rules(state: ContractState):
        query = state["text"]

        general = collection.query(query_texts=[query], n_results=5)
        rules_context = format_rules(general)

        rules_by_type = {}
        for risk in ["legal", "financial", "compliance", "operational", "data", "termination"]:
            try:
                result = collection.query(
                    query_texts=[query],
                    n_results=3,
                    where={"risk_type": risk}
                )
                rules_by_type[risk] = format_rules(result)
            except Exception:
                rules_by_type[risk] = ""

        return {
            "rules_context": rules_context,
            "rules_by_type": rules_by_type
        }

    # -----------------------------
    # 5. AGENTS (UNCHANGED)
    # -----------------------------
    def legal_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a legal risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(LegalOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("legal", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "legal_risk": result.legal_risk,
            "comments": [HumanMessage(content=f"[LEGAL] {result.comment}")]
        }

    def financial_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a financial risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(FinancialOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("financial", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "financial_risk": result.financial_risk,
            "comments": [HumanMessage(content=f"[FINANCIAL] {result.comment}")]
        }

    def compliance_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a compliance risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(ComplianceOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("compliance", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "compliance_risk": result.compliance_risk,
            "comments": [HumanMessage(content=f"[COMPLIANCE] {result.comment}")]
        }

    def operational_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an operational risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(OperationalOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("operational", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "operational_risk": result.operational_risk,
            "comments": [HumanMessage(content=f"[OPERATIONAL] {result.comment}")]
        }

    def data_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(DataOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("data", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "data_risk": result.data_risk,
            "comments": [HumanMessage(content=f"[DATA] {result.comment}")]
        }

    def termination_agent(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a termination risk expert."),
            ("user", "RULES:\n{rules}\n\nCONTRACT:\n{contract}")
        ])
        chain = prompt | llm.with_structured_output(TerminationOut)
        result = chain.invoke({
            "rules": state["rules_by_type"].get("termination", state["rules_context"]),
            "contract": state["text"]
        })
        return {
            "termination_risk": result.termination_risk,
            "comments": [HumanMessage(content=f"[TERMINATION] {result.comment}")]
        }

    def evaluator(state: ContractState):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a contract risk evaluator."),
            ("user", "COMMENTS:\n{comments}\n\nRISK:\n{risk}")
        ])
        chain = prompt | llm.with_structured_output(Summarizer)

        risk_json = json.dumps({
            "legal_risk": state["legal_risk"],
            "financial_risk": state["financial_risk"],
            "compliance_risk": state["compliance_risk"],
            "operational_risk": state["operational_risk"],
            "data_risk": state["data_risk"],
            "termination_risk": state["termination_risk"]
        })

        result = chain.invoke({
            "comments": state["comments"],
            "risk": risk_json
        })

        return {
            "final_score": result.final_score,
            "final_report": result.risk_analyzed_report
        }

    # -----------------------------
    # 6. GRAPH
    # -----------------------------
    graph = StateGraph(ContractState)

    graph.add_node("retrieve", retrieve_rules)
    graph.add_node("legal", legal_agent)
    graph.add_node("financial", financial_agent)
    graph.add_node("compliance", compliance_agent)
    graph.add_node("operational", operational_agent)
    graph.add_node("data", data_agent)
    graph.add_node("termination", termination_agent)
    graph.add_node("evaluate", evaluator)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "legal")
    graph.add_edge("legal", "financial")
    graph.add_edge("financial", "compliance")
    graph.add_edge("compliance", "operational")
    graph.add_edge("operational", "data")
    graph.add_edge("data", "termination")
    graph.add_edge("termination", "evaluate")
    graph.add_edge("evaluate", END)

    app = graph.compile()

    # -----------------------------
    # 7. STREAM EXECUTION 🔥
    # -----------------------------
    initial_state = {
        "text": anonymized_text,
        "rules_context": "",
        "rules_by_type": {},
        "comments": [],
        "legal_risk": 0.0,
        "financial_risk": 0.0,
        "compliance_risk": 0.0,
        "operational_risk": 0.0,
        "data_risk": 0.0,
        "termination_risk": 0.0,
        "final_score": 0.0,
        "final_report": ""
    }

    state = initial_state.copy()

    for step in app.stream(initial_state):
        node = list(step.keys())[0]
        updates = step[node]

        print(f"\n🔹 Node: {node}")

        state.update(updates)

        for k, v in updates.items():
            if k != "comments":
                print(f"{k}: {v}")

    print("\n" + "=" * 50)
    print(state["final_report"])
    print("=" * 50)
    print("FINAL RISK SCORE:", state["final_score"])

    return state
    
#SOURCE = "C:/Users/Lenovo/Downloads/Contracts_dataset_1/full_contract_pdf/Part_II/Hosting/CENTRACKINTERNATIONALINC_10_29_1999-EX-10.3-WEB SITE HOSTING AGREEMENT.PDF"
    
#evaluate_contract(SOURCE)
>>>>>>> senindu
