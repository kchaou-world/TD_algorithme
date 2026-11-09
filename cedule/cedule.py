"""
Ordonnancement des maintenances par algorithme génétique.

Chaque gène représente, pour une unité, les quatre intervalles de maintenance.
Le programme utilise uniquement la bibliothèque standard de Python.
"""

from __future__ import annotations

import itertools
import random
from collections.abc import Sequence


# Données du problème (puissances en MW).
CAPACITES: tuple[int, ...] = (20, 15, 35, 40, 15, 15, 10)
DEMANDES: tuple[int, ...] = (80, 90, 65, 70)
CAPACITE_TOTALE: int = 150

# Configuration admise pour chacune des sept unités.
CONFIGURATIONS: tuple[tuple[str, ...], ...] = (
    ("1100", "0110", "0011"),
    ("1100", "0110", "0011"),
    ("1000", "0100", "0010", "0001"),
    ("1000", "0100", "0010", "0001"),
    ("1000", "0100", "0010", "0001"),
    ("1000", "0100", "0010", "0001"),
    ("1000", "0100", "0010", "0001"),
)

# Paramètres de l'algorithme génétique.
TAILLE_POPULATION: int = 50
NOMBRE_GENERATIONS: int = 100
PROBABILITE_CROISEMENT: float = 0.8
PROBABILITE_MUTATION: float = 0.3
ELITISME: int = 1
GRAINE_ALEATOIRE: int = 42


def chromosome_valide(chromosome: Sequence[str]) -> bool:
    """Indique si les sept gènes respectent les configurations autorisées."""
    return (
        len(chromosome) == len(CONFIGURATIONS)
        and all(gene in options for gene, options in zip(chromosome, CONFIGURATIONS))
    )


def _verifier_chromosome_binaire(chromosome: Sequence[str]) -> None:
    """Vérifie la forme minimale nécessaire au calcul des réserves."""
    if len(chromosome) != len(CAPACITES):
        raise ValueError(f"Un chromosome doit contenir {len(CAPACITES)} gènes.")
    if any(
        len(gene) != len(DEMANDES) or any(bit not in "01" for bit in gene)
        for gene in chromosome
    ):
        raise ValueError("Chaque gène doit être une chaîne binaire de quatre bits.")


def creer_chromosome(rng: random.Random) -> list[str]:
    """Crée une cédule en tirant un motif autorisé pour chaque unité."""
    chromosome = [rng.choice(options) for options in CONFIGURATIONS]
    assert chromosome_valide(chromosome)
    return chromosome


def creer_population(taille: int, rng: random.Random) -> list[list[str]]:
    """Crée une population initiale de chromosomes valides."""
    if taille < 1:
        raise ValueError("La taille de la population doit être positive.")
    return [creer_chromosome(rng) for _ in range(taille)]


def calculer_reserves(chromosome: Sequence[str]) -> list[int]:
    """Calcule la réserve de puissance de chacun des quatre intervalles."""
    _verifier_chromosome_binaire(chromosome)
    reserves: list[int] = []

    for intervalle, demande in enumerate(DEMANDES):
        puissance_indisponible = sum(
            capacite
            for capacite, gene in zip(CAPACITES, chromosome)
            if gene[intervalle] == "1"
        )
        reserves.append(CAPACITE_TOTALE - puissance_indisponible - demande)

    return reserves


def objectif(chromosome: Sequence[str]) -> int:
    """Retourne la plus petite réserve, objectif à maximiser."""
    return min(calculer_reserves(chromosome))


def fitness(chromosome: Sequence[str]) -> float:
    """
    Convertit la qualité en poids non négatif pour la roulette.

    Une solution faisable reçoit 1 + sa réserve minimale. Une solution
    infaisable reçoit une valeur strictement inférieure à 1, qui diminue
    avec la somme des déficits de réserve. Un chromosome invalide vaut 0.
    """
    if not chromosome_valide(chromosome):
        return 0.0

    reserves = calculer_reserves(chromosome)
    deficits = sum(max(0, -reserve) for reserve in reserves)
    if deficits:
        return 1.0 / (1.0 + deficits)
    return 1.0 + min(reserves)


def cle_evaluation(chromosome: Sequence[str]) -> tuple[int, int, int]:
    """Classe les solutions: faisabilité, objectif, puis déficits cumulés."""
    if not chromosome_valide(chromosome):
        return (0, -10**9, -10**9)

    reserves = calculer_reserves(chromosome)
    deficits = sum(max(0, -reserve) for reserve in reserves)
    if deficits == 0:
        return (1, min(reserves), 0)
    return (0, -deficits, min(reserves))


def selection_loterie(
    population: Sequence[Sequence[str]],
    valeurs_fitness: Sequence[float],
    rng: random.Random,
) -> list[str]:
    """Tire un individu avec une probabilité proportionnelle à sa fitness."""
    if not population:
        raise ValueError("La population ne peut pas être vide.")
    if len(population) != len(valeurs_fitness):
        raise ValueError("Il faut une fitness pour chaque individu.")

    poids = [max(0.0, float(valeur)) for valeur in valeurs_fitness]
    total = sum(poids)
    if total <= 0.0:
        # Secours uniforme lorsque tous les poids sont nuls.
        return list(rng.choice(population))

    tirage = rng.random() * total
    cumul = 0.0
    for individu, poids_individu in zip(population, poids):
        cumul += poids_individu
        if tirage < cumul:
            return list(individu)

    # Protection contre les arrondis flottants.
    return list(population[-1])


def croisement_un_point(
    parent1: Sequence[str],
    parent2: Sequence[str],
    rng: random.Random,
) -> tuple[list[str], list[str]]:
    """Croise deux parents en un point sans changer les domaines des unités."""
    if not chromosome_valide(parent1) or not chromosome_valide(parent2):
        raise ValueError("Le croisement exige deux chromosomes valides.")

    point = rng.randint(1, len(CONFIGURATIONS) - 1)
    enfant1 = list(parent1[:point]) + list(parent2[point:])
    enfant2 = list(parent2[:point]) + list(parent1[point:])

    # Chaque position garde un gène provenant de la même unité d'un parent.
    assert chromosome_valide(enfant1)
    assert chromosome_valide(enfant2)
    return enfant1, enfant2


def mutation_inversion(
    chromosome: Sequence[str],
    rng: random.Random,
) -> list[str]:
    """
    Inverse un segment de gènes d'une même classe d'unités.

    Les unités 1-2 et 3-7 ont des domaines différents. Le segment inversé
    reste donc à l'intérieur de l'un de ces deux groupes. Si l'ordre des
    gènes d'un groupe ne peut pas changer le chromosome (motifs identiques),
    le calendrier d'une unité est renversé dans le temps; les configurations
    fournies restent autorisées par cette inversion.
    """
    if not chromosome_valide(chromosome):
        raise ValueError("La mutation exige un chromosome valide.")

    enfant = list(chromosome)
    groupes = ((0, 2), (2, 7))  # bornes de fin exclusives
    segments = [
        (debut, fin)
        for debut_groupe, fin_groupe in groupes
        for debut in range(debut_groupe, fin_groupe)
        for fin in range(debut + 2, fin_groupe + 1)
        if enfant[debut:fin] != list(reversed(enfant[debut:fin]))
    ]

    if segments:
        debut, fin = rng.choice(segments)
        enfant[debut:fin] = reversed(enfant[debut:fin])
    else:
        # Une inversion d'un gène entier équivaut à renverser les quatre
        # intervalles de son calendrier; les domaines sont symétriques.
        unites_inversables = [
            indice
            for indice, gene in enumerate(enfant)
            if gene != gene[::-1] and gene[::-1] in CONFIGURATIONS[indice]
        ]
        if not unites_inversables:
            raise RuntimeError("Aucune inversion valide ne peut modifier ce chromosome.")
        indice = rng.choice(unites_inversables)
        enfant[indice] = enfant[indice][::-1]

    assert chromosome_valide(enfant)
    assert enfant != list(chromosome)
    return enfant


def algorithme_genetique(
    taille_population: int = TAILLE_POPULATION,
    nombre_generations: int = NOMBRE_GENERATIONS,
    probabilite_croisement: float = PROBABILITE_CROISEMENT,
    probabilite_mutation: float = PROBABILITE_MUTATION,
    elitisme: int = ELITISME,
    graine: int = GRAINE_ALEATOIRE,
) -> list[str]:
    """Exécute l'algorithme génétique et renvoie la meilleure cédule trouvée."""
    if taille_population < 2:
        raise ValueError("La population doit contenir au moins deux individus.")
    if nombre_generations < 0:
        raise ValueError("Le nombre de générations ne peut pas être négatif.")
    if not 0 <= probabilite_croisement <= 1:
        raise ValueError("La probabilité de croisement doit être entre 0 et 1.")
    if not 0 <= probabilite_mutation <= 1:
        raise ValueError("La probabilité de mutation doit être entre 0 et 1.")
    if not 1 <= elitisme < taille_population:
        raise ValueError("L'élitisme doit conserver au moins 1 individu et moins que la population.")

    rng = random.Random(graine)
    population = creer_population(taille_population, rng)
    meilleur = max(population, key=cle_evaluation)

    for _ in range(nombre_generations):
        valeurs_fitness = [fitness(individu) for individu in population]
        meilleur_generation = max(population, key=cle_evaluation)
        if cle_evaluation(meilleur_generation) > cle_evaluation(meilleur):
            meilleur = list(meilleur_generation)

        nouvelle_population = [list(meilleur) for _ in range(elitisme)]
        while len(nouvelle_population) < taille_population:
            parent1 = selection_loterie(population, valeurs_fitness, rng)
            parent2 = selection_loterie(population, valeurs_fitness, rng)

            if rng.random() < probabilite_croisement:
                enfant1, enfant2 = croisement_un_point(parent1, parent2, rng)
            else:
                enfant1, enfant2 = list(parent1), list(parent2)

            for enfant in (enfant1, enfant2):
                if rng.random() < probabilite_mutation:
                    enfant = mutation_inversion(enfant, rng)
                assert chromosome_valide(enfant)
                nouvelle_population.append(enfant)
                if len(nouvelle_population) == taille_population:
                    break

        population = nouvelle_population

    meilleur_generation = max(population, key=cle_evaluation)
    if cle_evaluation(meilleur_generation) > cle_evaluation(meilleur):
        meilleur = list(meilleur_generation)

    assert chromosome_valide(meilleur)
    return list(meilleur)


def enumeration_exhaustive() -> list[str]:
    """Énumère toutes les cédules permises et renvoie la meilleure."""
    return list(max(itertools.product(*CONFIGURATIONS), key=cle_evaluation))


def afficher_solution(titre: str, chromosome: Sequence[str]) -> None:
    """Affiche les motifs de maintenance, les réserves et la faisabilité."""
    reserves = calculer_reserves(chromosome)
    faisable = all(reserve >= 0 for reserve in reserves)

    print(titre)
    for numero, gene in enumerate(chromosome, start=1):
        print(f"  Unité {numero} : {gene}")
    print("  Réserves (MW) :", ", ".join(map(str, reserves)))
    print(f"  Réserve minimale (MW) : {min(reserves)}")
    print(f"  Faisable : {'oui' if faisable else 'non'}")


def main() -> None:
    """Lance l'algorithme, puis compare son résultat à l'énumération exacte."""
    meilleure_solution = algorithme_genetique()
    solution_exacte = enumeration_exhaustive()

    print("Ordonnancement des maintenances — algorithme génétique")
    print(f"Population : {TAILLE_POPULATION} | Générations : {NOMBRE_GENERATIONS}")
    print(
        "Croisement : "
        f"{PROBABILITE_CROISEMENT} | Mutation : {PROBABILITE_MUTATION} "
        f"| Élitisme : {ELITISME} | Graine : {GRAINE_ALEATOIRE}"
    )
    print()
    afficher_solution("Meilleure solution de l'algorithme génétique :", meilleure_solution)
    print()
    afficher_solution("Meilleure solution par énumération exhaustive :", solution_exacte)
    meme_objectif = objectif(meilleure_solution) == objectif(solution_exacte)
    meme_faisabilite = (
        all(r >= 0 for r in calculer_reserves(meilleure_solution))
        == all(r >= 0 for r in calculer_reserves(solution_exacte))
    )
    print()
    if meme_objectif and meme_faisabilite:
        print("Comparaison : l'algorithme génétique atteint la valeur optimale vérifiée par énumération.")
    else:
        print("Comparaison : l'algorithme génétique n'atteint pas la meilleure valeur énumérée.")


if __name__ == "__main__":
    main()
