import marimo

__generated_with = "0.23.2"
app = marimo.App(width="medium", app_title="Indicador do Rotas")


@app.cell
def _():
    import marimo as mo
    import sys
    import pandas as pd
    import numpy as np
    import requests
    import os
    import zipfile
    import io

    # Geospatial imports guarded against WASM
    if sys.platform != "emscripten":
        import geopandas as gpd
        import geobr
        from plotnine import ggplot, aes, geom_map, geom_rect, scale_fill_gradientn, scale_color_manual, annotate, coord_fixed, theme_void, theme, element_rect, element_text, element_blank, labs
    else:
        gpd = geobr = ggplot = aes = geom_map = geom_rect = scale_fill_gradientn = scale_color_manual = annotate = coord_fixed = theme_void = theme = element_rect = element_text = element_blank = labs = None
    return (
        aes,
        coord_fixed,
        element_blank,
        element_rect,
        element_text,
        geobr,
        geom_map,
        ggplot,
        gpd,
        io,
        labs,
        mo,
        np,
        os,
        pd,
        requests,
        scale_color_manual,
        scale_fill_gradientn,
        sys,
        theme,
        theme_void,
        zipfile,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # **Apuração do Indicador do PPA do Rotas**

    Foram apurados os indicadores de seis Rotas, incluindo os indicadores para cada Polo.

    A Fonte de dados são as Pesquisas do IBGE:
    - Pesquisa da Pecuária Municipal - PPM
    - Produção Agrícola Municipal - PAM
    - Produção da Extração Vegetal e da Silvicultura - PEVS

    ```
    * O código requisita os dados direto da API do SIDRA do IBGE
    * Observe que o indicador do ano de referência só fica disponível a partir de setembro no ano seguinte.

    ```
    ## Indicador de ganho ou perda de participação da Rota
    ---

    **Fórmula de cálculo:**

    $$
    I_pR = \frac{\Delta R_p - \Delta T_p}{|\Delta T_p|}
    $$

    Onde:

    - $I_pR$ Representa o Indicador de ganho ou perda de participação da Rota/Polo/município;
    - ${\Delta R_p}$ Representa a variação da produção do total de municípios da Rota em relação ao produto da Rota no período; e
    - ${\Delta T_p}$ Representa a variação da produção do total de municípios em relação ao produto da Rota no período.

    **Interpretação:**

    Se **maior que 0**: O crescimento da produção foi maior nos municípios das Rotas
    (ou caiu menos que nos demais)

    Se **menor que 0**: O crescimento da produção foi menor nos municípios das Rotas (ou caiu mais que nos demais)

    O indicador pode ser decomposto para cada município e para cada Polo

    ---
    """)
    return


@app.cell
def _(mo):
    ano_input = mo.ui.dropdown(options=[str(y) for y in range(2000, 2031)], value="2024", label="Ano de Referência:")
    rota_input = mo.ui.dropdown(
        options=["Leite", "Mel", "Pescado", "Cordeiro", "Açaí", "Cacau", "Todas as Rotas (Média PPA e PEI)"],
        value="Leite",
        label="Selecione a Rota:"
    )
    return ano_input, rota_input


@app.cell
def _(ano_input, mo, rota_input):
    ui_controls = mo.hstack([ano_input, rota_input], justify="start", align="center", gap=1)
    return (ui_controls,)


@app.cell
def _(mo, ui_controls):
    mo.vstack([
        mo.md("## Filtros da Consulta"),
        ui_controls
    ])
    return


@app.cell
def _(ano_input, geobr, gpd, io, mo, np, os, pd, requests, sys, zipfile):
    ano_val = str(ano_input.value)
    ano_0_val = str(int(ano_val) - 1)
    period = f"{ano_0_val}-{ano_val}"

    if sys.platform == "emscripten":
        from pyodide.http import open_url
        import js
        # O código roda dentro de um Web Worker, então js.location.href
        # aponta para o script do worker (ex: .../assets/worker-xxx.js),
        # não para a URL da página. Precisamos subir para a raiz do site.
        worker_href = str(js.location.href)
        if '/assets/' in worker_href:
            base_url = worker_href.split('/assets/')[0] + '/'
        else:
            base_url = worker_href.rsplit('/', 1)[0] + '/'
        csv_url = base_url + 'classificacao_municipios_SDR.csv'
        try:
            classificacoes = pd.read_csv(open_url(csv_url), dtype=str)
        except Exception as e:
            raise Exception(f"Erro ao carregar CSV no WASM ({csv_url}): {e}")
    else:
        classificacoes = pd.read_csv('classificacao_municipios_SDR.csv', dtype=str)

    configs = {
        "Leite": {'table_code': '74', 'variable': '215', 'classifications': {"80": "2682"}, 'rota_col': 'R_LEITE'},
        "Mel": {'table_code': '74', 'variable': '215', 'classifications': {"80": "2687"}, 'rota_col': 'R_MEL'},
        "Pescado": {'table_code': '3940', 'variable': '215', 'classifications': {"654": "0"}, 'rota_col': 'R_PESCADO'},
        "Cordeiro": {'table_code': '3939', 'variable': '105', 'classifications': {"79": "2681,2677"}, 'rota_col': 'R_CORDEIRO'},
        "Cacau": {'table_code': '1613', 'variable': '215', 'classifications': {"82": "2722"}, 'rota_col': 'R_CACAU'},
        "Açaí": {'rota_col': 'R_ACAI'}
    }

    def fetch_sidra_data(table_code, variable, classifications, period_str):
        try:
            url = f"https://apisidra.ibge.gov.br/values/t/{table_code}/n6/all/v/{variable}/p/{period_str}"
            if classifications:
                for c, v in classifications.items():
                    url += f"/c{c}/{v}"

            response = requests.get(url, timeout=120)
            if response.status_code != 200:
                print(f"Erro SIDRA HTTP {response.status_code}")
                return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])

            data = response.json()
            if not data or len(data) < 2:
                return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])

            df = pd.DataFrame(data)
            if df.empty:
                return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])

            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            df = df[['Município (Código)', 'Valor', 'Ano']]
            df = df.replace(['-',"..."], np.nan)
            df['Valor'] = pd.to_numeric(df['Valor'])
            df = df.rename(columns={'Município (Código)': 'COD_IBGE'})
            df_pivot = df.pivot_table(index='COD_IBGE', columns='Ano', values='Valor', aggfunc='sum').reset_index()
            df_pivot.columns.name = None
            return df_pivot
        except Exception as e:
            print(f"Erro ao buscar dados SIDRA: {e}")
            return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])

    def fetch_acai(period_str):
        try:
            df1 = fetch_sidra_data('1613', '215', {"82": "45981"}, period_str)
            df2 = fetch_sidra_data('289', '145', {"193": "3403"}, period_str)
            df1_melt = df1.melt(id_vars='COD_IBGE', var_name='Ano', value_name='Valor') if not df1.empty else pd.DataFrame()
            df2_melt = df2.melt(id_vars='COD_IBGE', var_name='Ano', value_name='Valor') if not df2.empty else pd.DataFrame()
            df_concat = pd.concat([df1_melt, df2_melt], ignore_index=True)
            if not df_concat.empty:
                df_pivot = df_concat.pivot_table(index='COD_IBGE', columns='Ano', values='Valor', aggfunc='sum').reset_index()
                df_pivot.columns.name = None
                return df_pivot
            return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])
        except Exception as e:
            print(f"Erro no Açai: {e}")
            return pd.DataFrame(columns=['COD_IBGE', ano_0_val, ano_val])

    def calc_indicadores(df, rota_col):
        if df.empty or ano_0_val not in df.columns or ano_val not in df.columns:
            return None, None, None, None

        df_rota = classificacoes[['COD_MUNIC_IBGE', rota_col]].rename(columns={'COD_MUNIC_IBGE': 'COD_IBGE', rota_col: 'NOME_DO_POLO'})
        df = pd.merge(df, df_rota, on='COD_IBGE', how='left')
        df['regiao'] = df['COD_IBGE'].astype(str).str[0]

        Vlr_Ano0 = df[ano_0_val].sum()
        Vlr_Ano = df[ano_val].sum()
        Var_Total = (Vlr_Ano / Vlr_Ano0) - 1 if Vlr_Ano0 != 0 else np.nan

        df_grouped = df.groupby(['regiao', 'NOME_DO_POLO'])[[ano_0_val, ano_val]].sum().reset_index()

        Vlr_Rota_Ano0 = df_grouped[ano_0_val].sum()
        Vlr_Rota_Ano = df_grouped[ano_val].sum()

        Var_Rota = (Vlr_Rota_Ano / Vlr_Rota_Ano0) - 1 if Vlr_Rota_Ano0 != 0 else np.nan

        Part_Rota_Ano0 = Vlr_Rota_Ano0 / Vlr_Ano0 if Vlr_Ano0 != 0 else 0
        Part_Rota_Ano = Vlr_Rota_Ano / Vlr_Ano if Vlr_Ano != 0 else 0

        Ind_Participacao = (Var_Rota - Var_Total) / abs(Var_Total) if Var_Total != 0 and not np.isnan(Var_Total) else np.nan

        df_grouped['Part%_Ano_0'] = (df_grouped[ano_0_val] / Vlr_Ano0) * 100 if Vlr_Ano0 != 0 else 0
        df_grouped['Part%_Ano'] = (df_grouped[ano_val] / Vlr_Ano) * 100 if Vlr_Ano != 0 else 0
        df_grouped['Variação'] = (df_grouped[ano_val] / df_grouped[ano_0_val] - 1)
        df_grouped['Indicador_participação'] = (df_grouped['Variação'] - Var_Total) / abs(Var_Total) if Var_Total != 0 and not np.isnan(Var_Total) else np.nan

        df_grouped_reg_totais = df.groupby('regiao')[[ano_0_val, ano_val]].sum().reset_index()
        df_sum_by_regiao = df_grouped.groupby('regiao')[[ano_0_val, ano_val]].sum().reset_index()

        df_sum_by_regiao = df_sum_by_regiao.merge(df_grouped_reg_totais, on='regiao', how='left', suffixes=('_rota', '_total'))

        col_ano0_rota = f"{ano_0_val}_rota"
        col_ano_rota = f"{ano_val}_rota"
        col_ano0_total = f"{ano_0_val}_total"
        col_ano_total = f"{ano_val}_total"

        df_sum_by_regiao['var_rota'] = (df_sum_by_regiao[col_ano_rota] / df_sum_by_regiao[col_ano0_rota]) - 1
        df_sum_by_regiao['var_total'] = (df_sum_by_regiao[col_ano_total] / df_sum_by_regiao[col_ano0_total]) - 1
        df_sum_by_regiao['Indicador_participação'] = (df_sum_by_regiao['var_rota'] - df_sum_by_regiao['var_total']) / abs(df_sum_by_regiao['var_total'])

        df['Part%_Ano_0'] = (df[ano_0_val] / Vlr_Ano0) * 100 if Vlr_Ano0 != 0 else 0
        df['Part%_Ano'] = (df[ano_val] / Vlr_Ano) * 100 if Vlr_Ano != 0 else 0
        df['Variação'] = (df[ano_val] / df[ano_0_val] - 1)
        df['Indicador_participação'] = (df['Variação'] - Var_Total) / abs(Var_Total) if Var_Total != 0 and not np.isnan(Var_Total) else np.nan

        return {
            'Vlr_Ano0': Vlr_Ano0, 'Vlr_Ano': Vlr_Ano, 'Var_Total': Var_Total,
            'Vlr_Rota_Ano0': Vlr_Rota_Ano0, 'Vlr_Rota_Ano': Vlr_Rota_Ano, 'Var_Rota': Var_Rota,
            'Part_Rota_Ano0': Part_Rota_Ano0, 'Part_Rota_Ano': Part_Rota_Ano,
            'Ind_Participacao': Ind_Participacao
        }, df_grouped, df_sum_by_regiao, df

    @mo.cache
    def load_base_maps(ano_str):
        uf_map = geobr.read_state(year=2000)
        directory = './shapefiles'
        os.makedirs(directory, exist_ok=True)
        shape_path = f'./shapefiles/BR_Municipios_{ano_str}.shp'
        if not os.path.exists(shape_path):
            url = f"https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_{ano_str}/Brasil/BR_Municipios_{ano_str}.zip"
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    zip_ref.extractall(directory)
            else:
                return uf_map, None
        brazil_map = gpd.read_file(shape_path)
        return uf_map, brazil_map

    return (
        ano_0_val,
        ano_val,
        calc_indicadores,
        configs,
        fetch_acai,
        fetch_sidra_data,
        load_base_maps,
        period,
    )


@app.cell
def _(
    aes,
    ano_0_val,
    ano_val,
    calc_indicadores,
    configs,
    coord_fixed,
    element_blank,
    element_rect,
    element_text,
    fetch_acai,
    fetch_sidra_data,
    geom_map,
    ggplot,
    labs,
    load_base_maps,
    mo,
    np,
    pd,
    period,
    rota_input,
    scale_color_manual,
    scale_fill_gradientn,
    sys,
    theme,
    theme_void,
):
    with mo.status.spinner("Buscando dados no SIDRA e calculando indicadores...") as _spinner:
        rotas_processadas = {}
        rotas_a_processar = ["Leite", "Mel", "Pescado", "Cordeiro", "Açaí", "Cacau"] if rota_input.value == "Todas as Rotas (Média PPA e PEI)" else [rota_input.value]

        for r_nome in rotas_a_processar:
            _spinner.update(f"Buscando dados no SIDRA para a Rota do {r_nome}...")
            if r_nome == "Açaí":
                df_r = fetch_acai(period)
                rota_col = 'R_ACAI'
            else:
                cfg = configs[r_nome]
                df_r = fetch_sidra_data(cfg['table_code'], cfg['variable'], cfg['classifications'], period)
                rota_col = cfg['rota_col']

            res, df_grp, df_reg, df_mun = calc_indicadores(df_r, rota_col)
            rotas_processadas[r_nome] = {'res': res, 'df_grp': df_grp, 'df_reg': df_reg, 'df_mun': df_mun}

        # Carregar mapas se não for Todas as Rotas
        uf_map, brazil_map = None, None
        if rota_input.value != "Todas as Rotas (Média PPA e PEI)" and sys.platform != "emscripten":
            _spinner.update("Baixando e carregando malha geográfica do IBGE...")
            uf_map, brazil_map = load_base_maps(ano_val)

    _output_blocks = []
    if rota_input.value == "Todas as Rotas (Média PPA e PEI)":
        indicadores = [rotas_processadas[r]['res']['Ind_Participacao'] for r in rotas_processadas if rotas_processadas[r]['res'] and not np.isnan(rotas_processadas[r]['res']['Ind_Participacao'])]
        media_ppa = np.mean(indicadores) if indicadores else np.nan

        regioes_lista = []
        for r in rotas_processadas:
            if rotas_processadas[r]['df_reg'] is not None:
                df_tmp = rotas_processadas[r]['df_reg'][['regiao', 'Indicador_participação']].copy()
                df_tmp['Rota'] = r
                regioes_lista.append(df_tmp)

        if regioes_lista:
            df_todas_regioes = pd.concat(regioes_lista)
            df_media_regional = df_todas_regioes.groupby('regiao')['Indicador_participação'].mean().reset_index()
            df_media_regional.rename(columns={'Indicador_participação': 'Média do Indicador de Participação'}, inplace=True)
            reg_map = {'1': 'Norte', '2': 'Nordeste', '3': 'Sudeste', '4': 'Sul', '5': 'Centro-Oeste'}
            df_media_regional['regiao_nome'] = df_media_regional['regiao'].map(reg_map)
            df_media_regional = df_media_regional[['regiao', 'regiao_nome', 'Média do Indicador de Participação']]
        else:
            df_media_regional = pd.DataFrame()

        _output_blocks.append(mo.md(f"## Média do Indicador de Ganho/Perda de Participação (PPA e PEI) para {ano_val}"))

        _output_blocks.append(
            mo.stat(
                label="Média Global",
                value=f"{media_ppa:.4f}",
                bordered=True
            )
        )

        if not df_media_regional.empty:
            _output_blocks.append(mo.md("### Média do Indicador de Participação por Região"))
            _output_blocks.append(mo.ui.table(df_media_regional, selection=None))

        _output_blocks.append(mo.md("### Indicador de Participação por Rota"))
        for r in rotas_processadas:
            res = rotas_processadas[r]['res']
            if res:
                _output_blocks.append(mo.md(f"- **{r}**: `{res['Ind_Participacao']:.4f}`"))

    else:
        r = rota_input.value
        res = rotas_processadas[r]['res']
        df_grp = rotas_processadas[r]['df_grp']
        df_reg = rotas_processadas[r]['df_reg']
        df_mun = rotas_processadas[r]['df_mun']

        if res:
            _output_blocks.append(mo.md(f"## Resultados para Rota do {r}"))

            stats = mo.hstack([
                mo.stat("Var. Municípios", f"{res['Var_Total']*100:.2f}%", bordered=True),
                mo.stat("Var. Rota", f"{res['Var_Rota']*100:.2f}%", bordered=True),
                mo.stat("Indicador de Ganho/Perda", f"{res['Ind_Participacao']:.4f}", bordered=True)
            ])
            _output_blocks.append(stats)

            _output_blocks.append(mo.md(
                "- **Valor da produção de todos os municípios em " + ano_0_val + "**: " + f"{res['Vlr_Ano0']:,.2f}\n" +
                "- **Valor da produção de todos os municípios em " + ano_val + "**: " + f"{res['Vlr_Ano']:,.2f}\n" +
                "- **Valor da produção da Rota em " + ano_0_val + "**: " + f"{res['Vlr_Rota_Ano0']:,.2f} ({res['Part_Rota_Ano0']*100:.2f}% do nacional)\n" +
                "- **Valor da produção da Rota em " + ano_val + "**: " + f"{res['Vlr_Rota_Ano']:,.2f} ({res['Part_Rota_Ano']*100:.2f}% do nacional)"
            ))

            _output_blocks.append(mo.md("### Resumo por Polo"))
            _output_blocks.append(mo.ui.table(df_grp, selection=None))

            _output_blocks.append(mo.md("### Resumo Regional"))
            df_reg_copy = df_reg.copy()
            reg_map = {'1': 'Norte', '2': 'Nordeste', '3': 'Sudeste', '4': 'Sul', '5': 'Centro-Oeste'}
            df_reg_copy['regiao_nome'] = df_reg_copy['regiao'].map(reg_map)
            cols = list(df_reg_copy.columns)
            cols.insert(1, cols.pop(cols.index('regiao_nome')))
            df_reg_copy = df_reg_copy[cols]
            _output_blocks.append(mo.ui.table(df_reg_copy, selection=None))

            # Geração dos Mapas
            if sys.platform == "emscripten":
                _output_blocks.append(mo.md("---"))
                _output_blocks.append(mo.md("### Mapas Geográficos"))
                _output_blocks.append(mo.callout("A geração de mapas espaciais está desabilitada na versão Web para garantir alta performance e navegação instantânea. Os dados completos continuam disponíveis nas tabelas acima.", kind="info"))
            elif brazil_map is not None and not df_mun.empty:
                _output_blocks.append(mo.md("---"))
                _output_blocks.append(mo.md("### Mapas Geográficos"))

                with mo.status.spinner("Renderizando mapas espaciais (isso pode levar alguns instantes)..."):
                    df_geo = brazil_map.merge(df_mun, left_on='CD_MUN', right_on='COD_IBGE', how='inner')
                    df_shape = df_geo[df_geo['NOME_DO_POLO'].notna()].copy()
                    df_shape['geometry'] = df_shape.geometry.buffer(0)
                    df_shape = df_shape.dissolve(by='NOME_DO_POLO').reset_index()
                    df_shape = df_shape[['NOME_DO_POLO', 'geometry']]

                    # Mapa 1: Valor
                    limite_inferior = df_geo[ano_val].min()
                    q75 = df_geo[ano_val].quantile(0.75)
                    limite_superior = df_geo[ano_val].max()
                    colors_vlr = ['white', '#0081a7', '#0081a7']
                    breaks_vlr = [limite_inferior, q75, limite_superior]

                    mapa_valor = (
                        ggplot(df_geo, aes(fill=ano_val))
                        + geom_map(color='lightgray', size=0.0)
                        + geom_map(data=uf_map, mapping=aes(color='"Estados"'), fill='none', size=0.3)
                        + geom_map(data=df_shape, mapping=aes(color='"Polos"'), fill='none', size=0.5)
                        + scale_fill_gradientn(
                            colors=colors_vlr, breaks=breaks_vlr, limits=(limite_inferior, limite_superior),
                            name='Valor da Produção\n(R$ mil)'
                        )
                        + scale_color_manual(values={'Estados': 'gray', 'Polos': 'black'}, name='')
                        + coord_fixed()
                        + theme_void()
                        + theme(
                            plot_background=element_rect(fill='white'),
                            panel_background=element_rect(fill='white'),
                            plot_title=element_text(size=18, face='bold', hjust=0.5, backgroundcolor='white'),
                            legend_title=element_text(face='bold', size=10),
                            legend_text=element_text(size=10),
                            legend_position='right',
                            legend_box='vertical',
                            legend_background=element_blank(),
                            figure_size=(10, 8)
                        )
                        + labs(title=f'Valor da produção de {r} ({ano_val})', color='')
                    )

                    # Mapa 2: Indicador
                    df_geo['Indicador_participação_trunc'] = df_geo['Indicador_participação'].clip(-5, 5)
                    colors_ind = ['#f07167', 'white', '#0081a7']
                    breaks_ind = [-5, 0, 5]

                    mapa_ind = (
                        ggplot(df_geo, aes(fill='Indicador_participação_trunc'))
                        + geom_map(color='lightgray', size=0.0)
                        + geom_map(data=uf_map, mapping=aes(color='"Estados"'), fill='none', size=0.3)
                        + geom_map(data=df_shape, mapping=aes(color='"Polos"'), fill='none', size=0.5)
                        + scale_fill_gradientn(
                            colors=colors_ind, breaks=breaks_ind, limits=(-5, 5),
                            name='Valor do indicador'
                        )
                        + scale_color_manual(values={'Estados': 'gray', 'Polos': 'black'}, name='')
                        + coord_fixed()
                        + theme_void()
                        + theme(
                            plot_background=element_rect(fill='white'),
                            panel_background=element_rect(fill='white'),
                            plot_title=element_text(size=18, face='bold', hjust=0.5, backgroundcolor='white'),
                            legend_title=element_text(face='bold', size=10),
                            legend_text=element_text(size=10),
                            legend_position='right',
                            legend_box='vertical',
                            legend_background=element_blank(),
                            figure_size=(10, 8)
                        )
                        + labs(title=f'Indicador de participação da produção de {r} ({ano_val})', color='')
                    )

                _output_blocks.append(mo.vstack([mapa_valor, mapa_ind]))

        else:
            _output_blocks.append(mo.md("Não foi possível calcular os indicadores para a rota selecionada."))

    final_output = mo.vstack(_output_blocks)
    return (final_output,)


@app.cell
def _(final_output):
    final_output
    return


if __name__ == "__main__":
    app.run()
