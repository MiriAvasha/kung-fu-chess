from model.position import Position


def path_cells(source: Position, destination: Position):
    """Squares from source to destination inclusive (knight-like jumps have no intermediates)."""
    cells = [Position(source.row, source.col)]
    d_row = destination.row - source.row
    d_col = destination.col - source.col
    steps = max(abs(d_row), abs(d_col))
    if steps == 0:
        return cells

    # Non-sliding leap (e.g. knight): only endpoints.
    if d_row != 0 and d_col != 0 and abs(d_row) != abs(d_col):
        cells.append(Position(destination.row, destination.col))
        return cells

    row_step = 0 if d_row == 0 else d_row // abs(d_row)
    col_step = 0 if d_col == 0 else d_col // abs(d_col)
    row, col = source.row, source.col
    for _ in range(steps):
        row += row_step
        col += col_step
        cells.append(Position(row, col))
    return cells


def last_square_before(source: Position, destination: Position, collision: Position) -> Position:
    """Closest square reached on the path before the collision square."""
    path = path_cells(source, destination)
    for index, cell in enumerate(path):
        if cell == collision:
            if index == 0:
                return path[0]
            return path[index - 1]
    if len(path) >= 2:
        return path[-2]
    return path[0]


def _are_adjacent(a: Position, b: Position) -> bool:
    return max(abs(a.row - b.row), abs(a.col - b.col)) == 1


def last_squares_before_head_on(
    source_a: Position, dest_a: Position,
    source_b: Position, dest_b: Position,
):
    """
    For two allies walking into each other: each stops on the closest square
    reached before they meet (same cell or face-to-face).
    """
    path_a = path_cells(source_a, dest_a)
    path_b = path_cells(source_b, dest_b)
    max_t = min(len(path_a), len(path_b)) - 1
    for t in range(1, max_t + 1):
        cell_a = path_a[t]
        cell_b = path_b[t]
        if cell_a == cell_b:
            return path_a[t - 1], path_b[t - 1]
        if _are_adjacent(cell_a, cell_b):
            return cell_a, cell_b
    stop_a = path_a[-2] if len(path_a) >= 2 else path_a[0]
    stop_b = path_b[-2] if len(path_b) >= 2 else path_b[0]
    return stop_a, stop_b
