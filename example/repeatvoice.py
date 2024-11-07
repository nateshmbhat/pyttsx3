# pip3 install SpeechRecognition
import speech_recognition  # A speech-to-text conversion library in Python

import pyttsx3  # A text-to-speech conversion library in Python


def text_to_speech(text) -> None:
    # engine connects us to hardware in this case
    eng = pyttsx3.init()
    # Engine created
    eng.say(text)
    # Runs for small duration of time otherwise we may not be able to hear
    eng.runAndWait()


def speech_to_text() -> None:
    recognizer = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as microphone:
        audio = recognizer.listen(microphone)
    text = recognizer.recognize_google(audio)
    print(text)
    text_to_speech(text)


if __name__ == "__main__":
    speech_to_text()
