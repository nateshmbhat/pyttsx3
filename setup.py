import platform
from setuptools import setup


# Ubuntu: sudo apt install espeak ffmpeg
install_requires = [
    'comtypes; platform_system == "Windows"',
    'pypiwin32; platform_system == "Windows"',
    'pywin32; platform_system == "Windows"',
    'pyobjc>=2.4; platform_system == "Darwin"',
    'six'
]


with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='pyttsx4',
    packages=['pyttsx4', 'pyttsx4.drivers'],
    version='3.0.15',
   description='Text to Speech (TTS) library for Python 3. Works without internet connection or delay. Supports multiple TTS engines, including Sapi5, nsss, and espeak.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    summary='Offline Text to Speech library with multi-engine support',
    author='Natesh M Bhat',
    url='https://github.com/Jiangshan00001/pyttsx4',
    author_email='710806594@qq.com',
    install_requires=install_requires ,
    keywords=['pyttsx' , 'ivona','pyttsx for python3' , 'TTS for python3' , 'pyttsx4' ,'text to speech for python','tts','text to speech','speech','speech synthesis','offline text to speech','offline tts','gtts'],
    classifiers = [
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          ],
)
