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



def order_crossover(first, second, generator):
    left, right = sorted(generator.sample(range(1, len(first)), 2))
    child = [None] * len(first)
    child[0] = 1
    child[left:right] = first[left:right]

    remaining = [city for city in second[1:] if city not in child]
    positions = [index for index in range(1, len(child)) if child[index] is None]
    for index, city in zip(positions, remaining):
        child[index] = city
    return child


def genetic_algorithm(
    initial,
    population_size=100,
    generations=200,
    mutation_rate=0.15,
    seed=42,
):
    if not is_valid_route(initial):
        raise ValueError("La tournée initiale n'est pas valide.")
    if population_size < 2:
        raise ValueError("La taille de la population doit être supérieure ou égale à 2.")

    generator = random.Random(seed)
    population = [initial[:]]
    while len(population) < population_size:
        candidate = initial[:]
        tail = candidate[1:]
        generator.shuffle(tail)
        candidate[1:] = tail
        if is_valid_route(candidate):
            population.append(candidate)

    def tournament():
        contestants = generator.sample(population, 3)
        return min(contestants, key=route_cost)

    for _ in range(generations):
        next_population = [min(population, key=route_cost)[:]]
        while len(next_population) < population_size:
            child = order_crossover(tournament(), tournament(), generator)
            if generator.random() < mutation_rate:
                first, second = generator.sample(range(1, len(child)), 2)
                child[first], child[second] = child[second], child[first]
            if is_valid_route(child):
                next_population.append(child)
        population = next_population

    return min(population, key=route_cost)


def main():
    best = genetic_algorithm(INITIAL)
    print(f"Meilleure tournée : {best + [best[0]]}")
    print(f"Coût : {route_cost(best)}")


if __name__ == "__main__":
    main()
