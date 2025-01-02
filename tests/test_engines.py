from __future__ import annotations

import sys

import pytest

import pyttsx3

quick_brown_fox = "The quick brown fox jumped over the lazy dog."


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_engine_name(driver_name) -> None:
    engine = pyttsx3.init(driver_name)
    assert engine.driver_name == driver_name
    assert str(engine) == driver_name
    assert repr(engine) == f"pyttsx3.engine.Engine('{driver_name}', debug=False)"
    engine.stop()


@pytest.mark.skipif(
    sys.platform == "win32", reason="TODO: Make this test pass on eSpeak-NG on Windows"
)
@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_speaking_text(driver_name) -> None:
    engine = pyttsx3.init(driver_name)
    engine.say("Sally sells seashells by the seashore.")
    engine.say(quick_brown_fox)
    print(list(pyttsx3._activeEngines.values()), flush=True)
    engine.runAndWait()
    print(list(pyttsx3._activeEngines.values()), flush=True)
    engine.stop()


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_espeak_voices(driver_name) -> None:
    if driver_name != "espeak":
        pytest.skip(f"Skipping eSpeak-specific test for {driver_name}.")

    engine = pyttsx3.init(driver_name)
    print(list(pyttsx3._activeEngines))
    print(engine)
    assert str(engine) == "espeak", "Expected engine name to be espeak"

    # Verify initial voice
    default_voice = engine.getProperty("voice")
    print(f"Initial default voice ID: {default_voice}")
    assert (
        default_voice == "gmw/en"
    ), f"Expected default voice ID to be 'gmw/en', Got: {default_voice}"

    # Get and validate the number of voices
    voices = engine.getProperty("voices")
    print(f"{engine} has {len(voices) = } voices.")
    # Linux eSpeak-NG v1.51 has 131 voices,
    # macOS eSpeak-NG v1.52.0 has 141 voices,
    # Windows eSpeak-NG v1.52-dev has 221 voices.
    assert len(voices) in {131, 141, 221}, "Unexpected number of voices"

    # Define the expected English voice IDs (excluding Caribbean for now as not in some envs
    # Linux eSpeak-NG v1.50 has 7 English voices,
    # macOS eSpeak-NG v1.51 and Windows eSpeak-NG v1.52-dev have 8 English voices.
    english_voice_ids = (
        "gmw/en",  # Great Britain
        "gmw/en-GB-scotland",  # Scotland
        "gmw/en-GB-x-gbclan",  # Lancaster
        "gmw/en-GB-x-gbcwmd",  # West Midlands
        "gmw/en-GB-x-rp",  # Received Pronunciation
        "gmw/en-US",  # America
        "gmw/en-US-nyc",  # America, New York City
    )

    for voice_id in english_voice_ids:
        target_voice = next((v for v in voices if v.id == voice_id), None)
        if not target_voice:
            print(f"Voice with ID '{voice_id}' not found. Skipping.")
            continue

        print(f"Attempting to set voice to ID: {voice_id} (Name: {target_voice.name})")
        engine.setProperty("voice", target_voice.id)

        # Verify the change
        current_voice = engine.getProperty("voice")
        print(f"Current voice ID: {current_voice}")
        if current_voice != target_voice.id:
            print(
                "Voice change mismatch. "
                f"Expected: {target_voice.id}, Got: {current_voice}. Skipping."
            )
            continue

        engine.say(f"Hello, this is {target_voice.name}.")
        engine.runAndWait()


@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_apple_nsss_voices(driver_name) -> None:
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
    if voice:
        assert (
            voice == "com.apple.voice.compact.en-US.Samantha"
        ), "Expected default voice to be com.apple.voice.compact.en-US.Samantha on macOS and iOS"
    voices = engine.getProperty("voices")
    # On macOS v13.x or v14.x, nsss has 143 voices.
    # On macOS v15.x, nsss has 176 voices
    print(f"On macOS v{macos_version}, {engine} has {len(voices) = } voices.")
    assert len(voices) in {176, 143}, "Expected 176 or 143 voices on macOS and iOS"
    # print("\n".join(voice.id for voice in voices))
    en_us_voices = [voice for voice in voices if voice.id.startswith("com.apple.eloquence.en-US.")]
    assert len(en_us_voices) == 8, "Expected 8 com.apple.eloquence.en-US voices on macOS and iOS"
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
