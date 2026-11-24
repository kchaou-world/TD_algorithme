# TD4 - Heuristiques et métaheuristiques

**Étudiant : Kchaou Mohamed**

## Organisation du rendu

La demande de rendu est un dossier contenant ce `README.md`, avec le travail des quatre exercices, et un programme Python pour l'exercice 4. Les questions et les données numériques ci-dessous proviennent de l'énoncé du TD4. Les choix de modélisation ajoutés pour rendre certains calculs déterminés sont signalés explicitement.

Le programme de l'exercice 4 se trouve dans [`exercice4_aco_knapsack.py`](exercice4_aco_knapsack.py).

## Exercice 1 - Théorème des schémas

On utilise l'estimation classique du théorème des schémas, avec sélection proportionnelle à l'adaptation :

`m(H,t+1) >= m(H,t) * f(H)/f_moy * (1 - pc * delta(H)/(L-1)) * (1-pm)^o(H)`

où `m(H,t)` est le nombre de chaînes correspondant au schéma, `f(H)` leur adaptation moyenne, `f_moy` l'adaptation moyenne de la population, `delta(H)` la longueur définissante, `o(H)` le nombre de positions fixées et `L` la longueur des chaînes. Cette formule donne une borne inférieure, car elle comptabilise la survie des instances présentes et ne compte pas les schémas qui pourraient être créés par hasard.

Données : `L=5`, `f_moy=(20+10+5+15)/4=12,5`, `pc=0,1`, `pm=0,01`.

### a) Schéma `H1 = 1****`

Les instances à la génération 0 sont `10001` (adaptation 20) et `11100` (adaptation 10). Ainsi `m(H1,0)=2`, `f(H1)=15`, `o(H1)=1` et `delta(H1)=0`.

`m(H1,1) >= 2 * (15/12,5) * (1 - 0,1*0/4) * (0,99)^1 = 2,376`.

On attend donc **au moins environ 2,376 instances** selon cette estimation (la valeur est une espérance, elle n'a pas besoin d'être entière).

### b) Schéma `H2 = 0**10`

L'unique instance est `01110`, d'adaptation 15. Donc `m(H2,0)=1`, `f(H2)=15`, `o(H2)=3` et `delta(H2)=4`.

`m(H2,1) >= 1 * (15/12,5) * (1 - 0,1*4/4) * (0,99)^3 = 1,04792292`.

Le nombre attendu estimé est donc **environ 1,048 instance ou davantage** selon la borne du théorème.

## Exercice 2 - Instances et évolution de schémas

La population contient quatre chaînes de longueur `L=6`, d'adaptation moyenne `f_moy=(20+30+16+14)/4=20`. Les schémas sont `H1=1*0**1` et `H2=0**0**`.

### 1) Chaînes instances

- `H1=1*0**1` : `110001` et `110111` (les positions 1, 3 et 6 valent respectivement 1, 0 et 1).
- `H2=0**0**` : `011001` et `000010` (les positions 1 et 4 valent 0).

### 2) Longueur utile

La longueur utile, ou ordre, est le nombre de positions fixées : `o(H1)=3` et `o(H2)=2`.

Pour le calcul de la disruption par croisement, on a aussi besoin de la longueur définissante : `delta(H1)=6-1=5` (positions fixées extrêmes 1 et 6) et `delta(H2)=4-1=3` (positions extrêmes 1 et 4).

### 3) Bornes du nombre d'instances

Dans l'espace de toutes les chaînes binaires de longueur 6, un joker peut prendre 0 ou 1 :

- `H1` a trois jokers, donc **8 chaînes distinctes** peuvent l'instancier (`2^3`).
- `H2` a quatre jokers, donc **16 chaînes distinctes** peuvent l'instancier (`2^4`).

Dans une population de taille 4, le nombre de copies de chaque schéma est nécessairement entre **0 et 4**. Dans la population donnée à la génération 0, le nombre observé est exactement **2 pour `H1` et 2 pour `H2`**.

### 4) Nombre attendu d'instances de `H1` à la génération 1

Les deux instances ont une adaptation moyenne `f(H1)=(20+30)/2=25`. Avec `pc=0,6` et `pm=0,01` :

`m(H1,1) >= 2 * (25/20) * (1 - 0,6*5/5) * (0,99)^3 = 0,970299`.

La borne estimée est **environ 0,970 instance ou davantage**.

### 5) Nombre attendu d'instances de `H2` à la génération 1

Les deux instances ont une adaptation moyenne `f(H2)=(16+14)/2=15` :

`m(H2,1) >= 2 * (15/20) * (1 - 0,6*3/5) * (0,99)^2 = 0,940896`.

La borne estimée est **environ 0,941 instance ou davantage**.

Ces deux résultats sont les bornes de survie du théorème des schémas, pas des prédictions exactes du contenu de la prochaine population.

### 6) Disparition de `H2` si croisement et mutation sont négligeables

On suppose une sélection proportionnelle à l'adaptation. Les instances de `H2` ont une adaptation moyenne 15, contre 25 pour les deux chaînes qui ne l'instancient pas. Si `p_t` est la proportion de `H2`, alors :

`p_(t+1) = 15*p_t / (15*p_t + 25*(1-p_t))`.

Avec `p_0=1/2`, on obtient `p_t=0,6^t/(1+0,6^t)` et un nombre moyen de copies `4*p_t` : 2 à `t=0`, 1,5 à `t=1`, 1,059 à `t=2`, puis 0,711 à `t=3`.

Dans ce modèle, l'espérance passe sous une copie à la **3e génération** : c'est un seuil pratique d'extinction. Mathématiquement, la proportion déterministe tend vers zéro sans l'atteindre en un nombre fini de générations. Dans une population réelle de quatre individus, l'extinction dépend du tirage de sélection et peut survenir plus tôt ou plus tard.

## Exercice 3 - Optimisation par essaim de particules (PSO)

On maximise `f(x)=-x^2+4x` sur `[-5,5]`. La mise à jour est :

`v_i(t+1) = omega*v_i(t) + c_cog*r1*(pbest_i-x_i) + c_soc*r2*(gbest-x_i)`

`x_i(t+1) = x_i(t) + v_i(t+1)`.

Dans les données du TD, l'inertie vaut `omega=0,8` et les deux accélérations valent 2. Le TD ne précise pas les valeurs des tirages `r1` et `r2` pour la première itération. Pour rendre le calcul à la main reproductible, on prend **`r1=r2=0,5` pour chaque particule**. Le code général tire ces coefficients dans `[0,1]`.

### 1) Première itération à partir des trois particules fournies

À l'initialisation, `pbest_i=x_i`. Les évaluations sont `f(2)=4`, `f(4)=0` et `f(-1)=-5`. Ainsi `pbest=(2,4,-1)` et `gbest=2`.

| Particule | `x_i^0` | `v_i^0` | `v_i^1` | `x_i^1` | `f(x_i^1)` | `pbest_i^1` |
| --------- | ------: | ------: | ------: | ------: | ---------: | ----------: |
| 1         |       2 |       0 |       0 |       2 |          4 |           2 |
| 2         |       4 |       0 |      -2 |       2 |          4 |           2 |
| 3         |      -1 |       0 |       3 |       2 |          4 |           2 |

La meilleure position globale après cette itération est donc **`gbest^1=2`**, d'adaptation 4.

### 2a) Initialisation de `n` particules

Pour chaque particule `i`, tirer `x_i` dans `[-5,5]` et une vitesse initiale `v_i`. Le TD ne donne pas l'intervalle des vitesses ; on peut, par exemple, tirer `v_i` dans `[-5,5]` (ce choix est configurable). Poser ensuite `pbest_i=x_i`, calculer `f(x_i)`, et retenir la position ayant la meilleure valeur comme `gbest`.

### 2b) Complexité de l'initialisation

Chaque particule est traitée une fois : temps **`O(n)`** et mémoire **`O(n)`** pour stocker positions, vitesses et meilleures positions.

### 2c) Algorithme PSO complet

1. Initialiser `x_i`, `v_i`, `pbest_i` et `gbest`.
2. Répéter jusqu'au nombre maximal d'itérations :
   - tirer indépendamment `r1,r2` dans `[0,1]` pour chaque particule ;
   - calculer sa nouvelle vitesse puis sa position ;
   - borner la position à `[-5,5]` ;
   - mettre à jour `pbest_i` si la nouvelle adaptation est meilleure ;
   - mettre à jour `gbest` depuis les `pbest_i`.
3. Renvoyer `gbest` et `f(gbest)`.

Pour `T` itérations, le temps est **`O(Tn)`** et la mémoire reste **`O(n)`**. Le maximum analytique de la fonction est `f(2)=4`, ce qui permet de contrôler le résultat recherché.

## Exercice 4 - Sac à dos par colonie de fourmis

### 1) Représentation et nombre de solutions

Une solution est un vecteur binaire `x=(x_1,...,x_n)`, avec `x_i=1` si l'objet `i` est pris et `x_i=0` sinon. L'espace contient **`2^n` sous-ensembles candidats**. Le nombre de solutions réalisables dépend des poids et de la capacité ; il est au plus `2^n`.

### 2) Formulation mathématique

`maximiser somme(i=1..n) V_i*x_i`

sous les contraintes `somme(i=1..n) p_i*x_i <= C` et `x_i ∈ {0,1}` pour tout `i`.

### 3) Nombre et rôle des fourmis

Il n'existe pas de nombre universel imposé. On utilise souvent un nombre de fourmis de l'ordre du nombre d'objets ; le programme choisit par défaut `max(10,n)`, valeur que l'on peut régler. À chaque itération, chaque fourmi construit une sélection réalisable, en choisissant parmi les objets non encore pris qui tiennent encore dans le sac. La probabilité de choisir un objet dépend de la phéromone du déplacement précédent et d'une heuristique de qualité. Après construction, les bonnes solutions renforcent les traces correspondantes et les autres traces s'évaporent.

### 4) Distance entre objets

On représente chaque objet par ses attributs normalisés (poids, valeur) et on prend la distance euclidienne :

`d(i,j) = sqrt(((p_i-p_j)/p_max)^2 + ((V_i-V_j)/V_max)^2)`.

Cette distance est une proposition de modélisation, car l'énoncé ne fournit pas de coordonnées géographiques. L'heuristique utilisée dans le programme combine la proximité au dernier objet et le rendement `V_j/p_j` : `eta(i,j)=(V_j/p_j)/(1+d(i,j))`. Depuis le départ, la distance est fixée à zéro.

### 5) Algorithme et fichier Python

Pour chaque itération, les fourmis construisent une solution sans dépasser la capacité. Pour choisir le prochain objet `j` à partir de `i`, le programme utilise :

`P(i,j) = tau(i,j)^alpha * eta(i,j)^beta / somme(k admissible) tau(i,k)^alpha * eta(i,k)^beta`.

Après l'évaluation des solutions, les phéromones s'évaporent au taux `rho`, puis les fourmis déposent une quantité proportionnelle à la valeur de leur sac sur chaque transition empruntée. Le programme standard-library Python, avec paramètres modifiables et un exemple d'exécution, est dans [`exercice4_aco_knapsack.py`](exercice4_aco_knapsack.py).
