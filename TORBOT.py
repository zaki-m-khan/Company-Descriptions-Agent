from dotenv import load_dotenv
from io import StringIO
import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
import requests
import PyPDF2

#loads environment variables from a .env file, configures gemini with google api key, returns SerpAPI key
def load_env_variables():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return os.getenv("SERPAPI_API_KEY")

#initializes gemini model and starts chat with empty history represented as an array
def initialize_gemini():
    model = genai.GenerativeModel("gemini-pro")
    return model.start_chat(history=[])

#uses SerpAPI for online search from Google & returns results in JSON format
def get_search_results(query, serp_api_key):
    params = {"engine": "google", "q": query, "api_key": serp_api_key}
    response = requests.get("https://serpapi.com/search", params=params)
    return response.json()

#sends instructions to the chatbot and reuturns response
def get_gemini_response(chat, instructions):
    response = chat.send_message(instructions, stream=True)
    return response

# reads a file and per the StringIO documentation handles the encoding issues
def read_file(uploaded_file):
    try:
        return StringIO(uploaded_file.getvalue().decode("utf-8"))
    except UnicodeDecodeError:
        try:
            return StringIO(uploaded_file.getvalue().decode("ISO-8859-1"))
        except UnicodeDecodeError:
            st.error("Unable to read file. Unsupported encoding.")
            return None

#reads pdf file
def read_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = "".join(page.extract_text() for page in pdf_reader.pages)
    return text

# writes to the stream the company names from the pdf or a csv, uses Pandas package to display info from CSV
def handle_uploaded_file(uploaded_file):
    company_names = []
    if uploaded_file.name.endswith(".pdf"):
        pdf_text = read_pdf(uploaded_file)
        company_names = [name.strip() for name in pdf_text.splitlines()]
        st.write(", ".join(company_names))
    else:
        string_data = read_file(uploaded_file)
        if string_data is not None:
            file_content = string_data.read()
            st.write(file_content)
            string_data.seek(0)
            dataframe = pd.read_csv(string_data)
            st.write(dataframe)
            company_names = dataframe.iloc[:, 0].tolist()
            st.write(", ".join(company_names))
    return company_names

# uses chain-of-thought prompting to get the most optimal search results for a company
def construct_instructions(name, search_summary):
    instructions = (
        f"I am a company analyst and need to collect extensive company descriptions. "
        f"The user who inputted the prompt MUST input a valid company name. If the user does not input a valid company name, reprompt the user to input a company name. "
        f"The user may input a list of names split by commas. In that case, you must follow the instructions on each of the company that is split by commas. Do not miss a company."
        f"Can you help me create a detailed and comprehensive description for the following company: {name}?\n\n"
        f"### Instructions:\n"
        f"1. **Information Gathering**: Search the internet to find extensive and relevant information about **{name}**. Utilize a wide variety of reliable websites.\n"
        f"2. **Information Verification**: Double-check the collected information to ensure accuracy and relevance. Rely only on verified and trustworthy sources.\n"
        f"3. **Description Creation**: Based on the verified information, write a clear and comprehensive company description.\n"
        f"4. **Format**: Focus on including all significant details about the company, highlighting its main practices and unique aspects. Ensure the description is detailed and thorough, without any additional headings or sections. "
        f"### Search Summary:\n{search_summary}\n"
    )
    return instructions

# saves comp descriptions to a downloadable text file
def save_comp_desc(comp_text):
    with open("comp_text.txt", "w") as file:
        file.write(comp_text)

def main():
    # Load environment variables and configure APIs
    serp_api_key = load_env_variables()
    
    # Initialize Gemini model and chat
    chat = initialize_gemini()

    # Initialize Streamlit app
    st.set_page_config(page_title="Company Description Lookup")
    st.header("Company Description Lookup Agent")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Input and button
    company_name = st.text_input("Enter the company name:", key="input")
    uploaded_file = st.file_uploader("Choose a file")
    company_names = handle_uploaded_file(uploaded_file) if uploaded_file else []

    submit = st.button("Get Description")

    if submit and (company_name or company_names):
        if company_name:
            company_names.append(company_name)
        for name in company_names:
            search_query = f"{name} company description"
            search_results = get_search_results(search_query, serp_api_key)
            search_summary = "\n".join(
                f"{result['title']}: {result['snippet']}"
                for result in search_results.get("organic_results", [])
            )
            instructions = construct_instructions(name, search_summary)
            response = get_gemini_response(chat, instructions)
            st.session_state["chat_history"].append(("User", name))

            full_response = "".join(chunk.text for chunk in response)
            st.session_state["chat_history"].append(("Bot", full_response))
            st.text_area("Full Company Description", value=full_response, height=200)

    st.subheader("Chat History")
    for role, text in st.session_state["chat_history"]:
        st.write(f"{role}: {text}")

    if st.button("Save Company Descriptions"):
        comp_desc_text = "\n".join(text for role, text in st.session_state["chat_history"] if role == "Bot")
        save_comp_desc(comp_desc_text)
        with open("comp_text.txt", "rb") as file:
            st.download_button(
                label="Download Company Descriptions",
                data=file,
                file_name="comp_text.txt",
                mime="text/plain",
            )

if __name__ == "__main__":
    main()
