import pddl_planning

if __name__ == "__main__":
    tile_idx_matrix = [
        [12, 0, 10, 4],
        [9, 13, 14, 5],
        [1, -1, 3, 6],
        [8, 11, 7, 2]
    ]

    problem = pddl_planning.generate_N_puzzle(4, tile_idx_matrix)
    actions = pddl_planning.solve_N_puzzle(problem)
