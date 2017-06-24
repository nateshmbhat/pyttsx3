from distutils.core import setup

setup(

    name='pyttsx3',
    packages = ['pyttsx3'] ,
    version = '1.12',
    description = '''
An OFFLINE Python Text to Speech library (TTS) which works for both python3 and python2.
This library very usefull especially if you don't want any delay in the speech produced and don't want to depend only on the internet for TTS conversion.
It also supports multiple TTS engines like Sapi5 , nsss , espeak .
''' ,
    summary = 'Offline Text to Speech library with multi-engine support'  ,
    author = 'Natesh M Bhat' ,
    url = 'https://github.com/nateshmbhat/pyttsx3',
    author_email = 'nateshmbhatofficial@gmail.com' ,
    download_url = 'https://github.com/nateshmbhat/pyttsx3/archive/v1.12.tar.gz',
    keywords=['ivona','pyttsx for python3' , 'TTS for python3' , 'pyttsx3' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [] ,

)