
from Foundation import *
from AppKit import NSSpeechSynthesizer
from PyObjCTools import AppHelper
from PyObjCTools.AppHelper import PyObjCAppHelperRunLoopStopper
from ..voice import Voice

class RunLoopStopper(PyObjCAppHelperRunLoopStopper):

    def init(self):
        self = super(RunLoopStopper, self).init()
        self.shouldStop = False
        return self

    def stop(self):
        self.shouldStop = True
        # this should go away when/if runEventLoop uses
        # runLoop iteration
        # if NSApp() is not None:
        #     NSApp().terminate_(self)

def buildDriver(proxy):
    return NSSpeechDriver.alloc().initWithProxy(proxy)


class NSSpeechDriver(NSObject):
    @objc.python_method
    def initWithProxy(self, proxy):
        self = super(NSSpeechDriver, self).init()
        if self:
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
        NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.0, self, 'onPumpFirst:', None, False)
        runLoop = NSRunLoop.currentRunLoop()
        stopper = RunLoopStopper.alloc().init()
        PyObjCAppHelperRunLoopStopper.addRunLoopStopper_toRunLoop_(stopper, runLoop)
        try:

            while stopper.shouldRun():
                nextfire = runLoop.limitDateForMode_(NSDefaultRunLoopMode)
                if not stopper.shouldRun():
                    break
                if not runLoop.runMode_beforeDate_(NSDefaultRunLoopMode, nextfire):
                    stopper.stop()

        finally:
            PyObjCAppHelperRunLoopStopper.removeRunLoopStopperFromRunLoop_(runLoop)

    def endLoop(self):
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
        try:
            lang = attr['VoiceLocaleIdentifier']
        except KeyError:
            lang = attr['VoiceLanguage']
        return Voice(attr['VoiceIdentifier'], attr['VoiceName'],
                     [lang], attr['VoiceGender'])

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
        url = Foundation.NSURL.fileURLWithPath_(filename)
        import time

        self._tts.startSpeakingString_toURL_(text, url)
        time.sleep(max(1, len(text) * 0.01))

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
