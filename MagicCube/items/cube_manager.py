import threading

import cv2
import numpy as np
import math
from MagicCube.utils import util


class Color(object):
    # WHITE = 0
    # BLUE = 1
    # RED = 2
    # ORANGE = 3
    # GREEN = 4
    # YELLOW = 5

    WHITE = 0
    RED = 1
    BLUE = 2
    ORANGE = 3
    GREEN = 4
    YELLOW = 5
    NONE = 6

    colors = [
        (200, 200, 200),
        (0, 0, 255),
        (255, 0, 0),
        (0, 120, 255),
        (0, 255, 0),
        (0, 255, 255),
        (50, 50, 50)
    ]

    # hsvRange = [
    #     ((0, 0, 100), (180, 70, 255)),
    #     ((156, 100, 100), (180, 255, 255), (0, 100, 100), (0, 255, 255)),
    #     ((90, 100, 100), (124, 255, 255)),
    #     ((1, 100, 100), (12, 255, 255)),
    #     ((42, 100, 100), (80, 255, 255)),
    #     ((13, 100, 100), (41, 255, 255))
    # ]
    hsvRange = [
        ((0, 0, 46), (180, 70, 255)),
        ((156, 71, 46), (180, 255, 255), (0, 71, 46), (4, 255, 255)),
        ((90, 71, 46), (124, 255, 255)),
        ((5, 71, 46), (16, 255, 255)),
        ((45, 71, 46), (80, 255, 255)),
        ((17, 71, 46), (44, 255, 255))
    ]

    names = {
        WHITE: 'white',
        RED: 'red',
        BLUE: 'blue',
        ORANGE: 'orange',
        GREEN: 'green',
        YELLOW: 'yellow',
        NONE: 'NONE',
        None: 'None',

    }

    @staticmethod
    def getColorByIndex(index):
        if index is None or index > 5 or index < 0:
            return None
        return Color.colors[index]

    @staticmethod
    def getColorByHSV(hsv):

        for hsvs in Color.hsvRange:
            for index in range(0, len(hsvs), 2):
                min = hsvs[index]
                max = hsvs[index + 1]

                if min[0] <= hsv[0] <= max[0] and min[1] <= hsv[1] <= max[1] and min[2] <= hsv[2] <= max[2]:
                    # divide orange and red
                    # if 0 <= hsv[0] <= 5:
                    #     if hsv[1] > 125:
                    #         # orange
                    #         return 3
                    #     else:
                    #         # red
                    #         return 2
                    assumeColorIndex = Color.hsvRange.index(hsvs)
                    if assumeColorIndex == Color.ORANGE or assumeColorIndex == Color.RED:
                        pass

                    return Color.hsvRange.index(hsvs)
        return None

    @staticmethod
    def bgr2hsv(bgr):
        src = np.uint8([[bgr]])
        ret = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)[0][0]
        return ret[0], ret[1], ret[2]

    @staticmethod
    def getColorByBGR(bgr):
        return Color.getColorByHSV(Color.bgr2hsv(bgr))


class Line(object):

    def __init__(self, x1, y1, x2, y2) -> None:
        self.theta = 0
        self.p = 0
        self.points = ((x1, y1), (x2, y2))
        if y1 == y2:
            self.theta = np.pi / 2
            self.p = y1
        else:
            self.theta = math.atan(float(x2 - x1) / (y1 - y2))
            # self.theta = math.atan2(x2 - x1, y1 - y2)
            self.p = x1 * math.cos(self.theta) + y1 * math.sin(self.theta)

    def __str__(self) -> str:
        return '(p=' + str(self.p) + ', theta=' + str(self.theta) + ')'

    __repr__ = __str__

    def getTheta(self):
        if self.theta > np.pi / 2:
            return self.theta - np.pi
        return self.theta

    def atan2(self) -> float:
        return math.atan2(self.points[1][1] - self.points[0][1], self.points[1][0] - self.points[0][0])

    @staticmethod
    def parallelDistanceArc(arc1, arc2):
        arc1, arc2 = max(arc1, arc2), min(arc1, arc2)
        distance1 = arc1 - arc2 if arc1 - arc2 < np.pi * 2 + arc2 - arc1 else np.pi * 2 + arc2 - arc1
        distance2 = abs(np.pi + arc2 - arc1)
        return min(distance1, distance2)


class Block(object):
    __block_num = 0

    def __init__(self, cnt, color) -> None:
        self.id = Block.__block_num
        Block.__block_num += 1

        self.__contour = cnt
        self.__color = color
        M = self.__moments = cv2.moments(cnt)
        self.__centroid = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        self.lines = []  # type: list[Line]
        self.thetas = []
        if len(cnt) == 4:
            self.probability = 1
            self.__cal_lines()
            self.__adj_lines()
        else:
            self.probability = 0.5

        self.links = []  # type: list[Block]
        self.position = None

    def __str__(self) -> str:
        content = '(id = ' + str(self.id) + ', theta = (' + str(round(self.thetas[0], 3)) + ',' + str(
            round(self.thetas[1], 3)) + '), area = ' + str(
            round(cv2.contourArea(self.contour()), 3)) + ")"

        # points = []
        # for (point,) in self.contour():
        #     points.append(point)
        #
        # crossvec0 = util.divideList(
        #     util.listPlus(util.listPlus(points[1], points[0], False), util.listPlus(points[2], points[3], False)),
        #     2)
        # crossvec1 = util.divideList(
        #     util.listPlus(util.listPlus(points[3], points[0], False), util.listPlus(points[2], points[1], False)),
        #     2)
        #
        # content += '\n'
        # content += str([crossvec0, crossvec1, util.negativeList(crossvec0), util.negativeList(crossvec1)])

        content += '\n -- links: '
        for linkedBlocks in self.links:
            content += str(linkedBlocks.id)
            content += ' '

        if self.position is not None:
            content += ('(' + str(self.position[0]) + ',' + str(self.position[1]) + ')')

        return content

    __repr__ = __str__

    def inBlock(self, point):
        return cv2.pointPolygonTest(self.__contour, (point[0], point[1]), False) >= 0

    def isLinkedWith(self, block, set) -> bool:
        searchingblocks = set.blocks[:]

        remains = [self]
        while len(remains) != 0:
            current = remains.pop()

            for b in current.links:
                if b is block:
                    return True
                else:
                    if b in searchingblocks:
                        remains.append(b)
                        searchingblocks.remove(b)
        return False

    def __cal_lines(self):
        for i in range(0, 4):
            i2 = (i + 1) % 4
            x1, y1 = self.__contour[i][0]
            x2, y2 = self.__contour[i2][0]
            line = Line(x1, y1, x2, y2)
            self.lines.append(line)

    def __adj_lines(self):
        for i in range(0, 2):
            line1 = self.lines[i]
            line2 = self.lines[i + 2]

            if self.id == 27:
                aaa = 1

            arctan1 = line1.atan2()
            arctan2 = line2.atan2()
            # arctan1, arctan2 = max(arctan1, arctan2), min(arctan1, arctan2)
            # distance1 = arctan1 - arctan2 if arctan1 - arctan2 < np.pi * 2 + arctan2 - arctan1 else np.pi * 2 + arctan2 - arctan1
            # distance2 = abs(np.pi + arctan2 - arctan1)
            # if min(distance1, distance2) > math.pi / 18:
            if Line.parallelDistanceArc(arctan1, arctan2) > math.pi / 18:
                # 2 lines which are opposite to the other
                self.probability = 0.8
                return
            # if math.fabs(line1.theta - line2.theta) > math.pi / 18:
            #     # 2 lines which are opposite to the other
            #     self.probability = 0.8
            #     return
            else:
                theta = (line1.theta + line2.theta) / 2
                # if theta > np.pi:
                #     theta -= np.pi
                # elif theta < 0:
                #     theta += np.pi
                if theta > np.pi / 2:
                    theta -= np.pi
                self.thetas.append(theta)

        # 2 lines which are neighbours
        for i in range(0, 2):
            line1 = self.lines[i]
            line2 = self.lines[i + 1]

            arctan1 = line1.atan2()
            arctan2 = line2.atan2()

            if Line.parallelDistanceArc(arctan1, arctan2) < math.pi / 10:
                # 2 lines which are opposite to the other
                self.probability = 0.9
                return

        # 2 lines which are neighbours
        # distance = abs(self.thetas[0] - self.thetas[1])
        # if distance > np.pi / 2:
        #     distance = np.pi - distance
        # if distance < math.pi / 10:
        #     self.probability = 0.9

        self.thetas.sort()

    def get_centroid(self) -> ():
        return self.__centroid

    def get_color(self) -> Color:
        return self.__color

    def set_color(self, color):
        self.__color = color

    def contour(self):
        return self.__contour

    def distanceWithBlock(self, block) -> float:
        return np.sqrt(pow(self.get_centroid()[0] - block.get_centroid()[0], 2) + pow(
            self.get_centroid()[1] - block.get_centroid()[1], 2))

    def distanceWithPoint(self, point) -> float:
        return np.sqrt(pow(self.get_centroid()[0] - point[0], 2) + pow(
            self.get_centroid()[1] - point[1], 2))


class LinkedGroup(object):

    def __init__(self, blockset, startblock) -> None:
        self.blocks = LinkedGroup.getLinkedBlocks(startblock)
        self.blockset = blockset

        blockset.linkedgroups.append(self)

    def __str__(self) -> str:
        content = 'group:\n'
        content += '( '
        for block in self.blocks:
            content += str(block.id)
            content += ' '
        content += ')'

        return content

    __repr__ = __str__

    def calPositionRange(self):
        minx = miny = 1000
        maxx = maxy = -1000
        for block in self.blocks:
            if block.position[0] < minx:
                minx = block.position[0]
            if block.position[0] > maxx:
                maxx = block.position[0]

            if block.position[1] < miny:
                miny = block.position[1]
            if block.position[1] > maxy:
                maxy = block.position[1]

        return (minx, miny), (maxx, maxy)

    def addToPosition(self, block, position):
        if block.position is None:
            block.position = position[:]
            pass
        elif block.position is not None:

            deltaX = position[0] - block.position[0]
            deltaY = position[1] - block.position[1]

            for updateblock in LinkedGroup.getLinkedBlocks(block):
                updateblock.position[0] += deltaX
                updateblock.position[1] += deltaY
                if updateblock in self.blockset.linkstartblocks:
                    self.blockset.linkstartblocks.remove(updateblock)

        # only to show in the picture
        self.blocks[0].links.append(block)
        block.links.append(self.blocks[0])

        # append this block into group
        self.blocks.append(block)

    def searchingPositions(self):
        positions = []

        # oldpositions = []
        # minx = miny = 1000
        # maxx = maxy = -1000
        # for block in self.blocks:
        #     oldpositions.append(block.position)
        #     if block.position[0] < minx:
        #         minx = block.position[0]
        #     if block.position[0] > maxx:
        #         maxx = block.position[0]
        #
        #     if block.position[1] < miny:
        #         miny = block.position[1]
        #     if block.position[1] > maxy:
        #         maxy = block.position[1]
        #
        # counter0 = [maxx - 2, maxy - 2]
        # counter1 = [minx + 2, miny + 2]

        mins, maxs = self.calPositionRange()
        counter0 = [maxs[0] - 2, maxs[1] - 2]
        counter1 = [mins[0] + 2, mins[1] + 2]

        oldpositions = []
        for block in self.blocks:
            oldpositions.append(block.position)

        for i in range(counter0[0], counter1[0] + 1):
            for j in range(counter0[1], counter1[1] + 1):
                if [i, j] not in oldpositions:
                    positions.append([i, j])
        return positions

    def positionCentroid(self, position):
        centroid = None
        number = len(self.blocks)
        for block in self.blocks:
            x, y = block.get_centroid()
            deltaX = position[0] - block.position[0]
            deltaY = position[1] - block.position[1]

            x += (self.blockset.crossvectors[0][0] * self.blockset.crossratio * deltaX)
            y += (self.blockset.crossvectors[0][1] * self.blockset.crossratio * deltaX)

            x += (self.blockset.crossvectors[1][0] * self.blockset.crossratio * deltaY)
            y += (self.blockset.crossvectors[1][1] * self.blockset.crossratio * deltaY)

            if centroid == None:
                centroid = [x, y]
            else:
                centroid[0] += x
                centroid[1] += y

        centroid[0] = int(round(centroid[0] / number))
        centroid[1] = int(round(centroid[1] / number))
        return centroid

    @staticmethod
    def getLinkedBlocks(original):
        blocks = [original]

        waitBlocks = [original]

        while len(waitBlocks) != 0:
            currBlock = waitBlocks.pop()
            for block in currBlock.links:
                if block not in blocks:
                    blocks.append(block)
                    waitBlocks.append(block)

        return blocks

    @staticmethod
    def calNextPosition(position, direction):
        if direction % 2 == 0:
            resultPosition = [position[0] + 1, position[1] + 0] if direction // 2 == 0 else [position[0] - 1,
                                                                                             position[1] + 0]
        else:
            resultPosition = [position[0] + 0, position[1] + 1] if direction // 2 == 0 else [position[0] + 0,
                                                                                             position[1] - 1]
        return resultPosition


class BlockSet(object):
    __angleThresh = np.pi / 12
    __areaThresh = 0.6

    def __init__(self, handler) -> None:
        self.framehandler = handler
        self.blocks = []  # type: list[Block]
        self.thetas = [0, 0]
        self.area = 0
        self.crossvectors = []
        self.crossratio = 1.32
        self.dic_neighbor2Axis = {}
        self.dic_neighbor2DiplomacyPosition = {}

        self.linkstartblocks = []  # type: list[Block]
        self.linkedgroups = []  # type:list[LinkedGroup]

        self.colordic = {}
        self.centerPos = None
        self.centerBlock = None  # type: Block
        self.legal = True
        self.face = None

    def __str__(self) -> str:
        content = '{ n = ' + str(len(self.blocks)) + ', thetas = (' + str(round(self.thetas[0], 3))
        ', ' + str(
            round(self.thetas[1], 3)) + '), area = ' + str(
            round(self.area, 3)) + '\n'
        content += 'blocks:\n'
        for block in self.blocks:
            content += str(block)
            content += '\n'
        content += str(self.crossvectors)
        content += '\n'
        content += ' ---end---'
        return content

    __repr__ = __str__

    def calPointColor(self, point):
        img = self.framehandler.getimg()
        # saka
        b = img.item(point[1], point[0], 0)
        g = img.item(point[1], point[0], 1)
        r = img.item(point[1], point[0], 2)
        # b,g,r = img[point[1], point[0]]
        color = Color.getColorByBGR((b, g, r))
        # print('point = ' + str(point) + ', bgr = ' + str((b, g, r)) + ", color = " + str(color))
        return color

    def groupOfBlock(self, block):
        for group in self.linkedgroups:
            if block in group.blocks:
                return group
        return None

    def link(self, fromBlock: Block, toBlock: Block, direction: int):
        if fromBlock.position is None and toBlock.position is None:
            self.linkstartblocks.append(fromBlock)
            fromBlock.position = [0, 0]
            toBlock.position = LinkedGroup.calNextPosition(fromBlock.position, direction)
        elif fromBlock.position is not None and toBlock.position is None:
            toBlock.position = LinkedGroup.calNextPosition(fromBlock.position, direction)
        elif fromBlock.position is None and toBlock.position is not None:
            fromBlock.position = LinkedGroup.calNextPosition(toBlock.position, (direction + 2) % 4)
        elif fromBlock.position is not None and toBlock.position is not None:
            newPosition = LinkedGroup.calNextPosition(fromBlock.position, direction)
            deltaX = newPosition[0] - toBlock.position[0]
            deltaY = newPosition[1] - toBlock.position[1]

            for updateblock in LinkedGroup.getLinkedBlocks(toBlock):
                updateblock.position[0] += deltaX
                updateblock.position[1] += deltaY
                if updateblock in self.linkstartblocks:
                    self.linkstartblocks.remove(updateblock)

        fromBlock.links.append(toBlock)
        toBlock.links.append(fromBlock)

    def add(self, block: Block) -> bool:
        if self.blocks.count(block) > 0:
            return

        if len(self.blocks) == 0:
            self.area = cv2.contourArea(block.contour())
            self.thetas = block.thetas[:]

            points = []
            for (point,) in block.contour():
                points.append(point)

            crossvec0 = util.divideList(
                util.listPlus(util.listPlus(points[1], points[0], False), util.listPlus(points[2], points[3], False)),
                2)
            crossvec1 = util.divideList(
                util.listPlus(util.listPlus(points[3], points[0], False), util.listPlus(points[2], points[1], False)),
                2)
            self.crossvectors.append(crossvec0)
            self.crossvectors.append(crossvec1)
            self.crossvectors.append(util.negativeList(crossvec0))
            self.crossvectors.append(util.negativeList(crossvec1))
        else:
            number = len(self.blocks)

            # calculate the avg area
            area = cv2.contourArea(block.contour())
            self.area = float(self.area * number + area) / (number + 1)

            distance00 = BlockSet.__absthetaDistance(self.thetas[0], block.thetas[0])
            distance11 = BlockSet.__absthetaDistance(self.thetas[1], block.thetas[1])
            distance01 = BlockSet.__absthetaDistance(self.thetas[0], block.thetas[1])
            distance10 = BlockSet.__absthetaDistance(self.thetas[1], block.thetas[0])

            if distance00 + distance11 < distance01 + distance10:
                pass
            else:
                block.thetas[0], block.thetas[1] = block.thetas[1], block.thetas[0]

            # calculate the avg thetas
            self.thetas[0] = BlockSet.__avgTheta(self.thetas[0], block.thetas[0], number)
            self.thetas[1] = BlockSet.__avgTheta(self.thetas[1], block.thetas[1], number)

            # calculate the avg cross vectors

            points = []
            for (point,) in block.contour():
                points.append(point)

            crossvec0 = util.divideList(
                util.listPlus(util.listPlus(points[1], points[0], False), util.listPlus(points[2], points[3], False)),
                2)
            crossvec1 = util.divideList(
                util.listPlus(util.listPlus(points[3], points[0], False), util.listPlus(points[2], points[1], False)),
                2)

            crossvecs = [crossvec0, crossvec1]
            minindex = [0, 0]
            # for i in range(2):
            #     mindistance = 100000000
            #     for avgvec in self.crossvectors:
            #         distance = pow(avgvec[0] - crossvecs[i][0], 2) + pow(avgvec[1] - crossvecs[i][1], 2)
            #         if distance < mindistance:
            #             mindistance = distance
            #             minindex[i] = self.crossvectors.index(avgvec)

            if block.id == 33:
                aaa = 1

            for i in range(2):

                minangledistance = 4  # it should be big enough
                for avgvec in self.crossvectors:
                    arctan1 = math.atan2(avgvec[1], avgvec[0])
                    arctan2 = math.atan2(crossvecs[i][1], crossvecs[i][0])
                    absangledistance = abs(arctan1 - arctan2)
                    if absangledistance > np.pi:
                        absangledistance = np.pi * 2 - absangledistance
                    if absangledistance < minangledistance:
                        for j in range(i):
                            pass
                        minangledistance = absangledistance
                        minindex[i] = self.crossvectors.index(avgvec)

            finalcrossvec = [None, None]

            for i in range(2):
                if minindex[i] == 0:
                    finalcrossvec[0] = crossvecs[i][:]
                elif minindex[i] == 1:
                    finalcrossvec[1] = crossvecs[i][:]
                elif minindex[i] == 2:
                    finalcrossvec[0] = [-crossvecs[i][0], -crossvecs[i][1]]
                elif minindex[i] == 3:
                    finalcrossvec[1] = [-crossvecs[i][0], -crossvecs[i][1]]

            if finalcrossvec[0] is None or finalcrossvec[1] is None:
                return False

            for i in range(2):
                self.crossvectors[i][0] = float(self.crossvectors[i][0] * number + finalcrossvec[i][0]) / (number + 1)
                self.crossvectors[i][1] = float(self.crossvectors[i][1] * number + finalcrossvec[i][1]) / (number + 1)

            self.crossvectors[2] = [-self.crossvectors[0][0], -self.crossvectors[0][1]]
            self.crossvectors[3] = [-self.crossvectors[1][0], -self.crossvectors[1][1]]

        if block.id == 42 or block.id == 43 or block.id == 44 or block.id == 31 or block.id == 33 or block.id == 35:
            aaa = 1

        self.blocks.append(block)
        return True

    def isLegalBlock(self, block) -> bool:
        result = False

        # print(' ---isLegalBlock---')
        # print(self)
        # print(block)
        # if len(block.thetas) != 2:
        #     print('result = ' + str(result))
        #     print(' ---isLegalBlock end---')

        distance0, distance1 = BlockSet.__distanceOfThetas(self.thetas, block.thetas)

        angleThresh = BlockSet.__angleThresh
        areaThresh = BlockSet.__areaThresh

        if distance0 < angleThresh and distance1 < angleThresh:
            area1 = self.area
            area2 = cv2.contourArea(block.contour())
            ratio = abs(area1 - area2) / max(area1, area2)
            if ratio < areaThresh:
                result = True
            else:
                result = False
        else:
            result = False

        # print('result = ' + str(result))
        # print(' ---isLegalBlock end---')

        return result

    def getCrossPoints(self, block: Block):
        crosspoints = []
        ratio = self.crossratio
        for crossvector in self.crossvectors:
            crosspoint = (
                block.get_centroid()[0] + crossvector[0] * ratio, block.get_centroid()[1] + crossvector[1] * ratio)
            crosspoints.append(crosspoint)
        return crosspoints

    def getNearestBlock(self, point, block):
        minDistance = 100000000
        nearestblock = None
        for block2 in self.blocks:
            if block is block2:
                continue

            distance = pow(block2.get_centroid()[0] - point[0], 2) + pow(block2.get_centroid()[1] - point[1], 2)
            if distance < minDistance:
                minDistance = distance
                nearestblock = block2

        return nearestblock

    def isLegalNearBlock(self, nearestblock, crosspoint, block) -> bool:
        if not nearestblock.inBlock(crosspoint):
            return False
        # x1, y1 = nearestblock.get_centroid()
        # x2, y2 = block.get_centroid()
        # line = Line(x1, y1, x2, y2)
        # theta = line.getTheta()
        #
        # thetadistance1 = BlockSet.__thetaDistance(theta, self.thetas[0])
        # thetadistance2 = BlockSet.__thetaDistance(theta, self.thetas[1])
        #
        # if abs(thetadistance1) > BlockSet.__angleThresh and abs(thetadistance2) > BlockSet.__angleThresh:
        #     # the theta is not similar to all the 2 thetas
        #     return False
        return True

    @staticmethod
    def areSimularBlocks(block1: Block, block2: Block) -> bool:

        result = False

        # print(' ---areSimularBlocks---')
        # print(block1)
        # print(block2)
        # if len(block1.thetas) != 2 or len(block2.thetas) != 2:
        # result = False
        # print('result = ' + str(result))
        # print(' ---areSimularBlocks end---')

        distance0, distance1 = BlockSet.__distanceOfThetas(block1.thetas, block2.thetas)

        angleThresh = BlockSet.__angleThresh
        areaThresh = BlockSet.__areaThresh

        if distance0 < angleThresh and distance1 < angleThresh:
            area1 = cv2.contourArea(block1.contour())
            area2 = cv2.contourArea(block2.contour())
            ratio = abs(area1 - area2) / max(area1, area2)
            if ratio < areaThresh:
                result = True
            else:
                result = False
        else:
            result = False

        # print('result = ' + str(result))
        # print(' ---areSimularBlocks end---')

        return result

    @staticmethod
    def __avgTheta(avgtheta, newtheta, n) -> float:
        distance = BlockSet.__thetaDistance(newtheta, avgtheta)
        avg = avgtheta + float(distance) / (n + 1)
        return avg

    @staticmethod
    def __absthetaDistance(theta1, theta2) -> float:
        distance = abs(theta1 - theta2)
        if distance > np.pi / 2:
            distance = np.pi - distance
        return distance

    @staticmethod
    def __thetaDistance(theta1, theta2) -> float:
        if abs(theta1 - theta2) == np.pi / 2:
            return np.pi / 2
        if 0 <= theta1 <= np.pi / 2 and 0 <= theta2 <= np.pi / 2 or -np.pi / 2 <= theta1 <= 0 and -np.pi / 2 <= theta2 <= 0:
            return theta1 - theta2
        else:
            if -np.pi / 2 <= theta1 <= 0:
                theta1 += np.pi
            else:
                theta2 += np.pi
            distance = theta1 - theta2
            if distance > np.pi / 2:
                distance = distance - np.pi
            elif distance < -np.pi / 2:
                distance = distance + np.pi
            return distance

    @staticmethod
    def __thetaPlus(theta1, theta2) -> float:
        theta = theta1 + theta2
        if theta < -np.pi / 2:
            theta += np.pi
        elif theta > np.pi / 2:
            theta -= np.pi
        return theta

    @staticmethod
    def __distanceOfThetas(thetas1, thetas2):
        distance00 = BlockSet.__absthetaDistance(thetas1[0], thetas2[0])
        distance11 = BlockSet.__absthetaDistance(thetas1[1], thetas2[1])
        distance01 = BlockSet.__absthetaDistance(thetas1[0], thetas2[1])
        distance10 = BlockSet.__absthetaDistance(thetas1[1], thetas2[0])

        if distance00 + distance11 < distance01 + distance10:
            return distance00, distance11
        else:
            return distance01, distance10


class BlockLinker(object):

    def __init__(self, blocks, handler) -> None:
        self.blocks = blocks
        self.sets = []  # type: 'list[BlockSet]'
        self.legalSets = []  # type: 'list[BlockSet]'
        self.faces = []  # type: 'list[CubeManager.FaceData]'
        self.framehandler = handler

    def excute(self):
        # divide the blocks into several sets
        for block in self.blocks:
            if self.__inSets(block):
                continue
            index = self.blocks.index(block)
            for block2 in self.blocks[index + 1:]:
                if self.__inSets(block2):
                    continue
                else:
                    if self.__inSets(block):
                        # block in sets
                        blockset = self.__setOfBlock(block)
                        isLegal = blockset.isLegalBlock(block2)

                        if isLegal:
                            blockset.add(block2)
                    else:
                        # block not in sets
                        isSimulate = BlockSet.areSimularBlocks(block, block2)

                        if isSimulate:
                            # new a set and put the blocks in it
                            blockset = BlockSet(self.framehandler)
                            blockset.add(block)
                            blockset.add(block2)
                            self.sets.append(blockset)

        # legal?
        if len(self.sets) < 2:
            print("len(self.sets) < 2")
            return
        else:
            allLackBlocks = True
            for set in self.sets:
                if len(set.blocks) > 3:
                    allLackBlocks = False
            if allLackBlocks:
                print("allLackBlocks = True")
                return

        # link the blocks of each set
        for set in self.sets:
            for block in set.blocks:

                # get 4 cross points
                crosspoints = set.getCrossPoints(block)
                for crosspoint in crosspoints:

                    # find the nearest block to the cross point
                    nearestblock = set.getNearestBlock(crosspoint, block)

                    if nearestblock is None or block.isLinkedWith(nearestblock, set):
                        continue
                    else:
                        # adjust if it is legal
                        if set.isLegalNearBlock(nearestblock, crosspoint, block):
                            # block.linkTo(nearestblock, crosspoints.index(crosspoint))
                            set.link(block, nearestblock, crosspoints.index(crosspoint))

        # calculate linked groups
        for set in self.sets:
            for startblock in set.linkstartblocks:
                group = LinkedGroup(set, startblock)
                # set.linkedgroups.append(group)

        # link the other block into the group
        for set in self.sets:
            for group in set.linkedgroups:
                for position in group.searchingPositions():
                    for otherblock in set.blocks:
                        if otherblock in group.blocks:
                            continue

                        point = group.positionCentroid(position)
                        if otherblock.inBlock(point):
                            deletingGroup = set.groupOfBlock(otherblock)
                            if deletingGroup is not None:
                                set.linkedgroups.remove(deletingGroup)
                            group.addToPosition(otherblock, position)

        for set in self.sets:
            for block in set.blocks:
                if block.position is None:
                    set.blocks.remove(block)

        # each set should only have 1 group now

        # make the positions lie in (0,0) ~ (2,2)
        for set in self.sets:
            if len(set.linkedgroups) != 1:
                set.legal = False
                print('groups over 1')
                continue

            group = set.linkedgroups[0]
            minx, miny = group.calPositionRange()[0]
            deltaX = - minx
            deltaY = - miny
            for updateblock in set.blocks:
                updateblock.position[0] += deltaX
                updateblock.position[1] += deltaY

        # calculate the accurate color or each block
        img = self.framehandler.getimg()
        height, width = img.shape[0:2]
        for set in self.sets:
            for block in self.blocks:
                mask = np.zeros((height, width), np.uint8)
                cv2.drawContours(mask, [block.contour()], 0, 255, -1)
                mean_color = cv2.mean(img, mask=mask)
                round_color = (round(mean_color[0]), round(mean_color[1]), round(mean_color[2]))
                block.set_color(Color.getColorByBGR(round_color))
                pass

        # record the color of each block into the colordic
        for set in self.sets:
            if len(set.linkedgroups) != 1:
                continue

            for block in set.linkedgroups[0].blocks:
                position_tuple = (block.position[0], block.position[1])
                set.colordic[position_tuple] = block.get_color()

        # search the colored-area of the magic cube's which is not a block and set the color
        for set in self.sets:
            if len(set.linkedgroups) != 1:
                continue

            group = set.linkedgroups[0]

            # search only those group whose positions lies in 3*3 already
            mins, maxs = group.calPositionRange()
            if maxs[0] - mins[0] + 1 == 3 and maxs[1] - mins[1] + 1 == 3:

                set.centerPos = (mins[0] + 1, mins[1] + 1)
                for position in group.searchingPositions():
                    point = group.positionCentroid(position)
                    color = set.calPointColor(point)
                    if color is not None:
                        position_tuple = (position[0], position[1])
                        set.colordic[position_tuple] = color
                        print(position_tuple)
            else:
                # these sets are not legal
                set.legal = False

        # make sure all the set have accurate center
        for set in self.sets:
            if set.legal:
                hascenter = False

                for position in set.colordic.keys():
                    if position == set.centerPos:
                        hascenter = True
                        break
                if not hascenter:
                    set.legal = False
                if set.legal:
                    self.legalSets.append(set)

        # search each sets' crossvectors and find there common directions
        minangledistance = 15 / 180 * math.pi
        for i, set in enumerate(self.legalSets):
            for set2 in self.legalSets[i + 1:]:

                mindistance = 10
                opposite = True
                minindex1 = -1
                minindex2 = -1

                for index1, crossvector1 in enumerate(set.crossvectors[0:2]):
                    for index2, crossvector2 in enumerate(set2.crossvectors[0:2]):
                        arctan1 = math.atan2(crossvector1[1], crossvector1[0])
                        arctan2 = math.atan2(crossvector2[1], crossvector2[0])

                        if abs(arctan1 - arctan2) < mindistance:
                            mindistance = abs(arctan1 - arctan2)
                            minindex1 = index1
                            minindex2 = index2
                            opposite = True

                        if abs(math.pi - abs(arctan1 - arctan2)) < mindistance:
                            mindistance = abs(math.pi - abs(arctan1 - arctan2))
                            minindex1 = index1
                            minindex2 = index2
                            opposite = False

                        if abs(arctan1 - arctan2) < minangledistance:
                            # thses 2 directions are the same
                            set.dic_neighbor2Axis[set2] = (index1, True)
                            set2.dic_neighbor2Axis[set] = (index2, True)

                        elif math.pi - abs(arctan1 - arctan2) < minangledistance:
                            # these 2 directions are opposite
                            set.dic_neighbor2Axis[set2] = (index1, True)
                            set2.dic_neighbor2Axis[set] = (index2, False)
                set.dic_neighbor2Axis[set2] = (minindex1, True)
                set2.dic_neighbor2Axis[set] = (minindex2, opposite)

        # cal dic_neighbor2DiplomaticPosition
        for index, set in enumerate(self.legalSets):
            for set2 in self.legalSets[index + 1:]:

                aaa = 1

                if set2 in set.dic_neighbor2Axis.keys():

                    for turn in range(0, 2):
                        if turn == 0:
                            s1 = set
                            s2 = set2
                        else:
                            s1 = set2
                            s2 = set

                        oppositeAxis = 1 if s1.dic_neighbor2Axis[s2][0] == 0 else 0
                        # centerPos1 = s1.centerBlock.position
                        centerPos1 = s1.centerPos
                        guessPositions = [None, None]
                        guessPoints = [None, None]
                        if oppositeAxis == 0:
                            guessPositions[0] = (centerPos1[0] + 1, centerPos1[1])
                            guessPositions[1] = (centerPos1[0] - 1, centerPos1[1])
                        elif oppositeAxis == 1:
                            guessPositions[0] = (centerPos1[0], centerPos1[1] + 1)
                            guessPositions[1] = (centerPos1[0], centerPos1[1] - 1)

                        # centerPoint1 = s1.centerBlock.get_centroid()
                        centerPoint1 = s1.linkedgroups[0].positionCentroid(s1.centerPos)
                        guessPoints[0] = (centerPoint1[0] + s1.crossvectors[oppositeAxis][0] * s1.crossratio,
                                          centerPoint1[1] + s1.crossvectors[oppositeAxis][1] * s1.crossratio)
                        guessPoints[1] = (centerPoint1[0] - s1.crossvectors[oppositeAxis][0] * s1.crossratio,
                                          centerPoint1[1] - s1.crossvectors[oppositeAxis][1] * s1.crossratio)
                        # centerPoint2 = s2.centerBlock.get_centroid()
                        centerPoint2 = s2.linkedgroups[0].positionCentroid(s2.centerPos)

                        distances = [None, None]
                        for i in range(0, 2):
                            distances[i] = (guessPoints[i][0] - centerPoint2[0]) * (
                                    guessPoints[i][0] - centerPoint2[0]) + (
                                                   guessPoints[i][1] - centerPoint2[1]) * (
                                                   guessPoints[i][1] - centerPoint2[1])
                        if distances[0] < distances[1]:
                            s1.dic_neighbor2DiplomacyPosition[s2] = guessPositions[0]
                        else:
                            s1.dic_neighbor2DiplomacyPosition[s2] = guessPositions[1]

    def generateFaceDatas(self):

        # create faces
        for set in self.legalSets:
            face = CubeManager.FaceData(set.colordic)  # type: CubeManager.FaceData
            set.face = face
            self.faces.append(face)

        # set the neighbors
        for index, set in enumerate(self.legalSets):
            for neighborSet in set.dic_neighbor2DiplomacyPosition.keys():
                diplomacyPosition = set.dic_neighbor2DiplomacyPosition[neighborSet]

                # set.face.dic_neighbor2diplomacy[neighborSet.face] = tuple(reversed(diplomacyPosition))

                set.face.setNeighbor2Diplomacy(neighborSet.face, diplomacyPosition)
                set.face.setNeighbor2Parallel(neighborSet.face, True if set.dic_neighbor2Axis[neighborSet][1] ==
                                                                        neighborSet.dic_neighbor2Axis[set][
                                                                            1] else False)

        print('faces:')
        for face in self.faces:
            print(face)

    def print(self):
        print('\n\n\n ---finished link---')
        print(self.sets)
        print('len(sets) = ' + str(len(self.sets)))
        print('len(legalsets) = ' + str(len(self.legalSets)))

        # print dic
        print('dic_neighbor2Axis')
        for index, set in enumerate(self.legalSets):
            outputstr = 'set ' + str(index)
            for neighborset in set.dic_neighbor2Axis.keys():
                outputstr += '   '
                outputstr += str(self.legalSets.index(neighborset)) + ': ' + str(set.dic_neighbor2Axis[neighborset])
            print(outputstr)

        print('dic_neighbor2DiplomacyPosition')
        for set in self.legalSets:
            outputstr = 'set '
            for neighborset in set.dic_neighbor2DiplomacyPosition.keys():
                outputstr += '   '
                outputstr += str(self.legalSets.index(neighborset)) + ': ' + str(
                    set.dic_neighbor2DiplomacyPosition[neighborset])
            print(outputstr)

        for set in self.sets:
            for group in set.linkedgroups:
                print(group)

    def __inSets(self, block) -> bool:
        if len(self.sets) == 0:
            return False

        for set in self.sets:
            if set.blocks.count(block) > 0:
                return True
        return False

    def __setOfBlock(self, block) -> BlockSet:
        if len(self.sets) == 0:
            return None

        for set in self.sets:
            if set.blocks.count(block) > 0:
                return set
        return None

    def __shortestDistanceList(self, block, n) -> [Block]:
        result = []
        centroid = block.get_centroid()

        list1 = []
        for block2 in self.blocks:
            list1.append([block2, centroid])

        list1.sort(key=BlockLinker.__key_distance)

        for item in list1[1:n + 1]:
            result.append(item[0])

        # print("block: " + str(block.get_centroid()))
        # x0, y0 = block.get_centroid()
        # for block2 in result:
        #     x1, y1 = block2.get_centroid()
        #     print(str((x1, y1)), ", ", str((x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1)))

        return result

    @staticmethod
    def __key_distance(item):
        x0, y0 = item[1]
        x1, y1 = item[0].get_centroid()
        return (x0 - x1) * (x0 - x1) + (y0 - y1) * (y0 - y1)


class CubeManager(object):
    colorlinksdic = {}
    colorlinksdic[Color.WHITE] = (Color.ORANGE, Color.BLUE, Color.RED, Color.GREEN)
    colorlinksdic[Color.RED] = (Color.WHITE, Color.BLUE, Color.YELLOW, Color.GREEN)
    colorlinksdic[Color.BLUE] = (Color.WHITE, Color.ORANGE, Color.YELLOW, Color.RED)
    colorlinksdic[Color.ORANGE] = (Color.WHITE, Color.GREEN, Color.YELLOW, Color.BLUE)
    colorlinksdic[Color.GREEN] = (Color.WHITE, Color.RED, Color.YELLOW, Color.ORANGE)
    colorlinksdic[Color.YELLOW] = (Color.RED, Color.BLUE, Color.ORANGE, Color.GREEN)

    outerRingPositions = (
        (1, 0), (2, 0),
        (2, 1), (2, 2),
        (1, 2), (0, 2),
        (0, 1), (0, 0)
    )

    class Cube(object):
        def __init__(self, colors) -> None:
            self.colordic = {}

            for color in colors:
                # self.colordic[color] = Color.NONE
                self.colordic[color] = None

        def __str__(self) -> str:
            content = '( ';
            for color in self.colordic.keys():
                content += Color.names[color] + " "
            content += ')'
            return content

        def refresh(self):
            if len(self.colordic.keys()) == 1:
                for color in self.colordic.keys():
                    self.colordic[color] = color
            else:
                for color in self.colordic.keys():
                    # self.colordic[color] = Color.NONE
                    self.colordic[color] = None

    class FaceData(object):
        def __init__(self, dic_position2color) -> None:
            self.points = [[None, None, None], [None, None, None], [None, None, None]]
            # opencv's contour is counterclockwise, so here the x and y axix should exchange
            for position in dic_position2color.keys():
                self.points[position[1]][position[0]] = dic_position2color[position]

            self.dic_neighbor2diplomacy = {}  # type: "{CubeManager.FaceData: (int, int)}"
            self.dic_neighbor2Parallel = {}  # type: dict{CubeManager.FaceData: bool}

            print(self.points)

        def __str__(self) -> str:
            strcontent = 'centercolor: ' + Color.names[self.points[1][1]] + '\n'
            for y in range(0, 3):
                for x in range(0, 3):
                    strcontent += 'None' if self.points[x][y] is None else Color.names[self.points[x][y]]
                    strcontent += '  '
                strcontent += '\n'
            for neighborFace in self.dic_neighbor2diplomacy.keys():
                strcontent += Color.names[neighborFace.centerColor()] + ': ' + str(
                    self.dic_neighbor2diplomacy[neighborFace]) if self.dic_neighbor2diplomacy[
                                                                      neighborFace] is not None else 'None'
                strcontent += str(
                    self.dic_neighbor2Parallel[neighborFace]) if self.dic_neighbor2Parallel[
                                                                     neighborFace] is not None else 'None' + '\n'
            strcontent += '\n'
            return strcontent

        def centerColor(self):
            return self.points[1][1]

        def setNeighbor2Diplomacy(self, neighborFace, diplomacyPosition):
            # opencv's contour is counterclockwise, so here the x and y axix should exchange
            self.dic_neighbor2diplomacy[neighborFace] = tuple(reversed(diplomacyPosition))

        def setNeighbor2Parallel(self, neighborFace, parallel):
            self.dic_neighbor2Parallel[neighborFace] = parallel

        __repr__ = __str__

    def __init__(self) -> None:
        self.w_mutex = threading.Lock()
        self.r_mutex = threading.Lock()

        self.__handlers = []
        self.__colors = []
        self.__colors_hsv = {int: []}

        self.cubedic = {}
        self.cubes = set()

        # # white
        # self.set_color(Color.WHITE, (0, 0, 160), (180, 70, 255))
        # # blue
        # self.set_color(Color.BLUE, (90, 100, 100), (124, 255, 255))
        # # red
        # self.set_color(Color.RED, (156, 100, 100), (180, 255, 255))
        # self.set_color(Color.RED, (0, 100, 85), (3, 200, 255))
        # # orange
        # # cubemanager.set_color(Color.ORANGE, (0, 120, 100), (12, 255, 255))
        # # self.set_color(Color.ORANGE, (1, 100, 100), (6, 120, 120))
        # self.set_color(Color.ORANGE, (7, 120, 100), (12, 255, 255))
        # # green
        # self.set_color(Color.GREEN, (45, 100, 100), (80, 255, 255))
        # # yellow
        # self.set_color(Color.YELLOW, (13, 71, 100), (44, 255, 255))

        # white
        self.set_color(Color.WHITE, (0, 0, 160), (180, 70, 255))
        # blue
        self.set_color(Color.BLUE, (90, 100, 100), (124, 255, 255))
        # red # orange
        self.set_color(Color.RED, (156, 100, 100), (180, 255, 255))
        self.set_color(Color.ORANGE, (0, 100, 100), (12, 255, 255))
        # green
        self.set_color(Color.GREEN, (45, 100, 100), (80, 255, 255))
        # yellow
        self.set_color(Color.YELLOW, (13, 71, 100), (44, 255, 255))

        self.__init()

    # def __CubeDic(self, colorset, cube):
    #     l = list(colorset)
    #     l.sort()
    #     t = tuple(l)

    def __init(self):
        # init the cubes and the dic
        for centerColor in CubeManager.colorlinksdic.keys():

            # add the center cube
            colorSet = {centerColor}
            centerCube = CubeManager.Cube(colorSet)
            centerCube.colordic[centerColor] = centerColor
            self.cubes.add(centerCube)
            self.cubedic[CubeManager.__getTuple(colorSet)] = centerCube

            for nearColor in CubeManager.colorlinksdic[centerColor]:
                # add the edge cube
                colorSet = {centerColor, nearColor}
                if CubeManager.__getTuple(colorSet) not in self.cubedic.keys():
                    edgeCube = CubeManager.Cube(colorSet)
                    self.cubes.add(edgeCube)
                    self.cubedic[CubeManager.__getTuple(colorSet)] = edgeCube

            for nearColor in CubeManager.colorlinksdic[centerColor]:
                for nearColor2 in set(CubeManager.colorlinksdic[centerColor]) - {nearColor}:
                    # add the corner cube

                    # all the 3 cubes are neighbours
                    if nearColor in CubeManager.colorlinksdic[nearColor2]:
                        colorSet = {centerColor, nearColor, nearColor2}
                        if CubeManager.__getTuple(colorSet) not in self.cubedic.keys():
                            cornerCube = CubeManager.Cube(colorSet)
                            self.cubes.add(cornerCube)
                            self.cubedic[CubeManager.__getTuple(colorSet)] = cornerCube

    def inputFaces(self, faces: "[FaceData]"):
        remainFaces = set(faces)
        for face in faces:
            if face in remainFaces:
                if face.centerColor() == None:
                    continue

                # the face is single
                if len(face.dic_neighbor2diplomacy.keys()) == 0:
                    ret = self.inputSingleFace(face)

                    pass
                else:
                    for face2 in face.dic_neighbor2diplomacy.keys():
                        ret = self.adjustFace(face, face2)
                        if ret:
                            self.inputFace(face, face2)

                remainFaces.remove(face)

    def update_cubedatas(self, newdatas):

        # lock
        self.w_mutex.acquire()
        for subData in newdatas:
            data = subData['data']
            center_color = subData['center_color']

            # CubeManager内表示色块颜色未知用的是None，不能用Color.NONE = 6
            for colors in data:
                for i in range(3):
                    if colors[i] == Color.NONE:
                        colors[i] = None

            neighborsColors = CubeManager.colorlinksdic[center_color]

            self.getCube({center_color, neighborsColors[3], neighborsColors[0]}).colordic[center_color] = data[0][0]
            self.getCube({center_color, neighborsColors[0]}).colordic[center_color] = data[0][1]
            self.getCube({center_color, neighborsColors[0], neighborsColors[1]}).colordic[center_color] = data[0][2]

            self.getCube({center_color, neighborsColors[3]}).colordic[center_color] = data[1][0]
            self.getCube({center_color}).colordic[center_color] = data[1][1]
            self.getCube({center_color, neighborsColors[1]}).colordic[center_color] = data[1][2]

            self.getCube({center_color, neighborsColors[3], neighborsColors[2]}).colordic[center_color] = data[2][0]
            self.getCube({center_color, neighborsColors[2]}).colordic[center_color] = data[2][1]
            self.getCube({center_color, neighborsColors[2], neighborsColors[1]}).colordic[center_color] = data[2][2]

        self.w_mutex.release()

    def refresh_cubedatas(self):
        # lock
        self.w_mutex.acquire()
        for cube in self.cubes:
            cube.refresh()
        self.w_mutex.release()

    def getCurrentCubeData(self):
        faces = []

        # lock
        self.w_mutex.acquire()
        for color in CubeManager.colorlinksdic.keys():
            data = [[6, 6, 6], [6, 6, 6], [6, 6, 6]]
            face = {'center_color': color, 'data': data}
            faces.append(face)

            neighborsColors = CubeManager.colorlinksdic[color]

            data[0][0] = self.getCube({color, neighborsColors[3], neighborsColors[0]}).colordic[color]
            data[0][1] = self.getCube({color, neighborsColors[0]}).colordic[color]
            data[0][2] = self.getCube({color, neighborsColors[0], neighborsColors[1]}).colordic[color]

            data[1][0] = self.getCube({color, neighborsColors[3]}).colordic[color]
            data[1][1] = self.getCube({color}).colordic[color]
            data[1][2] = self.getCube({color, neighborsColors[1]}).colordic[color]

            data[2][0] = self.getCube({color, neighborsColors[3], neighborsColors[2]}).colordic[color]
            data[2][1] = self.getCube({color, neighborsColors[2]}).colordic[color]
            data[2][2] = self.getCube({color, neighborsColors[2], neighborsColors[1]}).colordic[color]

        self.w_mutex.release()
        print(faces)
        return faces

    def inputSingleFace(self, face: FaceData):

        outerRingPositions = CubeManager.outerRingPositions[:]
        faceCenterColor = face.centerColor()

        totalNones = []
        totalConflicts = []
        totalBingos = []

        noConflictColor = 0
        noConflictIndex = 0

        # lock
        self.w_mutex.acquire()

        for index, neighborColor in enumerate(CubeManager.colorlinksdic[face.centerColor()]):

            neighborColors = CubeManager.getNeighborColors(face.centerColor(), neighborColor)

            totalNones.append(0)
            totalConflicts.append(0)
            totalBingos.append(0)

            for i in range(0, 4):
                cube1 = self.getCube({faceCenterColor, neighborColors[i]})
                position1 = outerRingPositions[i * 2]
                # cube1.colordic[faceCenterColor] = face.points[position1[0]][position1[1]]
                if cube1.colordic[faceCenterColor] is None:
                    totalNones[index] += 1
                elif cube1.colordic[faceCenterColor] != face.points[position1[0]][position1[1]]:
                    totalConflicts[index] += 1
                elif cube1.colordic[faceCenterColor] == face.points[position1[0]][position1[1]]:
                    totalBingos[index] += 1

                cube2 = self.getCube({faceCenterColor, neighborColors[i], neighborColors[i + 1 if i < 3 else 0]})
                position2 = outerRingPositions[i * 2 + 1]
                # cube2.colordic[faceCenterColor] = face.points[position2[0]][position2[1]]
                if cube2.colordic[faceCenterColor] is None:
                    totalNones[index] += 1
                elif cube2.colordic[faceCenterColor] != face.points[position2[0]][position2[1]]:
                    totalConflicts[index] += 1
                elif cube2.colordic[faceCenterColor] == face.points[position2[0]][position2[1]]:
                    totalBingos[index] += 1

            if totalConflicts[index] == 0:
                noConflictColor = neighborColor
                noConflictIndex = index

        self.w_mutex.release()

        noConflictCount = 0
        fullNoneCount = 0

        for i in range(0, 4):
            if totalConflicts[i] == 0:
                noConflictCount += 1
            if totalNones[i] == 8:
                fullNoneCount += 1

        if fullNoneCount > 0:
            # the cube's face is none
            return False
        elif noConflictCount > 1:
            # multiple choices
            return False
        elif noConflictCount == 0:
            # all conflicts
            return False
        elif totalBingos[noConflictIndex] < 2:
            # bingos count is too small
            return False

        # lock
        self.w_mutex.acquire()
        # only one choice and have at least 2 bingos
        neighborColors = CubeManager.getNeighborColors(face.centerColor(), noConflictColor)
        for i in range(0, 4):
            cube1 = self.getCube({faceCenterColor, neighborColors[i]})
            position1 = outerRingPositions[i * 2]
            cube1.colordic[faceCenterColor] = face.points[position1[0]][position1[1]]

            cube2 = self.getCube({faceCenterColor, neighborColors[i], neighborColors[i + 1 if i < 3 else 0]})
            position2 = outerRingPositions[i * 2 + 1]
            cube2.colordic[faceCenterColor] = face.points[position2[0]][position2[1]]
        self.w_mutex.release()
        return True

    def adjustFace(self, face: FaceData, firstNeighborFace: FaceData) -> bool:
        neighborColors = CubeManager.getNeighborColors(face.centerColor(), firstNeighborFace.centerColor())
        if neighborColors is None:
            return False

        outerRingPositions = CubeManager.getOuterRingPositions(face.dic_neighbor2diplomacy[firstNeighborFace])
        faceCenterColor = face.centerColor()

        conflicts = 0

        # lock
        self.w_mutex.acquire()

        for i in range(0, 4):
            cube1 = self.getCube({faceCenterColor, neighborColors[i]})
            position1 = outerRingPositions[i * 2]
            # cube1.colordic[faceCenterColor] = face.points[position1[0]][position1[1]]
            if cube1.colordic[faceCenterColor] is not None and cube1.colordic[faceCenterColor] != \
                    face.points[position1[0]][position1[1]]:
                conflicts += 1

            cube2 = self.getCube({faceCenterColor, neighborColors[i], neighborColors[i + 1 if i < 3 else 0]})
            position2 = outerRingPositions[i * 2 + 1]
            # cube2.colordic[faceCenterColor] = face.points[position2[0]][position2[1]]
            if cube2.colordic[faceCenterColor] is not None and cube2.colordic[faceCenterColor] != \
                    face.points[position2[0]][position2[1]]:
                conflicts += 1

        self.w_mutex.release()

        return True if conflicts == 0 else False

    def inputFace(self, face: FaceData, firstNeighborFace: FaceData):
        neighborColors = CubeManager.getNeighborColors(face.centerColor(), firstNeighborFace.centerColor())
        outerRingPositions = CubeManager.getOuterRingPositions(face.dic_neighbor2diplomacy[firstNeighborFace])
        faceCenterColor = face.centerColor()

        # lock
        self.w_mutex.acquire()

        for i in range(0, 4):
            cube1 = self.getCube({faceCenterColor, neighborColors[i]})
            position1 = outerRingPositions[i * 2]
            cube1.colordic[faceCenterColor] = face.points[position1[0]][position1[1]]

            cube2 = self.getCube({faceCenterColor, neighborColors[i], neighborColors[i + 1 if i < 3 else 0]})
            position2 = outerRingPositions[i * 2 + 1]
            cube2.colordic[faceCenterColor] = face.points[position2[0]][position2[1]]

        self.w_mutex.release()

    @staticmethod
    def getOuterRingPositions(startPosition):
        if tuple(startPosition) not in CubeManager.outerRingPositions:
            return None

        index = CubeManager.outerRingPositions.index(tuple(startPosition))
        outerRings = list(CubeManager.outerRingPositions[index:]) + list(CubeManager.outerRingPositions[0:index])

        return outerRings

    @staticmethod
    def getNeighborColors(centerColor, startColor):
        colorList = [startColor]
        neighbors = CubeManager.colorlinksdic[centerColor]
        if startColor not in neighbors:
            # error
            return None
        index = neighbors.index(startColor)
        for i in range(0, 3):
            if index == 3:
                index = 0
            else:
                index += 1
            nextColor = neighbors[index]
            colorList.append(nextColor)

        return colorList

    @staticmethod
    def __getTuple(colorSet):
        l = list(colorSet)
        l.sort()
        return tuple(l)

    def getCubes(self, colorSet: set):
        if len(colorSet) == 1:
            color = list(colorSet)[0]
            s = set()
            s.add(self.getCube(colorSet))
            for nearColor in CubeManager.colorlinksdic[color]:
                s.add(self.getCube({color, nearColor}))

                for nearColor2 in set(CubeManager.colorlinksdic[color]) - {nearColor}:
                    if nearColor in CubeManager.colorlinksdic[nearColor2]:
                        s.add(self.getCube({color, nearColor, nearColor2}))
            return s
        elif len(colorSet) == 2:
            colors = list(colorSet)
            s = set()
            s.add(self.getCube({colors[0], colors[1]}))

            for nearColor in set(CubeManager.colorlinksdic[colors[0]]) & set(CubeManager.colorlinksdic[colors[1]]):
                s.add(self.getCube({colors[0], colors[1], nearColor}))
            return s
        elif len(colorSet) == 3:
            return {self.getCube(colorSet)}

        return None

    def getCube(self, colorSet) -> Cube:
        if CubeManager.__getTuple(colorSet) in self.cubedic.keys():
            return self.cubedic[CubeManager.__getTuple(colorSet)]
        return None

    def showCubes(self):

        content0 = ''
        content1 = ''
        content2 = ''
        content3 = ''

        # lock
        self.w_mutex.acquire()

        for color in CubeManager.colorlinksdic.keys():
            neighborsColors = CubeManager.colorlinksdic[color]

            if color == Color.WHITE or color == Color.YELLOW:
                print('---- ' + Color.names[color] + ' ----')
                content = ''
                content += "%-8s" % ('None' if self.getCube({color, neighborsColors[3], neighborsColors[0]}).colordic[
                                                   color] is None else Color.names[
                    self.getCube({color, neighborsColors[3], neighborsColors[0]}).colordic[color]])
                content += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[0]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[0]}).colordic[color]])
                content += "%-8s\n" % ('None' if self.getCube({color, neighborsColors[0], neighborsColors[1]}).colordic[
                                                     color] is None else Color.names[
                    self.getCube({color, neighborsColors[0], neighborsColors[1]}).colordic[color]])

                content += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[3]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[3]}).colordic[color]])
                content += "%-8s" % ('None' if self.getCube({color}).colordic[color] is None else Color.names[
                    self.getCube({color}).colordic[color]])
                content += "%-8s\n" % (
                    'None' if self.getCube({color, neighborsColors[1]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[1]}).colordic[color]])

                content += "%-8s" % ('None' if self.getCube({color, neighborsColors[3], neighborsColors[2]}).colordic[
                                                   color] is None else Color.names[
                    self.getCube({color, neighborsColors[3], neighborsColors[2]}).colordic[color]])
                content += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[2]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[2]}).colordic[color]])
                content += "%-8s" % ('None' if self.getCube({color, neighborsColors[2], neighborsColors[1]}).colordic[
                                                   color] is None else Color.names[
                    self.getCube({color, neighborsColors[2], neighborsColors[1]}).colordic[color]])
                print(content)
            else:
                content0 += "%-27s" % ('---- ' + Color.names[color] + ' ----')

                content1 += "%-8s" % ('None' if self.getCube({color, neighborsColors[3], neighborsColors[0]}).colordic[
                                                    color] is None else Color.names[
                    self.getCube({color, neighborsColors[3], neighborsColors[0]}).colordic[color]])
                content1 += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[0]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[0]}).colordic[color]])
                content1 += "%-8s" % ('None' if self.getCube({color, neighborsColors[0], neighborsColors[1]}).colordic[
                                                    color] is None else Color.names[
                    self.getCube({color, neighborsColors[0], neighborsColors[1]}).colordic[color]])

                content2 += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[3]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[3]}).colordic[color]])
                content2 += "%-8s" % ('None' if self.getCube({color}).colordic[color] is None else Color.names[
                    self.getCube({color}).colordic[color]])
                content2 += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[1]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[1]}).colordic[color]])

                content3 += "%-8s" % ('None' if self.getCube({color, neighborsColors[3], neighborsColors[2]}).colordic[
                                                    color] is None else Color.names[
                    self.getCube({color, neighborsColors[3], neighborsColors[2]}).colordic[color]])
                content3 += "%-8s" % (
                    'None' if self.getCube({color, neighborsColors[2]}).colordic[color] is None else Color.names[
                        self.getCube({color, neighborsColors[2]}).colordic[color]])
                content3 += "%-8s" % ('None' if self.getCube({color, neighborsColors[2], neighborsColors[1]}).colordic[
                                                    color] is None else Color.names[
                    self.getCube({color, neighborsColors[2], neighborsColors[1]}).colordic[color]])

                if color == Color.GREEN:
                    print(content0)
                    print(content1)
                    print(content2)
                    print(content3)
                else:
                    content1 += ' | '
                    content2 += ' | '
                    content3 += ' | '

        self.w_mutex.release()

    def register_handler(self, handler):
        self.__handlers.append(handler)

    def set_color(self, color, hsv_min, hsv_max):
        if self.__colors.count(color) == 1:
            self.__colors_hsv[color].append((hsv_min, hsv_max))
        else:
            self.__colors.append(color)
            self.__colors_hsv[color] = [(hsv_min, hsv_max)]

    def colors(self) -> [int]:
        return self.__colors

    def hsvs(self, color: int) -> []:
        return self.__colors_hsv[color]


class FrameHandler(object):
    counter = 0

    def __init__(self, img, cubemanager: CubeManager):
        FrameHandler.counter += 1
        self.cubemanager = cubemanager
        cubemanager.register_handler(self)
        self.__img = img
        self.__height, self.__width, self.__channels = img.shape
        self.__img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        self.__color_mask_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        # self.__color_mask_kernel = np.ones((5, 5), np.uint8)

        self.__masks_color = {}
        self.__imgs_color = {}
        self.blocks = []

        for color in self.cubemanager.colors():
            hsvs = self.cubemanager.hsvs(color)
            self.__set_color(color, hsvs)

        self.blocklinker = None  # type: BlockLinker

    def getimg(self):
        return self.__img

    def __set_color(self, color, hsvs):
        hsv_min, hsv_max = hsvs[0]
        mask = cv2.inRange(self.__img_hsv, hsv_min, hsv_max)

        if len(hsvs) > 1:
            for (hsv_min, hsv_max) in hsvs[1:]:
                mask2 = cv2.inRange(self.__img_hsv, hsv_min, hsv_max)
                mask = cv2.bitwise_or(mask, mask2)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.__color_mask_kernel)
        img = cv2.bitwise_and(self.__img, self.__img, mask=mask)
        self.__masks_color[color] = mask
        self.__imgs_color[color] = img

        # cv2.imshow(Color.names[color], mask)

    def mix_masks(self):
        color = self.cubemanager.colors()[0]
        # mask = np.zeros((self.__height, self.__width), np.uint8)
        mask = self.__masks_color[color].copy()
        for color2 in self.cubemanager.colors()[1:]:
            mask2 = self.__masks_color[color2].copy()
            mask = cv2.bitwise_or(mask, mask2)

        return mask

    def show_img_color(self, color):
        cv2.imshow(str(color), self.__imgs_color[color])

    def excute(self):
        # calculate all the legal blocks in the frame
        for i in range(0, 6):
            if i in self.__masks_color.keys():
                self.__cal_blocks(i)

        # calculate colors
        # for block in self.blocks:
        #     mask = np.zeros(self.__img.shape, np.uint8)
        #     cv2.drawContours(mask, [block.contour()], 0, 255, -1)
        #     mean_val = cv2.mean(self.__img, mask=mask)

        # link the blocks
        self.blockLinker = BlockLinker(self.blocks, self)
        self.blockLinker.excute()

        self.blockLinker.generateFaceDatas()
        self.cubemanager.inputFaces(self.blockLinker.faces)

        # self.cubemanager.showCubes()
        # self.blockLinker.print()

    def __cal_blocks(self, color):
        mask = self.__masks_color[color]
        mask, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        area_min = self.__height * self.__width // 3000

        cnts = []
        img_color = self.__imgs_color[color]

        for cnt in contours:
            area = cv2.contourArea(cnt)

            # make sure the contour is not too small
            if area > area_min:
                # approximate the contour
                epsilon = 0.01 * cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, epsilon, True)

                # make sure the contour has just a few points
                if len(cnt) <= 25:
                    epsilon = 0.045 * cv2.arcLength(cnt, True)
                    cnt = cv2.approxPolyDP(cnt, epsilon, True)
                    cnt = cv2.approxPolyDP(cnt, epsilon, True)

                    # cv2.drawContours(img_color, [cnt], 0, (50, 50, 50), 1)

                    ''' make sure the solidity is nearly 1'''
                    ''' solidity = contour area / convex hull area'''
                    area = cv2.contourArea(cnt)
                    area_hull = cv2.contourArea(cv2.convexHull(cnt))
                    if area_hull != 0 and float(area) / area_hull >= 0.95:
                        cnts.append(cnt)
                        block = Block(cnt, color)
                        if block.id == 27:
                            aaa = 1
                        if block.probability == 1:
                            self.__append_block(block)
                            # print("cnt: " + str(len(cnt)) + ', ' + str(len(cnt)) + ', solidity = ' + str(
                            #     float(cv2.contourArea(cnt)) / cv2.contourArea(cv2.convexHull(cnt))))
                            # cv2.circle(img_color, block.get_centroid(), 2, (0, 0, 255), -1)

        # cv2.drawContours(img_color, cnts, -1, (0, 255, 0), 1)
        # cv2.imshow('contour:  ' + Color.names[color], img_color)

    def __append_block(self, block):
        self.blocks.append(block)
