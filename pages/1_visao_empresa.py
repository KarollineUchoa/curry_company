#Imports
import pandas as pd
import plotly.express as px
from PIL import Image
from datetime import datetime
import folium
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='🏢', layout='wide')

#---------------------------------------
#Funções
#---------------------------------------
#---Funções tab1
#gráfico de barras
def pedidos_dia(df1):
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')        
    return fig

#gráfico de pizza
def pedidos_por_trafego(df1):                
    df_aux= df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values = 'entregas_perc', names = 'Road_traffic_density')                
    return fig

#gráfico de bolhas
def pedidos_por_cidade_e_trafego(df1):     
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()           
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

#---Funções tab2
#gráfico de linha 1
def pedidos_semana(df1):        
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    fig = px.line(df_aux, x='Week_of_year', y='ID')
    return fig

#gráfico de linha 2
def pedidos_entregador_unico_semana(df1):        
    df_aux1 = df1.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()  
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'Week_of_year']].groupby(['Week_of_year']).nunique().reset_index()   
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')        
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_year', y='Order_by_deliver')
    return fig

#---Função tab3
#mapa
def local_central(df1):
    df_aux=(df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                .groupby(['City','Road_traffic_density'])
                .median()
                .reset_index())
    map = folium.Map( zoom_start=11 )
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width=1024,height=600)
              
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

#---------------------------------------- Início da estrutura lógica do código ------------------------------------
#----------------------------------------------
#import dataset
df = pd.read_csv('dataset/train.csv')

#Limpando os dados
df1 = clean_code(df)

#=================================================
# Barra lateral
#=================================================

st.header('Marketplace - Visão Cliente')

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
tab1, tab2, tab3 = st.tabs( ['Visão gerencial', 'Visão tática', 'Visão geográfica'] )

with tab1:
    with st.container():
        st.markdown('# Pedidos por dia')
        fig = pedidos_dia(df1)
        st.plotly_chart(fig, use_container_width=True)            
        
    
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.header('Pedidos por tipo de tráfego')
            fig = pedidos_por_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)                
        
        with col2:
            st.header('Pedidos por cidade e tipo de tráfego')
            fig = pedidos_por_cidade_e_trafego(df1)
            st.plotly_chart(fig, use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('# Pedidos por semana')
        fig = pedidos_semana(df1)
        st.plotly_chart(fig, use_container_width=True)        
    
    with st.container():
        st.markdown('# Pedidos com entregador único por semana')
        fig = pedidos_entregador_unico_semana(df1)
        st.plotly_chart(fig, use_container_width=True)        
    
with tab3:
    st.markdown('# Localização central de entregas por tipo de cidade e tráfego:')
    local_central(df1)
  