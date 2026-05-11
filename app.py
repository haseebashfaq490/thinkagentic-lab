import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import base64
import os
import PyPDF2

load_dotenv()

st.set_page_config(page_title="ThinkAgentic Lab", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 2rem; max-width: 1300px; }

    .stApp {
        background-color: #080C13;
        background-image: radial-gradient(circle at 50% -20%, rgba(19, 197, 123, 0.15) 0%, #080C13 60%);
        color: #FFFFFF;
    }

    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #FFFFFF !important;
        line-height: 1.6;
    }
    div[data-testid="stMarkdownContainer"] p span,
    div[data-testid="stMarkdownContainer"] li span {
        color: #FFFFFF !important;
    }

    .think-white { color: #FFFFFF !important; }
    .think-green { color: #13C57B !important; }
    .think-gray  { color: #6B7280 !important; font-weight: 300; font-size: 2.5rem; }

    div[data-testid="stTabs"] > div > div > div { overflow: visible !important; }
    div[data-baseweb="tab_list"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 12px;
        padding: 5px 10px !important;
        border: 1px solid #1E293B !important;
        gap: 15px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
    }
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
    }
    button[data-baseweb="tab"] p {
        color: #9CA3AF !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease;
    }
    button[data-baseweb="tab"]:hover p { color: #FFFFFF !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(19, 197, 123, 0.1) !important;
        border: 1px solid rgba(19, 197, 123, 0.3) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: #13C57B !important;
        font-weight: 800 !important;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
        background-color: #0F172A !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    input, textarea { color: #FFFFFF !important; }

    /* Fix dropdown selected text */
    div[data-baseweb="select"] span {
        color: #FFFFFF !important;
    }
    div[data-baseweb="select"] div {
        color: #FFFFFF !important;
    }

    /* Fix placeholder text visibility */
    textarea::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }
    input::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
    }

    /* Fix number input */
    input[type="number"] {
        color: #FFFFFF !important;
    }

    /* Fix selectbox label text */
    .stSelectbox label, .stNumberInput label, .stTextArea label {
        color: #E2E8F0 !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background-color: #0F172A !important;
        border: 2px dashed #374151 !important;
        border-radius: 12px;
        padding: 20px;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #13C57B !important;
        background-color: rgba(19, 197, 123, 0.05) !important;
    }
    [data-testid="stFileUploaderDropzone"] div,
    [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stFileUploaderDropzone"] span,
    .st-emotion-cache-1wivap2 { color: #FFFFFF !important; }

    [data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        border: 1px solid #13C57B !important;
        color: #13C57B !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
    }
    [data-testid="stBaseButton-secondary"]:hover {
        background-color: rgba(19, 197, 123, 0.1) !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: #13C57B !important;
        color: #080C13 !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        border: none !important;
        padding: 0.8rem 0 !important;
        transition: all 0.3s ease !important;
        margin-top: 10px;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 20px rgba(19, 197, 123, 0.4) !important;
        transform: translateY(-2px) !important;
        background-color: #16D686 !important;
    }

    .stChatMessage {
        background-color: rgba(15, 23, 42, 0.6);
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    table { width: 100%; border-collapse: collapse; margin-top: 10px; border-radius: 8px; overflow: hidden;}
    th {
        background-color: rgba(19, 197, 123, 0.15) !important;
        color: #13C57B !important;
        text-align: left;
        padding: 14px !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 0.85rem;
    }
    td {
        padding: 14px !important;
        border-bottom: 1px solid #1E293B;
        color: #F8FAFC !important;
        font-size: 1rem;
    }
    tr:hover td { background-color: rgba(255, 255, 255, 0.05); }
    h3 { color: #FFFFFF !important; font-family: 'Inter', sans-serif !important; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def extract_pdf_text(uploaded_file):
    if uploaded_file is not None:
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception:
            return None
    return None

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ==========================================
# HEADER
# ==========================================
st.markdown("""
<h1 style='text-align: center; font-weight: 900; font-size: 4.5rem; margin-bottom: 0; letter-spacing: -0.05em;'>
    <span class='think-white'>Think</span><span class='think-green'>Agentic</span>
    <span class='think-gray'> Lab</span>
</h1>
<p style='text-align: center; color: #9CA3AF; font-size: 1.15rem; margin-bottom: 3rem;'>
    Test our autonomous systems in real-time. Powered by Llama 3.
</p>
""", unsafe_allow_html=True)

# ==========================================
# SYSTEM CONFIGURATION
# ==========================================
with st.expander("⚙️ System Configuration & Enterprise Context"):
    st.markdown("<p style='color: #9CA3AF;'>Upload enterprise data or policies here to contextualize the Document Intelligence and Concierge agents.</p>", unsafe_allow_html=True)
    uploaded_context = st.file_uploader("Upload Business Policy Document (PDF)", type=["pdf"], label_visibility="collapsed")
    context_text = extract_pdf_text(uploaded_context)
    if context_text:
        st.success("✅ Enterprise Context Loaded Securely into Agent Memory.")

# ==========================================
# TABS
# ==========================================
tabs = st.tabs([
    "📑 Claims Intelligence",
    "🔍 Visual QA",
    "🧠 Document Intelligence",
    "🎧 Support Concierge",
    "🤖 Automation Architect"
])

# ==========================================
# TAB 1: CLAIMS INTELLIGENCE + FRAUD DETECTION
# ==========================================
with tabs[0]:
    st.markdown("<h3 style='color: #13C57B; margin-bottom: 1.5rem;'>Agentic OCR & Fraud Detection Workspace</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        claim_img = st.file_uploader("Upload Claim Document", type=["jpg", "png"], key="claims_upload")
        if claim_img:
            st.image(claim_img, use_container_width=True, caption="Source Document Preview")
            btn_claim = st.button("Initialize Agentic Extraction", type="primary", use_container_width=True)
        else:
            btn_claim = False

    with col2:
        if btn_claim and claim_img:
            with st.chat_message("assistant", avatar="⚙️"):
                st.write("Initializing visual parsing and fraud analysis protocol...")
                try:
                    b64 = encode_image(claim_img)
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": """Analyze this claim document and produce TWO sections:

SECTION 1 — DATA EXTRACTION:
Output a professional Markdown table with columns 'Data Point' and 'Value'.
Extract: Name, Policy Number, Claim Amount, Date, Incident Description, Provider/Claimant details, and any other relevant fields visible.

SECTION 2 — FRAUD RISK ASSESSMENT:
Output a second Markdown table with columns 'Fraud Indicator' and 'Finding'.
Analyze the document for the following fraud signals:
- Inconsistencies in dates, amounts, or names
- Missing or suspicious fields
- Unusual claim patterns or inflated amounts
- Document quality issues (signs of tampering or alteration)
- Mismatched provider/claimant information

Then give a final FRAUD VERDICT as one of:
✅ LIKELY AUTHENTIC — with a 1-sentence reason
⚠️ REQUIRES REVIEW — with a 1-sentence reason
🚨 HIGH FRAUD RISK — with a 1-sentence reason"""},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                            ]
                        }],
                        temperature=0.0
                    )
                    st.write("Extraction and fraud analysis complete:")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Agent Error: {e}")
        else:
            with st.chat_message("assistant", avatar="⚙️"):
                st.write("Awaiting document upload. Agent will extract structured data and run fraud risk assessment simultaneously.")

# ==========================================
# TAB 2: VISUAL QA
# ==========================================
with tabs[1]:
    st.markdown("<h3 style='color: #13C57B; margin-bottom: 1.5rem;'>Automated Defect Inspection</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        defect_img = st.file_uploader("Upload Product Scan", type=["jpg", "png"], key="defect_upload")
        if defect_img:
            st.image(defect_img, use_container_width=True, caption="Physical Asset Scan")
            btn_qa = st.button("Run Anomaly Detection", type="primary", use_container_width=True)
        else:
            btn_qa = False

    with col2:
        if btn_qa and defect_img:
            with st.chat_message("assistant", avatar="👁️"):
                st.write("Scanning surface for physical anomalies...")
                try:
                    b64 = encode_image(defect_img)
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Perform physical defect inspection. Output ONLY a professional Markdown table detailing 'Defect Type', 'Location', and 'Severity (1-10)'."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]}]
                    )
                    st.write("Inspection sequence complete. Anomaly report generated:")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Agent Error: {e}")
        else:
            with st.chat_message("assistant", avatar="👁️"):
                st.write("Visual QA Agent online. Upload a product image to begin real-time defect detection.")

# ==========================================
# TAB 3: DOCUMENT INTELLIGENCE
# ==========================================
with tabs[2]:
    st.markdown("<h3 style='color: #13C57B; margin-bottom: 1.5rem;'>Semantic Data Extraction</h3>", unsafe_allow_html=True)

    uploaded_rag_doc = st.file_uploader("1. Upload Target Document (PDF)", type=["pdf"], key="rag_upload")
    query = st.text_input("2. Enter Semantic Query:", "Extract all compliance liabilities, strict deadlines, and financial penalties mentioned in this document.")
    btn_rag = st.button("Execute Semantic Search", type="primary", use_container_width=True)

    if btn_rag:
        if not uploaded_rag_doc:
            st.error("⚠️ Please upload a document first.")
        else:
            with st.chat_message("assistant", avatar="🧠"):
                st.write("Vectorizing document and parsing semantic relationships...")
                doc_text = extract_pdf_text(uploaded_rag_doc)
                if not doc_text:
                    st.error("Failed to read PDF text. Ensure the document is not password protected.")
                else:
                    truncated_text = doc_text[:20000]
                    system_msg = "Extract the requested info. Present findings strictly in a professional Markdown table with columns 'Entity/Clause', 'Details', and 'Action Required'."
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": f"Document:\n{truncated_text}\n\nQuery: {query}"}
                        ]
                    )
                    st.write("Analysis complete. Findings extracted:")
                    st.markdown(response.choices[0].message.content)

# ==========================================
# TAB 4: SUPPORT CONCIERGE
# ==========================================
with tabs[3]:
    st.markdown("<h3 style='color: #13C57B; margin-bottom: 1.5rem;'>Omnichannel Autonomous Agent</h3>", unsafe_allow_html=True)

    dummy_support_ticket = "\"Hi, I need to schedule a maintenance team for our industrial HVAC unit at the downtown Toronto facility for next Wednesday. Also, order two replacement HEPA filters to be shipped there. Escalate if Wednesday isn't available.\""
    support_query = st.text_area("Simulate Incoming Customer Transcript:", value=dummy_support_ticket, height=120)
    btn_support = st.button("Execute Autonomous Resolution", type="primary", use_container_width=True)

    if btn_support:
        with st.chat_message("assistant", avatar="🎧"):
            st.write("Analyzing intent, extracting entities, and triggering backend APIs...")
            system_msg = "You are an Enterprise Support Agent. Output a professional Markdown table detailing operations: 'Intent Detected', 'Entities Extracted', 'Backend API Simulated (e.g. POST /v1/orders)', and 'Escalated (Yes/No)'. Below it, draft the empathetic customer response."
            if context_text:
                system_msg += f"\nCompany Policy context: {context_text}"
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": support_query}
                    ]
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Agent Error: {e}")

# ==========================================
# TAB 5: AUTOMATION ARCHITECT
# ==========================================
with tabs[4]:
    st.markdown("<h3 style='color: #13C57B; margin-bottom: 1.5rem;'>AI Automation Architect & ROI Engine</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color: #9CA3AF; margin-bottom: 1.5rem;'>
    Describe any business process or operational challenge. The agent will design a custom multi-agent automation architecture,
    identify every step that can be eliminated or automated, and calculate your projected ROI and time savings.
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        industry = st.selectbox(
            "Industry",
            ["Financial Services", "Insurance", "Healthcare", "Manufacturing",
             "Retail & E-Commerce", "Legal", "Government", "Real Estate",
             "Supply Chain & Logistics", "Other"],
            label_visibility="visible"
        )
        team_size = st.selectbox(
            "Team Size Affected",
            ["1-5 people", "6-20 people", "21-50 people", "51-200 people", "200+ people"],
            label_visibility="visible"
        )
        hourly_rate = st.number_input(
            "Average Employee Hourly Rate (CAD $)",
            min_value=20,
            max_value=500,
            value=75,
            step=5
        )

    with col2:
        process_desc = st.text_area(
            "Describe your current process or pain point in detail:",
            height=180,
            placeholder="e.g. Our team manually reviews 200+ insurance claims per day. Each claim requires opening a PDF, extracting 12 data fields, cross-referencing our database, assigning a risk score, and routing to the right adjuster. This takes ~25 minutes per claim and has a 4% error rate causing costly rework..."
        )

    btn_architect = st.button("Design My Automation Architecture ⚡", type="primary", use_container_width=True)

    if btn_architect:
        if not process_desc.strip():
            st.error("⚠️ Please describe your business process first.")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write("Analyzing process inefficiencies and designing optimal agent architecture...")
                try:
                    prompt = f"""You are a Senior Agentic AI Solutions Architect at a top enterprise AI firm. 
A potential client has described their business process. Your job is to design a comprehensive automation solution and calculate their ROI.

CLIENT DETAILS:
- Industry: {industry}
- Team Size Affected: {team_size}
- Average Hourly Rate: CAD ${hourly_rate}
- Process Description: {process_desc}

Produce a detailed report with EXACTLY these sections:

## Process Inefficiency Analysis
A Markdown table with columns 'Current Step', 'Time Spent', 'Pain Point', and 'Automatable (Yes/Partial/No)'.
List every identifiable step in their current process.

## Recommended Multi-Agent Architecture
A Markdown table with columns 'Agent Name', 'Role', 'Tools/APIs Required', and 'Replaces'.
Design a specific set of AI agents that would work together to automate this process end-to-end.
Be specific — name the agents (e.g. "Document Ingestion Agent", "Risk Scoring Agent", "Routing Orchestrator").

## Projected ROI & Time Savings
A Markdown table with columns 'Metric', 'Before Automation', 'After Automation', and 'Impact'.
Include: Processing time per unit, Daily throughput, Error rate, Weekly hours saved, Monthly cost savings (calculate using the hourly rate and team size provided), Annual ROI.

## Implementation Roadmap
A Markdown table with columns 'Phase', 'Deliverable', 'Timeline', and 'Business Value Unlocked'.
Show a realistic phased delivery plan from V1 to full deployment.

## Risk & Compliance Considerations
2-3 bullet points on key risks or compliance factors specific to their industry that the architecture must account for.

## Executive Summary
3 sentences maximum. State the single most important insight, the projected annual savings in dollars, and the recommended first step.
"""
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are an expert enterprise AI architect. Always be specific, quantitative, and practical. Never give vague answers."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=2500
                    )
                    result = response.choices[0].message.content
                    st.markdown(result)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                    <div style='background: rgba(19,197,123,0.08); border: 1px solid rgba(19,197,123,0.3); border-radius: 12px; padding: 1.25rem; margin-top: 1rem;'>
                        <p style='color: #13C57B !important; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;'>Ready to build this?</p>
                        <p style='color: #9CA3AF !important; font-size: 0.9rem; margin-bottom: 0;'>
                            Book a free 30-minute discovery call with our architects at
                            <a href='https://calendly.com/thinkagentic-support/30min' target='_blank' style='color: #13C57B;'>thinkagentic.ca</a>
                            and we will turn this blueprint into a working system.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.download_button(
                        label="⬇ Download Architecture Report (.txt)",
                        data=result,
                        file_name="thinkagentic_automation_report.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Agent Error: {e}")

st.markdown("<br><br><br>", unsafe_allow_html=True)