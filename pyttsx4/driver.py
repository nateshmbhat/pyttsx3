import sys
import traceback
import weakref
import importlib


class DriverProxy(object):
    '''
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
    '''

    def __init__(self, engine, driverName, debug):
        '''
        Constructor.

        @param engine: Reference to the engine that owns the driver
        @type engine: L{engine.Engine}
        @param driverName: Name of the driver module to use under drivers/ or
            None to select the default for the platform
        @type driverName: str
        @param debug: Debugging output enabled or not
        @type debug: bool
        '''
        if driverName is None:
            # pick default driver for common platforms
            if sys.platform == 'darwin':
                driverName = 'nsss'
            elif sys.platform == 'win32':
                driverName = 'sapi5'
            else:
                driverName = 'espeak'
        # import driver module
        name = 'pyttsx4.drivers.%s' % driverName
        self._module = importlib.import_module(name)
        # build driver instance
        self._driver = self._module.buildDriver(weakref.proxy(self))
        # initialize refs
        self._engine = engine
        self._queue = []
        self._busy = True
        self._name = None
        self._iterator = None
        self._debug = debug

    def __del__(self):
        try:
            self._driver.destroy()
        except (AttributeError, TypeError):
            pass

    def _push(self, mtd, args, name=None):
        '''
        Adds a command to the queue.

        @param mtd: Method to invoke to process the command
        @type mtd: method
        @param args: Arguments to apply when invoking the method
        @type args: tuple
        @param name: Name associated with the command
        @type name: str
        '''
        self._queue.append((mtd, args, name))
        self._pump()

    def _pump(self):
        '''
        Attempts to process the next command in the queue if one exists and the
        driver is not currently busy.
        '''
        while (not self._busy) and len(self._queue):
            cmd = self._queue.pop(0)
            self._name = cmd[2]
            try:
                cmd[0](*cmd[1])
            except Exception as e:
                self.notify('error', exception=e)
                print('ERROR:pyttsx4-driver: _pump ',e)
                if self._debug:
                    traceback.print_exc()

    def notify(self, topic, **kwargs):
        '''
        Sends a notification to the engine from the driver.

        @param topic: Notification topic
        @type topic: str
        @param kwargs: Arbitrary keyword arguments
        @type kwargs: dict
        '''
        kwargs['name'] = self._name
        self._engine._notify(topic, **kwargs)

    def setBusy(self, busy):
        '''
        Called by the driver to indicate it is busy.

        @param busy: True when busy, false when idle
        @type busy: bool
        '''
        self._busy = busy
        if not self._busy:
            self._pump()

    def isBusy(self):
        '''
        @return: True if the driver is busy, false if not
        @rtype: bool
        '''
        return self._busy

    def say(self, text, name):
        '''
        Called by the engine to push a say command onto the queue.

        @param text: Text to speak
        @type text: unicode
        @param name: Name to associate with the utterance
        @type name: str
        '''
        self._push(self._driver.say, (text,), name)

    def stop(self):
        '''
        Called by the engine to stop the current utterance and clear the queue
        of commands.
        '''
        # clear queue up to first end loop command
        while(True):
            try:
                mtd, args, name = self._queue[0]
            except IndexError:
                break
            if(mtd == self._engine.endLoop):
                break
            self._queue.pop(0)
        self._driver.stop()

    def save_to_file(self, text, filename, name):
        '''
        Called by the engine to push a say command onto the queue.

        @param text: Text to speak
        @type text: unicode
        @param name: Name to associate with the utterance
        @type name: str
        '''
        self._push(self._driver.save_to_file, (text, filename), name)

    def getProperty(self, name):
        '''
        Called by the engine to get a driver property value.

        @param name: Name of the property
        @type name: str
        @return: Property value
        @rtype: object
        '''
        return self._driver.getProperty(name)

    def setProperty(self, name, value):
        '''
        Called by the engine to set a driver property value.

        @param name: Name of the property
        @type name: str
        @param value: Property value
        @type value: object
        '''
        self._push(self._driver.setProperty, (name, value))

    def runAndWait(self):
        '''
        Called by the engine to start an event loop, process all commands in
        the queue at the start of the loop, and then exit the loop.
        '''
        # actually there are no setBusy(True) in the old code and it works.
        # the error ocurrs when i added an sapi save_to_memory function.
        # after that, when the result is saved to memory, the busy is not set to True, so next runAndWait will
        # DEAD wait.
        # I don't know why it don't work for memory.
        # but here add setBusy(True) seem ok for the issue.
        # here first setBusy(True), and push the endLoop event, and setBusy(False) in startLoop，
        self.setBusy(True)
        self._push(self._engine.endLoop, tuple())
        self._driver.startLoop()

    def startLoop(self, useDriverLoop):
        '''
        Called by the engine to start an event loop.
        '''
        if useDriverLoop:
            self._driver.startLoop()
        else:
            self._iterator = self._driver.iterate()

    def endLoop(self, useDriverLoop):
        '''
        Called by the engine to stop an event loop.
        '''
        self._queue = []
        self._driver.stop()
        if useDriverLoop:
            self._driver.endLoop()
        else:
            self._iterator = None
        self.setBusy(True)

    def iterate(self):
        '''
        Called by the engine to iterate driver commands and notifications from
        within an external event loop.
        '''
        try:
            next(self._iterator)
        except StopIteration:
            pass
