## Exercice 2

Une solution optimale est :

- D1 livre 3 containers à M1, 5 à M2 et 0 à M3 (8 containers).
- D2 livre 1 container à M1, 0 à M2 et 8 à M3 (9 containers).
- Coût total : 3 × 5 + 5 × 3 + 1 × 6 + 8 × 2 = 52.

La recherche taboue représente les livraisons par des quantités entières. Un voisin échange un container entre deux magasins en inversant les dépôts d'origine; les demandes et capacités restent donc satisfaites. La solution initiale utilisée par le programme est valide, et le coût est calculé par container.

## Exercice 3

La tournée initiale 1-2-3-4-5-6-7-8-1 est réalisable et coûte 103.

1. Recherche taboue : avec un voisinage 2-opt, une liste taboue de taille 5 et 20 itérations, la meilleure tournée obtenue est 1-2-4-5-6-7-3-8-1, de coût 98.
2. Recuit simulé : cinq itérations, graine 42 et température initiale 100 divisée par 2 à chaque itération (100, 50, 25, 12.5, 6.25). La meilleure tournée conservée est la tournée initiale 1-2-3-4-5-6-7-8-1, de coût 103.
3. Algorithme génétique : population de 100 tournées, sélection par tournoi, croisement d'ordre, mutation par échange avec une probabilité de 0.15, élitisme et 200 générations. La meilleure tournée obtenue est 1-8-3-7-6-5-4-2-1, de coût 98.
