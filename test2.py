import pyttsx3
import time
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    engine = pyttsx3.init("dotnetspeech")
    print("[DEBUG] Engine initialized.")
    try:
        # Call say and directly invoke processing methods
        engine.say("The quick brown fox jumped over the lazy dog.")
        print("[DEBUG] Say method executed.")
        # engine.runAndWait()
        # print("[DEBUG] runAndWait executed.")
    except Exception as e:
        print(f"[ERROR] Exception in processing: {e}")
except Exception as e:
    print(f"[ERROR] Exception during initialization: {e}")