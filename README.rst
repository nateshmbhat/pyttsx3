*****************************************************
pyttsx3 (pyttsx for Python 3: offline TTS for Python)
*****************************************************

``pyttsx3`` is a text-to-speech conversion library in Python. Unlike alternative libraries, it works offline, and is compatible with both Python 2 and 3.

Installation
************
::

	pip install pyttsx3


If you recieve errors such as ``No module named win32com.client``, ``No module named win32``, or ``No module named win32api``, you will need to additionally install ``pypiwin32``.


Usage :
************
::

	import pyttsx3
	engine = pyttsx3.init()
	engine.say("I will speak this text")
	engine.runAndWait()


**Full documentation of the Library**
#####################################

https://pyttsx3.readthedocs.io/en/latest/


Included TTS engines:
*********************
* sapi5
* nsss
* espeak

Feel free to wrap another text-to-speech engine for use with ``pyttsx3``.

Project Links:
**************

* PyPI (https://pypi.python.org)
* GitHub (https://github.com/nateshmbhat/pyttsx3)
* Full Documentation (https://pyttsx3.readthedocs.org)
