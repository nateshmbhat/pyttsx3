import objc
from AVFoundation import (
    AVSpeechSynthesizer,
    AVSpeechUtterance,
    AVSpeechSynthesisVoice,
    AVAudioSession,
    AVSpeechUtteranceDefaultSpeechRate,
    AVSpeechBoundaryImmediate,
)
from Foundation import NSObject
from CoreFoundation import CFRunLoopRunInMode, kCFRunLoopDefaultMode
from ..voice import Voice


def buildDriver(proxy):
    driver = AVSpeechDriver.alloc().init()
    driver.setProxy(proxy)
    return driver


class AVSpeechDriver(NSObject):
    def init(self):
        self = objc.super(AVSpeechDriver, self).init()
        if self is None:
            raise RuntimeError("Unable to instantiate an AVSpeechDriver")

        session = AVAudioSession.sharedInstance()
        session.setCategory_error_("playback", None)
        session.setActive_error_(True, None)

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

    def destroy(self):
        self._tts.setDelegate_(None)
        self._tts = None

    def startLoop(self):
        self._should_stop_loop = False
        while not self._should_stop_loop and (self._queue or self._tts.isSpeaking()):
            self.processQueue_(None)
            CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.01, False)

    def endLoop(self):
        self._should_stop_loop = True

    @objc.typedSelector(b"v@:@")
    def processQueue_(self, _):
        if not self._queue:
            self.endLoop()
            return

        if not self._tts.isSpeaking():
            command, args = self._queue.pop(0)
            command(*args)  # Start speaking the next utterance
            print(
                f"Processing utterance: {args[0].speechString()}"
            )  # Debugging: Show each utterance
            self._proxy.setBusy(True)

    @objc.python_method
    def say(self, text):
        utterance = AVSpeechUtterance.speechUtteranceWithString_(text)
        if self._current_voice:
            utterance.setVoice_(self._current_voice)
        utterance.setRate_(self._rate)
        utterance.setVolume_(self._volume)
        self._queue.append((self._tts.speakUtterance_, (utterance,)))
        print(f"Queued utterance: {text}")  # Debugging: Track each queued item

    def stop(self):
        self._tts.stopSpeakingAtBoundary_(AVSpeechBoundaryImmediate)
        self.endLoop()

    # AVSpeechSynthesizer delegate methods
    def speechSynthesizer_didFinishSpeechUtterance_(self, tts, utterance):
        print(
            f"Finished utterance: {utterance.speechString()}"
        )  # Debugging: Track each completed utterance
        self._proxy.notify("finished-utterance", completed=True)
        self._proxy.setBusy(False)
        self.processQueue_(None)  # Continue processing next in queue

    def speechSynthesizer_willSpeakRangeOfSpeechString_(self, tts, info):
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
    def iterate(self):
        while self._queue or self._tts.isSpeaking():
            self.processQueue_(None)
            CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.01, False)
            yield

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
            self._rate = value * AVSpeechUtteranceDefaultSpeechRate
        elif name == "volume":
            self._volume = value
        else:
            raise KeyError(f"Unknown property: {name}")
