import os
import wave
import platform
import ctypes
import time
import subprocess
from tempfile import NamedTemporaryFile

if platform.system() == "Windows":
    import winsound

from . import _espeak
from ..voice import Voice


# noinspection PyPep8Naming
def buildDriver(proxy):
    return EspeakDriver(proxy)


# noinspection PyPep8Naming
class EspeakDriver(object):
    _moduleInitialized = False
    _defaultVoice = ""

    def __init__(self, proxy):
        if not EspeakDriver._moduleInitialized:
            # espeak cannot initialize more than once per process and has
            # issues when terminating from python (assert error on close)
            # so just keep it alive and init once
            rate = _espeak.Initialize(_espeak.AUDIO_OUTPUT_RETRIEVAL, 1000)
            if rate == -1:
                raise RuntimeError("could not initialize espeak")
            EspeakDriver._defaultVoice = "default"
            EspeakDriver._moduleInitialized = True
        self._proxy = proxy
        print("espeak init setting looping to false..")
        self._proxy._looping = False
        self._stopping = False
        self._speaking = False
        self._text_to_say = None
        self._data_buffer = b""
        self._numerise_buffer = []
        self._save_file = None

        _espeak.SetSynthCallback(self._onSynth)
        self.setProperty("voice", EspeakDriver._defaultVoice)
        self.setProperty("rate", 200)
        self.setProperty("volume", 1.0)

    def numerise(self, data):
        self._numerise_buffer.append(data)
        return ctypes.c_void_p(len(self._numerise_buffer))

    def decode_numeric(self, data):
        return self._numerise_buffer[int(data) - 1]

    @staticmethod
    def destroy():
        _espeak.SetSynthCallback(None)

    def stop(self):
        print("EspeakDriver.stop called, setting _stopping to True")
        if _espeak.IsPlaying():
            self._stopping = True
            _espeak.Cancel()

    @staticmethod
    def getProperty(name: str):
        if name == "voices":
            voices = []
            for v in _espeak.ListVoices(None):
                kwargs = {"id": v.name.decode("utf-8"), "name": v.name.decode("utf-8")}
                if v.languages:
                    try:
                        language_code_bytes = v.languages[1:]
                        language_code = language_code_bytes.decode(
                            "utf-8", errors="ignore"
                        )
                        kwargs["languages"] = [language_code]
                    except UnicodeDecodeError as e:
                        kwargs["languages"] = ["Unknown"]
                    genders = [None, "male", "female"]
                kwargs["gender"] = genders[v.gender]
                kwargs["age"] = v.age or None
                voices.append(Voice(**kwargs))
            return voices
        elif name == "voice":
            voice = _espeak.GetCurrentVoice()
            return voice.contents.name.decode("utf-8")
        elif name == "rate":
            return _espeak.GetParameter(_espeak.RATE)
        elif name == "volume":
            return _espeak.GetParameter(_espeak.VOLUME) / 100.0
        elif name == "pitch":
            return _espeak.GetParameter(_espeak.PITCH)
        else:
            raise KeyError("unknown property %s" % name)

    @staticmethod
    def setProperty(name: str, value):
        if name == "voice":
            if value is None:
                return
            try:
                utf8Value = str(value).encode("utf-8")
                _espeak.SetVoiceByName(utf8Value)
            except ctypes.ArgumentError as e:
                raise ValueError(str(e))
        elif name == "rate":
            try:
                _espeak.SetParameter(_espeak.RATE, value, 0)
            except ctypes.ArgumentError as e:
                raise ValueError(str(e))
        elif name == "volume":
            try:
                _espeak.SetParameter(_espeak.VOLUME, int(round(value * 100, 2)), 0)
            except TypeError as e:
                raise ValueError(str(e))
        elif name == "pitch":
            try:
                _espeak.SetParameter(_espeak.PITCH, int(value), 0)
            except TypeError as e:
                raise ValueError(str(e))
        else:
            raise KeyError("unknown property %s" % name)

    def save_to_file(self, text, filename):
        """
        Save the synthesized speech to the specified filename.
        """
        self._save_file = filename
        self._text_to_say = text

    def _start_synthesis(self, text):
        self._proxy.setBusy(True)
        self._proxy.notify("started-utterance")
        self._speaking = True
        self._data_buffer = b""  # Ensure buffer is cleared before starting
        try:
            _espeak.Synth(
                str(text).encode("utf-8"), flags=_espeak.ENDPAUSE | _espeak.CHARS_UTF8
            )
        except Exception as e:
            self._proxy.setBusy(False)
            self._proxy.notify("error", exception=e)
            raise

    def _onSynth(self, wav, numsamples, events):
        if not self._speaking:
            return 0

        # Process each event in the current callback
        i = 0
        while True:
            event = events[i]
            if event.type == _espeak.EVENT_LIST_TERMINATED:
                break
            elif event.type == _espeak.EVENT_WORD:
                if self._text_to_say:
                    start_index = event.text_position - 1
                    end_index = start_index + event.length
                    word = self._text_to_say[start_index:end_index]
                else:
                    word = "Unknown"
                self._proxy.notify(
                    "started-word",
                    name=word,
                    location=event.text_position,
                    length=event.length,
                )
            elif event.type == _espeak.EVENT_MSG_TERMINATED:
                print("EVENT_MSG_TERMINATED detected, ending loop.")
                # Ensure the loop stops when synthesis completes
                self._proxy._looping = False
                if not self._is_external_loop:
                    self.endLoop()  # End loop only if not in an external loop
                break
            elif event.type == _espeak.EVENT_END:
                print("EVENT_END detected.")
                # Optional: handle end of an utterance if applicable
                pass

            i += 1

        # Accumulate audio data if available
        if numsamples > 0:
            self._data_buffer += ctypes.string_at(
                wav, numsamples * ctypes.sizeof(ctypes.c_short)
            )

        return 0

    def endLoop(self):
        print("Ending loop...")
        print("EspeakDriver.endLoop called, setting looping to False")
        self._proxy._looping = False

    def startLoop(self, external=False):
        print(f"EspeakDriver: Entering startLoop (external={external})")
        self._proxy._looping = True
        self._is_external_loop = external  # Track if it's an external loop
        timeout = time.time() + 10
        while self._proxy._looping:
            if time.time() > timeout:
                print("Exiting startLoop due to timeout.")
                self._proxy._looping = False
                break
            print("EspeakDriver loop iteration")
            if self._text_to_say:
                self._start_synthesis(self._text_to_say)
            try:
                next(self.iterate())
            except StopIteration:
                print("StopIteration in startLoop")
                break
            time.sleep(0.01)

        print("EspeakDriver: Exiting startLoop")

    def iterate(self):
        print("running espeak iterate once")
        if not self._proxy._looping:
            print("Not looping, returning from iterate...")
            return
        if self._stopping:
            _espeak.Cancel()
            print("Exiting iterate due to stop.")
            self._stopping = False
            self._proxy.notify("finished-utterance", completed=False)
            self._proxy.setBusy(False)
            self._proxy._looping = False  # Mark the loop as done
            return

        # Only call endLoop in an internal loop, leave external control to external loop handler
        if not self._is_external_loop:
            self.endLoop()
        yield  # Yield back to `startLoop`

    def say(self, text):
        self._text_to_say = text
