import clr
import threading
import queue
import time


def get_dotnet_speech_classes():
    """Sets up .NET references and imports System.Speech classes."""
    clr.AddReference("System.Speech")
    from System.Speech.Synthesis import SpeechSynthesizer, SpeakCompletedEventArgs

    return SpeechSynthesizer, SpeakCompletedEventArgs


SpeechSynthesizer, SpeakCompletedEventArgs = get_dotnet_speech_classes()


def buildDriver(proxy):
    return DotNetSpeech(proxy)


class DotNetSpeech:
    def __init__(self, proxy):
        # Initialize .NET SpeechSynthesizer
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

    def _on_speak_completed(self, sender, event_args: SpeakCompletedEventArgs):
        """Callback for when speech completes."""
        if self._stop_requested:
            self._stop_requested = False
        else:
            self._proxy.notify("finished-utterance", completed=True)
        self._speaking = False
        self._proxy.setBusy(False)

    def say(self, text):
        """Queue a speech request."""
        self._queue.put(("say", text))
        self._proxy.setBusy(True)
        self._start_processing()

    def stop(self):
        """Stop current speech and clear the queue."""
        self._stop_requested = True
        self._synthesizer.SpeakAsyncCancelAll()
        self._queue.queue.clear()

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

    def _start_processing(self):
        """Process the speech queue in a background thread."""
        if not self._speaking and not self._queue.empty():
            self._speaking = True
            action, text = self._queue.get()
            if action == "say":
                threading.Thread(
                    target=self._synthesizer.SpeakAsync, args=(text,)
                ).start()

    def startLoop(self):
        """Start an internal loop to process the queue."""
        self._looping = True
        while self._looping:
            self._start_processing()
            time.sleep(0.1)

    def endLoop(self):
        """End the internal loop."""
        self._looping = False
