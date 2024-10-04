# noinspection PyUnresolvedReferences
import objc
import AVFoundation
from io import BytesIO
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
        self._current_text = ''
        self._audio_engine = AVAudioEngine.alloc().init()
        self._audio_format = AVAudioFormat.alloc().initStandardFormatWithSampleRate_channels_(44100, 1)
        self._buffer = BytesIO()


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
        self._current_text = text
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
        if self._current_text:
            current_word = self._current_text[rng.location:rng.location + rng.length]
        else:
            current_word = "Unknown"

        self._proxy.notify('started-word', name=current_word, location=rng.location,
                           length=rng.length)

    def to_bytestream(self, text, byte_stream):
        """
        Capture the spoken text as a byte stream using NSSpeechSynthesizer and AVAudioEngine.
    
        :param text: The text to speak
        :param byte_stream: The BytesIO object to store the byte stream
        """
        self._tts.setDelegate_(self)
    
        # Set up AVAudioEngine
        main_mixer = self._audio_engine.mainMixerNode()
        bus = 0
    
        # Define the buffer format
        format = self._audio_engine.outputNode().inputFormatForBus_(bus)
    
        def capture_handler(buffer, when):
            """Capture audio data as bytes in real-time."""
            # Get the audio buffer and extract its data
            audio_data = buffer.audioBufferList().mBuffers[0].mData
            audio_data_bytes = objc.objc_object_as_bytes(audio_data, buffer.frameLength)
            byte_stream.write(audio_data_bytes)
    
        # Tap the main mixer node to capture audio
        main_mixer.installTapOnBus_bufferSize_format_block_(bus, 1024, format, capture_handler)
    
        # Start the audio engine
        self._audio_engine.prepare()
        self._audio_engine.startAndReturnError_(None)
    
        # Start speaking the text
        self._tts.startSpeakingString_(text)
    
        # Wait for speech to finish
        while self._tts.isSpeaking():
            pass
    
        # Stop the audio engine
        self._audio_engine.stop()
        main_mixer.removeTapOnBus_(bus)