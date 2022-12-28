+++
title = "Ingénierie des performances avec Python 3.12"
date = "2022-12-26T22:54:29Z"
author = "Peter McConnell"
authorTwitter = "PeteMcConnell_" #do not include @
cover = ""
tags = ["python", "linux", "perf"]
keywords = ["python", "linux", "cpython", "perf", "performance", "flamegraph"]
description = ""
showFullContent = false
readingTime = true
hideComments = false
color = "" #color from the theme settings
Toc = true
+++

3.12 apporte le profilage des performances ! Prenez une seconde pour aller consulter https://docs.python.org/3.12/howto/perf_profiling.html et en effet le changelog à https://www.python.org/downloads/release/python-3120a3/

La partie importante (pour ce post) des liens ci-dessus est :

"""
Le profileur de performances Linux est un outil très puissant qui vous permet de profiler et d'obtenir des informations sur les performances de votre application. perf dispose également d'un écosystème d'outils très dynamique qui facilite l'analyse des données qu'il produit.

Le principal problème avec l'utilisation du profileur perf avec les applications Python est que perf ne permet d'obtenir des informations que sur les symboles natifs, c'est-à-dire les noms des fonctions et des procédures écrites en C. Cela signifie que les noms et les noms de fichiers des fonctions Python dans votre code n'apparaîtra pas dans la sortie de la perf.

Depuis Python 3.12, l'interpréteur peut s'exécuter dans un mode spécial qui permet aux fonctions Python d'apparaître dans la sortie du profileur de performances. Lorsque ce mode est activé, l'interpréteur interposera un petit morceau de code compilé à la volée avant l'exécution de chaque fonction Python et il apprendra à perf la relation entre ce morceau de code et la fonction Python associée à l'aide de fichiers de mappage de perf.
"""

écrire un "mauvais" programme
-----------------------------

J'ai hâte d'essayer ça, alors allons-y. Tout d'abord, créons un script python à profiler. Je le fais avant d'installer Python 3.12 car je veux créer un FlameGraph de l'apparence de ce processus dans 3.10 vers 3.12. Ici, nous avons un script qui tente d'effectuer des recherches sur une grande liste :

```python
import time


def run_dummy(numbers):
    for findme in range(100000):
        if findme in numbers:
            print("trouvé", trouvemoi)
        else:
            print("manqué", me trouver)


if __name__ == "__main__":
    # create a large sized input to show off inefficiency
    numbers = [i for i in range(20000000)]

    start_time = time.time()  # get the current time [start]
    run_dummy(numbers)  # run our inefficient method
    end_time = time.time()  # get the current time [end]

    duration = end_time - start_time  # calculate the duration
    print(f"Durée: {duration} secondes")  # print the duration
```

En exécutant ceci, j'obtiens le résultat suivant:

```sh
python3.10 assets/dummy/perf_py_proj/before.py
...
trouvé 99992
trouvé 99993
trouvé 99994
trouvé 99995
trouvé 99996
trouvé 99997
trouvé 99998
trouvé 99999
Durée : 36.06884431838989 secondes
```

36 secondes suffisent pour que nous prélevions un nombre raisonnable d'échantillons.

des flamegraphes !
------------

Nous pouvons maintenant créer notre [FlameGraph](https://github.com/brendangregg/FlameGraph) :

```sh
# enregistrer le profil dans le fichier "perf.data" (sortie par défaut)
perf record -F 99 -g -- python3.10 assets/dummy/perf_py_proj/before.py
# lire perf.data (créé ci-dessus) et afficher la sortie de trace
perf script > out.perf
# plier les échantillons de pile en une seule ligne
# ici, je fais référence à ~/FlameGraph/ - vous pouvez l'obtenir à partir de https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# générer un flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.10.svg
```

Cela nous donne un joli SVG qui visualise les traces :

![python 3.10 perf flamegraph](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.10.svg "python 3.10 perf flamegraph")

Ce n'est pas utile ... Je peux voir que la plupart du temps a été passé dans "new_keys_object.lto_priv.0" mais cela n'a aucun sens dans le contexte du code.

C'est l'heure de Python 3.12...
------------------------

Je dois d'abord l'installer - les étapes pour cela varient selon le système d'exploitation - suivez les instructions de construction ici pour votre environnement : https://github.com/python/cpython/tree/v3.12.0a3#build-instructions


```sh
# pour moi sur ubuntu:22.04
# assurez-vous que python3-dbg est installé
sudo apt-get install python3-dbg

# construire python
export CFLAGS="-fno-omit-frame-pointer -mno-omit-leaf-frame-pointer"
./configure --enable-optimizations
make
make test
sudo make install
unset CFLAGS

# après cela, j'ai réinitialisé le lien symbolique de mon système python3 à 3.10 car 3.12 n'est pas encore stable
# pour tester python3.12, j'appellerai "python3.12" au lieu de "python3"
ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3
```

Avec cela installé, je dois d'abord activer le support des performances. Ceci est détaillé dans https://docs.python.org/3.12/howto/perf_profiling.html et il y a trois options : 1) une variable d'environnement, 2) une option -X ou 3) dynamiquement en utilisant `sys`. J'opterai pour l'approche des variables d'environnement car cela ne me dérange pas que _tout_ soit profilé pour un petit script :

```sh
export PYTHONPERFSUPPORT=1
```

Maintenant, nous répétons simplement le processus ci-dessus en utilisant à la place le binaire `python3.12` :

```sh
# enregistrer le profil dans le fichier "perf.data" (sortie par défaut)
perf record -F 99 -g -- python3.12 assets/dummy/perf_py_proj/before.py
# lire perf.data (créé ci-dessus) et afficher la sortie de trace
perf script > out.perf
# plier les échantillons de pile en une seule ligne
# ici, je fais référence à ~/FlameGraph/ - vous pouvez l'obtenir à partir de https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# générer un flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.12.before.svg
```

Nous allons d'abord jeter un coup d'œil au rapport avec `perf report -g -i perf.data`

![sortie du rapport de performance python 3.12](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_report.png "rapport de performance python 3.12")

Impressionnant! Nous pouvons voir nos noms de fonctions Python et nos noms de scripts !

Nous pouvons maintenant jeter un œil au SVG mis à jour qui visualise les traces avec Python 3.12 :

![python 3.12 perf flamegraph](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.12.before.svg "python 3.12 perf flamegraph")

Cela semble déjà beaucoup plus utile. Nous voyons que la majorité du temps est consacrée à faire des comparaisons et dans la méthode list_contains. Nous pouvons également voir le fichier spécifique `before.py` et la méthode `run_dummy` qui l'appelle.

Temps d'enquête / le correctif
-------------------------------------

Maintenant que nous savons où se trouve le problème dans notre code, nous pouvons jeter un œil au code source dans CPython pour voir pourquoi la méthode `list_contains` serait si lente : https://github.com/python/cpython/blob/ 199507b81a302ea19f93593965b1e5088195a6c5/Objects/listobject.c#L440

_note : vous n'aurez peut-être pas toujours accès au code source - dans de telles circonstances, vous pouvez voir le désassemblage directement dans le rapport de performance pour avoir une idée de ce qui se passe. Je vais ajouter une section rapide à la fin montrant à quoi cela ressemble_

```c
// J'ai trouvé ceci en allant sur https://github.com/python/cpython/ et en recherchant "list_contains"

static int
list_contains(PyListObject *a, PyObject *el)
{
    PyObject *item;
    Py_ssize_t i;
    int cmp;

    for (i = 0, cmp = 0 ; cmp == 0 && i < Py_SIZE(a); ++i) {
        item = PyList_GET_ITEM(a, i);
        Py_INCREF(item);
        cmp = PyObject_RichCompareBool(item, el, Py_EQ);
        Py_DECREF(item);
    }
    return cmp;
}
```

Nasty ... en regardant ce code, je peux voir que chaque fois qu'il est invoqué, il parcourt le tableau et effectue une comparaison avec chaque élément. C'est loin d'être idéal pour notre cas d'utilisation, alors revenons au code Python que nous avons écrit. Notre Flamegraph nous montre que le problème est dans notre méthode `run_dummy` :

```python
def run_dummy(nombres):
    for findme in range(100000):
        if findme in numbers: # <- c'est ce qui déclenche list_contains
            print("trouvé", trouvemoi)
        autre:
            print("manqué", me trouver)
```

Nous ne pouvons pas vraiment changer cette ligne car elle fait ce que nous voulons qu'elle fasse - identifier si un entier est dans `numbers`. Peut-être pouvons-nous changer le type de données "numbers" pour un type mieux adapté aux recherches. Dans notre code existant, nous avons :

```python
    numbers = [i for i in range(20000000)]

    start_time = time.time()  # get the current time [start]
    run_dummy(numbers)  # run our inefficient method
```

Ici, nous avons utilisé un type de données LIST pour nos "nombres", qui sous le capot (dans CPython) est implémenté sous forme de tableaux de taille dynamique et, en tant que tel, est loin d'être aussi efficace (O (N)) que les goûts d'un Hashtable pour regarder un élément (qui est O (1)). Un SET d'autre part (un autre type de données Python) est implémenté en tant que table de hachage et nous donnerait la recherche rapide que nous recherchons. Modifions le type de données dans notre code Python et voyons quel en est l'impact :

```python
     # nous allons juste changer cette ligne, en jetant des nombres dans un ensemble avant d'exécuter run_dummy
     run_dummy(set(numbers)) # passage d'un set() pour des recherches rapides
```

Nous pouvons maintenant répéter les étapes ci-dessus pour générer notre nouveau flamegraph :

```sh
# enregistrer le profil dans le fichier "perf.data" (sortie par défaut)
enregistrement de performances -F 99 -g -- python3.12 assets/dummy/perf_py_proj/after.py
...
trouvé 99998
trouvé 99999
Durée : 0.8350753784179688 secondes
[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 0.039 MB perf.data (134 samples) ]
```

Nous pouvons déjà voir que les choses se sont massivement améliorées. Là où auparavant cela prenait 36 secondes pour s'exécuter, cela prend maintenant 0,8 seconde ! Continuons à créer notre flamegraph pour le nouveau code amélioré :

```sh
# lire perf.data (créé ci-dessus) et afficher la sortie de trace
perf script > out.perf
# plier les échantillons de pile en une seule ligne
# ici, je fais référence à ~/FlameGraph/ - vous pouvez l'obtenir à partir de https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# générer un flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.12.after.svg
```

![python 3.12 parf flamegraph amélioré] (https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.12.after.svg "python 3.12 perf flamegraph amélioré")

Il s'agit d'un Flamegraph beaucoup plus sain et notre application est maintenant beaucoup plus rapide en conséquence. La prise en charge du profilage des performances dans Python 3.12 apporte un outil extrêmement utile aux ingénieurs logiciels qui souhaitent fournir des programmes rapides et je suis ravi de voir l'impact que cela aura sur le langage.

bonus round : que faire quand on ne peut pas accéder au code source ?
-------------------------------------------------- ------------

Parfois, vous n'avez pas accès au code sous-jacent, ce qui peut rendre la compréhension de ce qui se passe beaucoup plus difficile. Heureusement, `perf report` nous permet de visualiser le code désassemblé, ce qui peut aider à brosser un tableau de ce que fait réellement la machine. C'est un premier endroit raisonnable à regarder - j'ai tendance à préférer le code source si je peux m'en procurer car cela me permet de "blâmer" / de voir les commits et PR associés. Pour l'afficher, vous pouvez procéder comme suit :

Ouvrez le rapport de perf et sélectionnez la ligne qui nous intéresse :

```sh
# cela suppose que nous avons déjà exécuté 'perf record' pour générer perf.data ...
perf report -g -i perf.data
```

![perf report dissassembly](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_report_dis.1.png "perf report dissassembly")

Appuyez sur Entrée et choisissez l'option d'annotation :

![Désassemblage du rapport de performances](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_report_dis.2.png "Désassemblage du rapport de performances")

Voir! Ici, nous pouvons voir à la fois le code C et les instructions de la machine. Super utile ! Vous pouvez comparer la capture d'écran ci-dessous avec l'extrait de code qui nous intéresse : https://github.com/python/cpython/blob/199507b81a302ea19f93593965b1e5088195a6c5/Objects/listobject.c#L440

![perf report dissassembly](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_report_dis.3.png "perf report dissassembly")
