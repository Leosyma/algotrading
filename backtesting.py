#%% Bibliotecas
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import MetaTrader5 as mt5
import json

#%% Conexão com o MetaTrader5
with open('credentials.json') as f:
   data = json.load(f)

# Conectar com MetaTrader5
if not mt5.initialize():
    mt5.login(login=data['loginJson'], password=data['passwordJson'], server=data['serverJson'])
    print("initialize() failed, error code = ", mt5.last_error())
    mt5.shutdown()
    quit()
    
#%% Leitura dos dados
# Mini Dolar - WDO$D
data = mt5.copy_rates_range("WDO$D", mt5.TIMEFRAME_M1,  #daily
                                            datetime(2022, 1, 1),
                                            datetime.now())
# Transforma em dataframe
df_data = pd.DataFrame(data)

# Converte a data
df_data['time']=pd.to_datetime(df_data['time'], unit='s')

# Define a data como o index
df_data.set_index('time',inplace=True, drop=False)

#%% Gráfico
# Cálculo do indicador
# Data de Corte
dt1 = datetime(2023,12,10).date()
dt2 = datetime(2023,12,15).date()
df_cut = df_data[(df_data.index.date >= dt1) & (df_data.index.date <= dt2)]

# Gráfico de vela com o volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    subplot_titles=('OHLC','Volume'), vertical_spacing=0.05,
                    row_width=[0.2, 0.7])
fig.add_trace(go.Candlestick(x=df_cut.index, open=df_cut.open, 
                             high=df_cut.high, low=df_cut.low, close=df_cut.close), row=1, col=1)

fig.add_trace(go.Bar(x=df_cut.index, y=df_cut['real_volume']), row=2, col=1)
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_xaxes(rangebreaks=[{'pattern': 'day of week', 'bounds': [6, 1]}, {'pattern': 'hour', 'bounds': [18, 10]}])
fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
fig.show()

#%% Estratégia - Bollinger Bands
# Período desejado para analisar
w = 200

# Constante para ser multiplicada pelo STD
boll_size = 2

# Quantas ações são compradas
bet_size = 5

# Média móvel
df_data['roll_mean'] = df_data['close'].rolling(w).mean()
df_data['roll_std'] = df_data['close'].rolling(w).std()
df_data['roll_vol'] = df_data['real_volume'].rolling(w).mean()
df_data['up_band'] = df_data['roll_mean'] + boll_size * df_data['roll_std']
df_data['down_band'] = df_data['roll_mean'] - boll_size * df_data['roll_std']
df_data['over_mean_vol'] = df_data['real_volume'] > df_data['roll_vol']

df_cut['roll_mean'] = df_cut['close'].rolling(w).mean()
df_cut['roll_std'] = df_cut['close'].rolling(w).std()
df_cut['up_band'] = df_cut['roll_mean'] + boll_size * df_cut['roll_std']
df_cut['down_band'] = df_cut['roll_mean'] - boll_size * df_cut['roll_std']

# Gráfico de vela com o volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    subplot_titles=('OHLC','Volume'), vertical_spacing=0.05,
                    row_width=[0.2, 0.7])
fig.add_trace(go.Candlestick(x=df_cut.index, open=df_cut.open, 
                             high=df_cut.high, low=df_cut.low, close=df_cut.close), row=1, col=1)

fig.add_trace(go.Scatter(x=df_cut.index, y=df_cut.roll_mean), row=1, col=1)
fig.add_trace(go.Scatter(x=df_cut.index, y=df_cut.up_band), row=1, col=1)
fig.add_trace(go.Scatter(x=df_cut.index, y=df_cut.down_band), row=1, col=1)

fig.add_trace(go.Bar(x=df_cut.index, y=df_cut['real_volume']), row=2, col=1)
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_xaxes(rangebreaks=[{'pattern': 'day of week', 'bounds': [6, 1]}, {'pattern': 'hour', 'bounds': [18, 10]}])
fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
fig.show()

#%% Planejamento da estratégia
# 1. Abrir uma posição comprada quando o preço fecha abaixo da banda inferior
# 2. Entrar na posição apenas se o volume estiver acima da média histórica
# 3. Encerrar a posição quando o preço fecha acima da banda superior
from time import time

# Variável para saber se abrimos uma posição de compra ou venda
open_position = 0

# Guarda os trades realizados
trades = []

t1 = time()
for idx, row in df_data.iterrows():
    if open_position == 0 and row['close'] < row['down_band'] and row['over_mean_vol'] == 1:
        open_position = 1
        # side = 1 (compra) e side = =1 (venda)
        trades += [{'price': row['close'], 'side': 1, 'volume': bet_size}]

    elif open_position == 1 and row['close'] > row['up_band']:
        open_position = 0
        trades += [{'price': row['close'], 'side': -1, 'volume': bet_size}]
t2 = time()
print(t2 - t1)

len(trades)

#%% Otimização de performance da estratégia
{j:i for i, j in enumerate(df_data.columns)}

# Variável para saber se abrimos uma posição de compra ou venda
open_position = 0

# Guarda os trades realizados
trades = []

# Nomes das colunas
dict_map = {j:i for i, j in enumerate(df_data.columns)}

t1 = time()
for row in df_data.values:
    if open_position == 0 and row[dict_map['close']] < row[dict_map['down_band']] and row[dict_map['over_mean_vol']] == 1:
        open_position = 1
        # side = 1 (compra) e side = =1 (venda)
        trades += [{'time': row[dict_map['time']],'price': row[dict_map['close']], 'side': 1, 'volume': bet_size}]

    elif open_position == 1 and row[dict_map['close']] > row[dict_map['up_band']]:
        open_position = 0
        trades += [{'time': row[dict_map['time']],'price': row[dict_map['close']], 'side': -1, 'volume': bet_size}]
t2 = time()
print(t2 - t1)

len(trades)

#%% Resultado
df_trades = pd.DataFrame(trades)
df_trades.set_index('time',inplace=True)

# Retorno
df_trades['return'] = df_trades['price'] - df_trades['price'].shift(1)
df_trades[df_trades['side'] == -1]['return'].cumsum().plot()

#%% Debugando a estratégia
# Data de Corte
dt1 = datetime(2023,12,10).date()
dt2 = datetime(2023,12,15).date()
df_cut = df_data[(df_data.index.date >= dt1) & (df_data.index.date <= dt2)]

df_trades_cut = df_trades[(df_trades.index.date >= dt1) & (df_trades.index.date <= dt2)]
df_buys = df_trades_cut[df_trades_cut['side'] == 1]
df_sells = df_trades_cut[df_trades_cut['side'] == -1]

# Gráfico de vela com o volume
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    subplot_titles=('OHLC','Volume'), vertical_spacing=0.05,
                    row_width=[0.2, 0.7])
fig.add_trace(go.Candlestick(x=df_cut.index, open=df_cut.open, 
                             high=df_cut.high, low=df_cut.low, close=df_cut.close), row=1, col=1)

fig.add_trace(go.Scatter(x=df_cut.index, y=df_cut.up_band), row=1, col=1)
fig.add_trace(go.Scatter(x=df_cut.index, y=df_cut.down_band), row=1, col=1)

fig.add_trace(go.Scatter(x=df_buys.index, y=df_buys['price'], marker_size=15, mode='markers',
                        marker_color='green', marker_symbol='triangle-up'), row=1, col=1)
fig.add_trace(go.Scatter(x=df_sells.index, y=df_sells['price'], marker_size=15, mode='markers',
                        marker_color='red', marker_symbol='triangle-down'), row=1, col=1)

fig.add_trace(go.Bar(x=df_cut.index, y=df_cut['real_volume']), row=2, col=1)
fig.update_layout(xaxis_rangeslider_visible=False)
fig.update_xaxes(rangebreaks=[{'pattern': 'day of week', 'bounds': [6, 1]}, {'pattern': 'hour', 'bounds': [18, 10]}])
fig.update_layout(margin=dict(l=30, r=30, t=30, b=30))
fig.show()

#%% Avaliação de múltiplos parâmetros
# Período desejado para analisar
w = 200

# Constante para ser multiplicada pelo STD
boll_size = 2

# Quantas ações são compradas
bet_size = 5

def bollinger_band(w, boll_size, bet_size=5):
    # Média móvel
    df_data['roll_mean'] = df_data['close'].rolling(w).mean()
    df_data['roll_std'] = df_data['close'].rolling(w).std()
    df_data['roll_vol'] = df_data['real_volume'].rolling(w).mean()
    df_data['up_band'] = df_data['roll_mean'] + boll_size * df_data['roll_std']
    df_data['down_band'] = df_data['roll_mean'] - boll_size * df_data['roll_std']
    df_data['over_mean_vol'] = df_data['real_volume'] > df_data['roll_vol']

    # Variável para saber se abrimos uma posição de compra ou venda
    open_position = 0

    # Guarda os trades realizados
    trades = []

    # Nomes das colunas
    dict_map = {j:i for i, j in enumerate(df_data.columns)}

    for row in df_data.values:
        if open_position == 0 and row[dict_map['close']] < row[dict_map['down_band']] and row[dict_map['over_mean_vol']] == 1:
            open_position = 1
            # side = 1 (compra) e side = =1 (venda)
            trades += [{'time': row[dict_map['time']],'price': row[dict_map['close']], 'side': 1, 'volume': bet_size}]

        elif open_position == 1 and row[dict_map['close']] > row[dict_map['up_band']]:
            open_position = 0
            trades += [{'time': row[dict_map['time']],'price': row[dict_map['close']], 'side': -1, 'volume': bet_size}]

    df_trades = pd.DataFrame(trades)
    df_trades.set_index('time',inplace=True)

    # Retorno
    df_trades['return'] = df_trades['price'] - df_trades['price'].shift(1)

    return df_trades

df_trades = bollinger_band(100, 2)
df_trades[df_trades['side'] == -1]['return'].cumsum().plot()

# Testando outros parâmetros
for i in [10, 20, 50, 100, 200]:
    for j in [1, 2]:
        print(i, j)
        df_trades = bollinger_band(i, j)
        df_trades[df_trades['side'] == -1]['return'].cumsum().plot()