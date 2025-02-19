from utils.vector import Vector3D
from typing import Union
from math import sin, cos


class Matrix3D:
    def __init__(self, row1: 'Vector3D', row2: 'Vector3D', row3: 'Vector3D', row4: 'Vector3D') -> None:
        self.columns = [row1, row2, row3, row4]

    def __add__(self, other: 'Matrix3D') -> 'Matrix3D':
        return Matrix3D(self.columns[0] + other.columns[0],
                        self.columns[1] + other.columns[1],
                        self.columns[2] + other.columns[2],
                        self.columns[3] + other.columns[3])

    def __mul__(self, scalar: Union[int, float]) -> 'Matrix3D':
        return Matrix3D(self.columns[0] * scalar,
                        self.columns[1] * scalar,
                        self.columns[2] * scalar,
                        self.columns[3] * scalar)

    def __rmul__(self, scalar: Union[int, float]) -> 'Matrix3D':
        return self * scalar

    def __matmul__(self, other: Union['Vector3D', 'Matrix3D']) -> Union['Vector3D', 'Matrix3D']:
        if type(other) is Vector3D:
            return Vector3D(self.columns[0].dot(other),
                            self.columns[1].dot(other),
                            self.columns[2].dot(other),
                            self.columns[3].dot(other))

        other_m = other.transpose()
        return Matrix3D(*[Vector3D(*[row.dot(other_m_row) for other_m_row in other_m]) for row in self.columns])

    def transpose(self) -> 'Matrix3D':
        return Matrix3D(
            Vector3D(self.columns[0].x, self.columns[1].x,
                     self.columns[2].x, self.columns[3].x),
            Vector3D(self.columns[0].y, self.columns[1].y,
                     self.columns[2].y, self.columns[3].y),
            Vector3D(self.columns[0].z, self.columns[1].z,
                     self.columns[2].z, self.columns[3].z),
            Vector3D(self.columns[0].w, self.columns[1].w,
                     self.columns[2].w, self.columns[3].w))

    @staticmethod
    def identity():
        return Matrix3D(Vector3D(1, 0, 0, 0),
                        Vector3D(0, 1, 0, 0),
                        Vector3D(0, 0, 1, 0),
                        Vector3D(0, 0, 0, 1))

    @staticmethod
    def rotation_x(theta):
        return Matrix3D(Vector3D(1, 0, 0, 0),
                        Vector3D(0, cos(theta), sin(theta), 0),
                        Vector3D(0, -sin(theta), cos(theta), 0),
                        Vector3D(0, 0, 0, 1))

    @staticmethod
    def rotation_y(theta):
        return Matrix3D(Vector3D(cos(theta), 0, -sin(theta), 0),
                        Vector3D(0, 1, 0, 0),
                        Vector3D(sin(theta), 0, cos(theta), 0),
                        Vector3D(0, 0, 0, 1))

    @staticmethod
    def rotation_z(theta):
        return Matrix3D(Vector3D(cos(theta), -sin(theta), 0, 0),
                        Vector3D(sin(theta), cos(theta), 0, 0),
                        Vector3D(0, 0, 1, 0),
                        Vector3D(0, 0, 0, 1))

    def __getitem__(self, index: int) -> 'Vector3D':
        return self.columns[index]

    def __str__(self) -> str:
        return "Matrix3D(" + ",\n         ".join(map(str, self.columns)) + ")"


if __name__ == "__main__":
    a = Matrix3D(Vector3D(1, 0, 0, 0), Vector3D(0, 2, 1, 0),
                 Vector3D(0, 0, 1, 0), Vector3D(0, 0, 0, 1))
    b = Matrix3D(Vector3D(2, 3, 1, 0), Vector3D(2, 3, 1, 0),
                 Vector3D(2, 3, 1, 0), Vector3D(2, 3, 1, 0))
    c = Vector3D(3, 2, 1, 0)

    d = Matrix3D.rotation_z(60)
    print(a)
    print(a @ b)
    print(d)
