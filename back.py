from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import openai
import os

app = Flask(__name__)

# Set OpenAI API Key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt):
    """Query OpenAI GPT API for any question."""
    if not openai.api_key:
        return "OpenAI API key is missing."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error getting response from OpenAI: {e}"

@app.route("/process_voice", methods=["POST"])
def process_voice():
    """API endpoint to process user input."""
    data = request.get_json()
    user_input = data.get("message", "").lower()

    if not user_input:
        return jsonify({"response": "Please say something."})

    if "exit" in user_input or "stop" in user_input or "quit" in user_input:
        return jsonify({"response": "Goodbye!"})

    response = ask_gpt(user_input)
    return jsonify({"response": response})

# -------------------- Voice Assistant CLI Mode --------------------

def listen():
    """Listens for user input and converts it to text."""
    recognizer = sr.Recognizer()
    microphone_count = len(sr.Microphone.list_microphone_names())

    if microphone_count == 0:
        print("No microphones found. Please ensure a microphone is connected.")
        return ""

    device_index = 0  # Default to first microphone

    with sr.Microphone(device_index=device_index) as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"User said: {text}")
        return text.lower()

    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def speak(text):
    """Converts text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    """Main loop for the voice assistant."""
    while True:
        user_input = listen()
        if user_input:
            if "exit" in user_input or "stop" in user_input or "quit" in user_input:
                print("Goodbye!")
                speak("Goodbye!")
                break

            answer = ask_gpt(user_input)
            print(answer)
            speak(answer)

if __name__ == "__main__":
    # Run Flask API
    app.run(debug=True)
    # Uncomment below line to run voice assistant in terminal mode
    # main()
