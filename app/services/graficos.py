import matplotlib
matplotlib.use('Agg')  # Backend não-interativo

import matplotlib.pyplot as plt
import numpy as np
from typing import List
import os
import uuid

from app.models.proposta import ProducaoMensalModel, RetornoInvestimentoModel
from app.utils.formatters import formatar_moeda_br, formatar_numero_br

class GraficoService:
    """Serviço para geração de gráficos da proposta com Design Level5"""
    
    # PALETA DE CORES
    COR_AZUL_ESCURO = '#1B2A41'
    COR_TEAL = '#16A085'
    COR_LARANJA = '#F39C12'
    COR_CINZA = '#7F8C8D'
    COR_FUNDO = '#FFFFFF'
    COR_VERMELHO = '#C0392B' 
    
    def gerar_grafico_producao(
        self,
        dados_producao: List[ProducaoMensalModel],
        quantidade_modulos: int,
        output_dir: str
    ) -> str:
        # Preparar dados
        meses = []
        geracao_total = []
        geracao_por_placa = []
        
        for item in dados_producao:
            if isinstance(item.mes, int):
                meses.append(str(item.mes))
            else:
                meses.append('MÉD')
            
            geracao_total.append(item.geracao_total)
            val_placa = item.geracao_total / quantidade_modulos if quantidade_modulos > 0 else 0
            geracao_por_placa.append(val_placa)
        
        # Configurar figura
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        fig.patch.set_facecolor(self.COR_FUNDO)
        ax.set_facecolor(self.COR_FUNDO)
        
        # Posições das barras
        x = np.arange(len(meses))
        width = 0.35
        
        # Barras
        bars1 = ax.bar(x - width/2, geracao_por_placa, width, 
                      label='Geração por Placa', color=self.COR_AZUL_ESCURO,
                      edgecolor=self.COR_FUNDO, linewidth=0)
        
        bars2 = ax.bar(x + width/2, geracao_total, width, 
                      label='Geração Total Estimada', color=self.COR_TEAL,
                      edgecolor=self.COR_FUNDO, linewidth=0)
        
        # Rótulos
        def add_labels(bars, color):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=7, fontweight='bold',
                           color=color)

        add_labels(bars1, self.COR_AZUL_ESCURO)
        add_labels(bars2, self.COR_AZUL_ESCURO)
        
        # Eixos
        ax.set_xticks(x)
        ax.set_xticklabels(meses, fontsize=9, color=self.COR_AZUL_ESCURO, fontweight='bold')
        ax.set_yticks([])
        ax.tick_params(axis='x', length=0)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.axhline(y=0, color=self.COR_AZUL_ESCURO, linewidth=2)
        
        # Legenda no fundo
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), 
                 ncol=2, frameon=False, fontsize=9)
        
        # Título
        ax.set_title('PRODUÇÃO MENSAL (kWh)', fontsize=11, fontweight='bold', 
                    color=self.COR_AZUL_ESCURO, pad=20)
        
        plt.tight_layout()
        
        # Salvar
        filename = f"grafico_producao_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor=self.COR_FUNDO)
        plt.close(fig)
        
        return filepath
    
    def gerar_tabela_retorno(
        self,
        dados_retorno: List[RetornoInvestimentoModel],
        output_dir: str
    ) -> str:
        dados_tabela = []
        for item in dados_retorno:
            saldo_str = f"R$ {formatar_numero_br(item.saldo)}"
            if item.saldo < 0:
                saldo_str = f"-R$ {formatar_numero_br(abs(item.saldo))}"
            
            # ADICIONADO: Coluna de Economia Mensal que faltava
            dados_tabela.append([
                str(item.ano),
                saldo_str,
                f"R$ {formatar_numero_br(item.economia_mensal)}",
                f"R$ {formatar_numero_br(item.economia_anual)}"
            ])
        
        # Aumentada a largura para 10 polegadas para caber as 4 colunas confortavelmente
        fig_height = len(dados_tabela) * 0.4 + 1.2
        fig, ax = plt.subplots(figsize=(10, fig_height), dpi=300)
        
        fig.patch.set_facecolor(self.COR_FUNDO)
        ax.axis('off')
        
        headers = ['ANO', 'SALDO ACUMULADO', 'ECONOMIA MÉDIA MENSAL', 'ECONOMIA ANUAL']
        
        table = ax.table(
            cellText=dados_tabela,
            colLabels=headers,
            loc='center',
            cellLoc='center',
            colLoc='center'
        )
        
        # Estilização
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.8)
        
        for (row, col), cell in table.get_celld().items():
            cell.set_edgecolor('#ECF0F1')
            cell.set_linewidth(1)
            
            if row == 0:
                cell.set_facecolor(self.COR_AZUL_ESCURO)
                cell.set_text_props(color='white', weight='bold')
                cell.set_height(0.06)
            else:
                if row % 2 == 0:
                    cell.set_facecolor('#F8F9FA')
                else:
                    cell.set_facecolor(self.COR_FUNDO)
                
                cell.set_text_props(color='#333333')
                
                # Coluna Saldo (índice 1) com cores
                if col == 1:
                    valor_txt = dados_tabela[row-1][1]
                    if '-' in valor_txt:
                        cell.set_text_props(color=self.COR_VERMELHO, weight='bold')
                    else:
                        cell.set_text_props(color=self.COR_TEAL, weight='bold')

        filename = f"tabela_retorno_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight', pad_inches=0.05)
        plt.close(fig)
        
        return filepath
