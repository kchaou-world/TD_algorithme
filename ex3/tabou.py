from collections import deque

from common import is_valid_route, route_cost, two_opt_neighbors

DISTANCES = [
    [None, 14, 15, None, None, None, None, 17],
    [14, None, 13, 14, 20, None, None, 21],
    [15, 13, None, 11, 21, 17, 9, 9],
    [None, 14, 11, None, 11, 10, 8, 20],
    [None, 20, 21, 11, None, 15, 18, None],
    [None, None, 17, 10, 15, None, 9, None],
    [None, None, 9, 8, 18, 9, None, 13],
    [17, 21, 9, 20, None, None, 13, None],
]
INITIAL = [1, 2, 3, 4, 5, 6, 7, 8]

def route_cost(route):
    total = 0
    for index, city in enumerate(route):
        next_city = route[(index + 1) % len(route)]
        distance = DISTANCES[city - 1][next_city - 1]
        if distance is None:
            raise ValueError(f"Aucune liaison entre les villes {city} et {next_city}.")
        total += distance
    return total


def is_valid_route(route):
    return (
        len(route) == len(DISTANCES)
        and set(route) == set(range(1, len(DISTANCES) + 1))
        and all(
            DISTANCES[route[index] - 1][route[(index + 1) % len(route)] - 1]
            is not None
            for index in range(len(route))
        )
    )


def two_opt_neighbors(route):
    result = []
    for first in range(1, len(route) - 1):
        for last in range(first + 1, len(route)):
            candidate = (
                route[:first]
                + list(reversed(route[first : last + 1]))
                + route[last + 1 :]
            )
            if is_valid_route(candidate):
                result.append(candidate)
    return result


def tabu_search(initial, iterations=20, tabu_size=5):
    if not is_valid_route(initial):
        raise ValueError("La tournée initiale n'est pas valide.")

    current = initial[:]
    best = initial[:]
    tabu = deque([tuple(current)], maxlen=tabu_size)
    history = []

    for iteration in range(1, iterations + 1):
        candidates = [
            route
            for route in two_opt_neighbors(current)
            if tuple(route) not in tabu or route_cost(route) < route_cost(best)
        ]
        if not candidates:
            break

        current = min(candidates, key=route_cost)
        tabu.append(tuple(current))
        if route_cost(current) < route_cost(best):
            best = current[:]
        history.append((iteration, current[:], route_cost(current), best[:], route_cost(best)))

    return best, history


def main():
    best, history = tabu_search(INITIAL)
    for iteration, route, cost, _, _ in history:
        print(f"Itération {iteration}: {route + [route[0]]}, coût={cost}")
    print(f"Meilleure tournée : {best + [best[0]]}")
    print(f"Coût : {route_cost(best)}")


if __name__ == "__main__":
    main()
