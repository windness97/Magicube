import cv2
# from MagicCube.items.cube_manager import CubeManager, Color, FrameHandler
import time

from MagicCube.items.cube_manager import *
from MagicCube.utils import util

cubemanager = CubeManager()

dic_pos2color1 = {
    (0, 0): Color.RED,
    (1, 0): Color.YELLOW,
    (2, 0): Color.WHITE,

    (0, 1): Color.ORANGE,
    (1, 1): Color.RED,
    (2, 1): Color.WHITE,

    (0, 2): Color.WHITE,
    (1, 2): Color.YELLOW,
    (2, 2): Color.BLUE,
}

dic_pos2color2 = {
    (0, 0): None,
    (1, 0): Color.GREEN,
    (2, 0): None,

    (0, 1): Color.ORANGE,
    (1, 1): Color.YELLOW,
    (2, 1): Color.ORANGE,

    (0, 2): None,
    (1, 2): None,
    (2, 2): None,
}

dic_pos2color22 = {
    (0, 0): Color.ORANGE,
    (1, 0): Color.RED,
    (2, 0): Color.ORANGE,

    (0, 1): Color.WHITE,
    (1, 1): Color.WHITE,
    (2, 1): Color.WHITE,

    (0, 2): Color.ORANGE,
    (1, 2): Color.ORANGE,
    (2, 2): Color.ORANGE,
}

dic_pos2color3 = {
    (0, 0): Color.BLUE,
    (1, 0): Color.BLUE,
    (2, 0): Color.BLUE,

    (0, 1): Color.BLUE,
    (1, 1): Color.BLUE,
    (2, 1): Color.BLUE,

    (0, 2): Color.BLUE,
    (1, 2): Color.BLUE,
    (2, 2): Color.BLUE,
}

face = CubeManager.FaceData(dic_pos2color1)
face2 = CubeManager.FaceData(dic_pos2color2)
face22 = CubeManager.FaceData(dic_pos2color22)
face3 = CubeManager.FaceData(dic_pos2color3)

face.setNeighbor2Diplomacy(face2, (2, 1))
face2.setNeighbor2Diplomacy(face, (0, 1))

face.setNeighbor2Parallel(face2, True)
face2.setNeighbor2Parallel(face, True)

face22.setNeighbor2Diplomacy(face3, (0, 1))
face3.setNeighbor2Diplomacy(face22, (1, 2))

cubemanager.inputFaces([face, face2])
cubemanager.showCubes()
cubemanager.inputFaces([face22, face3])
cubemanager.showCubes()
