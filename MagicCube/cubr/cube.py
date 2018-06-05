# cube.py
# Chris Barker
# CMU S13 15-112 Term Project

from MagicCube.cubr.geometry import *
import MagicCube.cubr.solutions as solutions
import copy


class Struct(object): pass


def brief(L):
    s = ''
    for e in L:
        s += str(e[0])
    return s

class CubeState(object):
    """Container for a 3D list representing the cube's state.
Non-graphical; meant for algorithmic purposes."""

    # Each element is in the form (pieceID, orientationKey)
    # Orientation Keys:
    # CORNERS
    # 2 == Z
    # 1 == Y
    # 0 == X
    # orientationKey = [first priority][second priority][third priority]
    # 210 = ZYX
    # 021 = XZY
    # etc.

    solvedState = [[[(1, 210), (2, 210), (3, 210)],
                    [(4, 210), (5, 210), (6, 210)],
                    [(7, 210), (8, 210), (9, 210)]],

                   [[(10, 210), (11, 210), (12, 210)],
                    [(13, 210), (14, 210), (15, 210)],
                    [(16, 210), (17, 210), (18, 210)]],

                   [[(19, 210), (20, 210), (21, 210)],
                    [(22, 210), (23, 210), (24, 210)],
                    [(25, 210), (26, 210), (27, 210)]]]

    barebones = [[[[], [], []],
                  [[], (5, 210), []],
                  [[], [], []]],

                 [[[], (11, 210), []],
                  [(13, 210), (14, 210), (15, 210)],
                  [[], (17, 210), []]],

                 [[[], [], []],
                  [[], (23, 210), []],
                  [[], [], []]]]
    keys = {2: Vector(0, 0, 1),
            1: Vector(0, 1, 0),
            0: Vector(1, 0, 0)}
    perpendiculars = {Vector(0, 0, 1): [0, 1],
                      Vector(0, 1, 0): [0, 2],
                      Vector(1, 0, 0): [1, 2]}

    movementCodes = solutions.MOVE_CODES
    movementKeys = {
        "U": Vector(0, 0, 1),
        "D": Vector(0, 0, -1),
        "L": Vector(-1, 0, 0),
        "R": Vector(1, 0, 0),
        "F": Vector(0, 1, 0),
        "B": Vector(0, -1, 0)
    }

    def __init__(self, state='solved'):
        self.state = state
        self.size = 3
        if self.state == 'solved':
            self.setSolved()
        elif self.state == 'barebones':
            self.setBare()

    def __str__(self):
        s = ''
        for z in range(self.size):
            for y in range(self.size):
                for x in range(self.size):
                    item = str(self.state[z][y][x])
                    s += item
                s += '\n'
            s += '\n'
        return s

    def condense(self):
        s = 'State:'
        for z in range(self.size):
            for y in range(self.size):
                for x in range(self.size):
                    item = self.state[z][y][x]
                    item2 = str(item[0]) + "'" + str(item[1])
                    s += item2
                    s += ','
                s += ','
            s += ','
        return s

    @classmethod
    def getPerps(cls, p):
        for key in cls.perpendiculars:
            if key // p: return cls.perpendiculars[key]

    @staticmethod
    def kthDigit(num, k):
        num //= (10 ** k)
        return num % 10

    @staticmethod
    def swapDigits(num, i, j):
        ithDigit = CubeState.kthDigit(num, i)
        num -= ithDigit * int(10 ** i)
        jthDigit = CubeState.kthDigit(num, j)
        num -= jthDigit * int(10 ** j)
        num += ithDigit * int(10 ** j)
        num += jthDigit * int(10 ** i)
        return num

    def rotationInfo(self, axis):
        isNeg = False
        if type(axis) == str and "'" in axis:
            isNeg = True
            axis = axis[0]

        if type(axis) == str:
            axis = CubeState.movementKeys[axis]

        rotationIndcs = []
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    pos = Vector(x - 1, y - 1, z - 1)
                    if pos ** axis > 0 and pos == axis:
                        rotationIndcs.append((x, y, z))

        oldValues = {}
        for i in rotationIndcs:
            oldValues[i] = self.state[i[2]][i[1]][i[0]]

        rot = Struct()
        rot.rotationAxis = axis
        rot.rotatingValues = [val[0] for val in oldValues.values()]
        rot.rotationDirection = isNeg
        rot.oldValues = oldValues
        rot.rotationIndcs = rotationIndcs
        return rot

    def rotate(self, r):

        # Vector axis of rotation

        axis = r.rotationAxis
        isNeg = r.rotationDirection
        rotationIndcs = r.rotationIndcs
        oldValues = r.oldValues

        for idx in rotationIndcs:
            pos = Vector(idx[0] - 1, idx[1] - 1, idx[2] - 1)
            posn = pos - (pos > axis)
            newn = axis * posn
            if isNeg:
                newn = newn * -1.
            new = newn + (pos > axis)

            # Alter the rotationkey
            (oldId, oldKey) = oldValues[idx]
            perps = CubeState.getPerps(axis)
            toSwap = []
            for perp in perps:
                for i in range(self.size):
                    if CubeState.kthDigit(oldKey, i) == perp:
                        toSwap.append(i)
            newKey = CubeState.swapDigits(oldKey, *toSwap)
            # newKey = CubeState.swapDigits(oldKey, toSwap[0], toSwap[1])
            newValue = (oldId, newKey)

            newi = (int(new.x + 1), int(new.y + 1), int(new.z + 1))
            self.state[newi[2]][newi[1]][newi[0]] = newValue

    def copy(self):
        return CubeState(copy.deepcopy(self.state))

    def setBare(self):
        self.state = copy.deepcopy(CubeState.barebones)

    def setSolved(self):
        self.state = copy.deepcopy(CubeState.solvedState)

    def setState(self, state):
        self.state = state

    def setStateItem(self, z, y, x, item):
        self.state[z][y][x] = item