import objc
from AppKit import NSSpeechSynthesizer
from Foundation import NSObject, NSTimer, NSRunLoop, NSDefaultRunLoopMode, NSURL, NSDate
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
            return
            # or perhaps better...
            raise RuntimeError("Unable to instantiate an AVSpeechDriver")
        self._proxy = None
        self._tts = NSSpeechSynthesizer.alloc().initWithVoice_(None)
        self._tts.setDelegate_(self)
        self._current_voice = None
        self._queue = []
        self._should_stop_loop = False  # Flag to control loop
        return self

    @objc.python_method
    def setProxy(self, proxy):
        self._proxy = proxy

    @objc.python_method
    def initialize_busy_state(self):
        if self._proxy:
            self._proxy.setBusy(False)

    def destroy(self):
        self._tts.setDelegate_(None)
        self._tts = None

    def onPumpFirst_(self, timer):
        self._proxy.setBusy(False)

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
            command(*args)
            self._proxy.setBusy(True)
        else:
            self.endLoop()

    def endLoop(self):
        self._should_stop_loop = True
        AppHelper.stopEventLoop()

    @objc.python_method
    def say(self, text):
        self._queue.append((self._tts.startSpeakingString_, (text,)))
        self.startLoop()

    def stop(self):
        self._tts.stopSpeaking()
        self.endLoop()

    @objc.python_method
    def save_to_file(self, text, filename):
        url = NSURL.fileURLWithPath_(filename)
        self._queue.append((self._tts.startSpeakingString_toURL_, (text, url)))
        self.startLoop()

    def speechSynthesizer_didFinishSpeaking_(self, tts, success):
        self._proxy.notify("finished-utterance", completed=success)
        self._proxy.setBusy(False)
        # Check the queue after finishing each command
        if not self._queue:
            self.endLoop()

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text):
        current_word = text[rng.location : rng.location + rng.length]
        self._proxy.notify(
            "started-word", name=current_word, location=rng.location, length=rng.length
        )

    # Property management
    @objc.python_method
    def getProperty(self, name):
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
        if name == "voice":
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
