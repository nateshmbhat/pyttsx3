from __future__ import annotations

import sys

import pytest

import pyttsx3

quick_brown_fox = "The quick brown fox jumped over the lazy dog."


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_engine_name(driver_name):
    engine = pyttsx3.init(driver_name)
    assert engine.driver_name == driver_name
    assert str(engine) == driver_name
    assert repr(engine) == f"pyttsx3.engine.Engine('{driver_name}', debug=False)"
    engine.stop()


@pytest.mark.skipif(
    sys.platform == "win32", reason="TODO: Make this test pass on eSpeak-NG on Windows"
)
@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_speaking_text(driver_name):
    engine = pyttsx3.init(driver_name)
    engine.say("Sally sells seashells by the seashore.")
    engine.say(quick_brown_fox)
    print(list(pyttsx3._activeEngines.values()), flush=True)
    engine.runAndWait()
    print(list(pyttsx3._activeEngines.values()), flush=True)
    engine.stop()


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_espeak_voices(driver_name):
    if driver_name != "espeak":
        pytest.skip(f"Skipping eSpeak-specific test for {driver_name}.")

    engine = pyttsx3.init(driver_name)
    original_voice = engine.getProperty("voice")

    assert str(engine) == "espeak", "Expected engine name to be 'espeak'"

    # Retrieve and print voices without modifying `voice` property
    # Linux eSpeak-NG v1.50 has 109 voices,
    # macOS eSpeak-NG v1.51 has 131 voices,
    # Windows eSpeak-NG v1.52-dev has 221 voices.
    voices = engine.getProperty("voices")
    print(f"{engine} has {len(voices)} voices.")
    assert len(voices) in {
        109,
        131,
        221,
    }, f"Expected 109, 131, or 221 voices in {engine}"

    # Filter English voices
    english_voices = [voice for voice in voices if voice.id.startswith("English")]
    # Linux eSpeak-NG v1.50 has 7 English voices,
    # macOS eSpeak-NG v1.51 and Windows eSpeak-NG v1.52-dev have 8 English voices.
    assert len(english_voices) in {7, 8}, "Expected 7 or 8 English voices"

    # Queue a single utterance for each voice without calling `runAndWait()` in a loop
    names = []
    for _voice in english_voices:
        engine.setProperty("voice", _voice.id)
        # English (America, New York City) --> America, New York City
        name = _voice.id[9:-1]  # Extract name for display
        names.append(name)
        engine.say(f"{name} says hello")  # Queue the utterance

    # Run all queued utterances at once
    engine.runAndWait()

    # Verify the names collected against expected values
    name_str = "|".join(names)
    expected = (
        "Caribbean|Great Britain|Scotland|Lancaster|West Midlands"
        "|Received Pronunciation|America|America, New York City"
    )
    no_nyc = expected.rpartition("|")[0]
    assert name_str in {expected, no_nyc}, f"Expected '{expected}' or '{no_nyc}'."
    print(f"({name_str.replace('|', ' ; ')})", end=" ", flush=True)

    # Reset to the original voice and stop engine
    engine.setProperty("voice", original_voice)
    engine.stop()


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_voice_reset_on_restart(driver_name):
    engine = pyttsx3.init(driver_name)
    original_voice = engine.getProperty("voice")

    # Change voice
    if voices := engine.getProperty("voices"):
        engine.setProperty("voice", voices[1].id if len(voices) > 1 else voices[0].id)
        assert engine.getProperty("voice") != original_voice, "Voice did not change."

    # Stop and restart the engine
    engine.stop()
    engine = pyttsx3.init(driver_name)  # Re-initialize with the same driver
    assert (
        engine.getProperty("voice") == original_voice
    ), "Voice did not reset to default after restart."

    # Reset to original voice if needed and stop the engine
    engine.setProperty("voice", original_voice)
    engine.runAndWait()
    engine.stop()


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_apple_nsss_voices(driver_name):
    if driver_name != "nsss":
        pytest.skip(f"Skipping nsss-specific test for {driver_name}.")

    import platform

    engine = pyttsx3.init(driver_name)
    macos_version, _, macos_hardware = platform.mac_ver()
    print(f"{sys.platform = }, {macos_version = } on {macos_hardware = }")
    print(list(pyttsx3._activeEngines))
    print(engine)
    assert str(engine) == "nsss", "Expected engine name to be nsss on macOS and iOS"
    voice = engine.getProperty("voice")
    # On macOS v14.x, the default nsss voice is com.apple.voice.compact.en-US.Samantha.
    # ON macOS v15.x, the default nsss voice is ""
    assert (
        voice in {"", "com.apple.voice.compact.en-US.Samantha"}
    ), "Expected default voice to be com.apple.voice.compact.en-US.Samantha on macOS and iOS"
    voices = engine.getProperty("voices")
    # On macOS v13.x or v14.x, nsss has 143 voices.
    # On macOS v15.x, nsss has 176 voices
    print(f"On macOS v{macos_version}, {engine} has {len(voices) = } voices.")
    assert len(voices) in {176, 143}, "Expected 176 or 143 voices on macOS and iOS"
    # print("\n".join(voice.id for voice in voices))
    en_us_voices = [
        voice for voice in voices if voice.id.startswith("com.apple.eloquence.en-US.")
    ]
    assert (
        len(en_us_voices) == 8
    ), "Expected 8 com.apple.eloquence.en-US voices on macOS and iOS"
    names = []
    for _voice in en_us_voices:
        engine.setProperty("voice", _voice.id)
        name = _voice.id.split(".")[-1]
        names.append(name)
        engine.say(f"{name} says hello")
    name_str = ", ".join(names)
    assert name_str == "Eddy, Flo, Grandma, Grandpa, Reed, Rocko, Sandy, Shelley"
    print(f"({name_str})", end=" ", flush=True)
    engine.runAndWait()
    engine.setProperty("voice", voice)  # Reset voice to original value
    engine.stop()
