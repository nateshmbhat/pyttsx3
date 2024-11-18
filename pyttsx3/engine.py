from __future__ import annotations

import sys
import traceback
import weakref

from . import driver

# https://docs.python.org/3/library/sys.html#sys.platform
# The keys are values of Python sys.platform, the values are tuples of engine names.
# The first engine in the value tuple is the default engine for that platform.
_engines_by_sys_platform = {
    "darwin": ("nsss", "espeak", "avspeech"),
    "win32": ("sapi5", "espeak"),
}


def engines_by_sys_platform() -> tuple[str]:
    """
    Return the names of all TTS engines for the current operating system.
    If sys.platform is not in _engines_by_sys_platform, return ("espeak",).
    """
    return _engines_by_sys_platform.get(sys.platform, ("espeak",))


def default_engine_by_sys_platform() -> str:
    """
    Return the name of the default TTS engine for the current operating system.
    The first engine in the value tuple is the default engine for that platform.
    """
    return engines_by_sys_platform()[0]


class Engine:
    """
    @ivar proxy: Proxy to a driver implementation
    @type proxy: L{DriverProxy}
    @ivar _connects: Array of subscriptions
    @type _connects: list
    @ivar _inLoop: Running an event loop or not
    @type _inLoop: bool
    @ivar _driverLoop: Using a driver event loop or not
    @type _driverLoop: bool
    @ivar _debug: Print exceptions or not
    @type _debug: bool.
    """

    def __init__(self, driverName: str | None = None, debug: bool = False) -> None:
        """
        Constructs a new TTS engine instance.

        @param driverName: Name of the platform specific driver to use. If
            None, selects the default driver for the operating system.
        @type: str
        @param debug: Debugging output enabled or not
        @type debug: bool
        """
        self.driver_name = driverName or default_engine_by_sys_platform()
        self.proxy = driver.DriverProxy(weakref.proxy(self), self.driver_name, debug)
        self._connects = {}
        self._debug = debug
        self._driverLoop = True
        self._inLoop = False

    def __repr__(self) -> str:
        """repr(pyttsx3.init('nsss')) -> "pyttsx3.engine.Engine('nsss', debug=False)"."""
        module_and_class = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return f"{module_and_class}('{self.driver_name}', debug={self._debug})"

    def __str__(self) -> str:
        """str(pyttsx3.init('nsss')) -> 'nsss'."""
        return self.driver_name

    def _notify(self, topic: str, **kwargs) -> None:
        """
        Invokes callbacks for an event topic.

        @param topic: String event name
        @type topic: str
        @param kwargs: Values associated with the event
        @type kwargs: dict
        """
        for cb in self._connects.get(topic, []):
            try:
                cb(**kwargs)
            except Exception:  # noqa: PERF203
                if self._debug:
                    traceback.print_exc()

    def connect(self, topic: str, cb: callable) -> dict:
        """
        Registers a callback for an event topic. Valid topics and their
        associated values:

        started-utterance: name=<str>
        started-word: name=<str>, location=<int>, length=<int>
        finished-utterance: name=<str>, completed=<bool>
        error: name=<str>, exception=<exception>

        @param topic: Event topic name
        @type topic: str
        @param cb: Callback function
        @type cb: callable
        @return: Token to use to unregister
        @rtype: dict
        """
        arr = self._connects.setdefault(topic, [])
        arr.append(cb)
        return {"topic": topic, "cb": cb}

    def disconnect(self, token: dict) -> None:
        """
        Unregisters a callback for an event topic.

        @param token: Token of the callback to unregister
        @type token: dict
        """
        topic = token["topic"]
        try:
            arr = self._connects[topic]
        except KeyError:
            return
        arr.remove(token["cb"])
        if len(arr) == 0:
            del self._connects[topic]

    def say(self, text: str | None, name: str | None = None) -> str | None:
        """
        Adds an utterance to speak to the event queue.

        @param text: Text to speak
        @type text: unicode
        @param name: Name to associate with this utterance. Included in
            notifications about this utterance.
        @type name: str
        """
        if str(text or "").strip():
            self.proxy.say(text, name)
            return None
        return "Argument value can't be None or empty"

    def stop(self) -> None:
        """Stops the current utterance and clears the event queue."""
        self.proxy.stop()

    def save_to_file(self, text: str, filename: str, name: str | None = None) -> None:
        """
        Adds an utterance to speak to the event queue.

        @param text: Text to speak
        @type text: unicode
        @param filename: the name of file to save.
        @param name: Name to associate with this utterance. Included in
            notifications about this utterance.
        @type name: str
        """
        assert text
        assert filename
        self.proxy.save_to_file(text, filename, name)

    def isBusy(self) -> bool:
        """
        @return: True if an utterance is currently being spoken, false if not
        @rtype: bool.
        """
        return self.proxy.isBusy()

    def getProperty(self, name: str) -> object:
        """
        Gets the current value of a property. Valid names and values include:

        voices: List of L{voice.Voice} objects supported by the driver
        voice: String ID of the current voice
        rate: Integer speech rate in words per minute
        volume: Floating point volume of speech in the range [0.0, 1.0]

        Numeric values outside the valid range supported by the driver are
        clipped.

        @param name: Name of the property to fetch
        @type name: str
        @return: Value associated with the property
        @rtype: object
        @raise KeyError: When the property name is unknown
        """
        assert name
        return self.proxy.getProperty(name)

    def setProperty(self, name: str, value: str | float) -> None:
        """
        Adds a property value to set to the event queue. Valid names and values
        include:

        voice: String ID of the voice
        rate: Integer speech rate in words per minute
        volume: Floating point volume of speech in the range [0.0, 1.0]

        Numeric values outside the valid range supported by the driver are
        clipped.

        @param name: Name of the property to fetch
        @type name: str
        @param: Value to set for the property
        @rtype: object
        @raise KeyError: When the property name is unknown
        """
        self.proxy.setProperty(name, value)

    def runAndWait(self) -> None:
        """
        Runs an event loop until all commands queued up until this method call
        complete. Blocks during the event loop and returns when the queue is
        cleared.

        @raise RuntimeError: When the loop is already running
        """
        if self._inLoop:
            msg = "run loop already started"
            raise RuntimeError(msg)
        self._inLoop = True
        self._driverLoop = True
        self.proxy.runAndWait()
        self._inLoop = False
        self.proxy.setBusy(False)

    def startLoop(self, useDriverLoop: bool = True) -> None:
        """
        Starts an event loop to process queued commands and callbacks.

        @param useDriverLoop: If True, uses the run loop provided by the driver
            (the default). If False, assumes the caller will enter its own
            run loop which will pump any events for the TTS engine properly.
        @type useDriverLoop: bool
        @raise RuntimeError: When the loop is already running
        """
        if self._inLoop:
            msg = "run loop already started"
            raise RuntimeError(msg)
        self._inLoop = True
        self._driverLoop = useDriverLoop
        self.proxy.startLoop(self._driverLoop)

    def endLoop(self) -> None:
        """
        Stops a running event loop.

        @raise RuntimeError: When the loop is not running
        """
        if not self._inLoop:
            msg = "run loop not started"
            raise RuntimeError(msg)
        self.proxy.endLoop(self._driverLoop)
        self._inLoop = False

    def iterate(self) -> None:
        """Must be called regularly when using an external event loop."""
        if not self._inLoop:
            msg = "run loop not started"
            raise RuntimeError(msg)
        if self._driverLoop:
            msg = "iterate not valid in driver run loop"
            raise RuntimeError(msg)
        self.proxy.iterate()
