# noinspection PyUnresolvedReferences
import comtypes.client  # Importing comtypes.client will make the gen subpackage

try:
    from comtypes.gen import SpeechLib  # comtypes
except ImportError:
    # Generate the SpeechLib lib and any associated files
    engine = comtypes.client.CreateObject("SAPI.SpVoice")
    stream = comtypes.client.CreateObject("SAPI.SpFileStream")
    # noinspection PyUnresolvedReferences
    from comtypes.gen import SpeechLib

# noinspection PyUnresolvedReferences
import math
import os
import time
import weakref
from ctypes import c_int16
import pythoncom
from ..voice import Voice
from . import fromUtf8, toUtf8

# common voices
MSSAM = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSSam"
MSMARY = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSMary"
MSMIKE = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSMike"

# coeffs for wpm conversion
E_REG = {MSSAM: (137.89, 1.11), MSMARY: (156.63, 1.11), MSMIKE: (154.37, 1.11)}


# noinspection PyPep8Naming
def buildDriver(proxy):
    return SAPI5Driver(proxy)


# noinspection PyPep8Naming,PyShadowingNames
class SAPI5Driver(object):
    def __init__(self, proxy):
        self._tts = comtypes.client.CreateObject("SAPI.SPVoice")
        # all events
        self._tts.EventInterests = 33790
        self._event_sink = SAPI5DriverEventSink()
        self._event_sink.setDriver(weakref.proxy(self))
        self._advise = comtypes.client.GetEvents(self._tts, self._event_sink)
        self._proxy = proxy
        self._looping = False
        self._speaking = False
        self._stopping = False
        self._current_text = ""
        # initial rate
        self._rateWpm = 200
        self.setProperty("voice", self.getProperty("voice"))

    def destroy(self):
        self._tts.EventInterests = 0

    def say(self, text):
        self._proxy.setBusy(True)
        self._proxy.notify("started-utterance")
        self._speaking = True
        self._current_text = text
        # call this async otherwise this blocks the callbacks
        # see SpeechVoiceSpeakFlags: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ms720892%28v%3dvs.85%29
        # and Speak : https://docs.microsoft.com/en-us/previous-versions/windows/desktop/ms723609(v=vs.85)
        self._tts.Speak(
            fromUtf8(toUtf8(text)), 1
        )  # -> stream_number as described in the remarks of the documentation

    def stop(self):
        if not self._speaking:
            return
        self._proxy.setBusy(True)
        self._stopping = True
        self._tts.Speak("", 3)

    def save_to_file(self, text, filename):
        cwd = os.getcwd()
        stream = comtypes.client.CreateObject("SAPI.SPFileStream")
        stream.Open(filename, SpeechLib.SSFMCreateForWrite)
        temp_stream = self._tts.AudioOutputStream
        self._current_text = text
        self._tts.AudioOutputStream = stream
        self._tts.Speak(fromUtf8(toUtf8(text)))
        self._tts.AudioOutputStream = temp_stream
        stream.close()
        os.chdir(cwd)
        
    def to_memory(self, text, olist):
        stream = comtypes.client.CreateObject('SAPI.SpMemoryStream')
        temp_stream = self._tts.AudioOutputStream
        self._tts.AudioOutputStream = stream
        self._tts.Speak(fromUtf8(toUtf8(text)))
        self._tts.AudioOutputStream = temp_stream
        data = stream.GetData()        
        olist.append([c_int16((data[i])|data[i+1]<<8).value for i in range(0,len(data),2)])
        stream.close()
       

    @staticmethod
    def _toVoice(attr):
        return Voice(attr.Id, attr.GetDescription())

    def _tokenFromId(self, id_):
        tokens = self._tts.GetVoices()
        for token in tokens:
            if token.Id == id_:
                return token
        raise ValueError("unknown voice id %s", id_)

    def getProperty(self, name):
        if name == "voices":
            return [self._toVoice(attr) for attr in self._tts.GetVoices()]
        elif name == "voice":
            return self._tts.Voice.Id
        elif name == "rate":
            return self._rateWpm
        elif name == "volume":
            return self._tts.Volume / 100.0
        elif name == "pitch":
            print("Pitch adjustment not supported when using SAPI5")
        else:
            raise KeyError("unknown property %s" % name)

    def setProperty(self, name, value):
        if name == "voice":
            token = self._tokenFromId(value)
            self._tts.Voice = token
            a, b = E_REG.get(value, E_REG[MSMARY])
            self._tts.Rate = int(math.log(self._rateWpm / a, b))
        elif name == "rate":
            id_ = self._tts.Voice.Id
            a, b = E_REG.get(id_, E_REG[MSMARY])
            try:
                self._tts.Rate = int(math.log(value / a, b))
            except TypeError as e:
                raise ValueError(str(e))
            self._rateWpm = value
        elif name == "volume":
            try:
                self._tts.Volume = int(round(value * 100, 2))
            except TypeError as e:
                raise ValueError(str(e))
        elif name == "pitch":
            print("Pitch adjustment not supported when using SAPI5")
        else:
            raise KeyError("unknown property %s" % name)

    def startLoop(self):
        first = True
        self._looping = True
        while self._looping:
            if first:
                self._proxy.setBusy(False)
                first = False
            pythoncom.PumpWaitingMessages()
            time.sleep(0.05)

    def endLoop(self):
        self._looping = False

    def iterate(self):
        self._proxy.setBusy(False)
        while 1:
            pythoncom.PumpWaitingMessages()
            yield


# noinspection PyPep8Naming,PyProtectedMember,PyUnusedLocal,PyShadowingNames
class SAPI5DriverEventSink(object):
    def __init__(self):
        self._driver = None

    def setDriver(self, driver):
        self._driver = driver

    def _ISpeechVoiceEvents_StartStream(self, stream_number, stream_position):
        self._driver._proxy.notify(
            "started-word", location=stream_number, length=stream_position
        )

    def _ISpeechVoiceEvents_EndStream(self, stream_number, stream_position):
        d = self._driver
        if d._speaking:
            d._proxy.notify("finished-utterance", completed=not d._stopping)
        d._speaking = False
        d._stopping = False
        d._proxy.setBusy(False)
        d.endLoop()  # hangs if you dont have this

    def _ISpeechVoiceEvents_Word(self, stream_number, stream_position, char, length):
        current_text = self._driver._current_text
        if current_text:
            current_word = current_text[char : char + length]
        else:
            current_word = "Unknown"

        self._driver._proxy.notify(
            "started-word", name=current_word, location=char, length=length
        )
