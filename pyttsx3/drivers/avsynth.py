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
            return None
        self._proxy = None
        self._tts = NSSpeechSynthesizer.alloc().initWithVoice_(None)
        self._tts.setDelegate_(self)
        self._queue = []
        self._should_stop_loop = False
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

    def startLoop(self):
        """Start the event loop for processing the queue."""
        print("[DEBUG] AVSpeechDriver: Starting event loop")
        self._should_stop_loop = False
        try:
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
                0.1, self, "processQueue:", None, True
            )
            print("[DEBUG] NSTimer scheduled successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to schedule NSTimer: {e}")
        self.processQueue_(None)  # Immediate initial process to check queue
        AppHelper.runConsoleEventLoop()

    @objc.signature(b"v@:@")
    def processQueue_(self, _):
        """Process the next item in the queue."""
        print("[DEBUG] AVSpeechDriver: Processing queue")

        if self._should_stop_loop:
            print("[DEBUG] AVSpeechDriver: Stopping event loop")
            AppHelper.stopEventLoop()
            return

        if not self._queue:
            print("[DEBUG] AVSpeechDriver: Queue empty, ending loop")
            self.endLoop()
            return

        command, args = self._queue.pop(0)
        print(
            f"[DEBUG] AVSpeechDriver: Executing command {command.__name__} with args {args}"
        )
        command(*args)
        self._proxy.setBusy(True)

    def endLoop(self):
        """Stop the event loop."""
        print("[DEBUG] AVSpeechDriver: Ending loop")
        self._should_stop_loop = True
        AppHelper.stopEventLoop()

    @objc.python_method
    def say(self, text):
        """Queue the say command and verify queue contents."""
        print(f"[DEBUG] AVSpeechDriver: Queueing 'say' command with text: {text}")
        self._queue.append((self._tts.startSpeakingString_, (text,)))
        print(f"[DEBUG] Queue after appending 'say': {self._queue}")
        self._should_stop_loop = False
        self.startLoop()

    @objc.python_method
    def save_to_file(self, text, filename):
        """Queue the save_to_file command and verify queue contents."""
        url = NSURL.fileURLWithPath_(filename)
        print(
            f"[DEBUG] AVSpeechDriver: Queueing 'save_to_file' command with text: {text} to file: {filename}"
        )
        self._queue.append((self._tts.startSpeakingString_toURL_, (text, url)))
        print(f"[DEBUG] Queue after appending 'save_to_file': {self._queue}")
        self._should_stop_loop = False
        self.startLoop()

    def speechSynthesizer_didFinishSpeaking_(self, tts, success):
        """Callback when speech finishes."""
        print(f"[DEBUG] AVSpeechDriver: Speech finished with success={success}")
        self._proxy.notify("finished-utterance", completed=success)
        self._proxy.setBusy(False)
        if not self._queue:
            self.endLoop()

    def speechSynthesizer_willSpeakWord_ofString_(self, tts, rng, text):
        """Callback when about to speak a word."""
        current_word = text[rng.location : rng.location + rng.length]
        self._proxy.notify(
            "started-word", name=current_word, location=rng.location, length=rng.length
        )

    def stop(self):
        print("[DEBUG] AVSpeechDriver: Stopping speech")
        self._tts.stopSpeaking()
        self.endLoop()

    def iterate(self):
        """
        Iterator for processing queued items in an external loop.
        This allows external control over the loop.
        """
        while not self._should_stop_loop:
            print("[DEBUG] AVSpeechDriver: Processing queue in iterate")
            self.processQueue_(None)
            yield

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
