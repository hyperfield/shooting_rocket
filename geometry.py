def get_frame_size(text):
    """Return number of rows and columns occupied by a multiline frame."""
    if not text:
        return 0, 0

    rows = len(text.splitlines())
    columns = max((len(line) for line in text.splitlines()), default=0)
    return rows, columns
