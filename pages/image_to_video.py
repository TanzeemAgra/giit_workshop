import streamlit as st
import openai
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os
import base64
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import json

#Load Environment 
load_dotenv()

#Configure Page
st.set_page_config(page_title="Disease Progress Video Generator",
                   page_icon="++^",
                   layout="wide"
                   )

def encode_image_to_base64(image):
    """ Convert PIL Image to base64 String"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode
    return img_str

def generate_disease_progress_frames(diseases_info, api_key, num_frames=5):
    """Generate frames showing diseas progress using DALL-E"""
    try:
        openai.api_key = api_key
        generated_frames = []

        #Deine Progress Stages
        progression_stages = [
            "Early stage - initial symptoms barely visible",
            "Mild progression - early signs becoming apparent", 
            "Moderate progression - clear manifestation of symptoms",
            "Advanced stage - significant disease presentation",
            "Severe stage - advanced disease characteristics"
        ]

