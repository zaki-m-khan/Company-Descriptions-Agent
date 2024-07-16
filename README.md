# Company-Descriptions-Agent
As part of my time as a Research Assistant at the Technical University, a PHD student tasked me with creating an AI agent to generate company descriptions given a list of companies. I used a mixture of past programming experience, online tutorials, reading API documentation, and generative AI for small tweaks. 

## Overview

This project involves a Streamlit web application that leverages multiple APIs to generate detailed company descriptions. It uses Google Generative AI (Gemini) for chatbot capabilities and SerpAPI for online search results.

## Features

- **Load Environment Variables**: Load API keys and configure Gemini.
- **Initialize Gemini Model**: Start a chat session with Gemini.
- **Search Results**: Use SerpAPI to fetch search results.
- **Chat with Gemini**: Send instructions to Gemini and get a response.
- **File Handling**: Read and process CSV and PDF files.
- **Company Description Generation**: Generate and display company descriptions.
- **Save Descriptions**: Save generated descriptions to a text file.

## Installation

To install the required packages, run the following command:
pip install streamlit pandas requests python-dotenv google-generativeai PyPDF2

You must create your .env file giving reference to your API keys. Here is an example of the .env file:

GOOGLE_API_KEY = "xxxxxx"

SERPAPI_API_KEY = "xxxxx"
