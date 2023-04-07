the code is all from pyttsx3.

### **Full documentation of the Library**

https://pyttsx3.readthedocs.io/en/latest/


#### Included TTS engines:

* sapi5
* nsss
* espeak

Feel free to wrap another text-to-speech engine for use with ``pyttsx3``.

### Project Links :

* PyPI (https://pypi.python.org)
* GitHub (https://github.com/nateshmbhat/pyttsx3)
* Full Documentation (https://pyttsx3.readthedocs.org)



only because the repo pyttsx3 does not update for years and some new feature i want is not here, i cloned this repo.

the changelog:

1. add memory support for sapi. 
   eg: 
   
```
b = BytesIO()
engine.save_to_file('i am Hello World', b)
engine.runAndWait()
```