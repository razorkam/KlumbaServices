class District:
    def __init__(self, p_data, p_name):
        self.data = p_data # Polygon representation
        self.name = p_name

    def contains(self, point):
        if self.data.contains(point):
            return self.name
        else:
            return None
