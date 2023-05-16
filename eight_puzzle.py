import heapq
import copy
import time

def main():
    # prompt the use to enter the desired grid size of the puzzle
    puzzle_grid_size = input("Please start by entering the desired grid size of the puzzle(default/recommend size is 3)\nEnter a positive integer that is at least 2: ")

    # throw error if non integer entered or less than 2 entered
    try:
        int(puzzle_grid_size)
        puzzle_grid_size = int(puzzle_grid_size)
    except ValueError:
        print("What you entered was not an integer, please restart the program and enter an integer instead.\n")
        return 0
    if puzzle_grid_size < 2:
        print("What you entered was less than 2, please restart the program and enter a number that is at least 2 instead.\n")
        return 0
    
    # form the goal state to use for later
    goal_state = form_goal_state(puzzle_grid_size)

    # customize is set to true, meaning user will customize their puzzle
    customize = True

    # default puzzle is only available for grid of 3 by 3
    if puzzle_grid_size == 3:
        enter_puzzle = input("\nGreat, default puzzles are available for grid size of 3, please enter the corresponding number to select \n1. Use default puzzles  \n2. Customize your puzzle \nYour selection: ")
        
        # choose from default puzzles
        if enter_puzzle == "1": 
            difficulty = input("\nYou've selected default puzzles, now please enter level of difficulties from 1 to 8: ")
            print("\nHere is your selected puzzle: \n")
            puzzle = default_puzzles(int(difficulty))
            print_puzzle(puzzle)
            customize = False

    # if didn't choose the default, customize the puzzle
    if customize:
        print("\nNow let's customize your puzzle by entering your desired values one row at a time,", 
              "\nnotice that the puzzle will be validated and please use number '0' to represent the blank space,",
              "\nand please put a space between each value entered for each row \n")
        
        puzzle = []
        for i in range(puzzle_grid_size):
            prompt_string = "Please enter the values for row "+ str(i+1) + ":\n"
            puzzle_row = input(prompt_string)
            puzzle_row = (puzzle_row).split()
            puzzle_row = [int(num) for num in puzzle_row]
            puzzle.append(puzzle_row)

        # this will validate if the entered puzzle is valid, avoid overflow
        if validate_puzzle(puzzle) == False:
            print("The puzzle you entered is invalid, please restart the program.\n")
            return 0
        else:
            print("\nHere is your cutomized puzzle: \n")
            print_puzzle(puzzle)

    # depending on the input, start to search 
    method = input("Great, now let's choose the desired method you want to solve with, please enter the corresponding number to select \n1. Uniform Cost Search \n2. A* with the Misplaced Tile heuristic \n3. A* with the Manhattan Distance heuristic\nYour selection: ")
    start_time = time.time() # use a timer to time the execution time
    if method == "1": # uniform cost search     
        uniform_cost_search(puzzle, goal_state)
    if method == "2": # A* with misplaced tile heuristic
        astar_heuristic_search(puzzle, goal_state, "misplaced")
    if method == "3": # A* with Manhattan distance heuristic
        astar_heuristic_search(puzzle, goal_state, "manhattan")
    print("The time taken to solve this puzzle is %s seconds" % (time.time() - start_time))

# this class contains each state as node, containing necessary information
class SearchNode: 
    def __init__(self, state, parent = None, cost = 0, distance = 0): # cost is g(n), distance is h(n)
        self.state = state
        self.parent = parent
        self.cost = cost
        self.distance = distance

    def __lt__(self, other): # This function allows heapq to comapre SearchNode instances
        return (self.cost + self.distance) < (other.cost + other.distance)
    
# this function takes in a node and return a list containing all possible expansion by move up, down, right, or left
def expand(initial_node):
    n = len(initial_node.state)

    # this two for loops find the location of 0, which is the empty space
    for i in range(n):
        for j in range(n):
            if initial_node.state[i][j] == 0:
                row = i
                col = j
                break

    expanded_states = []

    # expand up
    if row > 0:
        new_state = copy.deepcopy(initial_node.state)
        new_state[row][col] = initial_node.state[row-1][col]
        new_state[row-1][col] = 0
        if initial_node.parent == None or (not check_puzzle(initial_node.state, initial_node.parent.state)):
            expanded_states.append(new_state)
    
    # expand down
    if row < n - 1:
        new_state = copy.deepcopy(initial_node.state)
        new_state[row][col] = initial_node.state[row+1][col]
        new_state[row+1][col] = 0
        if initial_node.parent == None or (not check_puzzle(initial_node.state, initial_node.parent.state)):
            expanded_states.append(new_state)

    # expand left
    if col > 0:
        new_state = copy.deepcopy(initial_node.state)
        new_state[row][col] = initial_node.state[row][col-1]
        new_state[row][col-1] = 0
        if initial_node.parent == None or (not check_puzzle(initial_node.state, initial_node.parent.state)):
            expanded_states.append(new_state)

    # expand right
    if col < n - 1:
        new_state = copy.deepcopy(initial_node.state)
        new_state[row][col] = initial_node.state[row][col+1]
        new_state[row][col+1] = 0
        if initial_node.parent == None or (not check_puzzle(initial_node.state, initial_node.parent.state)):
            expanded_states.append(new_state)
    return expanded_states

# This is the uniform cost search algorithm, it takes an initial state and a goal state and finish the search
def uniform_cost_search(initial_state, goal_state):
    initial_node = SearchNode(state = initial_state)
    queue = []            # use priority queue to be able to find the smallest node
    worked_states = []    # track the worked states to avoid reaching the same states
    heapq.heappush(queue, initial_node)     # push the current node to the heap
    expanded_nodes = 0    # initialize the expanded nodes to 0
    depth = 0             # initialize the depth to 0
    max_queue = 1         # initialize the max queue size to 1
    while queue: 
        current_node = heapq.heappop(queue)  # remove the smallest node from the queue to search
        if check_puzzle(current_node.state, goal_state):  # if meet the goal state, end search and print summary
            print("\nSolved! \n")
            while current_node:
                print("This state has g(n) of",current_node.cost,"and h(n) of",current_node.distance)
                print_puzzle(current_node.state)
                current_node = current_node.parent
            print("Here is a summary")
            print("The number of nodes expanded is",expanded_nodes)
            print("The depth is",depth)
            print("The maximum size of the queue is",max_queue)
            return 0
        else:
            current_cost = current_node.cost
            worked_states.append(current_node.state)   # since this node has been searched, add it to worked states
            expanded_states = expand(current_node)     # expand the children of current node
            expanded_nodes += 1                        # update expanded nodes
            max_queue = max(max_queue, len(queue))     # update max queue size
            for state in expanded_states:
                if state not in worked_states:
                    new_node = SearchNode(parent = current_node, state = state, cost = current_cost+1)
                    if new_node not in queue:
                        # if the current node is neither in worked states nor in queue, push it into queue
                        heapq.heappush(queue, new_node)
                        depth = max(depth, new_node.cost-1)   # update depth
            
# This function prints out the puzzle into a matrix view
def print_puzzle(puzzle):
    for row in puzzle:
        print(row)
    print(" ")

# This function calculates and returns the misplaced tile calculation between current state and goal state
def misplaced_tile_distance(current_state, goal_state):
    count = 0
    n = len(current_state)
    for i in range(n):
        for j in range(n):
            if current_state[i][j] != goal_state[i][j] and current_state[i][j] != 0:  # ignore 0 because it is empty
                count += 1
    return count

# This function calculates and finds the manhattan distance difference between current state and the goal state
def manhattan_distance(current_state, goal_state):
    res = 0
    n = len(current_state)
    for i in range(n):       # the first two for loops find where the initial state doesn't math the goal state
        for j in range(n):
            if current_state[i][j] != goal_state[i][j] and current_state[i][j] != 0: # ignore 0 because it is empty
                for k in range(n):      # the next two for loops find where the mismatching number is located in goal state
                    for l in range(n):
                        if current_state[i][j] == goal_state[k][l]:
                            row_diff = abs(k-i)           # find row difference
                            col_diff = abs(l-j)           # find column difference
                            res += row_diff + col_diff    
                            break
    return res

# This is the A* with Misplaced Tile heuristic search function
def astar_heuristic_search(initial_state, goal_state, distance_method):
    if distance_method == "misplaced":
        initial_distance = misplaced_tile_distance(initial_state, goal_state)
    if distance_method == "manhattan":
        initial_distance = manhattan_distance(initial_state, goal_state)
    initial_node = SearchNode(state=initial_state, distance = initial_distance)
    queue = []                       # here below are the same with uniform cost search
    worked_states = []
    heapq.heappush(queue, initial_node)
    expanded_nodes = 0
    depth = 0
    max_queue = 1
    while queue: 
        current_node = heapq.heappop(queue)
        if check_puzzle(current_node.state, goal_state):
            print("\nSolved! Here is a traceback of the solution:\n")
            while current_node:
                print("This state has g(n) of",current_node.cost,"and h(n) of",current_node.distance)
                print_puzzle(current_node.state)
                current_node = current_node.parent
            print("Here is a summary")
            print("The number of nodes expanded is",expanded_nodes)
            print("The depth is",depth)
            print("The maximum size of the queue is",max_queue)
            return 0
        else:
            current_cost = current_node.cost
            worked_states.append(current_node.state)
            expanded_states = expand(current_node)
            expanded_nodes += 1
            max_queue = max(max_queue, len(queue))
            for state in expanded_states:
                if state not in worked_states:             # here are all pretty much the same with uniform, except for adding h(n)
                    if distance_method == "misplaced":
                        distance = misplaced_tile_distance(state, goal_state)
                    if distance_method == "manhattan":
                        distance = manhattan_distance(state, goal_state)
                    new_node = SearchNode(parent = current_node, state = state, cost = current_cost+1, distance = distance)
                    if new_node not in queue:
                        heapq.heappush(queue, new_node)
                        depth = max(depth, new_node.cost)

# This function check if current state matches the goal state
def check_puzzle(current_state, goal_state):
    return current_state == goal_state

# This function check if customized puzzle is valid
def validate_puzzle(puzzle):
    size = len(puzzle) ** 2
    authentic = [i for i in range(size)]
    actual = []
    for row in puzzle:
        for num in row:
            actual.append(num)
    return sorted(actual) == authentic

# This function simply return the desired defualt puzzle according to selected difficulty
def default_puzzles(difficulty):
    puzzles = [[[1,2,3],[4,5,6],[7,8,0]],
               [[1,2,3],[4,5,6],[0,7,8]],
               [[1,2,3],[5,0,6],[4,7,8]],
               [[1,3,6],[5,0,2],[4,7,8]],
               [[1,3,6],[5,0,7],[4,8,2]],
               [[1,6,7],[5,0,3],[4,8,2]],
               [[7,1,2],[4,8,5],[6,3,0]],
               [[0,7,2],[4,6,1],[3,5,8]]
               ]
    return puzzles[difficulty-1]

# This function takes in the input grid size and form a goal state 
def form_goal_state(n): 
    limit = n * n
    res = []
    cur = 1
    for i in range(n):
        row = []
        for j in range(n):
            if cur < limit:
                row.append(cur)
            else:
                row.append(0)
            cur += 1
        res.append(row)
    return res

main()
