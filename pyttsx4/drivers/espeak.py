
import time
import ctypes
import io
import wave
import os
from tempfile import NamedTemporaryFile
from ..voice import Voice
from . import _espeak, toUtf8, fromUtf8


def buildDriver(proxy):
    return EspeakDriver(proxy)


class EspeakDriver(object):
    _moduleInitialized = False
    _defaultVoice = ''

    def __init__(self, proxy):
        if not EspeakDriver._moduleInitialized:
            # espeak cannot initialize more than once per process and has
            # issues when terminating from python (assert error on close)
            # so just keep it alive and init once
            rate = _espeak.Initialize(_espeak.AUDIO_OUTPUT_RETRIEVAL, 1000)
            if rate == -1:
                raise RuntimeError('could not initialize espeak')
            EspeakDriver._defaultVoice = 'default'
            EspeakDriver._moduleInitialized = True
        _espeak.SetSynthCallback(self._onSynth)
        # make sure all props reset
        self.setProperty('voice', EspeakDriver._defaultVoice)
        self.setProperty('rate', 200)
        self.setProperty('volume', 1.0)
        self._proxy = proxy
        self._looping = True
        self._stopping = False
        self._data_buffer = b''
        self._numerise_buffer = []
        self.to_filename = None

    def numerise(self, data):
        self._numerise_buffer.append(data)
        return ctypes.c_void_p(len(self._numerise_buffer))

    def decode_numeric(self, data):
        return self._numerise_buffer[int(data) - 1]

    def destroy(self):
        _espeak.SetSynthCallback(None)

    def say(self, text):
        self.to_filename=None
        self._proxy.setBusy(True)
        self._proxy.notify('started-utterance')
        _espeak.Synth(toUtf8(text), flags=_espeak.ENDPAUSE |
                      _espeak.CHARS_UTF8)

    def stop(self):
        if _espeak.IsPlaying():
            self._stopping = True

    def getProperty(self, name):
        if name == 'voices':
            voices = []
            for v in _espeak.ListVoices(None):
                kwargs = {}
                kwargs['id'] = fromUtf8(v.name)
                kwargs['name'] = fromUtf8(v.name)
                if v.languages:
                    kwargs['languages'] = [v.languages]
                genders = [None, 'male', 'female']
                kwargs['gender'] = genders[v.gender]
                kwargs['age'] = v.age or None
                voices.append(Voice(**kwargs))
            return voices
        elif name == 'voice':
            voice = _espeak.GetCurrentVoice()
            return fromUtf8(voice.contents.name)
        elif name == 'rate':
            return _espeak.GetParameter(_espeak.RATE)
        elif name == 'volume':
            return _espeak.GetParameter(_espeak.VOLUME) / 100.0
        elif name == 'pitch':
            return _espeak.GetParameter(_espeak.PITCH)
        else:
            raise KeyError('unknown property %s' % name)

    def setProperty(self, name, value):
        if name == 'voice':
            if value is None:
                return
            try:
                utf8Value = toUtf8(value)
                _espeak.SetVoiceByName(utf8Value)
            except ctypes.ArgumentError as e:
                raise ValueError(str(e))
        elif name == 'rate':
            try:
                _espeak.SetParameter(_espeak.RATE, value, 0)
            except ctypes.ArgumentError as e:
                raise ValueError(str(e))
        elif name == 'volume':
            try:
                _espeak.SetParameter(
                    _espeak.VOLUME, int(round(value * 100, 2)), 0)
            except TypeError as e:
                raise ValueError(str(e))
        elif name == 'pitch':
            try:
                _espeak.SetParameter(
                    _espeak.PITCH, int(value), 0
                )
            except TypeError as e:
                raise ValueError(str(e))
        else:
            raise KeyError('unknown property %s' % name)

    def startLoop(self):
        first = True
        self._stopping = False
        self._looping = True
        while self._looping:
            if first:
                # kick the queue
                self._proxy.setBusy(False)
                first = False
            if self._stopping and self._looping:
                # have to do the cancel on the main thread, not inside the
                # callback else deadlock
                _espeak.Cancel()
                self._stopping = False
                self._proxy.notify('finished-utterance', completed=False)
                self._proxy.setBusy(False)
            time.sleep(0.01)

    def save_to_file(self, text, filename):
        self._proxy.setBusy(True)
        self._proxy.notify('started-utterance')  
        self.to_filename = filename
        if isinstance(filename, io.BytesIO):
            code = None
        else:
            code = self.numerise(self.to_filename)
        _espeak.Synth(toUtf8(text), flags=_espeak.ENDPAUSE |
                    _espeak.CHARS_UTF8, user_data=code)

    def endLoop(self):
        self._looping = False

    def iterate(self):
        self._proxy.setBusy(False)
        while 1:
            if self._stopping:
                # have to do the cancel on the main thread, not inside the
                # callback else deadlock
                _espeak.Cancel()
                self._stopping = False
                self._proxy.notify('finished-utterance', completed=False)
                self._proxy.setBusy(False)
            yield

    def _onSynth(self, wav, numsamples, events):
        i = 0
        while True:
            event = events[i]
            if event.type == _espeak.EVENT_LIST_TERMINATED:
                break
            if event.type == _espeak.EVENT_WORD:
                self._proxy.notify('started-word',
                                   location=event.text_position - 1,
                                   length=event.length)
            elif event.type == _espeak.EVENT_MSG_TERMINATED:

                if isinstance(self.to_filename,io.BytesIO):
                    self.to_filename.write(self._data_buffer)
                elif event.user_data:
                    stream = NamedTemporaryFile()
                    with wave.open(stream, 'wb') as f:
                        f.setnchannels(1)
                        f.setsampwidth(2)
                        f.setframerate(22050.0)
                        f.writeframes(self._data_buffer)
                    os.system('ffmpeg -y -i {} {} -loglevel quiet'.format(stream.name, self.decode_numeric(event.user_data)))
                else:
                    stream = NamedTemporaryFile()
                    with wave.open(stream, 'wb') as f:
                        f.setnchannels(1)
                        f.setsampwidth(2)
                        f.setframerate(22050.0)
                        f.writeframes(self._data_buffer)
                    os.system('aplay {} -q'.format(stream.name))  # -q for quiet

                self._data_buffer = b''
                self._proxy.notify('finished-utterance', completed=True)
                self._proxy.setBusy(False)
            i += 1
        
        if numsamples > 0:
            self._data_buffer += ctypes.string_at(wav, numsamples *
                                                ctypes.sizeof(ctypes.c_short))
        return 0
