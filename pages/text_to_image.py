import streamlit as st
import openai
import requests
from PIL import Image
import io
import os
from datetime import datetime
from dotenv import load_dotenv

#Load Emnironemnt 
load_dotenv()

#Configure Page
st.set_page_config(page_title="AI Image Generator Hub",
                   page_icon="+^",
                   layout="wide"
                   )

#Title and Description
st.title("AI Image Generator")
st.markdown("Generate Stunning images from text describtion using OpenAI's DALLE-E Model")

st.sidebar.header("Settings")

#API Key Input - Check Environment Variable First 
default_api_key = os.getenv("OPENAI_API_KEY", "")
if default_api_key:
    st.sidebar.success("API Key Loaded from the Environment")
    api_key = default_api_key
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="Enter Your OpenAI API Key")

if api_key:
    openai.api_key = api_key

    #Image Generator Paramete
    st.sidebar.subheader("Generate Parameter")
    #Model Selection
    model = st.sidebar.selectbox(
        "Model",
        ["dall-e-3", "dalle-e-2"],
        help="Choose the DALL-E Model Version"
    )

    #Image Size
    if model == "dall-e-3":
        size_option = ["1024x1024", "1024x1792", "1792x1024"]
    else:
        size_option = ["256x256", "512x512", "1024x1024"]

    size = st.sidebar.selectbox("Image Size", size_option)

    #Quality (Only for Dall_E 3)
    if model == "dall-e-3":
        quality = st.sidebar.selectbox("Quality", ["standard","hd"])
    else:
        quality = "standard"

    #Style (Only For DALLE 3)
    if model == "dall-e-3":
        style = st.sidebar.selectbox("Style", ["vivid","natural"])
    else:
        style = "natural"

    if model == "dall-e-2":
        n_images = st.sidebar.slider("Number of Images", 1,4,1)
    else:
        n_images = 1

#Main Content Area

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Text Prompt")

    #Sample Prompts
    st.markdown("** Quick Start - Sample Prompts:**")
    sample_prompts = {
        "Landscapes": [
            "A serene mountain landscape at sunset with a crystal-clear lake",
            "A tropical beach with palm trees and turquoise water",
            "A misty forest with tall pine trees and morning sunlight"
        ],
        "Fantasy": [
            "A majestic dragon flying over a medieval castle",
            "A magical forest with glowing mushrooms and fairy lights",
            "A steampunk airship floating in cloudy skies"
        ],
        "Modern": [
            "A futuristic cityscape with flying cars and neon lights",
            "A cozy coffee shop with warm lighting and people reading",
            "A modern minimalist living room with large windows"
        ]
    }