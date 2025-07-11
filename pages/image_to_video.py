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
        10. **Treatment Option**: recomend medical treatment option for disease

        **Format**: Use clear medical terminology suitable for healthcare professionals while being educational.
        **Disclaimer**: Include appropriate medical disclaimers about individual variation and professional consultation.
        """
        response = openai.ChatCompletion.create(
            model= model,
            messages=[
                {
                    "role":"system",
                    "content": "You are a medical education specialist with expertise in disease progression and pathology. Provide comprehensive, educational analysis for healthcare professional and medical students." 
                    
                },
                {
                    "role":"user",
                    "content": analysis_prompt
                }
            ],
            max_token=2000,
            temperature=0.1
        )

        return response.choices[0].message.content
    except Exception as e:
        raise Exception (f"Error Generating Progress Analysis: {str(e)}")


def main():
    st.title("Disease Progress Video Generation")
    st.markdown("Generate educational videos showin disease progression over time for medical education and patient understanding")

    # Medical disclaimer
    st.error("""
    ⚠️ **MEDICAL DISCLAIMER**: This tool generates educational content for medical professionals and students. 
    It should NOT be used for self-diagnosis or replace professional medical consultation. 
    Generated content is for educational purposes only and may not reflect individual patient variations.
    """)

    #Side Bar Setting 
    with st.sidebar:
        st.header("Video Generation Setting")

        #API Key
        default_api_key = os.getenv("OPENAI_API_KEY", "")
        if default_api_key:
            st.success("API Key Loaded from Environment")
            api_key = default_api_key
        else:
            api_key = st.text_input("OPENAI API KEY", type="password", help="Enter Your OpenAI API Key")
        
        #Selection Model
        model = st.selectbox(
            "AI Model",
            ["gpt-4o","gpt-4o-mini","gpt-4-turbo"],
            help="Choose the AI Model for Analysis"
        
        )

        #Video Settings
        st.subheader ("Video Parameter")
        num_frames = st.slider("Number of Stages", 3,8,5, help="Number of progression stages to generate")
        frame_duration = st.slider("Stahe Duration(seconds)", 1,10,3, help="How long the frame duration")

        #Disease Category
        st.subheader("Disease Categories")
        disease_category = st.selectbox(
            "Medical Specialty",
            [
                "Dermatology",
                "Oncology", 
                "Cardiology",
                "Neurology",
                "Ophthalmology",
                "Orthopedics",
                "Pulmonology",
                "Gastroenterology",
                "Infectious Disease",
                "Rheumatology"
            ]
        )

        #Main Content Area

    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("Diseases Configuration")
        # Pre-defined disease examples
        disease_examples = {
            "Dermatology": {
                "Melanoma Progression": {
                    "condition": "Melanoma",
                    "location": "Skin lesion on back",
                    "visual_characteristics": "Changing mole with irregular borders, color variation, and size increase",
                    "demographics": "Adults 30-70 years"
                },
                "Psoriasis Development": {
                    "condition": "Psoriasis",
                    "location": "Elbow and knee areas",
                    "visual_characteristics": "Red, scaly plaques with silvery scales",
                    "demographics": "Adults 20-50 years"
                }
            },
            "Oncology": {
                "Breast Cancer Progression": {
                    "condition": "Breast Cancer",
                    "location": "Breast tissue",
                    "visual_characteristics": "Tumor growth, tissue changes, lymph node involvement",
                    "demographics": "Women 40-70 years"
                },
                "Lung Cancer Development": {
                    "condition": "Lung Cancer",
                    "location": "Lung tissue - chest X-ray view",
                    "visual_characteristics": "Nodule growth, opacity changes, pleural involvement",
                    "demographics": "Adults 50-80 years"
                }
            },
            "Cardiology": {
                "Atherosclerosis Progression": {
                    "condition": "Atherosclerosis",
                    "location": "Coronary artery",
                    "visual_characteristics": "Plaque buildup, arterial narrowing, calcification",
                    "demographics": "Adults 40-80 years"
                }
            },
            "Ophthalmology": {
                "Diabetic Retinopathy": {
                    "condition": "Diabetic Retinopathy",
                    "location": "Retina - fundus view",
                    "visual_characteristics": "Microaneurysms, hemorrhages, neovascularization",
                    "demographics": "Diabetic patients"
                },
                "Glaucoma Progression": {
                    "condition": "Glaucoma",
                    "location": "Optic nerve head",
                    "visual_characteristics": "Optic disc cupping, nerve fiber layer thinning",
                    "demographics": "Adults over 40"
                }
            }
        }

        #Select Diseases Example
        if disease_category in disease_examples:
            diseases_option = list(disease_examples[disease_category].keys())
            selected_diseases = st.selectbox("Select Disease Example", diseases_option)
            diseases_info = disease_examples[disease_category][selected_diseases]

            #Display selected disease Info
            st.json(diseases_info)
        else:
            diseases_info = {
                "condition": "Custom Disease",
                "location": "Specific Location",
                "visual_characteristics": "Describe Visual Changes",
                "demographics": "Target Population"
            }

        #Custom Disease Information
        st.subheader("Custom Disease Configuration")
        condition = st.text_input("Diseases/Condition", value=diseases_info["condition"])
        location = st.text_input("Specifi Location", value=diseases_info["location"])
        visual_characteristics = st.text_area("Visual Characteristics", value=diseases_info["visual_characteristics"])
        demographics = st.text_input("Patient Demographics", value=diseases_info["demographics"])

        #Update Disease Info
        disease_info = {
            "condition": condition,
            "location": location,
            "visual_characteristics": visual_characteristics,
            "demographics": demographics
        }

        # Generate Buttons
        st.subheader("Generation Controls")

        col_analysis, col_video = st.columns(2)
        with col_analysis:
            if st.button("Generate Analysis", disabled=not api_key):
                if api_key and condition:
                    st.session_state.disease_info = disease_info
                    st.session_state.generate_analysis = True
                else:
                    st.error("Please enter the API Key and Disease Information")
                
        with col_video:
            if st.button("Generate Video Frames", disabled=not api_key):
                if api_key and condition:
                    st.session_state.disease_info = disease_info
                    st.session_state.generate_frames = True
                    st.session_state.num_frames = num_frames
                else:
                    st.error("Please enter the API Key and Disease Information")

    with col2:
        st.subheader("Disease Progress Result")

        #Generate Analysis
        if hasattr(st.session_state, 'generate_analysis') and st.session_state.generate_analysis:
            if st.button("Statrt Analysis Generation"):
                try:
                    with st.spinner("Generate Progress Analysis"):
                        analysis = create_progression_analysis(st.session_state.disease_info, api_key, model)
                        st.session_state.progression_analysis = analysis
                        st.session_state.generate_analysis = False
                        st.success("✅ Analysis generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        #Video Analysis
        if hasattr(st.session_state, 'generate_frame') and st.session_state.generate_frame:
            if st.button("Statrt Frame Generation"):
                try:
                    with st.spinner("Generate Frame"):
                        frame = generate_disease_progress_frames(st.session_state.disease_info, api_key, st.session_state.num_frames)
                        st.session_state.progression_frame = frame
                        st.session_state.generate_frames = False
                        st.success("✅ Video Frame generated successfully!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        #Display Analysis
        if hasattr(st.session_state, 'progression_analysis'):
            st.markdown("Disease Progression Analysis")
            with st.expander("View Full Analysis", expanded=True):
                st.markdown(st.session_state.progression_analysis)

         #Save analysis
        if st.button("💾 Save Analysis Report"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"disease_progression_analysis_{timestamp}.txt"
                
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"DISEASE PROGRESSION ANALYSIS REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Disease: {st.session_state.disease_info['condition']}\n")
                f.write(f"Location: {st.session_state.disease_info['location']}\n")
                f.write(f"{'='*60}\n\n")
                f.write(st.session_state.progression_analysis)
                f.write(f"\n\n{'='*60}\n")
                f.write("DISCLAIMER: This is educational content for medical professionals.\n")
                
            st.success(f"📄 Analysis saved as {filename}")






























if __name__ == "__main__":
    main()
