import os


def shorten_filename(filename, max_length):
    name, ext = os.path.splitext(filename)
    if len(filename) <= max_length:
        return filename
    keep = max_length - len(ext) - 3
    if keep <= 0:
        return '...' + ext[-(max_length - 3):]
    return name[:keep] + '...' + ext


def shorten_path(path, max_total_length=45):
    if len(path) <= max_total_length:
        return path

    parts = path.replace("\\", "/").split("/")
    if not parts:
        return path

    filename = parts[-1]
    folders = parts[:-1]
    min_filename_len = 10
    max_filename_len = max_total_length - len(folders)
    if max_filename_len < min_filename_len:
        return shorten_filename(filename, max_total_length)

    filename_short = shorten_filename(filename, min(max_filename_len, len(filename)))
    remaining = max_total_length - len(filename_short) - len(folders)
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
    if len(result) > max_total_length:
        return "..." + result[-(max_total_length - 3):]
    return result
