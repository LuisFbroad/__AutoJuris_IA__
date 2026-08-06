from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo


class ExcelExporter:


    def exportar(self, dados, arquivo="relatorio_rpv.xlsx"):


        wb = Workbook()

        ws = wb.active

        ws.title = "Processos RPV"



        # =========================
        # TÍTULO
        # =========================

        ws.merge_cells(
            "A1:E1"
        )


        titulo = ws["A1"]

        titulo.value = (
            "RELATÓRIO DE PROCESSOS RPV - TRF5"
        )


        titulo.font = Font(
            bold=True,
            size=14
        )


        titulo.alignment = Alignment(
            horizontal="center",
            vertical="center"
        )



        # =========================
        # CABEÇALHO
        # =========================


        cabecalho = [
            "Nº Processo",
            "Vara",
            "Banco",
            "Nº RPV",
            "Data Decisão"
        ]


        for coluna, valor in enumerate(cabecalho, 1):

            celula = ws.cell(
                row=3,
                column=coluna
            )


            celula.value = valor


            celula.font = Font(
                bold=True,
                color="FFFFFF"
            )


            celula.fill = PatternFill(
                fill_type="solid",
                fgColor="4F81BD"
            )


            celula.alignment = Alignment(
                horizontal="center"
            )



        # =========================
        # DADOS
        # =========================


        linha = 4


        for item in dados:


            # Número do processo com link

            processo = ws.cell(
                linha,
                1
            )


            processo.value = item.get(
                "processo",
                ""
            )


            processo.hyperlink = item.get(
                "link"
            )


            processo.style = (
                "Hyperlink"
            )



            ws.cell(
                linha,
                2,
                item.get(
                    "vara",
                    ""
                )
            )


            ws.cell(
                linha,
                3,
                item.get(
                    "banco",
                    ""
                )
            )


            ws.cell(
                linha,
                4,
                str(
                    item.get(
                        "rpv",
                        ""
                    )
                )
            )


            ws.cell(
                linha,
                5,
                item.get(
                    "data_decisao",
                    ""
                )
            )


            linha += 1



        # =========================
        # TABELA EXCEL
        # =========================


        tabela = Table(
            displayName="TabelaRPV",
            ref=f"A3:E{ws.max_row}"
        )


        estilo = TableStyleInfo(
            name="TableStyleMedium2",
            showRowStripes=True
        )


        tabela.tableStyleInfo = estilo


        ws.add_table(
            tabela
        )



        # =========================
        # BORDAS
        # =========================


        borda = Border(

            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin")

        )


        for linha in ws.iter_rows():

            for celula in linha:

                celula.border = borda

                celula.alignment = Alignment(
                    vertical="center"
                )



        # =========================
        # TAMANHO COLUNAS
        # =========================


        larguras = {

            "A": 32,
            "B": 15,
            "C": 25,
            "D": 25,
            "E": 22

        }


        for coluna, tamanho in larguras.items():

            ws.column_dimensions[
                coluna
            ].width = tamanho



        # =========================
        # CONGELAR CABEÇALHO
        # =========================


        ws.freeze_panes = "A4"



        # =========================
        # SALVAR
        # =========================


        wb.save(
            arquivo
        )


        print(
            f"Arquivo gerado: {arquivo}"
        )