import streamlit as st
import sys
import os
from dotenv import load_dotenv
import PyPDF2
import io
from typing import List, Dict
import hashlib
import pickle

#Load Environment Variables
load_dotenv()

#Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI

#Initialize OpenAI Client 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class PDFProcessor:
    def __init__(self):
        self.pdf_cache_dir = "pdf_cache"
        if not os.path.exists(self.pdf_cache_dir):
            os.makedirs(self.pdf_cache_dir)

    def extract_text_from_pdf(self, pdf_file) -> str:
        "Extract Text From PDF"
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    text += f"\n ---Page {page_num + 1} --\n {page_text}\n"
                except Exception as e:
                    st.warning(f"Could not extract Text: {str(e)}")
                    continue
            return text
        except Exception as e:
                    st.warning(f"Could not extract File: {str(e)}")
    def get_file_hash(self, pdf_file) -> str:
         "Generate Hash Value"
         pdf_file.seek(0)
         content = pdf_file.read()
         pdf_file.seek(0)
         return hashlib.md5(content).hexdigest()
    
    def cache_pdf_content(self, file_hash: str, content: str, filename: str):
         """Cache Extracted PDF Content"""
         cache_data = {
              'content' : content,
              'filename': filename
         }
         cache_path = os.path.join(self.pdf_cache_dir, f"{file_hash}.pkl")
         with open(cache_path, 'wb') as f:
              pickle.dump(cache_data, f)

    def load_cached_content(self, file_hash: str) -> Dict:
         """Load Cache PDF Content"""
         cache_path = os.path.join(self.pdf_cache_dir, f"{file_hash}.pkl")
         if os.path.exists(cache_path):
              with open(cache_path, 'rb') as f:
                   return pickle.load(f)
         return None
    

def get_pdf_based_response(question: str, pdf_contents: Dict[str, str], chat_history: List = None) -> tuple:
     """Get Response Based Onluy on PDF Document"""
     # Combine All PDF Contents

     combined_content = ""
     for filename, content in pdf_contents.item():
          combined_content += f"\n\n ---Content Form {filename + 1} --\n {content}\n"
    
     if not combined_content.strip():
          return "I dont have any PDF content to answer your question. Please updload the PDF File", chat_history or []

     # Create a System Prompt
     system_prompt = f"""You are a helpful assistant that answers questions ONLY based on the provided PDF content.
     
     IMPORTANT RULES:
     1. Only use information from the provided PDF content below
     2. If the answer is not in the PDF content, clearly state "I cannot find this information in the uploaded PDF documents"
     3. Always cite which document/page the information comes from when possible
     4. Be accurate and don't make up information not present in the PDFs
     5. If asked about something not in the PDFs, politely explain that you can only answer based on the uploaded documents

     
    PDF CONTENT:
    {combined_content}

    Remeber: Answer ONLY based on the above pdf content."""
     
     #Prepare messages
     messages = [{"role":"system", "content": system_prompt}]

     #add chat History if available
     if chat_history:
          messages.extend(chat_history)

     #Add Current Question
     messages.append({"role":"user", "content": question})

     try:
          response = client.chat.completions.create(
               model = "gpt-4",
               messages=messages,
               max_tokens = 1000,
               temperature =0.3
          )

          reply = response.choices[0].message.content

          # Update chat History
          update_history = chat_history if chat_history else []
          update_history.append({"role": "user", "content": question})
          update_history.append({"role": "assistant", "content": reply})

          return reply, update_history
     except Exception as e:
          error_msg = f"Error Getting Response: {str(e)}"
          return error_msg, chat_history or []
     
#Streamlit App Configuration
st.set_page_config(
        page_title="PDF-Based AI Assistant", 
        page_icon="+", 
        layout="wide"
    )

# Custom CSS
st.markdown("""
<style>
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
    }
    .pdf-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .stats-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

#Initialize the Session State

if "pdf_contents" not in st.session_state:
     st.session_state.pdf_contents = {}
if "pdf_chat_history" not in st.session_state:
     st.session_state.pdf_chat_history = []
if "pdf_inout_key" not in st.session_state:
     st.session_state.pdf_input_key = 0

#Inititialise PDF Processor 

pdf_processor = PDFProcessor()

# Header
st.title("📚 PDF-Based AI Assistant")
st.markdown("Upload multiple PDFs and ask questions based on their content!")

#Sidebar
with st.sidebar:
     st.header("PDF Document")

     #File Uploader
     uploaded_files = st.file_uploader(
          "choose PDf files",
          type="pdf",
          accept_multiple_files=True,
          help="Upload One or more PDF Files to Analyse"
     )

     #Process Uploaded Files
     if uploaded_files:
          progress_bar = st.progress(0)
          status_text = st.empty()

          for i, uploaded_file in enumerate(uploaded_files):
               status_text.text(f"Processing {uploaded_files.name}...")

               #Check if file is already processed 
               file_hash = pdf_processor.get_file_hash(uploaded_file)
               cached_data = pdf_processor.load_cached_content(file_hash)

               if cached_data:
                    st.session_state.pdf_contents[uploaded_file.name] = cached_data['content']
                    status_text.text(f"Loaded from cache: {uploaded_file.name}")
               else:
                    # Extract TExt
                    extracted_text = pdf_processor.extract_text_from_pdf(uploaded_file)
                    if extracted_text:
                         st.session_state.pdf_contents[uploaded_file.name] = extracted_text
                         # Cache the Contents
                         pdf_processor.cache_pdf_content(file_hash, extracted_text, uploaded_file.name)
                         status_text.text = (f" Process Successful ")
                    else:
                         status_text.text(f"Process Failed")
               progress_bar.progress( "The progress of the file ")
               st.success(f"Successfully Processed")

               #Display Loaded PDF

               if st.session_state.pdf_contents:
                    st.markdown(" Loaded Documents")
                    for filename, content in st.session_state.pdf_contents.items():
                         word_count = len(content.split())
                         st.markdown(f"""
                                     <div class="pdf-card">
                                     <strong> {filename} </strong>
                                     <small> {word_count:,} words extracted</small>
                                     </div>
                                     """, unsafe_allow_html=True)

#Main Content Area
if not st.session_state.pdf_Contents:
     # Welcome screen
    st.markdown("""
    <div class="upload-section">
        <h2 style="color: white; text-align: center;">📚 Welcome to PDF-Based AI Assistant</h2>
        <p style="color: white; text-align: center; font-size: 1.2em;">
            Upload your PDF documents and start asking questions based on their content!
        </p>
    </div>
    """, unsafe_allow_html=True)
     

               

                     
                





