# Inverval.py

class CompactInterval(object):
    def __init__(self, min_point=0.0, max_point=0.0):
        self.min_point = min_point
        self.max_point = max_point

    def ContainsPoint(self, point):
        return self.min_point <= point <= self.max_point

    def Lerp(self, lerp_value):
        return self.min_point + lerp_value * (self.max_point - self.min_point)

    def LerpValue(self, point):
        return (point - self.min_point) / (self.max_point - self.min_point)

    # Intersect?  Union?  Etc.