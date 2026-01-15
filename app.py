import dash
from dash import html, dcc
import pandas as pd
from flask import Flask


server = Flask(__name__)
app = dash.Dash(__name__, server=server)

df = pd.read_csv("output/weekly_kpi_report.csv")

app.layout = html.Div([
    html.H1("ETL KPI Business Dashboard"),

    dcc.Dropdown(
        id="business_unit",
        options=[{"label": b, "value": b} for b in df["business_unit"].unique()],
        value=df["business_unit"].unique()[0]
    ),

    dcc.Graph(
        figure={
            "data": [{
                "x": df["week"],
                "y": df["kpi_value"],
                "type": "line"
            }],
            "layout": {"title": "Weekly KPI Trend"}
        }
    )
])

if __name__ == "__main__":
    app.run(debug=True)
