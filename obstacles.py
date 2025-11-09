class Obstacle:
    """Keep obstacle bounds and provide collision helpers."""

    def __init__(self, row, column, rows_size, columns_size, kind="generic"):
        self.row = row
        self.column = column
        self.rows_size = rows_size
        self.columns_size = columns_size
        self.kind = kind
        self.destroyed = False

    def has_collision(self, obj_row, obj_column, size_rows=1, size_columns=1):
        """Check whether a rectangular area intersects the obstacle."""
        obj_bottom = obj_row + size_rows
        obj_right = obj_column + size_columns
        obstacle_bottom = self.row + self.rows_size
        obstacle_right = self.column + self.columns_size

        if obj_bottom < self.row:
            return False

        if obj_row > obstacle_bottom:
            return False

        if obj_right < self.column:
            return False

        if obj_column > obstacle_right:
            return False

        return True


obstacles = []


def add_obstacle(obstacle):
    obstacles.append(obstacle)


def remove_obstacle(obstacle):
    if obstacle in obstacles:
        obstacles.remove(obstacle)


def find_collision(row, column, size_rows=1, size_columns=1):
    for obstacle in obstacles:
        if obstacle.destroyed:
            continue
        if obstacle.has_collision(row, column, size_rows, size_columns):
            return obstacle
    return None


def destroy_obstacle(obstacle):
    obstacle.destroyed = True
