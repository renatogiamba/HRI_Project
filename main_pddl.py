import pddl_planning

if __name__ == "__main__":
    tile_matrix = [
        [4,3],
        [1,2]

    ]

    problem = pddl_planning.generate_N_puzzle(tile_matrix)
    print(problem)
    actions = pddl_planning.solve_N_puzzle(problem)
    print(actions)
