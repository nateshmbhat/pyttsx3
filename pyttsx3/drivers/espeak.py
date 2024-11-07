import ctypes
import os
import platform
import subprocess
import time
import wave
from tempfile import NamedTemporaryFile

if platform.system() == "Windows":
    import winsound

from ..voice import Voice
from . import _espeak


# noinspection PyPep8Naming
def buildDriver(proxy):
    return EspeakDriver(proxy)


# noinspection PyPep8Naming
class EspeakDriver:
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
        self._looping = False
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
                    except UnicodeDecodeError:
                        kwargs["languages"] = ["Unknown"]
                    genders = [None, "male", "female"]
                kwargs["gender"] = genders[v.gender]
                kwargs["age"] = v.age or None
                voices.append(Voice(**kwargs))
            return voices
        if name == "voice":
            voice = _espeak.GetCurrentVoice()
            return voice.contents.name.decode("utf-8") if voice.contents.name else None
        if name == "rate":
            return _espeak.GetParameter(_espeak.RATE)
        if name == "volume":
            return _espeak.GetParameter(_espeak.VOLUME) / 100.0
        if name == "pitch":
            return _espeak.GetParameter(_espeak.PITCH)
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
            if event.type == _espeak.EVENT_WORD:
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
                # Final event indicating synthesis completion
                if self._save_file:
                    try:
                        with wave.open(self._save_file, "wb") as f:
                            f.setnchannels(1)  # Mono
                            f.setsampwidth(2)  # 16-bit samples
                            f.setframerate(22050)  # 22,050 Hz sample rate
                            f.writeframes(self._data_buffer)
                        print(f"Audio saved to {self._save_file}")
                    except Exception as e:
                        raise RuntimeError(f"Error saving WAV file: {e}")
                else:
                    try:
                        with NamedTemporaryFile(
                            suffix=".wav", delete=False
                        ) as temp_wav:
                            with wave.open(temp_wav, "wb") as f:
                                f.setnchannels(1)  # Mono
                                f.setsampwidth(2)  # 16-bit samples
                                f.setframerate(22050)  # 22,050 Hz sample rate
                                f.writeframes(self._data_buffer)

                            temp_wav_name = temp_wav.name
                            temp_wav.flush()

                        # Playback functionality (for say method)
                        if platform.system() == "Darwin":  # macOS
                            subprocess.run(["afplay", temp_wav_name], check=True)
                        elif platform.system() == "Linux":
                            os.system(f"aplay {temp_wav_name} -q")
                        elif platform.system() == "Windows":
                            winsound.PlaySound(temp_wav_name, winsound.SND_FILENAME)

                        # Remove the file after playback
                        os.remove(temp_wav_name)
                    except Exception as e:
                        print(f"Playback error: {e}")

                # Clear the buffer and mark as finished
                self._data_buffer = b""
                self._speaking = False
                self._proxy.notify("finished-utterance", completed=True)
                self._proxy.setBusy(False)
                self.endLoop()
                break

            i += 1

        # Accumulate audio data if available
        if numsamples > 0:
            self._data_buffer += ctypes.string_at(
                wav, numsamples * ctypes.sizeof(ctypes.c_short)
            )

        return 0

    def endLoop(self):
        self._looping = False

    def startLoop(self):
        first = True
        self._looping = True
        while self._looping:
            if not self._looping:
                break
            if first:
                self._proxy.setBusy(False)
                first = False
                if self._text_to_say:
                    self._start_synthesis(self._text_to_say)
            self.iterate()
            time.sleep(0.01)

    def iterate(self):
        if not self._looping:
            return
        if self._stopping:
            _espeak.Cancel()
            self._stopping = False
            self._proxy.notify("finished-utterance", completed=False)
            self._proxy.setBusy(False)
            self.endLoop()

    def say(self, text):
        self._text_to_say = text
