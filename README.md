<p align="center">
  <img src=".github/logo.svg?sanitize=true" width="200px" height="200px">
</p>
<h2 align="center">Offline Text To Speech (TTS) converter for Python </h2>


[![Downloads](https://pepy.tech/badge/pyttsx3)](https://pepy.tech/project/pyttsx3) ![Downloads](https://pepy.tech/badge/pyttsx3/week)  [![](https://img.shields.io/github/languages/code-size/nateshmbhat/pyttsx3.svg?style=plastic)](https://github.com/nateshmbhat/pyttsx3)  [![](https://img.shields.io/github/license/nateshmbhat/pyttsx3?style=plastic)](https://github.com/nateshmbhat/pyttsx3) [![](https://img.shields.io/pypi/v/pyttsx3.svg?style=plastic)](https://pypi.org/project/pyttsx3/) [![](https://img.shields.io/github/languages/top/nateshmbhat/pyttsx3.svg?style=plastic)](https://github.com/nateshmbhat/pyttsx3) [![](https://img.shields.io/badge/author-nateshmbhat-green.svg)](https://github.com/nateshmbhat)


`pyttsx3` is a text-to-speech conversion library in Python. Unlike alternative libraries, **it works offline**.

<a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/nateshmbhat"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee 😇"><span style="margin-left:5px;font-size:19px !important;">Buy me a coffee 😇</span></a>

## Installation :

	pip install pyttsx3

> If you get installation errors , make sure you first upgrade your wheel version using :
`pip install --upgrade wheel`


## Features :

- ✨Fully **OFFLINE** text to speech conversion
- 🎈 Choose among different voices installed in your system
- 🎛 Control speed/rate of speech
- 🎚 Tweak Volume
- 📀 Save the speech audio as a file
- ❤️ Simple, powerful, & intuitive API


#### Linux installation requirements :

+ If you are on a Linux system and if the voice output is not working, then  :

	Install espeak-ng and libespeak1 as shown below:

	```
	sudo apt update && sudo apt install espeak-ng libespeak1
	```

## Usage :

```python3
import pyttsx3
engine = pyttsx3.init()

# For Mac, If you face error related to "pyobjc" when running the `init()` method :
# Install 9.0.1 version of pyobjc : "pip install pyobjc>=9.0.1"

engine.say("I will speak this text")
engine.runAndWait()
```

**Single line usage with speak function with default options**

```python3
import pyttsx3
pyttsx3.speak("I will speak this text")
```

**Changing Voice , Rate and Volume :**

```python3
import pyttsx3
engine = pyttsx3.init() # object creation

# RATE
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        # printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate

# VOLUME
volume = engine.getProperty('volume')   # getting to know current volume level (min=0 and max=1)
print (volume)                          # printing current volume level
engine.setProperty('volume',1.0)        # setting up volume level  between 0 and 1

# VOICE
voices = engine.getProperty('voices')       # getting details of current voice
#engine.setProperty('voice', voices[0].id)  # changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   # changing index, changes voices. 1 for female

engine.say("Hello World!")
engine.say('My current speaking rate is ' + str(rate))
engine.runAndWait()
engine.stop()

# Saving Voice to a file
# On Linux, make sure that 'espeak-ng' is installed
engine.save_to_file('Hello World', 'test.mp3')
engine.runAndWait()
```

### **Full documentation of the Library**

https://pyttsx3.readthedocs.io

#### Included Text-To-Speech Engines by Operating System
|                         | Linux | macOS | Windows |
|-------------------------|:-----:|:-----:|:-------:|
| [AVSpeech][]            |       |   ✅︎  |         |
| [eSpeak][]              |   ✅︎  |   ✅︎  |    ✅︎   |
| [NSSpeechSynthesizer][] |       |   ✅︎  |         |
| [SAPI5][]               |       |       |    ✅︎   |

> [!NOTE]
> * AVSpeechSynthesizer support is still experimental.
> * NSSpeechSynthesizer is deprecated by Apple.

[AVSpeech]: https://developer.apple.com/documentation/avfoundation/speech_synthesis
[eSpeak]: https://github.com/espeak-ng/espeak-ng?tab=readme-ov-file#readme
[NSSpeechSynthesizer]: https://developer.apple.com/documentation/appkit/nsspeechsynthesizer
[SAPI5]: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms723627(v=vs.85)

Feel free to wrap another text-to-speech engine for use with ``pyttsx3``.

### Project Links :

* PyPI (https://pypi.org/project/pyttsx3)
* GitHub (https://github.com/nateshmbhat/pyttsx3)
* Full Documentation (https://pyttsx3.readthedocs.org)
