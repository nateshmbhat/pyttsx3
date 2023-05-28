#coding:utf-8
import time
import numpy as np
import pyaudio

try:
    from TTS.api import TTS
except ImportError:
    import sys, subprocess
    print('no TTS package. installing...')
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'TTS', '-i','https://mirrors.aliyun.com/pypi/simple/'])
    from TTS.api import TTS

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
        
        self.speaker_wav = None


    def destroy(self):
        self._tts=None

    def say(self, text):
        if self._tts.is_multi_speaker:
            wav = self._tts.tts(text, speaker_wav=self.speaker_wav, speaker=self._tts.speakers[0], language=self._tts.languages[0])
        else:
            wav = self._tts.tts(text, 
                            speaker_wav=self.speaker_wav)
        #speaker=self._tts.speakers[0], language=self._tts.languages[0],
        # wav is the raw data of the wav file
        #format: sample_rate:16000 self._tts.synthesizer.tts_config.audio["sample_rate"]
        #format: sample_width:2
        #format: channels:1

        # wav是 -1.0-+1.0 转为 -32768-+32767
        #wav = (wav * 32767)
        # wav 从list转为np.array
        wav = np.array(wav, dtype=np.float32)
        # wav 从-1.0-+1.0 转为 -32768-+32767
        wav = (wav * 32767).astype(np.int16)
        wav = wav.tobytes()
        
        # list 转为bytes类型
        #wav = np.array(wav, dtype=np.int16).tobytes()
        
        # 播放wav
        # import wave
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=16000,
                        output=True)
        stream.write(wav)
        stream.stop_stream()
        stream.close()
        p.terminate()

        self.endLoop()

    def stop(self):
        self.endLoop()

    def save_to_file(self, text, filename):
        if self._tts.is_multi_speaker:
            self._tts.tts_to_file(text=text, file_path = filename, speaker_wav = self.speaker_wav, speaker=self._tts.speakers[0], language=self._tts.languages[0])
        else:
            self._tts.tts_to_file(text=text, file_path = filename, speaker_wav = self.speaker_wav)
        
    def getProperty(self, name):
        if name == 'voices':
            return TTS.list_models()
        elif name == 'voice':
            return self.model_name
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
            self.model_name = value
            self._tts = TTS(model_name=self.model_name)
            return

        elif name == 'rate':
            pass
        elif name == 'volume':
            pass
        elif name == 'pitch':
            pass
        elif name == 'speaker_wav':
            self.speaker_wav = value
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
