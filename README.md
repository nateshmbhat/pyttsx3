# pyttsx3 (offline TTS or Text To Speech converter for Python 3)

[![Downloads](https://pepy.tech/badge/pyttsx3)](https://pepy.tech/project/pyttsx3) ![Downloads](https://pepy.tech/badge/pyttsx3/week)  [![](https://img.shields.io/github/languages/code-size/nateshmbhat/pyttsx3.svg?style=plastic)](https://github.com/nateshmbhat/pyttsx3)  [![](https://img.shields.io/github/license/nateshmbhat/pyttsx3?style=plastic)](https://github.com/nateshmbhat/pyttsx3) [![](https://img.shields.io/pypi/v/pyttsx3.svg?style=plastic)](https://github.com/nateshmbhat/pyttsx3) [![](https://img.shields.io/github/languages/top/nateshmbhat/pyttsx3.svg?style=plastic)](https://github.com/nateshmbhat/pyttsx3) [![](https://img.shields.io/badge/author-nateshmbhat-green.svg)](https://github.com/nateshmbhat)


`pyttsx3` is a text-to-speech conversion library in Python. Unlike alternative libraries, it works offline, and is compatible with both Python 2 and 3.

### Installation :


	pip install pyttsx3


If you recieve errors such as `No module named win32com.client`, `No module named win32`, or `No module named win32api`, you will need to additionally install `pypiwin32`.


### Usage :

```python3
import pyttsx3
engine = pyttsx3.init()
engine.say("I will speak this text")
engine.runAndWait()
```
	
**Changing Voice , Rate and Volume :**

```python3
import pyttsx3
engine = pyttsx3.init() # object creation

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate


"""VOLUME"""
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

engine.say("Hello World!")
engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()
engine.stop()
```

#### **Full documentation of the Library**

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
