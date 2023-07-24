#Imports
import pandas as pd
from PIL import Image
from datetime import datetime
import streamlit as st

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#---------------------------------------
#Funções
#---------------------------------------
#---Funções tab1
#container 3
#Top entregadores mais rápidos e mais lentos
def top_delivers(df1, top_asc):
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby(['City', 'Delivery_person_ID'])
               .mean()
               .sort_values(['City','Time_taken(min)'], ascending=top_asc)
               .reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df3


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

st.header('Marketplace - Visão Entregadores')

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
tab1, tab2, tab3 = st.tabs( ['Visão gerencial', '_', '_'] )

with tab1:
#------------------container 1
    with st.container():
        st.title('Overall Metrics')
        col1,col2, col3, col4 = st.columns (4, gap='large')
        with col1:
            #A maior idade dos entregadores          
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)
            
        with col2:
            #A menor idade dos entregadores            
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)            
            
        with col3:
            #Melhor condição de veículo           
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_condicao)
            
        with col4:
            #Pior condição de veículo            
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Melhor condição', pior_condicao)

#------------------container 2
    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Avaliações médias por entregador')
            df_avaliacao_media_entregador =( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                         .groupby(['Delivery_person_ID'])
                         .mean()
                         .reset_index())
            st.dataframe(df_avaliacao_media_entregador)
            
        with col2:            
            st.markdown('##### Avaliação média por trânsito')
            df_mean_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings' ,'Road_traffic_density']]
                                                 .groupby('Road_traffic_density')
                                                 .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            df_mean_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            df_mean_std_rating_by_traffic = df_mean_std_rating_by_traffic.reset_index()
            st.dataframe(df_mean_std_rating_by_traffic)
            
            st.markdown('##### Avaliação média por clima')
            df_mean_std_by_weather = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                          .groupby('Weatherconditions')
                                          .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
            df_mean_std_by_weather.columns = ['delivery_mean', 'delivery_std']
            df_mean_std_by_weather = df_mean_std_by_weather.reset_index()
            st.dataframe(df_mean_std_by_weather)

#------------------container 3
    with st.container():
        st.markdown('''---''')
        st.title('Velocidade de entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_delivers(df1, top_asc=False)
            st.dataframe(df3)
            
            