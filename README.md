the code is all from pyttsx3.

only because the repo pyttsx3 does not update for years and some new feature i want is not here, i cloned this repo.

the changelog:

1. add memory support for sapi. 
   eg: 
   
```
b = BytesIO()
engine.save_to_file('i am Hello World', b)
engine.runAndWait()
```

2. fix VoiceAge key error


3. fix for sapi save_to_file when it run on machine without outputsream device.

4. add memory support for espeak(not tested).

NOTE:
if save_to_file with BytesIO, there is no wav header in the BytesIO.
the format of the bytes data is that 2-bytes = one sample.
if you want to add a header, the format of the data is:
1-channel. 2-bytes of sample width.  22050-framerate.

how to add a wav header in memory:https://github.com/Jiangshan00001/pyttsx4/issues/2


#TBD:
add support for TTS.



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

Feel free to wrap another text-to-speech engine for use with ``pyttsx3``.

### Project Links :

* PyPI (https://pypi.python.org)
* GitHub (https://github.com/nateshmbhat/pyttsx3)
* Full Documentation (https://pyttsx3.readthedocs.org)


