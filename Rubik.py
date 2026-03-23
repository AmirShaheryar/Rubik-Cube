# Roll Number: [23L-0828] Section: [BCS-6TH B]

import heapq
import time
import sys

# ─────────────────────────────────────────────
#  INDEX LAYOUT  (flat string of 24 chars)
#
#        0  1
#        2  3
# 16 17  8  9  4  5  20 21
# 18 19 10 11  6  7  22 23
#       12 13
#       14 15
#
#  Face colour order in input string:
#  W(0-3)  R(4-7)  G(8-11)  Y(12-15)  O(16-19)  B(20-23)
# ─────────────────────────────────────────────

DEFAULT_STATE = "WWWWRRRRGGGGYYYYOOOOBBBB"

MOVES = {
    "U":  [2,0,3,1, 8,9,6,7, 16,17,10,11, 12,13,14,15, 20,21,18,19, 4,5,22,23],
    "U'": [1,3,0,2, 20,21,6,7, 4,5,10,11, 12,13,14,15, 8,9,18,19, 16,17,22,23],
    "F":  [0,1,19,17, 2,5,3,7, 10,8,11,9, 6,4,14,15, 16,12,18,13, 20,21,22,23],
    "F'": [0,1,4,6, 13,5,12,7, 9,11,8,10, 17,19,14,15, 16,3,18,2, 20,21,22,23],
    "R":  [0,22,2,20, 6,4,7,5, 8,1,10,3, 12,9,14,11, 16,17,18,19, 15,21,13,23],
    "R'": [0,9,2,11, 5,7,4,6, 8,13,10,15, 12,22,14,20, 16,17,18,19, 3,21,1,23],
    "D":  [0,1,2,3, 4,5,22,23, 8,9,6,7, 14,12,15,13, 16,17,10,11, 20,21,18,19],
    "D'": [0,1,2,3, 4,5,10,11, 8,9,18,19, 13,15,12,14, 16,17,22,23, 20,21,6,7],
    "L":  [8,1,10,3, 4,5,6,7, 12,9,14,11, 23,13,21,15, 18,16,19,17, 20,2,22,0],
    "L'": [23,1,21,3, 4,5,6,7, 0,9,2,11, 8,13,10,15, 17,19,16,18, 20,14,22,12],
    "B":  [7,5,2,3, 4,15,6,14, 8,9,10,11, 12,13,18,16, 1,17,0,19, 22,20,23,21],
    "B'": [18,16,2,3, 4,1,6,0, 8,9,10,11, 12,13,7,5, 15,17,14,19, 21,23,20,22],
}


def _inverse(perm):
    inv = [0] * 24
    for i, p in enumerate(perm):
        inv[p] = i
    return inv

for _move in list(MOVES.keys()):
    MOVES[_move + "'"] = _inverse(MOVES[_move])

ALL_MOVES = list(MOVES.keys())



class Cube:
    def __init__(self, state=None):
        if state is None:
            state = DEFAULT_STATE
        # Accept space-separated format: "WWWW RRRR GGGG YYYY OOOO BBBB"
        self.state = tuple(state.replace(" ", ""))
        assert len(self.state) == 24, "State must have exactly 24 tiles."

    def display(self):
        s = self.state
        lines = []
        lines.append("   " + s[0] + s[1])
        lines.append("   " + s[2] + s[3])
        lines.append(s[16] + s[17] + s[8] + s[9] + s[4] + s[5] + s[20] + s[21])
        lines.append(s[18] + s[19] + s[10] + s[11] + s[6] + s[7] + s[22] + s[23])
        lines.append("   " + s[12] + s[13])
        lines.append("   " + s[14] + s[15])
        return "\n".join(lines)

    def is_goal(self):
        s = self.state
        faces = [s[0:4], s[4:8], s[8:12], s[12:16], s[16:20], s[20:24]]
        return all(len(set(f)) == 1 for f in faces)

    def apply_move(self, move):
        perm = MOVES[move]
        new_state = tuple(self.state[perm[i]] for i in range(24))
        return Cube.__from_tuple(new_state)

    def successors(self):
        return [(move, self.apply_move(move)) for move in ALL_MOVES]

    @staticmethod
    def __from_tuple(t):
        c = Cube.__new__(Cube)
        c.state = t
        return c

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def __repr__(self):
        return "".join(self.state)

FACE_INDICES = [
    (0, 1, 2, 3),       # U / White
    (4, 5, 6, 7),       # R / Red
    (8, 9, 10, 11),     # G / Green
    (12, 13, 14, 15),   # D / Yellow
    (16, 17, 18, 19),   # L / Orange
    (20, 21, 22, 23),   # B / Blue
]

def heuristic(cube):
    s = cube.state
    h = 0
    for face in FACE_INDICES:
        colours = [s[i] for i in face]
        most_common = max(set(colours), key=colours.count)
        wrong = sum(1 for c in colours if c != most_common)
        h = max(h, wrong)
    return (h + 1) // 2   
def astar(start_cube):
    start_time = time.time()

    counter = 0
    start_h = heuristic(start_cube)
    open_list = [(start_h, 0, counter, start_cube, [])]
    heapq.heapify(open_list)

    closed = {}          
    nodes_generated = 1
    nodes_expanded = 0

    while open_list:
        f, g, _, cube, path = heapq.heappop(open_list)

        if cube.state in closed and closed[cube.state] <= g:
            continue
        closed[cube.state] = g

        nodes_expanded += 1

        if cube.is_goal():
            elapsed = time.time() - start_time
            return path, nodes_generated, nodes_expanded, elapsed

        for move, child in cube.successors():
            new_g = g + 1
            if child.state in closed and closed[child.state] <= new_g:
                continue
            new_h = heuristic(child)
            new_f = new_g + new_h
            counter += 1
            nodes_generated += 1
            heapq.heappush(open_list, (new_f, new_g, counter, child, path + [move]))

    return None, nodes_generated, nodes_expanded, time.time() - start_time
def parse_state(args, idx=1):
    """Return (state_string | None, next_arg_index)."""
    if idx < len(args):
        candidate = args[idx].replace(" ", "")
        if len(candidate) == 24 and candidate.isalpha():
            return candidate, idx + 1
    return None, idx


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: python RubiksCube2x2x2.py <command> [state]")
        print("Commands: print | goal | move <MOVE> | solve")
        print("Example : python RubiksCube2x2x2.py solve WWWWRRRRGGGGYYYYOOOOBBBB")
        return

    command = args[0].lower()

    if command == "print":
        raw, _ = parse_state(args, 1)
        cube = Cube(raw)
        print(cube.display())

    elif command == "goal":
        raw, _ = parse_state(args, 1)
        cube = Cube(raw)
        print(cube.is_goal())

    elif command == "move":
        if len(args) < 2:
            print("Please specify a move, e.g.: move U")
            return
        move_name = args[1]
        if move_name not in MOVES:
            print(f"Unknown move '{move_name}'. Valid moves: {', '.join(ALL_MOVES)}")
            return
        raw, _ = parse_state(args, 2)
        cube = Cube(raw)
        result = cube.apply_move(move_name)
        print(f"After move {move_name}:")
        print(result.display())

    elif command == "solve":
        raw, _ = parse_state(args, 1)
        cube = Cube(raw)

        print("Initial state:")
        print(cube.display())
        print()

        if cube.is_goal():
            print("Already solved!")
            return

        print("Running A* Search...")
        solution, gen, exp, elapsed = astar(cube)

        if solution is None:
            print("No solution found.")
        else:
            print(f"Solution found in {len(solution)} move(s)!\n")
            current = cube
            for i, move in enumerate(solution):
                current = current.apply_move(move)
                print(f"Move {i+1}: {move}")
                print(current.display())
                print()

            print(f"Moves sequence : {' -> '.join(solution)}")
            print(f"Nodes generated: {gen}")
            print(f"Nodes expanded : {exp}")
            print(f"Time taken     : {elapsed:.4f} seconds")

    else:
        print(f"Unknown command '{command}'. Use: print | goal | move | solve")


if __name__ == "__main__":
    main()
