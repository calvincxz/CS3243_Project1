import os
import sys
from Queue import PriorityQueue

result = list()
visited_nodes = set()

# Using ManhattanDist as heuristic
class Puzzle(object):
    def __init__(self, init_state, goal_state):
        # you may add more attributes if you think is useful
        self.size = len(init_state)
        self.init_state = init_state
        self.goal_state = goal_state
        self.actions = list()
        self.empty_cell_position = [-1, -1]
        self.evaluation_cost = -1

    def __lt__(self, other):
        return self.evaluation_cost < other.evaluation_cost

    def getEmptyCellPosition(self):
        if self.empty_cell_position != [-1, -1]:
            return self.empty_cell_position
        for i in range(0, self.size):
            for j in range(0, self.size):
                cell_value = self.init_state[i][j]
                if cell_value == 0:
                    return [i, j]

    def getManhattanDistanceChange(self, blankRow, blankCol, direction):
        # find the tile that is to be moved into the blank space. note its current position, final position and goal position
        # and then calculate the difference in manhattan distance after the move
        if direction == 'left':
            movedTileOrigCol = blankCol - 1
            movedTileVal = self.init_state[blankRow][movedTileOrigCol]
            movedTileGoalCol = (movedTileVal - 1) % self.size
            if movedTileOrigCol < movedTileGoalCol:
                return -1
            else: 
                return 1

        elif direction == 'right':
            movedTileOrigCol = blankCol + 1
            movedTileVal = self.init_state[blankRow][movedTileOrigCol]
            movedTileGoalCol = (movedTileVal - 1) % self.size
            if movedTileOrigCol > movedTileGoalCol:
                return -1
            else: 
                return 1

        elif direction == 'up':
            movedTileOrigRow = blankRow - 1
            movedTileVal = self.init_state[movedTileOrigRow][blankCol]
            movedTileGoalRow = (movedTileVal - 1) / self.size
            if movedTileOrigRow < movedTileGoalRow:
                return -1
            else: 
                return 1
        
        # moving blank tile down
        else:
            movedTileOrigRow = blankRow + 1
            movedTileVal = self.init_state[movedTileOrigRow][blankCol]
            movedTileGoalRow = (movedTileVal - 1) / self.size
            if movedTileOrigRow > movedTileGoalRow:
                return -1
            else: 
                return 1

    def moveEmptyCellToLeft(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if col <= 0:
            return None

        manhattanDistanceChange = self.getManhattanDistanceChange(row, col, 'left')

        new_state[row][col] = new_state[row][col - 1]
        new_state[row][col - 1] = 0
        new_actions = self.actions[:]
        new_actions.append("RIGHT")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row, col - 1]
        new_puzzle.actions = new_actions
        # update the manhattandistance by 1 or -1, and the g(n) by 1 since we're going deeper by 1 level
        new_puzzle.evaluation_cost = self.evaluation_cost + manhattanDistanceChange + 1   

        return new_puzzle

    def moveEmptyCellUp(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if row <= 0:
            return None

        manhattanDistanceChange = self.getManhattanDistanceChange(row, col, 'up')

        new_state[row][col] = new_state[row - 1][col]
        new_state[row - 1][col] = 0
        new_actions = self.actions[:]
        new_actions.append("DOWN")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row - 1, col]
        new_puzzle.actions = new_actions
        # update the manhattandistance by 1 or -1, and the g(n) by 1 since we're going deeper by 1 level
        new_puzzle.evaluation_cost = self.evaluation_cost + manhattanDistanceChange + 1

        return new_puzzle

    def moveEmptyCellToRight(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if col >= self.size - 1:
            return None

        manhattanDistanceChange = self.getManhattanDistanceChange(row, col, 'right')
        
        new_state[row][col] = new_state[row][col + 1]
        new_state[row][col + 1] = 0
        new_actions = self.actions[:]
        new_actions.append("LEFT")
        new_puzzle = Puzzle(new_state, self.goal_state)       
        new_puzzle.empty_cell_position = [row, col + 1]
        new_puzzle.actions = new_actions
        # update the manhattandistance by 1 or -1, and the g(n) by 1 since we're going deeper by 1 level
        new_puzzle.evaluation_cost = self.evaluation_cost + manhattanDistanceChange + 1        
        return new_puzzle

    def moveEmptyCellDown(self):
        empty_cell_position = self.getEmptyCellPosition()
        new_state = list(map(list, self.init_state))
        row = empty_cell_position[0]
        col = empty_cell_position[1]
        if row >= self.size - 1:
            return None

        manhattanDistanceChange = self.getManhattanDistanceChange(row, col, 'down')

        new_state[row][col] = new_state[row + 1][col]
        new_state[row + 1][col] = 0
        new_actions = self.actions[:]
        new_actions.append("UP")
        new_puzzle = Puzzle(new_state, self.goal_state)
        new_puzzle.empty_cell_position = [row + 1, col]
        new_puzzle.actions = new_actions
        new_puzzle.evaluation_cost = self.evaluation_cost + manhattanDistanceChange + 1        
        return new_puzzle

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
        print("number of inversions", inversions)
        print("evenInversion?", evenInversions)
        print("blankOnEvenRow?", blankOnEvenRow)
        return ((not(evenDimensions) and evenInversions) or (evenDimensions and (blankOnEvenRow != evenInversions)))

    def solve(self):
        if self.solvable():
            # run manhattan calculation only once. Eval cost at the start is only = manhattan distance as we have not traversed any nodes yet so g(n) = 0
            self.evaluation_cost = self.calcManhattanDist()
            global result
            global visited_nodes
            pq = PriorityQueue()
            pq.put(self)

            # loops till goal state is found or all nodes are visited
            while not (pq.empty()):
                node = pq.get()
                # print "manhattan distance of this node", node.evaluation_cost
                tuple_for_set = tuple(map(tuple, node.init_state))

                # check if popped node's state = goal state
                if node.init_state == node.goal_state:
                    print(node.actions)
                    print(len(node.actions))
                    return node.actions

                # checks if node has been visited before
                visited_nodes.add(tuple_for_set)

                # adds neighbour to frontier
                neighbours = [node.moveEmptyCellDown(), node.moveEmptyCellUp(), \
                            node.moveEmptyCellToLeft(), node.moveEmptyCellToRight()]
                for neighbour in neighbours:
                    if neighbour != None:
                        tuple_for_set = tuple(map(tuple, neighbour.init_state))
                        if not (tuple_for_set in visited_nodes):
                            pq.put(neighbour)

        print("UNSOLVABLE")
        return ["UNSOLVABLE"]

    # def evaluation_function(self):
    #     return self.manhattanValue + len(self.actions)

    # heuristic 1 - calculates number of misplaced tiles from init state to goal state
    def misplacedTiles(self):
        count = 0
        for i in range(0, self.size):
            for j in range(0, self.size):
                if self.init_state[i][j] != self.size * i + j + 1:
                    if i == j == self.size - 1 and self.init_state[i][j] == 0:
                        continue
                    else:
                        count += 1
        return count

    # heuristic 2 - calculates manhattan tiles from init state to goal state (O(n^2) complexity though)

    def calcManhattanDist(self):
        count = 0
        for i in range(0, self.size):
            for j in range(0, self.size): 
                if self.init_state[i][j] != 0 and self.init_state[i][j] != self.goal_state[i][j]:
                    goal = self.getGoalPosition(self.init_state[i][j])
                    count += abs(goal[0] - i) + abs(goal[1] - j)
        # print("manhattan distance is", count)
        return count

    def getGoalPosition(self, value):
        return (value - 1) / self.size, (value - 1) % self.size
    # heuristic 3 - calculates sum of manhattan tiles and linear conflict between tiles in a row  
    
    def calcLinearConflict(self):
        count = 0
        for i in range(0, self.size):
            min = (i * self.size)
            max = (i + 1) * self.size
            curr_row = []
            # check manhattan distance
            for j in range(0, self.size):
                if self.init_state[i][j] != self.goal_state[i][j]:
                    goal = self.getGoalPosition(self.init_state[i][j])
                    count += abs(goal[0] - i + goal[1] - j)
                # push all values belonging to current row in another array
                value = self.init_state[i][j]
                if (value > min & value <= max):
                    curr_row.append(value)
            # check current row values for linear conflict. count + 2 for each linear conflict
            for k in range(0, len(curr_row)-2):
                for m in range(k + 1, len(curr_row)-1):
                    if curr_row[k] > curr_row[m]:
                        count += 2
        # print count
        return count

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