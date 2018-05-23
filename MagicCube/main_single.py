import cv2, glob
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
    global img
    global curr_framehandler  # type: FrameHandler

    img_copy = np.copy(img)

    if event == cv2.EVENT_LBUTTONDOWN:
        # print("BUTTONDOWN")
        button_state = DOWN
        button_start_pos = (x, y)

    if event == cv2.EVENT_MOUSEMOVE:
        # print("MOUSEMOVE")
        if button_state == DOWN:
            g = img.item(y, x, 0)
            b = img.item(y, x, 1)
            r = img.item(y, x, 2)
            newColor = ((b + 128) % 256, (g + 128) % 256, (r + 128) % 256)
            cv2.rectangle(img_copy, button_start_pos, (x, y), newColor, 1)

    if event == cv2.EVENT_LBUTTONUP:
        # print("BUTTONUP")
        button_state = UP
        if x == button_start_pos[0] and y == button_start_pos[1]:
            return
        img_slice = img[button_start_pos[1]: y, button_start_pos[0]: x]
        mean_color = cv2.mean(img_slice)
        round_color = (round(mean_color[0]), round(mean_color[1]), round(mean_color[2]))
        if round_color[0] == 0 and round_color[1] == 0 and round_color[2] == 0:
            return
        currColor = round_color
        print("bgr: %-15s, hsv: %-15s, color: %s" % (
        round_color, Color.bgr2hsv(round_color), Color.names[Color.getColorByBGR(round_color)]))

    if event == cv2.EVENT_LBUTTONDBLCLK:

        for set in curr_framehandler.blocklinker.legalSets:
            for block in set.blocks:
                cnt = block.contour()
                if cv2.pointPolygonTest(cnt, (x, y), False):
                    print(block.id)

    cv2.imshow('img', img_copy)


def excuteFrame(img, cubemanager):
    global curr_framehandler

    framehandler = FrameHandler(img, cubemanager)
    curr_framehandler = framehandler
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
                cv2.circle(mask2, (centroid[0], centroid[1]), 4, colors[i + 3], -1)
            i += 1

    cv2.imshow('mask', mask2)
    cv2.imshow('img', img)
    # cv2.imshow('originmask', framehandler.mix_masks())

    return mask2


def initImg(img, scaleratio):
    height, width, channels = img.shape
    img = cv2.resize(img, (width // scaleratio, height // scaleratio), interpolation=cv2.INTER_AREA)
    # img = cv2.medianBlur(img, 5)
    # img = cv2.bilateralFilter(img,9,75,75)
    # img = cv2.blur(img, (5, 5))
    return img


# imgaddr = '/home/windness/Pictures/magic_cube/cubes/3.jpg' ;scaleratio = 4
# imgaddr = '/home/windness/Pictures/magic_cube/res_cube/7.jpg' ;scaleratio = 2
# imgaddr = '/home/windness/Pictures/magic_cube/blackcubes/6.png';scaleratio = 1
# imgaddr = '/home/windness/Pictures/magic_cube/blackcubes/0501_5.jpg';scaleratio = 2
# imgaddr = '/home/windness/Pictures/magic_cube/red_orange_yellow/1.jpeg';scaleratio = 2
# img0 = cv2.imread(imgaddr)

# files = glob.glob('/home/windness/Pictures/magic_cube/red_orange_yellow/*.*');scaleratio = 2
files = glob.glob('/home/windness/Pictures/magic_cube/blackcubes/series/*.*');scaleratio = 1

files.sort()
pic_index = 0
img0 = cv2.imread(files[pic_index])

img = initImg(img0, scaleratio)

cv2.namedWindow('mask')
cv2.namedWindow('img')
cv2.setMouseCallback('img', onMouseEvent)

cubemanager = CubeManager()
curr_framehandler = None  # type: FrameHandler
# # white
# cubemanager.set_color(Color.WHITE, (0, 0, 160), (180, 70, 255))
# # blue
# cubemanager.set_color(Color.BLUE, (90, 100, 100), (124, 255, 255))
# # red
# cubemanager.set_color(Color.RED, (156, 100, 100), (180, 255, 255))
# cubemanager.set_color(Color.RED, (0, 100, 85), (6, 255, 255))
# # orange
# # cubemanager.set_color(Color.ORANGE, (0, 120, 100), (12, 255, 255))
# cubemanager.set_color(Color.ORANGE, (1, 100, 100), (6, 120, 120))
# cubemanager.set_color(Color.ORANGE, (7, 120, 100), (12, 255, 255))
# # green
# cubemanager.set_color(Color.GREEN, (45, 100, 100), (80, 255, 255))
# # yellow
# cubemanager.set_color(Color.YELLOW, (13, 71, 100), (44, 255, 255))

result = excuteFrame(img, cubemanager)

while True:
    key = cv2.waitKey(0) & 0xFF
    if key == 27:
        break
    if key == ord('x') or key == ord('X'):
        cubemanager.showCubes()
    if key == ord('s') or key == ord('S'):
        filename = '/home/windness/Pictures/magic_cube/cube_examples/' + '4_source.png'
        ret = cv2.imwrite(filename, img)

        filename2 = '/home/windness/Pictures/magic_cube/cube_examples/' + '4_result.png'
        ret2 = cv2.imwrite(filename2, result)

        print("ret = %s, ret2 = %s" % (ret, ret2))
    if key == ord('q'):
        pic_index -= 1
        img = cv2.imread(files[pic_index % len(files)])
        img = initImg(img, scaleratio)
        result = excuteFrame(img, cubemanager)
        pass
    if key == ord('e'):
        pic_index += 1
        img = cv2.imread(files[pic_index % len(files)])
        img = initImg(img, scaleratio)
        result = excuteFrame(img, cubemanager)
        pass

cv2.destroyAllWindows()
