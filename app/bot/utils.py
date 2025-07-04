import os

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


def shorten_filename(filename, max_length):
    name, ext = os.path.splitext(filename)
    if len(filename) <= max_length:
        return filename
    keep = max_length - len(ext) - 3  # '...'
    if keep <= 0:
        return '...' + ext[-(max_length - 3):]
    return name[:keep] + '...' + ext


def shorten_path(path, max_total_length=45):
    parts = path.replace("\\", "/").split("/")
    if not parts:
        return path

    filename = parts[-1]
    folders = parts[:-1]

    # Если путь и так короткий — оставляем как есть
    if len(path) <= max_total_length:
        return path

    # Определим максимальную длину на файл
    min_filename_len = 10  # разумный минимум на имя файла
    max_filename_len = max_total_length - len(folders)  # учтём хотя бы один слэш между папками

    if max_filename_len < min_filename_len:
        return shorten_filename(filename, max_total_length)

    filename_short = shorten_filename(filename, min(max_filename_len, len(filename)))

    # Сколько осталось символов под папки
    remaining = max_total_length - len(filename_short) - len(folders)  # слэши между папками

    # Распределим оставшиеся символы по папкам
    if not folders or remaining <= 0:
        return filename_short if len(filename_short) <= max_total_length else filename_short[:max_total_length]

    per_folder = remaining // len(folders)
    shortened_folders = []
    for folder in folders:
        if len(folder) <= per_folder:
            shortened_folders.append(folder)
        elif per_folder <= 2:
            shortened_folders.append("..")
        else:
            shortened_folders.append(folder[:per_folder - 2] + "..")

    result = "/".join(shortened_folders + [filename_short])
    # Финальный обрез, если чуть-чуть не влезли
    if len(result) > max_total_length:
        return "..." + result[-(max_total_length - 3):]
    return result
