import pyttsx3
from io import BytesIO

engine = pyttsx3.init()

# Create a BytesIO object to store the audio data
byte_stream = BytesIO()

# Capture the text as a byte stream
engine.bytestream("Hello World!", byte_stream)
engine.bytestream("This is another example.", byte_stream)
engine.runAndWait()
print(byte_stream.getvalue())

# Now you have the byte_stream containing the audio data, which you can save or process
with open("output.wav", "wb") as f:
    f.write(byte_stream.getvalue())

engine.stop()