# Dashboard d'Analyse — Musées français

Ce dépôt contient un **dashboard interactif** permettant d’explorer, d’analyser et de visualiser les données relatives aux oeuvres des musées français et leur origine.

---

## User Guide

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/ton-utilisateur/ton-projet.git
   cd ton-projet

2. **Créer un environnement virtuel** (optionnel mais recommandé)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # sous macOS/Linux
   .venv\Scripts\activate     # sous Windows  


3. **Installer les dépendances**
   ```bash   
   pip install -r requirements.txt  
   
4. **Lancer le dashboard**
   ```bash   
   python main.py


### Data

#### Source des données

   Les données utilisées dans ce projet proviennent du **Centre de Recherche et de Restauration des Musées de France (C2RMF)** et sont accessibles publiquement sur le portail [data.gouv.fr](https://www.data.gouv.fr/fr/).

 [Notices d'œuvres du Centre de Recherche et de Restauration des Musées de France (C2RMF)](https://www.data.gouv.fr/fr/datasets/notices-doeuvres-du-centre-de-recherche-et-de-restauration-des-musees-de-france-c2rmf/)

   Ces données sont publiées par le **Ministère de la Culture** et regroupent les notices d'œuvres étudiées ou restaurées par le C2RMF.

#### Format et contenu

- **Format :** CSV (et disponible en d'autres formats selon le jeu de données)
- **Nombre d’enregistrements :** plusieurs dizaines de milliers de notices
- **Variables principales :**
  - `Identifiant` : identifiant unique de l’œuvre
  - `Titre` : titre de l’œuvre
  - `Artiste` : nom de l’auteur ou du créateur
  - `Datation` : période ou date de création
  - `Technique` : matériaux ou procédés utilisés
  - `Propriétaire` : musée ou institution détentrice
  - `Description` : résumé de l’œuvre ou de son étude

### Developper guide

#### Architecture du code

Base_de_donnee_musee/
│
├── main.py                 # Point d'entrée principal
├── requirements.txt        # Packages additionnels requis pour bon fonctionnement de l'app
├── pages/                  # Pages de l'application
│   ├── __init__.py
│   ├── accueil.py          # Page d'accueil
│   ├── dashboard_oeuvres.py # Dashboard des œuvres
│   └── carte_musees.py     # Carte des musées
│
├── data/                  # Données et utilitaires
│   ├── oeuvres.csv        # Dataset principal
│   ├── cleaned_oeuvres.csv # Csv retourné par geocoding.py (pour un fonctionnement hors ligne)
│   └── geocoding.py       # Fonctions de géolocalisation
│
└── images/                     # Images extraites de l'application et utilisées 
    ├── Carte_musée.png         # pour illustrer le rapport d'analyse
    ├── Graphe_céramique.png
    └── Graphe_domaines.png

#### Ajouter une Nouvelle Page
**Étape 1** : Créer le fichier de page
   ```bash 
   import dash
   from dash import html, dcc
   import dash_bootstrap_components as dbc
   
   # Layout de la page
   layout = dbc.Container([
       html.H1("Ma Nouvelle Page"),
       html.P("Contenu de la nouvelle page..."),
       dcc.Graph(id='graphique-nouveau')
   ])
   
   # Callbacks (optionnel)
   def register_callbacks(app):
       @app.callback(
           Output('graphique-nouveau', 'figure'),
           Input('some-input', 'value')
       )
       def update_graph(value):
           # Logique du callback
           return figure
   ```
**Étape 2** : Ajouter la route dans main.py
   ```bash
   # Dans le callback display_page, ajoutez :
   def display_page(pathname):
       if pathname == '/ma-nouvelle-page':
           from pages.ma_nouvelle_page import layout
           return layout
       # ... routes existantes
   ```
**Étape 3** : Ajouter le lien dans la navigation
   ```bash
      # Dans la navbar de main.py, ajoutez :
      dbc.NavItem(dbc.NavLink("📊 Nouvelle Page", href="/ma-nouvelle-page", active="exact"))
   ```

####Exemple Complet : Ajout d'un Graphique Circulaire
   ```bash
      # Dans pages/dashboard_oeuvres.py, ajoutez :
      
      layout = dbc.Container([
          # ... layout existant
          
          # Nouvelle ligne avec graphique circulaire
          dbc.Row([
              dbc.Col([
                  html.H3("Répartition par Domaine"),
                  dcc.Graph(id='pie-chart-domaines')
              ], width=6)
          ], className="mt-4")
      ])
      
      def register_callbacks(app):
          # ... callbacks existants
          
          # Nouveau callback pour le graphique circulaire
          @app.callback(
              Output('pie-chart-domaines', 'figure'),
              Input('url', 'pathname'),
              Input('year-range-slider', 'value')
          )
          def update_pie_chart(pathname, year_range):
              df_filtered = df[(df["date_de_l_oeuvre_ou_de_l_artiste"] >= year_range[0]) &
                               (df["date_de_l_oeuvre_ou_de_l_artiste"] <= year_range[1])]
              
              counts = df_filtered["domaine"].value_counts()
              fig = px.pie(values=counts.values, names=counts.index, title="Répartition par domaine")
              return fig
   ```

### Rapport d'analyse

#### 1. Domination de peinture
Les peintures représentent le domaine le plus important de la collection.
![Pricipaux domaines artistiques](./image/Graphe_domaines.png)

#### 2. Age de la céramique et de la terre
Comme on aurais pu s'y attendre, l'âge d'or de la céramique et de la terre à eu lieu au premier siècle de notre ère si l'on en croit les quantité datée de cette époque
![Age d'or de la céramique et de la terre](./image/Graphe_céramique.png)

#### 3. Majorité en région parisienne
On remarque qu'à l'échelle francaise, la majorité des oeuvres sont concentrées en Ile-de-France
![Concentration Ile-de-France](./image/Carte_musée.png)


### Développement futurs 
Voici ici une liste non exaustive des idées que nous avions eu.
Nous n'avons malheureusement pas eu le temps de les implementer.

**Phase 1 - Fondamentaux**
Recherche avancée et filtres combinés
Export des données et analyses

**Phase 2 - Expérience enrichie**
Intégration d'APIs externes : wikipédia par exemple pour récuperer les images des différentes oeuvres

**Phase 3 - Innovation**
Analyses par intelligence artificielle


### Copyright

Je confirme que l’ensemble du code présent dans ce dépôt a été produit par mes soins/nos soins, hormis les segments clairement indiqués comme provenant d’autres sources.

Tout code non listé comme emprunté est considéré comme original et développé par l’auteur ou les auteurs du projet.  
L’omission de déclarer un emprunt constituera un acte de plagiat.

