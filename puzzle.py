from __future__ import annotations
MAX_PUSH = 1


def prt_board(board: list[list[str]], player, boxes: list["Box"], doors: list["Door"], plates: list["PressurePlate"]):
    """Prints the board with the player, boxes, doors, and pressure plates overlayed."""
    display_board = [row[:] for row in board]

def ask_inputLimit(limit: list[str], prompt: str):
    """Ask the user for input until they choose a valid option."""
    while True:
        user_input = input(prompt).strip()
        if user_input in limit:
            return user_input
        print(f"Invalid input. Please choose from {limit}.")


class Player:
    def __init__(self, position: tuple[int, int]):
        self.pos = position

    def move(self, direction: str, board: list[list[str]], boxes: list["Box"]):
        x, y  = self.pos
        dx, dy = {
            'w': (0, 1),
            's': (0, -1),
            'a': (-1, 0),
            'd': (1, 0)
        }[direction]
        new_x, new_y = x + dx, y + dy

        if board[new_y][new_x] == "#":
            return False  # Wall collision



class Box:
    def __init__(self, position: tuple[int, int]):
        self.pos = position


# "#" = wall
# " " = empty space
# "&" = player
# "☒" = box
# "*" = pressure plate
# "E" = goal
# "|" = door
level1 = [
    ["#", "#", "#", "#", "#", "#", "#"],
    ["#", " ", " ", " ", "|", " ", "#"],
    ["#", " ", " ", " ", "#", "#", "#"],
    ["#", " ", " ", " ", " ", " ", "#"],
    ["#", " ", " ", " ", "*", " ", "#"],
    ["#", " ", " ", " ", " ", " ", "#"],
    ["#", "#", "#", "#", "#", "#", "#"]
]

running = True
player = Player((5, 1))
boxes = [Box((3, 3)), Box((3, 4))]

while running:
    prt_board(level1, player, boxes)
    action = ask_inputLimit(["w", "a", "s", "d", "q"],
                            "Move (w,a,s,d) or 'q' to quit: ")

    if action == "q":
        running = False
        continue

    if not player.move(action, level1, boxes):
        print("You cannot move there.")

    print()
