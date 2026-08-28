import os
import sys
import traceback
import customtkinter as ctk
from tkinter import messagebox


# ============================================================
# CONFIGURAÇÃO DE CAMINHOS
# ============================================================

def obter_caminho_recurso(*caminho_relativo):
    """
    Retorna o caminho absoluto de um recurso.

    Funciona tanto em:
        - execução normal pelo Python
        - executável criado pelo PyInstaller
    """

    if getattr(sys, "frozen", False):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_dir,
        *caminho_relativo
    )


# ============================================================
# CONFIGURAÇÃO DO PYTHONPATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

if BASE_DIR not in sys.path:
    sys.path.insert(
        0,
        BASE_DIR
    )


# ============================================================
# IMPORTAÇÕES DA INTERFACE
# ============================================================

try:

    from desktop.telas.login_view import LoginView
    from desktop.telas.coleta_view import ColetaView

except Exception:

    erro = traceback.format_exc()

    print("=" * 70)
    print("ERRO AO IMPORTAR AS TELAS")
    print("=" * 70)
    print(erro)

    try:
        messagebox.showerror(
            "Erro ao iniciar AutoJuris IA",
            "Não foi possível carregar as telas "
            "do sistema.\n\n"
            + erro
        )
    except Exception:
        pass

    sys.exit(1)


# ============================================================
# APLICAÇÃO PRINCIPAL
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

        self.largura = 1100
        self.altura = 700

        self.geometry(
            f"{self.largura}x{self.altura}"
        )

        self.minsize(
            900,
            600
        )

        self.centralizar_janela()

        # ----------------------------------------------------
        # ESTADO DA APLICAÇÃO
        # ----------------------------------------------------

        self.usuario_logado = None

        self.login_view = None
        self.coleta_view = None

        # ----------------------------------------------------
        # EVENTO DE FECHAMENTO
        # ----------------------------------------------------

        self.protocol(
            "WM_DELETE_WINDOW",
            self.fechar_aplicacao
        )

        # ----------------------------------------------------
        # INICIAR APLICAÇÃO
        # ----------------------------------------------------

        self.mostrar_login()

    # ========================================================
    # CENTRALIZAR JANELA
    # ========================================================

    def centralizar_janela(self):

        self.update_idletasks()

        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()

        x = (
            largura_tela - self.largura
        ) // 2

        y = (
            altura_tela - self.altura
        ) // 2

        self.geometry(
            f"{self.largura}x{self.altura}+{x}+{y}"
        )

    # ========================================================
    # LIMPAR CONTEÚDO DA JANELA
    # ========================================================

    def limpar_janela(self):

        for widget in self.winfo_children():

            try:
                widget.destroy()

            except Exception as e:

                print(
                    f"[AVISO] Erro ao destruir widget: {e}"
                )

        self.update_idletasks()

    # ========================================================
    # MOSTRAR LOGIN
    # ========================================================

    def mostrar_login(self):

        print(
            "[APP] Carregando tela de login..."
        )

        try:

            self.limpar_janela()

            self.login_view = LoginView(
                self,
                self.login_realizado
            )

            self.login_view.pack(
                expand=True,
                fill="both"
            )

            self.update_idletasks()

            print(
                "[APP] Tela de login carregada."
            )

        except Exception:

            self.mostrar_erro(
                "Erro ao carregar a tela de login"
            )

    # ========================================================
    # LOGIN REALIZADO
    # ========================================================

    def login_realizado(self, usuario):

        print()
        print("=" * 70)
        print("[APP] LOGIN REALIZADO")
        print("=" * 70)
        print(
            f"[APP] Usuário: {usuario}"
        )

        self.usuario_logado = usuario

        # ----------------------------------------------------
        # CRIA TELA PRINCIPAL
        # ----------------------------------------------------

        nova_tela = None

        try:

            print(
                "[APP] Criando ColetaView..."
            )

            nova_tela = ColetaView(
                self
            )

            print(
                "[APP] ColetaView criada."
            )

            nova_tela.pack(
                expand=True,
                fill="both",
                padx=15,
                pady=15
            )

            self.update_idletasks()

            print(
                "[APP] ColetaView exibida."
            )

        except Exception:

            if nova_tela is not None:

                try:
                    nova_tela.destroy()
                except Exception:
                    pass

            self.mostrar_erro(
                "Erro ao carregar a tela principal"
            )

            return

        # ----------------------------------------------------
        # REMOVE LOGIN
        # ----------------------------------------------------

        if self.login_view is not None:

            try:
                self.login_view.destroy()

            except Exception as e:

                print(
                    f"[AVISO] Erro ao remover login: {e}"
                )

        self.login_view = None
        self.coleta_view = nova_tela

        self.update_idletasks()

        print("=" * 70)
        print("[APP] TELA PRINCIPAL CARREGADA")
        print("=" * 70)
        print()

    # ========================================================
    # MOSTRAR ERRO
    # ========================================================

    def mostrar_erro(self, titulo):

        erro = traceback.format_exc()

        print()
        print("=" * 70)
        print(titulo.upper())
        print("=" * 70)
        print(erro)

        try:

            messagebox.showerror(
                titulo,
                f"{erro}"
            )

        except Exception:
            pass

    # ========================================================
    # FECHAR APLICAÇÃO
    # ========================================================

    def fechar_aplicacao(self):

        print(
            "[APP] Encerrando AutoJuris IA..."
        )

        try:

            self.destroy()

        except Exception:

            sys.exit(0)


# ============================================================
# CONFIGURAÇÃO DO CUSTOMTKINTER
# ============================================================

def configurar_interface():

    ctk.set_appearance_mode(
        "System"
    )

    ctk.set_default_color_theme(
        "blue"
    )


# ============================================================
# PONTO DE ENTRADA
# ============================================================

def main():

    try:

        print("=" * 70)
        print("             AUTOJURIS IA")
        print("=" * 70)
        print("[APP] Iniciando aplicação...")

        configurar_interface()

        app = App()

        print(
            "[APP] Aplicação iniciada."
        )

        app.mainloop()

    except Exception:

        erro = traceback.format_exc()

        print()
        print("=" * 70)
        print("ERRO FATAL DO APLICATIVO")
        print("=" * 70)
        print(erro)

        try:

            messagebox.showerror(
                "Erro fatal - AutoJuris IA",
                erro
            )

        except Exception:
            pass


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()
