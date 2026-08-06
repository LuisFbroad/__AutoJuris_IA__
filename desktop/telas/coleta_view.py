import customtkinter as ctk
import threading

from services.trf5_service import TRF5Service
from scrapers.processo_scraper import ProcessoScraper
from exports.excel_exporter import ExcelExporter



class ColetaView(ctk.CTkFrame):


    def __init__(self, parent):

        super().__init__(parent)


        self.service = TRF5Service()
        self.scraper = ProcessoScraper()
        self.excel = ExcelExporter()


        self.criar_interface()



    def criar_interface(self):


        titulo = ctk.CTkLabel(
            self,
            text="AutoJuris IA - Coleta TRF5",
            font=("Arial", 24)
        )

        titulo.pack(
            pady=30
        )



        self.input_paginas = ctk.CTkEntry(
            self,
            placeholder_text="Quantidade de páginas"
        )

        self.input_paginas.pack(
            pady=10
        )



        self.botao = ctk.CTkButton(
            self,
            text="Iniciar Coleta",
            command=self.iniciar
        )

        self.botao.pack(
            pady=10
        )



        self.status = ctk.CTkLabel(
            self,
            text="Aguardando..."
        )

        self.status.pack(
            pady=10
        )



        self.progress = ctk.CTkProgressBar(
            self,
            width=400
        )

        self.progress.pack(
            pady=20
        )


        self.progress.set(0)




    def iniciar(self):


        paginas = int(
            self.input_paginas.get()
        )


        self.botao.configure(
            state="disabled"
        )


        thread = threading.Thread(
            target=self.executar,
            args=(paginas,)
        )


        thread.start()




    def executar(self, paginas):


        lista_dados = []


        for pagina in range(1, paginas + 1):


            self.status.configure(
                text=f"Buscando página {pagina}/{paginas}"
            )


            processos = self.service.coletar_processos(
                pagina
            )


            for processo in processos:


                detalhes = self.scraper.extrair_detalhes_processo(
                    processo["link"]
                )


                lista_dados.append(
                    detalhes
                )


            self.progress.set(
                pagina / paginas
            )



        self.excel.exportar(
            lista_dados
        )


        self.status.configure(
            text="Finalizado! Excel criado."
        )


        self.botao.configure(
            state="normal"
        )