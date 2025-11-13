# dashboard_vendas_estatico.py
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'sistema_vendas')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Criar conexão com o banco
connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(connection_string)


def executar_query(query):
    """Executa uma query e retorna um DataFrame"""
    try:
        with engine.connect() as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        print(f"Erro na consulta: {e}")
        return pd.DataFrame()


# Queries para o dashboard
QUERY_VENDAS_CLIENTES = """
SELECT 
    v.id as venda_id,
    v.data_venda,
    c.nome as cliente,
    v.valor_total
FROM vendas v
JOIN clientes c ON v.cliente_id = c.id
ORDER BY v.data_venda DESC;
"""

QUERY_PRODUTOS_MAIS_VENDIDOS = """
SELECT 
    p.nome as produto,
    c.nome as categoria,
    SUM(iv.quantidade) as total_vendido,
    SUM(iv.subtotal) as total_faturado
FROM produtos p
JOIN categorias c ON p.categoria_id = c.id
JOIN itens_venda iv ON p.id = iv.produto_id
GROUP BY p.id, p.nome, c.nome
HAVING SUM(iv.subtotal) > 500
ORDER BY total_faturado DESC;
"""

QUERY_CLIENTES_ACIMA_MEDIA = """
SELECT 
    c.nome as cliente,
    c.cidade,
    v.data_venda,
    v.valor_total
FROM clientes c
JOIN vendas v ON c.id = v.cliente_id
WHERE v.valor_total > (
    SELECT AVG(valor_total) 
    FROM vendas
    WHERE data_venda >= CURRENT_DATE - INTERVAL '30 days'
)
ORDER BY v.valor_total DESC;
"""

QUERY_METRICAS_GERAIS = """
SELECT 
    COUNT(DISTINCT v.id) as total_vendas,
    SUM(v.valor_total) as faturamento_total,
    AVG(v.valor_total) as ticket_medio,
    COUNT(DISTINCT c.id) as total_clientes
FROM vendas v
JOIN clientes c ON v.cliente_id = c.id;
"""

QUERY_VENDAS_POR_CATEGORIA = """
SELECT 
    cat.nome as categoria,
    COUNT(iv.id) as total_itens,
    SUM(iv.subtotal) as faturamento_categoria
FROM categorias cat
JOIN produtos p ON cat.id = p.categoria_id
JOIN itens_venda iv ON p.id = iv.produto_id
GROUP BY cat.id, cat.nome
ORDER BY faturamento_categoria DESC;
"""

QUERY_TOP_CLIENTES = """
SELECT 
    c.nome as cliente,
    c.cidade,
    COUNT(v.id) as total_compras,
    SUM(v.valor_total) as total_gasto
FROM clientes c
JOIN vendas v ON c.id = v.cliente_id
GROUP BY c.id, c.nome, c.cidade
ORDER BY total_gasto DESC
LIMIT 10;
"""

# Executar queries e carregar dados
print("📊 Carregando dados do banco...")

vendas_clientes = executar_query(QUERY_VENDAS_CLIENTES)
produtos_mais_vendidos = executar_query(QUERY_PRODUTOS_MAIS_VENDIDOS)
clientes_acima_media = executar_query(QUERY_CLIENTES_ACIMA_MEDIA)
metricas_gerais = executar_query(QUERY_METRICAS_GERAIS)
vendas_por_categoria = executar_query(QUERY_VENDAS_POR_CATEGORIA)
top_clientes = executar_query(QUERY_TOP_CLIENTES)

print("✅ Dados carregados com sucesso!")

# Processar métricas gerais
if not metricas_gerais.empty:
    faturamento_total = f"R$ {metricas_gerais['faturamento_total'].iloc[0]:,.2f}"
    total_vendas = str(metricas_gerais['total_vendas'].iloc[0])
    total_clientes = str(metricas_gerais['total_clientes'].iloc[0])
    ticket_medio = f"R$ {metricas_gerais['ticket_medio'].iloc[0]:,.2f}"
else:
    faturamento_total = "R$ 0,00"
    total_vendas = "0"
    total_clientes = "0"
    ticket_medio = "R$ 0,00"


# Criar gráficos estáticos
def criar_grafico_vendas_por_categoria():
    if vendas_por_categoria.empty:
        return go.Figure().update_layout(
            title="Nenhum dado disponível",
            template="plotly_white"
        )

    fig = px.pie(
        vendas_por_categoria,
        values='faturamento_categoria',
        names='categoria',
        title='Distribuição de Vendas por Categoria',
        hole=0.4
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


def criar_grafico_produtos_mais_vendidos():
    if produtos_mais_vendidos.empty:
        return go.Figure().update_layout(
            title="Nenhum dado disponível",
            template="plotly_white"
        )

    fig = px.bar(
        produtos_mais_vendidos,
        x='produto',
        y='total_faturado',
        color='categoria',
        title='Produtos com Maior Faturamento (acima de R$ 500)',
        text='total_faturado'
    )

    fig.update_layout(
        xaxis_title="Produtos",
        yaxis_title="Faturamento Total (R$)",
        template="plotly_white",
        xaxis_tickangle=-45
    )

    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')

    return fig


def criar_grafico_top_clientes():
    if top_clientes.empty:
        return go.Figure().update_layout(
            title="Nenhum dado disponível",
            template="plotly_white"
        )

    fig = px.bar(
        top_clientes,
        x='cliente',
        y='total_gasto',
        color='total_compras',
        title='Top 10 Clientes por Valor Gasto',
        text='total_gasto'
    )

    fig.update_layout(
        xaxis_title="Clientes",
        yaxis_title="Total Gasto (R$)",
        template="plotly_white",
        xaxis_tickangle=-45
    )

    fig.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')

    return fig


def criar_tabela_clientes_acima_media():
    if clientes_acima_media.empty:
        return html.P("Nenhum cliente acima da média encontrado.", className="text-center")

    linhas = []
    for _, row in clientes_acima_media.head(8).iterrows():
        linha = html.Tr([
            html.Td(row['cliente']),
            html.Td(row['cidade']),
            html.Td(row['data_venda'].strftime('%d/%m/%Y') if hasattr(row['data_venda'], 'strftime') else row[
                'data_venda']),
            html.Td(f"R$ {row['valor_total']:,.2f}")
        ])
        linhas.append(linha)

    return dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Cliente"),
            html.Th("Cidade"),
            html.Th("Data"),
            html.Th("Valor")
        ]))] +
        [html.Tbody(linhas)],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


def criar_tabela_ultimas_vendas():
    if vendas_clientes.empty:
        return html.P("Nenhuma venda encontrada.", className="text-center")

    linhas = []
    for _, row in vendas_clientes.head(8).iterrows():
        linha = html.Tr([
            html.Td(row['data_venda'].strftime('%d/%m/%Y') if hasattr(row['data_venda'], 'strftime') else row[
                'data_venda']),
            html.Td(row['cliente']),
            html.Td(f"R$ {row['valor_total']:,.2f}")
        ])
        linhas.append(linha)

    return dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Data"),
            html.Th("Cliente"),
            html.Th("Valor")
        ]))] +
        [html.Tbody(linhas)],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


def criar_tabela_top_clientes():
    if top_clientes.empty:
        return html.P("Nenhum cliente encontrado.", className="text-center")

    linhas = []
    for _, row in top_clientes.iterrows():
        linha = html.Tr([
            html.Td(row['cliente']),
            html.Td(row['cidade']),
            html.Td(row['total_compras']),
            html.Td(f"R$ {row['total_gasto']:,.2f}")
        ])
        linhas.append(linha)

    return dbc.Table(
        [html.Thead(html.Tr([
            html.Th("Cliente"),
            html.Th("Cidade"),
            html.Th("Compras"),
            html.Th("Total Gasto")
        ]))] +
        [html.Tbody(linhas)],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
    )


# Inicializar o app Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard de Vendas - Análise Estática"

# Layout do dashboard
app.layout = dbc.Container([
    # Cabeçalho
    dbc.Row([
        dbc.Col([
            html.H1("📊 Dashboard de Vendas", className="text-center my-4"),
            html.P("Análise estática dos dados históricos de vendas", className="text-center text-muted"),
            html.Hr()
        ])
    ]),

    # Métricas Gerais
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("💰 Faturamento Total", className="card-title"),
                    html.H3(faturamento_total, className="card-text text-success"),
                    html.Small("Total acumulado", className="text-muted")
                ])
            ], className="h-100")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🛒 Total de Vendas", className="card-title"),
                    html.H3(total_vendas, className="card-text text-primary"),
                    html.Small("Quantidade de vendas", className="text-muted")
                ])
            ], className="h-100")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("👥 Total de Clientes", className="card-title"),
                    html.H3(total_clientes, className="card-text text-info"),
                    html.Small("Clientes ativos", className="text-muted")
                ])
            ], className="h-100")
        ], width=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("🎫 Ticket Médio", className="card-title"),
                    html.H3(ticket_medio, className="card-text text-warning"),
                    html.Small("Valor médio por venda", className="text-muted")
                ])
            ], className="h-100")
        ], width=3)
    ], className="mb-4"),

    # Gráficos Principais
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📊 Distribuição por Categoria"),
                dbc.CardBody([
                    dcc.Graph(figure=criar_grafico_vendas_por_categoria())
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🏆 Produtos Mais Vendidos"),
                dbc.CardBody([
                    dcc.Graph(figure=criar_grafico_produtos_mais_vendidos())
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("👑 Top Clientes"),
                dbc.CardBody([
                    dcc.Graph(figure=criar_grafico_top_clientes())
                ])
            ])
        ], width=4)
    ], className="mb-4"),

    # Tabelas Detalhadas
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("⭐ Clientes Acima da Média"),
                dbc.CardBody([
                    criar_tabela_clientes_acima_media()
                ])
            ], className="h-100")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📋 Últimas Vendas"),
                dbc.CardBody([
                    criar_tabela_ultimas_vendas()
                ])
            ], className="h-100")
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("🥇 Ranking de Clientes"),
                dbc.CardBody([
                    criar_tabela_top_clientes()
                ])
            ], className="h-100")
        ], width=4)
    ], className="mb-4"),

    # Resumo Estatístico
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Estatísticas Gerais"),
                dbc.CardBody([
                    html.Ul([
                        html.Li(f"Total de produtos analisados: {len(produtos_mais_vendidos)}"),
                        html.Li(f"Clientes premium identificados: {len(clientes_acima_media)}"),
                        html.Li(f"Categorias com vendas: {len(vendas_por_categoria)}"),
                        html.Li(f"Top clientes no ranking: {len(top_clientes)}")
                    ]),
                    html.Hr(),
                    html.P("Este dashboard apresenta uma análise estática dos dados históricos."),
                    html.P(f"Data da análise: {pd.Timestamp.now().strftime('%d/%m/%Y às %H:%M:%S')}"),
                    html.P(f"Base de dados: {len(vendas_clientes)} vendas registradas")
                ])
            ])
        ], width=12)
    ])
], fluid=True)

HOST = "0.0.0.0"

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard de Vendas Estático...")
    print(f"📊 Acesse: http://{HOST}:8010")
    print("⏹️  Para parar o servidor, pressione Ctrl+C")
    app.run(debug=True, host=HOST, port=8010)