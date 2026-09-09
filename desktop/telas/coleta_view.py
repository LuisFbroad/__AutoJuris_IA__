import os
import re
import threading
import traceback
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from services.trf5_service import TRF5Service
from exports.excel_exporter import ExcelExporter


class ColetaView(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        # ============================================================
        # DADOS
        # ============================================================

        self.dados = []
        self.caminho_excel = None
        self.total_trf5 = 0
        self.processos_coletados = 0

        # ============================================================
        # CONFIGURAÇÃO
        # ============================================================

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # ============================================================
        # CABEÇALHO
        # ============================================================

        self.frame_header = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        self.frame_header.grid(
            row=0,
            column=0,
            padx=15,
            pady=(15, 10),
            sticky="ew"
        )

        self.frame_header.grid_columnconfigure(
            1,
            weight=1
        )

        # ============================================================
        # LOGO
        # ============================================================

        try:

            caminho_logo = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__)
                        )
                    )
                ),
                "assets",
                "GAGC_logo.png"
            )

            if os.path.exists(caminho_logo):

                from PIL import Image

                imagem = ctk.CTkImage(
                    light_image=Image.open(caminho_logo),
                    dark_image=Image.open(caminho_logo),
                    size=(40, 40)
                )

                self.logo = ctk.CTkLabel(
                    self.frame_header,
                    image=imagem,
                    text=""
                )

                self.logo.grid(
                    row=0,
                    column=0,
                    padx=(15, 10),
                    pady=15
                )

        except Exception:
            pass

        # ============================================================
        # TÍTULO
        # ============================================================

        self.titulo = ctk.CTkLabel(
            self.frame_header,
            text="Coleta de Processos TRF5",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.titulo.grid(
            row=0,
            column=1,
            padx=10,
            pady=15,
            sticky="w"
        )

        # ============================================================
        # CONFIGURAÇÕES DA CONSULTA
        # ============================================================

        self.frame_config = ctk.CTkFrame(
            self,
            corner_radius=10
        )

        self.frame_config.grid(
            row=1,
            column=0,
            padx=15,
            pady=10,
            sticky="ew"
        )

        self.frame_config.grid_columnconfigure(
            1,
            weight=1
        )

        # ============================================================
        # CPF / CNPJ
        # ============================================================

        self.label_documento = ctk.CTkLabel(
            self.frame_config,
            text="CPF/CNPJ:"
        )

        self.label_documento.grid(
            row=0,
            column=0,
            padx=(15, 10),
            pady=(15, 8),
            sticky="w"
        )

        self.entry_documento = ctk.CTkEntry(
            self.frame_config,
            placeholder_text="Digite o CPF ou CNPJ"
        )

        self.entry_documento.grid(
            row=0,
            column=1,
            padx=(0, 15),
            pady=(15, 8),
            sticky="ew"
        )

        # ============================================================
        # TIPO DOCUMENTO
        # ============================================================

        self.label_tipo = ctk.CTkLabel(
            self.frame_config,
            text="Tipo:"
        )

        self.label_tipo.grid(
            row=1,
            column=0,
            padx=(15, 10),
            pady=8,
            sticky="w"
        )

        self.combo_tipo = ctk.CTkComboBox(
            self.frame_config,
            values=[
                "CPF",
                "CNPJ"
            ],
            state="readonly"
        )

        self.combo_tipo.set("CPF")

        self.combo_tipo.grid(
            row=1,
            column=1,
            padx=(0, 15),
            pady=8,
            sticky="ew"
        )

        # ============================================================
        # TIPO DE PAGAMENTO
        # ============================================================

        self.label_pagamento = ctk.CTkLabel(
            self.frame_config,
            text="Tipo de pagamento:"
        )

        self.label_pagamento.grid(
            row=2,
            column=0,
            padx=(15, 10),
            pady=8,
            sticky="w"
        )

        self.combo_pagamento = ctk.CTkComboBox(
            self.frame_config,
            values=[
                "RPV e Precatório",
                "RPV",
                "Precatório"
            ],
            state="readonly"
        )

        self.combo_pagamento.set(
            "RPV e Precatório"
        )

        self.combo_pagamento.grid(
            row=2,
            column=1,
            padx=(0, 15),
            pady=8,
            sticky="ew"
        )

        # ============================================================
        # QUANTIDADE DE PÁGINAS
        # ============================================================

        self.label_paginas = ctk.CTkLabel(
            self.frame_config,
            text="Quantidade de Páginas:"
        )

        self.label_paginas.grid(
            row=3,
            column=0,
            padx=(15, 10),
            pady=8,
            sticky="w"
        )

        self.entry_paginas = ctk.CTkEntry(
            self.frame_config,
            placeholder_text="Ex: 5"
        )

        self.entry_paginas.insert(
            0,
            "1"
        )

        self.entry_paginas.grid(
            row=3,
            column=1,
            padx=(0, 15),
            pady=8,
            sticky="ew"
        )

        # ============================================================
        # VALORES VINCULADOS
        # ============================================================

        self.var_vinculados = tk.BooleanVar(
            value=True
        )

        self.check_vinculados = ctk.CTkCheckBox(
            self.frame_config,
            text="Consultar somente valores vinculados",
            variable=self.var_vinculados
        )

        self.check_vinculados.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=15,
            pady=(8, 15),
            sticky="w"
        )

        # ============================================================
        # CONTROLES
        # ============================================================

        self.frame_controles = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.frame_controles.grid(
            row=2,
            column=0,
            padx=15,
            pady=(0, 10),
            sticky="ew"
        )

        self.frame_controles.grid_columnconfigure(
            0,
            weight=1
        )

        self.frame_controles.grid_columnconfigure(
            1,
            weight=1
        )

        # ============================================================
        # BOTÃO INICIAR
        # ============================================================

        self.botao_iniciar = ctk.CTkButton(
            self.frame_controles,
            text="▶ Iniciar Coleta",
            height=42,
            command=self.iniciar_coleta
        )

        self.botao_iniciar.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="ew"
        )

        # ============================================================
        # BOTÃO EXCEL
        # ============================================================

        self.botao_excel = ctk.CTkButton(
            self.frame_controles,
            text="📊 Abrir Arquivo Excel",
            height=42,
            fg_color="green",
            hover_color="darkgreen",
            state="disabled",
            command=self.abrir_excel
        )

        self.botao_excel.grid(
            row=0,
            column=1,
            padx=(10, 0),
            sticky="ew"
        )

        # ============================================================
        # STATUS
        # ============================================================

        self.label_status = ctk.CTkLabel(
            self,
            text="Pronto para iniciar uma consulta.",
            anchor="w"
        )

        self.label_status.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 5),
            sticky="ew"
        )

        # ============================================================
        # BARRA DE PROGRESSO
        # ============================================================

        self.progress = ctk.CTkProgressBar(
            self,
            mode="determinate"
        )

        self.progress.set(0)

        self.progress.grid(
            row=4,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="ew"
        )

        # ============================================================
        # LOG
        # ============================================================

        self.label_log = ctk.CTkLabel(
            self,
            text="Log da operação",
            anchor="w",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )

        self.label_log.grid(
            row=5,
            column=0,
            padx=20,
            pady=(0, 5),
            sticky="ew"
        )

        self.text_log = ctk.CTkTextbox(
            self,
            font=("Consolas", 11),
            wrap="none"
        )

        self.text_log.grid(
            row=6,
            column=0,
            padx=15,
            pady=(0, 15),
            sticky="nsew"
        )

    # ================================================================
    # LOG
    # ================================================================

    def adicionar_log(self, mensagem):

        def atualizar():

            try:

                self.text_log.insert(
                    "end",
                    mensagem + "\n"
                )

                self.text_log.see(
                    "end"
                )

            except Exception:
                pass

        self.after(
            0,
            atualizar
        )

    # ================================================================
    # STATUS
    # ================================================================

    def atualizar_status(self, mensagem):

        def atualizar():

            try:

                self.label_status.configure(
                    text=mensagem
                )

            except Exception:
                pass

        self.after(
            0,
            atualizar
        )

    # ================================================================
    # PROGRESSO
    # ================================================================

    def atualizar_progresso(self, valor):

        valor = max(
            0,
            min(
                1,
                valor
            )
        )

        self.after(
            0,
            lambda valor=valor: self.progress.set(valor)
        )

    # ================================================================
    # INICIAR COLETA
    # ================================================================

    def iniciar_coleta(self):

        documento = self.entry_documento.get().strip()

        tipo_documento = self.combo_tipo.get()

        paginas_texto = self.entry_paginas.get().strip()

        # ============================================================
        # VALIDAÇÃO DOCUMENTO
        # ============================================================

        documento = re.sub(
            r"\D",
            "",
            documento
        )

        if not documento:

            messagebox.showwarning(
                "Documento",
                "Digite um CPF ou CNPJ."
            )

            return

        if tipo_documento == "CPF" and len(documento) != 11:

            messagebox.showwarning(
                "CPF inválido",
                "O CPF deve possuir 11 dígitos."
            )

            return

        if tipo_documento == "CNPJ" and len(documento) != 14:

            messagebox.showwarning(
                "CNPJ inválido",
                "O CNPJ deve possuir 14 dígitos."
            )

            return

        # ============================================================
        # VALIDAÇÃO PÁGINAS
        # ============================================================

        try:

            paginas = int(
                paginas_texto
            )

        except ValueError:

            messagebox.showwarning(
                "Quantidade de páginas",
                "Informe uma quantidade válida de páginas."
            )

            return

        if paginas < 1:

            messagebox.showwarning(
                "Quantidade de páginas",
                "A quantidade de páginas deve ser maior que zero."
            )

            return

        # ============================================================
        # CAPTURA CONFIGURAÇÕES
        # ============================================================

        tipo_pagamento = self.combo_pagamento.get()

        somente_vinculados = self.var_vinculados.get()

        # ============================================================
        # PREPARA INTERFACE
        # ============================================================

        self.botao_iniciar.configure(
            state="disabled",
            text="⏳ Coletando..."
        )

        self.botao_excel.configure(
            state="disabled"
        )

        self.progress.set(
            0
        )

        self.text_log.delete(
            "1.0",
            "end"
        )

        self.caminho_excel = None
        self.dados = []
        self.total_trf5 = 0
        self.processos_coletados = 0

        # ============================================================
        # THREAD
        # ============================================================

        thread = threading.Thread(
            target=self.executar_coleta,
            args=(
                documento,
                tipo_documento,
                paginas,
                tipo_pagamento,
                somente_vinculados
            ),
            daemon=True
        )

        thread.start()

    # ================================================================
    # EXECUTAR COLETA
    # ================================================================

    def executar_coleta(
        self,
        documento,
        tipo_documento,
        paginas,
        tipo_pagamento,
        somente_vinculados
    ):

        try:

            # ========================================================
            # CABEÇALHO
            # ========================================================

            self.adicionar_log(
                "=" * 60
            )

            self.adicionar_log(
                "INICIANDO COLETA TRF5"
            )

            self.adicionar_log(
                "=" * 60
            )

            self.adicionar_log(
                f"Documento: {documento}"
            )

            self.adicionar_log(
                f"Tipo: {tipo_documento}"
            )

            self.adicionar_log(
                f"Páginas: {paginas}"
            )

            self.adicionar_log(
                f"Tipo de pagamento: {tipo_pagamento}"
            )

            self.adicionar_log(
                f"Somente vinculados: "
                f"{'Sim' if somente_vinculados else 'Não'}"
            )

            # ========================================================
            # STATUS
            # ========================================================

            self.atualizar_status(
                "Criando serviço TRF5..."
            )

            # ========================================================
            # SERVICE
            # ========================================================

            service = TRF5Service(
                documento=documento,
                tipo_documento=tipo_documento
            )

            self.adicionar_log(
                "[OK] TRF5Service criado."
            )

            # ========================================================
            # CONSULTA
            # ========================================================

            self.atualizar_status(
                "Consultando processos no TRF5..."
            )

            self.adicionar_log(
                ""
            )

            self.adicionar_log(
                "Iniciando coleta das páginas..."
            )

            # ========================================================
            # COLETA
            # ========================================================

            resultado = service.coletar_processos(
                documento=documento,
                tipo_documento=tipo_documento,
                limite_paginas=paginas,
                extrair_detalhes=True
            )

            # ========================================================
            # RESULTADO
            # ========================================================

            if isinstance(
                resultado,
                dict
            ):

                processos = resultado.get(
                    "processos",
                    []
                )

                self.total_trf5 = resultado.get(
                    "total",
                    len(processos)
                )

            else:

                processos = resultado

                self.total_trf5 = len(
                    processos
                )

            # ========================================================
            # SALVA DADOS
            # ========================================================

            self.dados = processos

            self.processos_coletados = len(
                processos
            )

            # ========================================================
            # LOG RESULTADO
            # ========================================================

            self.adicionar_log(
                ""
            )

            self.adicionar_log(
                "=" * 60
            )

            self.adicionar_log(
                "COLETA FINALIZADA"
            )

            self.adicionar_log(
                "=" * 60
            )

            self.adicionar_log(
                f"Total informado pelo TRF5: "
                f"{self.total_trf5}"
            )

            self.adicionar_log(
                f"Processos coletados: "
                f"{self.processos_coletados}"
            )

            # ========================================================
            # PROGRESSO
            # ========================================================

            self.atualizar_progresso(
                1
            )

            self.atualizar_status(
                f"Coleta concluída: "
                f"{self.processos_coletados} processos."
            )

            # ========================================================
            # EXPORTAÇÃO
            # ========================================================

            if self.dados:

                self.atualizar_status(
                    "Gerando arquivo Excel..."
                )

                self.adicionar_log(
                    ""
                )

                self.adicionar_log(
                    "Gerando relatório Excel..."
                )

                exporter = ExcelExporter()

                # ====================================================
                # EXPORTAR
                # ====================================================

                if hasattr(
                    exporter,
                    "exportar"
                ):

                    caminho = exporter.exportar(
                        self.dados
                    )

                elif hasattr(
                    exporter,
                    "exportar_processos"
                ):

                    caminho = exporter.exportar_processos(
                        self.dados
                    )

                else:

                    raise AttributeError(
                        "ExcelExporter não possui "
                        "um método de exportação conhecido."
                    )

                # ====================================================
                # SALVA CAMINHO
                # ====================================================

                self.caminho_excel = caminho

                self.adicionar_log(
                    f"[OK] Excel gerado: {caminho}"
                )

                self.atualizar_status(
                    "Consulta concluída com sucesso."
                )

                # ====================================================
                # HABILITA BOTÃO
                # ====================================================

                self.after(
                    0,
                    lambda: self.botao_excel.configure(
                        state="normal"
                    )
                )

            else:

                self.atualizar_status(
                    "Nenhum processo encontrado."
                )

                self.adicionar_log(
                    "[AVISO] Nenhum processo foi encontrado."
                )

        # ============================================================
        # ERRO
        # ============================================================

        except Exception as e:

            erro = traceback.format_exc()

            print(
                "=========================================="
            )

            print(
                "ERRO NA COLETA"
            )

            print(
                erro
            )

            print(
                "=========================================="
            )

            self.adicionar_log(
                ""
            )

            self.adicionar_log(
                "ERRO NA COLETA"
            )

            self.adicionar_log(
                str(e)
            )

            self.atualizar_status(
                "Erro durante a coleta."
            )

            # ========================================================
            # CORREÇÃO DO LAMBDA
            # ========================================================

            mensagem_erro = str(e)

            self.after(
                0,
                lambda mensagem_erro=mensagem_erro:
                    messagebox.showerror(
                        "Erro na coleta",
                        "Não foi possível concluir "
                        "a consulta.\n\n"
                        f"{mensagem_erro}"
                    )
            )

        # ============================================================
        # FINALMENTE
        # ============================================================

        finally:

            self.after(
                0,
                lambda: self.botao_iniciar.configure(
                    state="normal",
                    text="▶ Iniciar Coleta"
                )
            )

    # ================================================================
    # ABRIR EXCEL
    # ================================================================

    def abrir_excel(self):

        if not self.caminho_excel:

            messagebox.showwarning(
                "Excel",
                "Nenhum arquivo Excel foi gerado."
            )

            return

        try:

            if not os.path.exists(
                self.caminho_excel
            ):

                messagebox.showerror(
                    "Excel",
                    "O arquivo Excel não foi encontrado."
                )

                return

            os.startfile(
                self.caminho_excel
            )

        except Exception as e:

            messagebox.showerror(
                "Erro",
                f"Não foi possível abrir o Excel.\n\n{e}"
            )