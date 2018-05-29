import cv2

from MagicCube.items.cube_manager import CubeManager, FrameHandler

cubemanager = None
state = 0


def init_cubemanager():
    global cubemanager

    cubemanager = CubeManager()
    print("init_cubemanager success")


def excute_frame(filename):
    global cubemanager
    global state

    state = 233

    if cubemanager is None:
        print("cubemanager hasn't been initialized.")
        return
    else:
        img = cv2.imread(filename)

        framehandler = FrameHandler(img, cubemanager)
        framehandler.excute()

        cubemanager.showCubes()
        return cubemanager


def return_data():
    global cubemanager
    global state

    print("state = %s" % state)
    state += 1

    if cubemanager is None:
        print("cubemanager hasn't been initialized.")
        return
    else:
        return cubemanager.getCurrentCubeData()


def refresh_data():
    global cubemanager

    cubemanager.refresh_cubedatas()


def update_data(data):
    global cubemanager

    cubemanager.update_cubedatas(data)