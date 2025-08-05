import pyttsx3
import speech_recognition as sr
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
import sys

# ====================================================================
# --- AI Setup: Your API Key ---
# ====================================================================

# IMPORTANT: Your previous API key was reported as invalid.
# Please replace "YOUR_NEW_API_KEY_HERE" with a brand new, valid API key
# obtained from https://aistudio.google.com/apikey
GOOGLE_API_KEY = "Adding You'r API KEY "  # <--- UPDATED WITH YOUR NEW KEY
genai.configure(api_key=GOOGLE_API_KEY)

# Global variables for the AI model and chat session
model = None
chat = None


# ====================================================================
# --- Core Assistant Functions ---
# ====================================================================

def say(text):
    """
    Converts text to speech using the pyttsx3 library.
    This allows Jarvis to speak its responses.
    """
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as err:
        print(f"Error with text-to-speech: {err}")


def takeCommand():
    """
    Listens for user voice input from the microphone and converts it to text
    using Google's Web Speech API.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Adjust for ambient noise to improve recognition accuracy
        r.adjust_for_ambient_noise(source)
        # Pause threshold for how long to wait for a phrase to start
        r.pause_threshold = 0.8
        print("Listening...")
        try:
            # Listen for audio with a timeout and phrase time limit
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            print("Recognizing...")
            # Use Google Speech Recognition to convert audio to text
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            # Handle cases where speech is unintelligible
            print("Sorry, I could not understand the audio.")
            return "None"
        except sr.RequestError:
            # Handle cases where there's no internet connection or API issues
            print("Could not request results from the speech recognition service. Check your internet connection.")
            return "None"
        except Exception as err:
            # Catch any other unexpected errors during listening
            print(f"An unexpected error occurred during listening: {err}")
            return "None"


def initialize_model():
    """
    Dynamically finds and initializes an available Gemini model that supports
    content generation. This helps prevent '404 model not found' errors.
    """
    global model, chat

    print("Initializing AI model...")
    available_models = []
    try:
        # List all models accessible with the provided API key
        for m in genai.list_models():
            # Check if the model supports generating content (text responses)
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except Exception as err:
        print(f"Error listing models. Please check your API key and internet connection: {err}")
        return False

    print(f"Found available models: {available_models}")

    # Prioritize which model to use. 'gemini-2.5-flash-lite' is preferred
    # as per your last query, followed by other stable versions.
    preferred_models = ['gemini-2.5-flash-lite', 'gemini-1.5-flash-latest', 'gemini-1.0-pro-latest', 'gemini-1.0-pro']
    selected_model_name = None

    # Iterate through preferred models to find the first available one
    for p_model in preferred_models:
        full_model_name = f'models/{p_model}'
        if full_model_name in available_models:
            selected_model_name = p_model
            break  # Found a suitable model, exit loop

    if selected_model_name:
        try:
            # Initialize the generative model and start a chat session
            model = genai.GenerativeModel(selected_model_name)
            chat = model.start_chat(history=[])
            print(f"Successfully initialized with model: {selected_model_name}")
            return True
        except Exception as err:
            print(f"Error initializing model '{selected_model_name}': {err}")
            return False
    else:
        print("No suitable Gemini model found with 'generateContent' support.")
        print("Please check your API key and the Google AI Studio console for available models.")
        return False


def start_chat_mode():
    """
    Enters a text-based, interactive chat loop with the AI model.
    The user can type questions directly.
    """
    say("Switched to chat mode. You can type your questions now.")
    print("\n--------------------------------------------------")
    print("      Chat with Jarvis (Type 'exit' to end)       ")
    print("--------------------------------------------------\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "stop", "goodbye"]:
                say("Exiting chat mode. I'm back to listening for voice commands.")
                break

            print("Jarvis: Thinking...")
            try:
                # Send user input to the Gemini model with a timeout
                response = chat.send_message(user_input, stream=True, request_options={'timeout': 60})

                ai_response = ""
                # Stream the response chunks to build the full answer
                for chunk in response:
                    ai_response += chunk.text

                if ai_response:  # Check if the response is not empty
                    print(f"Jarvis: {ai_response}\n")
                    say(ai_response)
                else:
                    print("Jarvis: I received an empty response. Please try again.")
                    say("I received an empty response. Please try again.")
            except GoogleAPIError as api_err:
                # Catch specific Google API errors (e.g., timeouts, invalid requests)
                print(f"An API error occurred: {api_err}")
                say("Sorry, the AI took too long to respond or encountered an API error. Please try again.")
            except Exception as err:
                # Catch any other unexpected errors during AI interaction
                print(f"An unexpected error occurred during AI interaction: {err}")
                say("Sorry, I encountered an error. Please try again.")

        except Exception as err:
            # Catch errors within the chat mode loop itself
            print(f"An error occurred in chat mode: {err}")
            say("Sorry, I encountered an error. Please try again.")


# ====================================================================
# --- Main Logic: The core of the assistant's loop ---
# ====================================================================

if __name__ == '__main__':
    # Initialize the AI model at the start of the program
    if not initialize_model():
        say("I'm sorry, I could not initialize the AI model. Please check your API key and try again.")
        sys.exit(1)  # Exit if the AI model cannot be initialized

    say("Hello, I am Jarvis AI. How can I help you?")

    try:
        while True:
            # Listen for voice commands
            query = takeCommand()

            if query == "None":
                continue  # If no command was understood, continue listening

            # Check for the command to enter text-based chat mode
            if "talk to me" in query or "start chat" in query:
                start_chat_mode()
                continue  # Return to voice command listening after chat mode exits

            # This block handles any other voice commands by sending them to the AI.
            # All previous functionalities (open YouTube, date/time, folder ops)
            # have been removed as requested, and a message is given if they are attempted.
            elif "open youtube" in query or "the date" in query or "create a folder" in query or "delete a folder" in query or "open music" in query or "play" in query:
                say("I am currently in conversational mode only. That functionality has been removed.")

            else:
                # If the command is not a special action, send it to the AI for a response
                try:
                    print("Jarvis: Thinking...")
                    # Send the voice query to the Gemini model with a timeout
                    response = chat.send_message(query, stream=True, request_options={'timeout': 60})
                    ai_response = ""
                    for chunk in response:
                        ai_response += chunk.text

                    if ai_response:  # Ensure the AI returned a non-empty response
                        say(ai_response)
                    else:
                        print("Jarvis: I received an empty response. Please try again.")
                        say("I received an empty response. Please try again.")
                except GoogleAPIError as api_err:
                    print(f"An API error occurred: {api_err}")
                    say("Sorry, the AI took too long to respond or encountered an API error. Please try again.")
                except Exception as err:
                    say("I'm sorry, I cannot process that request right now. There was an unexpected error with the AI.")
                    print(err)

    except KeyboardInterrupt:
        # Gracefully exit the program if the user presses Ctrl+C
        print("\nProgram interrupted by user. Goodbye!")
        sys.exit(0)
