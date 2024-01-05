"""""""""""""""""""""""""""""
PYCORE·TEXT
"""""""""""""""""""""""""""""

.. image:: .\\pycoretext\\views\\image_login.png

Une interface simple pour effectuer des requêtes avec l'API publique française JUDILIBRE.
L'utilisateur peut utiliser les critères de recherche de l'API afin d'accéder aux décisions de justice :

* Cours d'appel
* Cour de cassation

Les résultats correspondent aux métadonnées et aux textes des décisions.


......................
LICENCE
......................

Copyright 2022, Yohan Chevalier

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

...................
DÉTAILS TECHNIQUES
...................

Se reporter au fichier "specifications_techniques.rst" dans le dossier \\docs

https://github.com/YohanChevalier/PYCORETEXT/blob/main/docs/specifications_techniques.rst

..........................
 Version de l'application
..........................

Numéro de version actuel = 2.8.0
Date de publication = 2024-01

Liste des améliorations :
    * Ajout des statistiques propres aux textes des TJ
    * Ajout du contexte 'tj' pour les recherches de taxonomy
    * Ajout du 'Siège tj' et gestion des validations de données
    * Correction d'un bug d'affichage sur la page de résultats en taxonomy (disparition de la liste de critères)
    * Correction d'un bug lors de l'affichage des messages d'erreur


Version précédente = 2.5.0
Date de publication = 2023-07

Liste des améliorations :
    * Meilleure gestion des requêtes API (ratelimit et backoff)
    * Affichage dans la page d'acceuil du nombre de requêtes réalisées
    * Affichage dans les pages de résultats du nombre de décisions attendues et obtenues
    * Affichage de la liste des requêtes ayant rencontré une erreur
    * Mise à disposition du fichier "app_log.txt" qui offre un accès complet aux requêtes effectuées durant la session
    * Ajout d'un mode test qui génère des erreurs HTML aléatoire et permet d'observer les réactions de l'application
    * Utilisation du threading pour les messages d'attente
    * Lorsque la fenêtre principale est déplacée, les fenêtres supérieures suivront désormais
    * Renforcement des validations de données dans le formulaire
    * Redisposition des éléments du formulaire = gain d'espace + gain de rapidité au démarrage
    * Nouveau critère de recherche = texte avec pdf
    * Gestion des hyperliens pour 'Visa' et 'Rapprochement' la prévisualisation des métadonnées d'un résulat
    * Ajout d'une alerte lorsque le nombre de résultat atteint 10 000
    * Ajout d'une export Excel de la liste de résultat
    * Meilleure affichage des exceptions déclenchaient dans les threads
    * Ajout d'un timeout de 5 secondes sur les requêtes API
    * Correction de divers bugs
    * Modification de quelques libellésandbox

..............
INSTALLATION
..............

=================================
Systèmes d'exploitation supportés
=================================

Windows uniquement

Compatibilité UNIX à venir

========================================
Directement via l'interprétateur Python
========================================

1. Installer la dernière version de Python 3.xx.x : https://www.python.org/downloads/
    * Lors de l'installation, ajoutez le chemin Python à votre variable d'environnement

2. Installer GIT sur votre machine : https://git-scm.com/downloads

3. Cloner le dépôt en local sur votre machine
    ``git clone XXXXXXXX``

4. Installer *virtualenv*
    ``pip install virtualenv``

5. Créer votre environnement virtuel dans la copie du dépôt
    * Le nom de dossier choisis est toujours ".venv"
    * ``python -m venv \path\vers\la\copie\du\dépôt\.venv``

6. Activer votre environnement virtuel
    ``.venv\Scripts\activate``

7. Installer les librairies nécessaires grâce au fichier requirements.txt
    ``pip install -r requirements.txt``

8. Exécuter le fichier source nommé : "pycoretext.py"

========================================
Exécutable Windows
========================================

Le dossier "bin" contient la dernière version à jour de l'application.

1. Sur Github, télécharger le projet au format .zip
2. Ne conserver que le dossier .zip présent dans pycoretext\bin
    -> Son nom est "pycoretext_v_xx.zip" 
3. Décompresser ce fichier
4. Double-cliquer sur le fichier .exe qu'il contient

..............
UTILISATION
..............
================
Démonstration
================

Recherche des décisions de la cour d'appel d'Agen publiées en 2022 :

.. image:: .\\docs\\demo.gif

================
Connexion
================

1. Choisir l'environnement : sandbox ou production
2. Entrer la clé correspondante
3. Cliquer sur *CONNEXION* ou presser la touche *entrée* du clavier

================
Page principale
================

La partie de gauche propose des statistiques en temps réel.
La partie de droite correspond au formulaire de recherche.

================================
Choix des critères et recherche
================================

Les champs proposés ne peut pas tous être complétés en même temps.
Ils dépendent des possibilités données par l'API.
Un système automatique rend actifs ou inactifs les champs selon vos actions.

En revanche, certaines recherches incohérentes ne seront pas bloquées et vous n'obtiendrez pas de résultat.
Par exemple, rechercher des textes en cour de cassation en ayant précisé un "siège ca".

Pour lancer la recherche, appuyer sur le bouton *Recherche* ou presser la touche *entrée* du clavier.

==================
Liste de résultas
==================

L'API ne peut pas retourner plus de 10 000 résultats.
Si un mot-clé a été donné en critère alors le texte de la décision ne sera pas disponible.
Par contre les métadonnées sont toujours présentes.

Pour afficher, les métadonnées d'une décision, il faut double-cliquer dessus dans la liste ou presser la touche *entrée* du clavier. 

..............
API JUDILIBRE
..............

================
Liens utiles
================

* Site offiel de l'API : https://api.gouv.fr/les-api/api-judilibre
* Github : https://github.com/Cour-de-cassation/judilibre-search
* Accès grâce à la plateforme PISTE : https://piste.gouv.fr/
* Serveur Judilibre production : https://api.piste.gouv.fr/cassation/judilibre/v1.0
* Serveur Judilibre sandbox : https://sandbox-api.piste.gouv.fr/cassation/judilibre/v1.0

=============================
Autorisation d'accès à l'API
=============================

Pycoretext exige l'utilisation d'une clé d'authentification API.
L'utilisateur obtiendra cette clé en respectant les étapes suivantes :

1. Créer un compte sur la plateforme PISTE
2. Créer une *application*
3. Approuver les conditions générales d'utilisation de l'API Judilibre (production ou sandbox)
4. Générer une *API key*

Veuillez consulter le Guide d'utilisation et la FAQ PISTE pour une explication détaillée.

La *clé API* est demandée sur la page de connexion de l'application.

**La clé API n'est utilisée que durant l'exécution de l'application PYCORETEXT.**
**Elle n'est jamais sauvegardée dans un fichier ou une base de données.**

=========================================================
Utilisation des données par PYCORETEXT
=========================================================

Les données et métadonnées collectées par l'utilisateur ne sont pas altérées et sont transmises sans traitement intermédiaire.
Elles sont échangées directement entre l'API et l'application, aucune base de données n'est utilisée.
PYCORETEXT n'est donc ni réutilisateur, ni rediffuseur, ni responsable de traitement au sens du RGPD.
Nous ne pouvons donc ni filtrer, ni supprimer, ni modifier le contenu des décisions de justice.

Toutefois, il est à noter que certaines métadonnées proposées en résulats de recherche par l'API n'ont pas été retenues dans l'application.
L'objectif n'est pas l'occultation de certaines informations mais au contraire la simplification de l'accès à l'information.
Les détails dans le fichier suivant :

https://github.com/YohanChevalier/PYCORETEXT/blob/main/docs/specifications_techniques.rst

=======================================================
Conditions d'utilisation à respecter par l'utilisateur
=======================================================

Puisque PYCORETEXT n'est qu'un habillage de l'API JUDILIBRE, les conditions d'utilisation de cette dernière priment.

........................
PROJET D'APPRENTISSAGE
........................

================================================
Domaines et librairies abordés grâce à ce projet
================================================

* GIT et Github
* Environnements virtuels
* VIM
* VSCODE
* Traitement des chaînes de caractères
* Requêtes API REST grâce à *requests*
* Design et création GUI : *tkinter*
* Concurrence et *threading* : *ratelimit* et *backoff*
* Programmation orientée objets
* UX and UI (expérience utilisateur, interface utilisateur)
* RST format
* Créer un exécutable Windows
* Création de logiciel *open source*

============================
La route sinueuse de Python
============================

Les informations ci-dessous pourront intéressées d'autres apprentis sorciers.

Autodidacte, j'ai débuté en 2020 mon apprentissage de la programmation informatique, Python particulièrement.

Les bases du langage m'ont été données par Gérard Swinnen et son livre *Apprendre à programmer avec Python 3*.
Une version numérique est disponible ici : https://inforef.be/swi/download/apprendre_python3_5.pdf
Mais je conseille grandement l'achat du livre papier.

Ensuite, j'ai passé deux certifications avec *Python institute*
https://pythoninstitute.org/
Les ressources mises à disposition sont d'une grande qualité.

Enfin, la programmation orientée objet est devenue plus claire grâce à Alan D. Moore et son livre *Python GUI Programming with Tkinter*
https://github.com/PacktPublishing/Python-GUI-Programming-with-Tkinter

Je dois aussi cité mes autres supports :

* Les documentions officielles
* *Coder proprement* de Robert C. Martin
* *Git par la pratique* de David Demaree
* *Le petit Python* de Richard Gomez
* https://realpython.com/
* Stackoverflow
* https://discord.com/invite/python

Ce projet est la modeste démonstration de mes acquis.

.............
CONTRIBUTIONS
.............

============================
Vos retours sont importants
============================

Comme déjà expliqué, cette application est un projet d'étude.
Tout retour constructif est donc bienvenu !

Merci de créer un nouveau post dans *Issues* afin de partager vos remarques avec moi.
Je vous répondrai avec plaisir.

==========================
Osez les *pull requests*
==========================

Si le coeur vous en dit, vous pouvez proposer des changements à ce projet.
Pour cela veuillez suivre les étapes suivantes :

1. *Fork* ce dépôt et créer une nouvelle branche.
2. Effectuez les modifications.
3. Validez les modifications, et incluez des messages de validation clairs et concis lorsque vous le faites.
4. Une fois les modifications apportées, soumettez une demande de tirage (Pull Request) !
    Cf. https://www.armandphilippot.com/article/premiere-pull-request-github pour davantage de détails.

J'analyserai vos propositions et vous ferai un retour par la suite.

Merci d'avoir soumis une demande de retrait !
Nous apprécions vraiment le temps et les efforts que vous y avez consacrés :)
