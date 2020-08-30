import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pydeck as pdk
import plotly.express as px
import geopandas
from matplotlib import cm
from matplotlib.colors import ListedColormap


## FUNCTIONS ###################################################################################################################################

#load data
@st.cache(allow_output_mutation=True)
def load_data(option):

    if option == 'mes':
        report = pd.read_csv('data_map2.csv')

        return report

    elif option == 'fornecedor':
        df = pd.read_csv('distribuicao_respiradores.csv', delimiter = ';')
        df = df[df['DATA DE ENTREGA'] != 'AGUARDANDO O MS']
        df['DATA DE ENTREGA'] = df['DATA DE ENTREGA'].str.replace('/', '-', regex=False)
        df['VALOR'] = df['VALOR'].str.replace(',', '.', regex=False).astype(float)
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst = True)
        df['FORNECEDOR'] = df['FORNECEDOR'].str.upper()

        gb = df.groupby('FORNECEDOR')

        qt_tot = []
        vl_tot = []
        for i in range(len(df)):
            st = gb.get_group(df['FORNECEDOR'].iloc[i])
            qt_tot.append(st.agg({'QUANTIDADE': ['sum']}).QUANTIDADE.values[0])
            vl_tot.append(st.agg({'VALOR': ['sum']}).VALOR.values[0])

        df['QT_TOT'] = qt_tot
        df['VL_TOT'] = vl_tot
        df['PREÇO_MEDIO'] = (np.array(vl_tot)/np.array(qt_tot))

        report = df.copy().drop(columns = ['ESTADO/MUNICIPIO','DATA','DESTINO','TIPO','DESTINATARIO','DATA DE ENTREGA','UF'])
        report2 = report.drop(columns = ['QUANTIDADE','VALOR']).drop_duplicates().round(1)

        return report2

    elif option == 'pedidoTot':
        report_month = pd.read_csv('data_map2.csv')
        gb = report_month.groupby('DESTINO')

        qt_tot = []
        vl_tot = []
        for i in range(len(report_month)):
            st = gb.get_group(report_month['DESTINO'].iloc[i])
            qt_tot.append(st.agg({'QT_MES': ['sum']}).QT_MES.values[0])
            vl_tot.append(st.agg({'VL_MES': ['sum']}).VL_MES.values[0])

        report_month['QT_TOT'] = qt_tot
        report_month['VL_TOT'] = vl_tot
        report_month['PREÇO_MEDIO'] = (np.array(vl_tot)/np.array(qt_tot))

        report = report_month.copy().drop(columns = ['QT_MES','VL_MES','MES','longitude','latitude'])
        report2 = report.sort_values(by='PREÇO_MEDIO', ascending=True)
        report3 = report2.round(1)
        report3.drop_duplicates(inplace= True)
        
        return report3
    
    elif option == 'anomalia':
        df = pd.read_csv('distribuicao_respiradores.csv', delimiter = ';')
        df = df[df['DATA DE ENTREGA'] != 'AGUARDANDO O MS']
        df['DATA DE ENTREGA'] = df['DATA DE ENTREGA'].str.replace('/', '-', regex=False)
        df['VALOR'] = df['VALOR'].str.replace(',', '.', regex=False).astype(float)
        df['DATA'] = pd.to_datetime(df['DATA'], dayfirst = True)
        df['FORNECEDOR'] = df['FORNECEDOR'].str.upper()


        reais = np.array(df['VALOR'].values)
        pedidos = np.array(df['QUANTIDADE'].values)


        df['PREÇO_MEDIO_REG'] = reais/pedidos

        caros = df[df['PREÇO_MEDIO_REG'] > 80000]
        baratos = df[df['PREÇO_MEDIO_REG'] < 20000]

        return caros, baratos
    
    elif option == 'respInit':

        hab = pd.read_csv('resps.csv').drop(columns=['Unnamed: 0'])
        hab['Respiradores/Pop'] = np.array(hab['Respiradores'].values)/(np.array(hab['População'].values)/100000)
        hab['Respiradores/Pop'] = hab['Respiradores/Pop'].apply(np.floor).astype(int)

        return hab

    elif option == 'respMes':

        hab = pd.read_csv('resps.csv').drop(columns=['Unnamed: 0'])
        return hab

    elif option == 'map':
        df = pd.read_csv('dados_respiradores2.csv')
        return df
    else:
        print('Wrong Option!')
        return 'Wrong Option!'


def plot_fornecedores():
    report2 = load_data('fornecedor')

    fig2 = px.bar(report2, y='FORNECEDOR', x='PREÇO_MEDIO',
                hover_data=['QT_TOT','VL_TOT'],color='PREÇO_MEDIO',
                labels={'QT_TOT':'Qnt. de respiradores','VL_TOT':'Valor total dos respiradores','PREÇO_MEDIO':'Valor Médio(R$)', 'FORNECEDOR':'Fornecedor'},
                height = 800, width = 800,
                color_continuous_scale= px.colors.sequential.Teal, title = 'Preço Médio por fornecedor'
                )

    fig2.update(layout_coloraxis_showscale=False)
    fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    #fig2.update_xaxes(tickangle=45)
    fig2.update_yaxes(visible=True)
    st.plotly_chart(fig2, use_container_width=True)


def plot_qnt_mes(mes):

    month_dict = {4 : 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto'}

    map_df = load_data('mes')

    mes_selec = mes

    df_month = map_df[map_df['MES'] == mes_selec]
    fig_qnt_mes = px.bar(df_month, x='DESTINO', y='QT_MES',
            hover_data=['VL_MES'],color='QT_MES',
            labels={'QT_MES':'Qnt. de respiradores','VL_MES':'Valor Gasto em Reais (R$)', 'DESTINO':'Estado'},
            height = 400, width = 1000,
            color_continuous_scale= px.colors.sequential.Teal, title = f'Pedido de respiradores em {month_dict[mes_selec]}'
            )

    fig_qnt_mes.update(layout_coloraxis_showscale=False)
    fig_qnt_mes.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_qnt_mes.update_xaxes(tickangle=45)
    fig_qnt_mes.update_yaxes(visible=True)

    st.plotly_chart(fig_qnt_mes, use_container_width=True)


def plot_val_mes(mes):

    month_dict = {4 : 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto'}

    map_df = load_data('mes')

    mes_selecionado = mes

    df_month = map_df[map_df['MES'] == mes_selecionado]
    fig_val_mes = px.bar(df_month, x='DESTINO', y='VL_MES',
            hover_data=['QT_MES'],color='VL_MES',
            labels={'QT_MES':'Qnt. de respiradores','VL_MES':'Valor Gasto em Reais (R$)', 'DESTINO':'Estado'},
            height = 400, width = 1000,
            color_continuous_scale= px.colors.sequential.Teal, title = f'Valor gasto com respiradores em {month_dict[mes_selecionado]}'
            )

    fig_val_mes.update(layout_coloraxis_showscale=False)
    fig_val_mes.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig_val_mes.update_xaxes(tickangle=45)
    fig_val_mes.update_yaxes(visible=True)

    st.plotly_chart(fig_val_mes, use_container_width=True)


def plot_val_tot():

    report3 = load_data('pedidoTot')

    fig = px.bar(report3, x='DESTINO', y='PREÇO_MEDIO',
                    hover_data=['QT_TOT','VL_TOT'],color='PREÇO_MEDIO',
                    labels={'QT_TOT':'Qnt. de respiradores comprados','VL_TOT':'Valor total gasto com respiradores','PREÇO_MEDIO':'Valor Médio em reais (R$)', 'DESTINO':'Estado'},
                    height = 400, width = 1000,
                    color_continuous_scale= px.colors.sequential.Teal, title = 'Valor médio gasto com respirador '
                    )

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update(layout_coloraxis_showscale=False)
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(visible=True)
    st.plotly_chart(fig, use_container_width=True)

def show_anomalias():

    caros, baratos = load_data('anomalia')
    if st.checkbox('Ver respiradores que foram comprados por um valor alto'):
        st.write(caros)
    if st.checkbox('Ver respiradores que foram comprados por um valor baixo'):
        st.write(baratos)


def plot_resp_mes(month):
    hab = load_data('respMes')


    month_dict = {4 : 'Abril', 5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto'}
    name = f'{month_dict[month]}/Pop'

    hab[name] = np.array(hab[month_dict[month]].values)/(np.array(hab['População'].values)/100000)
    hab[name] = hab[name].apply(np.floor).astype(int)

    #df_month = report_month[report_month['MES'] == month]

    figmes = px.bar(hab, x='Estado', y=name,
            hover_data=['População','Respiradores'],color=name,
            labels={'População':'Número de Habitantes','Respiradores':'Número de Respiradores',name:'Respiradores/100 mil habitantes'},
            height = 400, width = 1000,
            color_continuous_scale= px.colors.sequential.Teal,
            title = f'Quantidade de respiradores em {month_dict[month]}'
        )

    figmes.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    figmes.update(layout_coloraxis_showscale=False)
    figmes.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    figmes.update_xaxes(tickangle=45)
    figmes.update_yaxes(visible=True)
    st.plotly_chart(figmes, use_container_width=True)

def plot_resp_tot():

    hab = load_data('respInit')


    figtot = px.bar(hab, x='Estado', y='Respiradores/Pop',
             hover_data=['População','Respiradores'],color='Respiradores/Pop',
             labels={'População':'Número de Habitantes','Respiradores':'Número de Respiradores','Respiradores/Pop':'Respiradores/100 mil habitantes'},
             height = 400, width = 1000,
             color_continuous_scale= px.colors.sequential.Teal,
             title = f'Quantidade de respiradores antes da pandemia'
            )

    figtot.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    figtot.update(layout_coloraxis_showscale=False)
    figtot.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    figtot.update_xaxes(tickangle=45)
    figtot.update_yaxes(visible=True)
    st.plotly_chart(figtot, use_container_width=True)

def selectMap(gdf, df, df_column_name, month = 0):
    val_list = []
    
    if(month == 0):
        for state in gdf['ESTADO']:
            val_list.append(df[df_column_name].loc[df['State'] == state].sum())
    else:
        for state in gdf['ESTADO']:
            if(len(df[df_column_name].loc[df['State'] == state].loc[df['Month'] == month].values) > 0):    
                val_list.append(df[df_column_name].loc[df['State'] == state].loc[df['Month'] == month].values[0])
            else:
                val_list.append(0)
        
    gdf[df_column_name] = val_list
    
    return gdf


def load_geodata(file_path):
    gdf = geopandas.read_file(file_path)

    return gdf

##########################################################################################################################################################################
# Dashboard

st.title("A Distribuição de respiradores no Brasil durante a Pandemia")
st.markdown("""

    
   ## Introdução e definição do problema aqui:

   Neste artigo iremos analisar a distribuição de respiradores no Brasil a fim de expor e comparar as estratégias de compras efetuadas por cada Estado.
    Assim, evidenciando aqueles que fizeram compras
   com melhor custo-benefício e que tiveram maior crescimento na quantidade de respiradores por 100 mil habitantes. Além disso,
    iremos comparar os preços oferecidos pelos fornecedores e destacar pedidos
   que tiveram um custo que distoante do padrão.

   Para essa análise, combinamos informações disponíveis em portais de dados abertos. Nosso objetivo é disponibilizar esses materiais de maneira clara e objetiva através de gráficos interativos para
   o público em geral.


    *Atualizado em: (30/08/2020).*
"""
)


st.header("Tipos de Análise")
st.markdown(
    """
    Aqui você pode selecionar que tipo de análise sobre a distribuição de respiradores você deseja visualizar. Basta escolher na caixa abaixo.
    """
)



analise_box = st.selectbox('Escolha:', ('Análise de Gasto Total','Análise de Fornecedores e Anomalias','Análise de Gasto Mensal'))

if analise_box == 'Análise de Gasto Total':

    st.markdown("""
        Na análise de gastos totais, verificamos como foram direcionados os recursos em determinado estado durante o período da pandemia,
         comparando a quantidade de respiradores antes da pandemia com a quantidade em no mês de agosto. Também analisamos o valor médio que cada Estado gastou por respirador, assim observando
         que Estados gastaram de maneira eficiente com respiradores, assim como os Estados que tiveram custos elevados demais para um pouco aumento na quantidade de respiradores por 100 mil habitantes,
         como por exemplo o Amazonas.
    """)

    plot_val_tot()

    plot_resp_tot()

    plot_resp_mes(8)

elif analise_box == 'Análise de Gasto Mensal':

    st.markdown("""
    Na análise de gastos mensais, verificamos a quantidade de pedidos de respiradores que cada Estado fez em determinado mês,
     o valor gasto com esses pedidos e quantidade total de respiradores em cada Estado.
    """)

    box = st.selectbox('Mês', ('Abril','Maio','Junho','Julho','Agosto'))
    month_dict = {'Abril':4, 'Maio':5, 'Junho':6, 'Julho':7, 'Agosto':8}
    mes = month_dict[box]
    selected_month = mes

    plot_qnt_mes(mes)
    plot_val_mes(mes)
    plot_resp_mes(mes)

elif analise_box == 'Análise de Fornecedores e Anomalias':

    st.markdown(
                """
        Na análise de fornecedores e anomalias, é feita a detecção e identificação de contratos que destoam do conjunto analisado, ou seja,
        que possuam valor de respiradores muito discrepantes e que talvez indiquem irregularidade no contrato. Além disso,
         detalhamos o preço pago nos respiradores por fornecedor, tornando possível, além de verificar a regularidade,
         investigar os casos relevantes.
        """
    )


    plot_fornecedores()

    show_anomalias()


if st.checkbox('Mostrar as fontes de dados'):

    st.markdown(
        """
        ---

        ## Fontes: 

        * Distribuição de respiradores antes da pandemia:[CNES - Recursos Físicos - Respiradores](http://tabnet.datasus.gov.br/cgi/tabcgi.exe?cnes/cnv/equipobr.def)
        * Número de habitantes por estado: [SIDRA -IBGE](https://sidra.ibge.gov.br/tabela/6579)
        * Distribuição de respiradores durante a pandemia: [PORTAL BRASILEIRO DE DADOS ABERTOS](http://dados.gov.br/dataset/distribuicao-de-respiradores)        
        """
    )