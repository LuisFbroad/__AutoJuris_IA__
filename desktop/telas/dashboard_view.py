"""Dashboard inicial com indicadores reais da sessão atual."""

import customtkinter as ctk

from desktop.tema import CORES, FONTES, ESPACAMENTOS


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, abrir_coleta):
        super().__init__(master, fg_color="transparent")
        self.abrir_coleta = abrir_coleta
        for coluna in range(3):
            self.grid_columnconfigure(coluna, weight=1, uniform="indicadores")
        self.grid_rowconfigure(3, weight=1)
        self._criar_interface()
        self.atualizar(None)

    def _criar_interface(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, columnspan=3, sticky="ew", padx=24, pady=(24, 12))
        ctk.CTkLabel(
            topo,
            text="Visão geral",
            anchor="w",
            font=ctk.CTkFont(
                family=FONTES["familia"], size=FONTES["titulo"], weight="bold"
            ),
            text_color=CORES["texto"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            topo,
            text="Resumo das consultas realizadas nesta sessão.",
            anchor="w",
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["corpo"]),
            text_color=CORES["texto_secundario"],
        ).pack(anchor="w", pady=(4, 0))

        self.card_processos = self._criar_card(1, "Processos na última coleta", "—")
        self.card_total = self._criar_card(2, "Total informado pelo TRF5", "—")
        self.card_excel = self._criar_card(3, "Relatório Excel", "Ainda não gerado")

        painel = ctk.CTkFrame(
            self,
            fg_color=CORES["superficie"],
            corner_radius=14,
            border_width=1,
            border_color=CORES["borda"],
        )
        painel.grid(row=2, column=0, columnspan=3, sticky="new", padx=24, pady=12)
        painel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            painel,
            text="Comece uma consulta",
            anchor="w",
            font=ctk.CTkFont(
                family=FONTES["familia"], size=FONTES["subtitulo"], weight="bold"
            ),
            text_color=CORES["texto"],
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(
            painel,
            text="Consulte processos no TRF5 por CPF ou CNPJ. Ao concluir, os resultados e o relatório ficam disponíveis na tela de coleta.",
            anchor="w",
            justify="left",
            wraplength=700,
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["corpo"]),
            text_color=CORES["texto_secundario"],
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))
        ctk.CTkButton(
            painel,
            text="Abrir coleta TRF5",
            height=40,
            fg_color=CORES["primaria"],
            hover_color=CORES["primaria_hover"],
            command=self.abrir_coleta,
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 20))

        aviso = ctk.CTkLabel(
            self,
            text="Os indicadores acima refletem somente a coleta mantida em memória nesta sessão; ainda não representam um histórico persistente.",
            anchor="w",
            justify="left",
            wraplength=850,
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["pequena"]),
        )
        aviso.grid(row=3, column=0, columnspan=3, sticky="sew", padx=24, pady=20)

    def _criar_card(self, coluna, titulo, valor_inicial):
        card = ctk.CTkFrame(
            self,
            fg_color=CORES["superficie"],
            corner_radius=14,
            border_width=1,
            border_color=CORES["borda"],
        )
        card.grid(
            row=1,
            column=coluna - 1,
            sticky="ew",
            padx=(24 if coluna == 1 else 8, 8 if coluna < 3 else 24),
            pady=8,
        )
        ctk.CTkLabel(
            card,
            text=titulo,
            anchor="w",
            justify="left",
            wraplength=220,
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["pequena"]),
        ).pack(fill="x", padx=16, pady=(16, 8))
        valor = ctk.CTkLabel(
            card,
            text=valor_inicial,
            anchor="w",
            text_color=CORES["texto"],
            font=ctk.CTkFont(family=FONTES["familia"], size=20, weight="bold"),
        )
        valor.pack(fill="x", padx=16, pady=(0, 18))
        return valor

    def atualizar(self, coleta_view):
        """Atualiza os cartões usando os atributos reais da tela de coleta."""
        if coleta_view is None or not getattr(coleta_view, "data_hora_coleta", None):
            self.card_processos.configure(text="Nenhuma coleta")
            self.card_total.configure(text="Sem dados")
            self.card_excel.configure(text="Ainda não gerado")
            return

        self.card_processos.configure(
            text=str(getattr(coleta_view, "processos_coletados", 0))
        )
        self.card_total.configure(text=str(getattr(coleta_view, "total_trf5", 0)))
        caminho = getattr(coleta_view, "caminho_excel", None)
        self.card_excel.configure(text="Gerado" if caminho else "Não gerado")
