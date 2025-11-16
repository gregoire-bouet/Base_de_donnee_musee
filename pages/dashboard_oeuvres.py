
# Importation des bibliothèques nécessaires pour la création de l'application Dash
import plotly.express as px
import pandas as pd
from pathlib import Path
import unicodedata
import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import numpy as np
import os

# ----------------------------
# Fonctions utilitaires et chargement des données
# ----------------------------

def _normalize_col(name: str) -> str:
    """
    Normalise un nom de colonne en supprimant les accents,
    remplaçant les caractères spéciaux par des underscores,
    et mettant tout en minuscules.
    """
    s = str(name)
    # Décompose les caractères accentués (e.g., é -> e + accent)
    s = unicodedata.normalize("NFKD", s)
    # Supprime les accents
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # Met en minuscule et retire les espaces en début/fin
    s = s.lower().strip()
    # Remplace les caractères spéciaux par des underscores
    for ch in (" ", "/", ">", "-", ".", ",", ";", ":", "(", ")", "'", '"'):
        s = s.replace(ch, "_")
    # Supprime les underscores multiples ou vides
    parts = [p for p in s.split("_") if p]
    return "_".join(parts)

def load_data():
    """
    Charge le fichier CSV 'oeuvres.csv' à partir de plusieurs emplacements possibles.
    Normalise les noms des colonnes.
    Filtre les dates pour ne garder que celles <= 2025.
    """
    # Détermine le répertoire racine du projet
    project_root = Path(__file__).resolve().parent.parent
    # Liste des chemins possibles pour le fichier CSV
    candidates = [
        project_root / "oeuvres.csv",
        project_root / "data" / "oeuvres.csv",
        Path("oeuvres.csv"),
        Path("data") / "oeuvres.csv",
        Path("/data/oeuvres.csv"),
    ]

    last_error = None
    for p in candidates:
        try:
            if p.exists():
                df = pd.read_csv(p, sep=";", encoding="utf-8")
                break
        except Exception as e:
            last_error = e
            continue
    else:
        # Si aucun fichier n'a été trouvé, lève une erreur
        tried = ", ".join(str(p) for p in candidates)
        msg = f"Fichier 'oeuvres.csv' introuvable. Chemins testés: {tried}."
        if last_error:
            msg += f" Dernière erreur lors de la lecture: {last_error}"
        raise FileNotFoundError(msg)

    # Normalise les noms de colonnes pour faciliter l'accès
    df.columns = [_normalize_col(c) for c in df.columns]

    # Si la colonne de date existe, la convertit en numérique et filtre les dates
    if "date_de_l_oeuvre_ou_de_l_artiste" in df.columns:
        df["date_de_l_oeuvre_ou_de_l_artiste"] = pd.to_numeric(
            df["date_de_l_oeuvre_ou_de_l_artiste"], errors="coerce"
        )
        df = df[df["date_de_l_oeuvre_ou_de_l_artiste"] <= 2025]
    return df

# Chargement des données au démarrage de l'application
df = load_data()

# Si la colonne 'domaine' n'existe pas, on la crée avec une valeur par défaut
if "domaine" not in df.columns:
    df["domaine"] = "Aucune donnée"

# Récupère la liste des domaines uniques, triés
domaines = sorted(df["domaine"].dropna().unique())

# ----------------------------
# Définition de la barre latérale (sidebar)
# ----------------------------
sidebar = html.Div([
    dbc.Card(
        dbc.CardBody([
            html.H5("ℹ️ Informations", className="card-title"),
            html.Div([
                html.P(f"Nombre total d'œuvres: {len(df)}"),
                html.P(f"Nombre de domaines: {len(domaines)}")
            ]),
            html.Hr(), # Ligne horizontale
            html.H6("📅 Filtre temporel"),
            # Slider pour filtrer les données par année
            dcc.RangeSlider(
                id='year-range-slider',
                min=0,
                max=2025,
                value=[0, 2025], # Valeur par défaut
                step=1,
                marks={}, # Les marques seront définies dynamiquement
                tooltip={"placement": "bottom", "always_visible": True}
            ),
            html.Hr(),
            html.H6("🔬 Exploration libre"),
            # Dropdown pour choisir la variable X
            dcc.Dropdown(
                id='x-var',
                options=[{'label': c, 'value': c} for c in df.columns],
                placeholder='Variable X'
            ),
            # Dropdown pour choisir la variable Y
            dcc.Dropdown(
                id='y-var',
                options=[{'label': c, 'value': c} for c in df.columns],
                placeholder='Variable Y'
            ),
            html.Hr(),
            # Bouton de réinitialisation
            dbc.Button("🔄 Réinitialisation", id="reset-button", n_clicks=0, color='secondary', className='mt-2'),
            html.Br(),
            html.Hr(),
            # Lien vers la page de carte
            dcc.Link(
                dbc.Button("🗺️ Voir la carte", color="primary", className='mt-2'),
                href="/carte-musees",
                style={"textDecoration": "none"}
            ),
        ]),
        className="h-100",
        style={"backgroundColor": "#FFFFFF", "color": "#000000", "display": "flex", "flexDirection": "column"}
    ),
], style={"height": "100vh", "display": "flex", "flexDirection": "column"})

# ----------------------------
# Définition du layout principal
# ----------------------------
layout = dbc.Container([
    # Lien de retour à l'accueil
    html.Div([
        dcc.Link(
            dbc.Button("← Retour à l'accueil", color="outline-secondary", className="mb-3"),
            href="/accueil",
            style={"textDecoration": "none"}
        ),
    ]),
    
    # Mise en page en ligne (Row) avec la sidebar et le contenu principal
    dbc.Row([
        dbc.Col(sidebar, width=3, style={"height": "100vh"}), # Sidebar sur 3 colonnes
        dbc.Col([
            html.H1("📊 Dashboard Œuvres d'Art", style={"color": "#000000", "marginBottom": "20px"}),
            # Titre dynamique pour le domaine sélectionné
            html.Div(id="domain-title", style={"marginBottom": "20px"}),
            html.Div([
                # Boutons pour sélectionner un domaine spécifique
                html.Div(
                    [
                        html.Button(
                            domaine if pd.notna(domaine) else "Inconnu",
                            id=f"btn-{i}",
                            style={
                                "margin": "4px",
                                "padding": "6px 12px",
                                "borderRadius": "6px",
                                "border": "none",
                                "backgroundColor": "#939393",
                                "color": "#000000",
                                "cursor": "pointer",
                                "fontSize": "0.85rem",
                            },
                        )
                        for i, domaine in enumerate(domaines)
                    ],
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "justifyContent": "start",
                        "marginBottom": "25px",
                    },
                ),
                # Graphique principal
                dcc.Graph(id="main-graph")
            ])
        ], width=9) # Contenu principal sur 9 colonnes
    ], style={"minHeight": "100vh", "backgroundColor": "#FFFFFF", "paddingTop": "20px", "height": "100vh"})
], fluid=True, style={"height": "100vh"})

# ----------------------------
# Fonctions utilitaires pour la création des graphiques
# ----------------------------

def group_ancient_dates(df, date_col, threshold):
    """
    Regroupe les dates antérieures à un seuil dans une catégorie unique.
    """
    df = df.copy()
    threshold_str = str(int(threshold))
    df["date_grouped"] = df[date_col].apply(
        lambda x: ("Anterieur à " + threshold_str) if x < threshold else str(int(x))
    )
    return df

def get_main_figure(pathname, year_range):
    """
    Retourne la figure Plotly appropriée en fonction de l'URL et de la plage temporelle.
    - Si une URL spécifique de domaine est fournie, affiche un graphique pour ce domaine.
    - Sinon, affiche un graphique de tous les domaines.
    """
    # Filtre les données selon la plage temporelle
    df_filtered = df[(df["date_de_l_oeuvre_ou_de_l_artiste"] >= year_range[0]) &
                     (df["date_de_l_oeuvre_ou_de_l_artiste"] <= year_range[1])]
    
    # Vérifie si l'URL spécifie un domaine particulier
    if pathname.startswith("/dashboard-oeuvres/") and pathname != "/dashboard-oeuvres":
        # Extrait le nom du domaine de l'URL (et remplace les espaces encodées)
        domaine = pathname.split("/dashboard-oeuvres/")[1].replace("%20", " ")
        
        # FILTRE les données pour ce domaine seulement
        df_domaine = df_filtered[df_filtered["domaine"] == domaine].copy()
        
        if df_domaine.empty:
            # Si aucune donnée pour ce domaine, affiche un graphique vide
            return px.scatter(title=f"Aucune donnée pour {domaine} dans cette plage")
        
        # Analyse par siècle pour le domaine sélectionné
        df_domaine = df_domaine.dropna(subset=["date_de_l_oeuvre_ou_de_l_artiste"])
        
        if df_domaine.empty:
            # Si aucune date valide, affiche un graphique vide
            return px.scatter(title=f"Aucune date disponible pour {domaine} dans cette plage")
        
        # Calcul des siècles
        min_year = df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].min()
        max_year = df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].max()
        
        start_century = (int(min_year) // 100) * 100
        end_century = (int(max_year) // 100 + 1) * 100
        bins = list(range(start_century, end_century + 100, 100))
        labels = [f"{b}-{b+99}" for b in bins[:-1]]
        
        df_domaine["siecle"] = pd.cut(
            df_domaine["date_de_l_oeuvre_ou_de_l_artiste"], 
            bins=bins, 
            labels=labels, 
            right=False
        )
        
        # Compte le nombre d'œuvres par siècle
        counts_by_century = df_domaine["siecle"].value_counts().sort_index().reset_index()
        counts_by_century.columns = ["siecle", "nombre_d_oeuvres"]
        
        # Crée un graphique à barres
        fig = px.bar(
            counts_by_century,
            x="siecle",
            y="nombre_d_oeuvres",
            color="siecle",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"Répartition par siècle - Domaine : {domaine}",
            labels={"siecle": "Siècle", "nombre_d_oeuvres": "Nombre d'œuvres"}
        )
    
    else:
        # Vue générale - tous les domaines
        if df_filtered.empty:
            # Si aucune donnée filtrée, graphique vide
            fig = px.bar(title="Aucune donnée disponible dans cette plage")
        else:
            # Compte le nombre d'œuvres par domaine
            counts_filtered = df_filtered["domaine"].value_counts().reset_index()
            counts_filtered.columns = ["domaine", "nombre_d_oeuvres"]
            # Crée un graphique à barres
            fig = px.bar(
                counts_filtered,
                x="domaine",
                y="nombre_d_oeuvres",
                color="domaine",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                title="Nombre d'œuvres par domaine"
            )
    
    # Mise en page du graphique
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font_color="#000000",
        xaxis_tickangle=-45,
        yaxis={"gridcolor": "#334155"},
        showlegend=False,
        margin=dict(b=150, t=60),
    )
    return fig

# ----------------------------
# Définition des callbacks
# ----------------------------

def register_callbacks(app):
    """
    Enregistre tous les callbacks de l'application Dash.
    Ces callbacks gèrent l'interaction entre les composants de l'interface.
    """
    
    # Callback pour la navigation (changement d'URL)
    @app.callback(
        Output('url', 'pathname'), # Met à jour l'URL
        [Input(f'btn-{i}', 'n_clicks') for i in range(len(domaines))], # Boutons de domaine
        Input("reset-button", "n_clicks"), # Bouton de réinitialisation
        prevent_initial_call=True
    )
    def redirect(*args):
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Si c'est le bouton de réinitialisation
        if trigger_id == "reset-button":
            return "/dashboard-oeuvres" # Retourne à la vue générale
        
        # Si c'est un bouton de domaine
        if trigger_id.startswith('btn-'):
            index = int(trigger_id.split('-')[1])
            domaine = domaines[index]
            domaine_encoded = domaine.replace(" ", "%20") # Encode les espaces pour l'URL
            return f"/dashboard-oeuvres/{domaine_encoded}" # Redirige vers le domaine
        
        return dash.no_update

    # Callback pour mettre à jour le titre du domaine affiché
    @app.callback(
        Output("domain-title", "children"), # Met à jour le contenu HTML du titre
        Input("url", "pathname"), # Utilise l'URL pour savoir quel domaine est actif
        Input("year-range-slider", "value") # Utilise la plage temporelle
    )
    def update_domain_title(pathname, year_range):
        # Filtre les données selon la plage temporelle
        df_filtered = df[(df["date_de_l_oeuvre_ou_de_l_artiste"] >= year_range[0]) &
                         (df["date_de_l_oeuvre_ou_de_l_artiste"] <= year_range[1])]
        
        # Vérifie si l'URL spécifie un domaine particulier
        if pathname.startswith("/dashboard-oeuvres/") and pathname != "/dashboard-oeuvres":
            domaine = pathname.split("/dashboard-oeuvres/")[1].replace("%20", " ")
            df_domaine = df_filtered[df_filtered["domaine"] == domaine]
            count_oeuvres = len(df_domaine)
            return html.Div([
                html.H2(f"Domaine : {domaine}", 
                       style={"color": "#000000", "fontSize": "1.5rem", "marginBottom": "5px"}),
                html.P(f"{count_oeuvres} œuvres dans cette plage temporelle", 
                      style={"color": "#666666", "fontSize": "1rem", "marginBottom": "20px"})
            ])
        else:
            count_total = len(df_filtered)
            return html.Div([
                html.H2("Vue d'ensemble de tous les domaines", 
                       style={"color": "#000000", "fontSize": "1.5rem", "marginBottom": "5px"}),
                html.P(f"{count_total} œuvres au total dans cette plage temporelle", 
                      style={"color": "#666666", "fontSize": "1rem", "marginBottom": "20px"})
            ])

    # Callback pour ajuster dynamiquement les paramètres du slider temporel
    @app.callback(
        Output("year-range-slider", "marks"), # Marques sur le slider
        Output("year-range-slider", "min"), # Valeur minimale
        Output("year-range-slider", "max"), # Valeur maximale
        Output("year-range-slider", "value"), # Valeur actuelle
        Output("year-range-slider", "step"), # Pas d'incrément
        Input("url", "pathname") # L'URL détermine le jeu de données à analyser
    )
    def update_slider(pathname):
        # Filtre les données selon l'URL (domaine spécifique ou général)
        if pathname.startswith("/dashboard-oeuvres/") and pathname != "/dashboard-oeuvres":
            domaine = pathname.split("/dashboard-oeuvres/")[1].replace("%20", " ")
            subset = df[df["domaine"] == domaine].dropna(subset=["date_de_l_oeuvre_ou_de_l_artiste"])
        else:
            subset = df.dropna(subset=["date_de_l_oeuvre_ou_de_l_artiste"])

        if subset.empty:
            # Si aucune donnée, définit des valeurs par défaut
            min_year, max_year = 0, 2025
        else:
            # Calcule les bornes en fonction des données
            min_raw = int(np.percentile(subset["date_de_l_oeuvre_ou_de_l_artiste"], 5))
            min_year = min_raw // 100 * 100 # Arrondi à la centaine inférieure
            max_year = min(int(subset["date_de_l_oeuvre_ou_de_l_artiste"].max()), 2025)

        span = max_year - min_year
        # Définit le pas en fonction de l'étendue des dates
        if span <= 100:
            step = 1
        elif span <= 500:
            step = 10
        elif span <= 2000:
            step = 50
        else:
            step = 100

        # Calcule les marques à afficher sur le slider
        num_marks = min(10, max(2, span // step + 1))
        step_marks = max(200, span // (num_marks - 1)) if span > 0 else 1
        step_marks = step_marks // step * step if step > 0 else step_marks

        marks = {}
        for year in range(min_year, max_year + 1, step_marks):
            marks[year] = str(year)

        marks[min_year] = str(min_year)
        marks[max_year] = str(max_year)

        return marks, min_year, max_year, [min_year, max_year], step

    # Callback pour filtrer les options du dropdown Y en fonction de X
    @app.callback(
        Output("y-var", "options"), # Met à jour les options du dropdown Y
        Input("x-var", "value") # La valeur du dropdown X
    )
    def filter_y_options(x_col):
        if not x_col:
            # Si X n'est pas sélectionné, montre toutes les colonnes numériques
            return [{'label': c, 'value': c} for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        # Si X est numérique, Y doit aussi être numérique
        if pd.api.types.is_numeric_dtype(df[x_col]):
            return [{'label': c, 'value': c} for c in df.select_dtypes(include='number').columns]
        else:
            # Si X est non numérique, Y doit être numérique
            return [{'label': c, 'value': c} for c in df.select_dtypes(include='number').columns]

    # Callback principal pour mettre à jour le graphique principal
    @app.callback(
        Output("main-graph", "figure"), # Met à jour le graphique
        Input("x-var", "value"), # Variable X pour l'exploration libre
        Input("y-var", "value"), # Variable Y pour l'exploration libre
        Input("url", "pathname"), # L'URL pour savoir quel domaine afficher
        Input("year-range-slider", "value") # La plage temporelle
    )
    def update_main_graph(x_col, y_col, pathname, year_range):
        # Filtre les données selon la plage temporelle
        df_filtered = df[(df["date_de_l_oeuvre_ou_de_l_artiste"] >= year_range[0]) &
                         (df["date_de_l_oeuvre_ou_de_l_artiste"] <= year_range[1])]
        
        # Si une URL spécifique de domaine est active, filtre les données pour ce domaine
        if pathname.startswith("/dashboard-oeuvres/") and pathname != "/dashboard-oeuvres":
            domaine = pathname.split("/dashboard-oeuvres/")[1].replace("%20", " ")
            df_filtered = df_filtered[df_filtered["domaine"] == domaine]
        
        # Si les variables X et Y sont sélectionnées, crée un graphique d'exploration libre
        if x_col and y_col:
            try:
                fig = px.scatter(df_filtered, x=x_col, y=y_col)
                fig.update_layout(
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF",
                    font_color="#000000",
                    xaxis_tickangle=-45,
                    yaxis={"gridcolor": "#334155"},
                    margin=dict(b=150, t=60)
                )
                return fig
            except:
                # Si la création du graphique échoue
                return px.scatter(title="Impossible de créer le graphique")

        # Sinon, utilise la logique basée sur l'URL (vue générale ou spécifique)
        return get_main_figure(pathname, year_range)
