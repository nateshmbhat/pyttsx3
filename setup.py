import platform
from setuptools import setup


extras_require = {
    ':"darwin" in sys_platform': [
        'pyobjc>=2.4',
    ],
    ':"win32" in sys_platform': [
        'pypiwin32',
    ],
}

# Ubuntu: sudo apt install espeak
install_requires = []
if platform.system() == 'Windows':
    install_requires += [
        'pypiwin32'
    ]
elif platform.system() == 'Darwin':
    install_requires += [
        'pyobjc>=2.4'
    ]


with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name='pyttsx3',
    packages=['pyttsx3', 'pyttsx3.drivers'],
    version='2.7',
    description='Text to Speech (TTS) library for Python 2 and 3. Works without internet connection or delay. Supports multiple TTS engines, including Sapi5, nsss, and espeak.',
    long_description=long_description,
    summary='Offline Text to Speech library with multi-engine support',
    author='Natesh M Bhat',
    url='https://github.com/nateshmbhat/pyttsx3',
    author_email='nateshmbhatofficial@gmail.com',
    #download_url = 'https://github.com/nateshmbhat/pyttsx3/archive/v2.6.tar.gz',
    install_requires=install_requires
    keywords=['pyttsx' , 'ivona','pyttsx for python3' , 'TTS for python3' , 'pyttsx3' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [] ,
    extras_require=extras_require
)
