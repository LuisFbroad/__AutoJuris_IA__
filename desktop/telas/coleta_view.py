import os
import sys
import subprocess
import threading

import customtkinter as ctk

from PIL import Image

from services.trf5_service import TRF5Service
from exports.excel_exporter import ExcelExporter


# ============================================================
# RECURSOS DO PROGRAMA
# ============================================================

def recurso(*caminho):

    """
    Retorna o caminho correto de arquivos internos.

    Funciona tanto:

    python main.py

    quanto:

    programa.exe
    """

    if getattr(sys, "frozen", False):

        # PyInstaller
        base_path = sys._MEIPASS

    else:

        # Execução normal pelo Python
        base_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../.."
            )
        )

    return os.path.join(
        base_path,
        *caminho
    )


# ============================================================
# COLETA VIEW
# ============================================================

class ColetaView(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            corner_radius=10
        )

        # ========================================================
        # OBJETOS
        # ========================================================

        self.service = TRF5Service()

        self.exporter = ExcelExporter()

        self.dados = []

        self.caminho_excel = None

        # ========================================================
        # GRID PRINCIPAL
        # ========================================================

        self.grid_columnconfigure(
            0,
            weight=1
        )

        self.grid_rowconfigure(
            2,
            weight=1
        )

        # ========================================================
        # CABEÇALHO
        # ========================================================

        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.header_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        # ========================================================
        # LOGO
        # ========================================================

        caminho_logo = recurso(
            "desktop",
            "assets",
            "GAGC_logo.png"
        )

        print("Caminho da logo:")
        print(caminho_logo)

        if os.path.exists(caminho_logo):

            try:

                imagem = Image.open(
                    caminho_logo
                )

                logo_img = ctk.CTkImage(
                    light_image=imagem,
                    dark_image=imagem,
                    size=(40, 40)
                )

                self.logo_label = ctk.CTkLabel(
                    self.header_frame,
                    image=logo_img,
                    text=""
                )

                self.logo_label.pack(
                    side="left",
                    padx=(0, 10)
                )

            except Exception as e:

                print(
                    f"Erro ao carregar imagem da logo: {e}"
                )

        else:

            print(
                "AVISO: Logo não encontrada:"
            )

            print(
                caminho_logo
            )

        # ========================================================
        # TÍTULO
        # ========================================================

        self.titulo = ctk.CTkLabel(
            self.header_frame,
            text="Coleta de Processos TRF5",
            font=ctk.CTkFont(
                family="Arial",
                size=22,
                weight="bold"
            )
        )

        self.titulo.pack(
            side="left"
        )

        # ========================================================
        # CARD DE CONFIGURAÇÃO
        # ========================================================

        self.card_form = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        self.card_form.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        self.card_form.grid_columnconfigure(
            1,
            weight=1
        )

        # ========================================================
        # LABEL PÁGINAS
        # ========================================================

        self.label_paginas = ctk.CTkLabel(
            self.card_form,
            text="Quantidade de Páginas:",
            font=ctk.CTkFont(
                size=14
            )
        )

        self.label_paginas.grid(
            row=0,
            column=0,
            padx=15,
            pady=15,
            sticky="w"
        )

        # ========================================================
        # INPUT
        # ========================================================

        self.paginas_entry = ctk.CTkEntry(
            self.card_form,
            width=180,
            placeholder_text="Ex: 5"
        )

        self.paginas_entry.grid(
            row=0,
            column=1,
            padx=15,
            pady=15,
            sticky="w"
        )

        # ========================================================
        # BOTÃO COLETAR
        # ========================================================

        self.botao_coletar = ctk.CTkButton(
            self.card_form,
            text="▶ Iniciar Coleta",
            font=ctk.CTkFont(
                weight="bold"
            ),
            command=self.acao_iniciar_coleta
        )

        self.botao_coletar.grid(
            row=0,
            column=2,
            padx=15,
            pady=15,
            sticky="e"
        )

        # ========================================================
        # CARD DE STATUS
        # ========================================================

        self.card_status = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        self.card_status.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

        self.card_status.grid_columnconfigure(
            0,
            weight=1
        )

        self.card_status.grid_rowconfigure(
            2,
            weight=1
        )

        # ========================================================
        # STATUS
        # ========================================================

        self.status = ctk.CTkLabel(
            self.card_status,
            text="Aguardando início da operação.",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        )

        self.status.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 5),
            sticky="w"
        )

        # ========================================================
        # PROGRESSO
        # ========================================================

        self.progress_bar = ctk.CTkProgressBar(
            self.card_status,
            mode="determinate"
        )

        self.progress_bar.grid(
            row=1,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="ew"
        )

        self.progress_bar.set(0)

        # ========================================================
        # LOG
        # ========================================================

        self.log_textbox = ctk.CTkTextbox(
            self.card_status,
            font=ctk.CTkFont(
                family="Consolas",
                size=12
            ),
            wrap="word",
            activate_scrollbars=True
        )

        self.log_textbox.grid(
            row=2,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew"
        )

        self.log_textbox.configure(
            state="disabled"
        )

        self._log(
            "Sistema pronto para iniciar."
        )

        # ========================================================
        # RODAPÉ
        # ========================================================

        self.card_acoes = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.card_acoes.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="ew"
        )

        # ========================================================
        # BOTÃO EXCEL
        # ========================================================

        self.botao_excel = ctk.CTkButton(
            self.card_acoes,
            text="📊 Abrir Arquivo Excel",
            fg_color="#1D6F42",
            hover_color="#155231",
            font=ctk.CTkFont(
                weight="bold"
            ),
            command=self.abrir_excel,
            state="disabled"
        )

        self.botao_excel.pack(
            side="right"
        )

    # ============================================================
    # LOG
    # ============================================================

    def _log(self, mensagem):

        def append():

            try:

                self.log_textbox.configure(
                    state="normal"
                )

                self.log_textbox.insert(
                    "end",
                    f"> {mensagem}\n"
                )

                self.log_textbox.see(
                    "end"
                )

                self.log_textbox.configure(
                    state="disabled"
                )

            except Exception as e:

                print(
                    f"Erro no log: {e}"
                )

        self.after(
            0,
            append
        )

    # ============================================================
    # ATUALIZAR PROGRESSO
    # ============================================================

    def _atualizar_progresso(
        self,
        valor
    ):

        self.after(
            0,
            lambda: self.progress_bar.set(
                valor
            )
        )

    # ============================================================
    # INICIAR COLETA
    # ============================================================

    def acao_iniciar_coleta(self):

        try:

            paginas = int(
                self.paginas_entry.get()
            )

            if paginas <= 0:
                raise ValueError

        except ValueError:

            self.status.configure(
                text="⚠️ Informe um número válido de páginas."
            )

            return

        # --------------------------------------------------------
        # DESABILITAR BOTÕES
        # --------------------------------------------------------

        self.botao_coletar.configure(
            state="disabled"
        )

        self.botao_excel.configure(
            state="disabled"
        )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        self.status.configure(
            text="Coletando processos..."
        )

        # --------------------------------------------------------
        # LIMPAR LOG
        # --------------------------------------------------------

        self.log_textbox.configure(
            state="normal"
        )

        self.log_textbox.delete(
            "1.0",
            "end"
        )

        self.log_textbox.configure(
            state="disabled"
        )

        # --------------------------------------------------------
        # RESETAR PROGRESSO
        # --------------------------------------------------------

        self.progress_bar.set(
            0
        )

        self._log(
            f"Iniciando coleta para {paginas} página(s)..."
        )

        # --------------------------------------------------------
        # THREAD
        # --------------------------------------------------------

        threading.Thread(
            target=self._executar_coleta,
            args=(paginas,),
            daemon=True
        ).start()

    # ============================================================
    # EXECUTAR COLETA
    # ============================================================

    def _executar_coleta(
        self,
        paginas
    ):

        try:

            # ----------------------------------------------------
            # COLETAR
            # ----------------------------------------------------

            processos = self.service.coletar_processos(
                paginas
            )

            self._log(
                "Processando registros..."
            )

            dados_final = []

            vistos = set()

            total = len(
                processos
            )

            # ----------------------------------------------------
            # PROCESSAR
            # ----------------------------------------------------

            for i, processo in enumerate(
                processos
            ):

                numero = processo.get(
                    "numero",
                    processo.get(
                        "processo",
                        ""
                    )
                )

                # ------------------------------------------------
                # SEM NÚMERO
                # ------------------------------------------------

                if not numero:
                    continue

                # ------------------------------------------------
                # EVITAR DUPLICADOS
                # ------------------------------------------------

                if numero in vistos:
                    continue

                vistos.add(
                    numero
                )

                # ------------------------------------------------
                # ADICIONAR DADOS
                # ------------------------------------------------

                dados_final.append({

                    "nome": processo.get(
                        "nome",
                        ""
                    ),

                    "numero": numero,

                    "processo_originario": processo.get(
                        "processo_originario",
                        ""
                    ),

                    "link": processo.get(
                        "link",
                        ""
                    ),

                    "vara": processo.get(
                        "vara",
                        ""
                    ),

                    "banco": processo.get(
                        "banco",
                        ""
                    ),

                    "rpv": processo.get(
                        "rpv",
                        ""
                    )
                })

                # ------------------------------------------------
                # PROGRESSO
                # ------------------------------------------------

                if total > 0:

                    progresso = (
                        (i + 1) / total
                    )

                    self._atualizar_progresso(
                        progresso
                    )

            # ----------------------------------------------------
            # SALVAR DADOS
            # ----------------------------------------------------

            self.dados = dados_final

            quantidade = len(
                self.dados
            )

            # ====================================================
            # GERAR EXCEL
            # ====================================================

            if quantidade > 0:

                self._log(
                    "Gerando arquivo Excel..."
                )

                self.caminho_excel = (
                    self.exporter.exportar(
                        self.dados
                    )
                )

                self._log(
                    "Arquivo salvo com sucesso:"
                )

                self._log(
                    str(
                        self.caminho_excel
                    )
                )

                mensagem_status = (
                    f"✅ Coleta finalizada! "
                    f"{quantidade} processos encontrados."
                )

                sucesso = True

            else:

                mensagem_status = (
                    "ℹ️ Nenhum processo foi encontrado."
                )

                sucesso = False

        except Exception as e:

            mensagem_status = (
                f"❌ Erro durante a coleta: {e}"
            )

            self._log(
                "ERRO CRÍTICO:"
            )

            self._log(
                f"{type(e).__name__}: {e}"
            )

            sucesso = False

        # --------------------------------------------------------
        # FINALIZAR NA THREAD PRINCIPAL
        # --------------------------------------------------------

        self.after(
            0,
            self._finalizar_coleta,
            mensagem_status,
            sucesso
        )

    # ============================================================
    # FINALIZAR COLETA
    # ============================================================

    def _finalizar_coleta(
        self,
        mensagem_status,
        sucesso
    ):

        # --------------------------------------------------------
        # PROGRESSO
        # --------------------------------------------------------

        if sucesso:

            self.progress_bar.set(
                1.0
            )

        else:

            self.progress_bar.set(
                0
            )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        self.status.configure(
            text=mensagem_status
        )

        # --------------------------------------------------------
        # REATIVAR COLETA
        # --------------------------------------------------------

        self.botao_coletar.configure(
            state="normal"
        )

        # --------------------------------------------------------
        # HABILITAR EXCEL
        # --------------------------------------------------------

        if sucesso:

            self.botao_excel.configure(
                state="normal"
            )

            self._log(
                "Operação concluída."
            )

    # ============================================================
    # ABRIR EXCEL
    # ============================================================

    def abrir_excel(self):

        print()
        print(
            "=========================================="
        )
        print(
            "TENTANDO ABRIR ARQUIVO EXCEL"
        )
        print(
            "=========================================="
        )

        # --------------------------------------------------------
        # VERIFICAR CAMINHO
        # --------------------------------------------------------

        print(
            "Caminho armazenado:"
        )

        print(
            self.caminho_excel
        )

        if not self.caminho_excel:

            self._log(
                "❌ Nenhum arquivo Excel foi gerado."
            )

            print(
                "ERRO: self.caminho_excel está vazio."
            )

            return

        # --------------------------------------------------------
        # CAMINHO ABSOLUTO
        # --------------------------------------------------------

        caminho = os.path.abspath(
            str(
                self.caminho_excel
            )
        )

        print(
            "Caminho absoluto:"
        )

        print(
            caminho
        )

        # --------------------------------------------------------
        # VERIFICAR ARQUIVO
        # --------------------------------------------------------

        if not os.path.isfile(
            caminho
        ):

            self._log(
                "❌ Arquivo Excel não encontrado."
            )

            self._log(
                f"Caminho: {caminho}"
            )

            print(
                "ERRO: arquivo não existe."
            )

            return

        # --------------------------------------------------------
        # ABRIR
        # --------------------------------------------------------

        try:

            if sys.platform.startswith(
                "win"
            ):

                print(
                    "Abrindo Excel..."
                )

                os.startfile(
                    caminho
                )

            elif sys.platform == "darwin":

                subprocess.Popen([
                    "open",
                    caminho
                ])

            else:

                subprocess.Popen([
                    "xdg-open",
                    caminho
                ])

            self._log(
                "✅ Arquivo Excel aberto."
            )

            print(
                "Excel aberto com sucesso."
            )

        except Exception as e:

            print(
                "ERRO AO ABRIR EXCEL:"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            self._log(
                f"❌ Erro ao abrir Excel: {e}"
            )