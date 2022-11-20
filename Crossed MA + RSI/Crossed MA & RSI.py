import vectorbt as vbt
from datetime import datetime
from datetime import timedelta
import yfinance as yf
import pandas as pd
import numpy as np

# Oganizando os dados (períodos mais curtos como intradiários - necessário mudar a API)
end_d = datetime.now() 
start_d = end_d - timedelta(days=365)

carteira = ['^BVSP']

mdata = pd.DataFrame()
for t in carteira:
    mdata[t] = yf.download(t,start=start_d, end = end_d, interval='1d')['Adj Close']

# checar os dados
# print(mdata)

def custom_indicator(close, rsi_window = 14, entry= 70, exit1= 30, maf_window = 3, mas_window = 5):
  # Indicadores
  rsi = vbt.RSI.run(close, window= rsi_window).rsi.to_numpy() # Configurando RSI
  ma_fast = vbt.MA.run(close, window=  maf_window) # Configurando MA
  ma_slow1 = vbt.MA.run(close, window=  mas_window) # Configurando MA
  
  # Filtro
  trend = np.where( (rsi > entry) & (ma_fast.ma_crossed_below(ma_slow1)), -1, 0)
  trend = np.where( (rsi < exit1) & (ma_fast.ma_crossed_above(ma_slow1)), 1, trend)
  return trend
  

ind = vbt.IndicatorFactory(
  class_name='combination', # Nome do indicador
  short_name='comb', # Apelido
  input_names=['close'], # Dados que vão passar pela função
  param_names=['rsi_window', 'entry', 'exit1', 'maf_window', 'mas_window'], # Nome dos parâmetros passados
  output_names=['value']
  ).from_apply_func(
          custom_indicator,
          rsi_window=14, # Configure as janelas
          entry=70,
          exit1=30,
          maf_window = 3, 
          mas_window = 5 # Configure as janelas
          )

res = ind.run(
  mdata, 
  rsi_window= [16], # Configure as janelas
  entry=[70],
  exit1=[35],
  maf_window = [4], 
  mas_window = [9], # Configure as janelas
  param_product=True
  ) 

print(res.value)

entries = res.value == 1.0
exits = res.value == -1.0

pf = vbt.Portfolio.from_signals(mdata, entries, exits)
returns = pf.total_return()
#(pf.stats())
print(returns.max())
#print(returns.idxmax())
#print(pf.stats())

pf.value().vbt.plot().show()