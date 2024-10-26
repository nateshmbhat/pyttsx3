import objc
from AppKit import NSSpeechSynthesizer
from Foundation import *
from PyObjCTools import AppHelper
from ..voice import Voice


# noinspection PyPep8Naming
def buildDriver(proxy):
    driver = AVSpeechDriver.alloc().init()
    driver.setProxy(proxy)
    return driver


class AVSpeechDriver(NSObject):
    def init(self):
        self = objc.super(AVSpeechDriver, self).init()
        if self is None:
            return None
        self._proxy = None
        self._tts = NSSpeechSynthesizer.alloc().initWithVoice_(None)
        self._tts.setDelegate_(self)
        self._current_voice = None  # Store current voice as string
        return self

    @objc.python_method
    def setProxy(self, proxy):
        """Sets the proxy after initialization."""
        self._proxy = proxy

    def destroy(self):
        self._tts.setDelegate_(None)
        self._tts = None

    def onPumpFirst_(self, timer):
        self._proxy.setBusy(False)

    def startLoop(self):
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, "onPumpFirst:", None, False
        )
        runLoop = NSRunLoop.currentRunLoop()
        while runLoop.runMode_beforeDate_(
            NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.01)
        ):
            pass

    @staticmethod
    def endLoop():
        AppHelper.stopEventLoop()

    def iterate(self):
        self._proxy.setBusy(False)

    @objc.python_method
    def say(self, text):
        self._proxy.setBusy(True)
        self._proxy.notify("started-utterance")
        self._tts.startSpeakingString_(text)

    def stop(self):
        self._tts.stopSpeaking()

    @objc.python_method
    def save_to_file(self, text, filename):
        """Save the synthesized speech to the specified filename."""
        self._proxy.setBusy(True)
        url = Foundation.NSURL.fileURLWithPath_(filename)
        self._tts.startSpeakingString_toURL_(text, url)

    def speechSynthesizer_didFinishSpeaking_(self, tts, success):
        """Notify when speaking or file save completes."""
        self._proxy.notify("finished-utterance", completed=success)
        self._proxy.setBusy(False)

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text):
        """Notify when starting each word."""
        current_word = text[rng.location : rng.location + rng.length]
        self._proxy.notify(
            "started-word", name=current_word, location=rng.location, length=rng.length
        )

    # Property management
    @objc.python_method
    def getProperty(self, name):
        """Get the value of a TTS property."""
        if name == "voices":
            return [
                Voice(
                    id=v,
                    name=NSSpeechSynthesizer.attributesForVoice_(v).get("VoiceName"),
                    languages=[
                        NSSpeechSynthesizer.attributesForVoice_(v).get(
                            "VoiceLocaleIdentifier"
                        )
                    ],
                    gender=NSSpeechSynthesizer.attributesForVoice_(v).get(
                        "VoiceGender"
                    ),
                    age=NSSpeechSynthesizer.attributesForVoice_(v).get("VoiceAge"),
                )
                for v in NSSpeechSynthesizer.availableVoices()
            ]
        elif name == "voice":
            return self._tts.voice() or self._current_voice
        elif name == "rate":
            return self._tts.rate()
        elif name == "volume":
            return self._tts.volume()
        else:
            raise KeyError(f"Unknown property: {name}")

    @objc.python_method
    def setProperty(self, name, value):
        """Set the value of a TTS property."""
        if name == "voice":
            # Store current volume and rate to reapply after voice change
            current_volume = self._tts.volume()
            current_rate = self._tts.rate()
            self._tts.setVoice_(value)
            self._tts.setVolume_(current_volume)
            self._tts.setRate_(current_rate)
            self._current_voice = value
        elif name == "rate":
            self._tts.setRate_(value)
        elif name == "volume":
            self._tts.setVolume_(value)
        else:
            raise KeyError(f"Unknown property: {name}")
