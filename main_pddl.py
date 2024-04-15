import pddl_planning

if __name__ == "__main__":
    tile_matrix = [
        [5, 10, 8, 14],
        [2, 1, 7, 13],
        [11, 16, 12, 9],
        [4, 3, 15, 6]
    ]

    problem = pddl_planning.generate_N_puzzle(tile_matrix)
    print(problem)
    actions = pddl_planning.solve_N_puzzle(problem, True)
    print(actions)
