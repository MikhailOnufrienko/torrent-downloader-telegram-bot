import pygtrie


def file_paths_to_dict(paths: list[str]) -> dict[str, str]:
    trie = pygtrie.StringTrie(separator="/")
    for path in paths:
        trie[path] = None
    tree = trie_to_nested_dict(trie)
    return tree


def trie_to_nested_dict(trie, prefix=""):
    result = {}

    if prefix:
        items = trie.items(prefix=prefix)
    else:
        items = trie.items()

    seen = set()
    for full_key, value in items:
        relative = full_key[len(prefix):].lstrip("/") if prefix else full_key
        parts = relative.split("/")
        if not parts or parts[0] in seen:
            continue

        head = parts[0]
        seen.add(head)
        full_head = f"{prefix}/{head}" if prefix else head

        if trie.has_subtrie(full_head):
            result[head] = trie_to_nested_dict(trie, full_head)
        else:
            result[head] = value
    return result

def tree_to_file_paths(tree: dict, prefix="") -> set[str]:
    result = set()
    for key, value in tree.items():
        full_path = f"{prefix}/{key}" if prefix else key
        if isinstance(value, dict):
            result |= tree_to_file_paths(value, full_path)
        else:
            result.add(full_path)
    return result
