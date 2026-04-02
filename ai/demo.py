import os
import tempfile
import streamlit as st
import json

from evaluator import evaluate_contract

st.set_page_config(page_title="Contract Risk Analyzer", layout="centered")
st.title("📄 Contract Risk Analyzer")

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_file = st.file_uploader("Upload a contract PDF", type=["pdf"])

# -----------------------------
# BUTTON
# -----------------------------
analyze_clicked = st.button("🚀 Analyze Risk")

# -----------------------------
# RUN ONLY WHEN BUTTON CLICKED
# -----------------------------
if uploaded_file is not None and analyze_clicked:

    with st.spinner("Analyzing contract... ⏳"):

        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        try:
            # -----------------------------
            # STREAM UI CONTAINERS
            # -----------------------------
            st.subheader("⚡ Live Risk Analysis")

            legal_box = st.empty()
            financial_box = st.empty()
            compliance_box = st.empty()
            operational_box = st.empty()
            data_box = st.empty()
            termination_box = st.empty()

            score_box = st.empty()
            report_box = st.empty()

            # -----------------------------
            # STREAM EXECUTION
            # -----------------------------
            for step in evaluate_contract(temp_path):

                agent = step.get("agent")
                score = step.get("risk_score", 0)
                comments = step.get("comments", [])

                text = f"**Score:** {score:.2f}\n\n" + "\n".join(comments)

                if agent == "legal":
                    legal_box.markdown(f"### ⚖️ Legal\n{text}")

                elif agent == "financial":
                    financial_box.markdown(f"### 💰 Financial\n{text}")

                elif agent == "compliance":
                    compliance_box.markdown(f"### 📜 Compliance\n{text}")

                elif agent == "operational":
                    operational_box.markdown(f"### ⚙️ Operational\n{text}")

                elif agent == "data":
                    data_box.markdown(f"### 🔐 Data\n{text}")

                elif agent == "termination":
                    termination_box.markdown(f"### 🛑 Termination\n{text}")

                elif agent == "evaluate":
                    score_box.subheader("📊 Final Risk Score")
                    score_box.metric("Score", f"{score:.2f}")

                    report_box.subheader("📝 Risk Report")
                    report_box.write(step.get("final_report", ""))

        except Exception as e:
            st.error(f"❌ Error while analyzing contract:\n{e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


# -----------------------------
# WARNING MESSAGE
# -----------------------------
elif uploaded_file is None and analyze_clicked:
    st.warning("⚠️ Please upload a PDF before analyzing.")