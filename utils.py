import os
import cv2
import numpy as np


def get_files(path, type_='file', format_='*'):
    assert type_ in ['file', 'folder']
    name_list = []
    if type_ == 'file':
        name_list = [x for x in os.listdir(path) if any(x.endswith(extension) for extension in format_)]
    elif type_ == 'folder':
        name_list = [x for x in os.listdir(path) if os.path.isdir(path + x)]

    return name_list


# def distance(p1, p2):
#     return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
#
#
# def get_state(p, center_x, center_y):
#     if p[0] < center_x and p[1] < center_y:
#         state = (0, 0)
#     elif p[0] < center_x and p[1] > center_y:
#         state = (0, 1)
#     elif p[0] > center_x and p[1] < center_y:
#         state = (1, 0)
#     elif p[0] > center_x and p[1] > center_y:
#         state = (1, 1)
#     else:
#         state = (-1, -1)
#
#     print(state)
#     return state
#
#
# def sort_four_points(points):
#     p1 = list(points[0])
#     p2 = list(points[1])
#     p3 = list(points[2])
#     p4 = list(points[3])
#
#     x_list = [p1[0], p2[0], p3[0], p4[0]]
#     y_list = [p1[1], p2[1], p3[1], p4[1]]
#
#     points_copy = points[:]
#     points_copy = list(points_copy)
#
#     for i in range(points_copy.__len__()):
#         points_copy[i] = list(points_copy[i])
#
#     x_index = np.argsort(np.array(x_list))
#     y_index = np.argsort(np.array(y_list))
#
#     if x_list[x_index[1]] == x_list[x_index[2]]:
#         if points_copy[x_index[1]][1] < points_copy[x_index[2]][1]:
#             points_copy[x_index[1]][0] += 0.5
#         elif points_copy[x_index[1]][1] > points_copy[x_index[2]][1]:
#             points_copy[x_index[2]][0] += 0.5
#
#     if y_list[y_index[1]] == y_list[y_index[2]]:
#         if points_copy[x_index[1]][0] < points_copy[x_index[2]][0]:
#             points_copy[x_index[1]][1] += 0.5
#         elif points_copy[x_index[1]][0] > points_copy[x_index[2]][0]:
#             points_copy[x_index[2]][1] += 0.5
#
#     if x_list[x_index[1]] == x_list[x_index[2]] and y_list[y_index[1]] == y_list[y_index[2]]:
#         points_copy[x_index[0]] = [0, 0]
#         points_copy[y_index[0]] = [1, 0]
#         points_copy[x_index[3]] = [1, 1]
#         points_copy[y_index[3]] = [0, 1]
#
#     center_x = (points_copy[x_index[1]][0] + points_copy[x_index[2]][0]) / 2.
#     center_y = (points_copy[y_index[1]][1] + points_copy[y_index[2]][1]) / 2.
#
#     state1 = get_state(points_copy[0], center_x, center_y)
#     state2 = get_state(points_copy[1], center_x, center_y)
#     state3 = get_state(points_copy[2], center_x, center_y)
#     state4 = get_state(points_copy[3], center_x, center_y)
#
#     states = [state1, state2, state3, state4]
#
#     if (-1, -1) in states:
#         return points, False
#
#     if
#
#     points_sorted = []
#     points_sorted.append(points[states.index((0, 0))])
#     points_sorted.append(points[states.index((1, 0))])
#     points_sorted.append(points[states.index((1, 1))])
#     points_sorted.append(points[states.index((0, 1))])
#
#     return points_sorted, True
#
#     # rect = cv2.boundingRect(np.array(points))
#     # tl = (rect[0], rect[1])
#     # bl = (rect[0], rect[1] + rect[3])
#     # tr = (rect[0] + rect[2], rect[1])
#     # br = (rect[0] + rect[2], rect[1] + rect[3])


# def sort_four_points(points):



if __name__ == '__main__':
    points = ((1, 1), (2, 3), (2, 0), (4, 2))

    sorted_p, _ = sort_four_points(points)

    print(sorted_p)
