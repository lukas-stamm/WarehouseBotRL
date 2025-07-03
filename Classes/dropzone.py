class Dropzone:
    def __init__(self, grid_top_left, grid_bottom_right, accepted_type):
        self.x1, self.y1 = grid_top_left
        self.x2, self.y2 = grid_bottom_right
        self.accepted_type = accepted_type

    def contains(self, grid_x, grid_y):
        """
        Checks if (grid_x, grid_y) is inside the delivery zone.
        """
        return (self.x1 <= grid_x <= self.x2) and (self.y1 <= grid_y <= self.y2)
