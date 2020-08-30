import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pydeck as pdk
import plotly.express as px


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
    else:
        print('Wrong Option!')
        return 'Wrong Option!'


def plot_fornecedores():
    report2 = load_data('fornecedor')

    fig2 = px.bar(report2, y='FORNECEDOR', x='PREÇO_MEDIO',
                hover_data=['QT_TOT','VL_TOT'],color='PREÇO_MEDIO',
                labels={'QT_TOT':'Qnt. de respiradores','VL_TOT':'Valor total dos respiradores','PREÇO_MEDIO':'Valor Médio em reais (R$)', 'FORNECEDOR':'Fornecedor'},
                height = 800, width = 800,
                color_continuous_scale= px.colors.sequential.Blugrn
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
            color_continuous_scale= px.colors.sequential.Blugrn, title = f'Pedido de respiradores em {month_dict[mes_selec]}'
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
            color_continuous_scale= px.colors.sequential.Blugrn, title = f'Valor gasto com respiradores em {month_dict[mes_selecionado]}'
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
                    color_continuous_scale= px.colors.sequential.Blugrn
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

##########################################################################################################################################################################
# Dashboard

st.title("Portal da Transparência COVID-19")
st.markdown(
    """
    Deu certo aí Pardal ?
    """
)


st.sidebar.title("Sidebar")
st.sidebar.markdown(
    """
    Escolha o que deseja observar
    """
)


analise_box = st.sidebar.selectbox('Tipo de Análise', ('Análise de Gastos Totais','Análise de Fornecedores e Anomalias','Análise de Gasto Mensal'))

if analise_box == 'Análise de Gastos Totais':

    plot_val_tot()

elif analise_box == 'Análise de Gasto Mensal':

    box = st.selectbox('Mês', ('Abril','Maio','Junho','Julho','Agosto'))
    month_dict = {'Abril':4, 'Maio':5, 'Junho':6, 'Julho':7, 'Agosto':8}
    mes = month_dict[box]

    plot_val_mes(mes)
    plot_qnt_mes(mes)

elif analise_box == 'Análise de Fornecedores e Anomalias':


    plot_fornecedores()

    show_anomalias()
