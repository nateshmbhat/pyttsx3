import comtypes.client
import time
import pythoncom
import math
import os
import weakref

from ..voice import Voice

SAPI4_VOICE_CLASS_ID = "{EEE78591-FE22-11D0-8BEF-0060081841DE}"


def buildDriver(proxy):
    return SAPI4Driver(proxy)


class SAPI4DriverEventSink:
    def __init__(self):
        self._driver = None

    def setDriver(self, driver):
        self._driver = driver

    def StartStream(self, stream_number, stream_position):
        """Event triggered at the start of a stream."""
        if self._driver:
            self._driver._proxy.notify("started-utterance")

    def EndStream(self, stream_number, stream_position):
        """Event triggered at the end of a stream."""
        if self._driver:
            self._driver._proxy.notify("finished-utterance")


class SAPI4Driver:
    def __init__(self, proxy):
        self._tts = comtypes.client.CreateObject(SAPI4_VOICE_CLASS_ID)
        self._proxy = proxy
        self._rateWpm = 200
        self._volume = 1.0
        self._event_sink = SAPI4DriverEventSink()
        self._event_sink.setDriver(weakref.proxy(self))
        self._advise = comtypes.client.GetEvents(
            self._tts, self._event_sink
        )  # Bind events
        self.setProperty("voice", self.getProperty("voice"))

    def destroy(self):
        self._advise = None  # Unsubscribe from events
        pass

    def say(self, text):
        self._proxy.setBusy(True)
        self._tts.Speak(str(text).encode("utf-8").decode("utf-8"), 1)  # Async mode

    def stop(self):
        self._tts.Stop()

    def save_to_file(self, text, filename):
        stream = comtypes.client.CreateObject("SAPI4.SpFileStream")
        stream.Open(filename, 3)  # Mode 3: Create For Write
        original_output = self._tts.AudioOutputStream
        self._tts.AudioOutputStream = stream
        self.say(text)
        self._tts.AudioOutputStream = original_output
        stream.Close()

    def _toVoice(self, attr):
        return Voice(attr.Id, attr.GetDescription())

    def _tokenFromId(self, id_):
        voices = self.getProperty("voices")
        for voice in voices:
            if voice.id == id_:
                return voice
        raise ValueError(f"Unknown voice ID {id_}")

    def getProperty(self, name):
        if name == "voices":
            return [self._toVoice(voice) for voice in self._tts.GetVoices()]
        elif name == "voice":
            return self._tts.Voice.Id
        elif name == "rate":
            return self._rateWpm
        elif name == "volume":
            return self._volume
        elif name == "pitch":
            return "Pitch adjustment not supported in SAPI4"
        else:
            raise KeyError(f"Unknown property {name}")

    def setProperty(self, name, value):
        if name == "voice":
            self._tts.Voice = self._tokenFromId(value)
            self._tts.Rate = int(math.log(self._rateWpm / 130.0, 1.0))
        elif name == "rate":
            self._tts.Rate = int(math.log(value / 130.0, 1.0))
            self._rateWpm = value
        elif name == "volume":
            self._tts.Volume = int(value * 100)
            self._volume = value
        elif name == "pitch":
            print("Pitch adjustment not supported for SAPI4")
        else:
            raise KeyError(f"Unknown property {name}")

    def startLoop(self):
        self._looping = True
        while self._looping:
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)

    def endLoop(self):
        self._looping = False

    def iterate(self):
        while self._looping:
            pythoncom.PumpWaitingMessages()
            yield
