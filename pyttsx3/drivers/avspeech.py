"""
AVSpeech driver for pyttsx3.

This driver uses the AVSpeechSynthesizer class from AVFoundation on macOS.
It is based on the NSSpeechSynthesizer driver and provides similar functionality.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import objc
from AVFoundation import (
    AVAudioSession,
    AVSpeechBoundaryImmediate,
    AVSpeechSynthesisVoice,
    AVSpeechSynthesizer,
    AVSpeechUtterance,
    AVSpeechUtteranceDefaultSpeechRate,
)
from CoreFoundation import CFRunLoopRunInMode, kCFRunLoopDefaultMode
from Foundation import NSObject

from pyttsx3.voice import Voice

if TYPE_CHECKING:
    from collections.abc import Iterator


def buildDriver(proxy):
    """Build an AVSpeech driver instance."""
    driver = AVSpeechDriver.alloc().init()
    driver.setProxy(proxy)
    return driver


class AVSpeechDriver(NSObject):
    """AVSpeech driver for pyttsx3."""

    def init(self):
        """Initialize the AVSpeech driver."""
        instance = objc.super(AVSpeechDriver, self).init()  # Use a separate variable
        if instance is None:
            msg = "Unable to instantiate an AVSpeechDriver"
            raise RuntimeError(msg)

        # Setup audio session
        session = AVAudioSession.sharedInstance()
        session.setCategory_error_("playback", None)
        session.setActive_error_(True, None)

        # Initialize properties
        instance._proxy = None
        instance._tts = AVSpeechSynthesizer.alloc().init()
        instance._tts.setDelegate_(instance)
        instance._current_voice = AVSpeechSynthesisVoice.voiceWithIdentifier_(
            "com.apple.voice.compact.en-US.Samantha",
        )
        instance._rate = AVSpeechUtteranceDefaultSpeechRate
        instance._volume = 1.0
        instance._queue = []
        instance._should_stop_loop = False
        return instance

    @objc.python_method
    def setProxy(self, proxy) -> None:
        """Set the proxy for the AVSpeech driver."""
        self._proxy = proxy

    @objc.python_method
    def initialize_busy_state(self) -> None:
        """Initialize the busy state of the AVSpeech driver."""
        if self._proxy and hasattr(self._proxy, "_queue"):
            self._proxy.setBusy(False)

    def destroy(self) -> None:
        """Destroy the AVSpeech driver."""
        self._tts.setDelegate_(None)
        self._tts = None

    def startLoop(self) -> None:
        """Start the AVSpeech driver loop."""
        self._should_stop_loop = False
        while not self._should_stop_loop and (self._queue or self._tts.isSpeaking()):
            self.processQueue_(None)
            CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.01, False)

    def endLoop(self) -> None:
        """End the AVSpeech driver loop."""
        self._should_stop_loop = True

    @objc.typedSelector(b"v@:@")
    def processQueue_(self, _) -> None:
        """Process the queue of utterances."""
        if not self._queue:
            self.endLoop()
            return

        if not self._tts.isSpeaking():
            command, args = self._queue.pop(0)
            command(*args)  # Start speaking the next utterance
            logging.debug("Processing utterance: %s:", {args[0].speechString()})
            self._proxy.setBusy(True)

    @objc.python_method
    def say(self, text) -> None:
        """Speak the given text. Note - should queue it - not speak it immediately."""
        utterance = AVSpeechUtterance.speechUtteranceWithString_(text)
        if self._current_voice:
            utterance.setVoice_(self._current_voice)
        utterance.setRate_(self._rate)
        utterance.setVolume_(self._volume)
        self._queue.append((self._tts.speakUtterance_, (utterance,)))
        logging.debug("Queued utterance: %s", text)

    def stop(self) -> None:
        """Stop the current utterance."""
        self._tts.stopSpeakingAtBoundary_(AVSpeechBoundaryImmediate)
        self.endLoop()

    # AVSpeechSynthesizer delegate methods
    def speechSynthesizer_didFinishSpeechUtterance_(self, tts, utterance) -> None:
        """Notify the engine when an utterance is finished."""
        logging.debug("Finished utterance: %s", utterance.speechString())
        self._proxy.notify("finished-utterance", completed=True)
        self._proxy.setBusy(False)
        self.processQueue_(None)  # Continue processing next in queue

    def speechSynthesizer_willSpeakRangeOfSpeechString_(self, tts, info) -> None:
        """Notify the engine when a word is spoken."""
        characterRange = info["NSRange"]
        utterance = info["AVSpeechSynthesisSpeechString"]
        current_word = utterance[
            characterRange.location : characterRange.location + characterRange.length
        ]
        self._proxy.notify(
            "started-word",
            name=current_word,
            location=characterRange.location,
            length=characterRange.length,
        )

    @objc.python_method
    def iterate(self) -> Iterator[None]:
        """Iterate the AVSpeech driver loop."""
        while self._queue or self._tts.isSpeaking():
            self.processQueue_(None)
            CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.01, False)
            yield

    @objc.python_method
    def getProperty(self, name: str) -> str | float | list[Voice]:
        """Get the value of the given property."""
        if name == "voices":
            return [
                Voice(
                    id=voice.identifier(),
                    name=voice.name(),
                    languages=[voice.language()],
                    gender=None,
                    age=None,
                )
                for voice in AVSpeechSynthesisVoice.speechVoices()
            ]
        if name == "voice":
            return self._current_voice.identifier() if self._current_voice else None
        if name == "rate":
            return self._rate
        if name == "volume":
            return self._volume
        msg = f"Unknown property: {name}"
        raise KeyError(msg)

    @objc.python_method
    def setProperty(self, name: str, value: str | float | None) -> None:
        """Set the value of the given property."""
        if name == "voice":
            self._current_voice = AVSpeechSynthesisVoice.voiceWithIdentifier_(value)
        elif name == "rate":
            self._rate = value * AVSpeechUtteranceDefaultSpeechRate
        elif name == "volume":
            self._volume = value
        else:
            msg = f"Unknown property: {name}"
            raise KeyError(msg)
