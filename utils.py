# -*- coding: utf8 -*-
from termcolor import colored
import copy
import numpy as np

DEBUG = False

ALL = set(range(1, 10))


class GridPrinter(object):
    V2H = 3  # One V spans 3-time space as one H
    TL = '┏'
    TR = '┓'
    BL = '┗'
    BR = '┛'
    H  = '━' * V2H
    V  = '┃'
    TC = '┳'
    RC = '┫'
    BC = '┻'
    LC = '┣'
    C =  '╋'

    def _draw_one_row(self, left, mid, right, cell):
        return list(left + mid.join(cell) + right)

    def _make_grid(self, cell_size=1):
        tabular_grid = []

        for i in range(9):
            # Cell top
            if i == 0:
                tabular_grid.append(self._draw_one_row(
                    self.TL, self.TC, self.TR, [self.H * cell_size] * 9
                ))
            else:
                tabular_grid.append(self._draw_one_row(
                    self.LC, self.C, self.RC, [self.H * cell_size] * 9
                ))

            # Cell body
            oneline = self._draw_one_row(
                self.V, self.V, self.V, [' ' * self.V2H * cell_size] * 9
            )
            tabular_grid.extend([copy.deepcopy(oneline) for i in range(cell_size)])

        # Cell bottom
        tabular_grid.append(self._draw_one_row(
            self.BL, self.BC, self.BR, [self.H * cell_size] * 9
        ))

        return tabular_grid

    def print_choice_grid(self, choice_board, board):
        COLORS = [
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'white',
        ]
        tabular_grid = self._make_grid(cell_size=3)
        for i, row in enumerate(choice_board):
            _i = 4 * i
            for j, cell in enumerate(row):
                _j = 10 * j 

                if board[i][j]:
                    t = board[i][j]
                    _ii = (t - 1) // 3 + 1
                    _jj = ((t + 2) % 3 + 1) * 3 - 1
                    tabular_grid[_i + _ii][_j + _jj] = colored(str(t), COLORS[t % 7])
                    continue

                for k in range(1, 10):
                    _ii = (k - 1) // 3 + 1
                    _jj = ((k + 2) % 3 + 1) * 3 - 1
                    if cell and k in cell:
                        tabular_grid[_i + _ii][_j + _jj] = colored(str(k), COLORS[k % 7])


        print('\n'.join(map(lambda x: ''.join(x), tabular_grid)))


    def print_grid(self, board):
        tabular_grid = self._make_grid()

        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                tabular_grid[i * 2 + 1] \
                    [(self.V2H + 1) * (j + 1) - 1 - self.V2H // 2] = str(cell) if cell else ' '

        print('\n'.join(map(lambda x: ''.join(x), tabular_grid)))


def get_next_search_cell(stack, board):
    last = [0, 0] if not stack else stack[-1]

    for i in range(9):
        if i < last[0]:
            continue

        for j in range(9):
            if i == last[0] and j <= last[1]:
                continue
            if not board[i][j]:
                return i, j

    raise Exception('Reached the end of board, no further available search.')


def is_invalid_choice_board(choice_board, board):
    for i in range(9):
        for j in range(9):
            if not board[i][j] and not choice_board[i][j]:
                if DEBUG:
                    print('Invalid choice at: {}, {}, {}, {}'.format(
                        i, j, board[i][j], choice_board[i][j]
                    ))
                return True

    return False


def _is_unique_in_grid9(v, i, j, choice_board):
    lower_i = i // 3 * 3
    lower_j = j // 3 * 3
    for ii in range(lower_i, lower_i + 3):
        for jj in range(lower_j, lower_j + 3):
            if i == ii and j == jj:
                continue

            if choice_board[ii][jj] and v in choice_board[ii][jj]:
                return False

    return True


def find_unique_grid9(i, j, choice_board):
    for v in choice_board[i][j]:
        if _is_unique_in_grid9(v, i, j, choice_board):
            if DEBUG:
                print('in grid9: v - {}'.format(v))
            return v


def _is_unique_in_row(v, i, j, choice_board):
    for jj in range(9):
        if jj == j:
            continue

        if choice_board[i][jj] and v in choice_board[i][jj]:
            return False

    return True


def find_unique_hori(i, j, choice_board):
    for v in choice_board[i][j]:
        if _is_unique_in_row(v, i, j, choice_board):
            if DEBUG:
                print('in row: v - {}'.format(v))
            return v


def _is_unique_in_col(v, i, j, choice_board):
    for ii in range(9):
        if i == ii:
            continue

        if choice_board[ii][j] and v in choice_board[ii][j]:
            return False

    return True


def find_unique_verti(i, j, choice_board):
    for v in choice_board[i][j]:
        if _is_unique_in_col(v, i, j, choice_board):
            if DEBUG:
                print('in col: v - {}'.format(v))
            return v


def is_identical_board(b1, b2):
    for i in range(9):
        for j in range(9):
            if (b1[i][j] != b2[i][j]):
                return False

    return True


def parse_tab_chart(tab_chart):
    tab_chart = tab_chart.strip('\n').replace('\n', '\t').split('\t')
    tab_chart = list(map(lambda x: int(x) if x else None, tab_chart))
    return np.array(tab_chart).reshape(9, 9)


def get_hori_choices(i, j, board):
    if board[i][j]:
        raise Exception('Cannot get choice for filled cell.')

    hori_set = set(board[i])
    return ALL - hori_set


def get_verti_choices(i, j, board):
    if board[i][j]:
        raise Exception('Cannot get choice for filled cell.')

    verti_set = set([board[x][j] for x in range(9)])
    return ALL - verti_set


def _list_grid9_cells(i, j, board):
    lower_i = i // 3 * 3
    lower_j = j // 3 * 3

    return [board[x][y] 
        for x in range(lower_i, lower_i + 3)
        for y in range(lower_j, lower_j + 3)
    ]


def get_grid9_choices(i, j, board):
    if board[i][j]:
        raise Exception('Cannot get choice for filled cell.')

    grid9_set = set(_list_grid9_cells(i, j, board))
    return ALL - grid9_set
