from copy import deepcopy

from utils import (GridPrinter,
                   find_unique_grid9,
                   find_unique_hori,
                   find_unique_verti,
                   get_grid9_choices,
                   get_hori_choices,
                   get_next_search_cell,
                   get_verti_choices,
                   is_identical_board,
                   is_invalid_choice_board,
                   parse_tab_chart,
                   )


DEBUG = False

tab_chart = '''
	1	7					4	
6			3		4		7	8
								
						5	8	
	4			6				
3		2						
				2	8			3
			6		5			1
	7					2		
'''

choice_board = [[None for x in range(9)] for y in range(9)]
gp = GridPrinter()
stack = list()


def process_once(board, choice_board):
    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell:
                continue

            c1 = get_hori_choices(i, j, board)
            c2 = get_verti_choices(i, j, board)
            c3 = get_grid9_choices(i, j, board)
            choice_board[i][j] = c1 & c2 & c3

    if DEBUG:
        gp.print_choice_grid(choice_board, board)

    # Previous choice makes this search branch invalid
    if is_invalid_choice_board(choice_board, board):
        i, j, v, prev_board, choices = stack.pop(-1)

        # roll back to previous state
        board = prev_board

        v = choices.pop()
        if len(choices) > 0:
            stack.append((i, j, v, deepcopy(board), choices))

        board[i][j] = v
        choice_board[i][j] = set()

        return board, choice_board

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell:
                continue

            if len(choice_board[i][j]) == 1:
                if DEBUG:
                    print('only value: i - {}, j - {}'.format(i, j))
                board[i][j] = choice_board[i][j].pop()
                return board, choice_board

            u1 = find_unique_grid9(i, j, choice_board)
            if u1:
                if DEBUG:
                    print('grid9 unique: i - {}, j - {}'.format(i, j))
                board[i][j] = u1
                choice_board[i][j] = set()
                return board, choice_board

            u2 = find_unique_hori(i, j, choice_board)
            if u2:
                if DEBUG:
                    print('hori unique: i - {}, j - {}'.format(i, j))
                board[i][j] = u2
                choice_board[i][j] = set()
                return board, choice_board

            u3 = find_unique_verti(i, j, choice_board)
            if u3:
                if DEBUG:
                    print('verti unique: i - {}, j - {}'.format(i, j))
                board[i][j] = u3
                choice_board[i][j] = set()
                return board, choice_board

    # If the code gets here, it means no further restraint on choices
    try:
        i, j = get_next_search_cell(stack, board)
    except Exception as e:
        print(e)
        return board, choice_board

    v = choice_board[i][j].pop()
    stack.append((i, j, v, deepcopy(board), choice_board[i][j]))
    if DEBUG:
        print('Search: {}, {}, {}, {}'.format(i, j, v, choice_board[i][j]))

    board[i][j] = v
    choice_board[i][j] = set()

    return board, choice_board


if __name__ == "__main__":
    board = parse_tab_chart(tab_chart)
    gp.print_grid(board)

    last_choice_board = None
    i = 0
    while True:
        i += 1

        board, choice_board = process_once(board, choice_board)
        if DEBUG:
            print(i)

        if last_choice_board is not None and \
            is_identical_board(last_choice_board, choice_board):
            print('Reached stable state after {} iterations.'.format(i))
            break

        last_choice_board = deepcopy(choice_board)

    gp.print_grid(board)
