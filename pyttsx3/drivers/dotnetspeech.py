import clr
import threading
import queue
import time


def get_dotnet_speech_classes():
    """Sets up .NET references and imports System.Speech classes explicitly from GAC."""
    clr.AddReference(r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\System.Speech\v4.0_4.0.0.0__31bf3856ad364e35\System.Speech")
    from System.Speech.Synthesis import SpeechSynthesizer, SpeakCompletedEventArgs
    return SpeechSynthesizer, SpeakCompletedEventArgs


SpeechSynthesizer, SpeakCompletedEventArgs = get_dotnet_speech_classes()


def buildDriver(proxy):
    return DotNetSpeech(proxy)

class DotNetSpeech:
    def __init__(self, proxy):
        # Initialize .NET SpeechSynthesizer
        print("Initializing DotNetSpeech driver...")
        self._synthesizer = SpeechSynthesizer()
        self._proxy = proxy
        self._queue = queue.Queue()
        self._speaking = False
        self._looping = False
        self._stop_requested = False
        self._rate = 1.0
        self._volume = 1.0
        self._current_voice = None
        self._synthesizer.SpeakCompleted += self._on_speak_completed
        print("DotNetSpeech driver initialized.")

    def say(self, text):
        print(f"SAY Adding text to queue: {text}")
        try:
            """Queue a speech request."""
            print("Queueing speech request...")
            self._queue.put(("say", text))  # Add speech command to the queue
            print(f"Queue size after adding: {self._queue.qsize()}")
        except Exception as e:
            print(f"Error queuing speech request: {e}")
            
        # Do not set busy here; rely on _start_processing to set it when processing starts

    def _on_speak_completed(self, sender, event_args):
        """Callback for when asynchronous speech completes."""
        self._speaking = False
        print("Speech completed.")
        self._proxy.setBusy(False)  # Set busy to False when speech is done
        self._proxy.notify("finished-utterance", completed=True)

    def _start_processing(self):
        """Process the speech queue in a background thread."""
        if not self._speaking and not self._queue.empty():
            print("[DEBUG] Processing queue in DotNetSpeech...")
            self._speaking = True
            action, text = self._queue.get()
            print(f"Executing action: {action} with text: {text}")
            if action == "say":
                self._proxy.setBusy(True)  # Set busy when starting to speak
                speech_thread = threading.Thread(
                    target=self._synthesizer.SpeakAsync, args=(text,)
                )
                speech_thread.start()

    def startLoop(self):
        self._looping = True
        print("[DEBUG] Starting loop in DotNetSpeech...")
        while self._looping:
            self._start_processing()
            time.sleep(0.1)
        print("[DEBUG] Loop ended in DotNetSpeech.")

    def endLoop(self):
        """End the internal loop."""
        print("Ending loop...")
        self._looping = False

    def runAndWait(self):
        """Run an event loop until all commands queued up until this method call complete."""
        print("Running and waiting for all commands to complete...")
        self.startLoop()  # Starts processing the queue
        while self._proxy.isBusy():  # Wait until all speech commands are processed
            time.sleep(0.1)
        self.endLoop()  # Ends the loop after processing is complete


    def stop(self):
        """Stop current speech and clear the queue."""
        self._stop_requested = True
        self._synthesizer.SpeakAsyncCancelAll()
        self._queue.queue.clear()
        self._proxy.setBusy(False)
        self.notify("finished-utterance", name=self._current_text, completed=False)  # Notify of interruption


    def save_to_file(self, text, filename):
        """Save spoken text to a file."""
        self._synthesizer.SetOutputToWaveFile(filename)
        self._synthesizer.Speak(text)
        self._synthesizer.SetOutputToDefaultAudioDevice()

    def setProperty(self, name, value):
        """Set properties like rate and volume."""
        if name == "rate":
            self._synthesizer.Rate = int(value * 10)
            self._rate = value
        elif name == "volume":
            self._synthesizer.Volume = int(value * 100)
            self._volume = value
        elif name == "voice":
            self._synthesizer.SelectVoice(value)
            self._current_voice = value
        else:
            raise KeyError(f"Unknown property '{name}'")

    def getProperty(self, name):
        """Get property values."""
        if name == "rate":
            return self._rate
        elif name == "volume":
            return self._volume
        elif name == "voices":
            voices = []
            for voice in self._synthesizer.GetInstalledVoices():
                info = voice.VoiceInfo
                voices.append(
                    Voice(
                        id=info.Id,
                        name=info.Name,
                        languages=[info.Culture.Name],
                        gender=info.Gender.ToString(),
                        age=info.Age.ToString(),
                    )
                )
            return voices
        elif name == "voice":
            return self._current_voice
        else:
            raise KeyError(f"Unknown property '{name}'")

