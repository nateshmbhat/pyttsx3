import importlib
import traceback
import weakref
import time


class DriverProxy(object):
    """
    Proxy to a driver implementation.

    @ivar _module: Module containing the driver implementation
    @type _module: module
    @ivar _engine: Reference to the engine that owns the driver
    @type _engine: L{engine.Engine}
    @ivar _queue: Queue of commands outstanding for the driver
    @type _queue: list
    @ivar _busy: True when the driver is busy processing a command, False when
        not
    @type _busy: bool
    @ivar _name: Name associated with the current utterance
    @type _name: str
    @ivar _debug: Debugging output enabled or not
    @type _debug: bool
    @ivar _iterator: Driver iterator to invoke when in an external run loop
    @type _iterator: iterator
    """

    def __init__(self, engine, driverName: str, debug: bool):
        """
        Constructor.

        @param engine: Reference to the engine that owns the driver
        @type engine: L{engine.Engine}
        @param driverName: Name of the driver module to use under drivers/
        @type driverName: str
        @param debug: Debugging output enabled or not
        @type debug: bool
        """
        assert driverName
        # import driver module
        self._module = importlib.import_module(f"pyttsx3.drivers.{driverName}")
        # build driver instance
        self._driver = self._module.buildDriver(weakref.proxy(self))
        # initialize refs
        self._engine = engine
        self._queue = []
        self._busy = True
        self._name = None
        self._iterator = None
        self._debug = debug
        self._current_text = ""

    def __del__(self):
        try:
            self._driver.destroy()
        except (AttributeError, TypeError):
            pass

    def _push(self, mtd, args, name=None):
        """
        Adds a command to the queue.

        @param mtd: Method to invoke to process the command
        @type mtd: method
        @param args: Arguments to apply when invoking the method
        @type args: tuple
        @param name: Name associated with the command
        @type name: str
        """
        self._queue.append((mtd, args, name))
        self._pump()

    def _pump(self):
        """
        Attempts to process the next command in the queue if one exists and the
        driver is not currently busy.
        """
        while (not self._busy) and len(self._queue):
            cmd = self._queue.pop(0)
            self._name = cmd[2]
            try:
                cmd[0](*cmd[1])
            except Exception as e:
                self.notify("error", exception=e)
                if self._debug:
                    traceback.print_exc()

    def notify(self, topic, **kwargs):
        """
        Sends a notification to the engine from the driver.

        @param topic: Notification topic
        @type topic: str
        @param kwargs: Arbitrary keyword arguments
        @type kwargs: dict
        """
        if "name" not in kwargs or kwargs["name"] is None:  # Avoid overwriting
            kwargs["name"] = self._name
        self._engine._notify(topic, **kwargs)

    def setBusy(self, busy):
        """
        Called by the driver to indicate it is busy.

        @param busy: True when busy, false when idle
        @type busy: bool
        """
        if self._busy != busy:
            print(f"[DEBUG] Transitioning to {'busy' if busy else 'idle'} state.")
        self._busy = busy
        if not busy:
            self._pump()

    def isBusy(self):
        """
        @return: True if the driver is busy, False if not
        @rtype: bool
        """
        return self._busy

    def say(self, text, name):
        """
        Called by the engine to push a say command onto the queue.

        @param text: Text to speak
        @type text: unicode
        @param name: Name to associate with the utterance
        @type name: str
        """
        self._current_text = text
        self._push(self._driver.say, (text,), name)

    def stop(self):
        """
        Called by the engine to stop the current utterance and clear the queue
        of commands.
        """
        # clear queue up to first end loop command
        while True:
            try:
                mtd, args, name = self._queue[0]
            except IndexError:
                break
            if mtd == self._engine.endLoop:
                break
            self._queue.pop(0)
        self._driver.stop()

    def save_to_file(self, text, filename, name):
        """
        Called by the engine to push a say command onto the queue.

        @param text: Text to speak
        @type text: unicode
        @param name: Name to associate with the utterance
        @type name: str
        """
        self._push(self._driver.save_to_file, (text, filename), name)

    def getProperty(self, name):
        """
        Called by the engine to get a driver property value.

        @param name: Name of the property
        @type name: str
        @return: Property value
        @rtype: object
        """
        return self._driver.getProperty(name)

    def setProperty(self, name, value):
        """
        Called by the engine to set a driver property value.

        @param name: Name of the property
        @type name: str
        @param value: Property value
        @type value: object
        """
        self._push(self._driver.setProperty, (name, value))

    def runAndWait(self, timeout=0.01):
        """
        Runs an event loop until the queue is empty or the timeout is reached.
        """
        # First, check if the loop is already running
        if self._driver._looping:
            print("[DEBUG] Loop already active; waiting for completion.")
            start_time = time.time()
            while self._driver._looping and (time.time() - start_time < timeout):
                time.sleep(0.1)
            if self._driver._looping:
                print("[WARNING] Forcing loop exit due to timeout.")
                self._driver.endLoop()
                self.setBusy(False)

        # Push endLoop to the queue to complete the sequence
        self._push(self._engine.endLoop, tuple())

        # Start the loop if not already running
        if not self._driver._looping:
            self._driver.startLoop()

        # Track the start time for timeout handling
        start_time = time.time()

        # Main wait loop to ensure commands are fully processed
        while (
            self._driver._queue or self._driver._text_to_say or self._driver._speaking
        ):
            if time.time() - start_time > timeout:
                print("[WARNING] runAndWait timeout reached.")
                break
            time.sleep(0.1)  # Allow time for the loop to process items in the queue

        print("[DEBUG] runAndWait completed.")

    def startLoop(self, useDriverLoop):
        """
        Called by the engine to start an event loop.
        """
        if useDriverLoop:
            self._driver.startLoop()
        else:
            self._iterator = self._driver.iterate() or iter([])

    def endLoop(self, useDriverLoop):
        """
        Called by the engine to stop an event loop.
        """
        print("DriverProxy.endLoop called; useDriverLoop:", useDriverLoop)
        self._queue = []
        self._driver.stop()
        if useDriverLoop:
            print("DriverProxy.endLoop calling driver.endLoop")
            self._driver.endLoop()
        else:
            self._iterator = None
        # Set driver as not busy after loop finishes
        self.setBusy(False)

    def iterate(self):
        """
        Called by the engine to iterate driver commands and notifications from
        within an external event loop.
        """
        try:
            next(self._iterator)
        except StopIteration:
            pass
