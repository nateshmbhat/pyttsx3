Installing pyttsx3
-----------------

Tested versions
~~~~~~~~~~~~~~~

Version |version| of pyttsx3 includes drivers for the following text-to-speech synthesizers. Only operating systems on which a driver is tested and known to work are listed. The drivers may work on other systems.

* SAPI5 on Windows XP, Windows Vista, and Windows 7
* NSSpeechSynthesizer on Mac OS X 10.5 (Leopard), 10.6 (Snow Leopard), 10.7 (Lion), and 10.8 (Mountain Lion).
* `espeak`_ on 32-bit Ubuntu Desktop Edition 8.10 (Intrepid), 9.04 (Jaunty), 9.10 (Karmic), and 12.04 (Precise).

The :func:`pyttsx3.init` documentation explains how to select a specific synthesizer by name as well as the default for each platform.

Using pip to install system-wide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have pip installed, you can use it to install pyttsx3 in the system site-packages folder.

On Windows
##########

First install the `pywin32-extensions <http://sourceforge.net/projects/pywin32/files/pywin32/>`_ package using its Windows installer. Then use pip to install pyttsx3.

.. code-block:: bash

   $ pip install pyttsx3

On OSX or Linux
###############

.. code-block:: bash

   $ sudo pip install pyttsx3

Using pip to install in a virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have virtualenv_ installed with pip_, you can use pip to install a copy of pyttsx3 in the virtual environment folder.

On Windows
##########

You'll need to install the `pywin32-extensions <http://sourceforge.net/projects/pywin32/files/pywin32/>`_ package system-wide using its Windows installer. Then you'll need to give your virtualenv access to the system site-packages in order to install pyttsx3.

.. code-block:: bash

   $ virtualenv --system-site-packages myproj
   New python executable in myproj/bin/python
   Installing setuptools............done.
   Installing pip...............done.
   $ myproj\Scripts\activate
   (myproj)$ pip install pyttsx3

On OSX
######

Unless you wish to compile your own version of pyobjc (a lengthy process), you will need to give your virtualenv access to the system site-packages folder.

.. code-block:: bash

   $ virtualenv --system-site-packages myproj
   New python executable in myproj/bin/python
   Installing setuptools............done.
   Installing pip...............done.
   $ . myproj/bin/activate
   (myproj)$ pip install pyttsx3
   ...
   Successfully installed pyttsx3
   Cleaning up...

On Linux
########

pyttsx3 requires no Python dependencies on Linux. You can cut-off the pyttsx3 virtualenv from the system site-packages.

code-block:: bash

   $ virtualenv --no-site-packages myproj
   New python executable in myproj/bin/python
   Installing setuptools............done.
   Installing pip...............done.
   $ . myproj/bin/activate
   (myproj)$ pip install pyttsx3
   ...
   Successfully installed pyttsx3
   Cleaning up...


.. _espeak: http://espeak.sourceforge.net/
.. _virtualenv: https://pypi.python.org/pypi/virtualenv/1.10.1
.. _pip: https://pypi.python.org/pypi/pip
