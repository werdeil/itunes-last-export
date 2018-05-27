
.. image:: https://raw.githubusercontent.com/werdeil/itunes-last-export/master/itunes_last_export/images/itunes_last_export.png
   :align: center
   :alt: itunes_last_export

The ``itunes-last-export`` tool allows you import playcounts from Last.fm to update your iTunes database. It also update in the same time the last played date.

Requirements
------------

This tool is working on Mac and may work also on Windows but wasn't tested on this OS.

Install
-------

Install ``itunes-last-export`` from the `pypi repository <https://pypi.org/project/itunes-last-export/>`_::

    $ sudo pip3 install itunes-last-export

Run
---

Start the application using the command::

    $ itunes-last-export

The graphical interface shall start, you can then use it.

For information all the cache data is sotred in the .config/itunes_last_export folder of the user.

Install developing version
--------------------------

If you want to use an unofficial version of the ``itunes-last-export`` application, you need to work from a
clone of this ``git`` repository.

- clone from github ::

   $ git clone https://github.com/werdeil/itunes-last-export.git

- go in the cloned directory ::

   $ cd itunes-last-export

- install ``itunes-last-export`` in editable mode ::

   $ pip3 install -e . --user

- start the application exactly in the same way as installed from pypi. All modifications performed
  in the cloned repository are taken into account when the application starts.

Comments
--------

Feel free to give me any feedback on this github page: http://github.com/werdeil/itunes-last-export/
