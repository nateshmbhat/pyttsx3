#coding:utf-8

try:
    from TTS.api import TTS
except ImportError:
    import sys, subprocess
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'TTS'])


def buildDriver(proxy):
    return TTSDriver(proxy)


class TTSDriver(object):
    def __init__(self, proxy):

        self.model_name = TTS.list_models()[0]
        self._tts = TTS(self.model_name)

        # all events
        self._tts.EventInterests = 33790

        self._proxy = proxy
        self._looping = False
        self._speaking = False
        self._stopping = False


    def destroy(self):
        self._tts=None

    def say(self, text):
        self._proxy.setBusy(True)
        self._proxy.notify('started-utterance')
        self._speaking = True
        self._tts.Speak(self.pitch_str+fromUtf8(toUtf8(text)))

    def stop(self):
        if not self._speaking:
            return
        self._proxy.setBusy(True)
        self._stopping = True
        self._tts.Speak('', 3)

    def save_to_file(self, text, filename):
        if isinstance(filename, BytesIO):
            self.to_memory(text, filename)
            return

        cwd = os.getcwd()
        stream = comtypes.client.CreateObject('SAPI.SPFileStream')
        stream.Open(filename, SpeechLib.SSFMCreateForWrite)

        # in case there is no outputstream, the call to AudioOutputStream will fail
        is_stream_stored = False
        try:
            temp_stream = self._tts.AudioOutputStream
            is_stream_stored=True
        except Exception as e:
            #no audio output stream
            pass
        self._tts.AudioOutputStream = stream
        self._tts.Speak(self.pitch_str+fromUtf8(toUtf8(text)))
        if is_stream_stored:
            self._tts.AudioOutputStream = temp_stream
        else:
            try:
                self._tts.AudioOutputStream = None
            except Exception as e:
                print('set None no no-output stream machine:', e)
                pass
        stream.close()
        os.chdir(cwd)

    def to_memory(self, text, olist):
        stream = comtypes.client.CreateObject('SAPI.SpMemoryStream')
        temp_stream = self._tts.AudioOutputStream
        self._tts.AudioOutputStream = stream
        self._tts.Speak(self.pitch_str+fromUtf8(toUtf8(text)))
        self._tts.AudioOutputStream = temp_stream
        data = stream.GetData()
        olist.write(bytes(data))
        del stream

    def _toVoice(self, attr):
        return Voice(attr.Id, attr.GetDescription())

    def _tokenFromId(self, id_):
        tokens = self._tts.GetVoices()
        for token in tokens:
            if token.Id == id_:
                return token
        raise ValueError('unknown voice id %s', id_)

    def getProperty(self, name):
        if name == 'voices':
            return [self._toVoice(attr) for attr in self._tts.GetVoices()]
        elif name == 'voice':
            return self._tts.Voice.Id
        elif name == 'rate':
            return self._rateWpm
        elif name == 'volume':
            return self._tts.Volume / 100.0
        elif name == 'pitch':
            return self.pitch
            #print("Pitch adjustment not supported when using SAPI5")
        else:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
        if name == 'voice':
            token = self._tokenFromId(value)
            self._tts.Voice = token
            a, b = E_REG.get(value, E_REG[MSMARY])
            self._tts.Rate = int(math.log(self._rateWpm / a, b))
        elif name == 'rate':
            id_ = self._tts.Voice.Id
            a, b = E_REG.get(id_, E_REG[MSMARY])
            try:
                rate = int(math.log(value / a, b))
                if rate<-10:
                    rate = -10
                if rate>10:
                    rate = 10
                self._tts.Rate = int(math.log(value / a, b))
            except TypeError as e:
                raise ValueError(str(e))
            self._rateWpm = value
        elif name == 'volume':
            try:
                self._tts.Volume = int(round(value * 100, 2))
            except TypeError as e:
                raise ValueError(str(e))
        elif name == 'pitch':
            #-10 ->10
            self.pitch = value
            self.pitch_str = '<pitch absmiddle="'+str(value)+'"/>'
        else:
            raise KeyError('unknown property %s' % name)

    def startLoop(self):
        self._looping = True
        first = True
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


class SAPI5DriverEventSink(object):
    def __init__(self):
        self._driver = None

    def setDriver(self, driver):
        self._driver = driver

    def _ISpeechVoiceEvents_StartStream(self, char, length):
        self._driver._proxy.notify(
            'started-word', location=char, length=length)

    def _ISpeechVoiceEvents_EndStream(self, stream, pos):
        d = self._driver
        if d._speaking:
            d._proxy.notify('finished-utterance', completed=not d._stopping)
        d._speaking = False
        d._stopping = False
        d._proxy.setBusy(False)
