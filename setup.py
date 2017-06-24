from distutils.core import setup

setup(

    name='pyttsx3',
    packages = ['pyttsx3'] ,
    version = '1.0',
    description = '''
An OFFLINE Python Text to Speech library (TTS) which works for both python3 and python2.
This library very usefull especially if you don't want any delay in the speech produced and don't want to depend only on the internet for TTS conversion.
It also supports multiple TTS engines like Sapi5 , nsss

Installation :-

pip install pyttsx3


Usage :-

import pyttsx3
engine = pyttsx3.init()
engine.say("Hello its me . I am a talking computer.")
engine.say("This is my second sentence")
engine.runAndWait()


complete usage docs can be found at :- 

''' ,
    summary = 'Offline Text to Speech library with multi-engine support'  ,
    author = 'Natesh M Bhat' ,
    url = 'https://github.com/nateshmbhat/pyttsx3',
    author_email = 'nateshmbhatofficial@gmail.com' ,
    download_url = 'https://github.com/nateshmbhat/pyttsx3/archive/1.0.tar.gz',
    keywords=['ivona','pyttsx for python3' , 'TTS for python3' , 'pyttsx3' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [] ,

)