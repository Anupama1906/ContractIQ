import os
import tempfile
import streamlit as st
from evaluator import evaluate_contract

st.set_page_config(page_title="Contract Risk Analyzer", layout="centered")
st.title("📄 Contract Risk Analyzer")

uploaded_file = st.file_uploader("Upload a contract PDF", type=["pdf"])

if uploaded_file is not None:

    with st.spinner("Analyzing contract... ⏳"):

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        try:
            result = evaluate_contract(temp_path)

            # ✅ SAFETY CHECK (VERY IMPORTANT)
            if not result:
                st.error("❌ No result returned from analysis.")
            else:
                # ✅ SCORE
                st.subheader("📊 Final Risk Score")
                st.metric("Score", f"{result.get('final_score', 0):.2f}")

                # ✅ REPORT
                st.subheader("📝 Risk Report")
                st.write(result.get("final_report", "No report generated."))

        except Exception as e:
            st.error(f"❌ Error while analyzing contract:\n{e}")

        finally:
            # Clean temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)