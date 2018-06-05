from MagicCube.items.cube_manager import CubeManager, Color

manager = CubeManager()

# yellow = {'data': [[Color.ORANGE, Color.ORANGE, Color.ORANGE], [Color.YELLOW, Color.YELLOW, Color.YELLOW],
#                    [Color.YELLOW, Color.YELLOW, Color.YELLOW]], 'center_color': Color.YELLOW}
# red = {'data': [[Color.RED, Color.RED, Color.YELLOW], [Color.RED, Color.RED, Color.YELLOW],
#                 [Color.BLUE, Color.BLUE, Color.BLUE]], 'center_color': Color.RED}
# green = {'data': [[Color.GREEN, Color.GREEN, Color.GREEN], [Color.GREEN, Color.GREEN, Color.GREEN],
#                   [Color.RED, Color.RED, Color.YELLOW]], 'center_color': Color.GREEN}

# yellow = {'data': [[Color.YELLOW, Color.ORANGE, Color.ORANGE], [Color.YELLOW, Color.YELLOW, Color.YELLOW],
#                    [Color.YELLOW, Color.YELLOW, Color.YELLOW]], 'center_color': Color.YELLOW}
# red = {'data': [[Color.RED, Color.RED, Color.YELLOW], [Color.RED, Color.RED, Color.YELLOW],
#                 [Color.ORANGE, Color.BLUE, Color.BLUE]], 'center_color': Color.RED}
# green = {'data': [[Color.GREEN, Color.GREEN, Color.GREEN], [Color.GREEN, Color.GREEN, Color.GREEN],
#                   [Color.RED, Color.RED, Color.BLUE]], 'center_color': Color.GREEN}



# yellow = {'data': [[Color.ORANGE, Color.ORANGE, Color.YELLOW], [Color.YELLOW, Color.YELLOW, Color.YELLOW],
#                    [Color.YELLOW, Color.YELLOW, Color.YELLOW]], 'center_color': Color.YELLOW}
# red = {'data': [[Color.RED, Color.RED, Color.YELLOW], [Color.RED, Color.RED, Color.YELLOW],
#                 [Color.BLUE, Color.BLUE, Color.BLUE]], 'center_color': Color.RED}
# green = {'data': [[Color.GREEN, Color.GREEN, Color.GREEN], [Color.GREEN, Color.GREEN, Color.GREEN],
#                   [Color.RED, Color.RED, Color.YELLOW]], 'center_color': Color.GREEN}
#
# orange = {'data': [[Color.WHITE, Color.ORANGE, Color.ORANGE], [Color.WHITE, Color.ORANGE, Color.ORANGE],
#                    [Color.GREEN, Color.GREEN, Color.GREEN]], 'center_color': Color.ORANGE}
# blue = {'data': [[Color.BLUE, Color.BLUE, Color.BLUE], [Color.BLUE, Color.BLUE, Color.BLUE],
#                  [Color.WHITE, Color.ORANGE, Color.ORANGE]], 'center_color': Color.BLUE}
# white = {'data': [[Color.WHITE, Color.WHITE, Color.RED], [Color.WHITE, Color.WHITE, Color.RED],
#                   [Color.WHITE, Color.WHITE, Color.RED]], 'center_color': Color.WHITE}
# newdatas = [yellow, red, green, orange, blue, white]



white = {'data': [[Color.ORANGE, Color.BLUE, Color.YELLOW], [Color.YELLOW, Color.WHITE, Color.BLUE],
                  [Color.YELLOW, Color.GREEN, Color.GREEN]], 'center_color': Color.WHITE}

red = {'data': [[Color.BLUE, Color.YELLOW, Color.ORANGE], [Color.ORANGE, Color.RED, Color.ORANGE],
                [Color.ORANGE, Color.WHITE, Color.WHITE]], 'center_color': Color.RED}

blue = {'data': [[Color.YELLOW, Color.WHITE, Color.BLUE], [Color.YELLOW, Color.BLUE, Color.RED],
                 [Color.RED, Color.GREEN, Color.BLUE]], 'center_color': Color.BLUE}

orange = {'data': [[Color.RED, Color.YELLOW, Color.WHITE], [Color.GREEN, Color.ORANGE, Color.BLUE],
                   [Color.RED, Color.RED, Color.RED]], 'center_color': Color.ORANGE}

green = {'data': [[Color.BLUE, Color.RED, Color.ORANGE], [Color.RED, Color.GREEN, Color.WHITE],
                  [Color.YELLOW, Color.BLUE, Color.GREEN]], 'center_color': Color.GREEN}

yellow = {'data': [[Color.WHITE, Color.GREEN, Color.GREEN], [Color.ORANGE, Color.YELLOW, Color.ORANGE],
                   [Color.GREEN, Color.WHITE, Color.WHITE]], 'center_color': Color.YELLOW}

newdatas = [yellow, red, green, orange, blue, white]

manager.update_cubedatas(newdatas)

# cubeColorset = {Color.BLUE, Color.ORANGE}
# centerColorset = {Color.RED, Color.YELLOW}
cubeColorset = {Color.RED, Color.BLUE, Color.YELLOW}
centerColorset = {Color.RED, Color.BLUE, Color.WHITE}
cube = manager.getCubeByCenterColors(centerColorset)
standardItem = CubeManager.standardMagicube[CubeManager.getTuple(cubeColorset)]

# print(standardItem)

# a = [None, None, None]
# for i in range(3):
#     key = cube.getCenterColorIndex(standardItem[1][i])
#     # print('color:', standardItem[1][i], ", center:", key)
#     if key is not None:
#         a[i] = CubeManager.color2axis[key]
# twoOneZero = {2, 1, 0}
# noneIndexes = []
# for i in range(3):
#     if a[i] is not None:
#         twoOneZero.remove(a[i])
#     else:
#         noneIndexes.append(i)
#
# for i in range(len(noneIndexes)):
#     a[noneIndexes[i]] = twoOneZero.pop()
# retRotation = a[0] + a[1] * 10 + a[2] * 100
# ret = (standardItem[0], retRotation)
# print(ret)


# print(manager.solveCube())

manager.solveCubeDebug()
# solution = manager.cubrSolution2MySolution("FUDBF'D'")
# print(solution)