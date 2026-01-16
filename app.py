import base64
import io
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------------
# App Initialization
# ---------------------------------
app = dash.Dash(__name__)
server = app.server

# ---------------------------------
# Layout
# ---------------------------------
app.layout = html.Div(
    style={
        "minHeight": "100vh",
        "padding": "20px",
        "background": "linear-gradient(135deg, #0f2027, #203a43, #2c5364)",
        "color": "white",
        "fontFamily": "Arial",
    },
    children=[

        html.H1(
            "ETL KPI REPORTING DASHBOARD",
            style={"textAlign": "center"}
        ),

        # ---------- Upload ----------
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag & Drop or ", html.B("Select CSV / Excel File")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "border": "2px dashed #666",
                "borderRadius": "5px",
                "textAlign": "center",
                "backgroundColor": "#ffffff",
                "color": "#000000",
            },
            multiple=False,
        ),

        dcc.Store(id="stored-data"),

        html.Br(),

        # ---------- Filters ----------
        html.Div(
            [
                dcc.Dropdown(
                    id="business-unit-filter",
                    placeholder="Business Unit",
                    multi=True,
                    style={"color": "#000000"}
                ),
                dcc.Dropdown(
                    id="kpi-filter",
                    placeholder="KPI Name",
                    multi=True,
                    style={"color": "#000000"}
                ),
                dcc.Dropdown(
                    id="week-filter",
                    placeholder="Week",
                    multi=True,
                    style={"color": "#000000"}
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr 1fr",
                "gap": "15px",
            },
        ),

        html.Hr(),

        # ---------- KPI Cards ----------
        html.Div(
            [
                html.Div(id="total-kpi-card"),
                html.Div(id="avg-kpi-card"),
                html.Div(id="total-events-card"),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-around",
                "fontWeight": "bold",
            },
        ),

        html.Hr(),

        # ---------- Graphs ----------
        html.Div(
            [
                dcc.Graph(id="kpi-trend"),
                dcc.Graph(id="kpi-comparison"),
                dcc.Graph(id="event-distribution"),
                dcc.Graph(id="event-volume"),
                dcc.Graph(id="kpi-event-scatter"),
                dcc.Graph(id="kpi-matrix"),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "20px",
            },
        ),

        html.Hr(),

        # ---------- Table ----------
        html.H3("Analytical Data Table"),
        dash_table.DataTable(
            id="data-table",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "color": "#000000",
                "backgroundColor": "#ffffff",
            },
        ),

        html.Br(),

        html.Button("Download PDF Report", id="pdf-btn"),
        dcc.Download(id="pdf-download"),
    ],
)

# ---------------------------------
# Utilities
# ---------------------------------
def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    if filename.endswith(".csv"):
        return pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    else:
        return pd.read_excel(io.BytesIO(decoded))

# ---------------------------------
# Store Uploaded Data
# ---------------------------------
@app.callback(
    Output("stored-data", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    prevent_initial_call=True,
)
def store_data(contents, filename):
    df = parse_contents(contents, filename)
    return df.to_dict("records")

# ---------------------------------
# Populate ALL Slicers (FIXED)
# ---------------------------------
@app.callback(
    Output("business-unit-filter", "options"),
    Output("kpi-filter", "options"),
    Output("week-filter", "options"),
    Input("stored-data", "data"),
)
def populate_filters(data):
    if not data:
        return [], [], []

    df = pd.DataFrame(data)

    return (
        [{"label": i, "value": i} for i in sorted(df["business_unit"].dropna().unique())],
        [{"label": i, "value": i} for i in sorted(df["kpi_name"].dropna().unique())],
        [{"label": i, "value": i} for i in sorted(df["week"].dropna().unique())],
    )

# ---------------------------------
# Dashboard + Table
# ---------------------------------
@app.callback(
    Output("kpi-trend", "figure"),
    Output("kpi-comparison", "figure"),
    Output("event-distribution", "figure"),
    Output("event-volume", "figure"),
    Output("kpi-event-scatter", "figure"),
    Output("kpi-matrix", "figure"),
    Output("total-kpi-card", "children"),
    Output("avg-kpi-card", "children"),
    Output("total-events-card", "children"),
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Input("stored-data", "data"),
    Input("business-unit-filter", "value"),
    Input("kpi-filter", "value"),
    Input("week-filter", "value"),
)
def update_dashboard(data, bu, kpi, week):
    if not data:
        return [{}] * 6 + ["", "", "", [], []]

    df = pd.DataFrame(data)

    if bu:
        df = df[df["business_unit"].isin(bu)]
    if kpi:
        df = df[df["kpi_name"].isin(kpi)]
    if week:
        df = df[df["week"].isin(week)]

    kpi_trend = px.line(
        df.groupby(["week", "business_unit"], as_index=False)["kpi_value"].sum(),
        x="week", y="kpi_value", color="business_unit",
        title="KPI Trend Over Time"
    )

    kpi_comp = px.bar(
        df.groupby(["business_unit", "kpi_name"], as_index=False)["kpi_value"].sum(),
        x="business_unit", y="kpi_value", color="kpi_name",
        title="KPI Comparison by Business Unit"
    )

    event_dist = px.bar(
        df.groupby(["event_type"], as_index=False)["event_count"].sum(),
        x="event_count", y="event_type", orientation="h",
        title="Event Distribution"
    )

    event_vol = px.area(
        df.groupby(["week", "event_type"], as_index=False)["event_count"].sum(),
        x="week", y="event_count", color="event_type",
        title="Event Volume Over Time"
    )

    scatter = px.scatter(
        df,
        x="event_count", y="kpi_value", color="event_type",
        title="KPI vs Event Correlation"
    )

    matrix = px.imshow(
        df.pivot_table(
            index="business_unit",
            columns="kpi_name",
            values="kpi_value",
            aggfunc="mean"
        ),
        text_auto=True,
        title="KPI Performance Matrix"
    )

    return (
        kpi_trend,
        kpi_comp,
        event_dist,
        event_vol,
        scatter,
        matrix,
        f"Total KPI Value: {df['kpi_value'].sum():,.2f}",
        f"Average KPI Value: {df['kpi_value'].mean():,.2f}",
        f"Total Events: {df['event_count'].sum():,}",
        df.to_dict("records"),
        [{"name": c, "id": c} for c in df.columns],
    )

# ---------------------------------
# PDF Report
# ---------------------------------
@app.callback(
    Output("pdf-download", "data"),
    Input("pdf-btn", "n_clicks"),
    State("stored-data", "data"),
    prevent_initial_call=True,
)
def generate_pdf(_, data):
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    doc.build([
        Paragraph("ETL KPI & Event Analytics Report", styles["Title"]),
        Paragraph(f"Total KPI Value: {df['kpi_value'].sum():,.2f}", styles["Normal"]),
        Paragraph(f"Average KPI Value: {df['kpi_value'].mean():,.2f}", styles["Normal"]),
        Paragraph(f"Total Events: {df['event_count'].sum():,}", styles["Normal"]),
    ])

    buffer.seek(0)
    return dcc.send_bytes(buffer.read(), "ETL_KPI_Report.pdf")

# ---------------------------------
# Run
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)
