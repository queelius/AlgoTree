

- See `SPEC.md` for a newer way of representing the tree in JSON for
the `FlatTree` spec. For consistency, we'll likely want to provide the same
option for `TreeNode`.

- Provide in the init constructor ways to override the default keys for
the logical root node (defaut: `__ROOT__`), the detached key
(default: `__DETACHED__`), the mapping key (newer spec, default: `mapping`),
 in `FlatTree`, and parent key (default: `parent`).

