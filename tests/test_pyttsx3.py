from __future__ import annotations

import sys
import wave
from typing import TYPE_CHECKING
from unittest import mock

import pytest

import pyttsx3

if TYPE_CHECKING:
    from pathlib import Path

quick_brown_fox = "The quick brown fox jumped over the lazy dog."


@pytest.fixture
def engine(driver_name: str | None = None) -> pyttsx3.engine.Engine:
    """Fixture for initializing pyttsx3 engine."""
    engine = pyttsx3.init(driver_name)
    yield engine
    engine.stop()  # Ensure the engine stops after tests


def test_engine_name(engine) -> None:
    expected = pyttsx3.engine.default_engine_by_sys_platform()
    assert engine.driver_name == expected
    assert str(engine) == expected
    assert repr(engine) == f"pyttsx3.engine.Engine('{expected}', debug=False)"


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_speaking_text(engine) -> None:
    engine.say("Sally sells seashells by the seashore.")
    engine.say(quick_brown_fox)
    print(list(pyttsx3._activeEngines.values()))
    engine.runAndWait()


@pytest.mark.skipif(sys.platform not in ("darwin", "ios"), reason="Testing only on macOS and iOS")
def test_apple_avspeech_voices(engine):
    import platform

    macos_version, _, macos_hardware = platform.mac_ver()
    print(f"{sys.platform = }, {macos_version = } on {macos_hardware = }")
    print(list(pyttsx3._activeEngines))
    print(engine)
    # assert str(engine) == "avsynth", "Expected engine name to be avsynth on macOS and iOS"
    voice = engine.getProperty("voice")
    # On macOS v14.x, the default nsss voice is com.apple.voice.compact.en-US.Samantha.
    # ON macOS v15.x, the default nsss voice is "".
    # ON macOS v15.x, the default avsynth voice is None.

    assert voice in (
        None,
        "",
        "com.apple.voice.compact.en-US.Samantha",
    ), f"Expected default voice {voice} to be com.apple.voice.compact.en-US.Samantha"
    voices = engine.getProperty("voices")
    # On macOS v14.x, nsss has 143 voices.
    # On macOS v15.x, nsss has 176 voices
    print(f"On macOS v{macos_version}, {engine} has {len(voices) = } voices.")
    assert len(voices) in (176, 143), "Expected 176 or 143 voices on macOS and iOS"
    # print("\n".join(voice.id for voice in voices))
    en_us_voices = [voice for voice in voices if voice.id.startswith("com.apple.eloquence.en-US.")]
    assert len(en_us_voices) == 8, "Expected 8 com.apple.eloquence.en-US voices on macOS and iOS"
    names = []
    for _voice in en_us_voices:
        engine.setProperty("voice", _voice.id)
        name = _voice.id.split(".")[-1]
        names.append(name)
        engine.say(f"{name} says hello.")
    name_str = ", ".join(names)
    assert name_str == "Eddy, Flo, Grandma, Grandpa, Reed, Rocko, Sandy, Shelley"
    print(f"({name_str})", end=" ", flush=True)
    engine.runAndWait()
    engine.setProperty("voice", voice)  # Reset voice to original value


@pytest.mark.skipif(sys.platform not in ("darwin", "ios"), reason="Testing only on macOS and iOS")
def test_apple_nsss_voices(engine):
    import platform

    macos_version, _, macos_hardware = platform.mac_ver()
    print(f"{sys.platform = }, {macos_version = } on {macos_hardware = }")
    print(list(pyttsx3._activeEngines))
    print(engine)
    assert str(engine) == "nsss", "Expected engine name to be nsss on macOS and iOS"
    voice = engine.getProperty("voice")
    # On macOS v14.x, the default nsss voice is com.apple.voice.compact.en-US.Samantha.
    # ON macOS v15.x, the default nsss voice is ""
    assert voice in (
        "",
        "com.apple.voice.compact.en-US.Samantha",
    ), "Expected default voice to be com.apple.voice.compact.en-US.Samantha on macOS and iOS"
    voices = engine.getProperty("voices")
    # On macOS v14.x, nsss has 143 voices.
    # On macOS v15.x, nsss has 176 voices
    print(f"On macOS v{macos_version}, {engine} has {len(voices) = } voices.")
    assert len(voices) in (176, 143), "Expected 176 or 143 voices on macOS and iOS"
    # print("\n".join(voice.id for voice in voices))
    en_us_voices = [voice for voice in voices if voice.id.startswith("com.apple.eloquence.en-US.")]
    assert len(en_us_voices) == 8, "Expected 8 com.apple.eloquence.en-US voices on macOS and iOS"
    names = []
    for _voice in en_us_voices:
        engine.setProperty("voice", _voice.id)
        name = _voice.id.split(".")[-1]
        names.append(name)
        engine.say(f"{name} says {quick_brown_fox}")
    name_str = ", ".join(names)
    assert name_str == "Eddy, Flo, Grandma, Grandpa, Reed, Rocko, Sandy, Shelley"
    print(f"({name_str})", end=" ", flush=True)
    engine.runAndWait()
    engine.setProperty("voice", voice)  # Reset voice to original value


def test_saving_to_file(engine, tmp_path: Path) -> None:
    """
    Apple writes .aiff, not .wav.  https://github.com/nateshmbhat/pyttsx3/issues/361
    """
    test_file = tmp_path / "test.wav"  # Using .wav for easier validation

    # Save the speech to a file
    engine.save_to_file("Hello World", str(test_file))
    engine.runAndWait()

    # Check if the file was created
    assert test_file.exists(), "The audio file was not created"

    # Check if the file is not empty
    assert test_file.stat().st_size > 0, "The audio file is empty"

    # Check if the file is a valid .wav file using the wave module
    try:
        with wave.open(str(test_file), "rb") as wf:
            assert wf.getnchannels() == 1, "The audio file should have 1 channel (mono)"
            assert wf.getsampwidth() == 2, "Audio file sample width should be 2 bytes"
            assert wf.getframerate() == 22050, "Audio file framerate should be 22050 Hz"
    except wave.Error:
        assert sys.platform in {"darwin", "ios"}, "Apple writes .aiff, not .wav files."


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_listening_for_events(engine) -> None:
    onStart = mock.Mock()
    onWord = mock.Mock()
    onEnd = mock.Mock()

    engine.connect("started-utterance", onStart)
    engine.connect("started-word", onWord)
    engine.connect("finished-utterance", onEnd)

    engine.say(quick_brown_fox)
    engine.runAndWait()

    # Ensure the event handlers were called
    assert onStart.called
    assert onWord.called
    assert onEnd.called


@pytest.mark.skipif(
    sys.platform in ("linux", "win32"),
    reason="TODO: Fix this test to pass on Linux and Windows",
)
def test_interrupting_utterance(engine) -> None:
    def onWord(name, location, length) -> None:
        if location > 10:
            engine.stop()

    onWord_mock = mock.Mock(side_effect=onWord)
    engine.connect("started-word", onWord_mock)
    engine.say(quick_brown_fox)
    engine.runAndWait()

    # Check that stop was called
    assert onWord_mock.called


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_speech_rate(engine) -> None:
    rate = engine.getProperty("rate")
    rate_plus_fifty = rate + 50
    engine.setProperty("rate", rate_plus_fifty)
    engine.say(f"{rate_plus_fifty = } {quick_brown_fox}")
    engine.runAndWait()
    engine.setProperty("rate", rate)  # Reset rate to original value


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_volume(engine) -> None:
    volume = engine.getProperty("volume")
    volume_minus_a_quarter = volume - 0.25
    engine.setProperty("volume", volume_minus_a_quarter)
    engine.say(f"{volume_minus_a_quarter = } {quick_brown_fox}")
    engine.runAndWait()
    engine.setProperty("volume", volume)  # Reset volume to original value


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_changing_voices(engine) -> None:
    voices = engine.getProperty("voices")
    for voice in voices:  # TODO: This could be lots of voices! (e.g. 176 on macOS v15.x)
        engine.setProperty("voice", voice.id)
        engine.say(f"{voice.id = }. {quick_brown_fox}")
    engine.runAndWait()


@pytest.mark.skipif(sys.platform == "win32", reason="TODO: Fix this test to pass on Windows")
def test_running_driver_event_loop(engine) -> None:
    def onStart(name) -> None:
        print("starting", name)

    def onWord(name, location, length) -> None:
        print("word", name, location, length)

    def onEnd(name, completed) -> None:
        if name == "fox":
            engine.say("What a lazy dog!", "dog")
        elif name == "dog":
            engine.endLoop()

    engine.connect("started-utterance", onStart)
    engine.connect("started-word", onWord)
    engine.connect("finished-utterance", onEnd)
    engine.say(quick_brown_fox, "fox")
    engine.startLoop()


@pytest.mark.skipif(
    sys.platform in ("linux", "win32"),
    reason="TODO: Fix this test to pass on Linux and Windows",
)
def test_external_event_loop(engine) -> None:
    def externalLoop() -> None:
        for _ in range(5):
            engine.iterate()

    engine.say(quick_brown_fox, "fox")
    engine.startLoop(False)
    externalLoop()
    engine.endLoop()
