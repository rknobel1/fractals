from collections import deque
import matplotlib.pyplot as plt
import copy

import Functions as fl

# Storing all transitions and affinity rules
states = []
transitions = []
affinities = []

# To store the tiles where hard resetting will first occur
hard_reset_tiles = []

class Tile():

    def __init__(self, p, n):
        self.previous = p
        self.next = n

    # What direction to copy
    copy_direction = None

    # Caps
    caps = []

    # Local tile information (and neighbors)
    status = None
    tile_to_N = None
    tile_to_E = None
    tile_to_W = None
    tile_to_S = None

    # If tile becomes new key tile or not
    new_kt_N = False
    new_kt_E = False
    new_kt_W = False
    new_kt_S = False

    # Breadcrumb trail
    N = None
    E = None
    W = None
    S = None

    # Holds information from breadcrumb trail (what the state was before)
    temp = None

    # What is being transferred
    transfer = None

    # If tile is a seed 
    original_seed = False
    pseudo_seed = False

    # If tile is on edge of sub-assembly
    wall = False

    # Direction to key tile
    key_tile_N = None
    key_tile_E = None
    key_tile_W = None
    key_tile_S = None

    # Has assembly been copied for tile
    copied = False

    # Is tile terminal
    terminal = False

    # For seeds, number of times subassembly has been copied
    num_times_copied = 0

    # The new previous and next for tile
    new_p = None
    new_n = None

    # If first tile copied
    first_tile = False

# RETURNS: opp(d) i.e if N -> S
def opp(d):
    if d == "N": 
        return "S"
    if d == "E": 
        return "W"
    if d == "W": 
        return "E"
    if d == "S": 
        return "N"
    
# RETURNS: direction of breadcrumb trail (how to retrace signal)
def breadcrumb_trail(tile): 
    if tile.N == 'W' or tile.N == 'M':
        return 'N'
    if tile.E == 'W' or tile.E == 'M':
        return 'E'
    if tile.W == 'W' or tile.W == 'M':
        return 'W'
    if tile.S == 'W' or tile.S == 'M':
        return 'S'

# RETURNS: adjacent tile in direction d from current tile
def retrieve_tile(tile, d):
    if (d == "N"):
        return tile.tile_to_N
    if (d == "E"):
        return tile.tile_to_E
    if (d == "W"):
        return tile.tile_to_W
    if (d == "S"):
        return tile.tile_to_S
    
# RETURNS: whether subassembly is completed or ont
def is_assembly_finished(tile):
    if tile.N == 'N':
        return False
    if tile.E == 'N':
        return False
    if tile.W == 'N':
        return False
    if tile.S == 'N':
        return False
    
    return True

# Plot assembly onto graph (each tile is a mark)
def plot_graph(seed_tile): 
    x, y = [], []
    stack = deque()
    stack.append([seed_tile, 0, 0])
    num_tiles = 0

    print("PRINTING -----------------------")

    while len(stack) > 0:
        cur_tile = stack.pop()

        # Debug
        # print("Printing:", cur_tile[0].next, cur_tile[0].previous, cur_tile[0].N, cur_tile[0].E, cur_tile[0].W, cur_tile[0].S, "Keytiles:", cur_tile[0].key_tile_N, cur_tile[0].key_tile_E, cur_tile[0].key_tile_W, cur_tile[0].key_tile_S, cur_tile[0].copy_direction)
        # time.sleep(1)
        x.append(cur_tile[1])
        y.append(cur_tile[2])

        if cur_tile[0] == None: continue
        num_tiles += 1
        if cur_tile[0].next == None:
            continue

        for neighbor in cur_tile[0].next:
            if (neighbor == "N"):
                stack.append([cur_tile[0].tile_to_N, cur_tile[1], cur_tile[2]+1])
            if (neighbor == "E"):
                stack.append([cur_tile[0].tile_to_E, cur_tile[1]+1, cur_tile[2]])
            if (neighbor == "W"):
                stack.append([cur_tile[0].tile_to_W, cur_tile[1]-1, cur_tile[2]])
            if (neighbor == "S"):
                stack.append([cur_tile[0].tile_to_S, cur_tile[1], cur_tile[2]-1])

    if (max(x) - min(x)) > (max(y) - min(y)): l, r = min(x)-1, max(x) + 1
    else: l, r = min(x)-1, max(x) + 1

    print("Number of tiles: ", num_tiles)
    plt.xticks([])
    plt.yticks([])
    plt.plot(x, y, "x")
    plt.title('Result')
    plt.show()
    return 

def copy_direction_update_tiles(cur_tile, direction):
    c = 0
    if cur_tile.next != None: c += len(cur_tile.next)
    if cur_tile.previous != None: c += len(cur_tile.previous)
    if not cur_tile.original_seed or not cur_tile.pseudo_seed: c -= 1 

    if not cur_tile.terminal and not (cur_tile.original_seed or cur_tile.pseudo_seed): cur_tile.copy_direction = direction + str(c)
    else: cur_tile.copy_direction = direction

    if cur_tile.new_n == None and cur_tile.new_p == None: 
        cur_tile.new_n = copy.deepcopy(cur_tile.next)
        cur_tile.new_p = copy.deepcopy(cur_tile.previous)

    cur_tile.status = 'P'
    cur_tile.caps = []

    if cur_tile.N != None and cur_tile.key_tile_N != None: cur_tile.N = 'N'
    else: cur_tile.N = None
    if cur_tile.E != None and cur_tile.key_tile_E != None: cur_tile.E = 'N'
    else: cur_tile.E = None
    if cur_tile.W != None and cur_tile.key_tile_W != None: cur_tile.W = 'N'
    else: cur_tile.W = None
    if cur_tile.S != None and cur_tile.key_tile_S != None: cur_tile.S = 'N'
    else: cur_tile.S = None

# Proprogate copy direction through subassembly
def choose_copy_direction(tile, direction):
    stack = deque()
    stack.append(tile)
    visited_tiles = []

    t = []

    while len(stack) > 0:
        cur_tile = stack.pop()

        # Generate transition rule -----
        t1 = fl.generate_state(cur_tile)
        # ------------------------------

        if cur_tile.next != None:
            for neighbor in cur_tile.next:
                if retrieve_tile(cur_tile, neighbor) not in visited_tiles and retrieve_tile(cur_tile, neighbor) != None: 
                    adj_tile = retrieve_tile(cur_tile, neighbor)
                    stack.append(adj_tile)

                    # Generate transition rule --------------------
                    t2 = fl.generate_state(adj_tile)

                    copy_direction_update_tiles(cur_tile, direction)
                    copy_direction_update_tiles(adj_tile, direction)

                    t1_final, t2_final = fl.generate_state(cur_tile), fl.generate_state(adj_tile)

                    if neighbor == 'N': transitions.append([t2, t1, t2_final, t1_final, 'V'])
                    elif neighbor == 'E': transitions.append([t1, t2, t1_final, t2_final, 'H'])
                    elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1_final, 'H'])
                    elif neighbor == 'S': transitions.append([t1, t2, t1_final, t2_final, 'V'])
                    t1 = t1_final
                    # ----------------------------------------------

        if cur_tile.previous != None:
            for neighbor in cur_tile.previous:
                if retrieve_tile(cur_tile, neighbor) not in visited_tiles and retrieve_tile(cur_tile, neighbor) != None: 
                    adj_tile = retrieve_tile(cur_tile, neighbor)
                    stack.append(adj_tile)

                    # Generate transition rule ---------------------
                    t2 = fl.generate_state(adj_tile)

                    copy_direction_update_tiles(cur_tile, direction)
                    copy_direction_update_tiles(adj_tile, direction)

                    t1_final, t2_final = fl.generate_state(cur_tile), fl.generate_state(adj_tile)

                    if neighbor == 'N': transitions.append([t2, t1, t2_final, t1_final, 'V'])
                    elif neighbor == 'E': transitions.append([t1, t2, t1_final, t2_final, 'H'])
                    elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1_final, 'H'])
                    elif neighbor == 'S': transitions.append([t1, t2, t1_final, t2_final, 'V'])
                    t1 = t1_final
                    # ----------------------------------------------

        if cur_tile.terminal: t.append(cur_tile)

        visited_tiles.append(cur_tile)

    # All tiles are marked with copying direction, retrace back to original/pseudo seed
    while len(t) > 0:
        cur_tile = t.pop()

        # Generate transition rule ----
        t1 = fl.generate_state(cur_tile)
        # -----------------------------

        if cur_tile.next != None: 
            for neighbor in cur_tile.next:
                if len(retrieve_tile(cur_tile, neighbor).copy_direction) > 1:
                    adj_tile = retrieve_tile(cur_tile, neighbor)

                    # Generate transitions:
                    t2 = fl.generate_state(adj_tile)
                    # ---------------------

                    l = list(adj_tile.copy_direction)

                    l[1] = int(l[1]) - 1

                    if l[1] == 0: 
                        adj_tile.copy_direction = l[0]
                        t.append(adj_tile)

                        # Generate transitions -------------------
                        t2_final = fl.generate_state(adj_tile)

                        if neighbor == 'N': transitions.append([t2, t1, t2_final, t1, 'V'])
                        elif neighbor == 'E': transitions.append([t1, t2, t1, t2_final, 'H'])
                        elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1, 'H'])
                        elif neighbor == 'S': transitions.append([t1, t2, t1, t2_final, 'V'])
                        # ----------------------------------------
                    else: 
                        l[1] = str(l[1])
                        adj_tile.copy_direction = "".join(l)

                        # Generate transitions ------------------
                        t2_final = fl.generate_state(adj_tile)

                        if neighbor == 'N': transitions.append([t2, t1, t2_final, t1, 'V'])
                        elif neighbor == 'E': transitions.append([t1, t2, t1, t2_final, 'H'])
                        elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1, 'H'])
                        elif neighbor == 'S': transitions.append([t1, t2, t1, t2_final, 'V'])
                        # ----------------------------------------
                        break

        if cur_tile.previous != None: 
            for neighbor in cur_tile.previous:
                if len(retrieve_tile(cur_tile, neighbor).copy_direction) > 1:
                    adj_tile = retrieve_tile(cur_tile, neighbor)

                    # Generate transitions
                    t2 = fl.generate_state(adj_tile)
                    # --------------------

                    l = list(adj_tile.copy_direction)

                    l[1] = int(l[1]) - 1

                    if l[1] == 0: 
                        adj_tile.copy_direction = l[0]
                        t.append(adj_tile)

                        # Generate transitions ---------------------------------------------------
                        t2_final = fl.generate_state(adj_tile)

                        if neighbor == 'N': transitions.append([t2, t1, t2_final, t1, 'V'])
                        elif neighbor == 'E': transitions.append([t1, t2, t1, t2_final, 'H'])
                        elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1, 'H'])
                        elif neighbor == 'S': transitions.append([t1, t2, t1, t2_final, 'V'])
                        # -------------------------------------------------------------------------
                    else: 
                        l[1] = str(l[1])
                        adj_tile.copy_direction = "".join(l)

                        # Generate transitions ----------------------------------------------------
                        t2_final = fl.generate_state(adj_tile)
                        if neighbor == 'N': transitions.append([t2, t1, t2_final, t1, 'V'])
                        elif neighbor == 'E': transitions.append([t1, t2, t1, t2_final, 'H'])
                        elif neighbor == 'W': transitions.append([t2, t1, t2_final, t1, 'H'])
                        elif neighbor == 'S': transitions.append([t1, t2, t1, t2_final, 'V'])
                        # -------------------------------------------------------------------------
                        break

    return

# Reset assembly that was copied
# def reset_assembly(tile):
#     stack = deque()
#     stack.append(tile)
#     visited_tiles = []

#     while len(stack) > 0:
#         cur_tile = stack.pop()
#         cur_tile.copy_direction = None
#         cur_tile.status = 'P'
#         cur_tile.caps = []

#         if cur_tile.N != None and cur_tile.key_tile_N != None: cur_tile.N = 'N'
#         else: cur_tile.N = None
#         if cur_tile.E != None and cur_tile.key_tile_E != None: cur_tile.E = 'N'
#         else: cur_tile.E = None
#         if cur_tile.W != None and cur_tile.key_tile_W != None: cur_tile.W = 'N'
#         else: cur_tile.W = None
#         if cur_tile.S != None and cur_tile.key_tile_S != None: cur_tile.S = 'N'
#         else: cur_tile.S = None
    
#         if cur_tile.next != None:
#             for neighbor in cur_tile.next:
#                 if retrieve_tile(cur_tile, neighbor) not in visited_tiles: stack.append(retrieve_tile(cur_tile, neighbor))

#         if cur_tile.previous != None:
#             for neighbor in cur_tile.previous:
#                 if retrieve_tile(cur_tile, neighbor) not in visited_tiles: stack.append(retrieve_tile(cur_tile, neighbor))

#         visited_tiles.append(cur_tile)

#     return

# Reset stage
# def reset_stage(tile):
#     stack = deque()
#     stack.append(tile)

#     while len(stack) > 0:
#         cur_tile = stack.pop()

#         cur_tile.copy_direction = None
#         cur_tile.status = None
#         cur_tile.wall = False
#         cur_tile.pseudo_seed = False
#         cur_tile.caps = []
#         cur_tile.copied = False

#         if cur_tile.tile_to_N != None: cur_tile.N = 'N'
#         if cur_tile.tile_to_E != None: cur_tile.E = 'N'
#         if cur_tile.tile_to_W != None: cur_tile.W = 'N'
#         if cur_tile.tile_to_S != None: cur_tile.S = 'N'

#         # Fix any missing 'previous' and 'next'
#         if not cur_tile.original_seed:

#             if cur_tile.tile_to_N != None and (cur_tile.next == None or 'N' not in cur_tile.next) and (cur_tile.previous == None or cur_tile.previous[0] != 'N'): 
#                 if cur_tile.next == None: cur_tile.next = ['N']
#                 else: cur_tile.next.append('N')
                
#                 retrieve_tile(cur_tile, 'N').previous = ['S']

#             if cur_tile.tile_to_E != None and (cur_tile.next == None or 'E' not in cur_tile.next) and (cur_tile.previous == None or cur_tile.previous[0] != 'E'): 
#                 if cur_tile.next == None: cur_tile.next = ['E']
#                 else: cur_tile.next.append('E')
                
#                 retrieve_tile(cur_tile, 'E').previous = ['W']

#             if cur_tile.tile_to_W != None and (cur_tile.next == None or 'W' not in cur_tile.next) and (cur_tile.previous == None or cur_tile.previous[0] != 'W'): 
#                 if cur_tile.next == None: cur_tile.next = ['W']
#                 else: cur_tile.next.append('W')
                
#                 retrieve_tile(cur_tile, 'W').previous = ['E']

#             if cur_tile.tile_to_S != None and (cur_tile.next == None or 'S' not in cur_tile.next) and (cur_tile.previous == None or cur_tile.previous[0] != 'S'): 
#                 if cur_tile.next == None: cur_tile.next = ['S']
#                 else: cur_tile.next.append('S')
                
#                 retrieve_tile(cur_tile, 'S').previous = ['N']

#         # Update terminal
#         total = 0
#         if cur_tile.next != None: total += len(cur_tile.next)
#         if cur_tile.previous != None: total += len(cur_tile.previous)
#         if total == 1: cur_tile.terminal = True
#         else: cur_tile.terminal = False
        

#         if cur_tile.next != None:
#             for neighbor in cur_tile.next:
#                 stack.append(retrieve_tile(cur_tile, neighbor))

#     return

# Reset direction to keytile
# def reset_keytile_directions(tile):

#     kt_N, kt_E, kt_W, kt_S = None, None, None, None

#     # Locate the correct key tile locations
#     stack = deque()
#     stack.append(tile)
#     while len(stack) > 0: 
#         cur_tile = stack.pop()

#         if cur_tile.key_tile_N == None and cur_tile.new_kt_N: kt_N = cur_tile
#         if cur_tile.key_tile_E == None and cur_tile.new_kt_E: kt_E = cur_tile
#         if cur_tile.key_tile_W == None and cur_tile.new_kt_W: kt_W = cur_tile
#         if cur_tile.key_tile_S == None and cur_tile.new_kt_S: kt_S = cur_tile
        
#         if cur_tile.next != None: 
#             for n in cur_tile.next: 
#                 stack.append(retrieve_tile(cur_tile, n))

#     # Reset the system
#     # North
#     visited_tiles = []
#     stack = deque()
#     stack.append(kt_N)
#     while len(stack) > 0:
#         cur_tile = stack.pop()
#         visited_tiles.append(cur_tile)

#         if cur_tile.next != None:
#             for n in cur_tile.next: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_N = [opp(n)]
#                     stack.append(adj_tile)

#         if cur_tile.previous != None:
#             for n in cur_tile.previous: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_N = [opp(n)]
#                     stack.append(adj_tile)

#         cur_tile.new_kt_N = False

#     # East
#     visited_tiles = []
#     stack = deque()
#     stack.append(kt_E)
#     while len(stack) > 0:
#         cur_tile = stack.pop()
#         visited_tiles.append(cur_tile)

#         if cur_tile.next != None:
#             for n in cur_tile.next: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_E = [opp(n)]
#                     stack.append(adj_tile)

#         if cur_tile.previous != None:
#             for n in cur_tile.previous: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_E = [opp(n)]
#                     stack.append(adj_tile)

#         cur_tile.new_kt_E = False

#     # West
#     visited_tiles = []
#     stack = deque()
#     stack.append(kt_W)
#     while len(stack) > 0:
#         cur_tile = stack.pop()
#         visited_tiles.append(cur_tile)

#         if cur_tile.next != None:
#             for n in cur_tile.next: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_W = [opp(n)]
#                     stack.append(adj_tile)

#         if cur_tile.previous != None:
#             for n in cur_tile.previous: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_W = [opp(n)]
#                     stack.append(adj_tile)

#         cur_tile.new_kt_W = False

#     # South
#     visited_tiles = []
#     stack = deque()
#     stack.append(kt_S)
#     while len(stack) > 0:
#         cur_tile = stack.pop()
#         visited_tiles.append(cur_tile)

#         if cur_tile.next != None:
#             for n in cur_tile.next: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_S = [opp(n)]
#                     stack.append(adj_tile)

#         if cur_tile.previous != None:
#             for n in cur_tile.previous: 
#                 adj_tile = retrieve_tile(cur_tile, n)
#                 if adj_tile not in visited_tiles:
#                     adj_tile.key_tile_S = [opp(n)]
#                     stack.append(adj_tile)

#         cur_tile.new_kt_S = False

# Updates prev/next if tile is missing
def update_prev_next(ct):

    if ct.tile_to_N != None: ct.N = 'N'
    if ct.tile_to_E != None: ct.E = 'N'
    if ct.tile_to_W != None: ct.W = 'N'
    if ct.tile_to_S != None: ct.S = 'N'

    ct.next = copy.deepcopy(ct.new_n)
    ct.previous = copy.deepcopy(ct.new_p)

# Reset specific tile
def reset_tile(ct):

    # Reset current tile info
    ct.copy_direction = None
    ct.status = None
    ct.wall = False
    ct.pseudo_seed = False
    ct.caps = []
    ct.copied = False
    ct.num_times_copied = 0
    ct.temp = None
    ct.transfer = None

    ct.new_n = None
    ct.new_p = None
    ct.first_tile = False

    if num_next(ct)+1 == 1: ct.terminal = True
    else: ct.terminal = False

# Hard reset only using terminal tiles:
def hard_reset():

    while len(hard_reset_tiles) > 0:

        ct = hard_reset_tiles.pop()
        # print()
        # print("Tile from stack: ", ct.next, ct.previous, ct.key_tile_N, ct.key_tile_E, ct.key_tile_W, ct.key_tile_S, ct.copy_direction)
        update_prev_next(ct)

        # print("Updated: ", ct.next, ct.previous, ct.key_tile_N, ct.key_tile_E, ct.key_tile_W, ct.key_tile_S, ct.copy_direction)
        # print()

        # if ct.previous != None: 

        # Retrieve adjacent tile
        adj_tile = retrieve_tile(ct, ct.previous[0])
        update_prev_next(adj_tile)

        # print("Current BEFORE: ", ct.next, ct.previous, ct.key_tile_N, ct.key_tile_E, ct.key_tile_W, ct.key_tile_S, ct.copy_direction)
        # print("--- Adj BEFORE:", adj_tile.next, adj_tile.previous, adj_tile.key_tile_N, adj_tile.key_tile_E, adj_tile.key_tile_W, adj_tile.key_tile_S, adj_tile.copy_direction)

        # Start by first spreading hard reset if not yet done
        if adj_tile.copy_direction == 'r': 
            # print("RESET: ", adj_tile.next, adj_tile.previous)
            adj_tile.copy_direction = 'R?'
            t = [adj_tile]
            update_prev_next(adj_tile)

            while len(t) > 0:
                cur = t.pop()
                # print("-------- resetting tile:", cur.next, cur.previous)

                if cur.next != None: 
                    for neighbor in cur.next:
                        a = retrieve_tile(cur, neighbor)
                        update_prev_next(a)
                        if a != None and (a.copy_direction == 'r'):
                            if a.next == None: 
                                a.copy_direction = 'R'
                                hard_reset_tiles.append(a)
                            else: a.copy_direction = 'R?'
                            t.append(a)

                if cur.previous != None: 
                    for neighbor in cur.previous:
                        a = retrieve_tile(cur, neighbor)
                        update_prev_next(a)
                        if a != None and (a.copy_direction == 'r'):
                            if a.next == None: 
                                a.copy_direction = 'R'
                                hard_reset_tiles.append(a)
                            else: a.copy_direction = 'R?'
                            t.append(a)
                
                cur.key_tile_N = '*'
                cur.key_tile_E = '*'
                cur.key_tile_W = '*'
                cur.key_tile_S = '*'
                if num_next(cur) == 0: cur.copy_direction = 'R'
                else: cur.copy_direction = 'R' + str(num_next(cur))

        # Resetting tile
        reset_tile(ct)

        # Not at seed yet
        if not adj_tile.original_seed: 
            
            # Update direction to key tiles for cur tile and neighbor
            #   When cur_tile is terminal
            if ct.terminal:
                if ct.new_kt_N: 
                    ct.key_tile_N = None
                    adj_tile.key_tile_N = opp(ct.previous[0])
                else: ct.key_tile_N = ct.previous[0]

                if ct.new_kt_E: 
                    ct.key_tile_E = None
                    adj_tile.key_tile_E = opp(ct.previous[0])
                else: ct.key_tile_E = ct.previous[0]

                if ct.new_kt_W: 
                    ct.key_tile_W = None
                    adj_tile.key_tile_W = opp(ct.previous[0])
                else: ct.key_tile_W = ct.previous[0]

                if ct.new_kt_S: 
                    ct.key_tile_S = None
                    adj_tile.key_tile_S = opp(ct.previous[0])
                else: ct.key_tile_S = ct.previous[0]

            #   Cur_tile is not terminal
            else:
                if ct.new_kt_N: 
                    ct.key_tile_N = None
                    adj_tile.key_tile_N = opp(ct.previous[0])
                elif ct.key_tile_N != ct.previous[0]: adj_tile.key_tile_N = opp(ct.previous[0])

                if ct.new_kt_E or (ct.original_seed and ct.key_tile_E == None): 
                    ct.key_tile_E = None
                    adj_tile.key_tile_E = opp(ct.previous[0])
                elif ct.key_tile_E != ct.previous[0]: adj_tile.key_tile_E = opp(ct.previous[0])

                if ct.new_kt_W or (ct.original_seed and ct.key_tile_W == None): 
                    ct.key_tile_W = None
                    adj_tile.key_tile_W = opp(ct.previous[0])
                elif ct.key_tile_W != ct.previous[0]: adj_tile.key_tile_W = opp(ct.previous[0])
                
                if ct.new_kt_S or (ct.original_seed and ct.key_tile_S == None): 
                    ct.key_tile_S = None
                    adj_tile.key_tile_S = opp(ct.previous[0])
                elif ct.key_tile_S != ct.previous[0]: adj_tile.key_tile_S = opp(ct.previous[0])

            # Update adjacent
            l = list(adj_tile.copy_direction)
            l[1] = int(l[1]) - 1

            if adj_tile.original_seed: 
                # Reset the seed
                reset_tile(adj_tile)
                
                if adj_tile.key_tile_N == '*': adj_tile.key_tile_N = None 
                if adj_tile.key_tile_E == '*': adj_tile.key_tile_E = None 
                if adj_tile.key_tile_W == '*': adj_tile.key_tile_W = None 
                if adj_tile.key_tile_S == '*': adj_tile.key_tile_S = None 

            elif l[1]+1 == 1 and adj_tile.previous != None: 

                if adj_tile.key_tile_N == '*': adj_tile.key_tile_N = adj_tile.previous[0]
                if adj_tile.key_tile_E == '*': adj_tile.key_tile_E = adj_tile.previous[0]
                if adj_tile.key_tile_W == '*': adj_tile.key_tile_W = adj_tile.previous[0]
                if adj_tile.key_tile_S == '*': adj_tile.key_tile_S = adj_tile.previous[0]
                adj_tile.copy_direction = 'R'
                hard_reset_tiles.append(adj_tile)
            elif l[1]+1 == 1 and adj_tile.previous == None: 
                update_prev_next(adj_tile)
                
                if adj_tile.key_tile_N == '*': adj_tile.key_tile_N = adj_tile.previous[0]
                if adj_tile.key_tile_E == '*': adj_tile.key_tile_E = adj_tile.previous[0]
                if adj_tile.key_tile_W == '*': adj_tile.key_tile_W = adj_tile.previous[0]
                if adj_tile.key_tile_S == '*': adj_tile.key_tile_S = adj_tile.previous[0]
                adj_tile.copy_direction = 'R'
                hard_reset_tiles.append(adj_tile)
            else: 
                l[1] = str(l[1])
                adj_tile.copy_direction = "".join(l) 

            ct.new_kt_N = False
            ct.new_kt_E = False
            ct.new_kt_W = False
            ct.new_kt_S = False

        else:
            if ct.terminal:
                if ct.new_kt_N: 
                    ct.key_tile_N = None
                    adj_tile.key_tile_N = opp(ct.previous[0])
                else: ct.key_tile_N = ct.previous[0]

                if ct.new_kt_E: 
                    ct.key_tile_E = None
                    adj_tile.key_tile_E = opp(ct.previous[0])
                else: ct.key_tile_E = ct.previous[0]

                if ct.new_kt_W: 
                    ct.key_tile_W = None
                    adj_tile.key_tile_W = opp(ct.previous[0])
                else: ct.key_tile_W = ct.previous[0]

                if ct.new_kt_S: 
                    ct.key_tile_S = None
                    adj_tile.key_tile_S = opp(ct.previous[0])
                else: ct.key_tile_S = ct.previous[0]
            else: 
                if ct.new_kt_N: 
                    ct.key_tile_N = None
                    adj_tile.key_tile_N = opp(ct.previous[0])
                elif ct.key_tile_N != ct.previous[0]: adj_tile.key_tile_N = opp(ct.previous[0])

                if ct.new_kt_E or (ct.original_seed and ct.key_tile_E == None): 
                    ct.key_tile_E = None
                    adj_tile.key_tile_E = opp(ct.previous[0])
                elif ct.key_tile_E != ct.previous[0]: adj_tile.key_tile_E = opp(ct.previous[0])

                if ct.new_kt_W or (ct.original_seed and ct.key_tile_W == None): 
                    ct.key_tile_W = None
                    adj_tile.key_tile_W = opp(ct.previous[0])
                elif ct.key_tile_W != ct.previous[0]: adj_tile.key_tile_W = opp(ct.previous[0])
                
                if ct.new_kt_S or (ct.original_seed and ct.key_tile_S == None): 
                    ct.key_tile_S = None
                    adj_tile.key_tile_S = opp(ct.previous[0])
                elif ct.key_tile_S != ct.previous[0]: adj_tile.key_tile_S = opp(ct.previous[0])

            # Update adjacent
            l = list(adj_tile.copy_direction)
            l[1] = int(l[1]) - 1

            if l[1]+1 == 1:
                reset_tile(adj_tile)
                
                if adj_tile.key_tile_N == '*': adj_tile.key_tile_N = None 
                if adj_tile.key_tile_E == '*': adj_tile.key_tile_E = None 
                if adj_tile.key_tile_W == '*': adj_tile.key_tile_W = None 
                if adj_tile.key_tile_S == '*': adj_tile.key_tile_S = None 
            else: 
                l[1] = str(l[1])
                adj_tile.copy_direction = "".join(l) 

        # print("Current: ", ct.next, ct.previous, ct.key_tile_N, ct.key_tile_E, ct.key_tile_W, ct.key_tile_S, ct.copy_direction)
        # print("--- Adj:", adj_tile.next, adj_tile.previous, adj_tile.key_tile_N, adj_tile.key_tile_E, adj_tile.key_tile_W, adj_tile.key_tile_S, adj_tile.copy_direction)

# RETURNS: bool for whether caps on tile should be moved
def move_caps(tile): 
    if tile.wall: return False

    total = 0
    if tile.next != None: 
        total += len(tile.next)

    if tile.previous != None: 
        total += len(tile.previous)

    if len(tile.caps) == (total - 1): return True
    return False

# Copies a tile from current location to new subassembly
def copy_tile(tile, d, ps):
    pseudo_seed = None
    tile.status = "W"

    new_info = []

    if tile.next != None: 
        for i in tile.next: new_info.append(i)
    if tile.previous != None:
        new_info.append(tile.previous[0])

    tile_to_copy = Tile(None, new_info)

    tile_to_copy.key_tile_N = tile.key_tile_N
    tile_to_copy.key_tile_E = tile.key_tile_E
    tile_to_copy.key_tile_W = tile.key_tile_W
    tile_to_copy.key_tile_S = tile.key_tile_S

    tile_to_copy.terminal = tile.terminal
    tile_to_copy.caps = []

    if tile == ps: 
        tile_to_copy.pseudo_seed = True

        if tile.key_tile_N == None: tile_to_copy.new_kt_N = True
        if tile.key_tile_E == None: tile_to_copy.new_kt_E = True
        if tile.key_tile_W == None: tile_to_copy.new_kt_W = True
        if tile.key_tile_S == None: tile_to_copy.new_kt_S = True
    else: 
        tile_to_copy.new_kt_N = False
        tile_to_copy.new_kt_E = False
        tile_to_copy.new_kt_W = False
        tile_to_copy.new_kt_S = False

    if tile.original_seed: 
        if tile.key_tile_N == None: tile.new_kt_N = True
        if tile.key_tile_E == None: tile.new_kt_E = True
        if tile.key_tile_W == None: tile.new_kt_W = True
        if tile.key_tile_S == None: tile.new_kt_S = True

        tile.copied = True
        tile_to_copy.copied = True

    if tile.copied == True: tile_to_copy.copied = True

    tile.transfer = tile_to_copy
    
    # North
    if d == "N":
        while tile.key_tile_N != None:
            neighbor = retrieve_tile(tile, tile.key_tile_N[0])

            neighbor.transfer = tile.transfer
            tile.transfer = None

            if tile.key_tile_N[0] == 'N': 
                neighbor.temp = neighbor.S
                neighbor.S = 'W'
            if tile.key_tile_N[0] == 'E': 
                neighbor.temp = neighbor.W
                neighbor.W = 'W'
            if tile.key_tile_N[0] == 'W': 
                neighbor.temp = neighbor.E
                neighbor.E = 'W'
            if tile.key_tile_N[0] == 'S':
                neighbor.temp = neighbor.N 
                neighbor.N = 'W'

            tile = neighbor

        if tile.tile_to_N == None:
            tile_to_place = tile.transfer
            if "S" in tile_to_place.next:
                tile_to_place.next.remove("S")
            if len(tile_to_place.next) == 0: tile_to_place.next = None 
            # tile_to_place.previous = ["S"]
            tile.tile_to_N = tile_to_place
            tile_to_place.tile_to_S = tile

            tile.N, tile_to_place.S = None, 'N'

            tile.wall, tile_to_place.wall = True, True

            if tile.key_tile_S[0] == 'N': tile.N = 'M'
            if tile.key_tile_S[0] == 'E': tile.E = 'M'
            if tile.key_tile_S[0] == 'W': tile.W = 'M'
            if tile.key_tile_S[0] == 'S': tile.S = 'M'

            tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
            tile_to_place.new_p = ['S']
            if tile.new_n == None: tile.new_n = ['N']
            else: tile.new_n.append('N')
            # tile.new_p = copy.copy(tile.previous)

        else: 
            adj_tile = tile.tile_to_N
            adj_tile.S = 'W'
            adj_tile.transfer = tile.transfer
            tile.transfer = None
            tile = adj_tile
            tile_placed = False

            while not tile_placed:
                if 'N' in tile.next and 'N' not in tile.caps:
                    if tile.tile_to_N == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "S" in tile_to_place.next:
                            tile_to_place.next.remove("S")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["S"]
                        tile_to_place.tile_to_S = tile
                        tile.tile_to_N = tile_to_place

                        tile.N = 'N'
                        tile_to_place.S = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('N')

                        if tile.previous == None: tile.S = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'N')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.S
                        neighbor.S = 'W'

                        tile = neighbor

                elif 'E' in tile.next and 'E' not in tile.caps:
                    if tile.tile_to_E == None:
                        # Place the tile
                        tile_to_place = tile.transfer

                        if "W" in tile_to_place.next:
                            tile_to_place.next.remove("W")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["W"]
                        tile_to_place.tile_to_W = tile
                        tile.tile_to_E = tile_to_place

                        tile.E = 'N'
                        tile_to_place.W = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('E')

                        if tile.previous == None: tile.S = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'E')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.W
                        neighbor.W = 'W'

                        tile = neighbor

                elif 'W' in tile.next and 'W' not in tile.caps:
                    if tile.tile_to_W == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "E" in tile_to_place.next:
                            tile_to_place.next.remove("E")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["E"]
                        tile_to_place.tile_to_E = tile
                        tile.tile_to_W = tile_to_place

                        tile.W = 'N'
                        tile_to_place.E = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('W')

                        if tile.previous == None: tile.S = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'W')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.E
                        neighbor.E = 'W'

                        tile = neighbor

                elif 'S' in tile.next and 'S' not in tile.caps:
                    if tile.tile_to_S == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "N" in tile_to_place.next:
                            tile_to_place.next.remove("N")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["N"]
                        tile_to_place.tile_to_N = tile
                        tile.tile_to_S = tile_to_place

                        tile.S = 'N'
                        tile_to_place.N = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('S')

                        if tile.previous == None: tile.S = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'S')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.N
                        neighbor.N = 'W'

                        tile = neighbor

        tile.transfer = None
        breadcrumb_direction = breadcrumb_trail(tile)
        if breadcrumb_direction == 'N': 
            tile.N = 'M'
        if breadcrumb_direction == 'E': 
            tile.E = 'M'
        if breadcrumb_direction == 'W': 
            tile.W = 'M'
        if breadcrumb_direction == 'S': 
            tile.S = 'M'

        prev_tile = retrieve_tile(tile, breadcrumb_direction)

        if len(tile.caps) == num_dirs(tile) and tile.key_tile_S == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:

                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        while prev_tile.status != 'W':
            breadcrumb_direction = breadcrumb_trail(tile)

            if breadcrumb_direction == 'N':
                tile.N = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'E':
                tile.E = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'W':
                tile.W = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'S':
                tile.S = tile.temp
                tile.temp = None

            # Handle caps
            if move_caps(tile):
                prev_tile.caps.append(opp(breadcrumb_direction))
                tile.caps = []

            # print(tile.next, tile.previous, tile.caps)
            if len(tile.caps) == num_dirs(tile) and tile.key_tile_S == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:

                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

            breadcrumb_direction = breadcrumb_trail(prev_tile)

            if breadcrumb_direction == 'N':
                prev_tile.N = 'M'
            if breadcrumb_direction == 'E':
                prev_tile.E = 'M'
            if breadcrumb_direction == 'W':
                prev_tile.W = 'M'
            if breadcrumb_direction == 'S':
                prev_tile.S = 'M'

            tile = prev_tile
            prev_tile = retrieve_tile(tile, breadcrumb_direction)

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_S == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:

                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        breadcrumb_direction = breadcrumb_trail(tile)


        if breadcrumb_direction == 'N':
            tile.N = 'N'
        if breadcrumb_direction == 'E':
            tile.E = 'N'
        if breadcrumb_direction == 'W':
            tile.W = 'N'
        if breadcrumb_direction == 'S':
            tile.S = 'N'

        prev_tile.status = 'F'

    # East
    if d == "E":
        while tile.key_tile_E != None:
            neighbor = retrieve_tile(tile, tile.key_tile_E[0])

            neighbor.transfer = tile.transfer
            tile.transfer = None

            if tile.key_tile_E[0] == "N": 
                neighbor.temp = neighbor.S
                neighbor.S = "W"
            if tile.key_tile_E[0] == "E": 
                neighbor.temp = neighbor.W
                neighbor.W = "W"
            if tile.key_tile_E[0] == "W": 
                neighbor.temp = neighbor.E
                neighbor.E = "W"
            if tile.key_tile_E[0] == "S":
                neighbor.temp = neighbor.N 
                neighbor.N = "W"

            tile = neighbor
        
        if tile.tile_to_E == None:

            tile_to_place = tile.transfer
            if "W" in tile_to_place.next:
                tile_to_place.next.remove("W")
            if len(tile_to_place.next) == 0: tile_to_place.next = None 
            # tile_to_place.previous = ["W"]
            tile_to_place.tile_to_W = tile
            tile.tile_to_E = tile_to_place

            tile.E, tile_to_place.W = None, 'N'

            tile.wall, tile_to_place.wall = True, True

            if tile.key_tile_W[0] == 'N': tile.N = 'M'
            if tile.key_tile_W[0] == 'E': tile.E = 'M'
            if tile.key_tile_W[0] == 'W': tile.W = 'M'
            if tile.key_tile_W[0] == 'S': tile.S = 'M'

            tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
            tile_to_place.new_p = ['W']
            if tile.new_n == None: tile.new_n = ['E']
            else: tile.new_n.append('E')
            # tile.new_p = copy.copy(tile.previous)
        
        else:
            adj_tile = tile.tile_to_E
            adj_tile.W = 'W'
            adj_tile.transfer = tile.transfer
            tile = adj_tile
            tile_placed = False


            while not tile_placed:

                if 'N' in tile.next and 'N' not in tile.caps:
                    if tile.tile_to_N == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "S" in tile_to_place.next:
                            tile_to_place.next.remove("S")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["S"]
                        tile_to_place.tile_to_S = tile
                        tile.tile_to_N = tile_to_place

                        tile.N = 'N'
                        tile_to_place.S = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('N')

                        if tile.previous == None: tile.W = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'N')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.S
                        neighbor.S = 'W'

                        tile = neighbor

                elif 'E' in tile.next and 'E' not in tile.caps:
                    if tile.tile_to_E == None:
                        # Place the tile
                        tile_to_place = tile.transfer

                        if "W" in tile_to_place.next:
                            tile_to_place.next.remove("W")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["W"]
                        tile_to_place.tile_to_W = tile
                        tile.tile_to_E = tile_to_place

                        tile.E = 'N'
                        tile_to_place.W = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('E')
                            
                        if tile.previous == None: tile.W = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'E')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.W
                        neighbor.W = 'W'

                        tile = neighbor

                elif 'W' in tile.next and 'W' not in tile.caps:
                    if tile.tile_to_W == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "E" in tile_to_place.next:
                            tile_to_place.next.remove("E")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["E"]
                        tile_to_place.tile_to_E = tile
                        tile.tile_to_W = tile_to_place

                        tile.W = 'N'
                        tile_to_place.E = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False
                        
                        if tile_to_place.terminal: 
                            tile.caps.append('W')
                            
                        if tile.previous == None: tile.W = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'W')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.E
                        neighbor.E = 'W'

                        tile = neighbor

                elif 'S' in tile.next and 'S' not in tile.caps:
                    if tile.tile_to_S == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "N" in tile_to_place.next:
                            tile_to_place.next.remove("N")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["N"]
                        tile_to_place.tile_to_N = tile
                        tile.tile_to_S = tile_to_place

                        tile.S = 'N'
                        tile_to_place.N = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('S')
                            
                        if tile.previous == None: tile.W = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'S')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.N
                        neighbor.N = 'W'

                        tile = neighbor

        tile.transfer = None
        breadcrumb_direction = breadcrumb_trail(tile)
        if breadcrumb_direction == 'N': 
            tile.N = 'M'
        if breadcrumb_direction == 'E': 
            tile.E = 'M'
        if breadcrumb_direction == 'W': 
            tile.W = 'M'
        if breadcrumb_direction == 'S': 
            tile.S = 'M'

        prev_tile = retrieve_tile(tile, breadcrumb_direction)

        if len(tile.caps) == num_dirs(tile) and tile.key_tile_W == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        while prev_tile.status != 'W':
            breadcrumb_direction = breadcrumb_trail(tile)

            if breadcrumb_direction == 'N':
                tile.N = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'E':
                tile.E = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'W':
                tile.W = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'S':
                tile.S = tile.temp
                tile.temp = None

            # Handle caps
            if move_caps(tile):
                prev_tile.caps.append(opp(breadcrumb_direction))
                tile.caps = []

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_W == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

            breadcrumb_direction = breadcrumb_trail(prev_tile)

            if breadcrumb_direction == 'N':
                prev_tile.N = 'M'
            if breadcrumb_direction == 'E':
                prev_tile.E = 'M'
            if breadcrumb_direction == 'W':
                prev_tile.W = 'M'
            if breadcrumb_direction == 'S':
                prev_tile.S = 'M'

            tile = prev_tile
            prev_tile = retrieve_tile(tile, breadcrumb_direction)

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_W == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        breadcrumb_direction = breadcrumb_trail(tile)

        if breadcrumb_direction == 'N':
            tile.N = 'N'
        if breadcrumb_direction == 'E':
            tile.E = 'N'
        if breadcrumb_direction == 'W':
            tile.W = 'N'
        if breadcrumb_direction == 'S':
            tile.S = 'N'

        prev_tile.status = 'F'


    # West
    if d == "W":
        while tile.key_tile_W != None:
            neighbor = retrieve_tile(tile, tile.key_tile_W[0])

            neighbor.transfer = tile.transfer
            tile.transfer = None

            if tile.key_tile_W[0] == "N": 
                neighbor.temp = neighbor.S
                neighbor.S = "W"
            if tile.key_tile_W[0] == "E": 
                neighbor.temp = neighbor.W
                neighbor.W = "W"
            if tile.key_tile_W[0] == "W": 
                neighbor.temp = neighbor.E
                neighbor.E = "W"
            if tile.key_tile_W[0] == "S":
                neighbor.temp = neighbor.N 
                neighbor.N = "W"

            tile = neighbor

        if tile.tile_to_W == None:
            tile_to_place = tile.transfer
            if "E" in tile_to_place.next:
                tile_to_place.next.remove("E")
            if len(tile_to_place.next) == 0: tile_to_place.next = None 
            # tile_to_place.previous = ["E"]
            tile.tile_to_W = tile_to_place
            tile_to_place.tile_to_E = tile

            tile.W, tile_to_place.E = None, 'N'

            tile.wall, tile_to_place.wall = True, True

            if tile.key_tile_E[0] == 'N': tile.N = 'M'
            if tile.key_tile_E[0] == 'E': tile.E = 'M'
            if tile.key_tile_E[0] == 'W': tile.W = 'M'
            if tile.key_tile_E[0] == 'S': tile.S = 'M'

            tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
            tile_to_place.new_p = ['E']
            if tile.new_n == None: tile.new_n = ['W']
            else: tile.new_n.append('W')
            # tile.new_p = copy.copy(tile.previous)

        else: 
            adj_tile = tile.tile_to_W
            adj_tile.E = 'W'
            adj_tile.transfer = tile.transfer
            tile = adj_tile
            tile_placed = False

            while not tile_placed:

                if 'N' in tile.next and 'N' not in tile.caps:
                    if tile.tile_to_N == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "S" in tile_to_place.next:
                            tile_to_place.next.remove("S")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["S"]
                        tile_to_place.tile_to_S = tile
                        tile.tile_to_N = tile_to_place

                        tile.N = 'N'
                        tile_to_place.S = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('N')
                            
                        if tile.previous == None: tile.E = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'N')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.S
                        neighbor.S = 'W'

                        tile = neighbor

                elif 'E' in tile.next and 'E' not in tile.caps:
                    if tile.tile_to_E == None:
                        # Place the tile
                        tile_to_place = tile.transfer

                        if "W" in tile_to_place.next:
                            tile_to_place.next.remove("W")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["W"]
                        tile_to_place.tile_to_W = tile
                        tile.tile_to_E = tile_to_place

                        tile.E = 'N'
                        tile_to_place.W = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('E')
                            
                        if tile.previous == None: tile.E = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'E')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.W
                        neighbor.W = 'W'

                        tile = neighbor

                elif 'W' in tile.next and 'W' not in tile.caps:
                    if tile.tile_to_W == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "E" in tile_to_place.next:
                            tile_to_place.next.remove("E")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["E"]
                        tile_to_place.tile_to_E = tile
                        tile.tile_to_W = tile_to_place

                        tile.W = 'N'
                        tile_to_place.E = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('W')
                            
                        if tile.previous == None: tile.E = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'W')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.E
                        neighbor.E = 'W'

                        tile = neighbor

                elif 'S' in tile.next and 'S' not in tile.caps:
                    if tile.tile_to_S == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "N" in tile_to_place.next:
                            tile_to_place.next.remove("N")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["N"]
                        tile_to_place.tile_to_N = tile
                        tile.tile_to_S = tile_to_place

                        tile.S = 'N'
                        tile_to_place.N = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('S')
                            
                        if tile.previous == None: tile.E = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'S')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.N
                        neighbor.N = 'W'

                        tile = neighbor

        tile.transfer = None
        breadcrumb_direction = breadcrumb_trail(tile)
        if breadcrumb_direction == 'N': 
            tile.N = 'M'
        if breadcrumb_direction == 'E': 
            tile.E = 'M'
        if breadcrumb_direction == 'W': 
            tile.W = 'M'
        if breadcrumb_direction == 'S': 
            tile.S = 'M'

        prev_tile = retrieve_tile(tile, breadcrumb_direction)

        if len(tile.caps) == num_dirs(tile) and tile.key_tile_E == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        while prev_tile.status != 'W':
            
            breadcrumb_direction = breadcrumb_trail(tile)

            if breadcrumb_direction == 'N':
                tile.N = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'E':
                tile.E = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'W':
                tile.W = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'S':
                tile.S = tile.temp
                tile.temp = None

            # Handle caps
            if move_caps(tile):
                prev_tile.caps.append(opp(breadcrumb_direction))
                tile.caps = []

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_E == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

            breadcrumb_direction = breadcrumb_trail(prev_tile)

            if breadcrumb_direction == 'N':
                prev_tile.N = 'M'
            if breadcrumb_direction == 'E':
                prev_tile.E = 'M'
            if breadcrumb_direction == 'W':
                prev_tile.W = 'M'
            if breadcrumb_direction == 'S':
                prev_tile.S = 'M'
            
            tile = prev_tile
            prev_tile = retrieve_tile(tile, breadcrumb_direction)

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_E == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        breadcrumb_direction = breadcrumb_trail(tile)

        if breadcrumb_direction == 'N':
            tile.N = 'N'
        if breadcrumb_direction == 'E':
            tile.E = 'N'
        if breadcrumb_direction == 'W':
            tile.W = 'N'
        if breadcrumb_direction == 'S':
            tile.S = 'N'

        prev_tile.status = 'F'

    # South
    if d == "S":
        while tile.key_tile_S != None:
            neighbor = retrieve_tile(tile, tile.key_tile_S[0])

            neighbor.transfer = tile.transfer
            tile.transfer = None

            if tile.key_tile_S[0] == "N": 
                neighbor.temp = neighbor.S
                neighbor.S = "W"
            if tile.key_tile_S[0] == "E": 
                neighbor.temp = neighbor.W
                neighbor.W = "W"
            if tile.key_tile_S[0] == "W": 
                neighbor.temp = neighbor.E
                neighbor.E = "W"
            if tile.key_tile_S[0] == "S": 
                neighbor.temp = neighbor.N
                neighbor.N = "W"

            tile = neighbor

        if tile.tile_to_S == None:
            tile_to_place = tile.transfer
            if "N" in tile_to_place.next:
                tile_to_place.next.remove("N")
            if len(tile_to_place.next) == 0: tile_to_place.next = None 
            # tile_to_place.previous = ["N"]
            tile.tile_to_S = tile_to_place
            tile_to_place.tile_to_N = tile
            tile.S, tile_to_place.N = None, 'N'

            tile.wall, tile_to_place.wall = True, True

            if tile.key_tile_N[0] == 'N': tile.N = 'M'
            if tile.key_tile_N[0] == 'E': tile.E = 'M'
            if tile.key_tile_N[0] == 'W': tile.W = 'M'
            if tile.key_tile_N[0] == 'S': tile.S = 'M'

            tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
            tile_to_place.new_p = ['N']
            if tile.new_n == None: tile.new_n = ['S']
            else: tile.new_n.append('S')
            # tile.new_p = copy.copy(tile.previous)

        else: 
            adj_tile = tile.tile_to_S
            adj_tile.N = 'W'
            adj_tile.transfer = tile.transfer
            tile = adj_tile
            tile_placed = False

            while not tile_placed:

                if 'N' in tile.next and 'N' not in tile.caps:
                    if tile.tile_to_N == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "S" in tile_to_place.next:
                            tile_to_place.next.remove("S")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["S"]
                        tile_to_place.tile_to_S = tile
                        tile.tile_to_N = tile_to_place

                        tile.N = 'N'
                        tile_to_place.S = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('N')
                            
                        if tile.previous == None: tile.N = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'N')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.S
                        neighbor.S = 'W'

                        tile = neighbor

                elif 'E' in tile.next and 'E' not in tile.caps:
                    if tile.tile_to_E == None:
                        # Place the tile
                        tile_to_place = tile.transfer

                        if "W" in tile_to_place.next:
                            tile_to_place.next.remove("W")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["W"]
                        tile_to_place.tile_to_W = tile
                        tile.tile_to_E = tile_to_place

                        tile.E = 'N'
                        tile_to_place.W = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('E')
                            
                        if tile.previous == None: tile.N = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'E')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.W
                        neighbor.W = 'W'

                        tile = neighbor

                elif 'W' in tile.next and 'W' not in tile.caps:
                    if tile.tile_to_W == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "E" in tile_to_place.next:
                            tile_to_place.next.remove("E")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["E"]
                        tile_to_place.tile_to_E = tile
                        tile.tile_to_W = tile_to_place

                        tile.W = 'N'
                        tile_to_place.E = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False
                        
                        if tile_to_place.terminal: 
                            tile.caps.append('W')
                            
                        if tile.previous == None: tile.N = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'W')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.E
                        neighbor.E = 'W'

                        tile = neighbor

                elif 'S' in tile.next and 'S' not in tile.caps:
                    if tile.tile_to_S == None:
                        # Place the tile
                        tile_to_place = tile.transfer
                        if "N" in tile_to_place.next:
                            tile_to_place.next.remove("N")
                        if len(tile_to_place.next) == 0: tile_to_place.next = None 
                        tile_to_place.previous = ["N"]
                        tile_to_place.tile_to_N = tile
                        tile.tile_to_S = tile_to_place

                        tile.S = 'N'
                        tile_to_place.N = 'N'

                        tile_placed = True

                        if tile_to_place.pseudo_seed: pseudo_seed = tile_to_place

                        # Handle caps
                        if tile_to_place.next == None: tile_to_place.terminal = True
                        else: tile_to_place.terminal = False

                        if tile_to_place.terminal: 
                            tile.caps.append('S')
                            
                        if tile.previous == None: tile.N = 'M'
                        elif tile.previous[0] == 'N': tile.N = 'M' 
                        elif tile.previous[0] == 'E': tile.E = 'M'
                        elif tile.previous[0] == 'W': tile.W = 'M'
                        elif tile.previous[0] == 'S': tile.S = 'M'

                        tile_to_place.new_n = copy.deepcopy(tile_to_place.next)
                        tile_to_place.new_p = copy.deepcopy(tile_to_place.previous)

                    else: 
                        neighbor = retrieve_tile(tile, 'S')

                        neighbor.transfer = tile.transfer
                        tile.transfer = None

                        neighbor.temp = neighbor.N
                        neighbor.N = 'W'

                        tile = neighbor

        tile.transfer = None
        breadcrumb_direction = breadcrumb_trail(tile)
        if breadcrumb_direction == 'N': 
            tile.N = 'M'
        if breadcrumb_direction == 'E': 
            tile.E = 'M'
        if breadcrumb_direction == 'W': 
            tile.W = 'M'
        if breadcrumb_direction == 'S': 
            tile.S = 'M'

        prev_tile = retrieve_tile(tile, breadcrumb_direction)

        if len(tile.caps) == num_dirs(tile) and tile.key_tile_N == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                # Pass reset through subassembly
                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        while prev_tile.status != 'W':
            breadcrumb_direction = breadcrumb_trail(tile)

            if breadcrumb_direction == 'N':
                tile.N = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'E':
                tile.E = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'W':
                tile.W = tile.temp
                tile.temp = None
            if breadcrumb_direction == 'S':
                tile.S = tile.temp
                tile.temp = None

            # Handle caps
            if move_caps(tile):
                prev_tile.caps.append(opp(breadcrumb_direction))
                tile.caps = []

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_N == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                # Pass reset through subassembly
                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

            breadcrumb_direction = breadcrumb_trail(prev_tile)

            if breadcrumb_direction == 'N':
                prev_tile.N = 'M'
            if breadcrumb_direction == 'E':
                prev_tile.E = 'M'
            if breadcrumb_direction == 'W':
                prev_tile.W = 'M'
            if breadcrumb_direction == 'S':
                prev_tile.S = 'M'

            tile = prev_tile
            prev_tile = retrieve_tile(tile, breadcrumb_direction)

            if len(tile.caps) == num_dirs(tile) and tile.key_tile_N == None and retrieve_tile(tile, breadcrumb_direction).copy_direction == d:
                # Find pseudo seed
                tile.copy_direction = '?'
                t = [tile]
                r_tile = None

                while len(t) > 0:
                    ct = t.pop()

                    if ct.copy_direction == '?':
                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None:
                                    adj_tile.copy_direction = '?' + opp(neighbor)
                                    t.append(adj_tile)

                    else: 
                        l = list(ct.copy_direction)
                        if ct.next != None: 
                            for neighbor in ct.next:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                if neighbor != l[1]: 
                                    adj_tile = retrieve_tile(ct, neighbor)
                                    if adj_tile != None:
                                        adj_tile.copy_direction = '?' + opp(neighbor)
                                        t.append(adj_tile)

                    if ct.pseudo_seed: 
                        if ct.terminal: 
                            ct.copy_direction = 'R'
                            r_tile = ct
                            hard_reset_tiles.append(ct)
                        else: ct.copy_direction = 'Y'
                    else: ct.copy_direction = None

                # Pass reset through subassembly
                if r_tile != None:
                    t = [r_tile]
                    while len(t) > 0:
                        ct = t.pop()

                        if ct.next != None: 
                            for neighbor in ct.next:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        if ct.previous != None: 
                            for neighbor in ct.previous:
                                adj_tile = retrieve_tile(ct, neighbor)
                                if adj_tile != None and adj_tile.copy_direction == None:
                                    adj_tile.copy_direction = 'r?'
                                    t.append(adj_tile)

                        ct.key_tile_N = '*'
                        ct.key_tile_E = '*'
                        ct.key_tile_W = '*'
                        ct.key_tile_S = '*'
                        if ct.copy_direction == 'r?': ct.copy_direction = 'r'

        breadcrumb_direction = breadcrumb_trail(tile)

        if breadcrumb_direction == 'N':
            tile.N = 'N'
        if breadcrumb_direction == 'E':
            tile.E = 'N'
        if breadcrumb_direction == 'W':
            tile.W = 'N'
        if breadcrumb_direction == 'S':
            tile.S = 'N'

        prev_tile.status = 'F'

    return pseudo_seed

# RETURNS: Number of subassemblies completed - total number of subassemblies attached to tile
def directions_missing(tile):
    total, count = 0, 0

    if tile.N != None: total += 1
    if tile.E != None: total += 1
    if tile.W != None: total += 1
    if tile.S != None: total += 1

    if tile.N == 'Y': count += 1
    if tile.E == 'Y': count += 1
    if tile.W == 'Y': count += 1
    if tile.S == 'Y': count += 1

    return total - count

# RETURNS: Direction to incomplete subassembly
def direction_missing(tile):
    if tile.N == 'N': 
        return 'N'
    if tile.E == 'N': 
        return 'E'
    if tile.W == 'N': 
        return 'W'
    if tile.S == 'N': 
        return 'S'
    
    return 'DONE'

# Returns len(next) + len(prev)
def num_dirs(tile):
    total = 0
    if tile.next != None: 
        total += len(tile.next)
    if tile.previous != None: 
        total += len(tile.previous)

    return total

# Returns len(next)
def num_next(tile):
    if tile.next == None: return 0
    else: return len(tile.next)

# Returns len(previous)
def num_prev(tile):
    if tile.previous == None: return 0
    else: return 1


def copy_assembly(tile, d): 
    pseudo_seed = None
    returned_pseudo_seed = None
    tile.copied = True

    if d == "N":
        pseudo_seed = tile.tile_to_N
        while tile.key_tile_S != None:
            tile = retrieve_tile(tile, tile.key_tile_S[0])
    if d == "E":
        pseudo_seed = tile.tile_to_E
        while tile.key_tile_W != None:
            tile = retrieve_tile(tile, tile.key_tile_W[0])
    if d == "W":
        pseudo_seed = tile.tile_to_W
        while tile.key_tile_E != None:
            tile = retrieve_tile(tile, tile.key_tile_E[0])
    if d == "S":
        pseudo_seed = tile.tile_to_S
        while tile.key_tile_N != None:
            tile = retrieve_tile(tile, tile.key_tile_N[0])

    starting_tile = tile
    starting_tile.first_tile = True
    while not is_assembly_finished(starting_tile):
        # copy tile
        # print("------------------- copying tile: ", tile.next, tile.previous)
        is_pseudo_seed = copy_tile(tile, d, pseudo_seed)

        if is_pseudo_seed != None: 
            returned_pseudo_seed = is_pseudo_seed

        if num_dirs(tile) == 1 and not tile.original_seed and not tile.pseudo_seed and tile != starting_tile:
            if tile.previous != None: 
                adj_tile = retrieve_tile(tile, tile.previous[0])
                if tile.previous[0] == 'N': 
                    tile.N = 'Y'
                    adj_tile.S = 'Y'
                if tile.previous[0] == 'E': 
                    tile.E = 'Y'
                    adj_tile.W = 'Y'
                if tile.previous[0] == 'W': 
                    tile.W = 'Y'
                    adj_tile.E = 'Y'
                if tile.previous[0] == 'S': 
                    tile.S = 'Y'
                    adj_tile.N = 'Y'

                tile = adj_tile
            elif tile.next != None: 
                adj_tile = retrieve_tile(tile, tile.next[0])

                if tile.next[0] == 'N': 
                    tile.N = 'Y'
                    adj_tile.S = 'Y'
                if tile.next[0] == 'E': 
                    tile.E = 'Y'
                    adj_tile.W = 'Y'
                if tile.next[0] == 'W': 
                    tile.W = 'Y'
                    adj_tile.E = 'Y'
                if tile.next[0] == 'S': 
                    tile.S = 'Y'
                    adj_tile.N = 'Y'

                tile = adj_tile

            while directions_missing(tile) == 0:
                
                # Update tile and adjacent tile, then repeat
                if tile.tile_to_S != None and directions_missing(tile.tile_to_S) > 0 and ((tile.next != None and 'S' in tile.next) or (tile.previous != None and 'S' in tile.previous)):
                    adjacent_tile = tile.tile_to_S
                    adjacent_tile.N = 'Y'

                    tile = adjacent_tile

                elif tile.tile_to_W != None and directions_missing(tile.tile_to_W) > 0 and ((tile.next != None and 'W' in tile.next) or (tile.previous != None and 'W' in tile.previous)):
                    
                    adjacent_tile = tile.tile_to_W
                    adjacent_tile.E = 'Y'

                    tile = adjacent_tile

                elif tile.tile_to_E != None and directions_missing(tile.tile_to_E) > 0 and ((tile.next != None and 'E' in tile.next) or (tile.previous != None and 'E' in tile.previous)):
                    adjacent_tile = tile.tile_to_E
                    adjacent_tile.W = 'Y'
                    
                    tile = adjacent_tile

                elif tile.tile_to_N != None and directions_missing(tile.tile_to_N) > 0 and ((tile.next != None and 'N' in tile.next) or (tile.previous != None and 'N' in tile.previous)):
                    adjacent_tile = tile.tile_to_N
                    adjacent_tile.S = 'Y'
                    
                    tile = adjacent_tile
                
                else: break

        if tile.status == 'P': pass
        elif tile.tile_to_N != None and retrieve_tile(tile, 'N').status == 'P' and ((tile.next != None and 'N' in tile.next) or (tile.previous != None and 'N' in tile.previous)): 
            # Check if in next or previous
            tile = retrieve_tile(tile, 'N')
            tile.S = 'Y'
        elif tile.tile_to_E != None and retrieve_tile(tile, 'E').status == 'P' and ((tile.next != None and 'E' in tile.next) or (tile.previous != None and 'E' in tile.previous)): 
            
            tile = retrieve_tile(tile, 'E')
            tile.W = 'Y'

        elif tile.tile_to_W != None and retrieve_tile(tile, 'W').status == 'P' and ((tile.next != None and 'W' in tile.next) or (tile.previous != None and 'W' in tile.previous)): 

            tile = retrieve_tile(tile, 'W')
            tile.E = 'Y'

        elif tile.tile_to_S != None and retrieve_tile(tile, 'S').status == 'P' and ((tile.next != None and 'S' in tile.next) or (tile.previous != None and 'S' in tile.previous)): 
        
            tile = retrieve_tile(tile, 'S')
            tile.N = 'Y'
            
        else: 
            # print("Broke:", tile.next, tile.previous)
            break


        # print('new tile to copy: ', tile.next, tile.previous)

    r_tile = None
    # Need to find pseudo seed to copy in new direction: 
    # print("Checking: ", tile.next, tile.previous, starting_tile.next, starting_tile.previous)
    if tile == starting_tile:
        tile.copy_direction = '?'
        t = [tile]

        while len(t) > 0:
            ct = t.pop()

            if ct.copy_direction == '?':
                if ct.next != None: 
                    for neighbor in ct.next:
                        adj_tile = retrieve_tile(ct, neighbor)
                        if adj_tile != None:
                            adj_tile.copy_direction = '?' + opp(neighbor)
                            t.append(adj_tile)

                if ct.previous != None: 
                    for neighbor in ct.previous:
                        adj_tile = retrieve_tile(ct, neighbor)
                        if adj_tile != None:
                            adj_tile.copy_direction = '?' + opp(neighbor)
                            t.append(adj_tile)

            else: 
                l = list(ct.copy_direction)
                if ct.next != None: 
                    for neighbor in ct.next:
                        if neighbor != l[1]: 
                            adj_tile = retrieve_tile(ct, neighbor)
                            if adj_tile != None:
                                adj_tile.copy_direction = '?' + opp(neighbor)
                                t.append(adj_tile)

                if ct.previous != None: 
                    for neighbor in ct.previous:
                        if neighbor != l[1]: 
                            adj_tile = retrieve_tile(ct, neighbor)
                            if adj_tile != None:
                                adj_tile.copy_direction = '?' + opp(neighbor)
                                t.append(adj_tile)

            if ct.pseudo_seed: 
                ct.num_times_copied += 1
                if num_dirs(ct)-1 == ct.num_times_copied: 
                    ct.copy_direction = 'r?'
                    r_tile = ct
                else: ct.copy_direction = 'Y'
            elif ct.original_seed:
                ct.num_times_copied += 1
                if num_next(ct) == ct.num_times_copied: 
                    ct.copy_direction = 'r?'
                    r_tile = ct
                else: ct.copy_direction = 'Y'
            else: ct.copy_direction = None

        # If subassembly done copying, prepare the tiles for resetting
        if r_tile != None:
            t = [r_tile]
            while len(t) > 0:
                ct = t.pop()

                if ct.copy_direction == 'r?':
                    if ct.next != None: 
                        for neighbor in ct.next:
                            adj_tile = retrieve_tile(ct, neighbor)
                            if adj_tile != None and adj_tile.copy_direction == None:
                                adj_tile.copy_direction = 'r?'
                                t.append(adj_tile)

                    if ct.previous != None: 
                        for neighbor in ct.previous:
                            adj_tile = retrieve_tile(ct, neighbor)
                            if adj_tile != None and adj_tile.copy_direction == None:
                                adj_tile.copy_direction = 'r?'
                                t.append(adj_tile)

                ct.key_tile_N = '*'
                ct.key_tile_E = '*'
                ct.key_tile_W = '*'
                ct.key_tile_S = '*'
                ct.copy_direction = 'r'

    # reset_assembly(starting_tile)
    # if returned_pseudo_seed != None:
    #     reset_assembly(returned_pseudo_seed)

    return returned_pseudo_seed


# Run simulation -----------------------------------------------------------------------------------
def run_simulation(seed_tile, stage):
    original_seed_tile = copy.deepcopy(seed_tile)

    current_stage = 1
    # dir = []
    while current_stage < stage:
        # print()
        # print("STARTING STAGE: ", current_stage)

        stack = deque()
        stack.append(seed_tile)
        while len(stack) > 0:
            cur_tile = stack.pop()
            if cur_tile.next != None: 
                for neighbor in cur_tile.next:
                    if retrieve_tile(cur_tile, neighbor).copied == False:
                        # print("D: ", neighbor)
                        # dir.append(neighbor)
                        choose_copy_direction(cur_tile, neighbor)
                        new_pseudo_seed = copy_assembly(cur_tile, neighbor)

                        if new_pseudo_seed != None: stack.append(new_pseudo_seed)

            if cur_tile.previous != None: 
                if retrieve_tile(cur_tile, cur_tile.previous[0]).copied == False:
                    # print("D: ", cur_tile.previous[0])
                    # dir.append(neighbor)
                    choose_copy_direction(cur_tile, cur_tile.previous[0])
                    new_pseudo_seed = copy_assembly(cur_tile, cur_tile.previous[0])

                    if new_pseudo_seed != None: stack.append(new_pseudo_seed)

        hard_reset()

        # print(len(dir))
        # print(dir)
        # At end of stage
        # reset_stage(seed_tile)
        # reset_keytile_directions(seed_tile)
        current_stage += 1

    for [s1, s2, s1_final, s2_final, _] in transitions:
        if s1 not in states: states.append(s1)
        if s2 not in states: states.append(s2)
        if s1_final not in states: states.append(s1_final)
        if s2_final not in states: states.append(s2_final)

    # print(states)
    # print(transitions)
    # print(affinities)

    return [seed_tile, states, transitions, affinities, original_seed_tile]