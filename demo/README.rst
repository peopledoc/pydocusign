####
Demo
####

Here is sample code to illustrate `pydocusign` usage.

To run the demo code, you need a development environment. See
:doc:`/contributing`.

.. note::

   The demo can use the same environment variables as tests. See
   :doc:`/contributing`. If you do not set environment variables, you will be
   prompted for some configuration.


****************
Embedded signing
****************

.. literalinclude:: ../demo/embeddedsigning.py
   :language: python

You can run this code with:

.. code:: sh

   python demo/embeddedsigning.py


********************************
Creating envelope using template
********************************

.. literalinclude:: ../demo/templates.py
   :language: python

You can run this code with:

.. code:: sh

   python demo/templates.py


*****************
Managing accounts
*****************

.. literalinclude:: ../demo/accounts.py
   :language: python

You can run this code with:

.. code:: sh

   python demo/accounts.py
