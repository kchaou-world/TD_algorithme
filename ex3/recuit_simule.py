import math
import random


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


def swap_neighbors(route):
    result = []
    for first in range(1, len(route) - 1):
        for second in range(first + 1, len(route)):
            candidate = route[:]
            candidate[first], candidate[second] = candidate[second], candidate[first]
            if is_valid_route(candidate):
                result.append(candidate)
    return result


def simulated_annealing(initial, iterations=5, initial_temperature=100.0, cooling=0.5, seed=42):
    if not is_valid_route(initial):
        raise ValueError("La tournée initiale n'est pas valide.")

    generator = random.Random(seed)
    current = initial[:]
    best = current[:]
    temperature = initial_temperature
    history = []

    for iteration in range(1, iterations + 1):
        candidates = swap_neighbors(current)
        if not candidates:
            break

        candidate = generator.choice(candidates)
        delta = route_cost(candidate) - route_cost(current)
        accepted = delta <= 0 or generator.random() < math.exp(-delta / temperature)
        if accepted:
            current = candidate
        if route_cost(current) < route_cost(best):
            best = current[:]

        history.append(
            (iteration, candidate, route_cost(candidate), accepted, temperature, current[:])
        )
        temperature *= cooling

    return best, history


def main():
    best, history = simulated_annealing(INITIAL)
    for iteration, candidate, cost, accepted, temperature, current in history:
        decision = "acceptée" if accepted else "rejetée"
        print(
            f"Itération {iteration}: candidate={candidate + [candidate[0]]}, "
            f"coût={cost}, {decision}, T={temperature:g}, état={current + [current[0]]}"
        )
    print(f"Meilleure tournée : {best + [best[0]]}")
    print(f"Coût : {route_cost(best)}")


if __name__ == "__main__":
    main()
