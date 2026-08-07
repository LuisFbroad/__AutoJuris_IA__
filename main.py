import os
import customtkinter as ctk

from desktop.telas.coleta_view import ColetaView


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("AutoJuris IA")
        self.geometry("900x600")

        # Caminho absoluto para encontrar o ícone da janela na pasta assets/
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        caminho_ico = os.path.join(BASE_DIR, "assets", "GAGC_logo.ico")

        if os.path.exists(caminho_ico):
            try:
                self.iconbitmap(caminho_ico)
            except Exception as e:
                print(f"Erro ao carregar ícone da janela: {e}")

        # Instancia a tela de Coleta
        self.coleta_view = ColetaView(self)
        self.coleta_view.pack(expand=True, fill="both", padx=15, pady=15)


if __name__ == "__main__":
    app = App()
    app.mainloop()