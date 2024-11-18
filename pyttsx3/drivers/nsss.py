# noinspection PyUnresolvedReferences
import objc
from AppKit import NSSpeechSynthesizer
from Foundation import NSURL, NSDate, NSDefaultRunLoopMode, NSObject, NSRunLoop, NSTimer
from PyObjCTools import AppHelper

# noinspection PyProtectedMember
from PyObjCTools.AppHelper import PyObjCAppHelperRunLoopStopper

from pyttsx3.voice import Voice


# noinspection PyUnresolvedReferences
class RunLoopStopper(PyObjCAppHelperRunLoopStopper):
    """Overrides PyObjCAppHelperRunLoopStopper to terminate after endLoop."""

    def __init__(self) -> None:
        self.shouldStop = False

    def init(self):
        return objc.super(RunLoopStopper, self).init()

    def stop(self) -> None:
        self.shouldStop = True


# noinspection PyPep8Naming
def buildDriver(proxy):
    return NSSpeechDriver.alloc().initWithProxy(proxy)


# noinspection PyUnresolvedReferences,PyPep8Naming,PyUnusedLocal
class NSSpeechDriver(NSObject):
    def __init__(self) -> None:
        self._proxy = None
        self._tts = None
        self._completed = False
        self._current_text = ""

    @objc.python_method
    def initWithProxy(self, proxy):
        try:
            proxy_attr = objc.super(NSSpeechDriver, self).init()
        except AttributeError:
            proxy_attr = self
        if proxy_attr:
            self._proxy = proxy
            self._tts = NSSpeechSynthesizer.alloc().initWithVoice_(None)
            self._tts.setDelegate_(self)
            # default rate
            self._tts.setRate_(200)
            self._completed = True
        return self

    def destroy(self) -> None:
        self._tts.setDelegate_(None)
        del self._tts

    def onPumpFirst_(self, timer) -> None:
        self._proxy.setBusy(False)

    def startLoop(self) -> None:
        # https://github.com/ronaldoussoren/pyobjc/blob/master/pyobjc-framework-Cocoa/Lib/PyObjCTools/AppHelper.py#L243C25-L243C25  # noqa: E501
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, "onPumpFirst:", None, False
        )
        runLoop = NSRunLoop.currentRunLoop()
        stopper = RunLoopStopper.alloc().init()
        PyObjCAppHelperRunLoopStopper.addRunLoopStopper_toRunLoop_(stopper, runLoop)
        while stopper.shouldRun():
            nextfire = runLoop.limitDateForMode_(NSDefaultRunLoopMode)
            soon = NSDate.dateWithTimeIntervalSinceNow_(0)  # maxTimeout in runConsoleEventLoop
            if nextfire is not None:
                nextfire = soon.earlierDate_(nextfire)
            if not runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, nextfire):
                stopper.stop()
                break
        PyObjCAppHelperRunLoopStopper.removeRunLoopStopperFromRunLoop_(runLoop)

    @staticmethod
    def endLoop() -> None:
        AppHelper.stopEventLoop()

    def iterate(self):
        self._proxy.setBusy(False)
        yield

    @objc.python_method
    def say(self, text) -> None:
        self._proxy.setBusy(True)
        self._completed = True
        self._proxy.notify("started-utterance")
        self._current_text = text
        self._tts.startSpeakingString_(text)

    def stop(self) -> None:
        if self._proxy.isBusy():
            self._completed = False
        self._tts.stopSpeaking()

    @objc.python_method
    def _toVoice(self, attr):
        return Voice(
            attr.get("VoiceIdentifier"),
            attr.get("VoiceName"),
            [attr.get("VoiceLocaleIdentifier", attr.get("VoiceLanguage"))],
            attr.get("VoiceGender"),
            attr.get("VoiceAge"),
        )

    @objc.python_method
    def getProperty(self, name):
        if name == "voices":
            return [
                self._toVoice(NSSpeechSynthesizer.attributesForVoice_(v))
                for v in list(NSSpeechSynthesizer.availableVoices())
            ]
        if name == "voice":
            return self._tts.voice()
        if name == "rate":
            return self._tts.rate()
        if name == "volume":
            return self._tts.volume()
        if name == "pitch":
            print("Pitch adjustment not supported when using NSSS")
            return None
        msg = f"unknown property {name}"
        raise KeyError(msg)

    @objc.python_method
    def setProperty(self, name, value) -> None:
        if name == "voice":
            # vol/rate gets reset, so store and restore it
            vol = self._tts.volume()
            rate = self._tts.rate()
            self._tts.setVoice_(value)
            self._tts.setRate_(rate)
            self._tts.setVolume_(vol)
        elif name == "rate":
            self._tts.setRate_(value)
        elif name == "volume":
            self._tts.setVolume_(value)
        elif name == "pitch":
            print("Pitch adjustment not supported when using NSSS")
        else:
            msg = f"unknown property {name}"
            raise KeyError(msg)

    @objc.python_method
    def save_to_file(self, text, filename) -> None:
        """Apple writes .aiff, not .wav. https://github.com/nateshmbhat/pyttsx3/issues/361."""
        self._proxy.setBusy(True)
        self._completed = True
        self._current_text = text
        url = NSURL.fileURLWithPath_(filename)
        self._tts.startSpeakingString_toURL_(text, url)

    def speechSynthesizer_didFinishSpeaking_(self, tts, success) -> None:
        success = bool(self._completed)
        self._proxy.notify("finished-utterance", completed=success)
        self._proxy.setBusy(False)

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text) -> None:
        current_word = (
            self._current_text[rng.location : rng.location + rng.length]
            if self._current_text
            else "Unknown"
        )

        self._proxy.notify(
            "started-word", name=current_word, location=rng.location, length=rng.length
        )
