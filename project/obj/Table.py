class Table:
    def __init__(self, rows=None, columns=None):
        self.rows = rows            # row: list of connected elements on the same row
        self.columns = columns      # column: list of connected elements on the same column
