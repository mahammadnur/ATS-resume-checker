import streamlit as st
import os
from dotenv import load_dotenv
from utils.pdf_processor import extract_text_from_pdf
from utils.gemini_helper import analyze_resume_job_match, answer_resume_question

# Load environment variables
load_dotenv()

def main():
    st.set_page_config(
        page_title="Resume Job Matcher",
        page_icon="📋",
        layout="wide"
    )
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    st.title("📋 Resume Job Matcher")
    st.write("Upload your resume and job description to get AI-powered matching analysis")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📁 Upload Files")
        
        # Resume upload
        resume_file = st.file_uploader(
            "Upload your resume (PDF)", 
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        # Job description input
        st.header("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description",
            height=200,
            placeholder="Paste the complete job description here..."
        )
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Match", type="primary")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Resume Content")
        if resume_file:
            try:
                resume_text = extract_text_from_pdf(resume_file)
                st.text_area("Extracted Resume Text", resume_text, height=300)
                # Store in session state for chat
                st.session_state.resume_text = resume_text
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
                resume_text = None
        else:
            st.info("Please upload your resume PDF")
            resume_text = None
    
    with col2:
        st.header("💼 Job Description")
        if job_description:
            st.text_area("Job Description", job_description, height=300)
            # Store in session state for chat
            st.session_state.job_description = job_description
        else:
            st.info("Please paste the job description")
    
    # Analysis results
    if analyze_button:
        if resume_text and job_description:
            with st.spinner("Analyzing with Gemini AI..."):
                try:
                    analysis = analyze_resume_job_match(resume_text, job_description)
                    
                    st.header("🎯 Analysis Results")
                    
                    # Display results in tabs
                    tab1, tab2, tab3 = st.tabs(["📊 Match Score", "💡 Suggestions", "🔧 Improvements"])
                    
                    with tab1:
                        st.markdown(analysis.get('match_analysis', 'No match analysis available'))
                    
                    with tab2:
                        st.markdown(analysis.get('suggestions', 'No suggestions available'))
                    
                    with tab3:
                        st.markdown(analysis.get('improvements', 'No improvements available'))
                        
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
        else:
            st.warning("Please upload a resume and provide a job description before analyzing")
    
    # ---------- Floating chat section ----------
    chat_css = """
    <style>
    .chat-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 350px;
        max-height: 400px;
        background: white;
        border: 1px solid #ddd;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        padding: 15px;
        overflow-y: auto;
    }
    
    .chat-header {
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    }
    
    .chat-messages {
        max-height: 250px;
        overflow-y: auto;
        margin-bottom: 10px;
    }
    </style>
    """
    st.markdown(chat_css, unsafe_allow_html=True)
    
    # Create a placeholder for the floating chat
    chat_placeholder = st.empty()
    
    with chat_placeholder.container():
        # st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        st.markdown('<div class="chat-header">💬 Ask Questions</div>', unsafe_allow_html=True)
        
        # Display chat messages
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input
        query = st.text_input("Ask about resume / JD…", key="chat_input", placeholder="Type your question here...")
        
        if st.button("Send", key="send_button") and query:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": query})
            
            # Check if resume and job description are available
            if hasattr(st.session_state, 'resume_text') and hasattr(st.session_state, 'job_description'):
                try:
                    # Get answer from Gemini
                    answer = answer_resume_question(
                        query, 
                        st.session_state.resume_text, 
                        st.session_state.job_description
                    )
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": "Sorry, there was an error processing your question."
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "Please upload both resume and job description first to ask questions."
                })
            
            # Clear the input and rerun
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
