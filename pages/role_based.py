import streamlit as st
import sys
import os
from dotenv import load_dotenv

#Load Environemtn Variable
load_dotenv()

#add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_openai_response
