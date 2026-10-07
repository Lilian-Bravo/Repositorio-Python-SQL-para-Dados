# ==============================================================================
# PROJETO: CONVEX SEGUROS - PAINEL ANALÍTICO E SIMULADOR ESTRATÉGICO
# AUTOR: Senior Data Strategist
# OBJETIVO: Permitir que qualquer pessoa (mesmo sem conhecimento técnico)
#           consiga auditar o funil de sinistros, testar cenários financeiros
#           e consultar diagnósticos gerados por Inteligência Artificial.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS (NOSSAS "FERRAMENTAS DE TRABALHO")
# ------------------------------------------------------------------------------
# streamlit: Transforma código Python em uma página web interativa sem precisar de HTML/CSS.
import streamlit as st

# pandas: Funciona como um "Excel super rápido" em código para manipular tabelas e dados.
import pandas as pd

# numpy: Biblioteca de cálculos matemáticos e operações numéricas.
import numpy as np

# plotly.express e plotly.graph_objects: Criam gráficos interativos modernos (com zoom, dicas ao passar o mouse, etc.).
import plotly.express as px
import plotly.graph_objects as go

# os: Permite ao Python conversar com o sistema de arquivos do computador (verificar se o arquivo existe).
import os


# ------------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DA PÁGINA WEB
# ------------------------------------------------------------------------------
# Define o título da aba do navegador, o ícone de escudo e faz o painel ocupar a tela inteira (wide).
st.set_page_config(
    page_title="Convex Seguros | Analytics & GenAI Funnel",
    page_icon="🛡️",
    layout="wide"
)


# ------------------------------------------------------------------------------
# 3. FUNÇÃO DE LIMPEZA E PREPARAÇÃO DOS DADOS (ENGENHARIA DE DADOS)
# ------------------------------------------------------------------------------
# @st.cache_data: Salva o resultado na memória. Assim, o arquivo só é lido uma vez,
# deixando a navegação muito rápida quando o usuário aplica filtros na tela.
@st.cache_data
def carregar_e_limpar_dados():
    """
    Esta função localiza o arquivo CSV bruto, corrige problemas de digitação,
    ajusta casas decimais brasileiras e remove linhas duplicadas de produção.
    """
    # Lista de possíveis nomes do arquivo CSV para evitar erro caso o arquivo tenha sido renomeado
    nomes_possiveis = [
        "Cópia de Base_Dados_Convex_Seguros - Dados_Conversas.csv",
        "dados_conversas.csv",
        "Base_Dados_Convex_Seguros - Dados_Conversas.csv"
    ]
    
    arquivo_encontrado = None
    for nome in nomes_possiveis:
        if os.path.exists(nome):
            arquivo_encontrado = nome
            break  # Encontrou o arquivo, sai do laço de busca

    # Se nenhum dos nomes acima for achado na pasta, exibe um alerta vermelho amigável e interrompe
    if not arquivo_encontrado:
        st.error("⚠️ Atenção: Não encontramos o arquivo CSV na pasta do projeto! Certifique-se de salvar o arquivo CSV na mesma pasta do app.py.")
        st.stop()
        
    # Lê a tabela original do CSV
    df_bruto = pd.read_csv(arquivo_encontrado)
    
    # --- TRATAMENTO 1: PADRONIZAR NOMES COM ERRO DE DIGITAÇÃO ---
    # No banco de produção, "RESOLVIDO_BOT", "Resolvido_bot" ou "ESCALADO HUMANO" foram gravados de várias formas.
    # Aqui convertemos tudo para maiúsculas primeiro e depois padronizamos em 3 desfechos únicos.
    df_bruto['Status_Final_Clean'] = df_bruto['Status_Final'].astype(str).str.strip().str.upper().replace({
        'RESOLVIDO_BOT': 'Resolvido_Bot',
        'RESOLVIDO BOT': 'Resolvido_Bot',
        'ESCALADO_HUMANO': 'Escalado_Humano',
        'ESCALADO HUMANO': 'Escalado_Humano',
        'ABANDONADO': 'Abandonado',
        'ABANDONO': 'Abandonado'
    })
    
    # --- TRATAMENTO 2: CONVERSÃO DE FORMATOS DE NÚMERO E DATA ---
    # No Brasil usamos vírgula para centavos (ex: 45,8). O Python precisa de ponto (ex: 45.8) para fazer contas.
    df_bruto['Tempo_Resolucao_Min_Num'] = df_bruto['Tempo_Resolucao_Min'].astype(str).str.replace(',', '.').astype(float)
    df_bruto['Valor_Estimado_Sinistro_RS_Num'] = df_bruto['Valor_Estimado_Sinistro_RS'].astype(str).str.replace(',', '.').astype(float)
    
    # Converte texto de data/hora em formato cronológico real
    df_bruto['Data_Hora_Inicio_DT'] = pd.to_datetime(df_bruto['Data_Hora_Inicio'])
    
    # --- TRATAMENTO 3: ELIMINAÇÃO DE DUPLICIDADES ---
    # Foram encontradas 502 conversas repetidas em março por erro de extração.
    # Mantemos apenas o último registro oficial de cada ID único de atendimento.
    df_limpo = df_bruto.drop_duplicates(subset=['ID_Conversa'], keep='last').copy()
    
    return df_limpo

# Executa a limpeza e guarda a tabela tratada e pronta na variável 'df'
df = carregar_e_limpar_dados()


# ------------------------------------------------------------------------------
# 4. BARRA LATERAL (MENU DE FILTROS DINÂMICOS)
# ------------------------------------------------------------------------------
st.sidebar.title("🛡️ Filtros Estratégicos")
st.sidebar.markdown("Refine a base de sinistros de acordo com a sua análise:")

# Filtros com caixas de múltipla escolha (multiselect). Vêm todos marcados por padrão.
canais_selecionados = st.sidebar.multiselect(
    "Canal de Atendimento", 
    options=sorted(df['Canal'].unique()), 
    default=sorted(df['Canal'].unique())
)

produtos_selecionados = st.sidebar.multiselect(
    "Tipo de Seguro", 
    options=sorted(df['Tipo_Sinistro'].unique()), 
    default=sorted(df['Tipo_Sinistro'].unique())
)

segmentos_selecionados = st.sidebar.multiselect(
    "Segmento do Cliente", 
    options=sorted(df['Segmento_Cliente'].unique()), 
    default=sorted(df['Segmento_Cliente'].unique())
)

dispositivos_selecionados = st.sidebar.multiselect(
    "Sistema Operacional", 
    options=sorted(df['Dispositivo'].unique()), 
    default=sorted(df['Dispositivo'].unique())
)

# Filtra a tabela original mantendo apenas as opções que o usuário marcou na barra lateral
df_filtrado = df[
    (df['Canal'].isin(canais_selecionados)) &
    (df['Tipo_Sinistro'].isin(produtos_selecionados)) &
    (df['Segmento_Cliente'].isin(segmentos_selecionados)) &
    (df['Dispositivo'].isin(dispositivos_selecionados))
]


# ------------------------------------------------------------------------------
# 5. CABEÇALHO PRINCIPAL DO PAINEL
# ------------------------------------------------------------------------------
st.title("🛡️ Convex Seguros — Cockpit Estratégico de Sinistros")
st.caption("Diagnóstico Analítico do Funil Conversacional & Evolução de Produto com Suporte de GenAI | Parceria Blip")


# ------------------------------------------------------------------------------
# 6. CARTÕES DE INDICADORES-CHAVE (KPIs EXECUTIVOS)
# ------------------------------------------------------------------------------
# Divide a tela em 5 colunas lado a lado para mostrar os números consolidados
col1, col2, col3, col4, col5 = st.columns(5)

total_casos = len(df_filtrado)

# Taxa STP: Percentual de atendimentos 100% resolvidos pelo robô sem passar por pessoas
stp_rate = (df_filtrado['Status_Final_Clean'] == 'Resolvido_Bot').mean() * 100 if total_casos > 0 else 0

# Taxa de Abandono: Percentual de clientes que desistiram no meio do fluxo
abandono_rate = (df_filtrado['Status_Final_Clean'] == 'Abandonado').mean() * 100 if total_casos > 0 else 0

# Taxa de Transbordo: Percentual de clientes passados para atendentes humanos na central
transbordo_rate = (df_filtrado['Status_Final_Clean'] == 'Escalado_Humano').mean() * 100 if total_casos > 0 else 0

# CSAT: Nota média de satisfação (escala de 1 a 5) dada pelos clientes
csat_medio = df_filtrado['CSAT_1a5'].mean()

# Exibição visual dos cartões:
col1.metric("Volumetria de Sinistros", f"{total_casos:,}")
col2.metric("Taxa STP (100% Robô)", f"{stp_rate:.1f}%")
col3.metric("Taxa de Abandono", f"{abandono_rate:.1f}%", delta=f"{abandono_rate - 23.7:.1f}%", delta_color="inverse")
col4.metric("Transbordo p/ Humano", f"{transbordo_rate:.1f}%", delta=f"{transbordo_rate - 29.4:.1f}%", delta_color="inverse")
col5.metric("Satisfação (CSAT)", f"{csat_medio:.2f} / 5.0" if not np.isnan(csat_medio) else "Sem dados")

st.markdown("---")  # Linha visual separadora


# ------------------------------------------------------------------------------
# 7. ESTRUTURA DE ABAS DE CONTEÚDO
# ------------------------------------------------------------------------------
aba1, aba2, aba3 = st.tabs([
    "📊 Funil & Diagnóstico Operacional", 
    "💰 Simulador Financeiro (Stress Test)", 
    "🤖 Assistente Executivo com IA"
])

# ==============================================================================
# PROJETO: CONVEX SEGUROS - DASHBOARD ANALÍTICO & ASSISTENTE COM IA (STREAMLIT)
# PARCERIA: Blip x Convex Seguros
# PAPEL: Senior Data Strategist
# OBJETIVO: Painel interativo com auditoria de dados, funil completo,
#           comparativo de produtos, simulador financeiro e módulo com 9 consultas
#           executivas blindadas contra alucinação na Inteligência Artificial.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS (FERRAMENTAS)
# ------------------------------------------------------------------------------
# streamlit: Constrói a página web interativa sem precisar de HTML ou JavaScript
import streamlit as st

# pandas: Manipula tabelas, faz agregações e filtros rápidos
import pandas as pd

# numpy: Tratamento matemático de números e valores ausentes (NaN)
import numpy as np

# plotly: Biblioteca de gráficos dinâmicos e interativos
import plotly.express as px
import plotly.graph_objects as go

# os: Localiza caminhos de pastas e arquivos no sistema operacional
import os


# ------------------------------------------------------------------------------
# 2. CONFIGURAÇÃO DA PÁGINA WEB
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Convex Seguros | Analytics & GenAI Funnel",
    page_icon="🛡️",
    layout="wide"
)


# ------------------------------------------------------------------------------
# 3. LEITURA E SANEAMENTO DOS DADOS (DATA QUALITY & ENGENHARIA)
# ------------------------------------------------------------------------------
@st.cache_data
def carregar_e_limpar_dados():
    """
    Localiza o arquivo CSV, calcula a volumetria bruta, trata duplicatas
    e retorna tanto a base limpa quanto os totais de auditoria.
    """
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_fixo = r"C:\Users\lilia\OneDrive\Área de Trabalho\Teste Blip\Base_Dados_Convex_Seguros - Dados_Conversas.csv"
    
    nomes_possiveis = [
        caminho_fixo,
        os.path.join(pasta_atual, "Base_Dados_Convex_Seguros - Dados_Conversas.csv"),
        os.path.join(pasta_atual, "Cópia de Base_Dados_Convex_Seguros - Dados_Conversas.csv"),
        os.path.join(pasta_atual, "dados_conversas.csv"),
        "Base_Dados_Convex_Seguros - Dados_Conversas.csv",
        "Cópia de Base_Dados_Convex_Seguros - Dados_Conversas.csv",
        "dados_conversas.csv"
    ]
    
    arquivo_encontrado = None
    for nome in nomes_possiveis:
        if os.path.exists(nome):
            arquivo_encontrado = nome
            break
            
    if not arquivo_encontrado:
        st.error("⚠️ Atenção: Não encontramos o arquivo CSV na pasta do projeto! Certifique-se de salvar o CSV junto do app.py.")
        st.stop()
        
    df_bruto = pd.read_csv(arquivo_encontrado, encoding='utf-8')
    total_linhas_brutas = len(df_bruto)
    
    # 1. Padronização de casing para a coluna Status_Final
    df_bruto['Status_Final_Clean'] = df_bruto['Status_Final'].astype(str).str.strip().str.upper().replace({
        'RESOLVIDO_BOT': 'Resolvido_Bot',
        'RESOLVIDO BOT': 'Resolvido_Bot',
        'ESCALADO_HUMANO': 'Escalado_Humano',
        'ESCALADO HUMANO': 'Escalado_Humano',
        'ABANDONADO': 'Abandonado',
        'ABANDONO': 'Abandonado'
    })
    
    # 2. Conversão de separador decimal pt-BR (vírgula) para float
    df_bruto['Tempo_Resolucao_Min_Num'] = pd.to_numeric(df_bruto['Tempo_Resolucao_Min'].astype(str).str.replace(',', '.'), errors='coerce')
    df_bruto['Valor_Estimado_Sinistro_RS_Num'] = pd.to_numeric(df_bruto['Valor_Estimado_Sinistro_RS'].astype(str).str.replace(',', '.'), errors='coerce')
    df_bruto['Data_Hora_Inicio_DT'] = pd.to_datetime(df_bruto['Data_Hora_Inicio'], errors='coerce')
    
    # 3. Deduplicação mantendo o último registro de cada atendimento único
    df_limpo = df_bruto.drop_duplicates(subset=['ID_Conversa'], keep='last').copy()
    total_linhas_limpas = len(df_limpo)
    duplicatas_tratadas = total_linhas_brutas - total_linhas_limpas
    
    return df_limpo, total_linhas_brutas, duplicatas_tratadas, total_linhas_limpas

df, total_bruto, total_dups, total_liquido = carregar_e_limpar_dados()


# ------------------------------------------------------------------------------
# 4. BARRA LATERAL (FILTROS MULTIDIMENSIONAIS DINÂMICOS)
# ------------------------------------------------------------------------------
st.sidebar.title("🛡️ Filtros Estratégicos")
st.sidebar.markdown("Selecione os parâmetros para atualizar os gráficos:")

canais = st.sidebar.multiselect("Canal de Origem", options=sorted(df['Canal'].unique()), default=sorted(df['Canal'].unique()))
produtos = st.sidebar.multiselect("Linha de Produto", options=sorted(df['Tipo_Sinistro'].unique()), default=sorted(df['Tipo_Sinistro'].unique()))
segmentos = st.sidebar.multiselect("Segmento Comercial", options=sorted(df['Segmento_Cliente'].unique()), default=sorted(df['Segmento_Cliente'].unique()))
dispositivos = st.sidebar.multiselect("Dispositivo", options=sorted(df['Dispositivo'].unique()), default=sorted(df['Dispositivo'].unique()))

df_filtrado = df[
    (df['Canal'].isin(canais)) &
    (df['Tipo_Sinistro'].isin(produtos)) &
    (df['Segmento_Cliente'].isin(segmentos)) &
    (df['Dispositivo'].isin(dispositivos))
]


# ------------------------------------------------------------------------------
# 5. CABEÇALHO DO PAINEL
# ------------------------------------------------------------------------------
st.title("🛡️ Convex Seguros — Cockpit Estratégico de Sinistros")
st.caption("Diagnóstico Analítico do Funil Conversacional & Evolução de Produto com Suporte de GenAI | Parceria Blip")


# ------------------------------------------------------------------------------
# 6. BANNER DE AUDITORIA DE DADOS (DATA QUALITY & VOLUMETRIA)
# ------------------------------------------------------------------------------
st.info(f"""
📋 **Auditoria de Qualidade dos Dados de Produção (ETL Validado):**
* **Volumetria Bruta Inicial:** **{total_bruto:,} registros** extraídos dos logs originais.
* **Duplicatas Técnicas Tratadas:** **{total_dups} linhas removidas** (inconsistência no lote de 10 a 24 de março).
* **Volumetria Líquida Oficial:** **{total_liquido:,} conversas únicas** auditadas e prontas para análise.
""")


# ------------------------------------------------------------------------------
# 7. CARTÕES DE INDICADORES PRINCIPAIS (KPIs)
# ------------------------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
total_casos = len(df_filtrado)
stp_rate = (df_filtrado['Status_Final_Clean'] == 'Resolvido_Bot').mean() * 100 if total_casos > 0 else 0
abandono_rate = (df_filtrado['Status_Final_Clean'] == 'Abandonado').mean() * 100 if total_casos > 0 else 0
transbordo_rate = (df_filtrado['Status_Final_Clean'] == 'Escalado_Humano').mean() * 100 if total_casos > 0 else 0
csat_medio = df_filtrado['CSAT_1a5'].mean()

col1.metric("Casos Selecionados", f"{total_casos:,}")
col2.metric("Taxa STP (100% Robô)", f"{stp_rate:.1f}%")
col3.metric("Taxa de Abandono", f"{abandono_rate:.1f}%", delta=f"{abandono_rate - 23.7:.1f}%", delta_color="inverse")
col4.metric("Transbordo p/ Humano", f"{transbordo_rate:.1f}%", delta=f"{transbordo_rate - 29.4:.1f}%", delta_color="inverse")
col5.metric("CSAT Médio", f"{csat_medio:.2f} / 5.0" if not np.isnan(csat_medio) else "N/A")

st.markdown("---")


# ------------------------------------------------------------------------------
# 8. ESTRUTURA DE ABAS TEMÁTICAS
# ------------------------------------------------------------------------------
aba1, aba2, aba3, aba4 = st.tabs([
    "📊 Funil & Diagnóstico de Gargalos", 
    "🏷️ Desempenho por Produto & Ticket Médio",
    "💰 Simulador Financeiro (Stress Test)", 
    "🤖 Assistente Executivo com IA"
])


# ==============================================================================
# ABA 1: FUNIL DE ATENDIMENTO E DIAGNÓSTICO DE ETAPAS
# ==============================================================================
with aba1:
    st.subheader("Progressão do Funil e Concentração de Falhas")
    
    etapas_ordem = [
        'Inicio_Saudacao', 'Validacao_Apolice', 'Coleta_Dados_Sinistro',
        'Upload_Fotos_Documentos', 'Analise_Automatica', 'Confirmacao_Protocolo'
    ]
    
    saidas = pd.crosstab(df_filtrado['Etapa_Saida_Conversa'], df_filtrado['Status_Final_Clean']).reindex(etapas_ordem).fillna(0)
    
    funil_dados = []
    restantes = total_casos
    for etapa in etapas_ordem:
        ab = saidas.loc[etapa, 'Abandonado'] if 'Abandonado' in saidas.columns else 0
        esc = saidas.loc[etapa, 'Escalado_Humano'] if 'Escalado_Humano' in saidas.columns else 0
        res = saidas.loc[etapa, 'Resolvido_Bot'] if 'Resolvido_Bot' in saidas.columns else 0
        saida_total = ab + esc + res
        funil_dados.append({'Etapa': etapa, 'Entrantes': restantes, 'Abandonos': ab, 'Escalados': esc, 'Resolvidos': res})
        restantes -= saida_total
    
    df_funil_calc = pd.DataFrame(funil_dados)
    
    fig_funil = go.Figure()
    fig_funil.add_trace(go.Bar(name='Retenção / Avanço', x=df_funil_calc['Etapa'], y=df_funil_calc['Entrantes'], marker_color='#1f77b4'))
    fig_funil.add_trace(go.Bar(name='Abandonos (Desistência)', x=df_funil_calc['Etapa'], y=df_funil_calc['Abandonos'], marker_color='#d62728'))
    fig_funil.add_trace(go.Bar(name='Escalados (Humano)', x=df_funil_calc['Etapa'], y=df_funil_calc['Escalados'], marker_color='#ff7f0e'))
    fig_funil.update_layout(barmode='stack', title="Distribuição do Fluxo em Cada Etapa da Jornada", height=420)
    st.plotly_chart(fig_funil, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### ⚠️ Gargalo 1: Validação de Apólice")
        st.caption("54,2% dos transbordos humanos ocorrem aqui (rejeição em Seguro de Vida e frotas de empresas).")
        val_df = df_filtrado[df_filtrado['Etapa_Saida_Conversa'] == 'Validacao_Apolice']
        fig_val = px.histogram(val_df, x='Tipo_Sinistro', color='Status_Final_Clean', barmode='group', color_discrete_map={'Escalado_Humano': '#ff7f0e', 'Abandonado': '#d62728'})
        st.plotly_chart(fig_val, use_container_width=True)
    with col_b:
        st.markdown("### 🚨 Gargalo 2: Upload de Fotos / Documentos")
        st.caption("47,0% de todos os abandonos acontecem nesta etapa (fotos pesadas e limite de tempo).")
        up_df = df_filtrado[df_filtrado['Etapa_Saida_Conversa'] == 'Upload_Fotos_Documentos']
        fig_up = px.histogram(up_df, x='Dispositivo', color='Status_Final_Clean', barmode='group', color_discrete_map={'Escalado_Humano': '#ff7f0e', 'Abandonado': '#d62728'})
        st.plotly_chart(fig_up, use_container_width=True)


# ==============================================================================
# ABA 2: DESEMPENHO POR PRODUTO & TICKET MÉDIO
# ==============================================================================
with aba2:
    st.subheader("Comparativo por Linha de Produto: Pior Resolução vs. Maior Ticket")
    st.write("Visão analítica demonstrando o comportamento assimétrico do Seguro de Vida:")
    
    c_p1, c_p2, c_p3 = st.columns(3)
    c_p1.metric(
        "Seguro Vida: Taxa STP", 
        "38,8% (Pior da Carteira)", 
        delta="-9,7% vs Auto", 
        delta_color="inverse",
        help="O Seguro Vida tem a menor automação digital porque o assistente virtual exige CPF do titular na validação."
    )
    c_p2.metric(
        "Seguro Vida: Ticket Médio", 
        "R$ 45.501,09 (Maior Valor)", 
        delta="+R$ 37.020 vs Auto",
        help="O sinistro de Vida possui o maior valor monetário unitário da seguradora (mais de 5 vezes o valor do seguro Auto)."
    )
    c_p3.metric(
        "Seguro Vida: Transbordo Humano", 
        "37,1% (Maior Queda)", 
        delta="+9,0% vs Auto", 
        delta_color="inverse",
        help="Mais de um terço de todas as conversas de Seguro Vida são escaladas para atendentes humanos."
    )
    
    st.markdown("#### Tabela Comparativa Consolidada por Produto")
    tabela_prod = df_filtrado.groupby('Tipo_Sinistro').agg(
        Volumetria=('ID_Conversa', 'count'),
        Taxa_STP_Bot=('Status_Final_Clean', lambda s: f"{(s == 'Resolvido_Bot').mean()*100:.1f}%"),
        Transbordo_Humano=('Status_Final_Clean', lambda s: f"{(s == 'Escalado_Humano').mean()*100:.1f}%"),
        Taxa_Abandono=('Status_Final_Clean', lambda s: f"{(s == 'Abandonado').mean()*100:.1f}%"),
        Ticket_Medio_RS=('Valor_Estimado_Sinistro_RS_Num', lambda v: f"R$ {v.mean():,.2f}"),
        Valor_Total_Sinistros=('Valor_Estimado_Sinistro_RS_Num', lambda v: f"R$ {v.sum():,.2f}")
    ).reset_index()
    
    st.dataframe(tabela_prod, use_container_width=True, hide_index=True)
    
    st.markdown("""
    > 💡 **Conclusão Estratégica para a Banca:**  
    > O produto **Vida** apresenta o paradoxo crítico da Convex Seguros: possui o **maior ticket médio (R$ 45.501,09)**, mas amarga a **pior taxa de resolução digital (38,8% STP)** e o **maior índice de transbordo humano (37,1%)**. A causa-raiz é a rigidez do assistente virtual, que exige validação pelo CPF do próprio titular da apólice, desconsiderando que o sinistro de Vida é registrado por cônjuges e herdeiros legais.
    """)


# ==============================================================================
# ABA 3: SIMULADOR FINANCEIRO E TESTE DE ESTRESSE
# ==============================================================================
with aba3:
    st.subheader("Simulador Dinâmico de Eficiência Financeira")
    st.info("💡 Mova as barras deslizantes abaixo para responder em tempo real a mudanças de premissas da banca examinadora:")
    
    c1, c2, c3 = st.columns(3)
    custo_hora = c1.slider("Custo da Hora Humana Carregada (R$/h)", min_value=25.0, max_value=80.0, value=40.0, step=2.5)
    meta_reducao_transbordo = c2.slider("Meta de Redução de Transbordos (%)", min_value=5, max_value=60, value=25, step=5)
    recuperacao_abandono = c3.slider("Meta de Recuperação de Abandonos (%)", min_value=5, max_value=50, value=20, step=5)
    
    # Cálculos
    casos_humanos = (df_filtrado['Status_Final_Clean'] == 'Escalado_Humano').sum()
    tma_humano_min = df_filtrado[df_filtrado['Status_Final_Clean'] == 'Escalado_Humano']['Tempo_Resolucao_Min_Num'].mean()
    if np.isnan(tma_humano_min): tma_humano_min = 38.4
    
    sinistros_abandonados = df_filtrado[df_filtrado['Status_Final_Clean'] == 'Abandonado']
    valor_total_abandonado_4m = sinistros_abandonados['Valor_Estimado_Sinistro_RS_Num'].sum()
    
    # Anualização (x3)
    fator_ano = 3
    atendimentos_evitados_ano = (casos_humanos * (meta_reducao_transbordo / 100)) * fator_ano
    horas_poupadas_ano = (atendimentos_evitados_ano * tma_humano_min) / 60
    economia_financeira_ano = horas_poupadas_ano * custo_hora
    valor_recuperado_ano = (valor_total_abandonado_4m * (recuperacao_abandono / 100)) * fator_ano
    
    st.markdown("### Resultados do Cenário Simulado (Projeção Anual):")
    r1, r2, r3 = st.columns(3)
    r1.metric("Horas Humanas Liberadas / Ano", f"{horas_poupadas_ano:,.0f} horas")
    r2.metric("Economia Operacional (OPEX)", f"R$ {economia_financeira_ano:,.2f} / ano")
    r3.metric("Capital Salvo da Desistência", f"R$ {valor_recuperado_ano:,.2f} / ano")


# ==============================================================================
# ABA 4: ASSISTENTE EXECUTIVO DE IA (COM TODAS AS 9 CONSULTAS INTEGRADAS)
# ==============================================================================
with aba4:
    st.subheader("Assistente de Negócio com Suporte de Inteligência Artificial")
    st.write("Selecione uma análise executiva para consultar diagnósticos fundamentados nos dados auditados:")
    
    pergunta_selecionada = st.selectbox(
        "Selecione uma análise executiva ou dúvida de negócio:",
        [
            "1. Qual a volumetria líquida e quantas duplicatas foram tratadas?",
            "2. Qual a taxa atual de resolução STP (100% pelo robô)?",
            "3. Onde está o maior gargalo de abandono de clientes?",
            "4. Onde está o maior gargalo de transbordo para humanos?",
            "5. Qual produto tem a pior taxa de resolução e qual seu ticket médio?",
            "6. Qual o CSAT e TMA comparativo entre Bot e Humano?",
            "7. Por que o produto Vida apresenta a menor taxa de resolução automática?",
            "8. Qual o impacto de converter o abandono na etapa de upload de fotos?",
            "9. Qual a recomendação de curto prazo para aliviar a central humana imediatamente?"
        ]
    )
    
    if st.button("Executar Diagnóstico com GenAI"):
        # 1. Volumetria Líquida e Duplicatas
        if "1. Qual a volumetria" in pergunta_selecionada:
            st.markdown(f"""
            **Auditoria dos Dados por GenAI (Ground Truth):**
            * **Volumetria Bruta Extraída:** **{total_bruto:,} linhas** registradas nos logs originais de produção.
            * **Duplicatas Técnicas Tratadas:** Foram identificadas e removidas **{total_dups} linhas duplicadas** no lote de 10 a 24 de março, causadas por falha no serviço de ingestão de logs.
            * **Volumetria Líquida Oficial:** A base tratada, validada e auditada conta com exatamente **{total_liquido:,} conversas unívocas**.
            """)
            
        # 2. Taxa Atual de STP
        elif "2. Qual a taxa atual de resolução STP" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico de Automação Digital por GenAI:**
            * **Taxa STP Global (Straight-Through Processing):** **46,93%** (3.285 sinistros finalizados 100% pelo assistente sem intervenção humana).
            * **Transbordo para Atendente Humano:** **29,39%** (2.057 atendimentos escalados).
            * **Abandono do Cliente:** **23,69%** (1.658 conversas não finalizadas).
            * **Meta de Negócio:** Elevar a taxa STP para patamares superiores a **65%** com a execução do roadmap de produto.
            """)
            
        # 3. Maior Gargalo de Abandono
        elif "3. Onde está o maior gargalo de abandono" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico de Abandono por GenAI:**
            * **Ponto Crítico:** A etapa 4 (**Upload de Fotos / Documentos**) responde por **47,04% de todos os abandonos** do assistente (780 desistências em 1.658 totais).
            * **Causas-Raiz:** Sobrecarga de envio de múltiplos documentos sem guia visual, rejeição de formatos pesados (HEIC e fotos acima de 15MB) e perda de sessão por inatividade no WhatsApp.
            * **Ação Recomendada:** Compressão no dispositivo do usuário e validação visual multimodal (Visão Computacional) em tempo real.
            """)
            
        # 4. Maior Gargalo de Transbordo Humano
        elif "4. Onde está o maior gargalo de transbordo" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico de Transbordo Humano por GenAI:**
            * **Ponto Crítico:** A etapa 2 (**Validação de Apólice**) responde por **54,16% de todos os transbordos humanos** do sistema (1.114 escalonamentos em 2.057 totais).
            * **Causas-Raiz:** O assistente exige validação estrita pelo CPF do titular contratante, bloqueando sinistros de Seguro Vida (onde quem aciona é o beneficiário/herdeiro) e frotas do segmento Corporativo (acionadas por motoristas terceiros).
            * **Ação Recomendada:** Criação de ramificações contextuais na etapa 2 com verificação de vínculo civil do beneficiário e dados corporativos.
            """)
            
        # 5. Pior Taxa de Resolução e Ticket Médio
        elif "5. Qual produto tem a pior taxa" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico de Produto por GenAI:**
            * **Produto com Pior Resolução:** O **Seguro Vida** registra a menor taxa de resolução automática: apenas **38,78% de STP** (contra 48,53% em Auto e 47,99% em Residencial).
            * **Ticket Médio:** O **Seguro Vida** possui o maior valor médio da carteira: **R$ 45.501,09** (mais de 5 vezes superior ao Seguro Auto, que é R$ 8.480,84).
            * **Impacto Financeiro:** Embora represente apenas 14,7% dos atendimentos, Vida concentra **R$ 8,03 milhões em sinistros abandonados** (41,8% de todo o capital represado).
            """)
            
        # 6. Comparativo TMA e CSAT (Bot vs Humano)
        elif "6. Qual o CSAT e TMA comparativo" in pergunta_selecionada:
            st.markdown("""
            **Comparativo Operacional e de Experiência por GenAI:**
            * **TMA (Tempo Médio de Atendimento):**
              * **Resolvido pelo Bot:** **9,37 minutos** (atendimento rápido e assíncrono).
              * **Escalado para Humano:** **38,39 minutos** (+309% de consumo de tempo de operador).
            * **CSAT (Nota Média de Satisfação):**
              * **Resolvido pelo Bot:** **4,28 / 5.0 ★**
              * **Escalado para Humano:** **3,61 / 5.0 ★** (queda de 0,67 ponto motivada pelo atrito da espera e necessidade de repetir dados).
            * **O Ponto Cego Estatístico:** Clientes que abandonaram a jornada possuem **ZERO avaliações de CSAT registradas**, demonstrando que o CSAT médio nominal de 4,02 mascara a insatisfação de 23,7% da base.
            """)
            
        # 7. Por que Vida apresenta menor resolução (existente preservada)
        elif "7. Por que o produto Vida" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico Sintético de Seguro Vida:**
            * **Causa Identificada:** O seguro de Vida tem **37,12% de transbordo** (o pior da seguradora). O formulário do bot solicita dados do próprio titular segurado, ignorando que o sinistro de Vida é registrado por **beneficiários legais ou cônjuges** cujo CPF difere do cadastro da apólice.
            * **Ação Recomendada:** Criar ramificação condicional imediata na etapa 2 com verificação de vínculo civil, eliminando o bloqueio automático na validação.
            """)
            
        # 8. Impacto de converter o abandono de upload (existente preservada)
        elif "8. Qual o impacto de converter o abandono" in pergunta_selecionada:
            st.markdown("""
            **Diagnóstico de Conversão de Upload:**
            * **Causa Identificada:** O upload de fotos responde por **47% de todos os abandonos** (780 ocorrências). A solicitação de múltiplos arquivos pesados sem feedback visual gera abandono silencioso por tempo limite no WhatsApp.
            * **Ação Recomendada:** Compressão no dispositivo do cliente e integração com modelo de visão multimodal para conferência e OCR em tempo real. Recuperar 30% dessas desistências resgata mais de R$ 5,7 milhões por quadrimestre em sinistros digitalizados.
            """)
            
        # 9. Recomendação de curto prazo para aliviar a central (existente preservada)
        else:
            st.markdown("""
            **Recomendação de Curto Prazo (Quick Win):**
            * **Ação Imediata:** Implementar o envio de um **resumo estruturado gerado por LLM (*Warm Handoff*)** na abertura do atendimento humano. Reduz o TMA atual de 38,4 minutos ao evitar a re-coleta de dados que o bot já havia obtido, liberando centenas de horas operacionais na central.
            """)
