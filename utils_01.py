import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_response(user_input, chat_history):
    """
    Get response from OpenAI API and return updated chat history
    
    Args:
        user_input (str): The user's message
        chat_history (list): List of previous messages
    
    Returns:
        tuple: (response_content, updated_chat_history)
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Create messages for API call
    messages = []
    
    # Add chat history to messages
    for message in chat_history:
        messages.append({
            "role": message["role"],
            "content": message["content"]
        })
    
    # Add current user input
    messages.append({
        "role": "user",
        "content": user_input
    })
    
    try:
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        # Extract response content
        response_content = response.choices[0].message.content
        
        # Update chat history
        updated_history = chat_history.copy()
        updated_history.append({
            "role": "user",
            "content": user_input
        })
        updated_history.append({
            "role": "assistant",
            "content": response_content
        })
        
        return response_content, updated_history
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
