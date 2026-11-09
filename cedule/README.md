# Ordonnancement des maintenances par algorithme génétique

## Problème étudié

Sept unités de production doivent être planifiées sur quatre intervalles. Chaque unité suit une configuration de maintenance autorisée. L'objectif est de satisfaire la demande de chaque intervalle en gardant la plus grande réserve minimale possible.

Les capacités des sept unités totalisent 150 MW, ce qui confirme la capacité totale utilisée. Les données définissent les demandes et les configurations de maintenance; aucune autre contrainte de calendrier entre unités n'est ajoutée. Le programme suit les paramètres demandés et pénalise les solutions infaisables selon leurs déficits de réserve.

## Données

| Unité | Capacité (MW) | Configurations de maintenance autorisées |
|---|---:|---|
| 1 | 20 | 1100, 0110, 0011 |
| 2 | 15 | 1100, 0110, 0011 |
| 3 | 35 | 1000, 0100, 0010, 0001 |
| 4 | 40 | 1000, 0100, 0010, 0001 |
| 5 | 15 | 1000, 0100, 0010, 0001 |
| 6 | 15 | 1000, 0100, 0010, 0001 |
| 7 | 10 | 1000, 0100, 0010, 0001 |

La demande des quatre intervalles est [80, 90, 65, 70] MW. La capacité totale est de 150 MW, égale à la somme des capacités des unités.

Dans un motif, 1 signifie que l'unité est en maintenance et 0 qu'elle est disponible. Par exemple, 0100 signifie une maintenance au deuxième intervalle.

## Représentation des chromosomes

Un chromosome est une liste de sept gènes, dans l'ordre des unités 1 à 7. Chaque gène est une chaîne de quatre bits décrivant le calendrier d'une unité. Un chromosome est valide si chacun de ses gènes appartient à la liste autorisée pour cette unité.

La génération de la population choisit uniquement des motifs autorisés. Le croisement et la mutation vérifient et préservent cette propriété.

## Formulation mathématique

On note :

- P_i la capacité de l'unité i;
- d_t la demande à l'intervalle t;
- x_it = 1 si l'unité i est en maintenance à l'intervalle t, et 0 sinon;
- M_t la puissance indisponible à l'intervalle t;
- R_t la réserve à l'intervalle t.

La puissance indisponible et la réserve sont calculées par :

    M_t = somme(i=1..7) P_i x_it
    R_t = 150 - M_t - d_t

La décision doit respecter les configurations de maintenance autorisées et la contrainte de faisabilité :

    R_t >= 0, pour t = 1, 2, 3, 4

L'objectif est de maximiser la plus petite réserve :

    Z = min(R_1, R_2, R_3, R_4)

Une formulation équivalente introduit une variable z et maximise z sous z <= R_t pour chaque intervalle, avec z >= 0 et R_t >= 0.

## Algorithme génétique

### Fitness et pénalisation

La valeur de l'objectif est la réserve minimale. Pour sélectionner les parents par roulette, le programme transforme cette valeur en un poids positif :

- une solution faisable reçoit 1 + Z; le classement des solutions faisables suit donc bien l'objectif;
- une solution infaisable reçoit 1 / (1 + V), où V est la somme des déficits de réserve; ce poids reste inférieur à celui d'une solution faisable et décroît lorsque les déficits augmentent;
- un chromosome qui ne respecte pas les configurations reçoit un poids nul.

Ainsi, les contraintes de réserve sont prises en compte sans confondre une solution infaisable avec une solution faisable de faible réserve.

### Sélection par roulette

Pour chaque chromosome j, la probabilité de sélection est proportionnelle à son poids :

    p_j = fitness_j / somme(fitness)

Un tirage uniforme sur la somme cumulée choisit le parent. Si la somme des poids est nulle, le programme choisit uniformément un individu afin que l'algorithme puisse continuer.

### Croisement en un point

Un point de coupure est choisi entre deux unités. L'enfant reçoit le préfixe d'un parent et le suffixe de l'autre. Chaque position conserve le domaine de configurations de l'unité correspondante; les enfants restent donc valides.

### Mutation par inversion

La mutation inverse un segment contigu de gènes à l'intérieur d'un groupe ayant les mêmes configurations autorisées : unités 1–2 ou unités 3–7. Cela conserve la validité. Si les motifs du groupe sont identiques et qu'une inversion ne changerait pas le chromosome, le programme inverse le calendrier d'une unité dans le temps. Les motifs fournis restent autorisés après cette inversion.

### Élitisme

Le meilleur individu connu est copié dans la génération suivante. Cela garantit que le meilleur résultat conservé ne se dégrade pas au fil des générations.

## Paramètres

| Paramètre | Valeur |
|---|---:|
| Taille de la population | 50 |
| Nombre de générations | 100 |
| Probabilité de croisement | 0,8 |
| Probabilité de mutation | 0,3 |
| Élitisme | 1 individu |
| Graine aléatoire | 42 |

## Exécution

Depuis le dossier TD_ALGO, exécuter :

    python cedule/cedule.py

Le programme n'utilise que la bibliothèque standard de Python.

## Exemple de résultat obtenu

Avec les paramètres ci-dessus et la graine 42, l'algorithme génétique a produit :

    Unité 1 : 0110
    Unité 2 : 1100
    Unité 3 : 0010
    Unité 4 : 0001
    Unité 5 : 1000
    Unité 6 : 1000
    Unité 7 : 0001
    Réserves (MW) : 25, 25, 30, 30
    Réserve minimale : 25 MW
    Faisable : oui

Une énumération exhaustive des 3² × 4⁵ = 9 216 chromosomes autorisés donne également une meilleure réserve minimale de 25 MW. L'algorithme génétique atteint donc la meilleure valeur vérifiée pour les données et contraintes de ce modèle.
