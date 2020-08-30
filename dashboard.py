import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pydeck as pdk
import plotly.express as px


#load data
@st.cache(allow_output_mutation=True)
def load_data2(file):

    df = pd.read_csv(file)
    report_month = pd.read_csv(file)
    df['coordinates'] = df[['longitude', 'latitude']].values.tolist()

    if file == 'data_map2.csv':
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

    return df

@st.cache(allow_output_mutation=True)
def load_data(file):

    df = pd.read_csv(file)
    df['coordinates'] = df[['longitude', 'latitude']].values.tolist()


    return df

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
report3 = load_data2('data_map2.csv')

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

#st.sidebar.info(f'Foram carregadas {df.shape[0]} linhas')
if st.sidebar.checkbox('Mostrar distribuição de respiradores'):

    # Load Data
    df = load_data('dados_dash2.csv')
    map_df = load_data('data_map2.csv')


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

    # Slide bar do mês
    mes_selecionado = st.slider('Selecione o mês', 4, 8, 8)
    df.DATA = pd.to_datetime(df.DATA)
    df_selected = df[df.DATA.dt.month == mes_selecionado]
    map_selected = map_df[map_df.MES == mes_selecionado]

    if st.checkbox('Mostrar Tabela de Dados'):
        st.header("Tabela de Dados")
        st.write(df_selected.drop(columns = ['latitude', 'longitude']))

    # Mapa

    if st.checkbox('Mostrar Mapa # de compras por Estado'):

        # Define a layer to display on a map
        layer = pdk.Layer(
            "ScatterplotLayer",
            map_selected,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=400,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position='coordinates',
            get_radius='QT_MES',
            get_fill_color=[0, 0, 255],
            get_line_color=[0, 0, 0],
        )

        # Set the viewport location
        view_state = pdk.ViewState(latitude=-14.086503, longitude=-50.9322067, zoom=3, min_zoom=3, bearing=0, pitch=0)



        st.header("Mapa de Distribuição de Respiradores")
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    if st.checkbox('Mostrar Mapa valor gasto com respiradores por Estado'):

        COLOR_BREWER_BLUE_SCALE = [
            [240, 249, 232],
            [204, 235, 197],
            [168, 221, 181],
            [123, 204, 196],
            [67, 162, 202],
            [8, 104, 172],

        ]

        heat = pdk.Layer(
            "HeatmapLayer",
            map_selected,
            opacity=1,
            get_position='coordinates',
            aggregation='"SUM"',
            color_range=COLOR_BREWER_BLUE_SCALE,
            threshold=0.7,
            get_weight="VL_MES",
            pickable=True,
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            map_selected,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=400,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position='coordinates',
            get_radius='QT_MES',
            get_fill_color=[255, 0, 0],
            get_line_color=[255, 140, 0],
        )

        # Set the viewport location
        view_state = pdk.ViewState(latitude=-14.086503, longitude=-50.9322067, zoom=3, min_zoom=3, bearing=0, pitch=0)



        st.header("Mapa de Distribuição de Respiradores")
        st.pydeck_chart(pdk.Deck(layers=[heat], initial_view_state=view_state))

    if st.checkbox('Mostrar Tabela de Pedidos por Mês'):
        st.subheader("Pedidos do mês")
        st.write(map_selected.drop(columns = ['MES']))