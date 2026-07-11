import speech_recognition as sr

def listen_emergency():

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak your emergency...")

        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            return text

        except:
            return "Could not understand audio"