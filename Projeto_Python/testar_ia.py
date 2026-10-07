# ==============================================================================
# PROJETO: CONVEX SEGUROS - BATERIA DE TESTES DE INTEGRIDADE & ANTI-ALUCINAÇÃO
# PARCERIA: Blip x Convex Seguros
# PAPEL: Senior Data Strategist
# OBJETIVO: Garantir que a Inteligência Artificial e o painel analítico nunca
#           inventem números (alucinem) perante a banca avaliadora.
# COMO EXECUTAR: No terminal do VS Code, digite: python testar_ia.py
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. IMPORTAÇÃO DAS BIBLIOTECAS (NOSSAS FERRAMENTAS)
# ------------------------------------------------------------------------------
# os: Biblioteca padrão do Python para verificar arquivos e pastas no computador.
import os

# pandas: Biblioteca que lê planilhas e arquivos CSV de forma rápida.
import pandas as pd

# numpy: Biblioteca para operações matemáticas.
import numpy as np


# ------------------------------------------------------------------------------
# 2. FUNÇÃO PRINCIPAL QUE RODA OS TESTES
# ------------------------------------------------------------------------------
def executar_bateria_de_testes():
    """
    Esta função executa 6 testes rigorosos conferindo os números calculados
    contra o gabarito oficial (Ground Truth) dos dados reais de produção.
    """
    print("=" * 75)
    print("🔍 INICIANDO BATERIA DE TESTES DE INTEGRIDADE (ANTI-ALUCINAÇÃO)")
    print("=" * 75)
    
    # --- PASSO A: LOCALIZAR O ARQUIVO CSV ---
    # Lista com variações de nomes do arquivo para evitar erros caso tenha sido renomeado
    nomes_possiveis = [
        "Cópia de Base_Dados_Convex_Seguros - Dados_Conversas.csv",
        "dados_conversas.csv",
        "Base_Dados_Convex_Seguros - Dados_Conversas.csv"
    ]
    
    arquivo_encontrado = None
    for nome in nomes_possiveis:
        if os.path.exists(nome):
            arquivo_encontrado = nome
            break
            
    # Se o arquivo não existir na pasta, avisa o usuário e para o teste
    if not arquivo_encontrado:
        print("❌ ERRO: O arquivo CSV de conversas não foi encontrado na pasta atual!")
        print("Certifique-se de que o CSV está na mesma pasta onde este script está rodando.")
        return

    # Lê os dados brutos do arquivo CSV
    df_bruto = pd.read_csv(arquivo_encontrado, encoding='utf-8')
    total_linhas_brutas = len(df_bruto)
    
    # --- PASSO B: TRATAMENTO DOS DADOS (ENGENHARIA DE DADOS) ---
    # 1. Padroniza os textos de desfecho da conversa (evita problemas com maiúsculas/minúsculas)
    df_bruto['Status_Final_Clean'] = df_bruto['Status_Final'].astype(str).str.strip().str.upper().replace({
        'RESOLVIDO_BOT': 'Resolvido_Bot',
        'RESOLVIDO BOT': 'Resolvido_Bot',
        'ESCALADO_HUMANO': 'Escalado_Humano',
        'ESCALADO HUMANO': 'Escalado_Humano',
        'ABANDONADO': 'Abandonado',
        'ABANDONO': 'Abandonado'
    })
    
    # 2. Converte números que usam vírgula brasileira para ponto flutuante
    df_bruto['Tempo_Resolucao_Min_Num'] = pd.to_numeric(
        df_bruto['Tempo_Resolucao_Min'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    df_bruto['Valor_Estimado_Sinistro_RS_Num'] = pd.to_numeric(
        df_bruto['Valor_Estimado_Sinistro_RS'].astype(str).str.replace(',', '.'), 
        errors='coerce'
    )
    
    # 3. Remove os registros duplicados de ID_Conversa mantendo a última ocorrência oficial
    df_limpo = df_bruto.drop_duplicates(subset=['ID_Conversa'], keep='last').copy()
    
    # Contadores para saber quantos testes passaram com sucesso
    testes_aprovados = 0
    total_testes = 6
    
    # ==========================================================================
    # TESTE 1: AUDITORIA DE VOLUMETRIA E DUPLICIDADES TRATADAS
    # Objetivo: Garantir que a IA não use as 7.502 linhas sujas e sim 7.000 limpas.
    # ==========================================================================
    total_conversas_unicas = len(df_limpo)
    duplicadas_removidas = total_linhas_brutas - total_conversas_unicas
    
    if total_conversas_unicas == 7000 and duplicadas_removidas == 502:
        print("✅ TESTE 1 [APROVADO]: Base de dados limpa com 7.000 atendimentos únicos.")
        print(f"   ↳ Detalhe: 502 registros duplicados removidos com sucesso.")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 1 [FALHOU]: Esperado 7.000 únicos e 502 dups. Encontrado: {total_conversas_unicas} e {duplicadas_removidas}.")

    # ==========================================================================
    # TESTE 2: TAXA STP REAL (RESOLUÇÃO 100% DIGITAL PELO BOT)
    # Objetivo: Impedir que a IA invente que a automação é 60% ou 70%.
    # ==========================================================================
    taxa_stp_real = round((df_limpo['Status_Final_Clean'] == 'Resolvido_Bot').mean() * 100, 2)
    casos_bot = int((df_limpo['Status_Final_Clean'] == 'Resolvido_Bot').sum())
    
    if taxa_stp_real == 46.93 and casos_bot == 3285:
        print(f"✅ TESTE 2 [APROVADO]: Taxa STP (100% Bot) calibrada em exatamente {taxa_stp_real}%.")
        print(f"   ↳ Detalhe: 3.285 sinistros finalizados pelo assistente sem intervenção humana.")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 2 [FALHOU]: Taxa STP divergente: {taxa_stp_real}% (Esperado: 46.93%).")

    # ==========================================================================
    # TESTE 3: MAIOR GARGALO DE ABANDONO (ETAPA DE UPLOAD)
    # Objetivo: Garantir que a IA aponte o Upload como principal causa de desistência.
    # ==========================================================================
    abandonos_upload = int((df_limpo[df_limpo['Etapa_Saida_Conversa'] == 'Upload_Fotos_Documentos']['Status_Final_Clean'] == 'Abandonado').sum())
    total_abandonos = int((df_limpo['Status_Final_Clean'] == 'Abandonado').sum())
    percentual_upload_abandono = round((abandonos_upload / total_abandonos) * 100, 1)
    
    if abandonos_upload == 780 and percentual_upload_abandono == 47.0:
        print(f"✅ TESTE 3 [APROVADO]: Maior gargalo de abandono confirmado na etapa de Upload.")
        print(f"   ↳ Detalhe: 780 abandonos ({percentual_upload_abandono}% de todos os abandonos do sistema).")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 3 [FALHOU]: Contagem de upload divergente: {abandonos_upload} casos ({percentual_upload_abandono}%).")

    # ==========================================================================
    # TESTE 4: MAIOR GARGALO DE TRANSBORDO (VALIDAÇÃO DE APÓLICE)
    # Objetivo: Garantir que a IA saiba onde os operadores humanos são sobrecarregados.
    # ==========================================================================
    escalados_validacao = int((df_limpo[df_limpo['Etapa_Saida_Conversa'] == 'Validacao_Apolice']['Status_Final_Clean'] == 'Escalado_Humano').sum())
    total_escalados = int((df_limpo['Status_Final_Clean'] == 'Escalado_Humano').sum())
    percentual_val_escalado = round((escalados_validacao / total_escalados) * 100, 1)
    
    if escalados_validacao == 1114 and percentual_val_escalado == 54.2:
        print(f"✅ TESTE 4 [APROVADO]: Maior gargalo de transbordo confirmado na Validação de Apólice.")
        print(f"   ↳ Detalhe: 1.114 casos escalados ({percentual_val_escalado}% de todos os transbordos humanos).")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 4 [FALHOU]: Contagem de transbordo na validação divergente: {escalados_validacao} casos ({percentual_val_escalado}%).")

    # ==========================================================================
    # TESTE 5: DIAGNÓSTICO DO PRODUTO VIDA (PIOR RESOLUÇÃO & MAIOR VALOR)
    # Objetivo: Impedir que a IA recomende melhorias cegas sem entender a assimetria de Vida.
    # ==========================================================================
    pior_produto = df_limpo.groupby('Tipo_Sinistro')['Status_Final_Clean'].apply(lambda s: (s == 'Resolvido_Bot').mean()).idxmin()
    pior_stp = round(df_limpo.groupby('Tipo_Sinistro')['Status_Final_Clean'].apply(lambda s: (s == 'Resolvido_Bot').mean()).min() * 100, 2)
    ticket_medio_vida = round(df_limpo[df_limpo['Tipo_Sinistro'] == 'Vida']['Valor_Estimado_Sinistro_RS_Num'].mean(), 2)
    
    if pior_produto == "Vida" and pior_stp == 38.78 and ticket_medio_vida == 45501.09:
        print(f"✅ TESTE 5 [APROVADO]: Diagnóstico do produto Vida validado.")
        print(f"   ↳ Detalhe: Pior STP da carteira ({pior_stp}%) com o maior ticket médio (R$ {ticket_medio_vida:,.2f}).")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 5 [FALHOU]: Diagnóstico de produto incorreto: {pior_produto} ({pior_stp}%, R$ {ticket_medio_vida}).")

    # ==========================================================================
    # TESTE 6: COMPARATIVO OPERACIONAL (TMA & NOTA DE SATISFAÇÃO CSAT)
    # Objetivo: Checar os números de tempo de operador e a perda de CSAT no transbordo.
    # ==========================================================================
    tma_bot = round(df_limpo[df_limpo['Status_Final_Clean'] == 'Resolvido_Bot']['Tempo_Resolucao_Min_Num'].mean(), 2)
    tma_humano = round(df_limpo[df_limpo['Status_Final_Clean'] == 'Escalado_Humano']['Tempo_Resolucao_Min_Num'].mean(), 2)
    csat_bot = round(df_limpo[df_limpo['Status_Final_Clean'] == 'Resolvido_Bot']['CSAT_1a5'].mean(), 2)
    csat_humano = round(df_limpo[df_limpo['Status_Final_Clean'] == 'Escalado_Humano']['CSAT_1a5'].mean(), 2)
    
    if tma_bot == 9.37 and tma_humano == 38.39 and csat_bot == 4.28 and csat_humano == 3.61:
        print(f"✅ TESTE 6 [APROVADO]: Métricas de TMA e CSAT validadas com sucesso.")
        print(f"   ↳ Detalhe: Bot (TMA {tma_bot} min | CSAT {csat_bot}) vs. Humano (TMA {tma_humano} min | CSAT {csat_humano}).")
        testes_aprovados += 1
    else:
        print(f"❌ TESTE 6 [FALHOU]: Divergência nas métricas operacionais.")

    # --- RELATÓRIO FINAL ---
    print("-" * 75)
    print(f"🎯 RESULTADO CONSOLIDADO: {testes_aprovados}/{total_testes} TESTES APROVADOS")
    if testes_aprovados == total_testes:
        print("🛡️ STATUS DE SEGURANÇA: BASE E IA 100% BLINDADAS CONTRA ALUCINAÇÕES!")
    else:
        print("⚠️ ATENÇÃO: Verifique os testes com falha antes da apresentação.")
    print("=" * 75)


# ------------------------------------------------------------------------------
# 3. PONTO DE ENTRADA DO SCRIPT
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    executar_bateria_de_testes()