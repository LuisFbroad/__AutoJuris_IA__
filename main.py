import os
import time

import customtkinter as ctk
from dotenv import load_dotenv

from desktop.telas.login_view import LoginView
from desktop.telas.coleta_view import ColetaView


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ============================================================
# CARREGAR .ENV
# ============================================================

load_dotenv(
    os.path.join(
        BASE_DIR,
        ".env"
    )
)


# ============================================================
# APLICAÇÃO
# ============================================================

class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # CONFIGURAÇÕES DA JANELA
        # ----------------------------------------------------

        self.title(
            "AutoJuris IA"
        )

        self.geometry(
            "900x600"
        )

        self.minsize(
            800,
            500
        )

        # ----------------------------------------------------
        # ÍCONE
        # ----------------------------------------------------

        caminho_ico = os.path.join(
            BASE_DIR,
            "assets",
            "GAGC_logo.ico"
        )

        if os.path.exists(
            caminho_ico
        ):

            try:

                self.iconbitmap(
                    caminho_ico
                )

            except Exception as e:

                print(
                    f"Erro ao carregar ícone: {e}"
                )

        # ----------------------------------------------------
        # MOSTRAR LOGIN
        # ----------------------------------------------------

        self.mostrar_login()

    # ========================================================
    # LOGIN
    # ========================================================

    def mostrar_login(self):

        self.limpar_tela()

        self.title(
            "AutoJuris IA - Login"
        )

        self.login_view = LoginView(
            self,
            self.login_realizado
        )

        self.login_view.pack(
            expand=True,
            fill="both"
        )

    # ========================================================
    # LOGIN REALIZADO
    # ========================================================

    def login_realizado(
        self,
        usuario
    ):

        print(
            f"Usuário autenticado: {usuario}"
        )

        self.usuario_logado = usuario

        self.mostrar_sistema()

    # ========================================================
    # ABRIR SISTEMA
    # ========================================================

    def mostrar_sistema(self):

        self.limpar_tela()

        self.title(
            f"AutoJuris IA - {self.usuario_logado}"
        )

        self.coleta_view = ColetaView(
            self
        )

        self.coleta_view.pack(
            expand=True,
            fill="both",
            padx=15,
            pady=15
        )

    # ========================================================
    # LIMPAR JANELA
    # ========================================================

    def limpar_tela(self):

        for widget in self.winfo_children():

            widget.destroy()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    inicio_app = time.perf_counter()

    print(
        "🚀 AutoJuris IA iniciado..."
    )

    app = App()

    app.mainloop()

    tempo_sessao = (
        time.perf_counter()
        - inicio_app
    )

    print(
        "\n👋 Aplicação encerrada. "
        f"Tempo total da sessão: "
        f"{tempo_sessao:.2f} segundos"
    )