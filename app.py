import time
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pygments import highlight
from pygments.lexers import PythonLexer  # Adjust lexer for different languages
from pygments.formatters import HtmlFormatter
from guesslang import Guess

@st.cache_resource
def load_models():
    try:
        google_api_key = st.secrets["general"]["GOOGLE_API_KEY"]
        if not google_api_key:
            st.error("API key is empty. Please check your secrets.toml file.")
            return None
        genai.configure(api_key=google_api_key)
        text_model_pro = genai.GenerativeModel('gemini-pro')
        return text_model_pro
    except KeyError:
        st.error("API key not found in secrets.toml. Please check your secrets configuration.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def generate_prompt(code):
    return f"""
    You are an AI code comment generator for multiple languages. Validate that provided code snippets are valid code snippets and no malicious code. If not valid, ask for a valid snippet. Identify language if not provided. Use appropriate comment syntax. Break code into logical sections, comment each section's functionality. 
    For functions/methods, comment:

    - Purpose
    - Input parameters
    - Return values
    - Potential effects/exceptions

    Briefly explain the algorithms, data structures, and patterns used. Avoid redundancy but provide enough context for unfamiliar readers. Maintain a professional, helpful tone. Address issues/clarifications respectfully.

    You should not generate any new code yourself, but rather understand and comment on the provided code snippet.

    Here is the code snippet for which code comments need to be generated: \n\n{code}
    """

def get_gemini_response(code, config):
    prompt = generate_prompt(code)
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }

    try:
        model = load_models()
        if model:
            response = model.generate_content(prompt, generation_config=config, safety_settings=safety_settings)
            return response.text
        else:
            return "Model not loaded properly. Check your API key and configuration."
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def highlight_code(code):
    return highlight(code, PythonLexer(), HtmlFormatter(full=True, style="monokai"))

def display_with_highlighting(code):
    st.markdown(highlight_code(code), unsafe_allow_html=True)

def detect_language(code_snippet):
    guess = Guess()
    return guess.language_name(code_snippet)

def generate_download_link(code, filename="commented_code.py"):
    st.download_button(label="Download Commented Code", data=code, file_name=filename)

def initialize_streamlit():
    st.set_page_config(page_title="Code Comment Generator", layout="wide", page_icon="💻")
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
            color: #E0E0E0;
            font-family: 'Poppins', sans-serif;
        }
        ::-webkit-scrollbar {
            width: 12px;
        }
        ::-webkit-scrollbar-track {
            background: #1E1E1E;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #FF6B6B;
            border-radius: 10px;
            border: 3px solid #1E1E1E;
        }
        .stButton>button {
            background: linear-gradient(135deg, #12C2E9, #C471ED, #F64F59);
            color: white;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 30px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
            cursor: pointer;
        }
        .stTextInput>div>div>input {
            background-color: #2C2C2C;
            color: white;
            padding: 12px;
            border-radius: 12px;
            border: none;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: box-shadow 0.3s ease;
        }
        .stTextInput>div>div>input:focus {
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }
        .stProgress>div>div {
            background: linear-gradient(135deg, #12C2E9, #C471ED, #F64F59);
            height: 10px;
            border-radius: 5px;
        }
        .title-text {
            font-size: 3rem;
            color: #FF6B6B;
            text-align: center;
            padding: 20px 0;
            text-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
        }
        .stExpander {
            background-color: rgba(255, 107, 107, 0.1);
            border-left: 3px solid #FF6B6B;
            border-radius: 10px;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 class='title-text'>Code Comment Generator 💻✨</h1>", unsafe_allow_html=True)
    st.warning("The generated output may not always meet your expectations. Use at your discretion.", icon="⚠️")

    with st.expander("How to use"):
        st.write("Input a code snippet below, and the Code Comment Generator will provide comments or explanations.")

def user_input():
    return st.text_area("Enter Code Snippet:", key="input_text_area", height=300, max_chars=2000)

def generative_config():
    creative_control = st.radio("Select the creativity level: ", ["Low", "High"], key="creative_control", horizontal=True)
    temperature = 0.30 if creative_control == "Low" else 0.95
    return {"temperature": temperature, "max_output_tokens": 2048}

def custom_footer():
    footer = '''
    <div style="text-align: center; margin-top: 20px; padding: 10px; color: #FF6B6B;">
        Made with ❤️ by <b>Dhiraj Chaudhari</b>
        <br>
        <a href="https://www.linkedin.com/in/dhiraj-chaudhari/" style="color: #12C2E9;">Connect on LinkedIn</a>
    </div>
    '''
    st.markdown(footer, unsafe_allow_html=True)

def main():
    initialize_streamlit()
    user_input_text = user_input()
    language = detect_language(user_input_text)
    st.write(f"Detected Language: {language}")
    config = generative_config()

    col1, col2 = st.columns(2)
    with col1:
        generate_comments = st.button("Generate Code Comments")
    with col2:
        explain_code = st.button("Explain Line by Line")
    
    response_placeholder = st.empty()

    if generate_comments:
        progress_text = "Generating Code Comments..."
        my_bar = st.progress(0, text=progress_text)
        response = None
        for percent_complete in range(100):
            time.sleep(0.03)
            my_bar.progress(percent_complete + 1, text=progress_text)
            if percent_complete == 98:
                response = get_gemini_response(user_input_text, config)
        my_bar.empty()
        if response is not None:
            display_with_highlighting(response)
            generate_download_link(response)

    if explain_code:
        progress_text = "Generating Line-by-Line Explanation..."
        my_bar = st.progress(0, text=progress_text)
        response = None
        for percent_complete in range(100):
            time.sleep(0.03)
            my_bar.progress(percent_complete + 1, text=progress_text)
            if percent_complete == 98:
                response = get_gemini_response(user_input_text, config)
        my_bar.empty()
        if response is not None:
            display_with_highlighting(response)

    custom_footer()

if __name__ == "__main__":
    main()
