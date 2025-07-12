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

     """
           

