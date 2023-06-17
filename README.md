

[![Downloads](https://static.pepy.tech/personalized-badge/pyttsx4?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/project/pyttsx4)
[![Downloads](https://static.pepy.tech/personalized-badge/pyttsx4?period=month&units=international_system&left_color=black&right_color=green&left_text=downloads/month)](https://pepy.tech/project/pyttsx4)


the code is mostly from pyttsx3.

only because the repo pyttsx3 does not update for years and some new feature i want is not here, i cloned this repo.

feature:

# supported engines:

```
1 nsss
2 sapi5
3 espeak
4 coqui_ai_tts
```

# basic features:

1 say
```
engine = pyttsx4.init()
engine.say('this is an english text to voice test.')
engine.runAndWait()
```
2 save to file

```
import pyttsx4

engine = pyttsx4.init()
engine.save_to_file('i am Hello World, i am a programmer. i think life is short.', 'test1.wav')
engine.runAndWait()

```


# extra features:

1 memory support for sapi5, nsss, espeak.
NOTE: the memory is just raw adc data, wav header has to be added if you want to save to wav file.

```
import pyttsx4
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import os
import sys

engine = pyttsx4.init()
b = BytesIO()
engine.save_to_file('i am Hello World', b)
engine.runAndWait()
#the bs is raw data of the audio.
bs=b.getvalue()
# add an wav file format header
b=bytes(b'RIFF')+ (len(bs)+38).to_bytes(4, byteorder='little')+b'WAVEfmt\x20\x12\x00\x00' \
                                                               b'\x00\x01\x00\x01\x00' \
                                                               b'\x22\x56\x00\x00\x44\xac\x00\x00' +\
    b'\x02\x00\x10\x00\x00\x00data' +(len(bs)).to_bytes(4, byteorder='little')+bs
# changed to BytesIO
b=BytesIO(b)
audio = AudioSegment.from_file(b, format="wav")
play(audio)

sys.exit(0)
```


2 cloning voice 
```
# only coqui_ai_tts engine support cloning voice.
engine = pyttsx4.init('coqui_ai_tts')
engine.setProperty('speaker_wav', './docs/i_have_a_dream_10s.wav')

engine.say('this is an english text to voice test, listen it carefully and tell who i am.')
engine.runAndWait()


```

voice clone test1:

![speaker_wav_test_1](./docs/i_have_a_dream_10s.wav)
![the output1](./docs/test_mtk.wav)


voice clone test2:

![speaker_wav_test_2](./docs/the_ballot_or_the_bullet_15s.wav)
![the output2](./docs/test_mx.wav)



----------------







the changelog:

1. add memory support for sapi5
2. add memory support for espeak(espeak is not tested). 
   eg: 
   
```
b = BytesIO()
engine.save_to_file('i am Hello World', b)
engine.runAndWait()
```

3. fix VoiceAge key error


4. fix for sapi save_to_file when it run on machine without outputsream device.

5. fix  save_to_file does not work on mac os ventura error. --3.0.6

6. add pitch support for sapi5(not tested yet). --3.0.8

7. fix nsss engine: Import super from objc to fix AttributeError by @matt-oakes.

8. add tts support:
   deep-learning text to voice backend:

just say:
```
engine = pyttsx4.init('coqui_ai_tts')
engine.say('this is an english text to voice test.')
engine.runAndWait()
```

cloning someones voice:

```
engine = pyttsx4.init('coqui_ai_tts')
engine.setProperty('speaker_wav', './someones_voice.wav')

engine.say('this is an english text to voice test.')
engine.runAndWait()

```

demo output:

![test2](./docs/test2.wav)





NOTE:

if save_to_file with BytesIO, there is no wav header in the BytesIO.
the format of the bytes data is that 2-bytes = one sample.

if you want to add a header, the format of the data is:
1-channel. 2-bytes of sample width.  22050-framerate.

how to add a wav header in memory:https://github.com/Jiangshan00001/pyttsx4/issues/2


# how to use:

install:
```
pip install pyttsx4
```

use:

```
import pyttsx4
engine = pyttsx4.init()
```

the  other usage is the same as the pyttsx3



----------------------



### **Full documentation of the Library**

https://pyttsx3.readthedocs.io/en/latest/


#### Included TTS engines:

* sapi5
* nsss
* espeak

Feel free to wrap another text-to-speech engine for use with ``pyttsx4``.

### Project Links :

* PyPI (https://pypi.python.org)
* GitHub (https://github.com/Jiangshan00001/pyttsx4)
* Full Documentation (https://pyttsx3.readthedocs.org)


