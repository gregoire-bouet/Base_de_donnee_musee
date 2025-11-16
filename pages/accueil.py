# Importation des bibliothèques Dash et Bootstrap
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# -------------------------------
# 🏠 LAYOUT DE LA PAGE D'ACCUEIL
# -------------------------------

layout = dbc.Container([
    # Ligne principale contenant tout le contenu de la page
    dbc.Row([
        dbc.Col([
            # Titre principal de la page
            html.H1("🎨 Bienvenue sur ArtVision Explorer", className="text-center my-5"),
            
            # Description courte
            html.P("Explorez le monde de l'art à travers nos différentes plateformes d'analyse", 
                  className="text-center lead mb-5"),
            
            # Ligne contenant les deux cartes de navigation
            dbc.Row([
                # Colonne pour le Dashboard
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("📊 Dashboard Œuvres", className="card-title"),
                            html.P("Analysez les données avec des graphiques et tableaux détaillés"),
                            # Lien vers la page du dashboard
                            dcc.Link(
                                dbc.Button("Explorer le dashboard", color="primary", size="lg"),
                                href="/dashboard-oeuvres",
                                style={"textDecoration": "none"}  # Supprime le soulignement du lien
                            )
                        ])
                    ], className="h-100 text-center")  # h-100 pour que les cartes aient la même hauteur
                ], width=6, className="mb-4"),  # mb-4 pour un espacement en bas
                
                # Colonne pour la Carte des Musées
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("🗺️ Carte des Musées", className="card-title"),
                            html.P("Visualisez la répartition géographique des œuvres d'art"),
                            # Lien vers la page de la carte
                            dcc.Link(
                                dbc.Button("Explorer la carte", color="primary", size="lg"),
                                href="/carte-musees",
                                style={"textDecoration": "none"}
                            )
                        ])
                    ], className="h-100 text-center")
                ], width=6, className="mb-4"),
            ], className="g-4"),  # g-4 pour un espacement uniforme entre les colonnes
            
            # Ligne horizontale décorative
            html.Hr(className="my-5"),
            
            # Section "À propos"
            dbc.Row([
                dbc.Col([
                    html.H4("À propos de ArtVision Explorer"),
                    html.P("Notre plateforme vous permet d'explorer des milliers d'œuvres d'art à travers différentes perspectives interactives. "
                          "Utilisez le dashboard pour analyser les tendances par domaine et période, "
                          "ou explorez la carte pour découvrir la répartition géographique des collections.")
                ], width=8, className="mx-auto text-center")  # mx-auto centre la colonne horizontalement
            ])
        ])
    ])
], fluid=True)  # fluid=True pour que le conteneur prenne toute la largeur de l'écran