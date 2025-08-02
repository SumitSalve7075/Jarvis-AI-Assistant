import speech_recognition as sr
import pyttsx3
import webbrowser
import pywhatkit
import google.generativeai as genai

# Initialize Text-to-Speech engine
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Take voice command from microphone
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not get that.")
        return ""
    except sr.RequestError:
        speak("Service unavailable.")
        return ""

# Configure Gemini AI
genai.configure(api_key="")
model = genai.GenerativeModel('models/gemini-1.5-pro')
chat = model.start_chat(history=[])

# Process user's voice command
def process_query(query):
    if "play" in query and "song" in query:
        song = query.replace("play", "").replace("song", "").strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)
    elif "open google" in query:
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "exit" in query or "stop" in query:
        speak("Goodbye!")
        exit()
    else:
        speak("Thinking...")
        try:
            response = chat.send_message(query)
            speak(response.text)
        except Exception as e:
            speak("Something went wrong.")
            print("Gemini error:", e)

# Main loop
if __name__ == "__main__":
    speak("Hello, I am Jarvis. How can I help you?")
    while True:
        user_query = take_command()
        if user_query:
            process_query(user_query)
