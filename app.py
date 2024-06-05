from dash import Dash
from dash import dcc
from dash import html
from dash import Input, Output
from scipy.stats import pearsonr 

import numpy as np
import pandas as pd
import plotly.express as px

dados_metaverso = pd.read_csv('/Users/Dilermando/Documents/MFTD/csv/metaverse_transactions_dataset.csv')

# regioes e seus niveis
regioes = ['North America', 'South America', 'Europe', 'Africa', 'Asia']
niveis_de_risco = ['low_risk', 'high_risk', 'moderate_risk']

# Calculando médias para cada combinação de região e nível de risco

medias = {} #dicionario vazio
for regiao in regioes: #loop q intera as regioes
    for risco in niveis_de_risco: #loop q intera os niveis de risco
    #seleciona as linhas onde tem a localização e as msm coisa com o nivel
        filtro = (dados_metaverso['location_region'] == regiao) & (dados_metaverso['anomaly'] == risco)
        #calcula a media dos valores na coluna 'amount' do DataFrame que atendem ao filtro feito acima
        media = dados_metaverso.loc[filtro, 'amount'].mean()
        chave = f'{risco}_{regiao.replace(" ", "_")}' #substitui os espaços em brancos por _
        medias[chave] = media

#  dados -> DataFrame
df = pd.DataFrame({
    'Região': [regiao for risco in niveis_de_risco for regiao in regioes],
    'Nível de Risco': np.repeat(niveis_de_risco, len(regioes)),
    'Média de Valor da Transação': [medias[f'{risco}_{regiao.replace(" ", "_")}'] for risco in niveis_de_risco for regiao in regioes]
})

# Criando o gráfico
fig1 = px.bar(df, x='Região', y='Média de Valor da Transação', color='Nível de Risco', barmode='group',
             title='Média de Valor da Transação por Região e Nível de Risco',
             labels={'Média de Valor da Transação': 'Média de Valor da Transação ($)'})

# Lista de regiões
mediana_north_america = dados_metaverso[dados_metaverso['location_region'] == 'North America']['session_duration'].median()
mediana_south_america = dados_metaverso[dados_metaverso['location_region'] == 'South America']['session_duration'].median()
mediana_europe = dados_metaverso[dados_metaverso['location_region'] == 'Europe']['session_duration'].median()
mediana_africa = dados_metaverso[dados_metaverso['location_region'] == 'Africa']['session_duration'].median()
mediana_asia = dados_metaverso[dados_metaverso['location_region'] == 'Asia']['session_duration'].median()

df2 = pd.DataFrame({
    'Continente': ['North America', 'South America', 'Europe', 'Africa', 'Asia'],
    'Mediana do Tempo de Sessão': [mediana_north_america, mediana_south_america, mediana_europe, mediana_africa, mediana_asia]
})

fig2 = px.scatter(df2, x='Continente', y='Mediana do Tempo de Sessão')

# Função para calcular a moda e contagem das transações por região
def calcular_moda_e_contagem(df, regiao):
    filtro_regiao = df[df['location_region'] == regiao]
    moda_transacao = filtro_regiao['transaction_type'].mode()[0]
    contagem_transacao = filtro_regiao['transaction_type'].value_counts()[moda_transacao]
    return moda_transacao, contagem_transacao

# DataFrame para armazenar modas e contagens
df3 = pd.DataFrame({
    'Região': regioes,
    'Moda': [calcular_moda_e_contagem(dados_metaverso, regiao)[0] for regiao in regioes],
    'Contagem': [calcular_moda_e_contagem(dados_metaverso, regiao)[1] for regiao in regioes]
})

# Criando o gráfico
fig3 = px.bar(
    df3,
    x="Região",
    y="Contagem",
    color="Região",
    barmode="group",
    hover_name="Região",
    hover_data=["Moda", "Contagem"],
    title="Moda e Contagem das Transações por Região"
)

# Calculando médias para cada região
medias = {} #dicionario vazio
for regiao in regioes: #loop q intera as regioes
    #seleciona as linhas onde tem a localização
    filtro = (dados_metaverso['location_region'] == regiao)
    #calcula a media dos valores na coluna 'amount' do DataFrame que atendem ao filtro feito acima
    media = dados_metaverso.loc[filtro, 'amount'].mean()
    chave = f'amount_{regiao.replace(" ", "_")}' #substitui os espaços em brancos por _
    medias[chave] = media

#  dados -> DataFrame
df4 = pd.DataFrame({
    'Região': regioes,
    'Média de Valor da Transação': [medias[f'amount_{regiao.replace(" ", "_")}'] for regiao in regioes]
})

# Criando o gráfico de pizza
fig4 = px.pie(df4, values='Média de Valor da Transação', names='Região', title='Média de Valor da Transação por Região')

correlacao, p_valor = pearsonr(dados_metaverso['login_frequency'], dados_metaverso['risk_score'])

app = Dash(__name__)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)

def display_page(pathname):
    if pathname == '/grafico1':
        return html.Div(children=[
            dcc.Graph(id='grafico-1', figure=fig1),
        ])
    elif pathname == '/grafico2':
        return html.Div(children=[
            dcc.Graph(id='grafico-2', figure=fig2),
        ])
    elif pathname == '/grafico3':
        return html.Div(children=[
            dcc.Graph(id='grafico-3', figure=fig3),
        ])
    elif pathname == '/grafico4':
        return html.Div(children=[
            dcc.Graph(id='grafico-4', figure=fig4),
        ])
    elif pathname == '/grafico5':
        return html.Div(children=[
            dcc.Graph(
            figure=px.scatter(
                dados_metaverso,
                x='login_frequency',
                y='risk_score',
                title='Correlação entre Pontuação de Risco e Frequência de Login',
                labels={
                    'frequência de Login': 'Frequência de Login',
                    'pontuação de risco': 'Pontuação de Risco'
                    }
                )
            ),
        ])
    else:
        return 'Página não encontrada'

if __name__ == '__main__':
    app.run_server(debug=True)
