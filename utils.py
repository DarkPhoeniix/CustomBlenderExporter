
import mathutils
from math import pi
from bpy_extras.io_utils import axis_conversion

def console_log(message: str, end: str = '\n'):
    '''Helper function to write a log to the Blender's console'''
    print(message, end=end)


def rhs_to_lhs(matrix):
    axis_correction = axis_conversion('Y', 'Z', 'Z', 'Y')
    axis_correction = mathutils.Matrix(((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)))
    return axis_correction @ matrix


def format_float(num):
    return round(num, 4)


def format_matrix(matrix):
    return {
                'r0': f'{format_float(matrix[0][0])} {format_float(matrix[0][1])} {format_float(matrix[0][2])} {format_float(matrix[0][3])}',
                'r1': f'{format_float(matrix[1][0])} {format_float(matrix[1][1])} {format_float(matrix[1][2])} {format_float(matrix[1][3])}',
                'r2': f'{format_float(matrix[2][0])} {format_float(matrix[2][1])} {format_float(matrix[2][2])} {format_float(matrix[2][3])}',
                'r3': f'{format_float(matrix[3][0])} {format_float(matrix[3][1])} {format_float(matrix[3][2])} {format_float(matrix[3][3])}'
            }
