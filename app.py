# from flask import Flask
import dash
import dash_html_components as html
import dash_core_components as dcc
from plotly.subplots import make_subplots
import pandas as pd

df = pd.read_csv("marketdata.csv", index_col="Date")
# remove empty data points, for visualisation purposes
df.dropna(inplace=True)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_scatter(secondary_y=False, x=df.index, y=df["FTSEAW"],
                marker_color="MediumSlateBlue", name="FTSE All-World")
fig.add_scatter(secondary_y=True,  x=df.index, y=df["EUSA30"],
                marker_color="DarkOrange", name="30Y interest rate")
fig.update_layout(title_text="Equities vs interest rates")

dash_app = dash.Dash()
app = dash_app.server


dash_app.layout = html.Div(
    [
        dcc.Markdown('''
        # A simple financial data dashboard

        Just try out this *simple* dashboard! For more information,
        '''),
        dcc.Graph(figure=fig)
    ]
)

if __name__ == '__main__':
    dash_app.run_server(debug=True)
