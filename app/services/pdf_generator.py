from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, 
    PageTemplate, 
    Frame, 
    Paragraph, 
    Spacer, 
    Image, 
    Table, 
    TableStyle, 
    PageBreak,
    NextPageTemplate
)
from reportlab.graphics.shapes import Drawing, Line
import os
from datetime import datetime
from app.utils.formatters import formatar_moeda_br

class PDFGenerator:
    
    # Paleta de Cores Level5
    COR_AZUL_ESCURO = HexColor('#1B2A41')
    COR_TEAL = HexColor('#16A085')
    COR_LARANJA = HexColor('#F39C12')
    COR_CINZA = HexColor('#7F8C8D')
    COR_CINZA_CLARO = HexColor('#ECF0F1')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        
        # CAMINHOS DAS IMAGENS
        # 'background_capa_full.jpg': Imagem da capa JÁ com títulos e logo grande.
        # A parte inferior (branca) deve estar limpa para receber o nome do cliente.
        self.background_capa = 'app/assets/background_capa_full.jpg' 
        
        # 'logo-level5.png': Logo branca/transparente para o cabeçalho das páginas internas.
        self.logo_path = 'app/assets/logo-level5.png'
    
    def _criar_estilos_customizados(self):
        # --- Estilos da Capa ---
        self.styles.add(ParagraphStyle(
            name='LabelClienteCapa',
            fontSize=14,
            textColor=self.COR_AZUL_ESCURO,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=5
        ))

        self.styles.add(ParagraphStyle(
            name='NomeClienteCapa',
            fontSize=24,
            textColor=self.COR_TEAL,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=28
        ))

        # --- Estilos Gerais ---
        self.styles.add(ParagraphStyle(
            name='SecaoTitulo',
            fontSize=16,
            textColor=self.COR_AZUL_ESCURO,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceBefore=15,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='Corpo',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceBefore=3,
            spaceAfter=6,
            leading=16
        ))

    def _draw_cover(self, canvas, doc):
        """Desenha APENAS a imagem de fundo da capa na página inteira"""
        canvas.saveState()
        page_width, page_height = A4
        
        if os.path.exists(self.background_capa):
            canvas.drawImage(self.background_capa, 0, 0, width=page_width, height=page_height)
        
        canvas.restoreState()

    def _draw_header_footer(self, canvas, doc):
        """Cabeçalho e Rodapé das páginas internas"""
        canvas.saveState()
        page_width, page_height = A4
        
        # --- CABEÇALHO (Fundo Azul para logo branca) ---
        header_height = 3.0 * cm
        
        # Retângulo Azul
        canvas.setFillColor(self.COR_AZUL_ESCURO)
        canvas.rect(0, page_height - header_height, page_width, header_height, fill=1, stroke=0)
        
        # Linha Laranja Decorativa
        canvas.setFillColor(self.COR_LARANJA)
        canvas.rect(0, page_height - header_height, page_width, 0.1*cm, fill=1, stroke=0)
        
        # Logo (Superior Direito)
        if os.path.exists(self.logo_path):
            # Logo grande (5.0cm) para destaque no cabeçalho
            logo_width = 5.0 * cm
            logo_height = 1.8 * cm 
            margin_right = 1.0 * cm
            
            # Centraliza verticalmente no header azul
            y_pos = page_height - (header_height / 2) - (logo_height / 2)
            
            canvas.drawImage(
                self.logo_path, 
                page_width - logo_width - margin_right, 
                y_pos, 
                width=logo_width, 
                height=logo_height, 
                mask='auto'
            )
            
        # Texto do Cabeçalho (Esquerda)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.setFillColor(white)
        canvas.drawString(2 * cm, page_height - 1.8 * cm, "PROPOSTA TÉCNICA E COMERCIAL")
        
        # --- RODAPÉ ---
        canvas.setStrokeColor(self.COR_CINZA_CLARO)
        canvas.line(2*cm, 1.5*cm, page_width - 2*cm, 1.5*cm)
        
        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(self.COR_CINZA)
        canvas.drawString(2*cm, 1*cm, "Level5 Engenharia Elétrica")
        canvas.drawRightString(page_width - 2*cm, 1*cm, f"Página {doc.page}")
        
        canvas.restoreState()

    def gerar_proposta_plana(self, nome_cliente, modulos_quantidade, especificacoes_modulo, 
                           inversores_quantidade, especificacoes_inversores, investimento_kit, 
                           investimento_mao_de_obra, investimento_total, grafico_producao_path, 
                           tabela_retorno_path, ano_payback, valor_payback, economia_25_anos, output_path):
        
        doc = BaseDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3.5*cm,
            bottomMargin=2*cm
        )
        
        frame_normal = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 3.5*cm, id='normal')
        
        template_capa = PageTemplate(id='Capa', frames=[frame_normal], onPage=self._draw_cover)
        template_conteudo = PageTemplate(id='Conteudo', frames=[frame_normal], onPage=self._draw_header_footer)
        
        doc.addPageTemplates([template_capa, template_conteudo])
        
        story = []
        
        # --- PÁGINA 1: CAPA ---
        story.append(Spacer(1, 16*cm)) 
        story.append(Paragraph("CLIENTE:", self.styles['LabelClienteCapa']))
        story.append(Paragraph(nome_cliente.upper(), self.styles['NomeClienteCapa']))
        story.append(NextPageTemplate('Conteudo'))
        story.append(PageBreak())
        
        # --- PÁGINA 2 ---
        story.append(Paragraph("QUEM SOMOS?", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        texto_quem_somos = """Somos uma empresa especializada no segmento de engenharia elétrica, com foco no desenvolvimento de projetos elétricos e na instalação de sistemas fotovoltaicos. Desde 2019, temos trabalhado para oferecer soluções eficientes e sustentáveis, sempre com alto padrão de qualidade. Ao longo de nossa trajetória, já realizamos mais de 700 projetos fotovoltaicos, contribuindo para a geração de energia limpa e a redução de custos energéticos de nossos clientes. Nosso compromisso é entregar excelência em cada etapa do processo, desde o planejamento até a execução, garantindo resultados que superam expectativas."""
        story.append(Paragraph(texto_quem_somos, self.styles['Corpo']))
        
        story.append(Paragraph("FUNCIONAMENTO DO SISTEMA FOTOVOLTAICO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        texto_func = """O sistema fotovoltaico é composto principalmente por três componentes: painéis solares, inversor e medidor bidirecional. Os painéis captam a energia solar e a convertem em energia elétrica de corrente contínua (CC). Em seguida, o inversor transforma essa corrente contínua em corrente alternada (CA), que pode ser utilizada pelos equipamentos elétricos. O medidor bidirecional desempenha um papel essencial ao monitorar a energia produzida pelo sistema. Ele controla o fluxo de energia, permitindo o uso da eletricidade da concessionária quando necessário e acumulando créditos para a energia excedente gerada pelo sistema solar. Isso elimina a necessidade de baterias para armazenar a energia excedente, tornando o sistema mais econômico e eficiente."""
        story.append(Paragraph(texto_func, self.styles['Corpo']))

        story.append(Paragraph("DESCRIÇÃO DOS ITENS:", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph(f"• {modulos_quantidade} {especificacoes_modulo}", self.styles['Corpo']))
        story.append(Paragraph(f"• {inversores_quantidade} Inversor(es) {especificacoes_inversores}", self.styles['Corpo']))
        
        story.append(Paragraph("GARANTIA", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph("A garantia do sistema fotovoltaico é composta por:", self.styles['Corpo']))
        garantias = [
            "<b>Módulos Fotovoltaicos:</b> Garantia de desempenho linear de 25 anos e garantia contra defeitos de fabricação de 15 anos, fornecida pelo fabricante.",
            "<b>Inversor:</b> Garantia de 10 anos contra defeitos de fabricação, conforme especificado pelo fabricante.",
            "<b>Estrutura de Fixação:</b> Garantia contra corrosão e defeitos de fabricação, de acordo com as especificações do fabricante.",
            "<b>Serviço de Instalação:</b> Garantia de 1 ano, cobrindo a qualidade e a execução técnica do serviço realizado."
        ]
        for g in garantias:
            story.append(Paragraph(f"• {g}", self.styles['Corpo']))

        story.append(PageBreak())
        
        # --- PÁGINA 3 ---
        story.append(Paragraph("INVESTIMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        dados_inv = [
            ['DESCRIÇÃO', 'VALOR'],
            ['Kit Fotovoltaico', formatar_moeda_br(investimento_kit)],
            ['Mão de Obra e Projetos', formatar_moeda_br(investimento_mao_de_obra)],
            ['INVESTIMENTO TOTAL', formatar_moeda_br(investimento_total)]
        ]
        
        t_inv = Table(dados_inv, colWidths=[11*cm, 5*cm])
        t_inv.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,0), (-1,0), white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), self.COR_AZUL_ESCURO),
            ('TEXTCOLOR', (0,-1), (-1,-1), white),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (1,1), (-1,-2), [white, self.COR_CINZA_CLARO]),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('TOPPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(t_inv)
        
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("FORMAS DE PAGAMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        story.append(Paragraph("Oferecemos diversas formas de pagamento para facilitar a aquisição do seu sistema fotovoltaico. Entre as opções disponíveis estão:", self.styles['Corpo']))
        
        pagamentos = [
            "<b>Pagamento à Vista:</b> Desconto especial para pagamentos realizados à vista.",
            "<b>Financiamento Bancário:</b> Parcerias com instituições financeiras que permitem financiar o sistema em até 120 meses, com condições acessíveis e taxas competitivas.",
            "<b>Pagamento Parcelado:</b> Possibilidade de parcelamento direto no cartão."
        ]
        for p in pagamentos:
            story.append(Paragraph(f"• {p}", self.styles['Corpo']))
        
        story.append(Paragraph("Todas as opções são planejadas para proporcionar flexibilidade e viabilizar o investimento em energia solar de forma prática e acessível.", self.styles['Corpo']))

        story.append(Spacer(1, 0.5*cm))

        # --- SEÇÃO DIFERENCIAL ---
        story.append(Paragraph("DIFERENCIAL!", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        texto_diferencial = """Em parceria com a Yelum Seguradora, disponibilizamos uma excelente opção de seguro para os equipamentos do seu sistema fotovoltaico, proporcionando proteção completa e total tranquilidade. O valor do seguro varia entre 1% e 1,5% do custo total do sistema por ano e oferece cobertura para:"""
        story.append(Paragraph(texto_diferencial, self.styles['Corpo']))
        
        seguros = [
            "Danos acidentais de origem externa;",
            "Vendavais e chuvas de granizo;",
            "Incêndios, quedas de raio e explosões;",
            "Roubo ou furto."
        ]
        for s in seguros:
            story.append(Paragraph(f"• {s}", self.styles['Corpo']))
            
        texto_dif_final = """Essa parceria reforça nosso compromisso em oferecer não apenas soluções de qualidade e eficiência, mas também a segurança necessária para o seu investimento em energia solar. Caso tenha interesse, realizamos a simulação do valor do seguro no momento do fechamento do projeto fotovoltaico e finalizamos o processo diretamente com a seguradora."""
        story.append(Paragraph(texto_dif_final, self.styles['Corpo']))

        story.append(PageBreak())
        
        # --- PÁGINA 4 ---
        story.append(Paragraph("CUSTO X BENEFÍCIO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        story.append(Paragraph("O gráfico abaixo ilustra a produção estimada de energia mês a mês. Essa estimativa considera a variação de irradiância solar ao longo do ano, garantindo uma visão realista do desempenho do sistema em diferentes períodos.", self.styles['Corpo']))
        
        if os.path.exists(grafico_producao_path):
            story.append(Image(grafico_producao_path, width=16*cm, height=8*cm))
            
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("RETORNO DO INVESTIMENTO", self.styles['SecaoTitulo']))
        story.append(self._criar_linha_divisoria())
        
        story.append(Paragraph("Uma das etapas mais importantes para avaliar o custo-benefício do sistema fotovoltaico é o cálculo do retorno sobre o investimento. Com base na tarifa atual de energia elétrica, considerando um reajuste médio ao ano, projetamos os seguintes resultados:", self.styles['Corpo']))
        
        if ano_payback:
            story.append(Paragraph(f"• <b>Lucro a partir do {ano_payback}º ano:</b> O sistema começará a gerar um retorno acumulado de <b>{formatar_moeda_br(valor_payback)}</b>", self.styles['Corpo']))
            story.append(Paragraph(f"• <b>Retorno significativo em 25 anos:</b> Economia acumulada de <b>{formatar_moeda_br(economia_25_anos)}</b>", 
                                   ParagraphStyle('Highlight', parent=self.styles['Corpo'], textColor=self.COR_TEAL, fontSize=14)))
        
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph("Com essas premissas, o investimento no sistema fotovoltaico se mostra altamente vantajoso, garantindo economia no curto prazo e uma valorização significativa no longo prazo.", self.styles['Corpo']))
        story.append(Spacer(1, 0.3*cm))

        if os.path.exists(tabela_retorno_path):
            # Tabela inserida com proporção preservada para evitar distorção
            img_tabela = Image(tabela_retorno_path, width=16*cm, height=18*cm, preserveAspectRatio=True)
            img_tabela.hAlign = 'CENTER'
            story.append(img_tabela)

        doc.build(story)

    def _criar_linha_divisoria(self):
        d = Drawing(400, 5)
        d.add(Line(0, 0, 460, 0, strokeColor=self.COR_LARANJA, strokeWidth=2))
        return d
