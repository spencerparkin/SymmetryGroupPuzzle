# Region.py

from Math.Polygon import Polygon

class Region(object):
    # This class is a generalization of a polygon as representing a sub-region
    # of the plane that can have holes in it.
    
    def __init__(self):
        self.polygon = Polygon()
        self.hole_list = []
        self.triangle_list = []
        
    def SplitAgainst(self, cutting_polygon):
        pass # Hmmm...this might not be too much harder.  Holes can be created, coalesced, removed.
    
    def Tessellate(self):
        pass # Hmmm...this seems a hard problem.