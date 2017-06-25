*******************************************************
pyttsx3 ( pyttsx for python3 : offline tts for python )
*******************************************************

Pyttsx for python3 [ Offline text to speech for python3]

Pyttsx is a good text to speech conversion library in python but it was written only in python2 untill now !
Even some fair amount of googling didn't help much to get a tts library compatible with Python3. 

There is however , one library **gTTS** which works perfectly in python3 but it needs internet connection to work since it relies on google to get the audio data.But Pyttsx is completely offline and works seemlesly and has multiple tts-engine support.The codes in this repos are slightly modified version of the pyttsx module of python 2.x and is a clone from westonpace's repo. The purpose of creating this repo is to help those who want to have an offline tts lib for Python3 and don't want to port  it from python2 to python3 themselves. 

This project has been dead for over some years now and `pip install pyttsx` doesn't download the fixed python3 version of the library. So i decided to go ahead with my own repository and spread the fixed version.




Note : pyttsx3 library now works for both python2 and python3 and is also cross-platform
****************************************************************************************

How to install :
****************
::

	pip install pyttsx3


Fixes for possible errors :
***************************

* **No module named win32com.client**
* **No module named win32**
* **No module named win32api**

::

	pip install pypiwin32



Usage :
*******

::

	import pyttsx3;
	engine = pyttsx3.init();
	engine.say("I will speak this text");
	engine.runAndWait() ; 


**Full documentation of the Library is available at**
#####################################################

https://pyttsx3.readthedocs.io/en/latest/

Included TTS engines :
**********************
* sapi5
* nsss
* espeak

**Feel free to wrap another text-to-speech engine for use with pyttsx3.**
########################################################################

Project Links :
***************

* Python Package Index for downloads (https://pypi.python.org)
* GitHub site for source , bugs, and Q&A (https://github.com/nateshmbhat/pyttsx3)
* Read the Full documentation at (https://pyttsx3.readthedocs.org)
