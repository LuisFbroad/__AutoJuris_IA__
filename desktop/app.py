import customtkinter as ctk

from desktop.telas.coleta_view import ColetaView



class App(ctk.CTk):


    def __init__(self):

        super().__init__()


        self.title(
            "AutoJuris IA"
        )


        self.geometry(
            "800x500"
        )


        tela = ColetaView(
            self
        )


        tela.pack(
            fill="both",
            expand=True
        )



if __name__ == "__main__":

    app = App()

    app.mainloop()