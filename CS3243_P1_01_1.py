import os
import sys

visited_nodes = set()
result = list()

class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.size = len(init_state)
        self.init_state = init_state
        self.goal_state = goal_state
        self.actions = list()
        self.empty_cell_position = [-1, -1]

    def getEmptyCellPosition(self):
        if self.empty_cell_position != [-1, -1]:
            return self.empty_cell_position
        for i in range(0, self.size):
            for j in range(0, self.size):
                cell_value = self.init_state[i][j]
                if cell_value == 0:
                    return [i, j]

    def moveEmptyCellToLeft(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if col <= 0:
            return Puzzle([], [])
        
        new_state[row][col] = new_state[row][col - 1]
        new_state[row][col - 1] = 0
        new_actions = self.actions[:]
        new_actions.append("RIGHT")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row, col - 1]
        new_puzzle.actions = new_actions
        return new_puzzle

    def moveEmptyCellUp(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if row <= 0:
            return Puzzle([], [])

        new_state[row][col] = new_state[row - 1][col]
        new_state[row - 1][col] = 0
        new_actions = self.actions[:]
        new_actions.append("DOWN")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row - 1, col]
        new_puzzle.actions = new_actions
        
        return new_puzzle

    def moveEmptyCellToRight(self):          
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if col >= self.size - 1:
            return Puzzle([], [])
        
        new_state[row][col] = new_state[row][col + 1]
        new_state[row][col + 1] = 0
        new_actions = self.actions[:]
        new_actions.append("LEFT")
        new_puzzle = Puzzle(new_state, self.goal_state)       
        new_puzzle.empty_cell_position = [row, col + 1]
        new_puzzle.actions = new_actions
        
        return new_puzzle

    def moveEmptyCellDown(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if row >= self.size - 1:
            return Puzzle([], [])

        new_state[row][col] = new_state[row + 1][col]
        new_state[row + 1][col] = 0
        new_actions = self.actions[:]
        new_actions.append("UP")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row + 1, col]
        new_puzzle.actions = new_actions
        return new_puzzle

    def DLS(self, depth, limit):
        global result
        # puzzle state is invalid
        if self.init_state == []:
            return False
        if self.init_state == self.goal_state:
            result = self.actions
            return True
        if depth > limit:
            return False
        # checks if node has been visited before
        tuple_for_set = tuple(map(tuple, self.init_state))
        if tuple_for_set in visited_nodes:
            return False
        visited_nodes.add(tuple_for_set)

        return self.moveEmptyCellToRight().DLS(depth + 1, limit) or self.moveEmptyCellToLeft().DLS(depth + 1, limit) or \
            self.moveEmptyCellUp().DLS(
                depth + 1, limit) or self.moveEmptyCellDown().DLS(depth + 1, limit)

    # helper function to determine whether an initial state is solvable, using the concept of inversions
    # formula is derived from https://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html
    def solvable(self):
        # flatten 2d grid into 1d list
        flatList = []
        for i in range(0, self.size):
            for j in range(0, self.size):
                flatList.append(self.init_state[i][j])
        inversions = 0
        rowWithBlank = 0
        # run through the list and see how many inversions there are
        # this should be a one time n^2 operation
        for i in range(0, len(flatList)):
            current = flatList[i]
            if (current == 0):
                # take note of which row we are on
                rowWithBlank = i / self.size
            else:
                for j in range(i + 1, len(flatList)):
                    if (flatList[j] != 0 and current > flatList[j]):
                        inversions += 1
        
        evenDimensions = self.size % 2 == 0
        evenInversions = inversions % 2 == 0
        blankOnEvenRow = rowWithBlank % 2 == 0
        
        return ((not(evenDimensions) and evenInversions) or (evenDimensions and (blankOnEvenRow != evenInversions)))

    # insert unsolvable check here
    def solve(self):
        if self.solvable():
            global visited_nodes
            for limit in range(0, 1000):
                visited_nodes = set()
                if self.DLS(0, limit):
                    print(result)
                    print(len(result))
                    return result

        print("UNSOLVABLE")
        return ["UNSOLVABLE"]
    # you may add more functions if you think is useful


if __name__ == "__main__":
    # do NOT modify below

    # argv[0] represents the name of the file that is being executed
    # argv[1] represents name of input file
    # argv[2] represents name of destination output file
    if len(sys.argv) != 3:
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        raise IOError("Input file not found!")

    lines = f.readlines()
    
    # n = num rows in input file
    n = len(lines)
    # max_num = n to the power of 2 - 1
    max_num = n ** 2 - 1

    # Instantiate a 2D list of size n x n
    init_state = [[0 for i in range(n)] for j in range(n)]
    goal_state = [[0 for i in range(n)] for j in range(n)]
    

    i,j = 0, 0
    for line in lines:
        for number in line.split(" "):
            if number == '':
                continue
            value = int(number , base = 10)
            if  0 <= value <= max_num:
                init_state[i][j] = value
                j += 1
                if j == n:
                    i += 1
                    j = 0

    for i in range(1, max_num + 1):
        goal_state[(i-1)//n][(i-1)%n] = i
    goal_state[n - 1][n - 1] = 0

    puzzle = Puzzle(init_state, goal_state)
    ans = puzzle.solve()

    with open(sys.argv[2], 'a') as f:
        for answer in ans:
            f.write(answer+'\n')