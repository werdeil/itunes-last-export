
.. image:: https://raw.githubusercontent.com/werdeil/itunes-last-export/master/itunes_last_export/images/itunes_last_export.png
   :align: center
   :alt: itunes_last_export

The ``itunes_last_export`` tool allows you import playcounts from Last.fm to update your iTunes database. It also update in the same time the last played date.

Requirements
------------

This tool is working on Mac and may work also on Windows but wasn't tested on this OS.

Install
-------

It is planned to be able to install itunes_last_exporter through pip, issue #2 is opened to track this development

Install developing version
--------------------------

If you want to use an unofficial version of the ``itunes_last_export`` application, you need to work from a
clone of this ``git`` repository.

- clone from github ::

   $ git clone https://github.com/werdeil/itunes_last_export.git

- go in the cloned directory ::

   $ cd itunes_last_export

- start the application exactly in the same way as installed from pypi. All modifications performed
  in the cloned repository are taken into account when the application starts.

Run
---

Until the pip package is available, you can start the tool by cloing the repository and then in the cloned directory::

	$ PYTHONPATH=. bin/itunes_last_export

The graphical interface shall start, you can then use it.

Comments
--------

Feel free to give me any feedback on this github page: http://github.com/werdeil/itunes-last-export/
