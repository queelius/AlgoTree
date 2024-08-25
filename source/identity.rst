Understanding Equality in Trees and Nodes
=========================================

Identity and equality are foundational concepts that help us reason about
relationships between objects. While identity implies strict sameness, equality
often refers to contextual similarities between objects. In this document, we
will define identity in a strict sense and then explore different ways to define
and use equality.

Identity: The Strict Definition
-------------------------------

In philosophy, **Leibniz's Law** (or the *Indiscernibility of Identicals*)
states that two objects, `x` and `y`, are identical if and only if for all
predicates `p`, `p(x) = p(y)`. In other words, two objects are identical if
every possible property holds equally for both objects. This is a very strong
form of identity, implying that there is no possible distinction between `x` and
`y`.

In computer science, this strict definition of identity corresponds to the
concept of **object identity**. Two objects are identical if they are the same
instance in memory, which can be checked using the `id()` function in Python.
This is the only situation in which we can guarantee that every predicate will
yield the same result for both objects, as their memory addresses are the same.

**Example:** In Python, two variables are considered identical if they point to
the same object in memory:
  
.. code-block:: python

   x = [1, 2, 3]
   y = x
   assert id(x) == id(y)  # True, x and y are identical


However, strict identity is often not what we are interested in when reasoning
about data structures or values. In most cases, we want to compare objects based
on their properties or behaviors, rather than their memory addresses. This leads
us to the concept of **equality**, which can be defined in various ways
depending on the context.

Equality: Intrinsic and Extrinsic Properties
--------------------------------------------

When defining equality, we must consider whether we are comparing the
*intrinsic* properties of an object or its *extrinsic* properties:

1. **Intrinsic Properties:**: These are the properties that belong to the object
itself, independent of its relationships with other objects. For example, the
intrinsic properties of an object might include its name, value, or other
internal attributes.
   
2. **Extrinsic Properties:**: These are properties that depend on the object's 
relationships to other objects or its environment. For example, the extrinsic
properties of an object might include its position within a structure, its
relationships to other objects, or its role within a larger context.

Equality in Trees and Nodes
---------------------------

Now that we have discussed identity and equality at a high level, we can turn
our attention to how these concepts apply specifically to trees and nodes.
Trees, being hierarchical data structures, bring particular concerns about how
we compare nodes and entire tree structures. Equality can be defined based on
both intrinsic and extrinsic properties in this context.

1. **Value Equality (Intrinsic):**

   Two nodes are considered equal if they have the same intrinsic value
   (payload and name), even if they are different instances in memory. Note that
   we do not look at the parent-child relationships or the position in the tree.

2. **Path Equality (Mixed):**
   
   Two nodes or trees are equal if they occupy the same positions in trees that
   compare equal. This may often be relaxed and consider only the path from the
   root to the node, rather than the entire structure. Another related kind
   of equality is positional equality, which does not consider even the names
   of nodes, only their positions in isomorphic trees.

3. **Name Equality (Intrinsic):**
   
   Two nodes are equal if they share the same name. This focuses only on a
   specific intrinsic attribute, abstracting away other properties. It is
   often the most important property for certain types of trees (e.g., there
   may not even be payloads and names may be unique).

4. **Payload Equality (Intrinsic):**

   Two nodes are equal if they contain the same payload, even if their
   structure or position in the tree differs.

5. **Tree Equality (Mixed):**

   Two trees are equal if they have the same structure and the same data at each
   corresponding node, considering both intrinsic and extrinsic properties.

6. **Tree Isomorphism (Mixed):**

   Two trees are isomorphic if they have the same structure, but the labels and
   data at each node may differ. This is a weaker form of equality that focuses
   strictly on its structure.

Hashing and Equality
--------------------

Hashing is a technique used to map data of arbitrary size to fixed-size values.
It has a wide range of applications, but here we are interested in how it can be
used to implement different forms of equality. It is not necessarily the most
efficient way to implement equality, but it can also be used to store objects in
hash-based data structures like dictionaries or sets.

Here are examples of how different hash functions can be used to implement
various forms of equality for trees and nodes:

1. **Name Equality:**

   Two nodes are considered equal if they have the same name.

   .. code-block:: python
   
      node1 = Node('A', payload=10)
      node2 = Node('A', payload=20)
      assert NodeHasher.name(node1) == NodeHasher.name(node2) 

2. **Payload Equality:**

   Two nodes are considered equal if they have the same payload.

   .. code-block:: python

      node1 = Node('A', payload=10)
      node2 = Node('B', payload=10)
      assert NodeHasher.payload(node1) == NodeHasher.payload(node2)

3. **Node Equality (Name + Payload):**

   Two nodes are considered equal if they share the same name and payload.

   .. code-block:: python

      node1 = Node('A', payload=10)
      node2 = Node('A', payload=10)
      assert NodeHasher.node(node1) == NodeHasher.node(node2)

4. **Path Equality:**

   Two nodes are considered equal if they occupy the same position in their
   respective trees.

   .. code-block:: python

      root1 = Node('Root')
      child1 = Node('A')
      root1.add_child(child1)

      root2 = Node('Root')
      child2 = Node('B')
      root2.add_child(child2)

      assert NodeHasher.path(child1) == NodeHasher.path(child2)

5. **Tree Equality:**

   Two trees are considered equal if they have the same structure and data.

   .. code-block:: python

      root1 = Node('Root')
      child1_1 = Node('A', payload=10)
      child1_2 = Node('B', payload=20)
      root1.add_child(child1_1)
      root1.add_child(child1_2)

      root2 = Node('Root')
      child2_1 = Node('A', payload=10)
      child2_2 = Node('B', payload=20)
      root2.add_child(child2_1)
      root2.add_child(child2_2)

      assert TreeHasher.tree(root1) == TreeHasher.tree(root2)

6. **Tree Isomorphism:**

   Two trees are considered equal if they have the same structure, but not
   necessarily the same data or labels.

   .. code-block:: python

      root1 = Node('Root')
      child1_1 = Node('A', payload=10)
      child1_2 = Node('B', payload=20)
      root1.add_child(child1_1)
      root1.add_child(child1_2)

      root2 = Node('Root')
      child2_1 = Node('1', payload=30)
      child2_2 = Node('2', payload=40)
      root2.add_child(child2_1)
      root2.add_child(child2_2)

      assert TreeHasher.isomorphic(root1) == TreeHasher.isomorphic(root2)

Explanation of Hash Collisions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's important to note that hashing functions, while efficient for comparisons,
have a small probability of producing hash collisions—situations where two
different objects produce the same hash value. This is because the space of
possible hash values is finite, while the space of possible inputs (nodes,
trees, etc.) is effectively infinite.

For example, two different trees might produce the same hash value due to a
collision, but this would be rare assuming a good hash function.

Philosophical Perspective: The Ship of Theseus
----------------------------------------------

The **Ship of Theseus** is a famous philosophical thought experiment that raises
questions about identity and persistence over time. The thought experiment asks:
if all the parts of a ship are gradually replaced, piece by piece, is it still
the same ship? This highlights the tension between identity as a matter of
intrinsic properties (the materials of the ship) versus extrinsic properties
(the ship as a whole and its continuity over time).

In the context of trees and nodes, this thought experiment reminds us that
identity is often a convention and can depend on what we consider intrinsic or
extrinsic. For instance, a node might be considered the "same" if it has the
same name and payload, even if its position in the tree changes. Alternatively,
a node’s identity might be tied to its position within the tree, and changing
that position might alter its identity.

Conclusion
----------

Identity and equality are distinct but related concepts. **Identity** in its
strictest sense, as defined by Leibniz's Law, implies complete
indistinguishability and is typically realized in computer science through
object identity (i.e., the `id()` function). However, in practice, we often work
with different forms of **equality**, which allow us to compare objects based on
specific properties or criteria.

By distinguishing between **intrinsic** and **extrinsic** properties, we can
better define equality in context. Whether we care about value, structure, or
position, choosing the right form of equality for our problem is crucial to
building correct and efficient systems, particularly when working with tree
structures.
