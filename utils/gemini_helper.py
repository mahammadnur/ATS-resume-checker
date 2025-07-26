import google.generativeai as genai
import os

def configure_gemini():
    """Configure Gemini AI with API key"""
    api_key = os.getenv('GENAI_API_KEY')
    if not api_key:
        raise ValueError("GENAI_API_KEY not found in environment variables")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash-lite')

def analyze_resume_job_match(resume_text, job_description):
    """
    Analyze resume and job description match using Gemini AI
    """
    model = configure_gemini()
    
    prompt = f"""
    As an expert HR analyst, please analyze the following resume against the job description and provide:

    1. **MATCH SCORE & ANALYSIS** (provide percentage match and detailed explanation):
    - Overall compatibility percentage
    - Key matching skills and experiences
    - Missing critical requirements
    
    2. **ACTIONABLE SUGGESTIONS**:
    - Specific skills to highlight better
    - Experience sections to emphasize
    - Keywords to incorporate
    
    3. **RESUME IMPROVEMENTS**:
    - What to add or modify
    - How to better align with job requirements
    - Formatting or content suggestions

    **RESUME:**
    {resume_text}

    **JOB DESCRIPTION:**
    {job_description}

    Please format your response in clear sections with specific, actionable advice.
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Parse the response into sections
        response_text = response.text
        
        # Simple parsing - you can make this more sophisticated
        sections = response_text.split('\n\n')
        
        result = {
            'match_analysis': '',
            'suggestions': '',
            'improvements': ''
        }
        
        current_section = 'match_analysis'
        for section in sections:
            if 'SUGGESTIONS' in section.upper():
                current_section = 'suggestions'
            elif 'IMPROVEMENTS' in section.upper():
                current_section = 'improvements'
            
            result[current_section] += section + '\n\n'
        
        return result
        
    except Exception as e:
        raise Exception(f"Gemini AI analysis failed: {str(e)}")

def answer_resume_question(question, resume_text, job_description):
    """
    Answer specific questions about resume and job description using Gemini AI with context
    """
    model = configure_gemini()
    
    # Enhanced prompt with better context handling
    prompt = f"""
    You are an expert HR assistant and career counselor. Answer the user's question based ONLY on the provided resume and job description context.

    CONTEXT:
    **RESUME CONTENT:**
    {resume_text}

    **JOB DESCRIPTION:**
    {job_description}

    INSTRUCTIONS:
    - Provide a helpful, concise response (1-3 sentences)
    - Base your answer strictly on the resume and job description provided
    - If the question is about skills, experience, qualifications, or job requirements, answer from the context
    - If the question asks for comparisons, suggestions, or recommendations, use both documents
    - If the question is completely unrelated to resume/job content, respond with: "Not available details."
    - Be specific and reference actual details from the documents when possible

    EXAMPLES OF VALID QUESTIONS:
    - "What are my key skills?"
    - "Do I meet the job requirements?"
    - "What experience do I have in Python?"
    - "What qualifications does the job need?"
    - "How well do I match this role?"

    USER QUESTION: {question}

    ANSWER:
    """
    
    try:
        response = model.generate_content(prompt)
        answer = response.text.strip()
        
        # Clean up the response
        if answer.startswith("ANSWER:"):
            answer = answer.replace("ANSWER:", "").strip()
        
        # Check if response indicates out-of-context question
        if any(phrase in answer.lower() for phrase in [
            "not available details", 
            "cannot answer", 
            "not related to",
            "outside the scope",
            "not provided in"
        ]):
            return "Not available details."
        
        # Limit response length for chat
        if len(answer) > 300:
            # Find the last complete sentence within 300 chars
            sentences = answer.split('.')
            truncated = ""
            for sentence in sentences:
                if len(truncated + sentence + ".") <= 300:
                    truncated += sentence + "."
                else:
                    break
            answer = truncated if truncated else answer[:300] + "..."
        
        return answer
        
    except Exception as e:
        return "Sorry, I couldn't process your question at the moment."

def is_question_relevant(question, resume_text, job_description):
    """
    Check if the question is relevant to resume/JD content using Gemini
    """
    model = configure_gemini()
    
    prompt = f"""
    Determine if the following question is related to resume analysis, job matching, career advice, or professional qualifications.

    Question: {question}

    Respond with only "YES" if the question is related to:
    - Resume content analysis
    - Job requirements
    - Skills and qualifications
    - Career advice
    - Professional experience
    - Job matching

    Respond with only "NO" if the question is about:
    - General knowledge
    - Unrelated topics
    - Personal life unrelated to career
    - Technical questions not about skills

    Answer:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip().upper() == "YES"
    except:
        return True  # Default to allowing the question if check fails
