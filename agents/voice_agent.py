import speech_recognition as sr
from typing import Optional

def listen_emergency() -> str:
    """
    Listen to user voice input and convert to text.
    
    Returns:
        Transcribed text or error message
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Speak your emergency...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)

            try:
                text = recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError as e:
                print(f"Speech recognition service error: {str(e)}")
                return "Speech recognition service unavailable"
            except Exception as e:
                print(f"Error in speech recognition: {str(e)}")
                return "Could not process audio"

    except sr.WaitTimeoutError:
        return "No speech detected"
    except OSError as e:
        print(f"Microphone error: {str(e)}")
        return "Microphone not available"
    except Exception as e:
        print(f"Error in voice agent: {str(e)}")
        return "Voice input failed"