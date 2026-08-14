import os
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    Alignment,
    PatternFill,
    Border,
    Side
)
from openpyxl.utils import get_column_letter


class ExcelExporter:

    def __init__(self):

        # ============================================================
        # PASTA DE SAÍDA
        # ============================================================

        documentos = os.path.join(
            os.path.expanduser("~"),
            "Documents"
        )

        self.pasta_saida = os.path.join(
            documentos,
            "AutoJuris IA"
        )

        # Cria a pasta automaticamente
        os.makedirs(
            self.pasta_saida,
            exist_ok=True
        )

    # ================================================================
    # EXPORTAR
    # ================================================================

    def exportar(
        self,
        dados,
        arquivo="relatorio_rpv.xlsx"
    ):

        # ------------------------------------------------------------
        # CAMINHO COMPLETO
        # ------------------------------------------------------------

        caminho = os.path.join(
            self.pasta_saida,
            arquivo
        )

        # ------------------------------------------------------------
        # SE O ARQUIVO ESTIVER ABERTO NO EXCEL
        # ------------------------------------------------------------

        if os.path.exists(caminho):

            try:

                # Testa se conseguimos abrir para escrita
                with open(
                    caminho,
                    "a"
                ):
                    pass

            except PermissionError:

                # Gera outro nome automaticamente
                nome, extensao = os.path.splitext(
                    arquivo
                )

                data_hora = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                arquivo = (
                    f"{nome}_{data_hora}{extensao}"
                )

                caminho = os.path.join(
                    self.pasta_saida,
                    arquivo
                )

        # ============================================================
        # CRIA WORKBOOK
        # ============================================================

        wb = Workbook()

        ws = wb.active

        ws.title = "RPV"

        # ------------------------------------------------------------
        # LINHAS DE GRADE
        # ------------------------------------------------------------

        ws.views.sheetView[
            0
        ].showGridLines = True

        # ------------------------------------------------------------
        # CONGELAR CABEÇALHO
        # ------------------------------------------------------------

        ws.freeze_panes = "A2"

        # ============================================================
        # ESTILOS
        # ============================================================

        # Cabeçalho
        fill_header = PatternFill(
            start_color="1B365D",
            end_color="1B365D",
            fill_type="solid"
        )

        font_header = Font(
            name="Segoe UI",
            size=11,
            bold=True,
            color="FFFFFF"
        )

        # Zebra
        fill_zebra = PatternFill(
            start_color="F8FAFC",
            end_color="F8FAFC",
            fill_type="solid"
        )

        fill_white = PatternFill(
            start_color="FFFFFF",
            end_color="FFFFFF",
            fill_type="solid"
        )

        # Dados
        font_data = Font(
            name="Segoe UI",
            size=10,
            color="333333"
        )

        # Link
        font_link = Font(
            name="Segoe UI",
            size=10,
            color="0056B3",
            underline="single"
        )

        # Bordas
        thin_border_side = Side(
            border_style="thin",
            color="E0E0E0"
        )

        border_cell = Border(
            left=thin_border_side,
            right=thin_border_side,
            top=thin_border_side,
            bottom=thin_border_side
        )

        # Alinhamentos
        align_center = Alignment(
            horizontal="center",
            vertical="center"
        )

        align_left = Alignment(
            horizontal="left",
            vertical="center"
        )

        # ============================================================
        # CABEÇALHO
        # ============================================================

        headers = [
            "Número Processo",
            "Vara",
            "Banco",
            "Nº RPV"
        ]

        ws.append(
            headers
        )

        ws.row_dimensions[
            1
        ].height = 28

        for col_num, cell in enumerate(
            ws[1],
            start=1
        ):

            cell.fill = fill_header

            cell.font = font_header

            if col_num in [2, 4]:

                cell.alignment = align_center

            else:

                cell.alignment = align_left

            cell.border = border_cell

        # ============================================================
        # DADOS
        # ============================================================

        for idx, item in enumerate(
            dados,
            start=2
        ):

            ws.row_dimensions[
                idx
            ].height = 22

            # Zebra
            if idx % 2 == 0:

                fill_atual = fill_zebra

            else:

                fill_atual = fill_white

            # ========================================================
            # COLUNA A - PROCESSO / LINK
            # ========================================================

            cell_proc = ws.cell(
                row=idx,
                column=1,
                value=item.get(
                    "numero",
                    ""
                )
            )

            link_url = item.get(
                "link",
                ""
            )

            if link_url:

                cell_proc.hyperlink = link_url

                cell_proc.font = font_link

                # Mantém o link clicável
                cell_proc.style = "Hyperlink"

            else:

                cell_proc.font = font_data

            cell_proc.alignment = align_left

            # ========================================================
            # COLUNA B - VARA
            # ========================================================

            cell_vara = ws.cell(
                row=idx,
                column=2,
                value=item.get(
                    "vara",
                    ""
                )
            )

            cell_vara.font = font_data

            cell_vara.alignment = align_center

            # ========================================================
            # COLUNA C - BANCO
            # ========================================================

            cell_banco = ws.cell(
                row=idx,
                column=3,
                value=item.get(
                    "banco",
                    ""
                )
            )

            cell_banco.font = font_data

            cell_banco.alignment = align_left

            # ========================================================
            # COLUNA D - RPV
            # ========================================================

            cell_rpv = ws.cell(
                row=idx,
                column=4,
                value=item.get(
                    "rpv",
                    ""
                )
            )

            cell_rpv.font = font_data

            cell_rpv.alignment = align_center

            # ========================================================
            # FUNDO + BORDA
            # ========================================================

            for col in range(
                1,
                5
            ):

                cell = ws.cell(
                    row=idx,
                    column=col
                )

                cell.fill = fill_atual

                cell.border = border_cell

        # ============================================================
        # AUTOFIT
        # ============================================================

        for col in ws.columns:

            max_len = 0

            col_letter = get_column_letter(
                col[0].column
            )

            for cell in col:

                valor = str(
                    cell.value or ""
                )

                if len(valor) > max_len:

                    max_len = len(
                        valor
                    )

            ws.column_dimensions[
                col_letter
            ].width = max(
                max_len + 4,
                15
            )

        # ============================================================
        # SALVAR
        # ============================================================

        wb.save(
            caminho
        )

        print(
            "=========================================="
        )

        print(
            "EXCEL GERADO COM SUCESSO"
        )

        print(
            f"Arquivo: {caminho}"
        )

        print(
            "=========================================="
        )

        return caminho