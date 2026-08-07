from openpyxl import Workbook
from openpyxl.styles import Font, Alignment



class ExcelExporter:


    def exportar(
        self,
        dados,
        arquivo="relatorio_rpv.xlsx"
    ):



        wb = Workbook()


        ws = wb.active


        ws.title = "RPV"



        ws.append(
            [
                "Número Processo",
                "Vara",
                "Banco",
                "Nº RPV"
            ]
        )



        for coluna in ws[1]:

            coluna.font = Font(
                bold=True
            )



            coluna.alignment = Alignment(
                horizontal="center"
            )





        linha = 2



        for item in dados:



            celula = ws.cell(
                linha,
                1,
                item.get(
                    "numero",
                    ""
                )
            )


            # ==========================
            # LINK CLICÁVEL
            # ==========================

            celula.hyperlink = item.get(
                "link",
                ""
            )


            celula.style = "Hyperlink"





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
                item.get(
                    "rpv",
                    ""
                )
            )



            linha += 1





        ws.column_dimensions["A"].width = 35
        ws.column_dimensions["B"].width = 20
        ws.column_dimensions["C"].width = 25
        ws.column_dimensions["D"].width = 20




        wb.save(
            arquivo
        )



        return arquivo