from __future__ import annotations

import sys

import pytest

import pyttsx3

quick_brown_fox = "The quick brown fox jumped over the lazy dog."


@pytest.mark.skipif(
    sys.platform == "win32", reason="TODO: Install eSpeak-NG on Windows"
)
@pytest.mark.parametrize("driver_name", pyttsx3.engine.engines_by_sys_platform())
def test_engine_name(driver_name):
    engine = pyttsx3.init(driver_name)
    assert engine.driver_name == driver_name
    assert str(engine) == driver_name
    assert repr(engine) == f"pyttsx3.engine.Engine('{driver_name}', debug=False)"
    engine.stop()


@pytest.mark.skipif(
    sys.platform == "win32", reason="TODO: Install eSpeak-NG on Windows"
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
