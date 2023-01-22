'''''''''''''''''''''''''''''''''''''''''''''''''
DESCRIPTION TECHNIQUE DE PYCORETEXT
'''''''''''''''''''''''''''''''''''''''''''''''''
......................................
Cahier des charges au début de projet
......................................

Exigences fonctionnelles :

  * Formulaire offrant la gamme complète des champs proposés par l'API
    Judilibre (cf. *Tableau des champs API*). Aussi utilisation des
    commandes proposées par l'API (cf. *liste des commandes API*):
  
  * Les champs du formulaires devront être sécurisés et formatés en fonction
    du Type de données attendu (cf. *Tableau des champs API*). Les critères
    limités et définis par l'API devront être mis à jour à chaque ouverture
    de l'appli.
  
  * A partir du formulaire, générer une liste de résultat dans un onglet à part.
    Cette liste sera triée par défaut date de décision (ordre antéchronologique)
  
  * Proposer un aperçu des métadonnées lorsque une décision est sélectionnée
    dans la liste de résultat.
  
  * Possibilité d'afficher le text de la décision sélectionnée
  
Exigences non-fonctionnelles :
  * Rendre accessible l'API à des personnes non coutumières des API REST.
  * Connexion à l'environnement Sandbox comme production
  * Grouper et rationaliser les champs de recherche => simplifier l'API
  * Créer un outil du quotidien simple et efficace

Limites à prendre en compte
  * Les requêtes Judilibre (sandbox) sont restreintes :

+----------+--------------------+-------------------+
| Throttle | 1000000 message(s) | every 1 day(s)    |
+----------+--------------------+-------------------+
| Throttle | 20 message(s)      | every 1 second(s) |
+----------+--------------------+-------------------+

    10 000 résultats maximum en Sandbox
  
  * Obtenir un grand nombre de résulat requiert plusieurs secondes (utilisation
    du multi-threading)

  * Les commandes disponibles ne sont pas toujours pertinentes (Search et 
    Export)

  * Application multiplateforme (dans un premier temps la cible est Windows)

  * L'application évoluera et doit donc être modulable. 

........................
 Documentation API
........................

=========================================================
Liste des méthodes proposées par la méthode GET de l'API
=========================================================

+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| COMMANDE     | DESCRIPTION                                                                                                                               |
+==============+===========================================================================================================================================+
| EXPORT       | Export de décisions complètes par lot (batch).                                                                                            |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| SEARCH       | Recherche par mots clés et obtention d'un résumé des décisions correspondantes                                                            |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| DECISION     | Recherche grâce à l'identifiant Judilibre et obtention d'une décision complète                                                            |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| TAXONOMY     | Permet de récupérer la liste des termes constituants les différents critères et filtres                                                   |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| HEALTHCHECK  | Ce point d'entrée permet de connaître l'état de disponibilité du service (disponible ou indisponible).                                    |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| STATS        | Récupération de statistiques (nb de décisions indexées, nb de requêtes effectuées, date de décision la plus ancienne et la plus récente)  |
+--------------+-------------------------------------------------------------------------------------------------------------------------------------------+

=========================================================
Liste des résultats obtenus
=========================================================

**IMPORTANT**

Dans les tableaux ci-dessous, si "*" est accolé à la méta alors cela signifie qu'elle ne sera pas récupérée
par l'application.

##################################
Search : métadonnées essentielles
##################################

+---------------+----------------+----------+------------------------+-----------------------------+
| chamber       | decision_date  | ecli     | files                  | id                          |
+---------------+----------------+----------+------------------------+-----------------------------+
| jurisdiction  | number         | numbers  | publication            | solution                    |
+---------------+----------------+----------+------------------------+-----------------------------+
| summary       | themes         | type     | score (exclu search)*  | highlights (exclu search)*  |
+---------------+----------------+----------+------------------------+-----------------------------+
| location      | text*          |          |                        |                             |
+---------------+----------------+----------+------------------------+-----------------------------+

!! Attention, la méta "text" dans Search correspond aux textes qui contiennent seulement
le(s) mot(s) recherchés (query) tandis que "text". Cette information n'est pas utilisée
dans PYCORETEXT.

Au contraire, dans Export ou Decision, la métadonnée "text" correpond bien
au texte de la décicion

######################################################
Export et Decision : des informations supplémentaires
######################################################

+---------------+------------+------------+-----------------+----------------+
| bulletin      | contested  | formation  | forward         | legacy         |
+---------------+------------+------------+-----------------+----------------+
| nac           | partial    | portalis   | rapprochements  | to_be_deleted  |
+---------------+------------+------------+-----------------+----------------+
| solution_alt  | source     | text       | timeline        | update_date    |
+---------------+------------+------------+-----------------+----------------+
| visa          | zones*     |            |                 |                | 
+---------------+------------+------------+-----------------+----------------+

"zone" permet de structurer le texte de la décision.
Ce n'est pas le but de PYCORETEXT, c'est pourquoi cette information est ignorée.

###################
Résultats Taxonomy
###################

+----+---------------+--------+
| id | context_value |  result|
+----+---------------+--------+

cf. fichier "diff_taxo_ca_cc.docx"
=> on remarque que les critères donnés par Taxonomy peuvent variés selon
le contexte. Mais au 07/10/2022, seuls deux diffèrent vraiment :

* location
* theme

"type" varie aussi mais "cc" contient les types de "ca" qui sont moins nombreux.


######################
Résultats Healthcheck
######################

+--------+
| status |
+--------+

######################
Résultats Stats
######################

+----------------+-----------------+-----------------+---------------+------------------------+
| requestPerDay  | oldestDecision  | newestDecision  | indexedTotal  | indexedByjurisdiction  |
+----------------+-----------------+-----------------+---------------+------------------------+
| indexedByYear  | requestPerWeek  | requestPerMonth |               |                        |
+----------------+-----------------+-----------------+---------------+------------------------+

................................
 Mise en place de l'application
................................

==================================
Architecture du projet PYCORETEXT
==================================

#######
Schéma
#######

.. image:: .\\schema_pycoretext.jpg

##################################
Description des différents modules
##################################

L'application est exécutée grâce au fichier source **pycoretexte.py**

* **application.py**
    -> Module contenant la classe principale de l'application, l'objet Tk

* **exceptions.py**
    -> Module qui rassemble les exceptions gérées dans le projet pycoretext

* **widgets.py**
    -> Ce module contient les créations de classes de widgets pour pycoretext

* **api_controler**
    - *api_url.py*
        >  Module définissant les classes de construction de l'Url de recherche Judilibre
              Le but est d'obtenir la partie variable de l'Url pour composer la requête.
              La base de l'Url (endpoint) proviendra du module judilibre_connexion
    - *api_connexion.py*
        >  Module contenant les outils nécessaires à la mise en place d'une connexion
              entre un utilisateur et l'API Judilibre:
              Authentification (API key), vérification du service, vérification d'une URL
              créée grâce aux classes du module api_url, requête grâce au module
              request et génération de l'objet Answer approprié.
    - *api_answers.py*
        > Les classes de ce modules permettent de stocker et structurer les réponses
            obtenues par une requête dans l'API
* **views**
    - *login_page.py*
        > Module contenant la classe dédiée à la page de login.
    - *homepage.py*
        > Module qui contient les classes de construction pour la homepage.
            Une classe générale accompagnée de 3 sous-classes :
            3 Frames = "Informations de connexion", "Statistiques Judilibre", "Recherche"
    - *form.py*
        > Module contenant la classe pour construire le bloc de la homepage qui
            permettra de faire sélectionner des critères et de lancer des recherches
    - *result_page.py*
        > Classes pour instanciation d'une page de résultat


=====================================================================
Liste des informations générées à chaque connexion dans la homepage
=====================================================================

* Infos de connexion :
    - "Environnement"
    - "Clé d'auth avec masque"
    - "État du réseau"

* Statistiques Judilibre :
    - "Date de création la plus récente" 
    - "Total textes"
    - "Nb textes - cour de cassation"
    - "Créés hier - cour de cassation"
    - "Créés [mois en cours] - cour de cassation"
    - "Créés [mois en passé] - cour de cassation"
    - "Nb textes - cours d'appel"
    - "Créés hier - cours d'appel"
    - "Créés [mois en cours] - cours d'appel"
    - "Créés [mois en passé] - cours d'appel"

=========================================================
Liste des champs pour le formulaire de recherche
=========================================================

Ils seront divisés en 3 frames disctinctes dans le formulaire :
  * Recherche simple = recherche par ID Judilibre
  * Recherche combineée = recherche selon les critères donnés ci-dessous
  * Taxonomy : recherche par termes = commande spéciale à l'API

+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| Critère API  | Type valeur  | Type commande   | widget | Label widget          | Type Widget tkinter                             | Valeur par défaut    |
+==============+==============+=================+========+=======================+=================================================+======================+
| date_type    | string       | export          | oui    | Type de date          | Listbox (StringVar)                             | creation             |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| query        | string       | search          | oui    | Mot(s) clé(s)         | entry (StringVar)                               | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| operator     | string       | search          | oui    | Opérateur             | Listbox(StringVar)                              | none (or in the API) |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| type         | list[string] | search & export | oui    | Nature de la décision | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| chamber      | list         | search & export | oui    | Chambre               | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| formation    | list         | search & export | oui    | Formation             | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| jurisdiction | list         | search & export | oui    | Juridiction           | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| publication  | list         | search & export | oui    | Publication           | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| solution     | list         | search & export | oui    | Solution              | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| date_start   | ISO-8601     | search & export | oui    | Du                    | entry (StringVar) (voir Alan D. Moore Solution) | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| date_end     | ISO-8601     | search & export | oui    | Au                    | entry (StringVar) (voir Alan D. Moore Solution) | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| id           | string       | taxonomy        | oui    | Métadonnée            | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| key          | string       | taxonomy        | oui    | Abréviation           | Entry(StringVar)                                | tous                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| value        | string       | taxonomy        | oui    | Intitulé complet      | Entry(StringVar)                                | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| id           | string       | Decision        | oui    | ID Judilibre          | Entry(StringVar)                                | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| theme        | string       | search $ export | oui    | Matière cc            | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| theme + ca   | string       | search $ export | oui    | Matière ca            | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+
| location + ca| string       | search $ export | oui    | Siège ca              | Listbox(StringVar)                              | none                 |
+--------------+--------------+-----------------+--------+-----------------------+-------------------------------------------------+----------------------+

J'avais choisi comme widget principal "Combobox" mais celui-ci ne supporte pas le choix de plusieurs valeurs.
https://stackoverflow.com/questions/34549752/how-do-i-enable-multiple-selection-of-values-from-a-combobox
=> Finalement, ListBox a été choisi.

==================================================================
Colonnes de la liste de résultats
==================================================================

La list de résultats est conçue grâce au widget tkinter "treeview" :

+------------------------+---------------+-------+----------------+---------+----------+--------------+
| Id decision (interne)  | jurisdiction  | type  | decision_date  | number  | chamber  | publication  |
+------------------------+---------------+-------+----------------+---------+----------+--------------+


==================================================================
Validation des données dans le formulaire
==================================================================

  * Les 3 types de recherche devront intéragir entre elles telles des
    RadioButton. Seule l'une d'elles doit être active [Fait]
  * Dans Taxonomy, désactiver Abréviation ou Intitulé complet [Fait]
  * Dans Recherche combinée, désactiver Type de date si un mot clé existe [Fait]
  * Améliorer les champs de date pour qu'ils bloquent l'utilisateur en cas
    de mauvais format.

======================================================================
Validation de données à prévoir dans un second temps de développement
======================================================================

  * login_page -> key format
  * vérification du formate de date dans le formulaire
  * vérification du format d'ID JUDILIBRE dans le formulaire

==================================================================
Les listes des métadonnées collectées qui ne sont pas string
==================================================================

* Search :
   * numbers = list -> string
   * publication = list -> string
   * themes = list -> string
   * file = list -> dict

* Export :
   * numbers = list -> string
   * publication = list -> string
   * file = list -> dict
   * contested ("Décision attaquée") = dict
   * timeline ("Les dates clés") = list -> dict 
   * visa ("Textes appliqués") = list -> dict
   * rapprochement = list -> dict
   * legacy = list

==================================================================
Réflexion sur le traitement des données collectées [2022-10-20]
==================================================================

Les réponses obtenues par les requêtes Search ou Export sont stockés
dans un dictionnaire pour le moment. Chaque décision a son propre dictionnaire
de données.

Utiliser un dataframe pandas permettrait :
  * Une meilleure performance de l'application
  * Eviter les boucles for
  * Obtenir toute sorte de statistiques très simplement
  * Créer un tk.treeview à partir de ce dataframe
  * Faciliter l'export au format Excel ou CSV

!! Avantage supplémentaire : mise en pratique de la formation Analyse de données

La première version de l'application a été construite sans Pandas. Elle
fonctionne rapidement et donne satisfaction. Mais il faudra peut-être repenser
la structure tout de même.

========================
Améliorations possibles
========================

  * Ajouter les fonctions de tri sur le treeview (cf. Adam Moore)

  * Filtre des résultats grâce aux critères de second niveau
      * Les champs de second niveaux sont en réalité les métadonnées obtenues dans la
        réponse. Techniquement, il faudra donc faire une recherche avec les champs de 
        niveau 1 puis filtrer selon les critères de second niveau transmis dans le 
        formulaire.
      * Je pense qu'il est possible de proposer les filtres sur la page de
        résultat plutôt que dans le formulaire. Le treeview réagit très bien,
        il pourrait être actualisé sans souci par rapport à un critère.
      * Cependant Pandas serait encore mieux sans doute.

  * Meilleure gestion des images (voir p.278 Adam's book)

  * Améliorer les barres de progression et les icônes animés d'attente
      * Cf. les explications d'Adam Moore sur le multi-threading
      * cf. doc tkinter https://tkdocs.com/tutorial/eventloop.html#asyncio
      * La version 1.0 ne propose qu'un affichage simple de fenêtre.

=====================================
Sécurité des données utilisateurs
=====================================

Cette application ne manipule qu'une seule donnée sensible :
La clé d'authentification de l'utilisateur qui donne l'accès à l'API Judilibre.
=> Il est nécessaire de la conserver de manière sécurisée.
Les pistes de réflexion :

* https://stackoverflow.com/questions/64844995/how-to-encrypt-and-decrypt-a-string-with-a-password-with-python
* https://stackoverflow.com/questions/73532164/proper-data-encryption-with-a-user-set-password-in-python3/73551491#73551491
* https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
* https://onboardbase.com/blog/aes-encryption-decryption/
* https://pycryptodome.readthedocs.io/en/latest/src/examples.html#generate-an-rsa-key

Finalement, aucune solution viable n'a été trouvée.
Deux réponses obtenus m'ont conforté dans l'idée qu'un dispositif n'était nécessaire dans mon cas :

1. Réponse Discord : https://discord.com/channels/267624335836053506/1035199133436354600/threads/1060671948738265098
      *it's not really an issue if the API key just lives in the code in plaintext.*
      *Unless you're storing that key into a file without any encryption, just holding it in memory is quite safe*
      *that's because no other (unprivilledged) programs can access the memory of other programs*
      *and the user needs to be entering the key manually each time*
  
2. Réponse Stackoverflow : https://stackoverflow.com/questions/75024494/encrypt-or-hide-users-api-key-used-in-program-python-3
      *I don't think this is possible by the time you need your key in plaintext form to send requests to the API,*
      *except if API supports an encryption system and make an E2E encryption,*
      *so you send the key encrypted and the API's server decrypts it*

................................
OUTILS ANNEXES
................................

==================================================================
reStructured Text et Docutils
==================================================================

Docutils est un package installé par pip.
Il permet de transformer les fichiers .rst en d'autres formats notamment HTML.
Le script Python dans le cadre de ce projet se trouve dans
.venv\Scripts\rst2html.py

Lors de la génération html, si problème alors vérifier la longueur des signes qui anglobent les sections et titres

J'ai utilisé  https://tableconvert.com/excel-to-restructuredtext pour la
conversion Excel en fichier restructuredText


==================================================================
pyinstaller : comment créer l'exécutable
==================================================================

  * Aller voir la documentation ici https://pyinstaller.org/en/stable/index.html
  * Installer pyinstaller avec pip
      ``pip install pyinstaller``
  * Générer le fichier .spec à partir du script princpal
      ``pyi-makespec pycoretext.py``
  * Ouvrir le fichier pycoretext.spec et ajouter les éléments suvants dans l'attribut "datas" :
      - 'LICENCE.txt'
      - 'REAMDME.rst'
      - '.\docs\demo.gif'
      - '.\docs\schema_pycoretext.jpg'
      - '.\docs\CGU_open_data_V8.pdf'
      - '.\\pycoretext\\views\\image_login.png'
      - '.\\pycoretext\\views\\origine_donnees.txt'
      - '.\docs\specifications_techniques.rst'
      - '.\\pycoretext\\pycoretext.ico'
      - 'pycoretext.spec'
  * Ajouter aussi l'icône dans la partie "exe"
      "icon='.\pycoretext\pycoretext.ico'"
  * Lancer la création du bundle :
      ``pyinstaller pycoretext.spec``
  * Vérifier le contenu du dossier "dist" créé
  * Vérifier le bon fonctionnement de l'exécutable
  * Changer le nom du dossier \dist\pycoretext en \dist\pycoretext_v_xx_xx
  * Compresser le dossier \pycoretext_v_xx_xx et le placer dans \bin 

==================================================================
Git et GitHub
==================================================================

Le développement s'est déroulé sur un dépôt local.
Ce dernier étant devenu trop brouillon, il a été nécessaire de recomposer la structure du projet.
Je suis donc reparti de zéro.
C'est pourquoi le projet publié sur GitHub au final ne comporte que peut de commits.

Pour un bon exemple de fichier .gitignore :
https://github.com/github/gitignore/blob/main/Python.gitignore

=====================================================================
Note de lecture du guide RGPD pour l'équipe de développement
=====================================================================

https://www.cnil.fr/fr/la-cnil-publie-un-guide-rgpd-pour-les-developpeurs

  * Conserver les secrets et mots de passe en dehors de dépôt de code source
  * Chiffrement et déchiffrement de la clé d'authentification (Indiquer
    la méthode utilisée)
  * Purge automatique des données proposées à la fermeture de l'application
  * Documentation et licence
  * PEP8 conformité
  * Information sur la source des données
  * Indiquer l'objectif de l'application
  * Respect des conditions générales d'utilisation
