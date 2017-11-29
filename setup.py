'''MIT License

Copyright (c) 2017 nateshmbhat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

import platform
from setuptools import setup

install_requires = []
if platform.system() == 'Windows':
    install_requires = [
        'pypiwin32'
    ]
elif platform.system() == 'Darwin':
    install_requires = [
        'pyobjc>=2.4'
    ]

with open('README.rst' , 'r') as f:
    long_description = f.read() 

setup(

    name='pyttsx3',
    packages = ['pyttsx3','pyttsx3.drivers'] ,
    version = '2.7',
    description = '''An OFFLINE Python Text to Speech library (TTS) which works for both python3 and python2.This library very usefull especially if you don't want any delay in the speech produced and don't want to depend only on the internet for TTS conversion. It also supports multiple TTS engines like Sapi5 , nsss , espeak .
''' ,
    long_description = long_description , 
    summary = 'Offline Text to Speech library with multi-engine support'  ,
    author = 'Natesh M Bhat' ,
    url = 'https://github.com/nateshmbhat/pyttsx3',
    author_email = 'nateshmbhatofficial@gmail.com' ,
    #download_url = 'https://github.com/nateshmbhat/pyttsx3/archive/v2.6.tar.gz',
    keywords=['pyttsx' , 'ivona','pyttsx for python3' , 'TTS for python3' , 'pyttsx3' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [] ,
    install_requires=install_requires
)
