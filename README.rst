*****************************************************
pyttsx3 (offline TTS for Python 3)
*****************************************************

``pyttsx3`` is a text-to-speech conversion library in Python. Unlike alternative libraries, it works offline, and is compatible with both Python 2 and 3.

Installation
************
::

	pip install pyttsx3


> If you get installation errors , make sure you first upgrade your wheel version using :  
`pip install --upgrade wheel`

**Linux installation requirements :**
#####################################

+ If you are on a linux system and if the voice output is not working , then  : 

Install espeak , ffmpeg and libespeak1 as shown below: 

::

	sudo apt update && sudo apt install espeak ffmpeg libespeak1


Usage :
************
::

	import pyttsx3
	engine = pyttsx3.init()
	engine.say("I will speak this text")
	engine.runAndWait()
	
	
**Changing Voice , Rate and Volume :**

::

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

	"""Saving Voice to a file"""
	# On linux make sure that 'espeak' and 'ffmpeg' are installed
	engine.save_to_file('Hello World', 'test.mp3')
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
