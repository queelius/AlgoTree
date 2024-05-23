
Python package: ``treekit``
===============================

``treekit`` is a Python toolkit for creating, managing, and visualizing tree structures derived from JSON and dictionary data.

Installation
------------

Clone this repository and run:

.. code-block:: bash

   pip install .

Usage
-----

We have a JSON file that represents a tree structure:

.. code-block:: json

   {
       "author": "John Doe",
       "version": "1.0"
       "mapping": {
           "node1": {
               // no parent specified, will connect to the root node
               "data": "Some data for node1"
           },
           "node2": {
               "parent": "node1",
               "data": "Some data for node2",
               "more_data": "More data"
           },
           "node3": {
               "parent": "node1",
               "data": "Some data for node3"
           }
       }
   }

To convert this JSON to a visual tree structure:

.. code-block:: bash

   ./bin/jsontree-view.py tree.json
   # __root__
   # └── node1
   #     ├── node2
   #     └── node3

Here is another example:

.. code-block:: bash

   ./jsontree-view.py \
       --node-name "lambda n: f'{n.name}: {n.payload}'" tree.json 

   # __root__: { "author": "John Doe", "version": "1.0" }
   # └── node1: { "data": "Some data for node1" }
   # ├── node2: { "data": "Some data for node2", "more_data": "More data" }
   # └── node3: { "data": "Some data for node3" }

For more options, you can use the help command:

.. code-block:: bash

   ./jsontree-view.py --help

``FlatTree`` Class
----------------------

``FlatTree`` is a Python class that can be used to create tree structures from
flat dictionary (or JSON) data. It provides a robust API for working with
trees, including methods for manipulating and visualizing them.

See the `FlatTree tutorial <FLATTREE.md>`_ for more information.

``TreeNode`` Class
----------------------

``TreeNode`` is a Python class that can be used to create tree structures from
highly nested dictionary (or JSON) data. 

See the `TreeNode expression tree tutorial <TREENODE.md>`_ for more information.
Otherwise, the interface is similar to ``FlatTree``.

Development
-----------

To set up a development environment:


#. Clone the repository.
#. Install the dependencies:

.. code-block:: bash

   pip install -r requirements.txt

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request.
