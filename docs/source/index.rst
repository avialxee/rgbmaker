**************************************
            RGBMaker
**************************************

Getting started
===============

A python package which communicates to different astronomical services and fetches fits and numerical data.
Use the tool here : `RGBMaker <https://radathomeindia.org/rgbmaker/>`_

   
.. code-block:: bash

   $ pip install rgbmaker
    

.. jupyter-execute::

   from rgbmaker.fetch import query
   query(name='Avi', position='speca', radius=0.12, kind='plot', px=150)
    


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   rgbmaker
   examples


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
