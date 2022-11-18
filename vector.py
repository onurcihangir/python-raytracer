from math import sqrt
from typing import Union


class Vector3D:
    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __add__(self, vec2: 'Vector3D') -> 'Vector3D':
        """
        Returns new Vector3D object with new coordinates after addition
        """
        return self.__class__(vec2.x + self.x, vec2.y + self.y, vec2.z + self.z, self.w)

    def add(self, vec2: 'Vector3D') -> 'Vector3D':
        """
        Adds other vector's coordinates to itself
        """
        self.x += vec2.x
        self.y += vec2.y
        self.z += vec2.z

    def __sub__(self, vec2: 'Vector3D') -> 'Vector3D':
        """
        Returns new Vector3D object with new coordinates after subtraction
        """
        return self + (-vec2)

    def sub(self, vec2: 'Vector3D') -> 'Vector3D':
        """
        Subtracts other vector's coordinates to itself
        """
        self.x -= vec2.x
        self.y -= vec2.y
        self.z -= vec2.z

    def __mul__(self, scalar: Union[int, float]) -> 'Vector3D':
        """
        Returns new Vector3D object with new coordinates after multiplication
        """
        return self.__class__(scalar * self.x, scalar * self.y, scalar * self.z, self.w)

    def __rmul__(self, scalar: Union[int, float]) -> 'Vector3D':
        return self * scalar

    def mul(self, scalar: Union[int, float]) -> 'Vector3D':
        """Multiplies scalar with itself"""
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar

    def __truediv__(self, scalar: Union[int, float]) -> 'Vector3D':
        """
        Returns new Vector3D object with new coordinates after division
        """
        return self.__class__(self.x / scalar, self.y / scalar, self.z / scalar, self.w)

    def div(self, scalar: Union[int, float]) -> None:
        """Divides scalar with itself"""
        self.x /= scalar
        self.y /= scalar
        self.z /= scalar

    def dot(self, vec2: 'Vector3D') -> float:
        """Performs dot product and return float"""
        return self.x*vec2.x+self.y*vec2.y+self.z*vec2.z

    def cross(self, vec2: 'Vector3D') -> 'Vector3D':
        """Creates clone and calls cross product function"""
        return self.clone().cross_inline(vec2)

    def cross_inline(self, vec2: 'Vector3D') -> 'Vector3D':
        """Performs cross product"""
        x = self.y * vec2.z - self.z * vec2.y
        y = self.z * vec2.x - self.x * vec2.z
        z = self.x * vec2.y - self.y * vec2.x

        self.x, self.y, self.z, self.w = x, y, z, 0

        return self

    def length(self) -> 'Vector3D':
        return sqrt(self.x**2+self.y**2+self.z**2)

    def normalize_inline(self) -> 'Vector3D':
        """
        To normalize each component is divided by the length of th vector
        """
        length = self.length()

        if length > 0:
            oneOverMag = 1.0/length

            self.x = self.x*oneOverMag
            self.y = self.y*oneOverMag
            self.z = self.z*oneOverMag

        return self

    def normalize(self) -> 'Vector3D':
        """Calls normalization and returns new vector"""
        return self.clone().normalize_inline()

    def __neg__(self) -> 'Vector3D':
        return -1 * self

    def clone(self) -> 'Vector3D':
        """Creates clone of itself"""
        return self.__class__(self.x, self.y, self.z, self.w)

    def to_array(self) -> list:
        return list((self.x, self.y, self.z, self.w))

    def __str__(self) -> str:
        return f"({self.x},{self.y},{self.z},{self.w})"


if __name__ == "__main__":
    a = Vector3D(2, 3, 1, 0)
    b = Vector3D(1, 2, 3, 0)
    print(a * 2.0)
    print(a.cross(b).length())
    print(a.normalize())
    print(a.dot(b))
