"""
NIYAMR AI - Universal Credit Act 2025 Analyzer
Streamlit Web Interface
"""

import streamlit as st
import json
from pathlib import Path
import time
from datetime import datetime
from dotenv import load_dotenv

from src.pdf_extractor import extract_text_from_pdf, get_pdf_metadata
from src.gemini_analyzer import GeminiAnalyzer
from src.json_compiler import JSONCompiler

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="NIYAMR AI - Legislative Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .rule-pass {
        color: #28a745;
        font-weight: bold;
    }
    .rule-fail {
        color: #dc3545;
        font-weight: bold;
    }
    h1 {
        color: #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None

# Header
st.title("⚖️ NIYAMR AI - Legislative Document Analyzer")
st.markdown("**AI-Powered Analysis of the Universal Credit Act 2025**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 About")
    st.markdown("""
    This AI agent analyzes legislative documents and provides:
    - **Text Extraction** from PDFs
    - **5-Point Summaries**
    - **7 Legislative Sections**
    - **6 Compliance Checks**
    """)
    
    st.markdown("---")
    
    st.header("📊 Status")
    if st.session_state.analysis_complete:
        st.success("✅ Analysis Complete")
    else:
        st.info("⏳ Ready to analyze")
    
    st.markdown("---")
    
    st.header("ℹ️ How to Use")
    st.markdown("""
    1. Upload PDF document
    2. Click 'Start Analysis'
    3. View results in tabs
    4. Export reports
    """)

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Upload & Extract", 
    "📝 Summary", 
    "📚 Sections", 
    "✔️ Validation",
    "💾 Export"
])

# TAB 1: Upload & Extract
with tab1:
    st.header("📄 Document Upload & Text Extraction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Universal Credit Act 2025 PDF",
            type=['pdf'],
            help="Upload the legislative document for analysis"
        )
    
    with col2:
        st.markdown("### Quick Stats")
        if uploaded_file:
            st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
    
    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = Path("temp_upload.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialize components
                compiler = JSONCompiler()
                
                # Task 1: Extract Text
                status_text.text("📄 Task 1/4: Extracting text from PDF...")
                progress_bar.progress(10)
                
                extracted_text = extract_text_from_pdf(str(temp_path))
                pdf_metadata = get_pdf_metadata(str(temp_path))
                
                compiler.add_metadata(pdf_metadata)
                compiler.add_task1_result(extracted_text, temp_path)
                
                progress_bar.progress(25)
                st.success(f"✅ Extracted {len(extracted_text)} characters from {pdf_metadata.get('total_pages', 0)} pages")
                
                # Task 2: Summarize
                status_text.text("📝 Task 2/4: Generating AI summary...")
                progress_bar.progress(40)
                
                analyzer = GeminiAnalyzer()  # Uses .env automatically
                summary = analyzer.summarize_act(extracted_text)
                compiler.add_task2_result(summary)
                
                progress_bar.progress(55)
                st.success(f"✅ Generated {len(summary.get('summary', []))} summary points")
                
                # Task 3: Extract Sections
                status_text.text("📚 Task 3/4: Extracting legislative sections...")
                progress_bar.progress(70)
                
                sections = analyzer.extract_legislative_sections(extracted_text)
                compiler.add_task3_result(sections)
                
                progress_bar.progress(85)
                st.success(f"✅ Extracted {len(sections)} legislative sections")
                
                # Task 4: Rule Checks
                status_text.text("✔️ Task 4/4: Running compliance checks...")
                progress_bar.progress(90)
                
                rule_checks = analyzer.apply_rule_checks(extracted_text)
                compiler.add_task4_result(rule_checks)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis Complete!")
                
                # Store results in session state
                st.session_state.results = compiler.generate_report()
                st.session_state.analysis_complete = True
                
                # Save outputs
                output_dir = Path("output")
                compiler.save_to_file("output/final_report.json")
                compiler.save_extracted_text(extracted_text, "output")
                
                st.balloons()
                st.success("🎉 Analysis complete! Check other tabs for detailed results.")
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.error("Make sure your .env file contains GEMINI_API_KEY")
                import traceback
                with st.expander("Show Error Details"):
                    st.code(traceback.format_exc())

# TAB 2: Summary
with tab2:
    st.header("📝 Act Summary")
    
    if st.session_state.analysis_complete:
        summary_data = st.session_state.results.get('task2_summary', {})
        summary_points = summary_data.get('summary_points', [])
        
        st.markdown("### Key Points")
        for i, point in enumerate(summary_points, 1):
            with st.expander(f"**Point {i}**", expanded=True):
                st.markdown(point)
        
        st.markdown("---")
        
        # Download summary
        st.download_button(
            "📥 Download Summary (TXT)",
            data="\n\n".join(summary_points),
            file_name="act_summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("👈 Upload a PDF and run analysis to see the summary")

# TAB 3: Legislative Sections
with tab3:
    st.header("📚 Legislative Sections")
    
    if st.session_state.analysis_complete:
        sections_data = st.session_state.results.get('task3_legislative_sections', {})
        sections = sections_data.get('sections', {})
        
        section_icons = {
            'definitions': '📖',
            'obligations': '📋',
            'responsibilities': '👔',
            'eligibility': '✅',
            'payments': '💰',
            'penalties': '⚠️',
            'record_keeping': '📝'
        }
        
        for key, value in sections.items():
            icon = section_icons.get(key, '📄')
            with st.expander(f"{icon} **{key.replace('_', ' ').title()}**", expanded=False):
                st.markdown(value)
        
        st.markdown("---")
        
        # Download sections
        st.download_button(
            "📥 Download Sections (JSON)",
            data=json.dumps(sections, indent=2),
            file_name="legislative_sections.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("👈 Upload a PDF and run analysis to see legislative sections")

# TAB 4: Validation Results
with tab4:
    st.header("✔️ Compliance Validation")
    
    if st.session_state.analysis_complete:
        validation_data = st.session_state.results.get('task4_rule_checks', {})
        checks = validation_data.get('checks', [])
        passed = validation_data.get('passed', 0)
        failed = validation_data.get('failed', 0)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rules", len(checks))
        col2.metric("✅ Passed", passed)
        col3.metric("❌ Failed", failed)
        
        st.markdown("---")
        
        # Rule details
        for i, check in enumerate(checks, 1):
            status = check.get('status', 'unknown')
            rule = check.get('rule', '')
            evidence = check.get('evidence', '')
            confidence = check.get('confidence', 0)
            
            status_icon = "✅" if status == "pass" else "❌"
            
            with st.container():
                st.markdown(f"### {status_icon} Rule {i}: {rule}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Status:** :{'green' if status == 'pass' else 'red'}[{status.upper()}]")
                    st.markdown(f"**Evidence:** {evidence}")
                with col2:
                    st.metric("Confidence", f"{confidence}%")
                
                st.markdown("---")
        
    else:
        st.info("👈 Upload a PDF and run analysis to see validation results")

# TAB 5: Export
with tab5:
    st.header("💾 Export Results")
    
    if st.session_state.analysis_complete:
        results = st.session_state.results
        
        st.markdown("### Available Exports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📄 Full Report (JSON)")
            st.download_button(
                "Download Complete Analysis",
                data=json.dumps(results, indent=2),
                file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 📝 Summary Only (TXT)")
            summary_text = "\n\n".join(results.get('task2_summary', {}).get('summary_points', []))
            st.download_button(
                "Download Summary Text",
                data=summary_text,
                file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.markdown("---")
        
        st.markdown("#### 📊 Metadata")
        metadata = results.get('metadata', {})
        st.json(metadata)
        
        st.markdown("---")
        
        # Preview JSON
        with st.expander("👁️ Preview Full JSON Report"):
            st.json(results)
        
    else:
        st.info("👈 Upload a PDF and run analysis to export results")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>⚖️ <b>NIYAMR AI - Legislative Document Analyzer</b></p>
    <p>Built with Streamlit, LangChain & Google Gemini AI | 48-Hour Internship Challenge</p>
</div>
""", unsafe_allow_html=True)
