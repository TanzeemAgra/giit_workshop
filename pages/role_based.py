import streamlit as st
import sys
import os
from dotenv import load_dotenv

#Load Environemtn Variable
load_dotenv()

#add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_openai_response

#Role-Based System Prompts 
ROLE_PROMPTS = {
    "Default": "You are a helful assistant",
    "Teacher" : "You are an experienced and patient school teacher who explain concepts clearly with examples and encourage learning. Use simple language and break down complex topics into easy-to-understand parts",
}
