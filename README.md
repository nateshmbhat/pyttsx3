# pyttsx3 ( pyttsx for python3 : offline tts for python )


Pyttsx for python3 [ Offline text to speech for python3]

Pyttsx is a good text to speech conversion library in python but it was written only in python2 untill now !
Even some fair amount of googling didn't help much to get a tts library compatible with Python3. 

There is however , one library **gTTS** which works perfectly in python3 but it needs internet connection to work since it relies on google to get the audio data.But Pyttsx is completely offline and works seemlesly and has multiple tts-engine support.The codes in this repos are slightly modified version of the pyttsx module of python 2.x and is a clone from westonpace's repo. The purpose of creating this repo is to help those who want to have an offline tts lib for Python3 and don't want to port  it from python2 to python3 themselves. Also `pip install pyttsx` doesn't download the fixed python3 version of the library.


### Note : pyttsx3 library now works for both python2 and python3


Fixes for possible errors :
---------------------------

+ **No module named win32com.client**
  
```
pip install win32
pip install win32com
```

+ **No moudle named win32api**
  
`pip install pypiwin32`


How to install : 
----------------

`pip install pyttsx3`


Usage :
-------

**[Usage is same as that of the pyttsx]**
```
import pyttsx3;
engine = pyttsx3.init();
engine.say("I will speak this text");
engine.runAndWait() ; 
```
#### Included TTS engines :
+ sapi5
+ nsss
+ espeak

**Feel free to wrap another text-to-speech engine for use with pyttsx.**

**The Documentation for using the library is included in the docs directory of this repository.
