from transformers import pipeline
import requests
import os
from dotenv import load_dotenv
import openai
import streamlit as st
import tempfile


# Image to Text Generation
def img2text(url):
    image_to_text = pipeline('image-to-text', model="Salesforce/blip-image-captioning-base", max_new_tokens=100)
    text = image_to_text(url)
    return text[0]["generated_text"]


# Text to Story Generation
def generate_story(scenario):
    message = f"""
    You can generate a short story based on a simple narrative,
    the story should be no more than 100 words:

    CONTEXT: {scenario}
    STORY:
    """
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a story teller."},
        {"role": "user", "content": message}
    ])
    story = response["choices"][0]["message"]["content"]
    return story


# Story to Speech Generation
def text2speech(message):
    HUGGINGFACEHUB_API_TOKEN = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    API_URL = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
    payloads = {
        "inputs": message
    }
    response = requests.post(API_URL, headers=headers, json=payloads)
    with open('audio.mp3', 'wb') as file:
        file.write(response.content)


# Integration with streamlit
def main():
    load_dotenv()
    st.header("Turn _Images_ into Audio :red[Stories]")

    uploaded_file = st.file_uploader("Choose an image..", type='jpg')

    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with tempfile.NamedTemporaryFile(delete=False) as file:
            file.write(bytes_data)
            file_path = file.name

        st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

        scenario = img2text(file_path)
        story = generate_story(scenario)
        text2speech(story)

        with st.expander("Scenario"):
            st.write(scenario)
        with st.expander("Story"):
            st.write(story)

        st.audio("audio.mp3")


if __name__ == "__main__":
    main()
