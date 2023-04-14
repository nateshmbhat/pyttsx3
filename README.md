

[![Downloads](https://static.pepy.tech/personalized-badge/pyttsx4?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/project/pyttsx4)
[![Downloads](https://static.pepy.tech/personalized-badge/pyttsx4?period=month&units=international_system&left_color=black&right_color=green&left_text=downloads/month)](https://pepy.tech/project/pyttsx4)




the code is mostly from pyttsx3.

only because the repo pyttsx3 does not update for years and some new feature i want is not here, i cloned this repo.

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

6. add pitch support for sapi5(not tested yet). --3.0.7

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


