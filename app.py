import streamlit as st
import google.generativeai as genai
import os
import webbrowser
import speech_recognition as sr
from googletrans import Translator
from PIL import Image
import requests
from io import BytesIO
import openai

# Get API key from secrets
api_key = st.secrets.get("API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("API key not found. Please add it to the secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.error("OpenAI API key not found. Please add it to the secrets.")

translator = Translator()

st.title("AI Assistant")

# Sidebar for selecting task
task = st.sidebar.selectbox("Select Task", ["Generate Response", "Translate Text", "Open Website", "Play Music"])

def get_audio_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        st.success(f"Recognized: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
        return ""

# Mapping of common website names to their URLs
website_mapping = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://www.twitter.com",
    "github": "https://www.github.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "reddit": "https://www.reddit.com",
    # Add more mappings as needed
}

def play_music(platform, song_name):
    platform_urls = {
        "spotify": "https://open.spotify.com/search/",
        "youtube": "https://www.youtube.com/results?search_query=",
        "apple music": "https://music.apple.com/search?term="
    }
    if platform.lower() in platform_urls:
        url = platform_urls[platform.lower()] + song_name.replace(" ", "+")
        webbrowser.open(url)
        st.success(f"Playing {song_name} on {platform}")
    else:
        st.error("Platform not recognized. Please enter a valid platform name.")

if task == "Generate Response":
    st.header("Generate Response")
    input_method = st.radio("Input Method", ("Text", "Audio"))
    if input_method == "Text":
        question = st.text_input("Please enter your question:")
    else:
        question = get_audio_input()
    
    response_area = st.empty()

    if st.button("Generate Response"):
        if question:
            response = model.generate_content(question)
            response_area.text_area("Response:", response.text, height=200)
        else:
            st.error("Please enter a question")

if task == "Translate Text":
    st.header("Translate Text")
    text_to_translate = st.text_area("Enter text to translate:")
    target_language = st.text_input("Enter target language (e.g., 'es' for Spanish):")
    translation_area = st.empty()

    if st.button("Translate"):
        if text_to_translate and target_language:
            translation = translator.translate(text_to_translate, dest=target_language)
            translation_area.text_area("Translation:", translation.text, height=200)
        else:
            st.error("Please enter text and target language")

if task == "Open Website":
    st.header("Open Website")
    website_name = st.text_input("Enter website name to open:")
    
    if st.button("Open"):
        if website_name:
            website_name = website_name.lower().strip()
            if website_name in website_mapping:
                url = website_mapping[website_name]
                webbrowser.open(url)
                st.success(f"Opened {website_name}")
            else:
                st.error("Website not recognized. Please enter a valid website name.")
        else:
            st.error("Please enter a website name")

if task == "Play Music":
    st.header("Play Music")
    platform = st.text_input("Enter music platform (e.g., 'Spotify', 'YouTube', 'Apple Music'):")
    song_name = st.text_input("Enter song name:")
    
    if st.button("Play"):
        if platform and song_name:
            play_music(platform, song_name)
        else:
            st.error("Please enter both platform and song name")

if st.button("Clear"):
    st.experimental_rerun()