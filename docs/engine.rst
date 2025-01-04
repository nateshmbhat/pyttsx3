.. module:: pyttsx3
   :synopsis: The root pyttsx3 package defining the engine factory function

Using pyttsx3
-------------

An application invokes the :func:`pyttsx3.init` factory function to get a reference to a :class:`pyttsx3.Engine` instance. During construction, the engine initializes a :class:`pyttsx3.driver.DriverProxy` object responsible for loading a speech engine driver implementation from the :mod:`pyttsx3.drivers` module. After construction, an application uses the engine object to register and unregister event callbacks; produce and stop speech; get and set speech engine properties; and start and stop event loops.

The Engine factory
~~~~~~~~~~~~~~~~~~

.. function:: init([driverName : string, debug : bool]) -> pyttsx3.Engine

   Gets a reference to an engine instance that will use the given driver. If the requested driver is already in use by another engine instance, that engine is returned. Otherwise, a new engine is created.

   :param driverName: Name of the :mod:`pyttsx3.drivers` module to load and use. Defaults to the best available driver for the platform, currently:

      * `avspeech` - AVSynthesizer on macOS
      * `espeak` - eSpeak on all platforms
      * `nsss` - NSSpeechSynthesizer on macOS (Deprecated by Apple)
      * `sapi5` - SAPI5 on Windows

   :param debug: Enable debug output or not.
   :raises ImportError: When the requested driver is not found
   :raises RuntimeError: When the driver fails to initialize

The Engine interface
~~~~~~~~~~~~~~~~~~~~

.. module:: pyttsx3.engine
   :synopsis: The module containing the engine implementation

.. class:: Engine

   Provides application access to text-to-speech synthesis.

   .. method:: connect(topic : string, cb : callable) -> dict

      Registers a callback for notifications on the given topic.

      :param topic: Name of the event to subscribe to.
      :param cb: Function to invoke when the event fires.
      :return: A token that the caller can use to unsubscribe the callback later.

      The following are the valid topics and their callback signatures.

      .. describe:: started-utterance

         Fired when the engine begins speaking an utterance. The associated callback must have the following signature.

         .. function:: onStartUtterance(name : string) -> None

            :param name: Name associated with the utterance.

      .. describe:: started-word

         Fired when the engine begins speaking a word. The associated callback must have the following signature.

         .. function:: onStartWord(name : string, location : integer, length : integer)

            :param name: Name associated with the utterance.

      .. describe:: finished-utterance

         Fired when the engine finishes speaking an utterance. The associated callback must have the following signature.

         .. function:: onFinishUtterance(name : string, completed : bool) -> None

            :param name: Name associated with the utterance.
            :param completed: True if the utterance was output in its entirety or not.

      .. describe:: error

         Fired when the engine encounters an error. The associated callback must have the following signature.

         .. function:: onError(name : string, exception : Exception) -> None

            :param name: Name associated with the utterance that caused the error.
            :param exception: Exception that was raised.

   .. method:: disconnect(token : dict)

      Unregisters a notification callback.

      :param token: Token returned by :meth:`connect` associated with the callback to be disconnected.

   .. method:: endLoop() -> None

      Ends a running event loop. If :meth:`startLoop` was called with `useDriverLoop` set to True, this method stops processing of engine commands and immediately exits the event loop. If it was called with False, this method stops processing of engine commands, but it is up to the caller to end the external event loop it started.

      :raises RuntimeError: When the loop is not running

   .. method:: getProperty(name : string) -> object

      Gets the current value of an engine property.

      :param name: Name of the property to query.
      :return: Value of the property at the time of this invocation.

      The following property names are valid for all drivers.

      .. describe:: rate

         Integer speech rate in words per minute. Defaults to 200 word per minute.

      .. describe:: voice

         String identifier of the active voice.

      .. describe:: voices

         List of :class:`pyttsx3.voice.Voice` descriptor objects.

      .. describe:: volume

         Floating point volume in the range of 0.0 to 1.0 inclusive. Defaults to 1.0.

   .. method:: isBusy() -> bool

      Gets if the engine is currently busy speaking an utterance or not.

      :return: True if speaking, false if not.

   .. method:: runAndWait() -> None

      Blocks while processing all currently queued commands. Invokes callbacks for engine notifications appropriately. Returns when all commands queued before this call are emptied from the queue.

   .. method:: say(text : unicode, name : string) -> None

      Queues a command to speak an utterance. The speech is output according to the properties set before this command in the queue.

      :param text: Text to speak.
      :param name: Name to associate with the utterance. Included in notifications about this utterance.

   .. method:: setProperty(name, value) -> None

      Queues a command to set an engine property. The new property value affects all utterances queued after this command.

      :param name: Name of the property to change.
      :param value: Value to set.

      The following property names are valid for all drivers.

      .. describe:: rate

         Integer speech rate in words per minute.

      .. describe:: voice

         String identifier of the active voice.

      .. describe:: volume

         Floating point volume in the range of 0.0 to 1.0 inclusive.

   .. method:: startLoop([useDriverLoop : bool]) -> None

      Starts running an event loop during which queued commands are processed and notifications are fired.

      :param useDriverLoop: True to use the loop provided by the selected driver. False to indicate the caller will enter its own loop after invoking this method. The caller's loop must pump events for the driver in use so that pyttsx3 notifications are delivered properly (e.g., SAPI5 requires a COM message pump). Defaults to True.

   .. method:: stop() -> None

      Stops the current utterance and clears the command queue.

The Voice metadata
~~~~~~~~~~~~~~~~~~

.. module:: pyttsx3.voice
   :synopsis: The module containing the voice structure implementation

.. class:: Voice

   Contains information about a speech synthesizer voice.

   .. attribute:: age

      Integer age of the voice in years. Defaults to :const:`None` if unknown.

   .. attribute:: gender

      String gender of the voice: `male`, `female`, or `neutral`. Defaults to :const:`None` if unknown.

   .. attribute:: id

      String identifier of the voice. Used to set the active voice via :meth:`pyttsx3.engine.Engine.setPropertyValue`. This attribute is always defined.

   .. attribute:: languages

      List of string languages supported by this voice. Defaults to an empty list of unknown.

   .. attribute:: name

      Human readable name of the voice. Defaults to :const:`None` if unknown.

Examples
~~~~~~~~

Speaking text
#############

.. sourcecode:: python

   import pyttsx3
   engine = pyttsx3.init()
   engine.say('Sally sells seashells by the seashore.')
   engine.say('The quick brown fox jumped over the lazy dog.')
   engine.runAndWait()

Saving voice to a file
######################

.. sourcecode:: python

   import pyttsx3
   engine = pyttsx3.init()
   engine.save_to_file('Hello World' , 'test.mp3')
   engine.runAndWait()

Listening for events
####################

.. sourcecode:: python

    import pyttsx3
    def onStart(name):
        print('starting', name)
    def onWord(name, location, length):
        print('word', name, location, length)
    def onEnd(name, completed):
        print('finishing', name, completed)
    engine = pyttsx3.init()
    engine.connect('started-utterance', onStart)
    engine.connect('started-word', onWord)
    engine.connect('finished-utterance', onEnd)
    engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
    engine.runAndWait()

Interrupting an utterance
#########################

.. sourcecode:: python

    import pyttsx3
    def onWord(name, location, length):
        print('word', name, location, length)
        if location > 10:
            engine.stop()
    engine = pyttsx3.init()
    engine.connect('started-word', onWord)
    engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
    engine.runAndWait()

Changing voices
###############

.. sourcecode:: python

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        engine.setProperty('voice', voice.id)
        engine.say('The quick brown fox jumped over the lazy dog.')
    engine.runAndWait()

Changing speech rate
####################

.. sourcecode:: python

    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate+50)
    engine.say('The quick brown fox jumped over the lazy dog.')
    engine.runAndWait()

Changing volume
###############

.. sourcecode:: python

    engine = pyttsx3.init()
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume-0.25)
    engine.say('The quick brown fox jumped over the lazy dog.')
    engine.runAndWait()

Running a driver event loop
###########################

.. sourcecode:: python

    engine = pyttsx3.init()
    def onStart(name):
        print('starting', name)
    def onWord(name, location, length):
        print('word', name, location, length)
    def onEnd(name, completed):
        print('finishing', name, completed)
        if name == 'fox':
            engine.say('What a lazy dog!', 'dog')
        elif name == 'dog':
            engine.endLoop()
    engine = pyttsx3.init()
    engine.connect('started-utterance', onStart)
    engine.connect('started-word', onWord)
    engine.connect('finished-utterance', onEnd)
    engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
    engine.startLoop()

Using an external event loop
############################

.. sourcecode:: python

    engine = pyttsx3.init()
    engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
    engine.startLoop(False)
    # engine.iterate() must be called inside externalLoop()
    externalLoop()
    engine.endLoop()
