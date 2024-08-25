FlatForest Notebook
===================

.. contents:: Table of Contents
    :backlinks: none

Introduction
------------

In this notebook, we explore the ``FlatForest`` data structure, which is
a forest structure with a flat (non-nested) data structure. It is a
``dict`` with special methods to access the root nodes and other
tree-like operations.

The main implementation detail is the proxy class ``FlatForestNode``,
which allows us to access the ``dict`` with a node-centric abstraction.
This allows us to implement tree-like operations in a flat data
structure. As a proxy, it also modifies the ``dict`` in place, so it is
a mutable data structure.

Creating a ``FlatForest``
-------------------------

Let’s load the required libraries and create a ``FlatForest`` data
structure using the node interface.

.. code:: ipython3

    from AlgoTree.flat_forest_node import FlatForestNode
    from AlgoTree.flat_forest import FlatForest
    from AlgoTree.tree_converter import TreeConverter
    from IPython.display import display, Markdown
    from AlgoTree.pretty_tree import pretty_tree
    import json
    #from AlgoTree.treenode import TreeNode
    from copy import deepcopy
    
    
    def monotext(txt):
        display(Markdown(f"<pre>{txt}</pre>"))
    
    data = {
        "1": { "data": 1, "parent": None},
        "2": { "parent": "1", "data": 2},
        "3": { "parent": "1", "data": 3},
        "4": { "parent": "3", "data": 4},
        "5": { "parent": "3", "data": 5},
        "A": { "data": "Data for A", "parent": None },
        "B": { "parent": "A", "data": "Data for B" },
        "C": { "parent": "A", "data": "Data for C" },
        "D": { "parent": "C", "data": "Data for D" },
        "E": { "parent": "C", "data": "Data for E" },
        "F": { "parent": "E", "data": "Data for F" },
        "G": { "parent": "E", "data": "Data for G" },
        "H": { "parent": "B", "data": "Data for H" },
        "I": { "parent": "A", "data": "Data for I" },
        "J": { "parent": "I", "data": "Data for J" },
        "K": { "parent": "G", "data": "Data for K" },
        "L": { "parent": "G", "data": "Data for L" },
        "M": { "parent": "C", "data": "Data for M" },
    }
    
    forest = FlatForest()
    nodes = []
    for key, value in data.items():
        par_key = value.pop("parent", None)
        nodes.append(FlatForestNode(name=key, parent=par_key, forest=forest, data=value["data"]))
    
    for node in nodes:
        try:
            print(node.name, node.payload, node.parent.name if node.parent is not None else None)
        except ValueError as e:
            print(f"ValueError: {e}")
        except KeyError as e:
            print(f"KeyError: {e}")
        print()


Output
^^^^^^

.. parsed-literal::

    1 {'data': 1} None
    
    2 {'data': 2} 1
    
    3 {'data': 3} 1
    
    4 {'data': 4} 3
    
    5 {'data': 5} 3
    
    A {'data': 'Data for A'} None
    
    B {'data': 'Data for B'} A
    
    C {'data': 'Data for C'} A
    
    D {'data': 'Data for D'} C
    
    E {'data': 'Data for E'} C
    
    F {'data': 'Data for F'} E
    
    G {'data': 'Data for G'} E
    
    H {'data': 'Data for H'} B
    
    I {'data': 'Data for I'} A
    
    J {'data': 'Data for J'} I
    
    K {'data': 'Data for K'} G
    
    L {'data': 'Data for L'} G
    
    M {'data': 'Data for M'} C
    

Storing and Transmitting Trees
------------------------------

It’s easy to regenerate any JSON files that may have been used to
generate the ``FlatForest`` object. So, JSON is a good format for
storing and transmitting trees. And, of course, ``FlatForest`` *is* a
dictionary.

Note that when we load a dictionary, the tree is providing a *view* of it
in-place. So, if we modify the dictionary, we modify the tree, and vice versa.

Creating a `FlatForest` from a JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: ipython3

    # load a forest from data
    forest2 = FlatForest(deepcopy(data))
    # load a forest from a forest
    forest3 = FlatForest(forest)
    
    print(forest == forest2)
    
    print(json.dumps(dict(forest), indent=2, sort_keys=True) == json.dumps(dict(forest2), indent=2, sort_keys=True))
    print(json.dumps(dict(forest), indent=2, sort_keys=True) == json.dumps(dict(forest3), indent=2, sort_keys=True))
    print(json.dumps(dict(forest2), indent=2, sort_keys=True) == json.dumps(dict(forest3), indent=2, sort_keys=True))


.. parsed-literal::

    False
    False
    True
    False


.. code:: ipython3

    forest.logical_root_names()




.. parsed-literal::

    [None, None, '__DETACHED__']



.. code:: ipython3

    print(forest.detached)


.. parsed-literal::

    FlatForestNode(name=__DETACHED__, parent=None, payload={}, root=__DETACHED__, children=[])


.. code:: ipython3

    from copy import deepcopy
    new_forest = deepcopy(forest)
    new_forest.detach("1")




.. parsed-literal::

    FlatForestNode(name=1, parent=None, payload={'data': 1}, root=1, children=['2', '3'])



If we try to detach a node that was already detached, we get a
``KeyError``. Note that this can happen in two ways:

1. The node was detached and then we try to detach it again.
2. The node was detached and then we try to detach a child of it.

Any child of a detached node is also detached, so we can’t detach a
child of a detached node.

.. code:: ipython3

    try:
        new_forest.detach("2")
    except KeyError as e:
        print(f"KeyError: {e}")

.. code:: ipython3

    forest.as_tree()




.. parsed-literal::

    FlatForestNode(name=__ROOT__, parent=None, payload={}, root=__ROOT__, children=['1', 'A'])



.. code:: ipython3

    forest.preferred_root = "1"
    print(pretty_tree(forest.subtree()))
    forest.preferred_root = "A"
    print(pretty_tree(forest.subtree()))
    print(pretty_tree(forest.subtree("C")))


.. parsed-literal::

    1
    ├───── 2
    └───── 3
           ├───── 4
           └───── 5
    
    A
    ├───── B
    │      └───── H
    ├───── C
    │      ├───── D
    │      ├───── E
    │      │      ├───── F
    │      │      └───── G
    │      │             ├───── K
    │      │             └───── L
    │      └───── M
    └───── I
           └───── J
    
    C
    ├───── D
    ├───── E
    │      ├───── F
    │      └───── G
    │             ├───── K
    │             └───── L
    └───── M
    


For visualizing trees, we can use the ``PrettyTree`` class and the
``pretty_tree`` function. The ``PrettyTree`` class is a simple tree data
structure that can be used to visualize trees in pretty text format,
optionally with the ability to mark nodes for highlighting.

.. code:: ipython3

    monotext(pretty_tree(forest.subtree("A"), mark=["A", "G"], node_details=lambda node: node.payload['data']))



.. raw:: html

   <pre>A ◄ Data for A 🔵
   ├───── B ◄ Data for B
   │      └───── H ◄ Data for H
   ├───── C ◄ Data for C
   │      ├───── D ◄ Data for D
   │      ├───── E ◄ Data for E
   │      │      ├───── F ◄ Data for F
   │      │      └───── G ◄ Data for G 🟣
   │      │             ├───── K ◄ Data for K
   │      │             └───── L ◄ Data for L
   │      └───── M ◄ Data for M
   └───── I ◄ Data for I
          └───── J ◄ Data for J
   </pre>


.. code:: ipython3

    monotext(pretty_tree(forest.subtree("A"), mark=["H", "D"]))



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H 🟡
   ├───── C
   │      ├───── D ⭕
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   └───── I
          └───── J
   </pre>


.. code:: ipython3

    from pprint import pprint
    from AlgoTree import utils
    pprint(utils.node_stats(forest.subtree("C")))


.. parsed-literal::

    {'node_info': {'ancestors': [],
                   'children': ['D', 'E', 'M'],
                   'depth': 0,
                   'descendants': ['D', 'E', 'F', 'G', 'K', 'L', 'M'],
                   'is_internal': True,
                   'is_leaf': False,
                   'is_root': True,
                   'leaves_under': ['D', 'F', 'K', 'L', 'M'],
                   'name': 'C',
                   'parent': None,
                   'path': ['C'],
                   'payload': {'data': 'Data for C'},
                   'root_distance': 0,
                   'siblings': [],
                   'type': "<class 'AlgoTree.flat_forest_node.FlatForestNode'>"},
     'subtree_info': {'height': 3,
                      'leaves': ['D', 'F', 'K', 'L', 'M'],
                      'root': 'C',
                      'size': 8}}


The ``FlatForest`` class provides a **view** of a ``dict`` object as a
forest. We do not modify the ``dict`` passed into it (and you can create
a dict through the ``FlatForest`` API). Since it’s just a view of a
``dict`` we have all the normal operations on it that we would have on a
``dict`` object.

``FlatForest`` also implements the concept of a node, which is a view of
a particular node in our node-centric API. In order to do this, we
specify a preferred root node, which by default is the first root node
in the forest. This is the node that will be used as the root node in
the ``FlatForestNode`` API. If you want to change the root node, you can
do so by calling ``FlatForest.preferred_root`` with the name of the node
you want to be the preferred root.

We also provide as ``as_tree`` method that unifies any ``dict`` object
representing a flat forest structure into a flat forest structure with
just a single root node, where all the root nodes are children of this
root node. This is no longer a view, however, as we return a new
``dict`` object.

.. code:: ipython3

    print(forest["C"])
    C = forest.subtree("C")
    print(C)
    print(C["parent"])
    print(C.children)


.. parsed-literal::

    {'data': 'Data for C', 'parent': 'A'}
    FlatForestNode(name=C, parent=None, payload={'data': 'Data for C'}, root=C, children=['D', 'E', 'M'])
    A
    [FlatForestNode(name=D, parent=C, payload={'data': 'Data for D'}, root=C, children=[]), FlatForestNode(name=E, parent=C, payload={'data': 'Data for E'}, root=C, children=['F', 'G']), FlatForestNode(name=M, parent=C, payload={'data': 'Data for M'}, root=C, children=[])]


.. code:: ipython3

    N = forest.root.add_child(name="N", data="Data for N")
    print(N)
    forest.subtree("A").add_child(name="O", data="Data for O")
    monotext(pretty_tree(forest.root.node("A"), mark=["O"]))


.. parsed-literal::

    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N'}, root=A, children=[])



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   └───── O 🟡
   </pre>


If we try too add a non-unique node key to the tree, we will get a
``KeyError``.

.. code:: ipython3

    try:
        forest.subtree("A").add_child(name="B")
    except KeyError as e:
        print(e)


.. parsed-literal::

    'key already exists in the tree: B'


Let’s add some more nodes.

.. code:: ipython3

    P = N.add_child(name="P", data="Data for P")
    N.add_child(name="Q", data="Data for Q")
    P.add_child(name="R", data="Data for R").add_child(
        name="S", data="Data for S"
    )
    monotext(pretty_tree(forest.root, mark=["N", "P", "Q", "R", "S"]))
    
    print(forest.root.node("A"))
    print(forest.root.node("A").parent)



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N ⭕
   │      ├───── P 🟤
   │      │      └───── R 🔵
   │      │             └───── S 🟤
   │      └───── Q 🔘
   └───── O
   </pre>


.. parsed-literal::

    FlatForestNode(name=A, parent=None, payload={'data': 'Data for A'}, root=A, children=['B', 'C', 'I', 'N', 'O'])
    None


.. code:: ipython3

    f_nodes = utils.breadth_first_undirected(forest.node("F"), 2)
    print([n.name for n in f_nodes])



.. parsed-literal::

    ['F', 'E', 'G', 'C']


.. code:: ipython3

    
    monotext(pretty_tree(utils.subtree_rooted_at(forest.node("C"), 2), mark=["C"]))



.. raw:: html

   <pre>C ⭕
   ├───── D
   ├───── E
   │      ├───── F
   │      └───── G
   └───── M
   </pre>


.. code:: ipython3

    center_C = utils.subtree_centered_at(forest.node("C"), 2)
    monotext(pretty_tree(center_C, mark=["C"]))
    monotext(pretty_tree(forest.root, mark=["C"]))



.. raw:: html

   <pre>A
   ├───── B
   ├───── C ⭕
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      └───── M
   ├───── I
   ├───── N
   └───── O
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C ⭕
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


We also support conversions to and from any tree-like structure that
supports the node-centric API, including ``FlatForest`` and a simple
(but far more flexible) ``TreeNode`` class that we also provide for
illustrative purposes.

The function is called ``TreeConverter.copy_under`` which accepts a
``source`` and ``target`` object, and copies the ``source`` object under
the ``target`` object. The source is normally a node of some kind, and
the target is another node, and the result is the tree structure under
the source node is copied under the target node. The source node is not
modified in any way.

.. code:: ipython3

    from AlgoTree.treenode import TreeNode
    treeNodeMe = TreeNode(name="treenode", payload={"data": "Data for treenode"})
    treeNodeMe.add_child(name="child1", payload={"data": "Data for child1"})
    treeNodeMe.add_child(name="child2", payload={"data": "Data for child2"})
    tree1 = TreeConverter.copy_under(forest.subtree("C"), treeNodeMe.children[0])
    print(pretty_tree(tree1.root, mark=["child1"]))



.. parsed-literal::

    treenode
    ├───── child1 🟡
    │      └───── C
    │             ├───── D
    │             ├───── E
    │             │      ├───── F
    │             │      └───── G
    │             │             ├───── K
    │             │             └───── L
    │             └───── M
    └───── child2
    


.. code:: ipython3

    tree2 = TreeConverter.copy_under(tree1.root, forest.subtree("D"), node_name=lambda n: n.name + "_2")
    monotext(pretty_tree(tree2.forest.root))




.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      │      └───── treenode_2
   │      │             ├───── child1_2
   │      │             │      └───── C_2
   │      │             │             ├───── D_2
   │      │             │             ├───── E_2
   │      │             │             │      ├───── F_2
   │      │             │             │      └───── G_2
   │      │             │             │             ├───── K_2
   │      │             │             │             └───── L_2
   │      │             │             └───── M_2
   │      │             └───── child2_2
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


We can iterate over the items of the child and we can modify/delete its
data.

.. code:: ipython3

    for k, v in forest.subtree("N").items():
        print(k, "<--", v)
    
    N["new_data"] = "Some new data for G"
    print(N)
    
    del N["new_data"]
    N["other_new_data"] = "Some other data for G"
    print(N)


.. parsed-literal::

    data <-- Data for N
    parent <-- A
    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N', 'new_data': 'Some new data for G'}, root=A, children=['P', 'Q'])
    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N', 'other_new_data': 'Some other data for G'}, root=A, children=['P', 'Q'])


Let’s create a tree from a dictionary that refers to a non-existent
parent.

.. code:: ipython3

    try:
        non_existent_parent_tree = FlatForest(
            {
                "A": {
                    "parent": "non_existent_parent",
                    "data": "Data for A",
                }
            }
        )
        FlatForest.check_valid(non_existent_parent_tree)
    except KeyError as e:
        print(e)


.. parsed-literal::

    "Parent 'non_existent_parent' not in forest for node 'A'"


We see that the node is disconnected from the logical root, since it
refers to a non-existent parent.

.. code:: ipython3

    try:
        cycle_tree = FlatForest(
            {
                "x": {"parent": None, "data": "Data for x"},
                "A": {"parent": "C", "data": "Data for A"},
                "B": {"parent": "A", "data": "Data for B"},
                "C": {"parent": "B", "data": "Data for C"},
                "D": {"parent": "x", "data": "Data for D"},
            }
        )
    
        monotext(pretty_tree(cycle_tree.root))
        FlatForest.check_valid(cycle_tree)
    except ValueError as e:
        print(e)



.. raw:: html

   <pre>x
   └───── D
   </pre>


.. parsed-literal::

    Cycle detected: {'C', 'A', 'B'}


We see that the tree was in an invalid state. In particular, nodes 1, 2,
and 3 are from any root and in a cycle. We can fix this by breaking the
cycle and setting the parent of node 3 to, for instance, to ``x``.
However, we can also fix it by setting the parent to ``None``, so that
it is a seperate tree in the forest.

.. code:: ipython3

    cycle_tree["C"]["parent"] = None
    FlatForest.check_valid(cycle_tree)
    monotext(pretty_tree(cycle_tree.subtree("C"), mark=["C"]))
    print(cycle_tree.root_names)



.. raw:: html

   <pre>C ⭕
   └───── A
          └───── B
   </pre>


.. parsed-literal::

    ['x', 'C', None, None, '__DETACHED__']


Let’s look at the tree again, and see about creating a cycle.

We will make node 1 the parent of node 5, to create a cycle:

.. code:: ipython3

    try:
        new_tree = deepcopy(forest.root)
        new_tree.node("A")["parent"] = "E"
        FlatForest.check_valid(new_tree)
    except ValueError as e:
        print(e)


.. parsed-literal::

    Data is not a dictionary: data=FlatForestNode(name=A, parent=None, payload={'data': 'Data for A'}, root=A, children=['B', 'C', 'I', 'N', 'O'])


Notice that we use ``deepcopy`` to avoid modifying the original tree
with these invalid operations. We chose to do it this way so as to not
incur the overhead of reverting the tree to a valid state after an
invalid operation. This way, we can keep the tree in an invalid state
for as long as we want, and only revert it to a valid state when we want
to.

Each node is a key-value pair in the ``FlatForest``. We have the
``FlatForestNode`` so that we can have an API focused on the nodes and
not the underlying dictionary. However, we stiill permit access to the
underlying dictionary. When you modify the tree in this way, we still
maintain the integrity of the tree.

Since the ``FlatForest`` represents nodes as key-value pairs, and the
value may have a parent key, along with any other arbitrary data, each
value for a node must be a dictionary.

Below, we see that trying to add a ``test`` node with a non-dictionary
value generates an error.

.. code:: ipython3

    try:
        error_tree = deepcopy(forest)
        # this will raise a ValueError because the node with key `test` maps to
        # string instead of a dict.
        error_tree["test"] = "Some test data"
        FlatForest.check_valid(error_tree)
    except ValueError as e:
        print(e)


.. parsed-literal::

    Node 'test' does not have a payload dictionary: 'Some test data'


Let’s manipulate the tree a bit more using the ``dict`` API. We’re just
going to add a ``new_node`` with some data.

.. code:: ipython3

    forest["T"] = {
        "parent": "B",
        "data": "Data for T"
    }
    
    print(forest.node("T"))
    print(pretty_tree(forest.subtree("B"), mark=["T"]))



.. parsed-literal::

    FlatForestNode(name=T, parent=B, payload={'data': 'Data for T'}, root=A, children=[])
    B
    ├───── H
    └───── T 🔵
    


Logical roots are not a part of the underlying dictionary, so we can’t
access it through the ``dict`` API. It’s non-children data are also
immutable through the ``FlatForestNode`` API. Right now, we use
``FlatForest.DETACHED_KEY`` as a logical root for detached nodes.

.. code:: ipython3

    print(forest.detached)


.. parsed-literal::

    FlatForestNode(name=__DETACHED__, parent=None, payload={}, root=__DETACHED__, children=[])


We see that there are no detached nodes in the forest right now.

.. code:: ipython3

    try:
        forest.detached["data"] = "Some new data for root node"
    except TypeError as e:
        print(e)
    
    try:
        forest.detached["parent"] = None
    except TypeError as e:
        print(e)


.. parsed-literal::

    __DETACHED__ is an immutable logical root
    __DETACHED__ is an immutable logical root


We can *detach* nodes. Let’s first view the full tree, pre-detachment.

.. code:: ipython3

    monotext(pretty_tree(forest.root))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      └───── T
   ├───── C
   │      ├───── D
   │      │      └───── treenode_2
   │      │             ├───── child1_2
   │      │             │      └───── C_2
   │      │             │             ├───── D_2
   │      │             │             ├───── E_2
   │      │             │             │      ├───── F_2
   │      │             │             │      └───── G_2
   │      │             │             │             ├───── K_2
   │      │             │             │             └───── L_2
   │      │             │             └───── M_2
   │      │             └───── child2_2
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


.. code:: ipython3

    forest.node("D").detach()
    forest.detach("G")
    monotext(pretty_tree(forest.root))




.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      └───── T
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


Let’s view the detached tree.

.. code:: ipython3

    monotext(pretty_tree(forest.detached, mark=["B", "C"]))




.. raw:: html

   <pre>__DETACHED__
   ├───── D
   │      └───── treenode_2
   │             ├───── child1_2
   │             │      └───── C_2
   │             │             ├───── D_2
   │             │             ├───── E_2
   │             │             │      ├───── F_2
   │             │             │      └───── G_2
   │             │             │             ├───── K_2
   │             │             │             └───── L_2
   │             │             └───── M_2
   │             └───── child2_2
   └───── G
          ├───── K
          └───── L
   </pre>


We can purge detached nodes (and their descendants) from the tree with
the ``purge`` method. Let’s purge the detached nodes. Note that when we
do this, through the node-centric API, nothing will seem different
(unless we look at the tree rooted at the detached logical root).
However, if we look at the underlying dictionary, we will see that the
detached nodes are gone.

.. code:: ipython3

    forest.purge()
    print(json.dumps(forest, indent=2))


.. parsed-literal::

    {
      "1": {
        "data": 1,
        "parent": null
      },
      "2": {
        "data": 2,
        "parent": "1"
      },
      "3": {
        "data": 3,
        "parent": "1"
      },
      "4": {
        "data": 4,
        "parent": "3"
      },
      "5": {
        "data": 5,
        "parent": "3"
      },
      "A": {
        "data": "Data for A",
        "parent": null
      },
      "B": {
        "data": "Data for B",
        "parent": "A"
      },
      "C": {
        "data": "Data for C",
        "parent": "A"
      },
      "E": {
        "data": "Data for E",
        "parent": "C"
      },
      "F": {
        "data": "Data for F",
        "parent": "E"
      },
      "H": {
        "data": "Data for H",
        "parent": "B"
      },
      "I": {
        "data": "Data for I",
        "parent": "A"
      },
      "J": {
        "data": "Data for J",
        "parent": "I"
      },
      "M": {
        "data": "Data for M",
        "parent": "C"
      },
      "N": {
        "data": "Data for N",
        "parent": "A",
        "other_new_data": "Some other data for G"
      },
      "O": {
        "data": "Data for O",
        "parent": "A"
      },
      "P": {
        "data": "Data for P",
        "parent": "N"
      },
      "Q": {
        "data": "Data for Q",
        "parent": "N"
      },
      "R": {
        "data": "Data for R",
        "parent": "P"
      },
      "S": {
        "data": "Data for S",
        "parent": "R"
      },
      "T": {
        "parent": "B",
        "data": "Data for T"
      }
    }


We have a fairly complete API for manipulating the forest. Let’s explore
some additional methods. Let’s first create a node itrator to node A,
and then access or modify the payload data for node A. Since payload
data is mutable, and it must be a dictionary, we can access or modify it
using the dict API.

.. code:: ipython3

    forest.node("A").clear()
    forest.node("A")["new_data"] = "Some new data for A"
    forest.node("A")["other_new_data"] = "Some other data for A"
    print(forest["A"])


.. parsed-literal::

    {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}


This is fairly self-expalanatory.

Let’s add some more nodes without specifying a key name for them, since
often we don’t care about the key name and it’s only for bookkeeping
purposes.

.. code:: ipython3

    forest.root.add_child(whatever=3).add_child(
        name="U", whatever=4).add_child(whatever=5)




.. parsed-literal::

    FlatForestNode(name=779cc759-36a9-4dae-a1c9-e021d65aa1d4, parent=U, payload={'whatever': 5}, root=A, children=[])



.. code:: ipython3

    FlatForestNode(whatever=1000, parent=forest.root.children[0])
    FlatForestNode(name="V", whatever=2000, parent=forest.root.children[0].children[1])
    FlatForestNode(whatever=3000, more_data="yes", parent=forest.node("V"))
    FlatForestNode(name="W", parent=forest.root, whatever=200)




.. parsed-literal::

    FlatForestNode(name=W, parent=A, payload={'whatever': 200}, root=A, children=[])



.. code:: ipython3

    forest.node("V").parent = forest.node("W")
    monotext(pretty_tree(forest.root, mark=["U", "V", "W"], node_details=lambda n: n.payload))



.. raw:: html

   <pre>A ◄ {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}
   ├───── B ◄ {'data': 'Data for B'}
   │      ├───── H ◄ {'data': 'Data for H'}
   │      ├───── T ◄ {'data': 'Data for T'}
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978 ◄ {'whatever': 1000}
   ├───── C ◄ {'data': 'Data for C'}
   │      ├───── E ◄ {'data': 'Data for E'}
   │      │      └───── F ◄ {'data': 'Data for F'}
   │      └───── M ◄ {'data': 'Data for M'}
   ├───── I ◄ {'data': 'Data for I'}
   │      └───── J ◄ {'data': 'Data for J'}
   ├───── N ◄ {'data': 'Data for N', 'other_new_data': 'Some other data for G'}
   │      ├───── P ◄ {'data': 'Data for P'}
   │      │      └───── R ◄ {'data': 'Data for R'}
   │      │             └───── S ◄ {'data': 'Data for S'}
   │      └───── Q ◄ {'data': 'Data for Q'}
   ├───── O ◄ {'data': 'Data for O'}
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e ◄ {'whatever': 3}
   │      └───── U ◄ {'whatever': 4} 🔴
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4 ◄ {'whatever': 5}
   └───── W ◄ {'whatever': 200} ⚫
          └───── V ◄ {'whatever': 2000} 🔘
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8 ◄ {'whatever': 3000, 'more_data': 'yes'}
   </pre>


Let’s look at some tree conversions. We can convert between different
tree representations and data structures.

.. code:: ipython3

    new_tree = TreeConverter.convert(forest.root, TreeNode)
    monotext(pretty_tree(new_tree, node_details=lambda n: n.payload))



.. raw:: html

   <pre>A ◄ {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}
   ├───── B ◄ None
   │      ├───── H ◄ None
   │      ├───── T ◄ None
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978 ◄ None
   ├───── C ◄ None
   │      ├───── E ◄ None
   │      │      └───── F ◄ None
   │      └───── M ◄ None
   ├───── I ◄ None
   │      └───── J ◄ None
   ├───── N ◄ None
   │      ├───── P ◄ None
   │      │      └───── R ◄ None
   │      │             └───── S ◄ None
   │      └───── Q ◄ None
   ├───── O ◄ None
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e ◄ None
   │      └───── U ◄ None
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4 ◄ None
   └───── W ◄ None
          └───── V ◄ None
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8 ◄ None
   </pre>


We see that it’s a different type of tree, a ``TreeNode``, which is a
recursive data structure. It models the same tree data, but in a
different way. This one is also more flexible, so that it doesn’t
require unique names or the payload data to be a dictionary - it can be
any object or value. This simplicity comes at the cost of not being a
dictionary (or view of a dictionary), as FlatForest does.

We see that it has a very different structure. However, when we
pretty-print it using ``TreeViz``, we see that it’s the same tree.

.. code:: ipython3

    monotext(pretty_tree(forest.root))
    monotext(pretty_tree(new_tree))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


.. code:: ipython3

    result = TreeConverter.copy_under(new_tree, FlatForestNode(name="new_root"))
    monotext(pretty_tree(result))
    result2 = TreeConverter.copy_under(result, new_tree)
    monotext(pretty_tree(result2))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


The ``TreeNode`` is a bit more useful for operations that require
recursion, but any tree can support the sae operations. The ``TreeNode``
is a bit more specialized for this purpose, and the ``FlatTree`` is a
bit more specialized for more general storage and manipulation of data
that is tree-like, such as configuration data or log data. See
``TreeNode.md`` for more information on the ``TreeNode`` class.

.. code:: ipython3

    root = TreeNode(name="root", payload= {"value":0}, parent=None)
    A = TreeNode(name="A", payload={"value":1}, parent=root)
    print(root.children)



.. parsed-literal::

    [TreeNode(name=A, parent=root, root=root, payload={'value': 1}, len(children)=0)]


.. code:: ipython3

    root2 = TreeNode(name="root", payload=0)
    A2 = TreeNode(name="A", parent=root2, payload=1)
    B2 = TreeNode(name="B", parent=root2, payload=2)
    C2 = TreeNode(name="C", parent=root2, payload=3)
    D2 = TreeNode(name="D", parent=C2, payload=4)
    E2 = TreeNode(name="E", parent=C2, payload=5)
    F2 = TreeNode(name="F", parent=C2, payload="test")
    G2 = TreeNode(name="G", parent=C2, payload=7)
    H2 = TreeNode(name="H", parent=C2, payload=({1: 2}, [3, 4]))
    I2 = TreeNode(name="I", parent=F2, payload=9)
    monotext(pretty_tree(root2, node_details=lambda n: n.payload))



.. raw:: html

   <pre>root ◄ 0
   ├───── A ◄ 1
   ├───── B ◄ 2
   └───── C ◄ 3
          ├───── D ◄ 4
          ├───── E ◄ 5
          ├───── F ◄ test
          │      └───── I ◄ 9
          ├───── G ◄ 7
          └───── H ◄ ({1: 2}, [3, 4])
   </pre>


Algorithm Examples
------------------

Using utility algorithms with ``FlatTree`` and ``FlatTreeNode``:

Finding descendants of a node:

.. code:: ipython3

    from AlgoTree.utils import *
    from pprint import pprint
    pprint(descendants(C))


.. parsed-literal::

    [FlatForestNode(name=E, parent=C, payload={'data': 'Data for E'}, root=C, children=['F']),
     FlatForestNode(name=F, parent=E, payload={'data': 'Data for F'}, root=C, children=[]),
     FlatForestNode(name=M, parent=C, payload={'data': 'Data for M'}, root=C, children=[])]


Finding ancestors of a node:

.. code:: ipython3

    pprint(ancestors(I2))


.. parsed-literal::

    [TreeNode(name=F, parent=C, root=root, payload=test, len(children)=1),
     TreeNode(name=C, parent=root, root=root, payload=3, len(children)=5),
     TreeNode(name=root, root=root, payload=0, len(children)=3)]


Finding siblings of a node:

.. code:: ipython3

    pprint(siblings(E2))


.. parsed-literal::

    []


Finding leaves of a node:

.. code:: ipython3

    pprint(leaves(root2))


.. parsed-literal::

    [TreeNode(name=A, parent=root, root=root, payload=1, len(children)=0),
     TreeNode(name=B, parent=root, root=root, payload=2, len(children)=0),
     TreeNode(name=D, parent=C, root=root, payload=4, len(children)=0),
     TreeNode(name=E, parent=C, root=root, payload=5, len(children)=0),
     TreeNode(name=I, parent=F, root=root, payload=9, len(children)=0),
     TreeNode(name=G, parent=C, root=root, payload=7, len(children)=0),
     TreeNode(name=H, parent=C, root=root, payload=({1: 2}, [3, 4]), len(children)=0)]


Finding the height of a tree:

.. code:: ipython3

    pprint(height(root2))


.. parsed-literal::

    3


Finding the depth of a node:

.. code:: ipython3

    pprint(depth(F2))


.. parsed-literal::

    2


Breadth-first traversal:

.. code:: ipython3

    def print_node(node, level):
        print(f"Level {level}: {node.name}")
        return False
    
    breadth_first(root2, print_node)


.. parsed-literal::

    Level 0: root
    Level 1: A
    Level 1: B
    Level 1: C
    Level 2: D
    Level 2: E
    Level 2: F
    Level 2: G
    Level 2: H
    Level 3: I




.. parsed-literal::

    False



.. code:: ipython3

    print(json.dumps(utils.node_stats(forest.node("N")), indent=2))


.. parsed-literal::

    {
      "node_info": {
        "type": "<class 'AlgoTree.flat_forest_node.FlatForestNode'>",
        "name": "N",
        "payload": {
          "data": "Data for N",
          "other_new_data": "Some other data for G"
        },
        "children": [
          "P",
          "Q"
        ],
        "parent": "A",
        "depth": 1,
        "is_root": false,
        "is_leaf": false,
        "is_internal": true,
        "ancestors": [
          "A"
        ],
        "siblings": [
          "B",
          "C",
          "I",
          "O",
          "945ef525-fece-45f0-a499-b5449d28ef1e",
          "W"
        ],
        "descendants": [
          "P",
          "R",
          "S",
          "Q"
        ],
        "path": [
          "A",
          "N"
        ],
        "root_distance": 1,
        "leaves_under": [
          "S",
          "Q"
        ]
      },
      "subtree_info": {
        "leaves": [
          "H",
          "T",
          "d433395a-27bc-457d-b6d9-c7034d020978",
          "F",
          "M",
          "J",
          "S",
          "Q",
          "O",
          "779cc759-36a9-4dae-a1c9-e021d65aa1d4",
          "14e057df-8004-47c3-9415-b7c7235ea4d8"
        ],
        "height": 3,
        "root": "A",
        "size": 5
      }
    }


Mapping a function over the nodes:

.. code:: ipython3

    def add_prefix(node):
        if node is None:
            return None
        elif node.name == "D":
            # add Q and R as children of D
            node.add_child(name="Q", value=41)
            node.add_child(name="R", value=42)
        elif node.name == "I" or node.name == "W":
            # delete I by returning None (i.e. don't add it to the new tree)
            return None
        elif "U" in [child.name for child in node.children]:
            return None
        return node
    
    root_mapped = map(deepcopy(forest.root), add_prefix)
    
    monotext(pretty_tree(root_mapped))
    
    monotext(pretty_tree(forest.root))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


Pruning nodes based on a predicate:

.. code:: ipython3

    
    def should_prune(node):
        return node.name == "A"
    
    monotext(pretty_tree(root2))
    pruned_tree = prune(root2, should_prune)
    monotext(pretty_tree(pruned_tree))



.. raw:: html

   <pre>root
   ├───── A
   ├───── B
   └───── C
          ├───── D
          ├───── E
          ├───── F
          │      └───── I
          ├───── G
          └───── H
   </pre>



.. raw:: html

   <pre>root
   ├───── B
   └───── C
          ├───── D
          ├───── E
          ├───── F
          │      └───── I
          ├───── G
          └───── H
   </pre>


Finding root-to-leaf paths:

.. code:: ipython3

    from pprint import pprint
    paths = node_to_leaf_paths(root)
    # print max path length from root to leaf
    pprint(max(paths, key=len))
    print(utils.height(root) == len(max(paths, key=len)) - 1)



.. parsed-literal::

    [TreeNode(name=root, root=root, payload={'value': 0}, len(children)=1),
     TreeNode(name=A, parent=root, root=root, payload={'value': 1}, len(children)=0)]
    True


Converting paths to a tree:

.. code:: ipython3

    rooter = paths_to_tree([["a", "b", "c"], ["a", "b", "d"], ["a", "e", "d"],
                            ["a", "f", "d"], ["a", "e", "g" ], ["a", "e", "h"],
                            ["a", "i", "j", "b"], ["a", "i", "j", "b", "m"],
                            ["a", "i", "j", "l", "b", "b", "b", "b", "b", "b", "t", "u", "v", "w", "x", "y", "b"]],
                            FlatForestNode)
    monotext(pretty_tree(rooter))



.. raw:: html

   <pre>a
   ├───── b
   │      ├───── c
   │      └───── d
   ├───── e
   │      ├───── d_0
   │      ├───── g
   │      └───── h
   ├───── f
   │      └───── d_1
   └───── i
          └───── j
                 ├───── b_0
                 │      └───── m
                 └───── l
                        └───── b_1
                               └───── b_2
                                      └───── b_3
                                             └───── b_4
                                                    └───── b_5
                                                           └───── b_6
                                                                  └───── t
                                                                         └───── u
                                                                                └───── v
                                                                                       └───── w
                                                                                              └───── x
                                                                                                     └───── y
                                                                                                            └───── b_7
   </pre>


.. code:: ipython3

    from AlgoTree.utils import depth, path, ancestors, siblings, is_root
    A = rooter.node("i")
    pretty_tree(A)
    print(depth(A.children[0]))
    print([n.name for n in path(A.children[0].children[0])])
    print([n.name for n in ancestors(A.children[0].children[0])])
    print(siblings(A.children[0]))
    print(is_root(A))


.. parsed-literal::

    2
    ['a', 'i', 'j', 'b_0']
    ['j', 'i', 'a']
    []
    False


.. code:: ipython3

    treenode = TreeNode(name="A")
    TreeNode(name="B", parent=treenode)
    C = TreeNode(name="C", parent=treenode)
    TreeNode(name="D", parent=C)
    TreeNode(name="E", parent=C)
    
    monotext(pretty_tree(treenode))



.. raw:: html

   <pre>A
   ├───── B
   └───── C
          ├───── D
          └───── E
   </pre>


.. code:: ipython3

    treenode_dict = {
        "name": "A",
        "value": 1,
        "children": [
            {"name": "B"},
            {"name": "C", "children": [
                {"name": "D"},
                {"name": "E"}
            ]}
        ]}
    
    print(json.dumps(treenode_dict, indent=2))
    print(json.dumps(treenode.to_dict(), indent=2))


.. parsed-literal::

    {
      "name": "A",
      "value": 1,
      "children": [
        {
          "name": "B"
        },
        {
          "name": "C",
          "children": [
            {
              "name": "D"
            },
            {
              "name": "E"
            }
          ]
        }
      ]
    }
    {
      "name": "A",
      "payload": null,
      "children": [
        {
          "name": "B",
          "payload": null,
          "children": []
        },
        {
          "name": "C",
          "payload": null,
          "children": [
            {
              "name": "D",
              "payload": null,
              "children": []
            },
            {
              "name": "E",
              "payload": null,
              "children": []
            }
          ]
        }
      ]
    }


.. code:: ipython3

    treenode_from_dict = TreeNode.from_dict(treenode_dict)
    monotext(pretty_tree(treenode_from_dict))
    print(treenode_from_dict == treenode)



.. raw:: html

   <pre>A
   ├───── B
   └───── C
          ├───── D
          └───── E
   </pre>


.. parsed-literal::

    True


Conclusion
----------

The ``FlatForest`` class provides a powerful and flexible way to work
with tree-like and forest-like data structures using a flat dictionary
structure. It supports a wide range of operations, including node
manipulation, tree traversal, detachment, pruning, and conversion
between different tree representations.

Explore the ``AlgoTree`` package further to discover more features and
utilities for working with trees in Python.
