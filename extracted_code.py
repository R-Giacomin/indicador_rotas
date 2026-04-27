# @title
# Verificar se pacotes estão instalados e se não tiver, instala-los

import subprocess
import sys

def check_and_install_packages():
  """Checks if 'sidrapy' and others are installed and installs them if not."""
  packages = ['sidrapy']
  for package in packages:
    try:
      __import__(package)
      print(f"'{package}' is already installed.")
    except ImportError:
      print(f"'{package}' is not installed. Installing...")
      try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"'{package}' has been successfully installed.")
      except subprocess.CalledProcessError as e:
        print(f"Error installing '{package}': {e}")

# Call the function to check and install the packages.
check_and_install_packages()

# ---

# @title
import sidrapy
import pandas as pd
import numpy as np

# ---

path = '/content/drive/MyDrive/SICONV/classificações SDR/classificacao_municipios_SDR.csv'

# ---

# @title Fazer upload do arquivo "TODOS_OS_POLOS_30_04_2025.xlsx" com a relação dos municípios por Rotas e Polos

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

# ---

#@title Definição do ano para o qual será calculado o indicador:

Ano = '2024' # @param {type: "string"}
Ano0 = str(int(Ano) - 1)
period=f'{Ano0}-{Ano}'

# ---

# @title
# Importação da Tabela SIDRA 74 - Produção de origem animal, por tipo de produto, 215 Valor da produção,  2682  Leite (Mil litros), por municípios
Vlr_Prod_leite = sidrapy.get_table(table_code='74',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='215',
                        classifications={"80": "2682"})
# Substitui as colunas pela primeira observação
Vlr_Prod_leite.columns = Vlr_Prod_leite.iloc[0]
Vlr_Prod_leite = Vlr_Prod_leite[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_leite = Vlr_Prod_leite.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_leite = Vlr_Prod_leite.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_leite['Valor'] = pd.to_numeric(Vlr_Prod_leite['Valor'])
# Corrected column rename
Vlr_Prod_leite = Vlr_Prod_leite.rename(columns={'Município (Código)': 'COD_IBGE'})
# Desagregar os valores por ano
Vlr_Prod_leite = Vlr_Prod_leite.pivot(index='COD_IBGE', columns='Ano', values='Valor').reset_index() # Corrected column name
Vlr_Prod_leite

# ---

R_LEITE = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_LEITE'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_LEITE': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Vlr_Prod_leite = pd.merge(Vlr_Prod_leite, R_LEITE, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Vlr_Prod_leite['regiao'] = Vlr_Prod_leite['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos totais por município

# Indicadores do total de municípios
Vlr_Prod_leite_Ano0 = Vlr_Prod_leite.iloc[:, 1].sum()
Vlr_Prod_leite_Ano = Vlr_Prod_leite.iloc[:, 2].sum()
Variação_Vlr_Prod_leite = (Vlr_Prod_leite_Ano/Vlr_Prod_leite_Ano0)-1

# ---

# @title
Vlr_Prod_leite_grouped_reg = Vlr_Prod_leite.groupby('regiao').agg({
    Vlr_Prod_leite.columns[1]: 'sum',
    Vlr_Prod_leite.columns[2]: 'sum'
}).reset_index()
Vlr_Prod_leite_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Vlr_Prod_leite_grouped = Vlr_Prod_leite.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Vlr_Prod_leite.columns[1]: 'sum',
    Vlr_Prod_leite.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Vlr_Prod_leite_grouped['Part%_Ano_0'] = (Vlr_Prod_leite_grouped[Vlr_Prod_leite.columns[1]] / Vlr_Prod_leite_Ano0) * 100
Vlr_Prod_leite_grouped['Part%_Ano'] = (Vlr_Prod_leite_grouped[Vlr_Prod_leite.columns[2]] / Vlr_Prod_leite_Ano) * 100
Vlr_Prod_leite_grouped['Variação'] = (Vlr_Prod_leite_grouped[Vlr_Prod_leite.columns[2]]/Vlr_Prod_leite_grouped[Vlr_Prod_leite.columns[1]]-1)
Vlr_Prod_leite_grouped['Indicador_participação'] = (Vlr_Prod_leite_grouped['Variação']-Variação_Vlr_Prod_leite)/abs(Variação_Vlr_Prod_leite)

Vlr_Prod_leite_grouped

# ---

# @title
# Cálculo dos indicadores por municípios
Vlr_Prod_leite['Part%_Ano_0'] = (Vlr_Prod_leite[Vlr_Prod_leite.columns[1]] / Vlr_Prod_leite_Ano0) * 100
Vlr_Prod_leite['Part%_Ano'] = (Vlr_Prod_leite[Vlr_Prod_leite.columns[2]] / Vlr_Prod_leite_Ano) * 100
Vlr_Prod_leite['Variação'] = (Vlr_Prod_leite[Vlr_Prod_leite.columns[2]]/Vlr_Prod_leite[Vlr_Prod_leite.columns[1]]-1)
Vlr_Prod_leite['Indicador_participação'] = (Vlr_Prod_leite['Variação']-Variação_Vlr_Prod_leite)/abs(Variação_Vlr_Prod_leite)

Vlr_Prod_leite

# ---

# @title
# Indicadores do total da Rota
Vlr_Prod_leite_Rota_Ano0 = Vlr_Prod_leite_grouped.iloc[:, 2].sum()
Vlr_Prod_leite_Rota_Ano = Vlr_Prod_leite_grouped.iloc[:, 3].sum()
Variação_Vlr_Prod_leite_Rota = (Vlr_Prod_leite_Rota_Ano/Vlr_Prod_leite_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Leite_Ano0 = (Vlr_Prod_leite_Rota_Ano0/Vlr_Prod_leite_Ano0)
Part_Rota_Leite_Ano = (Vlr_Prod_leite_Rota_Ano/Vlr_Prod_leite_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Leite = (Variação_Vlr_Prod_leite_Rota-Variação_Vlr_Prod_leite)/abs(Variação_Vlr_Prod_leite)

# ---

# @title Cálculo do Indicador
# Impressão dos resultados

print(f"Valor da produção de todos os municípios em {Ano0}: {Vlr_Prod_leite_Ano0}")
print(f"Valor da produção de todos os municípios em {Ano} é: {Vlr_Prod_leite_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Vlr_Prod_leite*100:.2f}%")

print("\n")

print(f"Valor da produção da Rota em {Ano0}: {Vlr_Prod_leite_Rota_Ano0}, que corresponde a {Part_Rota_Leite_Ano0*100:.2f}% do valor da produção nacional")
print(f"Valor da produção da Rota em {Ano}: {Vlr_Prod_leite_Rota_Ano}, que corresponde a {Part_Rota_Leite_Ano*100:.2f}% do valor da produção nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Vlr_Prod_leite_Rota*100:.2f}%")
print("\n")
print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Leite:.4f}")

# ---

# @title Cálculo do indicador regional
Vlr_Prod_leite_sum_by_regiao = Vlr_Prod_leite_grouped.groupby('regiao').agg({
    Vlr_Prod_leite_grouped.columns[2]: 'sum',
    Vlr_Prod_leite_grouped.columns[3]: 'sum'
}).reset_index()

Vlr_Prod_leite_sum_by_regiao = Vlr_Prod_leite_sum_by_regiao.merge(Vlr_Prod_leite_grouped_reg, on='regiao', how='left')

Vlr_Prod_leite_sum_by_regiao['var_rota'] = Vlr_Prod_leite_sum_by_regiao.iloc[:, 2] / Vlr_Prod_leite_sum_by_regiao.iloc[:, 1] - 1
Vlr_Prod_leite_sum_by_regiao['var_total'] = Vlr_Prod_leite_sum_by_regiao.iloc[:, 4] / Vlr_Prod_leite_sum_by_regiao.iloc[:, 3] - 1
Vlr_Prod_leite_sum_by_regiao['Indicador_participação'] = (Vlr_Prod_leite_sum_by_regiao['var_rota'] - Vlr_Prod_leite_sum_by_regiao['var_total']) / abs(Vlr_Prod_leite_sum_by_regiao['var_total'])

Vlr_Prod_leite_sum_by_regiao

# ---

# @title
# Importação da Tabela SIDRA 74 - Produção de origem animal, por tipo de produto, 215 Valor da produção,  2687  Mel, por municípios
Vlr_Prod_Mel = sidrapy.get_table(table_code='74',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='215',
                        classifications={"80": "2687"},
                        timeout=60) # Added timeout
# Substitui as colunas pela primeira observação
Vlr_Prod_Mel.columns = Vlr_Prod_Mel.iloc[0]
Vlr_Prod_Mel = Vlr_Prod_Mel[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_Mel = Vlr_Prod_Mel.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_Mel = Vlr_Prod_Mel.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_Mel['Valor'] = pd.to_numeric(Vlr_Prod_Mel['Valor'])
Vlr_Prod_Mel = Vlr_Prod_Mel.rename(columns={'Município (Código)': 'COD_IBGE'}) # Corrected column rename
# Desagregar os valores por ano
Vlr_Prod_Mel = Vlr_Prod_Mel.pivot(index='COD_IBGE', columns='Ano', values='Valor').reset_index() # Corrected column name
Vlr_Prod_Mel.columns.name = None  # Remove the columns name
Vlr_Prod_Mel

# ---

# @title
# Extração da tabela da Rota
R_MEL = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_MEL'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_MEL': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Vlr_Prod_Mel = pd.merge(Vlr_Prod_Mel, R_MEL, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Vlr_Prod_Mel['regiao'] = Vlr_Prod_Mel['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos indicadores

# Indicadores do total de municípios
Vlr_Prod_Mel_Ano0 = Vlr_Prod_Mel.iloc[:, 1].sum()
Vlr_Prod_Mel_Ano = Vlr_Prod_Mel.iloc[:, 2].sum()
Variação_Vlr_Prod_Mel = (Vlr_Prod_Mel_Ano/Vlr_Prod_Mel_Ano0)-1

# ---

# @title
Vlr_Prod_Mel_grouped_reg = Vlr_Prod_Mel.groupby('regiao').agg({
    Vlr_Prod_Mel.columns[1]: 'sum',
    Vlr_Prod_Mel.columns[2]: 'sum'
}).reset_index()
Vlr_Prod_Mel_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Vlr_Prod_Mel_grouped = Vlr_Prod_Mel.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Vlr_Prod_Mel.columns[1]: 'sum',
    Vlr_Prod_Mel.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Vlr_Prod_Mel_grouped['Part%_Ano_0'] = (Vlr_Prod_Mel_grouped[Vlr_Prod_Mel.columns[1]] / Vlr_Prod_Mel_Ano0) * 100
Vlr_Prod_Mel_grouped['Part%_Ano'] = (Vlr_Prod_Mel_grouped[Vlr_Prod_Mel.columns[2]] / Vlr_Prod_Mel_Ano) * 100
Vlr_Prod_Mel_grouped['Variação'] = (Vlr_Prod_Mel_grouped[Vlr_Prod_Mel.columns[2]]/Vlr_Prod_Mel_grouped[Vlr_Prod_Mel.columns[1]]-1)
Vlr_Prod_Mel_grouped['Indicador_participação'] = (Vlr_Prod_Mel_grouped['Variação']-Variação_Vlr_Prod_Mel)/abs(Variação_Vlr_Prod_Mel)

Vlr_Prod_Mel_grouped

# ---

# @title
# Cálculo dos indicadores por municípios
Vlr_Prod_Mel['Part%_Ano_0'] = (Vlr_Prod_Mel[Vlr_Prod_Mel.columns[1]] / Vlr_Prod_Mel_Ano0) * 100
Vlr_Prod_Mel['Part%_Ano'] = (Vlr_Prod_Mel[Vlr_Prod_Mel.columns[2]] / Vlr_Prod_Mel_Ano) * 100
Vlr_Prod_Mel['Variação'] = (Vlr_Prod_Mel[Vlr_Prod_Mel.columns[2]]/Vlr_Prod_Mel[Vlr_Prod_Mel.columns[1]]-1)
Vlr_Prod_Mel['Indicador_participação'] = (Vlr_Prod_Mel['Variação']-Variação_Vlr_Prod_Mel)/abs(Variação_Vlr_Prod_Mel)

Vlr_Prod_Mel

# ---

# @title
# Indicadores do total da Rota
Vlr_Prod_Mel_Rota_Ano0 = Vlr_Prod_Mel_grouped.iloc[:, 2].sum()
Vlr_Prod_Mel_Rota_Ano = Vlr_Prod_Mel_grouped.iloc[:, 3].sum()
Variação_Vlr_Prod_Mel_Rota = (Vlr_Prod_Mel_Rota_Ano/Vlr_Prod_Mel_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Mel_Ano0 = (Vlr_Prod_Mel_Rota_Ano0/Vlr_Prod_Mel_Ano0)
Part_Rota_Mel_Ano = (Vlr_Prod_Mel_Rota_Ano/Vlr_Prod_Mel_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Mel = (Variação_Vlr_Prod_Mel_Rota-Variação_Vlr_Prod_Mel)/abs(Variação_Vlr_Prod_Mel)

# ---

# @title Cálculo do indicador
# Impressão dos resultados

print(f"Valor da produção de todos os municípios em {Ano0}: {Vlr_Prod_Mel_Ano0}")
print(f"Valor da produção de todos os municípios em {Ano}: {Vlr_Prod_Mel_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Vlr_Prod_Mel*100:.2f}%")

print("\n")

print(f"Valor da produção da Rota em {Ano0}: {Vlr_Prod_Mel_Rota_Ano0}, que corresponde a {Part_Rota_Mel_Ano0*100:.2f}% do valor da produção nacional")
print(f"Valor da produção da Rota em {Ano}: {Vlr_Prod_Mel_Rota_Ano}, que corresponde a {Part_Rota_Mel_Ano*100:.2f}% do valor da produção nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Vlr_Prod_Mel_Rota*100:.2f}%")

print("\n")

print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Mel:.4f}")

# ---

# @title Cálculo do indicador regional
Vlr_Prod_Mel_sum_by_regiao = Vlr_Prod_Mel_grouped.groupby('regiao').agg({
    Vlr_Prod_Mel_grouped.columns[2]: 'sum',
    Vlr_Prod_Mel_grouped.columns[3]: 'sum'
}).reset_index()

Vlr_Prod_Mel_sum_by_regiao = Vlr_Prod_Mel_sum_by_regiao.merge(Vlr_Prod_Mel_grouped_reg, on='regiao', how='left')

Vlr_Prod_Mel_sum_by_regiao['var_rota'] = Vlr_Prod_Mel_sum_by_regiao.iloc[:, 2] / Vlr_Prod_Mel_sum_by_regiao.iloc[:, 1] - 1
Vlr_Prod_Mel_sum_by_regiao['var_total'] = Vlr_Prod_Mel_sum_by_regiao.iloc[:, 4] / Vlr_Prod_Mel_sum_by_regiao.iloc[:, 3] - 1
Vlr_Prod_Mel_sum_by_regiao['Indicador_participação'] = (Vlr_Prod_Mel_sum_by_regiao['var_rota'] - Vlr_Prod_Mel_sum_by_regiao['var_total']) / abs(Vlr_Prod_Mel_sum_by_regiao['var_total'])

Vlr_Prod_Mel_sum_by_regiao

# ---

# @title
# Tabela SIDRA 3940- Produção da aquicultura, por tipo de produto, 215- Valor da produção, 0 - Total

Vlr_Prod_Pescado = sidrapy.get_table(table_code='3940',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='215',
                        classifications={"654": "0"},
                        timeout=60) # Added timeout
# Substitui as colunas pela primeira observação
Vlr_Prod_Pescado.columns = Vlr_Prod_Pescado.iloc[0]
Vlr_Prod_Pescado = Vlr_Prod_Pescado[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_Pescado = Vlr_Prod_Pescado.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_Pescado = Vlr_Prod_Pescado.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_Pescado['Valor'] = pd.to_numeric(Vlr_Prod_Pescado['Valor'])
Vlr_Prod_Pescado = Vlr_Prod_Pescado.rename(columns={'Município (Código)': 'COD_IBGE'}) # Corrected column rename
# Desagregar os valores por ano
Vlr_Prod_Pescado = Vlr_Prod_Pescado.pivot(index='COD_IBGE', columns='Ano', values='Valor').reset_index() # Corrected column name
Vlr_Prod_Pescado.columns.name = None  # Remove the columns name
Vlr_Prod_Pescado

# ---

# @title
# Extração da tabela da Rota
R_PESCADO = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_PESCADO'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_PESCADO': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Vlr_Prod_Pescado = pd.merge(Vlr_Prod_Pescado, R_PESCADO, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Vlr_Prod_Pescado['regiao'] = Vlr_Prod_Pescado['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos indicadores

# Indicadores do total de municípios
Vlr_Prod_Pescado_Ano0 = Vlr_Prod_Pescado.iloc[:, 1].sum()
Vlr_Prod_Pescado_Ano = Vlr_Prod_Pescado.iloc[:, 2].sum()
Variação_Vlr_Prod_Pescado = (Vlr_Prod_Pescado_Ano/Vlr_Prod_Pescado_Ano0)-1

# ---

# @title
Vlr_Prod_Pescado_grouped_reg = Vlr_Prod_Pescado.groupby('regiao').agg({
    Vlr_Prod_Pescado.columns[1]: 'sum',
    Vlr_Prod_Pescado.columns[2]: 'sum'
}).reset_index()
Vlr_Prod_Pescado_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Vlr_Prod_Pescado_grouped = Vlr_Prod_Pescado.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Vlr_Prod_Pescado.columns[1]: 'sum',
    Vlr_Prod_Pescado.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Vlr_Prod_Pescado_grouped['Part%_Ano_0'] = (Vlr_Prod_Pescado_grouped[Vlr_Prod_Pescado.columns[1]] / Vlr_Prod_Pescado_Ano0) * 100
Vlr_Prod_Pescado_grouped['Part%_Ano'] = (Vlr_Prod_Pescado_grouped[Vlr_Prod_Pescado.columns[2]] / Vlr_Prod_Pescado_Ano) * 100
Vlr_Prod_Pescado_grouped['Variação'] = (Vlr_Prod_Pescado_grouped[Vlr_Prod_Pescado.columns[2]]/Vlr_Prod_Pescado_grouped[Vlr_Prod_Pescado.columns[1]]-1)
Vlr_Prod_Pescado_grouped['Indicador_participação'] = (Vlr_Prod_Pescado_grouped['Variação']-Variação_Vlr_Prod_Pescado)/abs(Variação_Vlr_Prod_Pescado)

Vlr_Prod_Pescado_grouped

# ---

# @title
# Cálculo dos indicadores por Municípios
Vlr_Prod_Pescado['Part%_Ano_0'] = (Vlr_Prod_Pescado[Vlr_Prod_Pescado.columns[1]] / Vlr_Prod_Pescado_Ano0) * 100
Vlr_Prod_Pescado['Part%_Ano'] = (Vlr_Prod_Pescado[Vlr_Prod_Pescado.columns[2]] / Vlr_Prod_Pescado_Ano) * 100
Vlr_Prod_Pescado['Variação'] = (Vlr_Prod_Pescado[Vlr_Prod_Pescado.columns[2]]/Vlr_Prod_Pescado[Vlr_Prod_Pescado.columns[1]]-1)
Vlr_Prod_Pescado['Indicador_participação'] = (Vlr_Prod_Pescado['Variação']-Variação_Vlr_Prod_Pescado)/abs(Variação_Vlr_Prod_Pescado)

Vlr_Prod_Pescado

# ---

# @title
# Indicadores do total da Rota
Vlr_Prod_Pescado_Rota_Ano0 = Vlr_Prod_Pescado_grouped.iloc[:, 2].sum()
Vlr_Prod_Pescado_Rota_Ano = Vlr_Prod_Pescado_grouped.iloc[:, 3].sum()
Variação_Vlr_Prod_Pescado_Rota = (Vlr_Prod_Pescado_Rota_Ano/Vlr_Prod_Pescado_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Pescado_Ano0 = (Vlr_Prod_Pescado_Rota_Ano0/Vlr_Prod_Pescado_Ano0)
Part_Rota_Pescado_Ano = (Vlr_Prod_Pescado_Rota_Ano/Vlr_Prod_Pescado_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Pescado = (Variação_Vlr_Prod_Pescado_Rota-Variação_Vlr_Prod_Pescado)/abs(Variação_Vlr_Prod_Pescado)

# ---

# @title Cálculo do indicador
# Impressão dos resultados

print(f"Valor da produção de todos os municípios em {Ano0}: {Vlr_Prod_Pescado_Ano0}")
print(f"Valor da produção de todos os municípios em {Ano}: {Vlr_Prod_Pescado_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Vlr_Prod_Pescado*100:.2f}%")

print("\n")

print(f"Valor da produção da Rota em {Ano0}: {Vlr_Prod_Pescado_Rota_Ano0}, que corresponde a {Part_Rota_Pescado_Ano0*100:.2f}% do valor da produção nacional")
print(f"Valor da produção da Rota em {Ano}: {Vlr_Prod_Pescado_Rota_Ano}, que corresponde a {Part_Rota_Pescado_Ano*100:.2f}% do valor da produção nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Vlr_Prod_Pescado_Rota*100:.2f}%")
print("\n")
print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Pescado:.4f}")

# ---

# @title Cálculo do indicador regional
Vlr_Prod_Pescado_sum_by_regiao = Vlr_Prod_Pescado_grouped.groupby('regiao').agg({
    Vlr_Prod_Pescado_grouped.columns[2]: 'sum',
    Vlr_Prod_Pescado_grouped.columns[3]: 'sum'
}).reset_index()

Vlr_Prod_Pescado_sum_by_regiao = Vlr_Prod_Pescado_sum_by_regiao.merge(Vlr_Prod_Pescado_grouped_reg, on='regiao', how='left')

Vlr_Prod_Pescado_sum_by_regiao['var_rota'] = Vlr_Prod_Pescado_sum_by_regiao.iloc[:, 2] / Vlr_Prod_Pescado_sum_by_regiao.iloc[:, 1] - 1
Vlr_Prod_Pescado_sum_by_regiao['var_total'] = Vlr_Prod_Pescado_sum_by_regiao.iloc[:, 4] / Vlr_Prod_Pescado_sum_by_regiao.iloc[:, 3] - 1
Vlr_Prod_Pescado_sum_by_regiao['Indicador_participação'] = (Vlr_Prod_Pescado_sum_by_regiao['var_rota'] - Vlr_Prod_Pescado_sum_by_regiao['var_total']) / abs(Vlr_Prod_Pescado_sum_by_regiao['var_total'])

Vlr_Prod_Pescado_sum_by_regiao

# ---

# @title
# Tabela SIDRA 3939- Efetivo dos rebanhos, por tipo de rebanho, 105- Efetivo dos rebanhos, 2681- Caprino e 2677- Ovino

Rebanho_Cordeiro = sidrapy.get_table(table_code='3939',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='105',
                        classifications={"79": "2681,2677"})
# Substitui as colunas pela primeira observação
Rebanho_Cordeiro.columns = Rebanho_Cordeiro.iloc[0]
Rebanho_Cordeiro = Rebanho_Cordeiro[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Rebanho_Cordeiro = Rebanho_Cordeiro.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Rebanho_Cordeiro = Rebanho_Cordeiro.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Rebanho_Cordeiro['Valor'] = pd.to_numeric(Rebanho_Cordeiro['Valor'])
Rebanho_Cordeiro = Rebanho_Cordeiro.rename(columns={'Município (Código)': 'COD_IBGE'})
# Pivoting the DataFrame
Rebanho_Cordeiro = Rebanho_Cordeiro.pivot_table(index='COD_IBGE', columns='Ano', values='Valor', aggfunc='sum')
Rebanho_Cordeiro

# ---

# @title
# Extração da tabela da Rota
R_CORDEIRO = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_CORDEIRO'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_CORDEIRO': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Rebanho_Cordeiro = pd.merge(Rebanho_Cordeiro, R_CORDEIRO, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Rebanho_Cordeiro['regiao'] = Rebanho_Cordeiro['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos indicadores

# Indicadores do total de municípios
Rebanho_Cordeiro_Ano0 = Rebanho_Cordeiro.iloc[:, 1].sum()
Rebanho_Cordeiro_Ano = Rebanho_Cordeiro.iloc[:, 2].sum()
Variação_Rebanho_Cordeiro = (Rebanho_Cordeiro_Ano/Rebanho_Cordeiro_Ano0)-1

# ---

# @title
Rebanho_Cordeiro_grouped_reg = Rebanho_Cordeiro.groupby('regiao').agg({
    Rebanho_Cordeiro.columns[1]: 'sum',
    Rebanho_Cordeiro.columns[2]: 'sum'
}).reset_index()
Rebanho_Cordeiro_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Rebanho_Cordeiro_grouped = Rebanho_Cordeiro.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Rebanho_Cordeiro.columns[1]: 'sum',
    Rebanho_Cordeiro.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Rebanho_Cordeiro_grouped['Part%_Ano_0'] = (Rebanho_Cordeiro_grouped[Rebanho_Cordeiro.columns[1]] / Rebanho_Cordeiro_Ano0) * 100
Rebanho_Cordeiro_grouped['Part%_Ano'] = (Rebanho_Cordeiro_grouped[Rebanho_Cordeiro.columns[2]] / Rebanho_Cordeiro_Ano) * 100
Rebanho_Cordeiro_grouped['Variação'] = (Rebanho_Cordeiro_grouped[Rebanho_Cordeiro.columns[2]]/Rebanho_Cordeiro_grouped[Rebanho_Cordeiro.columns[1]]-1)
Rebanho_Cordeiro_grouped['Indicador_participação'] = (Rebanho_Cordeiro_grouped['Variação']-Variação_Rebanho_Cordeiro)/abs(Variação_Rebanho_Cordeiro)

Rebanho_Cordeiro_grouped

# ---

# @title
# Cálculo dos indicadores por Municípios
Rebanho_Cordeiro['Part%_Ano_0'] = (Rebanho_Cordeiro[Rebanho_Cordeiro.columns[1]] / Rebanho_Cordeiro_Ano0) * 100
Rebanho_Cordeiro['Part%_Ano'] = (Rebanho_Cordeiro[Rebanho_Cordeiro.columns[2]] / Rebanho_Cordeiro_Ano) * 100
Rebanho_Cordeiro['Variação'] = (Rebanho_Cordeiro[Rebanho_Cordeiro.columns[2]]/Rebanho_Cordeiro[Rebanho_Cordeiro.columns[1]]-1)
Rebanho_Cordeiro['Indicador_participação'] = (Rebanho_Cordeiro['Variação']-Variação_Rebanho_Cordeiro)/abs(Variação_Rebanho_Cordeiro)

Rebanho_Cordeiro

# ---

# @title
# Indicadores do total da Rota
Rebanho_Cordeiro_Rota_Ano0 = Rebanho_Cordeiro_grouped.iloc[:, 2].sum()
Rebanho_Cordeiro_Rota_Ano = Rebanho_Cordeiro_grouped.iloc[:, 3].sum()
Variação_Rebanho_Cordeiro_Rota = (Rebanho_Cordeiro_Rota_Ano/Rebanho_Cordeiro_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Cordeiro_Ano0 = (Rebanho_Cordeiro_Rota_Ano0/Rebanho_Cordeiro_Ano0)
Part_Rota_Cordeiro_Ano = (Rebanho_Cordeiro_Rota_Ano/Rebanho_Cordeiro_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Cordeiro = (Variação_Rebanho_Cordeiro_Rota-Variação_Rebanho_Cordeiro)/abs(Variação_Rebanho_Cordeiro)

# ---

# @title Cálculo do indicador
# Impressão dos resultados

print(f"Efetivo de rebanho de todos os municípios em {Ano0}: {Rebanho_Cordeiro_Ano0}")
print(f"Efetivo de rebanho de todos os municípios em {Ano}: {Rebanho_Cordeiro_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Rebanho_Cordeiro*100:.2f}%")

print("\n")

print(f"Efetivo de rebanho da Rota em {Ano0}: {Rebanho_Cordeiro_Rota_Ano0}, que corresponde a {Part_Rota_Cordeiro_Ano0*100:.2f}% do rebanho nacional")
print(f"Efetivo de rebanho da Rota em {Ano}: {Rebanho_Cordeiro_Rota_Ano}, que corresponde a {Part_Rota_Cordeiro_Ano*100:.2f}% do rebanho nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Rebanho_Cordeiro_Rota*100:.2f}%")

print("\n")

print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Cordeiro:.4f}")

# ---

# @title Cálculo do indicador regional
Rebanho_Cordeiro_sum_by_regiao = Rebanho_Cordeiro_grouped.groupby('regiao').agg({
    Rebanho_Cordeiro_grouped.columns[2]: 'sum',
    Rebanho_Cordeiro_grouped.columns[3]: 'sum'
}).reset_index()

Rebanho_Cordeiro_sum_by_regiao = Rebanho_Cordeiro_sum_by_regiao.merge(Rebanho_Cordeiro_grouped_reg, on='regiao', how='left')

Rebanho_Cordeiro_sum_by_regiao['var_rota'] = Rebanho_Cordeiro_sum_by_regiao.iloc[:, 2] / Rebanho_Cordeiro_sum_by_regiao.iloc[:, 1] - 1
Rebanho_Cordeiro_sum_by_regiao['var_total'] = Rebanho_Cordeiro_sum_by_regiao.iloc[:, 4] / Rebanho_Cordeiro_sum_by_regiao.iloc[:, 3] - 1
Rebanho_Cordeiro_sum_by_regiao['Indicador_participação'] = (Rebanho_Cordeiro_sum_by_regiao['var_rota'] - Rebanho_Cordeiro_sum_by_regiao['var_total']) / abs(Rebanho_Cordeiro_sum_by_regiao['var_total'])

Rebanho_Cordeiro_sum_by_regiao

# ---

# @title
# Tabela SIDRA 1613- Área destinada à colheita, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras permanentes, 215- Valor da produção, 45981- Açaí

Vlr_Prod_Açaí_lavoura = sidrapy.get_table(table_code='1613',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='215',
                        classifications={"82": "45981"})
# Substitui as colunas pela primeira observação
Vlr_Prod_Açaí_lavoura.columns = Vlr_Prod_Açaí_lavoura.iloc[0]
Vlr_Prod_Açaí_lavoura = Vlr_Prod_Açaí_lavoura[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_Açaí_lavoura = Vlr_Prod_Açaí_lavoura.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_Açaí_lavoura = Vlr_Prod_Açaí_lavoura.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_Açaí_lavoura['Valor'] = pd.to_numeric(Vlr_Prod_Açaí_lavoura['Valor'])
Vlr_Prod_Açaí_lavoura = Vlr_Prod_Açaí_lavoura.rename(columns={'Município (Código)': 'COD_IBGE'})

# Tabela SIDRA 289- Quantidade produzida e valor da produção na extração vegetal, por tipo de produto extrativo, 145- Valor da produção na extração vegetal, 3403- 1.1 - Açaí (fruto)

Vlr_Prod_Açaí_extração = sidrapy.get_table(table_code='289',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='145',
                        classifications={"193": "3403"})
# Substitui as colunas pela primeira observação
Vlr_Prod_Açaí_extração.columns = Vlr_Prod_Açaí_extração.iloc[0]
Vlr_Prod_Açaí_extração = Vlr_Prod_Açaí_extração[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_Açaí_extração = Vlr_Prod_Açaí_extração.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_Açaí_extração = Vlr_Prod_Açaí_extração.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_Açaí_extração['Valor'] = pd.to_numeric(Vlr_Prod_Açaí_extração['Valor'])
Vlr_Prod_Açaí_extração = Vlr_Prod_Açaí_extração.rename(columns={'Município (Código)': 'COD_IBGE'})


# Apensando (concatenando) os dois DataFrames verticalmente
Vlr_Prod_Açaí = pd.concat([Vlr_Prod_Açaí_lavoura, Vlr_Prod_Açaí_extração], ignore_index=True)

# Pivoting the DataFrame
Vlr_Prod_Açaí = Vlr_Prod_Açaí.pivot_table(index='COD_IBGE', columns='Ano', values='Valor', aggfunc='sum')

# Transform zero values to NaN
Vlr_Prod_Açaí = Vlr_Prod_Açaí.replace(0, np.nan)
Vlr_Prod_Açaí

# ---

# @title
# Extração da tabela da Rota
R_ACAI = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_ACAI'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_ACAI': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Vlr_Prod_Açaí = pd.merge(Vlr_Prod_Açaí, R_ACAI, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Vlr_Prod_Açaí['regiao'] = Vlr_Prod_Açaí['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos indicadores

# Indicadores do total de municípios
Vlr_Prod_Açaí_Ano0 = Vlr_Prod_Açaí.iloc[:, 1].sum()
Vlr_Prod_Açaí_Ano = Vlr_Prod_Açaí.iloc[:, 2].sum()
Variação_Vlr_Prod_Açaí = (Vlr_Prod_Açaí_Ano/Vlr_Prod_Açaí_Ano0)-1

# ---

# @title
Vlr_Prod_Açaí_grouped_reg = Vlr_Prod_Açaí.groupby('regiao').agg({
    Vlr_Prod_Açaí.columns[1]: 'sum',
    Vlr_Prod_Açaí.columns[2]: 'sum'
}).reset_index()
Vlr_Prod_Açaí_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Vlr_Prod_Açaí_grouped = Vlr_Prod_Açaí.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Vlr_Prod_Açaí.columns[1]: 'sum',
    Vlr_Prod_Açaí.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Vlr_Prod_Açaí_grouped['Part%_Ano_0'] = (Vlr_Prod_Açaí_grouped[Vlr_Prod_Açaí.columns[1]] / Vlr_Prod_Açaí_Ano0) * 100
Vlr_Prod_Açaí_grouped['Part%_Ano'] = (Vlr_Prod_Açaí_grouped[Vlr_Prod_Açaí.columns[2]] / Vlr_Prod_Açaí_Ano) * 100
Vlr_Prod_Açaí_grouped['Variação'] = (Vlr_Prod_Açaí_grouped[Vlr_Prod_Açaí.columns[2]]/Vlr_Prod_Açaí_grouped[Vlr_Prod_Açaí.columns[1]]-1)
Vlr_Prod_Açaí_grouped['Indicador_participação'] = (Vlr_Prod_Açaí_grouped['Variação']-Variação_Vlr_Prod_Açaí)/abs(Variação_Vlr_Prod_Açaí)

Vlr_Prod_Açaí_grouped

# ---

# @title
# Cálculo dos indicadores por Municípios
Vlr_Prod_Açaí['Part%_Ano_0'] = (Vlr_Prod_Açaí[Vlr_Prod_Açaí.columns[1]] / Vlr_Prod_Açaí_Ano0) * 100
Vlr_Prod_Açaí['Part%_Ano'] = (Vlr_Prod_Açaí[Vlr_Prod_Açaí.columns[2]] / Vlr_Prod_Açaí_Ano) * 100
Vlr_Prod_Açaí['Variação'] = (Vlr_Prod_Açaí[Vlr_Prod_Açaí.columns[2]]/Vlr_Prod_Açaí[Vlr_Prod_Açaí.columns[1]]-1)
Vlr_Prod_Açaí['Indicador_participação'] = (Vlr_Prod_Açaí['Variação']-Variação_Vlr_Prod_Açaí)/abs(Variação_Vlr_Prod_Açaí)

Vlr_Prod_Açaí

# ---

# @title
# Indicadores do total da Rota
Vlr_Prod_Açaí_Rota_Ano0 = Vlr_Prod_Açaí_grouped.iloc[:, 2].sum()
Vlr_Prod_Açaí_Rota_Ano = Vlr_Prod_Açaí_grouped.iloc[:, 3].sum()
Variação_Vlr_Prod_Açaí_Rota = (Vlr_Prod_Açaí_Rota_Ano/Vlr_Prod_Açaí_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Açaí_Ano0 = (Vlr_Prod_Açaí_Rota_Ano0/Vlr_Prod_Açaí_Ano0)
Part_Rota_Açaí_Ano = (Vlr_Prod_Açaí_Rota_Ano/Vlr_Prod_Açaí_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Açaí = (Variação_Vlr_Prod_Açaí_Rota-Variação_Vlr_Prod_Açaí)/abs(Variação_Vlr_Prod_Açaí)

# ---

# @title Cálculo do indicador
# Impressão dos resultados

print(f"Valor da produção de todos os municípios em {Ano0}: {Vlr_Prod_Açaí_Ano0}")
print(f"Valor da produção de todos os municípios em {Ano}: {Vlr_Prod_Açaí_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Vlr_Prod_Açaí*100:.2f}%")

print("\n")

print(f"Valor da produção da Rota em {Ano0}: {Vlr_Prod_Açaí_Rota_Ano0}, que corresponde a {Part_Rota_Açaí_Ano0*100:.2f}% do valor da produção nacional")
print(f"Valor da produção da Rota em {Ano}: {Vlr_Prod_Açaí_Rota_Ano}, que corresponde a {Part_Rota_Açaí_Ano*100:.2f}% do valor da produção nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Vlr_Prod_Açaí_Rota*100:.2f}%")
print("\n")
print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Açaí:.4f}")

# ---

# @title Cálculo do indicador regional
Vlr_Prod_Açaí_sum_by_regiao = Vlr_Prod_Açaí_grouped.groupby('regiao').agg({
    Vlr_Prod_Açaí_grouped.columns[2]: 'sum',
    Vlr_Prod_Açaí_grouped.columns[3]: 'sum'
}).reset_index()

Vlr_Prod_Açaí_sum_by_regiao = Vlr_Prod_Açaí_sum_by_regiao.merge(Vlr_Prod_Açaí_grouped_reg, on='regiao', how='left')

Vlr_Prod_Açaí_sum_by_regiao['var_rota'] = Vlr_Prod_Açaí_sum_by_regiao.iloc[:, 2] / Vlr_Prod_Açaí_sum_by_regiao.iloc[:, 1] - 1
Vlr_Prod_Açaí_sum_by_regiao['var_total'] = Vlr_Prod_Açaí_sum_by_regiao.iloc[:, 4] / Vlr_Prod_Açaí_sum_by_regiao.iloc[:, 3] - 1
Vlr_Prod_Açaí_sum_by_regiao['Indicador_participação'] = (Vlr_Prod_Açaí_sum_by_regiao['var_rota'] - Vlr_Prod_Açaí_sum_by_regiao['var_total']) / abs(Vlr_Prod_Açaí_sum_by_regiao['var_total'])

Vlr_Prod_Açaí_sum_by_regiao

# ---

# @title
# Tabela SIDRA 1613- Área destinada à colheita, área colhida, quantidade produzida, rendimento médio e valor da produção das lavouras permanentes, 215- Valor da produção, 2722- Cacau (em amêndoa)

Vlr_Prod_Cacau = sidrapy.get_table(table_code='1613',
                        period=period,
                        territorial_level="6",
                        ibge_territorial_code="all",
                        variable='215',
                        classifications={"82": "2722"},
                        timeout=60) # Added timeout
# Substitui as colunas pela primeira observação
Vlr_Prod_Cacau.columns = Vlr_Prod_Cacau.iloc[0]
Vlr_Prod_Cacau = Vlr_Prod_Cacau[1:].reset_index(drop=True)
# manter no dataframe apenas as colunas necessárias
Vlr_Prod_Cacau = Vlr_Prod_Cacau.iloc[:, [5,4,8]]
# prompt: tornar os valores "-" e "..." em nan no dataframe df
Vlr_Prod_Cacau = Vlr_Prod_Cacau.replace(['-',"..."], np.nan)
# Convert the 'Valor' column to numeric, coercing errors to NaN
Vlr_Prod_Cacau['Valor'] = pd.to_numeric(Vlr_Prod_Cacau['Valor'])
Vlr_Prod_Cacau = Vlr_Prod_Cacau.rename(columns={'Município (Código)': 'COD_IBGE'}) # Corrected column rename
# Desagregar os valores por ano
Vlr_Prod_Cacau = Vlr_Prod_Cacau.pivot(index='COD_IBGE', columns='Ano', values='Valor').reset_index() # Corrected column name
Vlr_Prod_Cacau.columns.name = None  # Remove the columns name
Vlr_Prod_Cacau

# ---

# Extração da tabela da Rota
R_CACAU = pd.read_csv(path, usecols=['COD_MUNIC_IBGE', 'R_CACAU'], dtype=str).rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', 'R_CACAU': 'NOME_DO_POLO'})

# ---

# @title
# Junção dos Dataframes
Vlr_Prod_Cacau = pd.merge(Vlr_Prod_Cacau, R_CACAU, on='COD_IBGE', how='left')

# ---

# @title
# Add a 'regiao' column based on the first digit of 'COD_IBGE'
Vlr_Prod_Cacau['regiao'] = Vlr_Prod_Cacau['COD_IBGE'].astype(str).str[0]

# ---

# @title
# Calculos dos indicadores

# Indicadores do total de municípios
Vlr_Prod_Cacau_Ano0 = Vlr_Prod_Cacau.iloc[:, 1].sum()
Vlr_Prod_Cacau_Ano = Vlr_Prod_Cacau.iloc[:, 2].sum()
Variação_Vlr_Prod_Cacau = (Vlr_Prod_Cacau_Ano/Vlr_Prod_Cacau_Ano0)-1

# ---

# @title
Vlr_Prod_Cacau_grouped_reg = Vlr_Prod_Cacau.groupby('regiao').agg({
    Vlr_Prod_Cacau.columns[1]: 'sum',
    Vlr_Prod_Cacau.columns[2]: 'sum'
}).reset_index()
Vlr_Prod_Cacau_grouped_reg

# ---

# @title
# Agregação dos dados pelos Polos
Vlr_Prod_Cacau_grouped = Vlr_Prod_Cacau.groupby(['regiao', 'NOME_DO_POLO']).agg({
    Vlr_Prod_Cacau.columns[1]: 'sum',
    Vlr_Prod_Cacau.columns[2]: 'sum'
}).reset_index()

# Cálculo dos indicadores por Polos
Vlr_Prod_Cacau_grouped['Part%_Ano_0'] = (Vlr_Prod_Cacau_grouped[Vlr_Prod_Cacau.columns[1]] / Vlr_Prod_Cacau_Ano0) * 100
Vlr_Prod_Cacau_grouped['Part%_Ano'] = (Vlr_Prod_Cacau_grouped[Vlr_Prod_Cacau.columns[2]] / Vlr_Prod_Cacau_Ano) * 100
Vlr_Prod_Cacau_grouped['Variação'] = (Vlr_Prod_Cacau_grouped[Vlr_Prod_Cacau.columns[2]]/Vlr_Prod_Cacau_grouped[Vlr_Prod_Cacau.columns[1]]-1)
Vlr_Prod_Cacau_grouped['Indicador_participação'] = (Vlr_Prod_Cacau_grouped['Variação']-Variação_Vlr_Prod_Cacau)/abs(Variação_Vlr_Prod_Cacau)

Vlr_Prod_Cacau_grouped

# ---

# @title
# Cálculo dos indicadores por Municípios
Vlr_Prod_Cacau['Part%_Ano_0'] = (Vlr_Prod_Cacau[Vlr_Prod_Cacau.columns[1]] / Vlr_Prod_Cacau_Ano0) * 100
Vlr_Prod_Cacau['Part%_Ano'] = (Vlr_Prod_Cacau[Vlr_Prod_Cacau.columns[2]] / Vlr_Prod_Cacau_Ano) * 100
Vlr_Prod_Cacau['Variação'] = (Vlr_Prod_Cacau[Vlr_Prod_Cacau.columns[2]]/Vlr_Prod_Cacau[Vlr_Prod_Cacau.columns[1]]-1)
Vlr_Prod_Cacau['Indicador_participação'] = (Vlr_Prod_Cacau['Variação']-Variação_Vlr_Prod_Cacau)/abs(Variação_Vlr_Prod_Cacau)

Vlr_Prod_Cacau

# ---

# @title
# Indicadores do total da Rota
Vlr_Prod_Cacau_Rota_Ano0 = Vlr_Prod_Cacau_grouped.iloc[:, 2].sum()
Vlr_Prod_Cacau_Rota_Ano = Vlr_Prod_Cacau_grouped.iloc[:, 3].sum()
Variação_Vlr_Prod_Cacau_Rota = (Vlr_Prod_Cacau_Rota_Ano/Vlr_Prod_Cacau_Rota_Ano0)-1

# Indicador de participação na produção nacional
Part_Rota_Cacau_Ano0 = (Vlr_Prod_Cacau_Rota_Ano0/Vlr_Prod_Cacau_Ano0)
Part_Rota_Cacau_Ano = (Vlr_Prod_Cacau_Rota_Ano/Vlr_Prod_Cacau_Ano)

# Indicador de ganho/perda de participação
Indicador_participação_Cacau = (Variação_Vlr_Prod_Cacau_Rota-Variação_Vlr_Prod_Cacau)/abs(Variação_Vlr_Prod_Cacau)

# ---

# @title Cálculo do indicador
# Impressão dos resultados

print(f"Valor da produção de todos os municípios em {Ano0}: {Vlr_Prod_Cacau_Ano0}")
print(f"Valor da produção de todos os municípios em {Ano}: {Vlr_Prod_Cacau_Ano}")
print(f"Variação em todos os municípios de {Ano0} para {Ano}: {Variação_Vlr_Prod_Cacau*100:.2f}%")

print("\n")

print(f"Valor da produção da Rota em {Ano0}: {Vlr_Prod_Cacau_Rota_Ano0}, que corresponde a {Part_Rota_Cacau_Ano0*100:.2f}% do valor da produção nacional")
print(f"Valor da produção da Rota em {Ano}: {Vlr_Prod_Cacau_Rota_Ano}, que corresponde a {Part_Rota_Cacau_Ano*100:.2f}% do valor da produção nacional")
print(f"Variação da Rota de {Ano0} para {Ano}: {Variação_Vlr_Prod_Cacau_Rota*100:.2f}%")
print("\n")
print(f"Indicador de ganho/perda de participação da Rota: {Indicador_participação_Cacau:.4f}")

# ---

# @title Cálculo do indicador regional
Vlr_Prod_Cacau_sum_by_regiao = Vlr_Prod_Cacau_grouped.groupby('regiao').agg({
    Vlr_Prod_Cacau_grouped.columns[2]: 'sum',
    Vlr_Prod_Cacau_grouped.columns[3]: 'sum'
}).reset_index()

Vlr_Prod_Cacau_sum_by_regiao = Vlr_Prod_Cacau_sum_by_regiao.merge(Vlr_Prod_Cacau_grouped_reg, on='regiao', how='left')

Vlr_Prod_Cacau_sum_by_regiao['var_rota'] = Vlr_Prod_Cacau_sum_by_regiao.iloc[:, 2] / Vlr_Prod_Cacau_sum_by_regiao.iloc[:, 1] - 1
Vlr_Prod_Cacau_sum_by_regiao['var_total'] = Vlr_Prod_Cacau_sum_by_regiao.iloc[:, 4] / Vlr_Prod_Cacau_sum_by_regiao.iloc[:, 3] - 1
Vlr_Prod_Cacau_sum_by_regiao['Indicador_participação'] = (Vlr_Prod_Cacau_sum_by_regiao['var_rota'] - Vlr_Prod_Cacau_sum_by_regiao['var_total']) / abs(Vlr_Prod_Cacau_sum_by_regiao['var_total'])

Vlr_Prod_Cacau_sum_by_regiao

# ---

# @title
Indicador_PPA = (Indicador_participação_Leite+Indicador_participação_Mel+Indicador_participação_Pescado+Indicador_participação_Açaí+Indicador_participação_Cacau+Indicador_participação_Cordeiro)/6

print(f"Indicador do PPA para {Ano}: {Indicador_PPA:.4f}")

# ---

# @title
Indicadores_Regionais_sum_by_regiao = pd.concat([
    Vlr_Prod_leite_sum_by_regiao,
    Vlr_Prod_Mel_sum_by_regiao,
    Vlr_Prod_Pescado_sum_by_regiao,
    Rebanho_Cordeiro_sum_by_regiao,
    Vlr_Prod_Açaí_sum_by_regiao,
    Vlr_Prod_Cacau_sum_by_regiao
], ignore_index=True)

mean_indicador_participacao_by_regiao = Indicadores_Regionais_sum_by_regiao.groupby('regiao')['Indicador_participação'].mean().reset_index()

print("Média do Indicador de Participação por Região:")
print(mean_indicador_participacao_by_regiao)

# ---

# @title
Vlr_Prod_leite_grouped['rota'] = "Rota do Leite"
Vlr_Prod_Mel_grouped['rota'] = "Rota do Mel"
Vlr_Prod_Pescado_grouped['rota'] = "Rota do Pescado"
Rebanho_Cordeiro_grouped['rota'] = "Rota do Cordeiro"
Vlr_Prod_Açaí_grouped['rota'] = "Rota do Açaí"
Vlr_Prod_Cacau_grouped['rota'] = "Rota do Cacau"

# ---

# @title
Indicadores_Regionais_Rotas = pd.concat([Vlr_Prod_leite_grouped, Vlr_Prod_Mel_grouped, Vlr_Prod_Pescado_grouped, Rebanho_Cordeiro_grouped, Vlr_Prod_Açaí_grouped, Vlr_Prod_Cacau_grouped], ignore_index=True)
display(Indicadores_Regionais_Rotas)

# ---

# @title
display(Indicadores_Regionais_Rotas.groupby('regiao')['Indicador_participação'].describe())

# ---

# @title
!pip install mapclassify -q
!pip install geobr -q

# ---

# @title
# Import necessary libraries
import os
import requests
import zipfile
import io
import geopandas as gpd
import pandas as pd
import numpy as np
import geobr
from plotnine import *
%matplotlib inline

# ---

# @title Baixar geometria dos estados
uf_map = geobr.read_state(year=2000)

# ---

# @title Baixar geometria dos municípios
# Check if the directory exists, and create it if it doesn't
directory = './shapefiles'
if not os.path.exists(directory):
  os.makedirs(directory)
  print(f"Directory '{directory}' created successfully.")
else:
  print(f"Directory '{directory}' already exists.")

# URL to download the shapefile
url = f"https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_{Ano}/Brasil/BR_Municipios_{Ano}.zip"

# Download the zip file
response = requests.get(url, stream=True)
response.raise_for_status()  # Raise an exception for bad status codes

# Extract the zip file
zip_file = zipfile.ZipFile(io.BytesIO(response.content))
zip_file.extractall('./shapefiles')

# List the contents of the shapefiles folder to check if the extraction was successful
print("Files in shapefiles directory:", os.listdir(directory))

# Load the shapefile
brazil_map = gpd.read_file(f'./shapefiles/BR_Municipios_{Ano}.shp')

# ---

Vlr_Prod_leite_geo

# ---

# @title
# Juntar a tabela da Rota do Leite com o GeoDataFrame de municípios
Vlr_Prod_leite_geo = brazil_map.merge(Vlr_Prod_leite, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

#Vlr_Prod_leite_geo = Vlr_Prod_leite_geo.drop(columns=['COD_IBGE', 'NOME_MUNICIPIO',	'UF', 'regiao'])

# Filter out rows where 'NOME_DO_POLO' is null
Vlr_Prod_leite_shape = Vlr_Prod_leite_geo[Vlr_Prod_leite_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Leite via dissolve
Vlr_Prod_leite_shape['geometry'] = Vlr_Prod_leite_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Vlr_Prod_leite_shape = Vlr_Prod_leite_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Vlr_Prod_leite_shape = Vlr_Prod_leite_shape.reset_index()

Vlr_Prod_leite_shape = Vlr_Prod_leite_shape[['NOME_DO_POLO',	'geometry']]

Vlr_Prod_leite_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Vlr_Prod_leite_geo = Vlr_Prod_leite_geo.copy()

limite_inferior = Vlr_Prod_leite_geo['2024'].min()
q75 = Vlr_Prod_leite_geo['2024'].quantile(0.75)
limite_superior = Vlr_Prod_leite_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_leite = (
    ggplot(Vlr_Prod_leite_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor da Produção\n(R$ mil)'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_leite_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Valor da produção de Leite {Ano}')
)

mapa_leite

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -5, 5
Vlr_Prod_leite_geo = Vlr_Prod_leite_geo.copy()
Vlr_Prod_leite_geo['Indicador_participação_trunc'] = Vlr_Prod_leite_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_leite = (
    ggplot(Vlr_Prod_leite_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=Vlr_Prod_leite_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação da produção de Leite {Ano}')
)

mapa_leite

# ---

# @title
# Juntar a tabela da Rota do Mel com o GeoDataFrame de municípios
Vlr_Prod_Mel_geo = brazil_map.merge(Vlr_Prod_Mel, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

#Vlr_Prod_Mel_geo = Vlr_Prod_Mel_geo.drop(columns=['COD_IBGE', 'NOME_MUNICIPIO',	'UF', 'regiao'])

# Filter out rows where 'NOME_DO_POLO' is null
Vlr_Prod_Mel_shape = Vlr_Prod_Mel_geo[Vlr_Prod_Mel_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Mel via dissolve
Vlr_Prod_Mel_shape['geometry'] = Vlr_Prod_Mel_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Vlr_Prod_Mel_shape = Vlr_Prod_Mel_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Vlr_Prod_Mel_shape = Vlr_Prod_Mel_shape.reset_index()

Vlr_Prod_Mel_shape = Vlr_Prod_Mel_shape[['NOME_DO_POLO',	'geometry']]

Vlr_Prod_Mel_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Vlr_Prod_Mel_geo = Vlr_Prod_Mel_geo.copy()

limite_inferior = Vlr_Prod_Mel_geo['2024'].min()
q75 = Vlr_Prod_Mel_geo['2024'].quantile(0.75)
limite_superior = Vlr_Prod_Mel_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_Mel = (
    ggplot(Vlr_Prod_Mel_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor da Produção\n(R$ mil)'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Mel_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Valor da produção de Mel {Ano}')
)

mapa_Mel

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Defina os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -5, 5
Vlr_Prod_Mel_geo = Vlr_Prod_Mel_geo.copy()
Vlr_Prod_Mel_geo['Indicador_participação_trunc'] = Vlr_Prod_Mel_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_Mel = (
    ggplot(Vlr_Prod_Mel_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Mel_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação da produção de Mel {Ano}')
)

mapa_Mel

# ---

# @title
# Juntar a tabela da Rota do Pescado com o GeoDataFrame de municípios
Vlr_Prod_Pescado_geo = brazil_map.merge(Vlr_Prod_Pescado, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

# Filter out rows where 'NOME_DO_POLO' is null
Vlr_Prod_Pescado_shape = Vlr_Prod_Pescado_geo[Vlr_Prod_Pescado_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Pescado via dissolve
Vlr_Prod_Pescado_shape['geometry'] = Vlr_Prod_Pescado_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Vlr_Prod_Pescado_shape = Vlr_Prod_Pescado_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Vlr_Prod_Pescado_shape = Vlr_Prod_Pescado_shape.reset_index()

Vlr_Prod_Pescado_shape = Vlr_Prod_Pescado_shape[['NOME_DO_POLO',	'geometry']]

Vlr_Prod_Pescado_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Vlr_Prod_Pescado_geo = Vlr_Prod_Pescado_geo.copy()

limite_inferior = Vlr_Prod_Pescado_geo['2024'].min()
q75 = Vlr_Prod_Pescado_geo['2024'].quantile(0.75)
limite_superior = Vlr_Prod_Pescado_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_Pescado = (
    ggplot(Vlr_Prod_Pescado_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor da Produção\n(R$ mil)'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Pescado_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Valor da produção de Pescado {Ano}')
)

mapa_Pescado

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Defina os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -5, 5
Vlr_Prod_Pescado_geo = Vlr_Prod_Pescado_geo.copy()
Vlr_Prod_Pescado_geo['Indicador_participação_trunc'] = Vlr_Prod_Pescado_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_Pescado = (
    ggplot(Vlr_Prod_Pescado_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Pescado_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação da produção de Pescado {Ano}')
)

mapa_Pescado

# ---

# @title
# Juntar a tabela da Rota do Cordeiro com o GeoDataFrame de municípios
Rebanho_Cordeiro_geo = brazil_map.merge(Rebanho_Cordeiro, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

# Filter out rows where 'NOME_DO_POLO' is null
Rebanho_Cordeiro_shape = Rebanho_Cordeiro_geo[Rebanho_Cordeiro_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Cordeiro via dissolve
Rebanho_Cordeiro_shape['geometry'] = Rebanho_Cordeiro_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Rebanho_Cordeiro_shape = Rebanho_Cordeiro_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Rebanho_Cordeiro_shape = Rebanho_Cordeiro_shape.reset_index()

Rebanho_Cordeiro_shape = Rebanho_Cordeiro_shape[['NOME_DO_POLO',	'geometry']]

Rebanho_Cordeiro_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Rebanho_Cordeiro_geo = Rebanho_Cordeiro_geo.copy()

limite_inferior = Rebanho_Cordeiro_geo['2024'].min()
q75 = Rebanho_Cordeiro_geo['2024'].quantile(0.75)
limite_superior = Rebanho_Cordeiro_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_Cordeiro = (
    ggplot(Rebanho_Cordeiro_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Efetivo de Rebanho'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Rebanho_Cordeiro_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36.3, xmax=-37.667, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-36, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36.3, xmax=-37.667, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-36, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Rebanho de Cordeiro {Ano}')
)

mapa_Cordeiro

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Defina os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -5, 5
Rebanho_Cordeiro_geo = Rebanho_Cordeiro_geo.copy()
Rebanho_Cordeiro_geo['Indicador_participação_trunc'] = Rebanho_Cordeiro_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_Pescado = (
    ggplot(Rebanho_Cordeiro_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Rebanho_Cordeiro_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação do rebanho de Cordeiro {Ano}')
)

mapa_Pescado

# ---

# @title
# Juntar a tabela da Rota do Açaí com o GeoDataFrame de municípios
Vlr_Prod_Açaí_geo = brazil_map.merge(Vlr_Prod_Açaí, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

# Filter out rows where 'NOME_DO_POLO' is null
Vlr_Prod_Açaí_shape = Vlr_Prod_Açaí_geo[Vlr_Prod_Açaí_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Açaí via dissolve
Vlr_Prod_Açaí_shape['geometry'] = Vlr_Prod_Açaí_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Vlr_Prod_Açaí_shape = Vlr_Prod_Açaí_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Vlr_Prod_Açaí_shape = Vlr_Prod_Açaí_shape.reset_index()

Vlr_Prod_Açaí_shape = Vlr_Prod_Açaí_shape[['NOME_DO_POLO',	'geometry']]

Vlr_Prod_Açaí_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Vlr_Prod_Açaí_geo = Vlr_Prod_Açaí_geo.copy()

limite_inferior = Vlr_Prod_Açaí_geo['2024'].min()
q75 = Vlr_Prod_Açaí_geo['2024'].quantile(0.75)
limite_superior = Vlr_Prod_Açaí_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_Açaí = (
    ggplot(Vlr_Prod_Açaí_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor da Produção\n(R$ mil)'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Açaí_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Valor da produção de Açaí {Ano}')
)

mapa_Açaí

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Defina os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -5, 5
Vlr_Prod_Açaí_geo = Vlr_Prod_Açaí_geo.copy()
Vlr_Prod_Açaí_geo['Indicador_participação_trunc'] = Vlr_Prod_Açaí_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_Açaí = (
    ggplot(Vlr_Prod_Açaí_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Açaí_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação da produção de Açaí {Ano}')
)

mapa_Açaí

# ---

# @title
# Juntar a tabela da Rota do Cacau com o GeoDataFrame de municípios
Vlr_Prod_Cacau_geo = brazil_map.merge(Vlr_Prod_Cacau, left_on='CD_MUN', right_on='COD_IBGE', how='inner')

# Filter out rows where 'NOME_DO_POLO' is null
Vlr_Prod_Cacau_shape = Vlr_Prod_Cacau_geo[Vlr_Prod_Cacau_geo['NOME_DO_POLO'].notna()]

# ---

# @title
# Criar Geometria da Rota do Cacau via dissolve
Vlr_Prod_Cacau_shape['geometry'] = Vlr_Prod_Cacau_shape.geometry.buffer(0)

# Dissolve o GeoDataFrame pela coluna 'Agreg_tipologia'
Vlr_Prod_Cacau_shape = Vlr_Prod_Cacau_shape.dissolve(by='NOME_DO_POLO')

# Exibir o resultado
Vlr_Prod_Cacau_shape = Vlr_Prod_Cacau_shape.reset_index()

Vlr_Prod_Cacau_shape = Vlr_Prod_Cacau_shape[['NOME_DO_POLO',	'geometry']]

Vlr_Prod_Cacau_shape

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Definir os limites
Vlr_Prod_Cacau_geo = Vlr_Prod_Cacau_geo.copy()

limite_inferior = Vlr_Prod_Cacau_geo['2024'].min()
q75 = Vlr_Prod_Cacau_geo['2024'].quantile(0.75)
limite_superior = Vlr_Prod_Cacau_geo['2024'].max()

colors = ['white', '#0081a7', '#0081a7']
breaks = [limite_inferior, q75, limite_superior]

# Criar o mapa
mapa_Cacau = (
    ggplot(Vlr_Prod_Cacau_geo, aes(fill='2024'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor da Produção\n(R$ mil)'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Cacau_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Valor da produção de Cacau {Ano}')
)

mapa_Cacau

# ---

# @title
from plotnine import *
import numpy as np
import pandas as pd
import geopandas as gpd

# Defina os limites e variável truncada (mantém igual)
limite_inferior, limite_superior = -2, 2
Vlr_Prod_Cacau_geo = Vlr_Prod_Cacau_geo.copy()
Vlr_Prod_Cacau_geo['Indicador_participação_trunc'] = Vlr_Prod_Cacau_geo['Indicador_participação'].clip(limite_inferior, limite_superior)

colors = ['#f07167', 'white', '#0081a7']
breaks = [limite_inferior, 0, limite_superior]

# Criar o mapa
mapa_Cacau = (
    ggplot(Vlr_Prod_Cacau_geo, aes(fill='Indicador_participação_trunc'))
    + geom_map(color='lightgray', size=0.0)
    + scale_fill_gradientn(
        colors=colors,
        values=np.linspace(0, 1, len(colors)),
        breaks=breaks,
        limits=(limite_inferior, limite_superior),
        name='Valor do indicador'
    )
    + geom_map(
        data=uf_map,
        mapping=aes(),
        fill='none',
        color='gray',
        size=0.3
    )
    + geom_map(
        data=Vlr_Prod_Cacau_shape,
        mapping=aes(),
        fill='none',
        color='black',
        size=0.5
    )
    # 🔲 Retângulo sobre o mapa (em coordenadas de dados)
    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-22.825, ymax=-22.045),
        fill='none',
        color='gray',
        size=0.3
    )
    + annotate('text', x=-35.7, y=-22.435,
           label='Estados', size=10, ha='left', va='center')

    + geom_rect(
        aes(xmin=-36, xmax=-37.367, ymin=-21.825, ymax=-21.045),
        fill='none',
        color='black',
        size=0.5
    )
    + annotate('text', x=-35.7, y=-21.435,
           label='Polos', size=10, ha='left', va='center')
    # 🔒 Mantém a proporção x/y fixa (sem distorcer)
    + coord_fixed()
    + theme_void()
    + theme(
        plot_background=element_rect(fill='white'),
        panel_background=element_rect(fill='white'),
        plot_title=element_text(
            size=18,
            face='bold',
            hjust=0.5,
            backgroundcolor='white'
        ),
        legend_title=element_text(face='bold', size=10),
        legend_text=element_text(size=10),
        legend_position=(0.9, 0.1),
        legend_background=element_blank(),
        figure_size=(12, 10)
    )
    + labs(title=f'Indicador de participação da produção de Cacau {Ano}')
)

mapa_Cacau

# ---

