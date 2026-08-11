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

        # Configuração do Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Faz o card de logs/status expandir verticalmente

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
        self.label_paginas.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.paginas_entry = ctk.CTkEntry(
            self.card_form,
            width=180,
            placeholder_text="Ex: 5"
        )
        self.paginas_entry.grid(row=0, column=1, padx=15, pady=15, sticky="w")

        self.botao_coletar = ctk.CTkButton(
            self.card_form,
            text="▶ Iniciar Coleta",
            font=ctk.CTkFont(weight="bold"),
            command=self.acao_iniciar_coleta
        )
        self.botao_coletar.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # -------------------------------------------------------------
        # 3. CARD CENTRAL: STATUS, PROGRESSO E CONSOLE DE LOGS
        # -------------------------------------------------------------
        self.card_status = ctk.CTkFrame(self, corner_radius=10)
        self.card_status.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.card_status.grid_columnconfigure(0, weight=1)
        self.card_status.grid_rowconfigure(2, weight=1)  # Expande o console de logs

        # Sub-header de Status
        self.status = ctk.CTkLabel(
            self.card_status,
            text="Aguardando início da operação.",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Barra de Progresso
        self.progress_bar = ctk.CTkProgressBar(self.card_status, mode="determinate")
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)

        # Terminal / Logs
        self.log_textbox = ctk.CTkTextbox(
            self.card_status,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            activate_scrollbars=True
        )
        self.log_textbox.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self._log("Sistema pronto para iniciar.")

        # -------------------------------------------------------------
        # 4. RODAPÉ DE AÇÕES (Botão de Exportação)
        # -------------------------------------------------------------
        self.card_acoes = ctk.CTkFrame(self, fg_color="transparent")
        self.card_acoes.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        self.botao_excel = ctk.CTkButton(
            self.card_acoes,
            text="📊 Abrir Arquivo Excel",
            fg_color="#1D6F42",        # Verde do Excel
            hover_color="#155231",
            font=ctk.CTkFont(weight="bold"),
            command=self.abrir_excel,
            state="disabled"
        )
        self.botao_excel.pack(side="right")  # Posicionado no canto inferior direito

    # -----------------------------------------------------------------
    # MÉTODOS DE LOG E NAVEGAÇÃO INTERNA
    # -----------------------------------------------------------------
    def _log(self, mensagem: str):
        """Escreve mensagens no console visual da interface (Thread-Safe)."""
        def append():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", f"> {mensagem}\n")
            self.log_textbox.see("end")
            self.log_textbox.configure(state="disabled")
        
        self.after(0, append)

    def _atualizar_progresso(self, valor: float):
        """Atualiza o preenchimento da barra de progresso (0.0 a 1.0)."""
        self.after(0, lambda: self.progress_bar.set(valor))

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
        
        # Limpa o log e reseta a barra de progresso
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")
        self.progress_bar.set(0)

        self._log(f"Iniciando coleta para {paginas} página(s)...")

        # Executa a busca em segundo plano
        threading.Thread(target=self._executar_coleta, args=(paginas,), daemon=True).start()

    def _executar_coleta(self, paginas):
        """Executado na thread de segundo plano."""
        try:
            # Caso o seu TRF5Service aceite uma função de callback para reportar progresso:
            # ex: processos = self.service.coletar_processos(paginas, callback_log=self._log)
            processos = self.service.coletar_processos(paginas)

            self._log("Processando e removendo duplicatas dos registros...")
            dados_final = []
            vistos = set()

            for i, processo in enumerate(processos):
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

            if quantidade > 0:
                self._log("Gerando arquivo Excel...")
                self.caminho_excel = self.exporter.exportar(self.dados)
                self._log(f"Arquivo salvo com sucesso em: {self.caminho_excel}")
                mensagem_status = f"✅ Coleta finalizada com sucesso! {quantidade} processos encontrados."
                sucesso = True
            else:
                mensagem_status = "ℹ️ Nenhum processo foi encontrado."
                sucesso = False

        except Exception as e:
            mensagem_status = f"❌ Erro durante a coleta: {str(e)}"
            self._log(f"ERRO CRÍTICO: {str(e)}")
            sucesso = False

        # Envia a atualização final de volta para a GUI
        self.after(0, self._finalizar_coleta, mensagem_status, sucesso)

    def _finalizar_coleta(self, mensagem_status, sucesso):
        """Restaura a interface na thread principal."""
        self.progress_bar.set(1.0 if sucesso else 0.0)
        self.status.configure(text=mensagem_status)

        self.botao_coletar.configure(state="normal")
        if sucesso:
            self.botao_excel.configure(state="normal")
            self._log("Operação concluída. Clique em 'Abrir Arquivo Excel' para visualizar os dados.")

    def abrir_excel(self):
        """Abre o arquivo Excel gerado."""
        if self.caminho_excel and os.path.exists(self.caminho_excel):
            if hasattr(os, "startfile"):
                os.startfile(self.caminho_excel)
            else:
                subprocess.Popen(["open", self.caminho_excel])