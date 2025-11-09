import unittest

from geometry import Point


class PointTest(unittest.TestCase):

    def test_distance(self):
        """test case for distance method"""

        p1 = Point(300100, 40000)
        p2 = Point(300000, 40000)

        distance = p1.distance(p2)
        self.assertEqual(100, distance)


    def test_from_geojson(self):
        ...