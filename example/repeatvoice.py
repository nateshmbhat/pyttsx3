import pyttsx3 # pyttsx3 is a text-to-speech conversion library in Python
import speech_recognition as s #Google Speech API in Python

#Functional programming Model

def text_to_speech(text):
    #engine connects us to hardware in this case 
    eng= pyttsx3.init()
    #Engine created 
    eng.say(text)
    #Runs for small duration of time ohterwise we may not be able to hear
    eng.runAndWait()

    
def speech_to_text():
    r=s.Recognizer()# an object r which recognises the voice
    with s.Microphone() as source:
        #when using with statement. The with statement itself ensures proper acquisition and release of resources
        print(r.recognize_google(audio))
        text_to_speech(r.recognize_google(audio)) 
        
speech_to_text()
