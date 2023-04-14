``pyttsx4`` is a text-to-speech conversion library in Python. 


it is all from pyttsx3:

* GitHub (https://github.com/nateshmbhat/pyttsx3)
* Full Documentation (https://pyttsx3.readthedocs.org)



the changelog and update is listed below:


1. add memory support for sapi5
2. add memory support for espeak(espeak is not tested). 
   eg: 
   
```
b = BytesIO()
engine.save_to_file('i am Hello World', b)
engine.runAndWait()
```

3. fix VoiceAge key error


4. fix for sapi save_to_file when it run on machine without outputsream device.

5. fix  save_to_file does not work on mac os ventura error. --3.0.6

6. add pitch support for sapi5(not tested yet). --3.0.7



