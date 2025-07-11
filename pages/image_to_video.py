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

        # Generate frames for each stage
        for i, stage in enumerate(progression_stages[:num_frames]):
            prompt = f"""
            Medical Illustration of {diseases_info['condition']}

            Style: Professional Medical Illustration, clinical photography style,
            educational medical content, anatomically accurate, clear visualization,
            medical textbook quality, diagnostic image style, healthcare professional standard

            show: {diseases_info["visual_characteristics"]} at {stage} """

            with st.spinner(f"Generating Frame {i+1}/{num_frames} - {stage}"):
                response = openai.Imagge.create(
                    prompt=prompt,
                    model="dall-e-3",
                    size="1024x1024",
                    quality="hd",
                    style="natural",
                    n=1
                )

                # Download and Store the IMage

                img_response = requests.get(response.data[0].url)
                frame_image = Image.open(io.BytesIO(img_response.content))

                #Add Stage Lable to Frame
                frame_with_label = add_stage_label(frame_image, f"Stage {i+1}: {stage}")

                generated_frames.append({
                    'image': frame_with_label,
                    'stage': stage,
                    'stage_number': i+1
                })
        return generated_frames
    except Exception as e:
        raise Exception(f"Error generating progress frame: {str(e)}")
        

def add_stage_label(image, label_text):
    """Add Stage label to the Images"""
    try:
        #Create a copy of the imgae
        labeled_image = image.copy()
        draw = ImageDraw.Draw(label_text)

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        text_width = draw.textlength(label_text, font=font)
        text_height = 30
        x = 10
        y = 10

        #Draw Background Rectangle for text
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+5], fill="black", outline="white")

        #Drwa TExt
        draw.text((x,y), label_text, fill="white", font=font)

        return labeled_image 
    except Exception as e:
        st.error(f"Error adding Label: {str(e)}")
        return image
    
def create_progression_analysis(disease_info, api_key, model="gpt-4o"):
    """Generate detailed analysis of disease progression"""
    try:
        openai.api_key = api_key

        analysis_prompt = f"""
        As a medical education specialist, provide a comprehensive analysis of {disease_info['condition']} progression:

        **Disease:** {disease_info['condition']}
        **Location:** {disease_info['location']}
        **Patient Demographics:** {disease_info.get('demographics', 'General population')}

        Please provide:
        1. **Disease Overview**: Brief description of the condition
        2. **Progression Timeline**: Typical timeline from onset to advanced stages
        3. **Stage-by-Stage Analysis**: Detailed description of each progression stage
        4. **Visual Changes**: How the appearance changes through each stage
        5. **Symptoms Evolution**: How symptoms develop and worsen over time
        6. **Risk Factors**: Factors that accelerate or influence progression
        7. **Intervention Points**: Key stages where treatment can be most effective
        8. **Prognosis**: Expected outcomes at different stages
        9. **Educational Notes**: Important points for patients and healthcare providers

        **Format**: Use clear medical terminology suitable for healthcare professionals while being educational.
        **Disclaimer**: Include appropriate medical disclaimers about individual variation and professional consultation.
        """



