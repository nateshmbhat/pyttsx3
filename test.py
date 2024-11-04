import time
import ctypes
from unittest import mock

import pyttsx3

# Initialize the pyttsx3 engine
engine = pyttsx3.init("espeak")


# Set up event listeners for debugging
def on_start(name):
    print(f"[DEBUG] Started utterance: {name}")
    print(f"Started utterance: {name}")


def on_word(name, location, length):
    print(f"Word: {name} at {location} with length {length}")
    # Interrupt the utterance if location is above a threshold to simulate test_interrupting_utterance
    if location > 10:
        print("Interrupting utterance by calling endLoop...")
        engine.stop()  # Directly call endLoop instead of stop


def on_end(name, completed):
    print(f"Finished utterance: {name}, completed: {completed}")


# Connect the listeners
engine.connect("started-utterance", on_start)
engine.connect("started-word", on_word)
engine.connect("finished-utterance", on_end)


# Demo for test_interrupting_utterance
def demo_interrupting_utterance():
    print("\nRunning demo_interrupting_utterance...")
    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()
    engine.endLoop()


# Demo for test_external_event_loop
def demo_external_event_loop():
    print("\nRunning demo_external_event_loop...")

    def external_loop():
        # Simulate external loop iterations
        for _ in range(5):
            engine.iterate()  # Process engine events
            time.sleep(0.5)  # Adjust timing as needed

    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.startLoop(False)  # Start loop without blocking
    external_loop()
    engine.endLoop()  # End the event loop explicitly


# Run demos
demo_interrupting_utterance()
from pyinstrument import Profiler

# Initialize the profiler
profiler = Profiler()

# Start profiling
profiler.start()

# Run the external event loop demo
demo_external_event_loop()

# Stop profiling
profiler.stop()

# Print the profiling report
profiler.print()
