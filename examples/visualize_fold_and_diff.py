"""
Worked example: "Watch it evaluate" and "Watch it shrink"

Demonstrates two core AlgoTree v3 P3 features:

1. Node.fold_traced -- evaluate an arithmetic AST while recording
   per-node step/value/arity; print a Mermaid step-through filmstrip.

2. diff(before, after).to_mermaid() -- visualize a one-rule rewrite
   (x*1 -> x) as a green/red/yellow Mermaid diff diagram.
"""

import sys
import os

# Ensure the package root is on sys.path so this script is runnable
# directly (e.g. ``python examples/visualize_fold_and_diff.py``) as well
# as via pytest subprocess invocation.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AlgoTree import Node, Trace, diff, DiffTree


# ---------------------------------------------------------------------------
# 1. Build an arithmetic AST:  add(mul(3, 1), 2)  == 5
#
#   Post-order steps:
#     step 0 -> '3'   (leaf, value 3)
#     step 1 -> '1'   (leaf, value 1)
#     step 2 -> 'mul' (3 * 1 = 3)
#     step 3 -> '2'   (leaf, value 2)
#     step 4 -> 'add' (3 + 2 = 5)  <- root
# ---------------------------------------------------------------------------

before = Node('add',
              Node('mul', Node('3'), Node('1')),
              Node('2'))


def eval_fn(n, cs):
    """Evaluate arithmetic tree node."""
    if n.is_leaf:
        return int(n.name)
    ops = {
        'add': sum,
        'mul': lambda xs: xs[0] * xs[1],
    }
    return ops[n.name](cs)


result, trace = before.fold_traced(eval_fn)

print("=" * 60)
print(f"AST: add(mul(3, 1), 2)  =>  {result}")
print("=" * 60)

# Show all steps
print("\n--- Fold trace (post-order steps) ---")
for step_node in trace.steps():
    arity = step_node['arity']
    kind = "leaf" if arity == 0 else f"arity={arity}"
    print(f"  step {step_node['step']:2d}  {step_node.name:6s}  value={step_node['value']}  ({kind})")

# Print the full Mermaid filmstrip
print("\n--- Step-through frames (Mermaid) ---")
frames = list(trace.frames())
print(f"  {len(frames)} frames total")
for i, frame in enumerate(frames):
    print(f"\n  [Frame {i}]")
    for line in frame.splitlines():
        print(f"    {line}")

# ---------------------------------------------------------------------------
# 2. Apply the rewrite rule:  x * 1  ->  x
#    (simplification: multiplying by 1 is a no-op)
# ---------------------------------------------------------------------------

def simplify(n):
    """Rewrite x * 1  ->  x (returns n unchanged for all other nodes)."""
    if n.name == 'mul' and len(n.children) == 2:
        left, right = n.children
        if right.name == '1':
            return left
        if left.name == '1':
            return right
    return n


after = before.map(simplify)

print("\n" + "=" * 60)
print("After simplify(mul(x, 1) -> x):")
print(f"  before: {before.render('unicode')!r}")
print(f"  after:  {after.render('unicode')!r}")
print("=" * 60)

# Show the diff
dt = diff(before, after)
s = dt.summary()
print(f"\nDiff summary: {s}")
print(f"Changed nodes: {[n.name for n in dt.changed_nodes()]}")

print("\n--- Diff Mermaid diagram ---")
mermaid_diff = dt.to_mermaid()
for line in mermaid_diff.splitlines():
    print(f"  {line}")

print("\n--- Diff HTML (first 500 chars) ---")
html_diff = dt.to_html()
print(f"  {html_diff[:500]}...")

# Verify result is correct after simplification
result_after, _ = after.fold_traced(eval_fn)
assert result_after == result, (
    f"Simplified tree should evaluate to the same result: {result_after} != {result}"
)
print(f"\nVerified: simplified tree evaluates to {result_after} (same as {result})")
print("\nDone.")
