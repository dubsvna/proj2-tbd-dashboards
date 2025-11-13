# app/dashboard.py
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
from sqlalchemy import create_engine, text

# Configura a conexão com o banco. O host é o nome do serviço no compose: 'db'
engine = create_engine(f"postgresql+psycopg2://arthur:postgres@localhost:5432/proj2-tbd-dashboard")

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Vendas", style={'textAlign': 'center'}),
    dcc.Graph(id='grafico-vendas')
])


@callback(
    Output('grafico-vendas', 'figure'),
    Input('grafico-vendas', 'id')
)
def update_graph(_):
    # Consulta os dados do PostgreSQL
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM vendas;"), conn)
        print("Conexão realizada com sucesso!")

    # Cria um gráfico de barras simples
    fig = {
        'data': [
            {
                'x': df['produto'],
                'y': df['quantidade'],
                'type': 'bar',
            }
        ],
        'layout': {
            'title': 'Vendas por Produto'
        }
    }
    return fig


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
