# Python Application to Check for Anomalies in Real Time Data Stream
# To run the application
# > pip install -r requirements.txt
# > python index.py
# Open http://127.0.0.1:8050/ to get live visualisation of data

from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from collections import deque

# Queues to store a maximum of 100 values for the data
# Older data is discarded to calculate anomalies
x = deque(maxlen=100)
y = deque(maxlen=100)
time = 0
app = Dash(__name__)

# Dash app to render the plot on a web page
app.layout = html.Div([
    html.H1(
        "Anomaly Detection in a Data Stream",
        style={
            "textAlign": "center",
            "color": "#000000",
            "margin-bottom": "20px",
            "font-family": "'Roboto Mono', monospace",
        },
    ),
    dcc.Graph(
        id="graph-content",
        animate=True,
        config={
            'displayModeBar': False
        }
    ),
    dcc.Interval(id="graph-interval", interval=500, n_intervals=0),
])

def add_data_point():
    global time
    time += 1
    x.append(time)

    pattern = np.cos(time*0.1)
    seasonal = np.sin(time*0.5)
    noise = np.random.normal(0, 0.1)

    # Data Point consisting of pattern data, seasonal data and random noise
    data_point = pattern + seasonal + noise

    # Adding random anomaly with a probability of 7%
    if np.random.rand() < 0.07:
        data_point += np.random.normal(0, 10)

    y.append(data_point)

# Callback function for rendering graph every 20 milliseconds
@app.callback(
    Output("graph-content", "figure"), [Input("graph-interval", "n_intervals")]
)
def update_graph(value):
    # Adding a data point on every call to callback function
    add_data_point()

    # Finding the First and Third Quartile 
    first_quartile = np.percentile(y, 25, method="midpoint")
    third_quartile = np.percentile(y, 75, method="midpoint")

    # Finding the Inter Quartile
    inter_quartile_range = third_quartile - first_quartile

    # Limits defining the anomalies
    lower_limit = first_quartile - 1.5*inter_quartile_range
    upper_limit = third_quartile + 1.5*inter_quartile_range

    # Re-evaluating the data to check for anomalies
    data = pd.DataFrame({"X": x, "Value": y})
    data["Anomaly"] = data["Value"].apply(
        lambda x: True if (x > upper_limit or x < lower_limit) else False
    )

    color_map = {True: "#ff0000", False: "#0000ff"}

    # Scatter Plot to be rendered on Web Page
    graph = go.Scatter(
        x=data["X"],
        y=data["Value"],
        mode="markers",
        marker=dict(color=data["Anomaly"].map(color_map), symbol="circle"),
        name="Value",
    )
    layout = go.Layout(
        xaxis=dict(
            range=[max(max(x)-100, 0), max(max(x)-100, 0)+100],
            title="Time",
            showline=True,
            showgrid=False,
        ),
        yaxis=dict(
            range=[min(y)-1, max(y)+1],
            title="Value",
            showgrid=False,
            zeroline=False,
        ),
        paper_bgcolor="#fff",
        plot_bgcolor="#fff",
    )

    return {"data": [graph], "layout": layout}

if __name__ == '__main__':
    app.run_server(debug=True)
