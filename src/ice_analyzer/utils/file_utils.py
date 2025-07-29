import os

def load_custom_comments(comment_file_path):
    """Lädt die Datei mit benutzerdefinierten Kommentaren im erweiterten Format."""
    if not os.path.exists(comment_file_path):
        print(f"⚠️ Kommentar-Datei nicht gefunden: {comment_file_path}")
        return {}

    with open(comment_file_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]

    comments = {}
    current_file = None
    buffer = []

    for line in lines:
        if line.startswith("#"):
            if current_file and buffer:
                comments[current_file] = "\n".join(buffer)
            current_file = line[1:].strip()
            buffer = []
        elif line:
            buffer.append(line)

    if current_file and buffer:
        comments[current_file] = "\n".join(buffer)

    return comments

    pass
