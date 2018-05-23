import cv2
# from MagicCube.items.cube_manager import CubeManager, Color, FrameHandler
import time

from MagicCube.items.cube_manager import *
from MagicCube.utils import util

DOWN = 'DOWN'
UP = 'UP'
button_state = UP
button_start_pos = None
currColor = None

def onMouseEvent(event, x, y, flags, param):
    global button_state
    global button_start_pos
    global currColor
    global source

    img_copy = np.copy(source)

    if event == cv2.EVENT_LBUTTONDOWN:
        # print("BUTTONDOWN")
        button_state = DOWN
        button_start_pos = (x, y)

    if event == cv2.EVENT_MOUSEMOVE:
        # print("MOUSEMOVE")
        if button_state == DOWN:
            g = source.item(y, x, 0)
            b = source.item(y, x, 1)
            r = source.item(y, x, 2)
            newColor = ((b + 128) % 256, (g + 128) % 256, (r + 128) % 256)
            cv2.rectangle(img_copy, button_start_pos, (x, y), newColor, 1)

    if event == cv2.EVENT_LBUTTONUP:
        # print("BUTTONUP")
        button_state = UP
        if x == button_start_pos[0] and y == button_start_pos[1]:
            return
        img_slice = source[button_start_pos[1]: y, button_start_pos[0]: x]
        mean_color = cv2.mean(img_slice)
        round_color = (round(mean_color[0]), round(mean_color[1]), round(mean_color[2]))
        if round_color[0] == 0 and round_color[1] == 0 and round_color[2] == 0:
            return
        currColor = round_color
        print("bgr: %-15s, hsv: %-15s, color: %s" % (round_color, Color.bgr2hsv(round_color), Color.names[Color.getColorByBGR(round_color)]))


    cv2.imshow('img', img_copy)


def excuteFrame(img, cubemanager):
    framehandler = FrameHandler(img, cubemanager)
    framehandler.excute()

    mask = framehandler.mix_masks()
    mask2 = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    colors = []
    colors.append((255, 0, 0))
    colors.append((255, 255, 0))
    colors.append((255, 0, 255))

    colors.append((120, 0, 0))
    colors.append((120, 120, 0))
    colors.append((120, 0, 120))

    i = 0
    for set in framehandler.blockLinker.sets:
        for block in set.blocks:
            cv2.circle(mask2, block.get_centroid(), 10, colors[i % 3], 2)
            for linkedBlock in block.links:
                cv2.line(mask2, block.get_centroid(), linkedBlock.get_centroid(), colors[i], 1)
        i += 1

    for block in framehandler.blocks:
        if block.probability == 1:
            cv2.drawContours(mask2, [block.contour()], -1, Color.getColorByIndex(block.get_color()), 2)
            centroid = block.get_centroid()
            cv2.putText(mask2, str(block.id), (centroid[0] - 3, centroid[1] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (120, 120, 120),
                        2)
            cv2.circle(mask2, centroid, 2, (0, 0, 255), -1)

    i = 0
    for set in framehandler.blockLinker.sets:
        for group0 in set.linkedgroups:
            for position in group0.searchingPositions():

                position_tuple = (position[0], position[1])
                if position_tuple in set.colordic.keys():
                    color0 = set.colordic[position_tuple]
                    point = group0.positionCentroid(position)
                    cv2.circle(mask2, (point[0], point[1]), 20, Color.getColorByIndex(color0), 2)

                centroid = group0.positionCentroid(position)
                cv2.circle(mask2, (centroid[0], centroid[1]), 4, colors[i % 3 + 3], -1)
            i += 1

    cv2.imshow('mask', mask2)
    cv2.imshow('img', img)

    return mask2


cubemanager = CubeManager()
# # white
# cubemanager.set_color(Color.WHITE, (0, 0, 160), (180, 70, 255))
# # blue
# cubemanager.set_color(Color.BLUE, (90, 100, 100), (124, 255, 255))
# # red
# cubemanager.set_color(Color.RED, (156, 100, 100), (180, 255, 255))
# cubemanager.set_color(Color.RED, (0, 100, 85), (3, 200, 255))
# # orange
# # cubemanager.set_color(Color.ORANGE, (0, 120, 100), (12, 255, 255))
# # cubemanager.set_color(Color.ORANGE, (1, 100, 100), (6, 120, 120))
# # cubemanager.set_color(Color.ORANGE, (3, 201, 100), (6, 255, 255))
# cubemanager.set_color(Color.ORANGE, (7, 120, 100), (12, 255, 255))
# # green
# cubemanager.set_color(Color.GREEN, (45, 100, 100), (80, 255, 255))
# # yellow
# cubemanager.set_color(Color.YELLOW, (13, 71, 100), (44, 255, 255))

# # white
# cubemanager.set_color(Color.WHITE, (0, 0, 160), (180, 70, 255))
# # blue
# cubemanager.set_color(Color.BLUE, (90, 100, 100), (124, 255, 255))
# # red
# cubemanager.set_color(Color.RED, (156, 100, 100), (180, 255, 255))
# cubemanager.set_color(Color.RED, (0, 43, 46), (10, 255, 255))
# # orange
# cubemanager.set_color(Color.ORANGE, (3, 201, 100), (6, 255, 255))
# cubemanager.set_color(Color.ORANGE, (7, 120, 100), (12, 255, 255))
# # green
# cubemanager.set_color(Color.GREEN, (45, 100, 100), (80, 255, 255))
# # yellow
# cubemanager.set_color(Color.YELLOW, (13, 100, 100), (44, 255, 255))

# excuteFrame(img, cubemanager)

cv2.namedWindow('mask')
cv2.namedWindow('img')
cv2.setMouseCallback('img', onMouseEvent)

str_time = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
total = 0
cap = cv2.VideoCapture(1)

source = None

while True:
    ret, frame = cap.read()
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('camera', frame)
    key = cv2.waitKey(30) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):

        # filename = '/home/windness/Pictures/magic_cube/cubes/' + str_time + '/' + str(sum) + '.png'
        filename = '/home/windness/Pictures/magic_cube/blackcubes/' + str_time + '__' + str(total) + '.png'
        print("writting " + filename + " ...")
        ret = cv2.imwrite(filename, source)
        print("ret = " + str(ret))
        total += 1
    elif key == ord('x'):
        output = excuteFrame(frame, cubemanager)
        cubemanager.showCubes()
        source = frame

cv2.waitKey(0) & 0xFF
cv2.destroyAllWindows()
