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

        self.colunas = [
            "Nome",
            "Número Processo",
            "Proc. Originário",
            "Vara",
            "Banco",
            "Nº RPV"
        ]

    # ============================================================
    # EXPORTAR
    # ============================================================

    def exportar(self, dados, caminho="relatorio_rpv.xlsx"):

        workbook = Workbook()

        sheet = workbook.active

        sheet.title = "RPVs"

        # ========================================================
        # CABEÇALHO
        # ========================================================

        for coluna, nome in enumerate(
            self.colunas,
            start=1
        ):

            celula = sheet.cell(
                row=1,
                column=coluna
            )

            celula.value = nome

            celula.font = Font(
                bold=True
            )

            celula.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        # ========================================================
        # DADOS
        # ========================================================

        for linha, processo in enumerate(
            dados,
            start=2
        ):

            valores = [

                processo.get(
                    "nome",
                    ""
                ),

                processo.get(
                    "processo",
                    ""
                ),

                processo.get(
                    "processo_originario",
                    ""
                ),

                processo.get(
                    "vara",
                    ""
                ),

                processo.get(
                    "banco",
                    ""
                ),

                processo.get(
                    "rpv",
                    ""
                ),
            ]

            for coluna, valor in enumerate(
                valores,
                start=1
            ):

                celula = sheet.cell(
                    row=linha,
                    column=coluna
                )

                celula.value = valor

                celula.alignment = Alignment(
                    vertical="center"
                )

        # ========================================================
        # BORDAS
        # ========================================================

        borda = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")
        )

        for row in sheet.iter_rows():

            for celula in row:

                celula.border = borda

        # ========================================================
        # LARGURA DAS COLUNAS
        # ========================================================

        for coluna in range(
            1,
            sheet.max_column + 1
        ):

            maior = 0

            for celula in sheet[
                get_column_letter(coluna)
            ]:

                if celula.value:

                    tamanho = len(
                        str(celula.value)
                    )

                    maior = max(
                        maior,
                        tamanho
                    )

            sheet.column_dimensions[
                get_column_letter(coluna)
            ].width = min(
                maior + 2,
                60
            )

        # ========================================================
        # CONGELAR CABEÇALHO
        # ========================================================

        sheet.freeze_panes = "A2"

        # ========================================================
        # FILTRO
        # ========================================================

        sheet.auto_filter.ref = (
            sheet.dimensions
        )

        # ========================================================
        # SALVAR
        # ========================================================

        workbook.save(caminho)

        print(
            f"\n[OK] Excel salvo em: {caminho}"
        )