#coding:utf-8
import time
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

        self._proxy = proxy
        self._looping = False
        self._speaking = False
        self._stopping = False


    def destroy(self):
        self._tts=None

    def say(self, text):
        # self._proxy.setBusy(True)
        # self._proxy.notify('started-utterance')
        # self._speaking = True
        # self._tts.Speak(self.pitch_str+fromUtf8(toUtf8(text)))
        # TBD
        pass

    def stop(self):
        # if not self._speaking:
        #     return
        # self._proxy.setBusy(True)
        # self._stopping = True
        # self._tts.Speak('', 3)
        pass

    def save_to_file(self, text, filename):
        self._tts.tts_to_file(text, filename)
        


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
            return TTS.list_models()
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
            time.sleep(0.05)

    def endLoop(self):
        self._looping = False

    def iterate(self):
        self._proxy.setBusy(False)
        while 1:
            yield
