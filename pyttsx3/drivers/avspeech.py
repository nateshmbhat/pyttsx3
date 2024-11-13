import objc
from AVFoundation import (
    AVSpeechSynthesizer,
    AVSpeechUtterance,
    AVSpeechSynthesisVoice,
    AVAudioSession,
    AVSpeechUtteranceDefaultSpeechRate,
)
from Foundation import NSObject, NSTimer
from PyObjCTools import AppHelper
from ..voice import Voice


# noinspection PyPep8Naming
def buildDriver(proxy):
    driver = AVSpeechDriver.alloc().init()
    driver.setProxy(proxy)
    driver.initialize_busy_state()
    return driver


class AVSpeechDriver(NSObject):
    def init(self):
        self = objc.super(AVSpeechDriver, self).init()
        if self is None:
            raise RuntimeError("Unable to instantiate an AVSpeechDriver")

        # Set up the audio session
        session = AVAudioSession.sharedInstance()
        session.setCategory_error_("playback", None)
        session.setActive_error_(True, None)

        # Initialize TTS and driver properties
        self._proxy = None
        self._tts = AVSpeechSynthesizer.alloc().init()
        self._tts.setDelegate_(self)
        self._current_voice = AVSpeechSynthesisVoice.voiceWithIdentifier_(
            "com.apple.voice.compact.en-US.Samantha"
        )
        self._rate = AVSpeechUtteranceDefaultSpeechRate
        self._volume = 1.0
        self._queue = []
        self._should_stop_loop = False
        return self

    @objc.python_method
    def setProxy(self, proxy):
        self._proxy = proxy

    @objc.python_method
    def initialize_busy_state(self):
        if self._proxy and hasattr(self._proxy, "_queue"):
            self._proxy.setBusy(False)
        else:
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                0.1, self, "initialize_busy_state", None, False
            )

    def destroy(self):
        self._tts.setDelegate_(None)
        self._tts = None

    def startLoop(self):
        self._should_stop_loop = False
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, "processQueue:", None, True
        )
        AppHelper.runConsoleEventLoop()

    @objc.typedSelector(b"v@:@")
    def processQueue_(self, _):
        if self._should_stop_loop:
            AppHelper.stopEventLoop()
            return

        if self._tts.isSpeaking():
            return  # Wait until speaking is finished

        if self._queue:
            command, args = self._queue.pop(0)
            print(f"Processing command: {command} with args: {args}")
            command(*args)
            self._proxy.setBusy(True)
        else:
            self.endLoop()

    def endLoop(self):
        self._should_stop_loop = True
        AppHelper.stopEventLoop()

    @objc.python_method
    def say(self, text):
        utterance = AVSpeechUtterance.speechUtteranceWithString_(text)
        if self._current_voice:
            utterance.setVoice_(self._current_voice)
        utterance.setRate_(self._rate)
        utterance.setVolume_(self._volume)
        self._queue.append((self._tts.speakUtterance_, (utterance,)))
        self.startLoop()

    def stop(self):
        self._tts.stopSpeaking()
        self.endLoop()

    @objc.python_method
    def save_to_file(self, text, filename):
        # File saving is not directly supported with AVSpeechSynthesizer, so this will require custom handling.
        print("save_to_file is not natively supported with AVSpeechSynthesizer.")

    # AVSpeechSynthesizer delegate methods
    def speechSynthesizer_didFinishSpeechUtterance_(self, tts, utterance):
        self._proxy.notify("finished-utterance", completed=True)
        self._proxy.setBusy(False)
        if not self._queue:
            self.endLoop()

    def speechSynthesizer_willSpeakRangeOfSpeechString_(self, tts, info):
        characterRange = info["AVSpeechSynthesisIPAPhonemeBounds"]
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

    # Property management
    @objc.python_method
    def getProperty(self, name):
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
        elif name == "voice":
            return self._current_voice.identifier() if self._current_voice else None
        elif name == "rate":
            return self._rate
        elif name == "volume":
            return self._volume
        else:
            raise KeyError(f"Unknown property: {name}")

    @objc.python_method
    def setProperty(self, name, value):
        if name == "voice":
            self._current_voice = AVSpeechSynthesisVoice.voiceWithIdentifier_(value)
        elif name == "rate":
            self._rate = value
        elif name == "volume":
            self._volume = value
        else:
            raise KeyError(f"Unknown property: {name}")
