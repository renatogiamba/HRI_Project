import unified_planning
import unified_planning.engines
import unified_planning.model
import unified_planning.shortcuts
from typing import *

def generate_N_puzzle(
        n: int, tile_idx_matrix: List[List[int]]
    ) -> unified_planning.model.Problem:
    tile_type = unified_planning.shortcuts.UserType("tile")
    coord_type = unified_planning.shortcuts.UserType("coord")
    bool_type = unified_planning.shortcuts.BoolType()

    at = unified_planning.model.Fluent(
        "at", typename=bool_type,
        t=tile_type, x=coord_type, y=coord_type
    )
    empty = unified_planning.model.Fluent(
        "empty", typename=bool_type,
        x=coord_type, y=coord_type
    )
    adjacent = unified_planning.model.Fluent(
        "adjacent", typename=bool_type,
        x1=coord_type, y1=coord_type, x2=coord_type, y2=coord_type
    )

    move = unified_planning.model.InstantaneousAction(
        "move", t=tile_type, x1=coord_type, y1=coord_type, x2=coord_type, y2=coord_type
    )
    move_t = move.parameter("t")
    move_x1 = move.parameter("x1")
    move_y1 = move.parameter("y1")
    move_x2 = move.parameter("x2")
    move_y2 = move.parameter("y2")
    move.add_precondition(at(move_t, move_x1, move_y1))
    move.add_precondition(empty(move_x2, move_y2))
    move.add_precondition(adjacent(move_x1, move_y1, move_x2, move_y2))
    move.add_effect(at(move_t, move_x2, move_y2), True)
    move.add_effect(at(move_t, move_x1, move_y1), False)
    move.add_effect(empty(move_x1, move_y1), True)
    move.add_effect(empty(move_x2, move_y2), False)

    tiles = [unified_planning.model.Object(f"tile_{i}", tile_type) for i in range(1, n * n)]
    coords = [unified_planning.model.Object(f"{i}", coord_type) for i in range(1, n + 1)]

    problem = unified_planning.model.Problem(name=f"{n} Puzzle")

    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(empty, default_initial_value=False)
    problem.add_fluent(adjacent, default_initial_value=False)
    problem.add_action(move)
    problem.add_objects(tiles)
    problem.add_objects(coords)

    for i in range(n):
        for j in range(n):
            tile_idx = tile_idx_matrix[i][j]
            if tile_idx == -1:
                problem.set_initial_value(empty(coords[i], coords[j]), True)
            else:
                problem.set_initial_value(at(tiles[tile_idx], coords[i], coords[j]), True)
            if i - 1 >= 0:
                problem.set_initial_value(
                    adjacent(coords[i], coords[j], coords[i - 1], coords[j]), True
                )
            if i + 1 < n:
                problem.set_initial_value(
                    adjacent(coords[i], coords[j], coords[i + 1], coords[j]), True
                )
            if j - 1 >= 0:
                problem.set_initial_value(
                    adjacent(coords[i], coords[j], coords[i], coords[j - 1]), True
                )
            if j + 1 < n:
                problem.set_initial_value(
                    adjacent(coords[i], coords[j], coords[i], coords[j + 1]), True
                )
            
            if i == n - 1 and j == n - 1:
                problem.add_goal(empty(coords[i], coords[j]))
            else:
                tile_idx = i * n + j
                problem.add_goal(at(tiles[tile_idx], coords[i], coords[j]))
    
    return problem

def solve_N_puzzle(n_puzzle_problem: unified_planning.model.Problem) -> List[str]:
    unified_planning.shortcuts.get_environment().credits_stream = None
    with unified_planning.shortcuts.OneshotPlanner(name="fast-downward") as planner:
        result = planner.solve(n_puzzle_problem)
        if result.status == unified_planning.engines\
        .PlanGenerationResultStatus.SOLVED_SATISFICING or \
        result.status == unified_planning.engines\
        .PlanGenerationResultStatus.SOLVED_OPTIMALLY:
            actions = str(result.plan).split("\n    ")
        else:
            actions = []
    
    return actions
