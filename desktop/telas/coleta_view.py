import os
import subprocess
import threading
import customtkinter as ctk
from PIL import Image

from services.trf5_service import TRF5Service
from exports.excel_exporter import ExcelExporter


class ColetaView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, corner_radius=10)

        self.service = TRF5Service()
        self.exporter = ExcelExporter()

        self.dados = []
        self.caminho_excel = None

        # Configuração do Layout
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # 1. CABEÇALHO (Logo + Título)
        # -------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")


        caminho_logo = os.path.join("desktop", "assets", "GAGC_logo.png")

        if os.path.exists(caminho_logo):
            try:
                logo_img = ctk.CTkImage(
                    light_image=Image.open(caminho_logo),
                    dark_image=Image.open(caminho_logo),
                    size=(40, 40)
                )
                self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
                self.logo_label.pack(side="left", padx=(0, 10))
            except Exception as e:
                print(f"Erro ao carregar imagem da logo: {e}")
        else:
            print(f"Aviso: Logo não encontrada no caminho: {caminho_logo}")

        self.titulo = ctk.CTkLabel(
            self.header_frame,
            text="Coleta de Processos TRF5",
            font=ctk.CTkFont(family="Arial", size=22, weight="bold")
        )
        self.titulo.pack(side="left")

        # -------------------------------------------------------------
        # 2. CARD DE CONFIGURAÇÃO (Entrada e Botão de Início)
        # -------------------------------------------------------------
        self.card_form = ctk.CTkFrame(self, corner_radius=10)
        self.card_form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.card_form.grid_columnconfigure(1, weight=1)

        self.label_paginas = ctk.CTkLabel(
            self.card_form,
            text="Quantidade de Páginas:",
            font=ctk.CTkFont(size=14)
        )
        self.label_paginas.grid(row=0, column=0, padx=15, pady=20, sticky="w")

        self.paginas_entry = ctk.CTkEntry(
            self.card_form,
            width=180,
            placeholder_text="Ex: 5"
        )
        self.paginas_entry.grid(row=0, column=1, padx=15, pady=20, sticky="w")

        self.botao_coletar = ctk.CTkButton(
            self.card_form,
            text="Iniciar Coleta",
            font=ctk.CTkFont(weight="bold"),
            command=self.acao_iniciar_coleta
        )
        self.botao_coletar.grid(row=0, column=2, padx=15, pady=20, sticky="e")

        # -------------------------------------------------------------
        # 3. CARD DE STATUS E BARRA DE PROGRESSO
        # -------------------------------------------------------------
        self.card_status = ctk.CTkFrame(self, corner_radius=10)
        self.card_status.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.status = ctk.CTkLabel(
            self.card_status,
            text="Aguardando início da operação.",
            font=ctk.CTkFont(size=13)
        )
        self.status.pack(pady=(15, 5))

        self.progress_bar = ctk.CTkProgressBar(self.card_status, mode="indeterminate")
        self.progress_bar.pack(fill="x", padx=30, pady=(5, 15))
        self.progress_bar.set(0)

        # -------------------------------------------------------------
        # 4. BOTÃO DE EXPORTAÇÃO EXCEL
        # -------------------------------------------------------------
        self.card_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.card_acoes.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")

        self.botao_excel = ctk.CTkButton(
            self.card_acoes,
            text="Abrir Arquivo Excel",
            fg_color="#1D6F42",        # Verde do Excel
            hover_color="#155231",
            font=ctk.CTkFont(weight="bold"),
            command=self.abrir_excel,
            state="disabled"
        )
        self.botao_excel.pack(fill="x", ipady=5)

    # -----------------------------------------------------------------
    # PROCESSAMENTO E LÓGICA DE EXECUÇÃO
    # -----------------------------------------------------------------
    def acao_iniciar_coleta(self):
        """Valida a quantidade de páginas e dispara a busca em Thread."""
        try:
            paginas = int(self.paginas_entry.get())
            if paginas <= 0:
                raise ValueError
        except ValueError:
            self.status.configure(text="⚠️ Informe um número válido de páginas (inteiro maior que 0).")
            return

        self.botao_coletar.configure(state="disabled")
        self.botao_excel.configure(state="disabled")
        self.status.configure(text="Coletando processos... Por favor, aguarde.")
        self.progress_bar.start()

        # Executa a busca em segundo plano
        threading.Thread(target=self._executar_coleta, args=(paginas,), daemon=True).start()

    def _executar_coleta(self, paginas):
        """Executado na thread de segundo plano."""
        try:
            processos = self.service.coletar_processos(paginas)

            dados_final = []
            vistos = set()

            for processo in processos:
                numero = processo.get("numero", "")
                if not numero or numero in vistos:
                    continue

                vistos.add(numero)
                dados_final.append({
                    "numero": numero,
                    "link": processo.get("link", ""),
                    "vara": processo.get("vara", ""),
                    "banco": processo.get("banco", ""),
                    "rpv": processo.get("rpv", "")
                })

            self.dados = dados_final
            quantidade = len(self.dados)

            print("==============================")
            print("DADOS RECEBIDOS PELA VIEW")
            print(self.dados)
            print("==============================")

            if quantidade > 0:
                self.caminho_excel = self.exporter.exportar(self.dados)
                mensagem_status = f"✅ Coleta finalizada com sucesso! {quantidade} processos encontrados."
                sucesso = True
            else:
                mensagem_status = "ℹ️ Nenhum processo foi encontrado."
                sucesso = False

        except Exception as e:
            mensagem_status = f"❌ Erro durante a coleta: {str(e)}"
            sucesso = False

        # Envia a atualização de volta para a GUI
        self.after(0, self._finalizar_coleta, mensagem_status, sucesso)

    def _finalizar_coleta(self, mensagem_status, sucesso):
        """Restaura a interface na thread principal."""
        self.progress_bar.stop()
        self.progress_bar.set(1 if sucesso else 0)
        self.status.configure(text=mensagem_status)

        self.botao_coletar.configure(state="normal")
        if sucesso:
            self.botao_excel.configure(state="normal")

    def abrir_excel(self):
        """Abre o arquivo Excel gerado."""
        if self.caminho_excel and os.path.exists(self.caminho_excel):
            if hasattr(os, "startfile"):
                os.startfile(self.caminho_excel)
            else:
                subprocess.Popen(["open", self.caminho_excel])