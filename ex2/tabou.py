from collections import deque


DEMANDS = [4, 5, 8]
CAPACITIES = [8, 9]
COSTS = [
    [5, 3, 4],
    [6, 7, 2],
]
INITIAL = [
    [4, 0, 4],
    [0, 5, 4],
]


def total_cost(allocation):
    return sum(
        allocation[depot][store] * COSTS[depot][store]
        for depot in range(len(CAPACITIES))
        for store in range(len(DEMANDS))
    )


def is_valid(allocation):
    if any(sum(allocation[d]) != CAPACITIES[d] for d in range(len(CAPACITIES))):
        return False
    if any(
        sum(allocation[d][s] for d in range(len(CAPACITIES))) != DEMANDS[s]
        for s in range(len(DEMANDS))
    ):
        return False
    return all(amount >= 0 for depot in allocation for amount in depot)


def neighbors(allocation):
    result = []
    for first_depot in range(len(CAPACITIES)):
        for second_depot in range(first_depot + 1, len(CAPACITIES)):
            for first_store in range(len(DEMANDS)):
                if allocation[first_depot][first_store] == 0:
                    continue
                for second_store in range(len(DEMANDS)):
                    if (
                        first_store != second_store
                        and allocation[second_depot][second_store] > 0
                    ):
                        candidate = [row[:] for row in allocation]
                        candidate[first_depot][first_store] -= 1
                        candidate[second_depot][first_store] += 1
                        candidate[second_depot][second_store] -= 1
                        candidate[first_depot][second_store] += 1
                        result.append(candidate)
    return result


def tabu_search(initial, iterations=20, tabu_size=5):
    if not is_valid(initial):
        raise ValueError("La solution initiale ne respecte pas les demandes et capacités.")

    current = [row[:] for row in initial]
    best = [row[:] for row in initial]
    tabu = deque([tuple(map(tuple, current))], maxlen=tabu_size)

    for _ in range(iterations):
        candidates = [
            candidate
            for candidate in neighbors(current)
            if tuple(map(tuple, candidate)) not in tabu
            or total_cost(candidate) < total_cost(best)
        ]
        if not candidates:
            break

        current = min(candidates, key=total_cost)
        tabu.append(tuple(map(tuple, current)))
        if total_cost(current) < total_cost(best):
            best = [row[:] for row in current]

    return best


def main():
    solution = tabu_search(INITIAL)
    print("Containers livrés (lignes D1/D2, colonnes M1/M2/M3) :")
    for depot, quantities in enumerate(solution, start=1):
        print(f"D{depot}: {quantities}")
    print(f"Coût total : {total_cost(solution)}")


if __name__ == "__main__":
    main()
