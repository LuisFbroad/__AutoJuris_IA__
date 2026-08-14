import customtkinter as ctk

from desktop.telas.login_view import LoginView
from desktop.telas.coleta_view import ColetaView


class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "AutoJuris IA"
        )

        self.geometry(
            "900x600"
        )

        self.mostrar_login()

    # ========================================================
    # LOGIN
    # ========================================================

    def mostrar_login(self):

        for widget in self.winfo_children():

            widget.destroy()

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

        self.usuario_logado = usuario

        for widget in self.winfo_children():

            widget.destroy()

        self.coleta_view = ColetaView(
            self
        )

        self.coleta_view.pack(
            expand=True,
            fill="both",
            padx=15,
            pady=15
        )