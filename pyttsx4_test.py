# coding:utf-8

from io import BytesIO
import time

import pyttsx4

import os


def test_save_to_file():
    engine = pyttsx4.init()
    ############
    file_path = os.path.dirname(__file__)+'/test.wav'
    engine.save_to_file('Hello World', file_path)


def test_say():
    # engine = pyttsx4.init('coqui_ai_tts') # object creation
    engine = pyttsx4.init()

    ############
    engine.setProperty('pitch', -20)

    while True:
        # engine.save_to_file('Hello World', 'test.wav')
        engine.say('Hello world')
        engine.runAndWait()
        time.sleep(4)


def test_2():
    engine = pyttsx4.init()

    engine.setProperty('pitch', 0)
    # engine.save_to_file('Hello World', 'test.wav')
    engine.say('你好,我是一个程序员')
    engine.runAndWait()

    engine.setProperty('pitch', 10)
    # engine.save_to_file('Hello World', 'test.wav')
    engine.say('你好,我是一个程序员')
    engine.runAndWait()

    engine.setProperty('pitch', 50)
    # engine.save_to_file('Hello World', 'test.wav')
    engine.say('你好,我是一个程序员')
    engine.runAndWait()


def test_3():

    engine = pyttsx4.init()

    b = BytesIO()
    engine.save_to_file('Hello World', b)
    engine.runAndWait()

    bs = b.getvalue()
    # to save b as a wav file, we have to add a wav file header:44byte
    # https://docs.fileformat.com/audio/wav/
    # b= bytes(b'RIFF')+ (len(bs)+38).to_bytes(4, byteorder='little')+b'WAVEfmt\x20' +\
    #   (18).to_bytes(4, byteorder='little')+(1).to_bytes(2, byteorder='little') +(1).to_bytes(2, byteorder='little')+ \
    #   (22050).to_bytes(4,byteorder='little')+(44100).to_bytes(4,byteorder='little') +(2).to_bytes(2, byteorder='little')+\
    #   (16).to_bytes(2,byteorder='little')+b'\x00\x00'+  b'data'+ (len(bs)).to_bytes(4, byteorder='little')+bs

    b = bytes(b'RIFF') + (len(bs)+38).to_bytes(4, byteorder='little')+b'WAVEfmt\x20\x12\x00\x00' \
        b'\x00\x01\x00\x01\x00' \
        b'\x22\x56\x00\x00\x44\xac\x00\x00' +\
        b'\x02\x00\x10\x00\x00\x00data' + \
        (len(bs)).to_bytes(4, byteorder='little')+bs

    f = open('test4.wav', 'wb')
    f.write(b)
    f.close()

    engine.setProperty(
        'voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')

    engine.say('Hello World')
    engine.say('你好，世界')
    engine.runAndWait()

    """ RATE"""
    rate = engine.getProperty(
        'rate')   # getting details of current speaking rate
    print(rate)  # printing current voice rate
    engine.setProperty('rate', 125)     # setting up new voice rate

    """VOLUME"""
    volume = engine.getProperty(
        'volume')  # getting to know current volume level (min=0 and max=1)
    print(volume)  # printing current volume level
    # setting up volume level  between 0 and 1
    engine.setProperty('volume', 1.0)

    """VOICE"""
    voices = engine.getProperty('voices')  # getting details of current voice
    # engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
    # changing index, changes voices. 1 for female
    engine.setProperty('voice', voices[1].id)

    """PITCH"""
    pitch = engine.getProperty('pitch')  # Get current pitch value
    print(pitch)  # Print current pitch value
    # Set the pitch (default 50) to 75 out of 100
    engine.setProperty('pitch', 75)

    engine.say("Hello World!")
    engine.say('My current speaking rate is ' + str(rate))
    engine.runAndWait()
    engine.stop()

    """Saving Voice to a file"""
    # On linux make sure that 'espeak' and 'ffmpeg' are installed
    engine.save_to_file('Hello World', 'test.mp3')
    engine.runAndWait()

    if __name__ == '__main__':
        test_save_to_file()
