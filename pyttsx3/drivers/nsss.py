# noinspection PyUnresolvedReferences
import objc
from AppKit import NSSpeechSynthesizer
from Foundation import *
from PyObjCTools import AppHelper
# noinspection PyProtectedMember
from PyObjCTools.AppHelper import PyObjCAppHelperRunLoopStopper

from ..voice import Voice


# noinspection PyUnresolvedReferences
class RunLoopStopper(PyObjCAppHelperRunLoopStopper):
    """
    Overrides PyObjCAppHelperRunLoopStopper to terminate after endLoop.
    """

    def __init__(self):
        self.shouldStop = False

    def init(self):
        return objc.super(RunLoopStopper, self).init()

    def stop(self):
        self.shouldStop = True


# noinspection PyPep8Naming
def buildDriver(proxy):
    return NSSpeechDriver.alloc().initWithProxy(proxy)


# noinspection PyUnresolvedReferences,PyPep8Naming,PyUnusedLocal
class NSSpeechDriver(NSObject):

    def __init__(self):
        self._proxy = None
        self._tts = None
        self._completed = False

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

    def destroy(self):
        self._tts.setDelegate_(None)
        del self._tts

    def onPumpFirst_(self, timer):
        self._proxy.setBusy(False)

    def startLoop(self):
        # https://github.com/ronaldoussoren/pyobjc/blob/mater/pyobjc-framework-Cocoa/Lib/PyObjCTools/AppHelper.py#L243C25-L243C25  # noqa
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, 'onPumpFirst:', None, False
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
    def endLoop():
        AppHelper.stopEventLoop()

    def iterate(self):
        self._proxy.setBusy(False)
        yield

    @objc.python_method
    def say(self, text):
        self._proxy.setBusy(True)
        self._completed = True
        self._proxy.notify('started-utterance')
        self._tts.startSpeakingString_(text)

    def stop(self):
        if self._proxy.isBusy():
            self._completed = False
        self._tts.stopSpeaking()

    @objc.python_method
    def _toVoice(self, attr):
        return Voice(attr.get('VoiceIdentifier'), attr.get('VoiceName'),
                     [attr.get('VoiceLocaleIdentifier', attr.get('VoiceLanguage'))], attr.get('VoiceGender'),
                     attr.get('VoiceAge'))

    @objc.python_method
    def getProperty(self, name):
        if name == 'voices':
            return [self._toVoice(NSSpeechSynthesizer.attributesForVoice_(v))
                    for v in list(NSSpeechSynthesizer.availableVoices())]
        elif name == 'voice':
            return self._tts.voice()
        elif name == 'rate':
            return self._tts.rate()
        elif name == 'volume':
            return self._tts.volume()
        elif name == "pitch":
            print("Pitch adjustment not supported when using NSSS")
        else:
            raise KeyError('unknown property %s' % name)

    @objc.python_method
    def setProperty(self, name, value):
        if name == 'voice':
            # vol/rate gets reset, so store and restore it
            vol = self._tts.volume()
            rate = self._tts.rate()
            self._tts.setVoice_(value)
            self._tts.setRate_(rate)
            self._tts.setVolume_(vol)
        elif name == 'rate':
            self._tts.setRate_(value)
        elif name == 'volume':
            self._tts.setVolume_(value)
        elif name == 'pitch':
            print("Pitch adjustment not supported when using NSSS")
        else:
            raise KeyError('unknown property %s' % name)

    @objc.python_method
    def save_to_file(self, text, filename):
        self._proxy.setBusy(True)
        self._completed = True
        url = Foundation.NSURL.fileURLWithPath_(filename)
        self._tts.startSpeakingString_toURL_(text, url)

    def speechSynthesizer_didFinishSpeaking_(self, tts, success):
        if not self._completed:
            success = False
        else:
            success = True
        self._proxy.notify('finished-utterance', completed=success)
        self._proxy.setBusy(False)

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text):
        self._proxy.notify('started-word', location=rng.location,
                           length=rng.length)
