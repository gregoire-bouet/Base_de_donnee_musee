import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import webbrowser
import threading
import time

# Création de l'application principale
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.COSMO], 
                suppress_callback_exceptions=True)
app.title = "ArtVision Explorer - Plateforme Principale"

# Layout principal avec navigation
# Layout principal avec navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False, pathname="/accueil"),  # ← AJOUT pathname="/accueil"
    
    # Barre de navigation
    dbc.Navbar(
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col(dbc.NavbarBrand("🎨 ArtVision Explorer", className="ms-2")),
                ], align="center", className="g-0"),
                href="/accueil",  # Déjà présent
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("🏠 Accueil", href="/accueil", active="exact")),
                    dbc.NavItem(dbc.NavLink("📊 Dashboard Œuvres", href="/dashboard-oeuvres", active="exact")),
                    dbc.NavItem(dbc.NavLink("🗺️ Carte des Musées", href="/carte-musees", active="exact")),
                ], className="ms-auto", navbar=True),
                id="navbar-collapse",
                navbar=True,
            ),
        ]),
        color="primary",
        dark=True,
        className="mb-4"
    ),
    
    # Contenu des pages
    html.Div(id='page-content')
])


# Import et enregistrement des callbacks
try:
    from pages.dashboard_oeuvres import register_callbacks as register_dashboard_callbacks
    from pages.carte_musees import register_callbacks as register_carte_callbacks
    
    # Enregistrer tous les callbacks au démarrage
    register_dashboard_callbacks(app)
    register_carte_callbacks(app)
except ImportError as e:
    print(f"Warning: Could not import callback modules: {e}")

# Callback pour la navigation
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/dashboard-oeuvres' or pathname.startswith('/dashboard-oeuvres/'):
        from pages.dashboard_oeuvres import layout
        return layout
    elif pathname == '/carte-musees':
        from pages.carte_musees import layout
        return layout
    elif pathname == '/accueil':
        from pages.accueil import layout
        return layout
    else:
        # Redirection automatique vers /accueil pour la racine et routes inconnues
        return dcc.Location(pathname="/accueil", id="redirect")
    
if __name__ == '__main__':    
    
    # Fonction pour ouvrir le navigateur
    def open_browser():
        time.sleep(2)  # Attendre que le serveur démarre
        print("🌐 Ouverture du navigateur...")
        webbrowser.open_new("http://localhost:8050/accueil")
    
    
    # Démarrer l'ouverture du navigateur dans un thread séparé
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Lancer l'application
    app.run(debug=True, use_reloader=False)