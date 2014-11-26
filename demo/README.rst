####
Demo
####

Here is sample code to illustrate `pydocusign` usage.

To run the demo code, you need a development environment. See
:doc:`/contributing`.


****************
Embedded signing
****************

.. literalinclude:: ../demo/embeddedsigning.py
   :language: python

You can run this code with:

.. code:: sh

   python demo/embeddedsigning.py

.. note::

   The demo can use the same environment variables as tests. See
   :doc:`/contributing`. If you do not set environment variables, you will be
   prompted for some configuration.


********************************
Creating envelope using template
********************************

.. literalinclude:: ../demo/templatesigning.py
   :language: python

You can run this code with:

.. code:: sh

   python demo/templatesigning.py

.. note::

   The demo can use the same environment variables as tests. See
   :doc:`/contributing`. If you do not set environment variables, you will be
   prompted for some configuration.
