import streamlit as st
from openai import OpenAI
import requests
from PIL import Image
import io
import os
from datetime import datetime
from dotenv import load_dotenv

#Load Environment 
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
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

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

    selected_category = st.selectbox("Category", list(sample_prompts.keys()))
    selected_prompts = st.selectbox("Sample Prompt", sample_prompts[selected_category])

    if st.button("Use This Prompt"):
        st.session_state.prompt_text = selected_prompts

    # Text Input
    prompt = st.text_area(
        "Custom Prompt:",
        value=st.session_state.get('prompt_text', ''),
        placeholder=" A scene landscape with moutain, a lake, and a sunset sky...",
        height=150
    )

    # Generate Button
    if st.button(" Generate Image", type="primary", disabled=not (api_key and prompt)):
        if not api_key:
            st.error("Please Enter Your OpenAI Key in the Sidebar")
        elif not prompt:
            st.error("Please Enter a text prompt")
        else:
            try:
                with st.spinner("Generating Image...This may take a few seconds or while"):
                    # Prepare parameters for the API call
                    params = {
                        "prompt": prompt,
                        "model": model,
                        "size": size,
                        "n": n_images
                    }
                    
                    # Add quality and style only for DALL-E 3
                    if model == "dall-e-3":
                        params["quality"] = quality
                        params["style"] = style
                    
                    response = client.images.generate(**params)

                    # Store Generated Images in session state
                    st.session_state.generated_images = response.data
                    st.session_state.current_prompt = prompt
                    st.success("Image Generated Successfully")
            except Exception as e:
                st.error(f"Error Generating Image: {str(e)}")

with col2:
    st.subheader("Generated Images")

    #Display Generated Images
    if hasattr(st.session_state, 'generated_images') and st.session_state.generated_images:
        for i, image_data in enumerate(st.session_state.generated_images):
            try:
                #Download and Display Image
                image_response = requests.get(image_data.url)
                image = Image.open(io.BytesIO(image_response.content))

                st.image(image, caption=f"Generated Image {i+1}", use_column_width=True)

                #Download Button
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"generated_image_{timestamp}_{i+1}.png"

                st.download_button(
                    label=f"Download Image",
                    data=img_buffer.getvalue(),
                    file_name=filename,
                    mime="image/png"
                )

                #show prompt used 
                if hasattr(st.session_state, 'current_prompt'):
                    st.caption(f"Prompt: {st.session_state.current_prompt}")
            except Exception as e:
                st.error(f"Error Display Image {i+1}: {str(e)}")
    else:
        st.info("Generated Images will appear here")
        

