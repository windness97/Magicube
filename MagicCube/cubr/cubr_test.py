from MagicCube.cubr.cube import CubeState, brief
import MagicCube.cubr.solutions as solutions

newState = [[[(19, 120), (2, 210), (3, 210)],
             [(10, 120), (5, 210), (6, 210)],
             [(1, 120), (8, 210), (9, 210)]],

            [[(22, 120), (11, 210), (12, 210)],
             [(13, 120), (14, 210), (15, 210)],
             [(4, 120), (17, 210), (18, 210)]],

            [[(7, 21), (16, 21), (25, 21)],
             [(26, 201), (23, 201), (20, 201)],
             [(27, 201), (24, 201), (21, 201)]]]

state = CubeState()
state.setState(newState)

solution = solutions.beginner3Layer(state)
print(brief(solution))

