import customtkinter as ctk

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


        self.coleta_view = ColetaView(
            self
        )

        self.coleta_view.pack(
            expand=True,
            fill="both"
        )