import math
from typing import Optional, Any, Dict

class Geometry:
    """Minimal Geometry class
    :param srid: the SRID
    """

    def __init__(self, srid: Optional[int] = None):
        self.srid: int = srid


class Point(Geometry):
    """Point Geometry
    
    :param x: the x coordinate
    :param y: the y coordinate
    :param srid: the SRID of the point

    """

    def __init__(self, x: float, y: float, srid: Optional[int] = None):
        """Initializer"""
        super().__init__(srid)
        self.x: float = x
        self.y: float = y
    
    def as_text(self) -> str:
        """return a WKT representation of the Point geometry"""
        return f"Point({self.x} {self.y})"


    def distance(self, other) -> float:
        """Return the distance between two Point objects"""
        distance = math.sqrt((self.x - other.x)**2) + \
                    math.sqrt((self.y - other.y)**2)
        
        return distance
    
    def equals(self, other) -> bool:
        """Check if two Point objects are equal"""
        if self.x == other.x \
        and self.y == other.y \
        and self.srid == other.srid:
            return True
        else:
            return False
        

    def __geo_interface__(self):
        """Return a GeoJSON representation of a Point object"""
        return {"type": 'Point',
                'coordinates': [self.x, self.y]}
    

    def from_jeojson(self, jeojson: Dict[Any, str]):
        """Return a Point object from a jeojson"""

        raise NotImplemented
    

class LineString(Geometry):
    """Line Geometry"""

    def __init__(self, vertices: list[Point], srid: Optional[int] = None):
        """Initializer"""
        super().__init__(srid)
        self.vertices: list[Point] = vertices


    def as_text(self) -> str:
        """ Return the WKT representation of a LineString object"""
        line_wkt = []
        for p in self.vertices:
            line_wkt.append(f"({p.x} {p.y})")

        return f"LineString({','.join(line_wkt)})"
    
    def length(self) -> float:
        """ calculate the length of a line using a list of points (x,y)"""
        length = 0

        for i in range(len(self.vertices) - 1):
            length += math.sqrt((self.vertices[i].x - self.vertices[i+1].x)**2
                            + (self.vertices[i].y - self.vertices[i+1].y)**2)
    
        return length
    
    def start_point(self) -> Point:
        """Return the first point in a line"""
        return self.vertices[0]

    def end_point(self) -> Point:
        """Return the last point in a lien"""
        return self.vertices[-1]

    def num_points(self) -> int:
        """Return the number of points in a line"""
        return len(self.vertices)
    
    def point_n(self, n: int) -> Point:
        """Return the nth point in a line
            n is the index of the point 
        """
        return self.vertices[n]
    
    def is_closed(self) -> bool:
        """Check if the line is closed"""
        if Point.equals(self.vertices[0], self.vertices[-1]):
            return True
        else: return False

    def __geo_interface__(self):
        """Return a GeoJSON representation of a LineString object"""
        return {"type": 'LineString',
                'coordinates':[[p.x, p.y] for p in self.vertices]}
    

    def from_jeojson(self, jeojson: Dict[Any, str]):
        """Return a LineString object from a jeojson"""

        raise NotImplemented


class Polygon(Geometry):
    """Polygon Geometry"""

    def __init__(self, exterior: LineString, srid: Optional[int] = None):
        super().__init__(srid)
        self.exterior: LineString = exterior

    def area(self) -> float:
        """Calculate the area of the polygon using the Shoelace formula
        https://en.wikipedia.org/wiki/Shoelace_formula
        """
        area = 0
        for i in range(len(self.exterior.vertices) - 1):
            p1 = self.exterior.vertices[i]
            p2 = self.exterior.vertices[i+1]
            area += (p1.x * p1.y) - (p1.y * p2.x)

        return abs(area) / 2.0
    

    def n_rings(self):
        """Return the number of rings in the Polygon"""

        raise NotImplemented
    
    def exterior_ring(self):
        """Return the outermost ring in the Polygon as a LineString"""

        raise NotImplemented
    
    def interior_ring(self):
        """Return the innermost ring in the Polygon as a LineString"""

        raise NotImplemented
    
    def perimeter(self):
        """Return the sum of all the rings"""

        raise NotImplemented

    
    
    def as_text(self) -> str:
        """Get the WKT representation of the geometry"""
        return f'Polygon(({','.join(f'{p.x} {p.y}' 
                                    for p in self.exterior.vertices)}))'
    


class MultiPoint(Geometry):
    raise NotImplemented

class MultiLineString(Geometry):
    raise NotImplemented
