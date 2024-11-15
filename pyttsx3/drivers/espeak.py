from ..voice import Voice
from . import _espeak

import ctypes
import os
import platform
import subprocess
import time
import wave
from tempfile import NamedTemporaryFile
import logging

logger = logging.getLogger(__name__)


if platform.system() == "Windows":
    import winsound


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
            current_voice = _espeak.GetCurrentVoice()
            if current_voice and current_voice.contents.name:
                EspeakDriver._defaultVoice = current_voice.contents.name.decode("utf-8")
            else:
                # Fallback to a known default if no voice is set
                EspeakDriver._defaultVoice = "gmw/en"  # Adjust this as needed
            EspeakDriver._moduleInitialized = True
        self._proxy = proxy
        self._looping = False
        self._stopping = False
        self._speaking = False
        self._text_to_say = None
        self._queue = []  #
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
        if not self._stopping:
            logger.debug("[DEBUG] EspeakDriver.stop called")
            if self._looping:
                self._stopping = True
                self._looping = False
                if _espeak.IsPlaying():
                    _espeak.Cancel()
                self._proxy.setBusy(False)

    @staticmethod
    def getProperty(name: str):
        if name == "voices":
            voices = []
            for v in _espeak.ListVoices(None):
                # Use identifier as the unique ID
                voice_id = v.identifier.decode(
                    "utf-8"
                ).lower()  # Identifier corresponds to the "File" in espeak --voices
                kwargs = {
                    "id": voice_id,  # Use "identifier" as the ID
                    "name": v.name.decode("utf-8"),  # Nice name
                }
                if v.languages:
                    try:
                        language_code_bytes = v.languages[1:]
                        language_code = language_code_bytes.decode(
                            "utf-8", errors="ignore"
                        )
                        kwargs["languages"] = [language_code]
                    except UnicodeDecodeError:
                        kwargs["languages"] = ["Unknown"]
                genders = [None, "Male", "Female"]
                kwargs["gender"] = genders[v.gender]
                kwargs["age"] = v.age or None
                voices.append(Voice(**kwargs))
            return voices
        if name == "voice":
            voice = _espeak.GetCurrentVoice()
            if voice and voice.contents.name:
                return voice.contents.identifier.decode("utf-8").lower()
            return None
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
                logging.debug(f"Attempting to set voice to: {value}")
                result = _espeak.SetVoiceByName(utf8Value)
                if result == 0:  # EE_OK is 0
                    logging.debug(f"Successfully set voice to: {value}")
                elif result == 1:  # EE_BUFFER_FULL
                    raise ValueError(
                        f"SetVoiceByName failed: EE_BUFFER_FULL while setting voice to {value}"
                    )
                elif result == 2:  # EE_INTERNAL_ERROR
                    raise ValueError(
                        f"SetVoiceByName failed: EE_INTERNAL_ERROR while setting voice to {value}"
                    )
                else:
                    raise ValueError(
                        f"SetVoiceByName failed with unknown return code {result} for voice: {value}"
                    )
            except ctypes.ArgumentError as e:
                raise ValueError(f"Invalid voice name: {value}, error: {e}")
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
        self._data_buffer = b""
        try:
            _espeak.Synth(
                text.encode("utf-8"), flags=_espeak.ENDPAUSE | _espeak.CHARS_UTF8
            )
        except Exception as e:
            self._proxy.setBusy(False)
            self._proxy.notify("error", exception=e)
            raise

    def _onSynth(self, wav, numsamples, events):
        if not self._speaking:
            return 0

        i = 0
        while True:
            event = events[i]

            if event.type == _espeak.EVENT_LIST_TERMINATED:
                break
            elif event.type == _espeak.EVENT_WORD:
                # Handle word events to notify on each word spoken
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
                # Handle utterance completion
                if self._save_file:
                    # Save audio to file if requested
                    try:
                        with wave.open(self._save_file, "wb") as f:
                            f.setnchannels(1)  # Mono
                            f.setsampwidth(2)  # 16-bit samples
                            f.setframerate(22050)  # 22,050 Hz sample rate
                            f.writeframes(self._data_buffer)
                        logger.debug(f"Audio saved to {self._save_file}")
                    except Exception as e:
                        raise RuntimeError(f"Error saving WAV file: {e}")
                else:
                    # Playback temporary file (if not saving to file)
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

                        if platform.system() == "Darwin":
                            subprocess.run(["afplay", temp_wav_name], check=True)
                        elif platform.system() == "Linux":
                            if "CI" in os.environ:
                                logger.debug(
                                    "Running in CI environment; using ffmpeg for silent processing."
                                )
                                # Use ffmpeg to process the audio file without playback
                                subprocess.run(
                                    f"ffmpeg -i {temp_wav_name} -f null -",
                                    shell=True,
                                    check=True,
                                )
                            else:
                                try:
                                    subprocess.run(
                                        f"aplay {temp_wav_name} -q",
                                        shell=True,
                                        check=True,
                                    )
                                except subprocess.CalledProcessError:
                                    logger.debug(
                                        "Falling back to ffplay for audio playback."
                                    )
                                    subprocess.run(
                                        f"ffplay -autoexit -nodisp {temp_wav_name}",
                                        shell=True,
                                    )
                        elif platform.system() == "Windows":
                            winsound.PlaySound(temp_wav_name, winsound.SND_FILENAME)

                        os.remove(temp_wav_name)
                    except Exception as e:
                        logger.debug(f"Playback error: {e}")

                logger.debug(
                    "[DEBUG] Utterance complete; resetting text_to_say and speaking flag."
                )
                self._text_to_say = None  # Clear text once utterance completes
                self._speaking = False
                self._proxy.notify("finished-utterance", completed=True)
                self._proxy.setBusy(False)
                if not self._is_external_loop:
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
        """End the loop only when there’s no more text to say."""
        if self._queue or self._text_to_say:
            logger.debug(
                "EndLoop called, but queue or text_to_say is not empty; continuing..."
            )
            return  # Keep looping if there’s still text
        else:
            logger.debug("EndLoop called; stopping loop.")
            self._looping = False
            self._proxy.setBusy(False)

    def startLoop(self, external=False):
        """Start the synthesis loop."""
        logging.debug("Starting loop")
        self._looping = True
        self._is_external_loop = external

        while self._looping:
            if not self._speaking and self._queue:
                self._text_to_say = self._queue.pop(0)
                logging.debug(f"Synthesizing text: {self._text_to_say}")
                self._start_synthesis(self._text_to_say)

            try:
                if not external:
                    next(self.iterate())
                time.sleep(0.01)
            except StopIteration:
                break
        self._proxy.setBusy(False)

    def iterate(self):
        """Process events within an external loop context."""
        if not self._looping:
            return

        if self._stopping:
            # Cancel the current utterance if stopping
            _espeak.Cancel()
            self._stopping = False
            self._proxy.notify("finished-utterance", completed=False)
            self._proxy.setBusy(False)
            self.endLoop()  # Set `_looping` to False, signaling exit

        # Yield only if in an external loop to hand control back
        if self._is_external_loop:
            yield

    def say(self, text):
        logging.debug(f"[DEBUG] EspeakDriver.say called with text: {text}")
        self._queue.append(text)  # Add text to the local queue
        if not self._looping:
            logging.debug("[DEBUG] Starting loop from say")
            self.startLoop()

    def runAndWait(self, timeout=0.01):
        """
        Runs an event loop until the queue is empty or the timeout is reached.
        """
        # First, check if the loop is already running
        if self._looping:
            logging.debug("[DEBUG] Loop already active; waiting for completion.")
            start_time = time.time()
            while self._looping and (time.time() - start_time < timeout):
                time.sleep(0.1)
            if self._looping:
                logging.debug("[WARNING] Forcing loop exit due to timeout.")
                self.endLoop()
                self._proxy.setBusy(False)

        # Push endLoop to the queue to complete the sequence
        self._proxy._push(self._proxy._engine.endLoop, tuple())

        # Start the loop if not already running
        if not self._looping:
            self.startLoop()

        # Track the start time for timeout handling
        start_time = time.time()

        # Main wait loop to ensure commands are fully processed
        while self._queue or self._text_to_say or self._speaking:
            if time.time() - start_time > timeout:
                logger.debug("[WARNING] runAndWait timeout reached.")
                break
            time.sleep(0.1)  # Allow time for the loop to process items in the queue

        logger.debug("[DEBUG] runAndWait completed.")
