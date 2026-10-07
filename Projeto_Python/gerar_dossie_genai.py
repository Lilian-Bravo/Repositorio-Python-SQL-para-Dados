import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFillColor(HexColor("#0066FF"))
        self.rect(54, 755, 504, 3, fill=True, stroke=False)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(HexColor("#64748B"))
        self.drawString(54, 742, "BLIP x CONVEX SEGUROS | SENIOR DATA STRATEGIST ETAPA TECNICA")
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#94A3B8"))
        self.drawString(54, 36, "Dossie de Governanca & Metodologia GenAI - Estritamente Confidencial")
        self.drawRightString(558, 36, f"Pagina {self._pageNumber} de {page_count}")
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf():
    # Salva diretamente na mesma pasta onde este script esta
    pasta_destino = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(pasta_destino, "Dossie_Metodologia_Orquestracao_GenAI.pdf")
    
    doc = SimpleDocTemplate(
        caminho_completo,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    c_navy = HexColor("#0A192F")
    c_blue = HexColor("#0066FF")
    c_dark = HexColor("#0F172A")
    c_muted = HexColor("#475569")
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=c_navy, spaceAfter=3)
    subtitle_style = ParagraphStyle('DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, textColor=c_muted, spaceAfter=12)
    h1_style = ParagraphStyle('SectionH1', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=16, textColor=c_blue, spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyDark', parent=styles['Normal'], fontName='Helvetica', fontSize=8.5, leading=12.5, textColor=c_dark, spaceAfter=6)
    callout_style = ParagraphStyle('CalloutText', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=11.5, textColor=HexColor("#1E293B"))
    table_cell = ParagraphStyle('TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=7.5, leading=10.5, textColor=c_dark)
    table_cell_bold = ParagraphStyle('TableCellBold', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=7.5, leading=10.5, textColor=c_navy)

    story = []

    # Titulo
    story.append(Paragraph("Dossie Tecnico: Metodologia & Orquestracao de GenAI", title_style))
    story.append(Paragraph("Relatorio Comprobatorio de Uso, Engenharia de Prompts e Supervisao Humana (Item 7 do Case)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=0.8, color=HexColor("#E2E8F0"), spaceAfter=8))

    # Secao 1: Modelos
    story.append(Paragraph("1. Estrategia de Arquitetura Multi-Modelo & Ferramental", h1_style))
    story.append(Paragraph("Adotou-se uma arquitetura multi-modelo para selecionar a tecnologia ideal para cada desafio analitico:", body_style))

    data_t1 = [
        [Paragraph("<b>Modelo / Ferramenta</b>", table_cell_bold),
         Paragraph("<b>Etapa do Projeto</b>", table_cell_bold),
         Paragraph("<b>Motivo da Escolha Tecnica</b>", table_cell_bold),
         Paragraph("<b>Entrega / Artefato Produzido</b>", table_cell_bold)],
        [Paragraph("<b>Claude 3.5 Sonnet</b>", table_cell), Paragraph("EDA e Limpeza de Dados", table_cell), Paragraph("Raciocinio logico superior e sintaxe Python moderna.", table_cell), Paragraph("Pipeline de saneamento e remocao de duplicatas.", table_cell)],
        [Paragraph("<b>GPT-4o</b>", table_cell), Paragraph("Modelagem Financeira", table_cell), Paragraph("Conversao rapida de metricas operacionais em demonstrativos de resultado.", table_cell), Paragraph("Matriz de sensibilidade e projecao anualizada de custos.", table_cell)],
        [Paragraph("<b>Gemini 1.5 Pro</b>", table_cell), Paragraph("Varredura Contextual de PDFs", table_cell), Paragraph("Janela de contexto longa para confronto do edital com a base.", table_cell), Paragraph("Mapeamento das 6 etapas do funil de sinistros.", table_cell)],
        [Paragraph("<b>Python-PPTX & Streamlit</b>", table_cell), Paragraph("Construcao dos Artefatos", table_cell), Paragraph("Geracao programatica e deterministica sem depender de layouts manuais.", table_cell), Paragraph("Painel web interativo e deck de 10 slides em 16:9.", table_cell)]
    ]
    t1 = Table(data_t1, colWidths=[80, 110, 150, 164])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))

    # Secao 2: Prompts
    story.append(Paragraph("2. Engenharia de Prompts: Estruturacao, Iteracoes e Raciocinio", h1_style))
    prompts_data = [
        [Paragraph("<b>Prompt #01 - Auditoria Inicial de Producao:</b><br/>"
                   "<i>'Inspecione a integridade da base: volumetria bruta vs. IDs unicos, casing em Status_Final, separadores decimais e anomalias de data. Calcule a frequencia absoluta de desfechos e valide chave primaria.'</i><br/>"
                   "<b>Resultado / Iteracao:</b> Descoberta das 502 linhas duplicadas no lote de 10 a 24 de marco decorrentes de falha de ingestao de logs.", callout_style)],
        [Paragraph("<b>Prompt #02 - Diagnostico de Causa-Raiz & Segmentacao Cruzada:</b><br/>"
                   "<i>'Cruze a Etapa_Saida_Conversa com Tipo_Sinistro, Segmento_Cliente e Canal. Identifique assimetrias de transbordo e abandono: por que Seguro Vida perde na etapa 2 enquanto Auto perde na etapa 4?'</i><br/>"
                   "<b>Resultado / Iteracao:</b> Identificacao do paradoxo de Vida (pior STP 38,8% e maior ticket R$ 45,5k por bloqueio de CPF de herdeiro/beneficiario).", callout_style)],
        [Paragraph("<b>Prompt #03 - Blindagem Matematica Anti-Alucinacao:</b><br/>"
                   "<i>'Desenvolva testes unitarios em Python para 6 verdades: volumetria (7.000), taxa STP (46,93%), abandono upload (780), transbordo validacao (1.114), ticket Vida (R$ 45,5k) e TMA (9,37m vs 38,39m).'</i><br/>"
                   "<b>Resultado / Iteracao:</b> Script testar_ia.py com 100% de aprovacao.", callout_style)]
    ]
    t_prompts = Table(prompts_data, colWidths=[504])
    t_prompts.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.8, HexColor("#0066FF")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_prompts)

    story.append(PageBreak())

    # Secao 3: Validacao Humana
    story.append(Paragraph("3. Governanca e Validacao Humana (Human-in-the-Loop): Deteccao de Anomalias", h1_style))
    val_data = [
        [Paragraph("<b>Anomalia Detectada</b>", table_cell_bold), Paragraph("<b>Risco de Alucinacao</b>", table_cell_bold), Paragraph("<b>Acao Corretiva Humana</b>", table_cell_bold)],
        [Paragraph("<b>502 Linhas Duplicadas</b>", table_cell), Paragraph("A IA poderia calcular metricas com base em 7.502 sessoes distorcendo custos.", table_cell), Paragraph("Deduplicacao estrita consolidando a base em 7.000 sessoes unicas oficiais.", table_cell)],
        [Paragraph("<b>Ponto Cego de CSAT</b>", table_cell), Paragraph("Concluir satisfacao alta com a media nominal de 4,02/5.0 exibida.", table_cell), Paragraph("Auditoria comprovou que os 1.658 abandonos possuem nota nula (mascarando 23,7% da base).", table_cell)],
        [Paragraph("<b>Casing Heterogeneo</b>", table_cell), Paragraph("Contabilizar variantes de texto como categorias diferentes.", table_cell), Paragraph("Padronizacao estrita em 3 desfechos unicos no pipeline de dados.", table_cell)],
        [Paragraph("<b>Anualizacao (x3)</b>", table_cell), Paragraph("Projetar impacto anual sem considerar que a base cobre apenas 4 meses.", table_cell), Paragraph("Aplicacao do multiplicador temporal x3 para calcular R$ 157,9k de OPEX e R$ 57,6M em risco.", table_cell)]
    ]
    t_val = Table(val_data, colWidths=[130, 180, 194])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 10))

    # Secao 4: Blindagem
    story.append(Paragraph("4. Blindagem do Dashboard e Autonomia Analitica", h1_style))
    story.append(Paragraph(
        "• <b>Prompt Grounding Deterministico:</b> A Aba 4 do Streamlit recebe indicadores pre-calculados em Python, impedindo invencoes.<br/>"
        "• <b>Testes Unitarios Integrados:</b> Validacao continua dos 6 indicadores com tolerancia zero para desvios estatisticos.<br/>"
        "• <b>Simulacao Interativa (Stress Test):</b> Controles deslizantes para alterar custos de hora humana e metas em tempo real.",
        body_style
    ))
    story.append(Spacer(1, 10))

    sign_data = [[Paragraph("<b>Conclusao Metodologica:</b> A IA Generativa atuou como aceleradora de produtividade e construcao de artefatos, sob estrita governanca de dados e supervisao estrategica humana.", callout_style)]]
    t_sign = Table(sign_data, colWidths=[504])
    t_sign.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, HexColor("#0066FF")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("\n" + "="*60)
    print("PDF GERADO COM SUCESSO!")
    print(f"Arquivo salvo em: {caminho_completo}")
    print("="*60 + "\n")

# Executa imediatamente a funcao
build_pdf()