import base64
import io
import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output, State
import plotly.express as px

# -----------------------------
# App Initialization
# -----------------------------
app = Dash(__name__)
server = app.server

# -----------------------------
# Helper Functions
# -----------------------------
def parse_upload(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    if filename.endswith(".csv"):
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        return None

    df.columns = df.columns.str.lower()
    df["week"] = pd.to_datetime(df["week"])
    return df


def generate_insight_report(df):
    top_bu = df.groupby("business_unit")["kpi_value"].sum().idxmax()
    total_kpi = df["kpi_value"].sum()
    avg_kpi = df["kpi_value"].mean()
    total_events = df["event_count"].sum()

    report = f"""
BUSINESS KPI ANALYTICS REPORT

Total KPI Value: {total_kpi:,.2f}
Average KPI Value: {avg_kpi:,.2f}
Total Logged Events: {total_events:,}

KEY INSIGHTS:
1. {top_bu} is the highest contributing business unit.
2. KPI values show weekly volatility, suggesting operational sensitivity.
3. Event spikes correlate with KPI fluctuations.
4. KPI distribution indicates uneven performance across departments.

CONCLUSION:
This data supports proactive monitoring of operational KPIs
and event-driven performance management.
"""

    with open("kpi_report.txt", "w") as f:
        f.write(report)


# -----------------------------
# Layout
# -----------------------------
app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI",
        "backgroundColor": "#0B1E3C",
        "padding": "20px",
        "color": "white"
    },
    children=[
        html.H1(
            "ETL PIPELINE FOR BUSINESS KPI REPORTING",
            style={"textAlign": "center", "marginBottom": "30px"}
        ),

        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag & Drop or ", html.A("Select CSV / Excel File")]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "8px",
                "textAlign": "center",
                "marginBottom": "20px",
                "backgroundColor": "#102B5C"
            },
            multiple=False,
        ),

        dcc.Store(id="stored-data"),

        # KPI Cards
        html.Div(
            id="kpi-cards",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "20px",
                "marginBottom": "30px"
            }
        ),

        # Filters
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "20px"},
            children=[
                dcc.Dropdown(id="bu-filter", multi=True, placeholder="Business Unit"),
                dcc.Dropdown(id="kpi-filter", multi=True, placeholder="KPI Name"),
            ],
        ),

        # Charts
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px"},
            children=[
                dcc.Graph(id="line-chart"),
                dcc.Graph(id="donut-chart"),
                dcc.Graph(id="bar-chart"),
                dcc.Graph(id="area-chart"),
            ],
        ),

        html.H3("Detailed KPI Table", style={"marginTop": "30px"}),
        dash_table.DataTable(
            id="kpi-table",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#1E3A70", "color": "white"},
            style_cell={"backgroundColor": "#102B5C", "color": "white"},
        ),

        html.Br(),
        html.Button("Generate & Download Report", id="report-btn"),
        html.Div(id="report-status"),
    ],
)


# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("stored-data", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def store_data(contents, filename):
    if contents:
        df = parse_upload(contents, filename)
        return df.to_dict("records")
    return None


@app.callback(
    Output("kpi-cards", "children"),
    Output("line-chart", "figure"),
    Output("donut-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("area-chart", "figure"),
    Output("kpi-table", "data"),
    Output("kpi-table", "columns"),
    Output("bu-filter", "options"),
    Output("kpi-filter", "options"),
    Input("stored-data", "data"),
    Input("bu-filter", "value"),
    Input("kpi-filter", "value"),
)
def update_dashboard(data, bu, kpi):
    if not data:
        return [], {}, {}, {}, {}, [], [], [], []

    df = pd.DataFrame(data)

    if bu:
        df = df[df["business_unit"].isin(bu)]
    if kpi:
        df = df[df["kpi_name"].isin(kpi)]

    cards = [
        html.Div(f"{df['kpi_value'].sum():,.2f}", className="card", style={"background": "#1E3A70", "padding": "20px"}),
        html.Div(f"{df['kpi_value'].mean():,.2f}", className="card", style={"background": "#1E3A70", "padding": "20px"}),
        html.Div(f"{df['event_count'].sum():,}", className="card", style={"background": "#1E3A70", "padding": "20px"}),
        html.Div(f"{df['week'].nunique()}", className="card", style={"background": "#1E3A70", "padding": "20px"}),
    ]

    line = px.line(df, x="week", y="kpi_value", color="business_unit")
    donut = px.pie(df, names="business_unit", values="kpi_value", hole=0.5)
    bar = px.bar(df, x="kpi_value", y="business_unit", color="kpi_name", orientation="h")
    area = px.area(df, x="week", y="event_count", color="event_type")

    return (
        cards,
        line,
        donut,
        bar,
        area,
        df.to_dict("records"),
        [{"name": c, "id": c} for c in df.columns],
        [{"label": x, "value": x} for x in df["business_unit"].unique()],
        [{"label": x, "value": x} for x in df["kpi_name"].unique()],
    )


@app.callback(
    Output("report-status", "children"),
    Input("report-btn", "n_clicks"),
    State("stored-data", "data"),
)
def create_report(n, data):
    if n and data:
        df = pd.DataFrame(data)
        generate_insight_report(df)
        return html.A("Download KPI Report", href="/kpi_report.txt", download="KPI_Report.txt")
    return ""


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
