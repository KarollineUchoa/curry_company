#Libraries
import pandas as pd
import plotly.express as px
from haversine import haversine
import plotly.graph_objects as go
import numpy as np
from PIL import Image
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽', layout='wide')

#---------------------------------------
#Funções
#---------------------------------------
#---Funções tab1
#container 1 e container 3
#Distância média e tempo médio por entrega  / Distância da distribuição da distância média por cidade
def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                                 haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis= 1)
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']        
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                                 haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                           (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis= 1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig= go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        return fig

#Tempo médio e desvio padrão do tempo de entrega / com e sem festival
    """ A função abaixo calcula o tempo médio e o desvio padrão do tempo de entrega
      Parâmetros:
        Input:
            -df: Dataframe com os dados necessários para o cáuculo
            -op: Tipo de operação que precisa ser calculado
                'avg_time': Calcula o tempo médio
                'std_time': Calcula o desvio padrão do tempo
            -festival: 
                'Yes': entregas realizadas durante o festival
                'No: entregas realizadas fora do festival
        Output:
            -df: Dataframe com 2 colunas e 1 linha                
            
    """
def avg_std_time_delivery(df1, festival, op):

    df_mean_delivery_festival = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                                .groupby('Festival')
                                .agg({'Time_taken(min)' : ['mean', 'std']}))
    df_mean_delivery_festival.columns = ['avg_time', 'std_time']
    df_mean_delivery_festival = df_mean_delivery_festival.reset_index()
    df_mean_delivery_festival = np.round(df_mean_delivery_festival.loc[df_mean_delivery_festival['Festival'] == festival, op], 2)
    return df_mean_delivery_festival

#container 2
#Distribuição do tempo por cidade
def avg_std_time_graph(df1):
    df_mean_std_by_city = (df1.loc[:, ['Time_taken(min)', 'City']]
                               .groupby('City')
                               .agg({'Time_taken(min)' : ['mean', 'std']}))
    df_mean_std_by_city.columns = ['avg_time', 'std_time']
    df_mean_std_by_city = df_mean_std_by_city.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                         x=df_mean_std_by_city['City'],
                         y=df_mean_std_by_city['avg_time'],
                         error_y=dict(type='data', array=df_mean_std_by_city['std_time'])))
    fig.update_layout(barmode='group')
    return fig

#container 3
#Tempo médio por tipo de cidade e tipo de tráfego
def avg_std_time_on_traffic(df1):
    df_mean_std_by_city_traffic = (df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']]
                                       .groupby(['City', 'Road_traffic_density'])
                                       .agg({'Time_taken(min)' : ['mean', 'std']}))
    df_mean_std_by_city_traffic.columns = ['avg_time', 'std_time']

    df_mean_std_by_city_traffic = df_mean_std_by_city_traffic.reset_index()
    fig = px.sunburst(df_mean_std_by_city_traffic, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='Rdbu',
                      color_continuous_midpoint=np.average(df_mean_std_by_city_traffic['std_time']))
    return fig

#---Função limpeza
def clean_code(df1):
    """     
        Esta função tem a responsabilidade de limpar o DataFrame
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
        
    """
    #Excluir as linhas com Nan
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias,:]

    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias,:]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias,:]

    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias,:]


    #Conversão de dados da coluna 'Delivery_person_age' de object para int:
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype('int64')

    #Conversão de dados da coluna 'Delivery_person_Ratings' de object para float:
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype('float64')

    #Conversão de dados da coluna 'Order_Date' de object para datetime:
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Remove as linhas da culuna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( 'int64' )


    #Remover espaço em branco das colunas ID e Delivery_person_ID:
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()

    #Limpeza de coluna Time Taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( 'int64' )
    
    return df1

#---------------------------------- Início da estrutura lógica do código ---------------------------------
#----------------------------------------------
#import dataset
df = pd.read_csv('dataset/train.csv')

#Limpando os dados
df1 = clean_code(df)



#=================================================
# Barra lateral
#=================================================

st.header('Marketplace - Visão Restaurantes')

image = Image.open('logo.png')

st.sidebar.image (image, width=180)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite:')

data_slider = st.sidebar.slider(
    "Até qual valor?",
    value=datetime(2022,4,13),
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Karol Uchôa')


#Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#=================================================
# Layout no Streamlit
#=================================================
#=================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title('Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='small')
        
        with col1:           
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores \n únicos', delivery_unique)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric('A distância média é: ', avg_distance)           
                       
        with col3:
            df_mean_delivery_festival = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo médio de entrega com Festival', df_mean_delivery_festival)
        
        with col4:
            df_mean_delivery_festival = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('Desvio padrão de entrega com Festival', df_mean_delivery_festival)
            
        with col5:
            df_mean_delivery_festival = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo médio de entrega sem Festival', df_mean_delivery_festival)
            
        with col6:           
            df_mean_delivery_festival = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('Desvio padrão de entrega sem Festival', df_mean_delivery_festival)   
  
            
    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Distribuição do tempo por cidade')
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig, use_container_width=True)            
            
        with col2:
            st.markdown('###### Tempo médio por tipo de entrega')
            df_mean_std_by_city_order = (df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']]
                                            .groupby(['City', 'Type_of_order'])
                                            .agg({'Time_taken(min)' : ['mean', 'std']}))
            df_mean_std_by_city_order.columns = ['time_mean', 'time_std']
            df_mean_std_by_city_order = df_mean_std_by_city_order.reset_index()
            st.dataframe(df_mean_std_by_city_order)

    with st.container():
        st.markdown('''---''')
        st.title('Tempo médio entrega por cidade')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Distância da distribuição da distância média por cidade')
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('###### Tempo médio por tipo de cidade e tipo de tráfego')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)     