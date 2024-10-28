import os
import sys
from unittest import mock

import pytest
import wave

import pyttsx3


@pytest.fixture
def engine():
    """Fixture for initializing pyttsx3 engine."""
    engine = pyttsx3.init()
    yield engine
    engine.stop()  # Ensure the engine stops after tests


# Test for speaking text
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_speaking_text(engine):
    engine.say("Sally sells seashells by the seashore.")
    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()


# Test for saving voice to a file with additional validation
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
# @pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
@pytest.mark.xfail(sys.platform == "darwin", reason="TODO: Fix this test to pass on macOS")
def test_saving_to_file(engine, tmp_path):
    test_file = tmp_path / "test.wav"  # Using .wav for easier validation

    # Save the speech to a file
    engine.save_to_file("Hello World", str(test_file))
    engine.runAndWait()

    # Check if the file was created
    assert test_file.exists(), "The audio file was not created"

    # Check if the file is not empty
    assert test_file.stat().st_size > 0, "The audio file is empty"

    # Check if the file is a valid .wav file using the wave module
    with wave.open(str(test_file), "rb") as wf:
        assert wf.getnchannels() == 1, "The audio file should have 1 channel (mono)"
        assert wf.getsampwidth() == 2, "The audio file sample width should be 2 bytes"
        assert wf.getframerate() == 22050, "The audio file framerate should be 22050 Hz"


# Test for listening for events
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_listening_for_events(engine):
    onStart = mock.Mock()
    onWord = mock.Mock()
    onEnd = mock.Mock()

    engine.connect("started-utterance", onStart)
    engine.connect("started-word", onWord)
    engine.connect("finished-utterance", onEnd)

    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()

    # Ensure the event handlers were called
    assert onStart.called
    assert onWord.called
    assert onEnd.called


# Test for interrupting an utterance
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_interrupting_utterance(engine):
    def onWord(name, location, length):
        if location > 10:
            engine.stop()

    onWord_mock = mock.Mock(side_effect=onWord)
    engine.connect("started-word", onWord_mock)
    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()

    # Check that stop was called
    assert onWord_mock.called


# Test for changing voices
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_voices(engine):
    voices = engine.getProperty("voices")
    for voice in voices:
        engine.setProperty("voice", voice.id)
        engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()


# Test for changing speech rate
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_speech_rate(engine):
    rate = engine.getProperty("rate")
    engine.setProperty("rate", rate + 50)
    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()


# Test for changing volume
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_volume(engine):
    volume = engine.getProperty("volume")
    engine.setProperty("volume", volume - 0.25)
    engine.say("The quick brown fox jumped over the lazy dog.")
    engine.runAndWait()


# Test for running a driver event loop
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_running_driver_event_loop(engine):
    def onStart(name):
        print("starting", name)

    def onWord(name, location, length):
        print("word", name, location, length)

    def onEnd(name, completed):
        if name == "fox":
            engine.say("What a lazy dog!", "dog")
        elif name == "dog":
            engine.endLoop()

    engine.connect("started-utterance", onStart)
    engine.connect("started-word", onWord)
    engine.connect("finished-utterance", onEnd)
    engine.say("The quick brown fox jumped over the lazy dog.", "fox")
    engine.startLoop()


# Test for using an external event loop
# @pytest.mark.timeout(10)  # Set timeout to 10 seconds
@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_external_event_loop(engine):
    def externalLoop():
        for _ in range(5):
            engine.iterate()

    engine.say("The quick brown fox jumped over the lazy dog.", "fox")
    engine.startLoop(False)
    externalLoop()
    engine.endLoop()
