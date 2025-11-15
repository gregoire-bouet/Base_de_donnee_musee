import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from pathlib import Path
import unicodedata

# -------------------------------
# 🔧 Fonctions utilitaires
# -------------------------------
def _normalize_col(name: str) -> str:
    s = str(name)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().strip()
    for ch in (" ", "/", ">", "-", ".", ",", ";", ":", "(", ")", "'", '"'):
        s = s.replace(ch, "_")
    parts = [p for p in s.split("_") if p]
    return "_".join(parts)

def parse_location(loc):
    if pd.isna(loc):
        return pd.Series({"pays": None, "ville": None, "musee": None})
    parts = [p.strip() for p in loc.split(",")]
    if len(parts) >= 2:
        musee, ville, *rest = parts
        pays = rest[-1] if rest else None
    elif len(parts) == 1:
        musee = parts[0]
        ville = None
        pays = None
    else:
        musee = ville = pays = None
    return pd.Series({"pays": pays, "ville": ville, "musee": musee})

# -------------------------------
# 🔹 Chargement des données (CSV déjà géocodé)
# -------------------------------
def load_data():
    csv_path = Path(r"C:\Users\noahb\Documents\Base_de_donnee_musee\data\cleaned\cleaneddata_geocoded_villes.csv")
    df = pd.read_csv(csv_path, sep=";", encoding="utf-8")
    df.columns = [_normalize_col(c) for c in df.columns]
    return df

df = load_data()
df[["pays", "ville", "musee"]] = df["lieu_de_conservation"].apply(parse_location)

# -------------------------------
# 🌍 Dash Layout
# -------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Carte des musées"

app.layout = dbc.Container([
    html.H1("📍 Carte des musées par ville", className="text-center mt-3"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Filtrer par domaine :"),
            dcc.Dropdown(
                id="domain-filter",
                options=[{"label": d, "value": d} for d in sorted(df["domaine"].dropna().unique())],
                multi=True,
                placeholder="Sélectionnez un ou plusieurs domaines"
            ),
        ], width=3),
        dbc.Col([
            dcc.Graph(id="museum-map", style={"height": "500px"}, config={"displayModeBar": False}),
            html.Hr(),
            dcc.Graph(id="sunburst-graph", style={"height": "400px"})
        ], width=9)
    ])
], fluid=True)

# -------------------------------
# 🔁 Callbacks
# -------------------------------
@app.callback(
    Output("museum-map", "figure"),
    Input("domain-filter", "value")
)
def update_map(selected_domains):
    df_filtered = df.copy()
    if selected_domains:
        df_filtered = df_filtered[df_filtered["domaine"].isin(selected_domains)]
    
    # On regroupe par ville pour éviter doublons
    df_grouped = df_filtered.groupby(["ville", "pays", "latitude", "longitude"]).size().reset_index(name="count")

    fig = px.scatter_map(
    df_grouped,
    lat="latitude",
    lon="longitude",
    hover_name="ville",
    hover_data=["pays", "count"],
    size_max=15,        # taille max des points
    zoom=2,
    height=500
)
    fig.update_layout(mapbox_style="open-street-map", margin=dict(l=0, r=0, t=10, b=0))
    return fig

@app.callback(
    Output("sunburst-graph", "figure"),
    Input("museum-map", "clickData")
)
def update_sunburst(clickData):
    if not clickData:
        return px.sunburst(names=["Cliquez sur une ville pour voir le Sunburst"], title="")

    ville_clicked = clickData["points"][0]["hovertext"]
    df_city = df[df["ville"] == ville_clicked].copy()

    if df_city.empty:
        return px.sunburst(names=["Aucune donnée"], title="")

    df_city["artiste"] = df_city["artiste"].fillna("Inconnu")
    df_city["domaine"] = df_city["domaine"].fillna("Inconnu")
    df_city["titre_ou_designation"] = df_city["titre_ou_designation"].fillna("Inconnu")

    fig_sb = px.sunburst(
        df_city,
        path=["domaine", "artiste", "titre_ou_designation"],
        title=f"Sunburst pour {ville_clicked}"
    )
    fig_sb.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig_sb

# -------------------------------
# 🔹 Lancement du serveur
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
