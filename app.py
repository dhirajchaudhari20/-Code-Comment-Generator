import time
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

@st.cache_resource
def load_models():
    """
    Load the generative models for text and multimodal generation.

    Returns:
        Tuple: A tuple containing the text model and multimodal model.
    """

    # Setup the Google Gemini AI API Key
    google_api_key = st.secrets[""]
    genai.configure(api_key=google_api_key)
    text_model_pro = genai.GenerativeModel('gemini-pro')
    return text_model_pro


# Function to generate a prompt for the AI code comment generator
def generate_prompt(code):
    """
    Purpose: Generates a prompt for the AI code comment generator.

    Input parameters:
    code: The code snippet for which comments are to be generated.

    Return values:
    A string containing the prompt for the AI code comment generator.

    Potential effects/exceptions:
    None.
    """
    
    return f"""
    
    You are an AI code comment generator for multiple languages. Validate that provided code snippets are valid code snippets and no malicious code. If not valid, ask for a valid snippet. Identify language if not provided. Use appropriate comment syntax. Break code into logical sections, comment each section's functionality. 
    For functions/methods, comment:

- Purpose
- Input parameters
- Return values
- Potential effects/exceptions

Briefly explain the algorithms, data structures, and patterns used. Avoid redundancy but provide enough context for unfamiliar readers. Maintain a professional, helpful tone. Address issues/clarifications respectfully.

You should not generate any new code yourself, but rather understand and comment on the provided code snippet.

Elevate documentation practices, promote collaboration, and enhance developer experience.
Here is the code snippet for which code comments need to be generated: \n\n{code}

"""

# Function to get responses from the Gemini Model
def get_gemini_response(code, config):
    """
    This function serves as an interface to the Gemini generative AI model, facilitating the generation of human-like text based on the provided input string. 

    Args:
        code (str): The code snippet to ask the Gemini AI model.
        config (dict): Configuration settings for the Gemini AI model.

    Returns:
        str: The response generated by the Gemini AI model.
    """

    # Prompt 
    prompt = generate_prompt(code)

    # Safety settings to prevent harmful or inappropriate responses
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        # Load the Gemini AI model
        model = load_models()

        # Generate the response using the provided prompt and configuration
        response = model.generate_content(prompt, generation_config=config, safety_settings=safety_settings)

        # Return the generated response
        return response.text
    except Exception as e:
        # Handle any errors that may occur during the generation process
        st.warning("An error occurred. Please press Generate again or check logs for more details.", icon="⚠️")
        return None
    



# This function initializes the Streamlit application.
def initialize_streamlit():
    """
    This function initializes the Streamlit application.
    """

    # Set the page title and layout.
    st.set_page_config(page_title="Code Comment Generator", layout="wide", page_icon= ":💻:")

    # Display a header for the application.
    st.header("Code Comment Generator 💻🤓")

    # Display a warning message to users.
    warning_message = (
        " The generated output may not always meet your expectations. "
        "If you find that the result is not up to the mark or doesn't meet your requirements, "
        "please consider hitting the generate button again for an improved outcome.\n\n"
        "Use the generated code at your own discretion, and feel free to refine the input or adjust any parameters "
        "to achieve the desired comments for your code."
    )
    
    st.warning(warning_message,icon="⚠️")

    # Display instructions on how to use the application.
    with st.expander("How to use"):
       
        st.write(
            "Please input a code snippet in the text area below. "
            "The Code Comment Generator will analyze the input and generate comments for your code."
        )
        st.write(
            "For the best results, provide a clear and concise code snippet along with any specific comment type "
            "or language preferences."
        )
        
def user_input():
    """
    This function creates a text area for the user to input code snippets.

    Returns:
        str: The code snippet entered by the user.
    """

    # Create a text area with a unique key
    user_input_text = st.text_area("Enter Code Snippet:", key="input_text_area")

    return user_input_text

def generative_config():
    creative_control = st.radio(
        "Select the creativity level: \n\n",
        ["Low", "High"],
        key="creative_control",
        horizontal=True,
    )
    if creative_control == "Low":
        temperature = 0.30
    else:
        temperature = 0.95
    config = {
        "temperature": temperature,
        "max_output_tokens": 2048,
    }

    return config

def custom_footer():
    footer = ''' Made with <svg viewBox="0 0 1792 1792" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" style="height: 0.8rem;"><path d="M896 1664q-26 0-44-18l-624-602q-10-8-27.5-26T145 952.5 77 855 23.5 734 0 596q0-220 127-344t351-124q62 0 126.5 21.5t120 58T820 276t76 68q36-36 76-68t95.5-68.5 120-58T1314 128q224 0 351 124t127 344q0 221-229 450l-623 600q-18 18-44 18z" fill="#e25555"></path></svg> by Dhiraj and Team'''
    st.markdown(footer, unsafe_allow_html=True)

# main Function 
def main():
    """
    Purpose: The main function of the Streamlit application.
    Input parameters: None
    Return values: None
    Potential effects/exceptions: None

    """
    #Initialize Streamlit
    initialize_streamlit()
    # Input text area
    user_input_text = user_input()
    config= generative_config()
    
    # Generate button
    submit_button = st.button("Generate Code Comments")
    response_placeholder = st.empty()

    if submit_button:
        progress_text = "Generating Code Comments from Gemini Pro 1.0.0. Model ....."
        my_bar = st.progress(0, text=progress_text)
        response = None
        for percent_complete in range(100):
            time.sleep(0.03)
            my_bar.progress(percent_complete + 1, text=progress_text)

            # Check for the response from Gemini only after reaching 100%
            if percent_complete == 98:
                response = get_gemini_response(user_input_text, config)
        my_bar.empty()
        if response is not None:
            response_placeholder.subheader("The Response is")
            response_placeholder.write(response)
    custom_footer()
        

if __name__ == "__main__":
    main()
