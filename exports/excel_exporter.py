from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


class ExcelExporter:

    def exportar(self, dados, arquivo="relatorio_rpv.xlsx"):
        wb = Workbook()
        ws = wb.active
        ws.title = "RPV"

        # Garantir exibição das linhas de grade
        ws.views.sheetView[0].showGridLines = True

        # Congelar a primeira linha (cabeçalho sempre visível ao rolar)
        ws.freeze_panes = "A2"

        # -------------------------------------------------------------
        # ESTILOS VISUAIS (PALETA DE CORES JURÍDICA/CORPORATIVA)
        # -------------------------------------------------------------
        # Cabeçalho: Azul Escuro com texto branco
        fill_header = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
        font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")

        # Linhas Alternadas (Zebra)
        fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        # Fontes de Dados e Hyperlink
        font_data = Font(name="Segoe UI", size=10, color="333333")
        font_link = Font(name="Segoe UI", size=10, color="0056B3", underline="single")

        # Bordas Sutis (Cinza Claro)
        thin_border_side = Side(border_style="thin", color="E0E0E0")
        border_cell = Border(
            left=thin_border_side,
            right=thin_border_side,
            top=thin_border_side,
            bottom=thin_border_side
        )

        # Alinhamentos
        align_center = Alignment(horizontal="center", vertical="center")
        align_left = Alignment(horizontal="left", vertical="center")

        # -------------------------------------------------------------
        # 1. CRIAÇÃO DO CABEÇALHO
        # -------------------------------------------------------------
        headers = ["Número Processo", "Vara", "Banco", "Nº RPV"]
        ws.append(headers)
        ws.row_dimensions[1].height = 28  # Altura elegante para o cabeçalho

        for col_num, cell in enumerate(ws[1], start=1):
            cell.fill = fill_header
            cell.font = font_header
            cell.alignment = align_center if col_num in [2, 4] else align_left
            cell.border = border_cell

        # -------------------------------------------------------------
        # 2. PREENCHIMENTO DOS DADOS
        # -------------------------------------------------------------
        for idx, item in enumerate(dados, start=2):
            ws.row_dimensions[idx].height = 22  # Espaçamento confortável por linha
            fill_atual = fill_zebra if idx % 2 == 0 else fill_white

            # Coluna 1: Número Processo (Link)
            cell_proc = ws.cell(row=idx, column=1, value=item.get("numero", ""))
            link_url = item.get("link", "")
            if link_url:
                cell_proc.hyperlink = link_url
                cell_proc.font = font_link
            else:
                cell_proc.font = font_data
            cell_proc.alignment = align_left

            # Coluna 2: Vara
            cell_vara = ws.cell(row=idx, column=2, value=item.get("vara", ""))
            cell_vara.font = font_data
            cell_vara.alignment = align_center

            # Coluna 3: Banco
            cell_banco = ws.cell(row=idx, column=3, value=item.get("banco", ""))
            cell_banco.font = font_data
            cell_banco.alignment = align_left

            # Coluna 4: Nº RPV
            cell_rpv = ws.cell(row=idx, column=4, value=item.get("rpv", ""))
            cell_rpv.font = font_data
            cell_rpv.alignment = align_center

            # Aplicação de fundo zebra e bordas em todas as células da linha
            for col in range(1, 5):
                c = ws.cell(row=idx, column=col)
                c.fill = fill_atual
                c.border = border_cell

        # -------------------------------------------------------------
        # 3. LARGURA AUTOMÁTICA DAS COLUNAS (AUTOFIT)
        # -------------------------------------------------------------
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or '')
                if len(val) > max_len:
                    max_len = len(val)
            
            # Define margem extra para respiração do texto
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

        wb.save(arquivo)
        return arquivo