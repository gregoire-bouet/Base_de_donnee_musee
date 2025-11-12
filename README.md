# Dashboard d'Analyse — [Nom du projet]

Ce dépôt contient un **dashboard interactif** permettant d’explorer, d’analyser et de visualiser les données relatives à [thème ou domaine du projet].

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

👉 [Notices d'œuvres du Centre de Recherche et de Restauration des Musées de France (C2RMF)](https://www.data.gouv.fr/fr/datasets/notices-doeuvres-du-centre-de-recherche-et-de-restauration-des-musees-de-france-c2rmf/)

Ces données sont publiées par le **Ministère de la Culture** et regroupent les notices d'œuvres étudiées ou restaurées par le C2RMF.

#### 📦 Format et contenu

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

### ⚙️ Méthode d’accès

Les données peuvent être téléchargées directement à partir de la ressource statique sur data.gouv.fr :  
👉 [https://www.data.gouv.fr/fr/datasets/r/c70b2f9f-3b0b-4a36-80ef-39a8d260832e](https://www.data.gouv.fr/fr/datasets/r/c70b2f9f-3b0b-4a36-80ef-39a8d260832e)

Pour reproduire l’analyse localement :

```bash
wget https://www.data.gouv.fr/fr/datasets/r/c70b2f9f-3b0b-4a36-80ef


