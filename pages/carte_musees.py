# -------------------------------
# 🔧 IMPORTATIONS DES BIBLIOTHÈQUES
# -------------------------------

# Manipulation de données
import pandas as pd

# Visualisation interactive
import plotly.express as px

# Composants Dash (interface web interactive)
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc  # Thème Bootstrap

# Gestion de fichiers et chemins
from pathlib import Path

# Normalisation de texte (accents, caractères spéciaux)
import unicodedata

# Interactions système (optionnel ici)
import os


# -------------------------------
# 🔧 FONCTIONS UTILITAIRES
# -------------------------------

def _normalize_col(name: str) -> str:
    """
    Nettoie et standardise un nom de colonne :
    - Supprime les accents (ex: é → e)
    - Remplace les caractères spéciaux par des underscores
    - Met tout en minuscules
    - Évite les underscores multiples
    Utile pour éviter les erreurs d’accès aux colonnes dans les données.
    """
    s = str(name)
    s = unicodedata.normalize("NFKD", s)  # Décompose les caractères accentués
    s = "".join(ch for ch in s if not unicodedata.combining(ch))  # Supprime les accents
    s = s.lower().strip()
    for ch in (" ", "/", ">", "-", ".", ",", ";", ":", "(", ")", "'", '"'):
        s = s.replace(ch, "_")
    parts = [p for p in s.split("_") if p]  # Élimine les parties vides
    return "_".join(parts)


def parse_location(loc):
    """
    Analyse une chaîne de type "Musée du Louvre, Paris, France"
    et la décompose en : pays, ville, musée.
    - Gère les chaînes mal formatées ou manquantes.
    - Retourne une série Pandas nommée avec les 3 champs.
    """
    if pd.isna(loc):
        return pd.Series({"pays": None, "ville": None, "musee": None})
    
    parts = [p.strip() for p in loc.split(",")]
    if len(parts) >= 2:
        musee = parts[0]
        ville = parts[1]
        pays = parts[2] if len(parts) >= 3 else None
    elif len(parts) == 1:
        musee = parts[0]
        ville = None
        pays = None
    else:
        musee = ville = pays = None
    return pd.Series({"pays": pays, "ville": ville, "musee": musee})


# -------------------------------
# 🔹 CHARGEMENT ET PRÉPARATION DES DONNÉES
# -------------------------------

def load_data():
    """
    Charge le fichier 'cleaneddata_geocoded_villes.csv' en essayant plusieurs emplacements.
    - Gère les erreurs de fichier manquant.
    - Nettoie et convertit les colonnes de coordonnées géographiques (latitude/longitude).
    """
    # Chemins possibles vers le fichier de données
    project_root = Path(__file__).resolve().parent.parent
    candidates = [
        project_root / "cleaneddata_geocoded_villes.csv",
        project_root / "data" / "cleaneddata_geocoded_villes.csv",
        Path("cleaneddata_geocoded_villes.csv"),
        Path("data") / "cleaneddata_geocoded_villes.csv",
        Path("./data/cleaned_oeuvres.csv"),
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
        # Si aucun fichier n’est trouvé, affiche un message d’erreur détaillé
        tried = ", ".join(str(p) for p in candidates)
        msg = "Fichier 'cleaneddata_geocoded_villes.csv' introuvable. Chemins testés: " + tried
        if last_error:
            msg += f"; dernière erreur: {last_error}"
        raise FileNotFoundError(msg)

    # Normalise les noms des colonnes
    df.columns = [_normalize_col(c) for c in df.columns]

    # Convertit latitude/longitude en numérique, ou crée des colonnes vides si absentes
    if "latitude" in df.columns:
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    else:
        df["latitude"] = pd.NA
    if "longitude" in df.columns:
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    else:
        df["longitude"] = pd.NA

    return df


# Chargement des données
df = load_data()
df.columns = [_normalize_col(c) for c in df.columns]  # Répète la normalisation au cas où

# Extraction des informations géographiques si la colonne "lieu_de_conservation" existe
if "lieu_de_conservation" in df.columns:
    df[["pays", "ville", "musee"]] = df["lieu_de_conservation"].apply(parse_location)
else:
    # Si la colonne n’existe pas, on crée des valeurs par défaut
    df["pays"] = "Inconnu"
    df["ville"] = "Inconnu"
    df["musee"] = "Inconnu"

# Nettoyage des données manquantes pour éviter les erreurs dans les graphiques
df_clean = df.copy()
df_clean["pays"] = df_clean["pays"].fillna("Pays inconnu")
df_clean["ville"] = df_clean["ville"].fillna("Ville inconnue")
df_clean["domaine"] = df_clean["domaine"].fillna("Domaine inconnu")
df_clean["artiste"] = df_clean["artiste"].fillna("Artiste inconnu")
df_clean["titre_ou_designation"] = df_clean["titre_ou_designation"].fillna("Œuvre sans titre")

# Vérifie que les coordonnées géographiques existent (valeurs par défaut = Paris)
if "latitude" not in df_clean.columns:
    df_clean["latitude"] = 48.8566  # Latitude de Paris
if "longitude" not in df_clean.columns:
    df_clean["longitude"] = 2.3522  # Longitude de Paris


# -------------------------------
# 🗺️ LAYOUT DE LA PAGE CARTE (INTERFACE UTILISATEUR)
# -------------------------------

layout = dbc.Container([
    # Barre de navigation en haut
    html.Div([
        dcc.Link(
            dbc.Button("← Retour à l'accueil", color="outline-secondary", className="mb-3"),
            href="/",
            style={"textDecoration": "none"}
        ),
        dcc.Link(
            dbc.Button("📊 Voir le dashboard", color="outline-primary", className="mb-3 ms-2"),
            href="/dashboard-oeuvres",
            style={"textDecoration": "none"}
        ),
    ]),

    # En-tête avec statistiques agrégées
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("🗺️ Carte des Musées", className="display-4 mb-2", 
                       style={"fontWeight": "700", "textShadow": "2px 2px 4px rgba(0,0,0,0.3)"}),
                html.P("Explorez la répartition géographique des œuvres d'art à travers le monde", 
                      className="lead mb-4", style={"opacity": "0.9"}),
                
                # Cartes de statistiques clés
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H3(f"{len(df_clean):,}", style={"fontSize": "2.5rem", "marginBottom": "0"}),
                            html.P("Œuvres cataloguées", className="mb-0", style={"opacity": "0.9"})
                        ], style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "color": "white",
                            "borderRadius": "12px",
                            "padding": "1rem",
                            "textAlign": "center"
                        })
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df_clean['ville'].nunique():,}", style={"fontSize": "2.5rem", "marginBottom": "0"}),
                            html.P("Villes représentées", className="mb-0", style={"opacity": "0.9"})
                        ], style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "color": "white",
                            "borderRadius": "12px",
                            "padding": "1rem",
                            "textAlign": "center"
                        })
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df_clean['domaine'].nunique():,}", style={"fontSize": "2.5rem", "marginBottom": "0"}),
                            html.P("Domaines artistiques", className="mb-0", style={"opacity": "0.9"})
                        ], style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "color": "white",
                            "borderRadius": "12px",
                            "padding": "1rem",
                            "textAlign": "center"
                        })
                    ], width=3),
                    dbc.Col([
                        html.Div([
                            html.H3(f"{df_clean['artiste'].nunique():,}", style={"fontSize": "2.5rem", "marginBottom": "0"}),
                            html.P("Artistes uniques", className="mb-0", style={"opacity": "0.9"})
                        ], style={
                            "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "color": "white",
                            "borderRadius": "12px",
                            "padding": "1rem",
                            "textAlign": "center"
                        })
                    ], width=3),
                ], className="mt-4")
            ], style={
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white",
                "padding": "2rem 1rem",
                "borderRadius": "0 0 20px 20px",
                "boxShadow": "0 4px 20px rgba(0,0,0,0.1)"
            })
        ])
    ], className="mb-4"),

    # Contenu principal : Filtres + Visualisations
    dbc.Row([
        # 🎛️ Sidebar avec filtres
        dbc.Col([
            html.Div([
                html.H4("🔍 Filtres", className="mb-3", 
                       style={"color": "#667eea", "fontWeight": "600"}),
                
                # Filtre par domaine artistique
                html.Label("Domaines artistiques", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id="domain-filter",
                    options=[{"label": d, "value": d} for d in sorted(df_clean["domaine"].dropna().unique())],
                    multi=True,
                    placeholder="Tous les domaines...",
                    style={"borderRadius": "8px", "border": "2px solid #e9ecef"}
                ),
                
                html.Hr(className="my-4"),

                # Filtre par pays (appelé "Musée" dans l’UI mais utilise "pays")
                html.Label("Pays", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id="country-filter",
                    options=[{"label": p, "value": p} for p in sorted(df_clean["pays"].dropna().unique())],
                    multi=True,
                    placeholder="Tous les pays...",
                    style={"borderRadius": "8px", "border": "2px solid #e9ecef"}
                ),

                html.Hr(className="my-4"),

                # Instructions utilisateur
                html.Div([
                    html.H6("Instructions", className="fw-bold", style={"color": "#667eea"}),
                    html.P("• Cliquez sur un point de la carte pour explorer les œuvres", className="mb-1 small"),
                    html.P("• Utilisez les filtres pour affiner votre recherche", className="mb-1 small"),
                    html.P("• Zoom/dézoom avec la molette de la souris", className="mb-0 small")
                ], style={"background": "#f8f9fa", "padding": "1rem", "borderRadius": "8px"})
                
            ], style={
                "background": "white",
                "borderRadius": "12px",
                "boxShadow": "0 2px 10px rgba(0,0,0,0.08)",
                "padding": "1.5rem",
                "height": "fit-content"
            })
        ], width=3),

        # 📊 Zone principale : cartes et graphiques
        dbc.Col([
            # 🌍 Carte interactive des musées
            html.Div([
                html.Div([
                    html.H4("🗺️ Carte des œuvres par ville", 
                           style={"color": "#495057", "marginBottom": "1rem"}),
                    dcc.Graph(
                        id="museum-map", 
                        style={"height": "500px", "borderRadius": "10px"},
                        config={"displayModeBar": True, "displaylogo": False}
                    )
                ], style={
                    "background": "white",
                    "borderRadius": "15px",
                    "boxShadow": "0 4px 15px rgba(0,0,0,0.1)",
                    "padding": "1.5rem",
                    "marginBottom": "1.5rem",
                    "border": "none"
                })
            ]),

            # Deux graphiques supplémentaires en dessous
            dbc.Row([
                # 🍰 Sunburst (hiérarchie : pays → ville → domaine)
                dbc.Col([
                    html.Div([
                        html.H4("📊 Répartition des œuvres", 
                               style={"color": "#495057", "marginBottom": "1rem"}),
                        dcc.Graph(
                            id="sunburst-graph", 
                            style={"height": "400px", "borderRadius": "10px"}
                        )
                    ], style={
                        "background": "white",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 15px rgba(0,0,0,0.1)",
                        "padding": "1.5rem",
                        "marginBottom": "1.5rem",
                        "border": "none"
                    })
                ], width=6),

                # 📈 Barres horizontales : Top 10 des domaines
                dbc.Col([
                    html.Div([
                        html.H4("📈 Top domaines", 
                               style={"color": "#495057", "marginBottom": "1rem"}),
                        dcc.Graph(
                            id="domain-bar", 
                            style={"height": "400px", "borderRadius": "10px"}
                        )
                    ], style={
                        "background": "white",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 15px rgba(0,0,0,0.1)",
                        "padding": "1.5rem",
                        "marginBottom": "1.5rem",
                        "border": "none"
                    })
                ], width=6)
            ])
        ], width=9)
    ])
], fluid=True, style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})


# -------------------------------
# 🔁 CALLBACKS : LOGIQUE DYNAMIQUE
# -------------------------------

def register_callbacks(app):
    """
    Enregistre tous les callbacks interactifs de la page.
    Ces fonctions mettent à jour les graphiques en fonction des actions de l’utilisateur.
    """

    # Callback principal : mise à jour de la carte et du graphique en barres
    @app.callback(
        [Output("museum-map", "figure"),
         Output("domain-bar", "figure")],
        [Input("domain-filter", "value"),
         Input("country-filter", "value")]
    )
    def update_visualizations(selected_domains, selected_countries):
        """
        Met à jour :
        - La carte des musées (taille = nombre d’œuvres par ville)
        - Le graphique en barres horizontales (Top 10 domaines)
        """
        df_filtered = df_clean.copy()
        
        # Applique les filtres
        if selected_domains:
            df_filtered = df_filtered[df_filtered["domaine"].isin(selected_domains)]
        if selected_countries:
            df_filtered = df_filtered[df_filtered["pays"].isin(selected_countries)]

        # Agrège les données par ville pour la carte
        df_grouped = df_filtered.groupby(["ville", "pays", "latitude", "longitude"]).size().reset_index(name="count")

        # 🌍 Carte interactive
        fig_map = px.scatter_mapbox(
            df_grouped,
            lat="latitude",
            lon="longitude",
            hover_name="ville",
            hover_data={"pays": True, "count": True, "ville": False},
            size="count",
            size_max=20,
            zoom=2,
            height=500,
            color="count",
            color_continuous_scale=px.colors.sequential.Viridis,
            title=""
        )
        fig_map.update_layout(
            mapbox_style="carto-positron",  # Style clair
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(
                title="Nombre d'œuvres",
                title_font=dict(size=12, color="#495057"),
                tickfont=dict(size=10, color="#495057")
            )
        )

        # 📊 Barres horizontales : Top 10 domaines
        domain_counts = df_filtered["domaine"].value_counts().head(10)
        fig_bar = px.bar(
            x=domain_counts.values,
            y=domain_counts.index,
            orientation='h',
            color=domain_counts.values,
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_bar.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Nombre d'œuvres",
            yaxis_title="",
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig_map, fig_bar


    # Callback pour le graphique Sunburst (interactif au clic sur une ville)
    @app.callback(
        Output("sunburst-graph", "figure"),
        [Input("museum-map", "clickData"),          # Données du clic sur la carte
         Input("domain-filter", "value"),           # Filtre domaine
         Input("country-filter", "value")]          # Filtre pays
    )
    def update_sunburst(clickData, selected_domains, selected_countries):
        """
        Affiche une hiérarchie des œuvres :
        - Vue globale par défaut (pays → ville → domaine)
        - Vue détaillée par ville si un point est cliqué
        """
        df_filtered = df_clean.copy()
        
        # Applique les filtres
        if selected_domains:
            df_filtered = df_filtered[df_filtered["domaine"].isin(selected_domains)]
        if selected_countries:
            df_filtered = df_filtered[df_filtered["pays"].isin(selected_countries)]

        # Si aucun clic → vue globale
        if not clickData:
            try:
                fig_sb = px.sunburst(
                    df_filtered,
                    path=["pays", "ville", "domaine"],
                    title="Répartition par Pays → Ville → Domaine",
                    maxdepth=2
                )
            except ValueError:
                # Cas où les données ne permettent pas le sunburst
                fig_sb = px.sunburst(
                    names=["Cliquez sur une ville pour voir le détail"],
                    title="Vue d'ensemble des œuvres"
                )
        else:
            # Récupère la ville cliquée
            ville_clicked = clickData["points"][0]["hovertext"]
            df_city = df_filtered[df_filtered["ville"] == ville_clicked]

            if df_city.empty:
                fig_sb = px.sunburst(
                    names=["Aucune œuvre trouvée"],
                    title=f"Aucune donnée pour {ville_clicked}"
                )
            else:
                # Exclut les artistes génériques pour une meilleure lisibilité
                artistes_a_exclure = ["Artiste inconnu", "inconnu", "anonyme", "Anonyme", "Unknown", "unknown"]
                df_city_filtre = df_city[~df_city["artiste"].str.lower().isin([a.lower() for a in artistes_a_exclure])]

                # Essaye successivement des niveaux de détail décroissants
                if len(df_city_filtre) > 0:
                    try:
                        fig_sb = px.sunburst(
                            df_city_filtre,
                            path=["domaine", "artiste", "titre_ou_designation"],
                            title=f"Exploration des œuvres à {ville_clicked} (artistes connus)"
                        )
                    except ValueError:
                        try:
                            fig_sb = px.sunburst(
                                df_city_filtre,
                                path=["domaine", "artiste"],
                                title=f"Exploration des œuvres à {ville_clicked} (vue simplifiée)"
                            )
                        except ValueError:
                            fig_sb = px.sunburst(
                                df_city_filtre,
                                path=["domaine"],
                                title=f"Répartition par domaine à {ville_clicked}"
                            )
                else:
                    # Si tous les artistes sont "inconnus"
                    fig_sb = px.sunburst(
                        df_city,
                        path=["domaine", "titre_ou_designation"],
                        title=f"Répartition par domaine à {ville_clicked} (artistes non spécifiés)"
                    )

        # Style du sunburst
        fig_sb.update_layout(
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

        return fig_sb