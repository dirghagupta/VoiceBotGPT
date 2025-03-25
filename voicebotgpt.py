import os
import openai
import speech_recognition as sr
import pygame
from gtts import gTTS
from flask import Flask, request, jsonify

# ✅ Define Flask app
app = Flask(__name__)

# ✅ OpenAI API Key (Store it securely)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Store API Key in Env Variable
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OpenAI API Key not found! Set the OPENAI_API_KEY environment variable.")
openai.api_key = OPENAI_API_KEY

# ✅ Home Route
@app.route('/')
def home():
    return "Voice AI Bot is Running!"

# ✅ Speech-to-Text Function
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand."
    except sr.RequestError:
        return "Could not request results, please check your connection."

# ✅ Generate AI Response
def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error generating response: {str(e)}"

# ✅ Text-to-Speech
def text_to_speech(response_text):
    try:
        tts = gTTS(text=response_text, lang='en')
        filename = "response.mp3"
        tts.save(filename)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.delay(100)  # Avoids CPU overuse
        os.remove(filename)
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")

# ✅ Chat API Route
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("text", "")
    response_text = generate_response(user_input)
    text_to_speech(response_text)
    return jsonify({"response": response_text})

# ✅ Run Flask App
if __name__ == "__main__":
    print("🚀 Voice AI Bot Running...")
    app.run(host="0.0.0.0", port=5001, debug=True)

