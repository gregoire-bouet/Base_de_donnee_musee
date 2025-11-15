import plotly.express as px
import pandas as pd
from pathlib import Path
import unicodedata
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ----------------------------
# Fonctions utilitaires
# ----------------------------
def _normalize_col(name: str) -> str:
    s = str(name)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip()
    for ch in (" ", "/", ">", "-", ".", ",", ";", ":", "(", ")", "'", '"'):
        s = s.replace(ch, "_")
    parts = [p for p in s.split("_") if p]
    return "_".join(parts)

def load_data():
    csv_path = Path(r"C:\Users\noahb\Documents\Base_de_donnee_musee\data\cleaned\cleaneddata.csv")
    try:
        df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    df.columns = [_normalize_col(c) for c in df.columns]
    return df

# ----------------------------
# Chargement des données
# ----------------------------
df = load_data()
if df is None:
    raise SystemExit("Impossible de charger les données.")

if "domaine" not in df.columns:
    raise SystemExit("Colonne 'domaine' non trouvée après normalisation.")

domaines = sorted(df["domaine"].dropna().unique())

# ----------------------------
# Application Dash
# ----------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Œuvres d'Art"

# ----------------------------
# Barre latérale
# ----------------------------
sidebar = dbc.Card(
    dbc.CardBody([
        html.H5("ℹ️ Informations", className="card-title"),
        html.Div([
            html.P(f"Nombre total d'œuvres: {len(df)}"),
            html.P(f"Nombre de domaines: {len(domaines)}")
        ]),
        html.Hr(),
        html.H6("📅 Filtre temporel"),
        dcc.RangeSlider(
            id='year-range-slider',
            step=1,
            min=int(df["date_de_l_oeuvre_ou_de_l_artiste"].min()),
            max=int(df["date_de_l_oeuvre_ou_de_l_artiste"].max()),
            value=[int(df["date_de_l_oeuvre_ou_de_l_artiste"].min()), int(df["date_de_l_oeuvre_ou_de_l_artiste"].max())],
            marks={},  # sera mis à jour dynamiquement
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Hr(),
        html.H6("📊 Analyses prédéfinies"),
        dcc.Dropdown(
            id='predefined-analysis',
            options=[{'label': 'Aucune', 'value': 'Aucune'}],
            value='Aucune'
        ),
        html.Hr(),
        html.H6("🔬 Exploration libre"),
        dcc.Dropdown(
            id='x-var',
            options=[{'label': c, 'value': c} for c in df.columns],
            placeholder='Variable X'
        ),
        dcc.Dropdown(
            id='y-var',
            options=[{'label': c, 'value': c} for c in df.columns],
            placeholder='Variable Y'
        ),
        html.Br(),
        dbc.Button("← Retour à l'accueil", href="/", color='secondary', className='mt-2')
    ]),
    className="h-100",
    style={"backgroundColor": "#FFFFFF", "color": "#000000"}
)

# ----------------------------
# Layout principal
# ----------------------------
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col([
            html.H1("Dashboard Œuvres d'Art", style={"color": "#000000", "marginBottom": "20px"}),
            html.Div([
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
                dcc.Graph(id="main-graph")  # <- Graph unique
            ], id="page-content")
        ], width=9)
    ], style={"minHeight": "100vh", "backgroundColor": "#FFFFFF", "paddingTop": "20px"})
], fluid=True)

# ----------------------------
# Fonctions utilitaires pour graph
# ----------------------------
def get_main_figure(pathname, year_range):
    df_filtered = df[(df["date_de_l_oeuvre_ou_de_l_artiste"] >= year_range[0]) &
                     (df["date_de_l_oeuvre_ou_de_l_artiste"] <= year_range[1])]
    
    if pathname == "/":
        counts_filtered = df_filtered["domaine"].value_counts().reset_index()
        counts_filtered.columns = ["domaine", "nombre_d_oeuvres"]
        fig = px.bar(
            counts_filtered,
            x="domaine",
            y="nombre_d_oeuvres",
            color="domaine",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Nombre d’œuvres par domaine"
        )
    elif pathname.startswith("/domaine/"):
        domaine = pathname.split("/domaine/")[1]
        df_domaine = df_filtered[df_filtered["domaine"] == domaine].copy()
        df_domaine = df_domaine.dropna(subset=["date_de_l_oeuvre_ou_de_l_artiste"])
        if df_domaine.empty:
            return px.scatter(title=f"Aucune donnée pour {domaine} dans cette plage")
        
        min_year = int(df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].min() // 100 * 100)
        max_year = int(df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].max() + 100)
        bins = list(range(min_year, max_year, 100))
        labels = [f"{b}-{b+100}" for b in bins[:-1]]
        df_domaine["decennie"] = pd.cut(df_domaine["date_de_l_oeuvre_ou_de_l_artiste"], bins=bins, labels=labels, right=False)
        counts_by_decade = df_domaine["decennie"].value_counts().sort_index().reset_index()
        counts_by_decade.columns = ["decennie", "nombre_d_oeuvres"]
        fig = px.bar(
            counts_by_decade,
            x="decennie",
            y="nombre_d_oeuvres",
            color="decennie",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"Nombre d’œuvres par siècle pour le domaine : {domaine}"
        )
    else:
        fig = px.scatter(title="Page non trouvée")
    
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
# Callbacks
# ----------------------------
# Slider dynamique
@app.callback(
    Output("year-range-slider", "marks"),
    Output("year-range-slider", "min"),
    Output("year-range-slider", "max"),
    Output("year-range-slider", "value"),
    Input("url", "pathname")
)
def update_slider(pathname):
    if pathname.startswith("/domaine/"):
        domaine = pathname.split("/domaine/")[1]
        df_domaine = df[df["domaine"] == domaine].dropna(subset=["date_de_l_oeuvre_ou_de_l_artiste"])
        min_year = int(df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].min())
        max_year = int(df_domaine["date_de_l_oeuvre_ou_de_l_artiste"].max())
    else:
        min_year = int(df["date_de_l_oeuvre_ou_de_l_artiste"].min())
        max_year = int(df["date_de_l_oeuvre_ou_de_l_artiste"].max())
    step = max(1, (max_year - min_year))
    marks = {year: str(year) for year in range(min_year, max_year + 1, step)}
    return marks, min_year, max_year, [min_year, max_year]

# Filtrer options Y selon X
@app.callback(
    Output("y-var", "options"),
    Input("x-var", "value")
)
def filter_y_options(x_col):
    if not x_col:
        return [{'label': c, 'value': c} for c in df.columns]
    if pd.api.types.is_numeric_dtype(df[x_col]):
        return [{'label': c, 'value': c} for c in df.select_dtypes(include='number').columns]
    else:
        return [{'label': c, 'value': c} for c in df.select_dtypes(include='number').columns]

# Boutons domaines
@app.callback(
    Output('url', 'pathname'),
    [Input(f'btn-{i}', 'n_clicks') for i in range(len(domaines))]
)
def redirect(*clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "/"
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    index = int(button_id.split('-')[1])
    return f"/domaine/{domaines[index]}"

# Graph principal (fusion principale + exploration libre)
@app.callback(
    Output("main-graph", "figure"),
    Input("x-var", "value"),
    Input("y-var", "value"),
    Input("url", "pathname"),
    Input("year-range-slider", "value")
)
def update_main_graph(x_col, y_col, pathname, year_range):
    # Exploration libre prioritaire
    if x_col and y_col:
        try:
            fig = px.scatter(df, x=x_col, y=y_col)
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
            return px.scatter(title="Impossible de créer le graphique")
    # Graph principal
    return get_main_figure(pathname, year_range)

# ----------------------------
# Lancement
# ----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=True)
