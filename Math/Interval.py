# Inverval.py

class CompactInterval(object):
    def __init__(self, min_point=0.0, max_point=0.0):
        self.min_point = min_point
        self.max_point = max_point

    def Serialize(self):
        data = {
            'min_point': self.min_point,
            'max_point': self.max_point
        }
        return data

    def Deserialize(self, data):
        self.min_point = float(data['min_point'])
        self.max_point = float(data['max_point'])
        return self

    def ContainsPoint(self, point):
        return self.min_point <= point <= self.max_point

    def Lerp(self, lerp_value):
        return self.min_point + lerp_value * (self.max_point - self.min_point)

    def LerpValue(self, point):
        return (point - self.min_point) / (self.max_point - self.min_point)

    def Intersection(self, intervalA, intervalB):
        pass # TODO: Return a list of zero, one or two intervals.
        
    def Union(self, intervalA, intervalB):
        pass # TODO: Return a list of one or more intervals.
    
    def Difference(self, intervalA, intervalB):
        pass # TODO: Return a list of zero or more intervals.