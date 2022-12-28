+++
title = "chatGPT - création d'un outil de test de base de données automatisé"
date = "2022-12-08T11:41:50Z"
author = ""
authorTwitter = "PeteMcConnell_" #do not include @
cover = ""
tags = ["chatGPT", "SQL", "Python"]
keywords = ["chatGPT", "sql"]
description = ""
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

Création d'un outil de test de base de données automatisé avec ChatGPT
-------------------------------------------------- ------

Hier soir, j'ai pensé essayer de faire en sorte que ChatGPT crée une base de données automatisée
outil de test et les résultats étaient assez prometteurs.

En conclusion, avec des conseils, il a pu construire un projet à partir de zéro
qui a exécuté un script python et une base de données postgres. Il a généré un
schéma aléatoire et valeurs pour les tables générées aléatoirement. Il a fourni
un script Python qui inspecterait la base de données et exécuterait des requêtes
sur celle-ci.

Est-ce que tout a fonctionné hors de la boîte? Non. Il y a quelques bogues à
corriger dans le python script qu'il a généré. Cependant, l'effort pour y
remédier n'est pas élevé et certainement l'ensemble du processus de bout en
bout est moins cher, en termes de temps, par rapport à partir de zéro.

J'ai trouvé que les bogues rencontrés étaient en grande partie dus à mon manque
de clarté ou ordre des questions qui lui sont posées. Il était tout à fait
capable de réparer lui-même erreurs / mise à jour du code existant pour
correspondre aux nouvelles exigences lorsque demandé de le faire.

Le seul problème _réel_ que j'ai rencontré était des erreurs d'API générales
que l'on pourrait attendez-vous à quelque chose d'aussi populaire dans un état
de prévisualisation précoce.

Je suis sorti de cette expérience en voyant ChatGPT et tout ce qui suit comme
un aide au développement vraiment utile pour ceux qui savent déjà programmer.
Il m'a aidé à construire un outil plus rapidement que je n'aurais pu si je me
suis assis pour le faire à partir de gratter. Je ne le considère pas encore
comme un remplacement pour les ingénieurs en logiciel pour deux raisons
principales - premièrement : pour les applications non triviales, je soupçonne
la personne l'alimentation des exigences dans le système (ou "ingénieur
rapide") doit avoir un idée raisonnable de la façon de construire un logiciel
en premier lieu, afin de savoir comment pour formuler des demandes et corriger
les erreurs / combler les lacunes. deuxièmement : le code étant généré n'est
pas toujours solide - sans qu'un ingénieur expérimenté examine et prendre
possession de tout code produit (la propriété étant importante pour raisons de
maintenance) alors il y a peu de garantie que vous obtiendrez ce que vous
espèrent.

Cependant; c'est encore très tôt. Les problèmes décrits peuvent-ils être
résolus plus loin? Absolument. Ce type d'outillage sera-t-il "mauvais" pour les
logiciels l'ingénierie dans son ensemble, à long terme ? Peut-être.
Personnellement, je suis très heureux d'avoir cet outil dans mon arsenal - il
m'a déjà permis d'échafauder un prototype candidatures rapidement. Est-ce que
je l'utiliserais pour du code de production sur un lieu de travail ? Non plus
ou moins que je ne le ferais avec des extraits de stackoverflow ou de son
acabit. Pour le moment

Github repository: https://github.com/peter-mcconnell/gpt_sql_test_generator

Screenshots:

![step 2](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/2.png "step 2")
![step 3](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/3.png "step 3")
![step 4](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/4.png "step 4")
![step 5](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/5.png "step 5")
![step 6](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/6.png "step 6")
![step 7](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/7.png "step 7")
![step 8](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/8.png "step 8")
![step 9](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/9.png "step 9")
![step 10](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/10.png "step 10")
![step 11](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/11.png "step 11")
![step 12](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/12.png "step 12")
![step 13](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/13.png "step 13")
![step 14](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/14.png "step 14")
![step 15](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/15.png "step 15")
![step 16](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/16.png "step 16")
