"""Résolution approchée du sac à dos 0/1 par colonie de fourmis.

Les objets sont numérotés de 1 à n dans le résultat retourné.
Le programme n'utilise que la bibliothèque standard de Python.
"""

from __future__ import annotations

import random
from math import sqrt
from typing import Sequence


def ant_colony_knapsack(
    weights: Sequence[float],
    values: Sequence[float],
    capacity: float,
    *,
    ants: int | None = None,
    iterations: int = 100,
    alpha: float = 1.0,
    beta: float = 2.0,
    evaporation: float = 0.2,
    seed: int | None = None,
) -> dict[str, object]:
    """Cherche une bonne sélection d'objets sans dépasser la capacité.

    Args:
        weights: poids positifs des objets.
        values: valeurs non négatives des objets.
        capacity: capacité maximale du sac.
        ants: nombre de fourmis par itération; par défaut max(10, n).
        iterations: nombre de cycles de construction et mise à jour.
        alpha: importance de la phéromone dans le choix d'un objet.
        beta: importance de l'heuristique dans le choix d'un objet.
        evaporation: taux d'évaporation, compris strictement entre 0 et 1.
        seed: graine facultative pour rendre l'exemple reproductible.

    Returns:
        Dictionnaire avec les numéros d'objets retenus (à partir de 1),
        la valeur totale, le poids total et le nombre d'itérations.
    """
    if len(weights) != len(values):
        raise ValueError("weights et values doivent avoir la même longueur")
    if capacity < 0:
        raise ValueError("capacity doit être positive ou nulle")
    if any(weight <= 0 for weight in weights):
        raise ValueError("Chaque poids doit être strictement positif")
    if any(value < 0 for value in values):
        raise ValueError("Chaque valeur doit être positive ou nulle")
    if iterations < 1:
        raise ValueError("iterations doit être au moins égal à 1")
    if not 0 < evaporation < 1:
        raise ValueError("evaporation doit être comprise strictement entre 0 et 1")
    if alpha < 0 or beta < 0:
        raise ValueError("alpha et beta doivent être positifs ou nuls")

    rng = random.Random(seed)
    n = len(weights)
    ant_count = ants if ants is not None else max(10, n)
    if ant_count < 1:
        raise ValueError("ants doit être au moins égal à 1")

    weights = [float(weight) for weight in weights]
    values = [float(value) for value in values]
    max_weight = max(max(weights, default=0.0), 1e-12)
    max_value = max(max(values, default=0.0), 1e-12)
    densities = [values[i] / weights[i] for i in range(n)]

    # Distance euclidienne normalisée entre objets dans l'espace (poids, valeur).
    distances = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dw = (weights[i] - weights[j]) / max_weight
            dv = (values[i] - values[j]) / max_value
            distances[i][j] = sqrt(dw * dw + dv * dv)

    # La ligne n représente le départ virtuel de chaque fourmi.
    pheromone = [[1.0] * n for _ in range(n + 1)]
    start = n
    best_items: list[int] = []
    best_value = 0.0
    best_weight = 0.0
    value_scale = max(sum(values), 1.0)
    epsilon = 1e-12

    for _ in range(iterations):
        ant_solutions: list[tuple[list[int], float, float]] = []

        for _ant in range(ant_count):
            chosen: list[int] = []
            chosen_set: set[int] = set()
            route: list[int] = []
            remaining = float(capacity)
            current = start
            total_value = 0.0
            total_weight = 0.0

            while True:
                feasible = [
                    j for j in range(n)
                    if j not in chosen_set and weights[j] <= remaining + epsilon
                ]
                if not feasible:
                    break

                desirabilities: list[float] = []
                for j in feasible:
                    distance = 0.0 if current == start else distances[current][j]
                    heuristic = max(densities[j] / (1.0 + distance), epsilon)
                    desirabilities.append(
                        (pheromone[current][j] ** alpha) * (heuristic ** beta)
                    )

                if sum(desirabilities) <= 0.0:
                    next_item = rng.choice(feasible)
                else:
                    next_item = rng.choices(
                        feasible, weights=desirabilities, k=1
                    )[0]

                chosen.append(next_item)
                chosen_set.add(next_item)
                route.append(next_item)
                remaining -= weights[next_item]
                total_value += values[next_item]
                total_weight += weights[next_item]
                current = next_item

            ant_solutions.append((route, total_value, total_weight))

            if (total_value > best_value) or (
                total_value == best_value and total_weight < best_weight
            ):
                best_items = chosen[:]
                best_value = total_value
                best_weight = total_weight

        # Evaporation: limite l'accumulation et permet d'oublier des chemins.
        for i in range(n + 1):
            for j in range(n):
                pheromone[i][j] = max(
                    pheromone[i][j] * (1.0 - evaporation), epsilon
                )

        # Renforcement des transitions parcourues, pondéré par la qualité du sac.
        for route, total_value, _total_weight in ant_solutions:
            if not route or total_value <= 0.0:
                continue
            deposit = total_value / value_scale
            previous = start
            for item in route:
                pheromone[previous][item] += deposit
                previous = item

    return {
        "selected_items": [item + 1 for item in best_items],
        "total_value": best_value,
        "total_weight": best_weight,
        "iterations": iterations,
    }


if __name__ == "__main__":
    # Exemple d'utilisation ; remplacez ces données par celles de votre instance.
    example_weights = [2, 3, 4, 5]
    example_values = [3, 4, 5, 8]
    example_capacity = 8

    solution = ant_colony_knapsack(
        example_weights,
        example_values,
        example_capacity,
        ants=10,
        iterations=100,
        seed=42,
    )
    print("Objets sélectionnés (numérotation à partir de 1) :", solution["selected_items"])
    print("Valeur totale :", solution["total_value"])
    print("Poids total :", solution["total_weight"])
