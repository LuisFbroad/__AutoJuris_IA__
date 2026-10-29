"""Aplicação principal e navegação do AutoJuris IA."""

import sys
import traceback
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from desktop.tema import CORES, DIMENSOES, FONTES, configurar_tema
from desktop.telas.login_view import LoginView
from desktop.telas.coleta_view import ColetaView
from desktop.telas.dashboard_view import DashboardView


class App(ctk.CTk):
    """Janela principal. O login continua usando o serviço de autenticação atual."""

    def __init__(self):
        configurar_tema()
        super().__init__()
        self.title("AutoJuris IA")
        self.largura = DIMENSOES["largura_janela"]
        self.altura = DIMENSOES["altura_janela"]
        self.geometry(f"{self.largura}x{self.altura}")
        self.minsize(DIMENSOES["largura_minima"], DIMENSOES["altura_minima"])
        self.configure(fg_color=CORES["fundo"])
        self._centralizar_janela()

        self.usuario_logado = None
        self.login_view = None
        self.workspace = None
        self.coleta_view = None
        self.dashboard_view = None
        self.pagina_atual = None
        self.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
        self.mostrar_login()

    def _centralizar_janela(self):
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth() - self.largura) // 2)
        y = max(0, (self.winfo_screenheight() - self.altura) // 2)
        self.geometry(f"{self.largura}x{self.altura}+{x}+{y}")

    def _limpar_janela(self):
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def mostrar_login(self):
        self._limpar_janela()
        self.workspace = None
        self.coleta_view = None
        self.dashboard_view = None
        self.pagina_atual = None
        self.login_view = LoginView(self, self.login_realizado)
        self.login_view.pack(expand=True, fill="both")

    def login_realizado(self, usuario):
        """Mantém o callback esperado pelo LoginView existente."""
        self.usuario_logado = usuario
        if self.login_view is not None:
            self.login_view.destroy()
            self.login_view = None
        self._criar_workspace()
        self.mostrar_pagina("visao_geral")

    def _criar_workspace(self):
        self.workspace = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.workspace.pack(fill="both", expand=True)
        self.workspace.grid_columnconfigure(1, weight=1)
        self.workspace.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(
            self.workspace,
            width=DIMENSOES["largura_sidebar"],
            fg_color=CORES["sidebar"],
            corner_radius=0,
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="AutoJuris",
            text_color=CORES["branco"],
            anchor="w",
            font=ctk.CTkFont(family=FONTES["familia"], size=22, weight="bold"),
        ).pack(fill="x", padx=22, pady=(28, 0))
        ctk.CTkLabel(
            sidebar,
            text="INTELIGÊNCIA JURÍDICA",
            text_color="#AFC4DC",
            anchor="w",
            font=ctk.CTkFont(family=FONTES["familia"], size=10, weight="bold"),
        ).pack(fill="x", padx=22, pady=(2, 28))

        self.nav_buttons = {}
        self._criar_botao_nav(sidebar, "visao_geral", "▦   Visão geral")
        self._criar_botao_nav(sidebar, "coleta", "⌕   Coleta TRF5")

        ctk.CTkFrame(sidebar, fg_color="#35506F", height=1).pack(
            fill="x", padx=18, pady=(20, 12)
        )
        ctk.CTkLabel(
            sidebar,
            text=f"Usuário: {self.usuario_logado or '—'}",
            anchor="w",
            text_color="#D6E0EB",
            wraplength=180,
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["pequena"]),
        ).pack(side="bottom", fill="x", padx=20, pady=(0, 8))
        ctk.CTkButton(
            sidebar,
            text="Sair",
            anchor="w",
            fg_color="transparent",
            hover_color=CORES["sidebar_hover"],
            text_color=CORES["branco"],
            command=self.sair,
        ).pack(side="bottom", fill="x", padx=12, pady=(8, 18))

        area = ctk.CTkFrame(self.workspace, fg_color=CORES["fundo"], corner_radius=0)
        area.grid(row=0, column=1, sticky="nsew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_rowconfigure(1, weight=1)
        header = ctk.CTkFrame(
            area, fg_color=CORES["superficie"], corner_radius=0, height=62
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.header_titulo = ctk.CTkLabel(
            header,
            text="Visão geral",
            anchor="w",
            text_color=CORES["texto"],
            font=ctk.CTkFont(
                family=FONTES["familia"], size=FONTES["subtitulo"], weight="bold"
            ),
        )
        self.header_titulo.grid(row=0, column=0, sticky="w", padx=24, pady=18)
        self.area_conteudo = ctk.CTkFrame(area, fg_color="transparent", corner_radius=0)
        self.area_conteudo.grid(row=1, column=0, sticky="nsew")
        self.area_conteudo.grid_columnconfigure(0, weight=1)
        self.area_conteudo.grid_rowconfigure(0, weight=1)

        self.dashboard_view = DashboardView(
            self.area_conteudo, lambda: self.mostrar_pagina("coleta")
        )
        self.coleta_view = ColetaView(self.area_conteudo)

    def _criar_botao_nav(self, parent, chave, texto):
        botao = ctk.CTkButton(
            parent,
            text=texto,
            anchor="w",
            height=42,
            corner_radius=9,
            fg_color="transparent",
            hover_color=CORES["sidebar_hover"],
            text_color=CORES["branco"],
            font=ctk.CTkFont(family=FONTES["familia"], size=FONTES["corpo"]),
            command=lambda pagina=chave: self.mostrar_pagina(pagina),
        )
        botao.pack(fill="x", padx=12, pady=4)
        self.nav_buttons[chave] = botao

    def mostrar_pagina(self, pagina):
        if self.workspace is None:
            return
        if self.pagina_atual == "visao_geral":
            self.dashboard_view.pack_forget()
        elif self.pagina_atual == "coleta":
            self.coleta_view.pack_forget()

        if pagina == "visao_geral":
            self.header_titulo.configure(text="Visão geral")
            self.dashboard_view.atualizar(self.coleta_view)
            self.dashboard_view.pack(fill="both", expand=True)
        elif pagina == "coleta":
            self.header_titulo.configure(text="Coleta de processos TRF5")
            self.coleta_view.pack(fill="both", expand=True)
        else:
            raise ValueError(f"Página desconhecida: {pagina}")

        self.pagina_atual = pagina
        for chave, botao in self.nav_buttons.items():
            botao.configure(
                fg_color=CORES["sidebar_selected"] if chave == pagina else "transparent"
            )

    def sair(self):
        """Encerra a sessão sem destruir uma coleta que ainda esteja executando."""
        if self.coleta_view is not None:
            estado = str(self.coleta_view.botao_iniciar.cget("state"))
            if estado == "disabled":
                messagebox.showwarning(
                    "Coleta em andamento",
                    "Aguarde a coleta terminar antes de sair da sessão.",
                    parent=self,
                )
                return
        self.mostrar_login()

    def mostrar_erro(self, titulo, erro=None):
        if erro is None:
            erro = traceback.format_exc()
        print(f"{titulo}: {erro}")
        messagebox.showerror(titulo, str(erro), parent=self)

    def fechar_aplicacao(self):
        try:
            self.destroy()
        except tk.TclError:
            sys.exit(0)


def configurar_interface():
    configurar_tema()


def main():
    try:
        app = App()
        app.mainloop()
    except Exception as erro:
        traceback.print_exc()
        try:
            messagebox.showerror("Erro fatal - AutoJuris IA", str(erro))
        except Exception:
            pass


if __name__ == "__main__":
    main()
