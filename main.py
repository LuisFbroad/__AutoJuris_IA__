import os
import sys
import traceback
from tkinter import messagebox

import customtkinter as ctk


# ============================================================
# CAMINHO DE RECURSOS
# ============================================================

def obter_caminho_recurso(caminho_relativo):
    """
    Retorna o caminho absoluto de um recurso.

    Funciona em:
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
        caminho_relativo
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
# IMPORTS
# ============================================================

try:

    from desktop.telas.login_view import LoginView
    from desktop.telas.coleta_view import ColetaView

except Exception:

    erro = traceback.format_exc()

    print(
        "=========================================="
    )

    print(
        "ERRO AO IMPORTAR AS TELAS"
    )

    print(
        erro
    )

    print(
        "=========================================="
    )

    messagebox.showerror(
        "Erro ao iniciar AutoJuris IA",
        "Não foi possível carregar as telas do sistema.\n\n"
        + erro
    )

    sys.exit(1)


# ============================================================
# APLICAÇÃO
# ============================================================

class App(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # CONFIGURAÇÃO DA JANELA
        # ----------------------------------------------------

        self.title(
            "AutoJuris IA"
        )

        self.geometry(
            "1100x700"
        )

        self.minsize(
            900,
            600
        )

        # Centraliza a janela
        self.centralizar_janela()

        # Usuário
        self.usuario_logado = None

        # Views
        self.login_view = None
        self.coleta_view = None

        # ----------------------------------------------------
        # FECHAMENTO
        # ----------------------------------------------------

        self.protocol(
            "WM_DELETE_WINDOW",
            self.fechar_aplicacao
        )

        # ----------------------------------------------------
        # INICIA LOGIN
        # ----------------------------------------------------

        self.mostrar_login()

    # ========================================================
    # CENTRALIZAR JANELA
    # ========================================================

    def centralizar_janela(self):

        self.update_idletasks()

        largura = 1100
        altura = 700

        largura_tela = self.winfo_screenwidth()
        altura_tela = self.winfo_screenheight()

        x = (
            largura_tela - largura
        ) // 2

        y = (
            altura_tela - altura
        ) // 2

        self.geometry(
            f"{largura}x{altura}+{x}+{y}"
        )

    # ========================================================
    # LIMPAR JANELA
    # ========================================================

    def limpar_janela(self):

        for widget in self.winfo_children():

            try:

                widget.destroy()

            except Exception as e:

                print(
                    f"Erro ao destruir widget: {e}"
                )

        self.update_idletasks()

    # ========================================================
    # LOGIN
    # ========================================================

    def mostrar_login(self):

        print(
            "Carregando tela de login..."
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
                "Tela de login carregada."
            )

        except Exception as e:

            erro = traceback.format_exc()

            print(
                "=========================================="
            )

            print(
                "ERRO AO CARREGAR LOGIN"
            )

            print(
                erro
            )

            print(
                "=========================================="
            )

            messagebox.showerror(
                "Erro",
                "Erro ao carregar a tela de login:\n\n"
                f"{e}\n\n"
                f"{erro}"
            )

    # ========================================================
    # LOGIN REALIZADO
    # ========================================================

    def login_realizado(
        self,
        usuario
    ):

        print(
            "=========================================="
        )

        print(
            "LOGIN REALIZADO"
        )

        print(
            f"Usuário: {usuario}"
        )

        print(
            "Iniciando carregamento da tela principal..."
        )

        print(
            "=========================================="
        )

        self.usuario_logado = usuario

        # ----------------------------------------------------
        # NÃO destrói o login imediatamente.
        # Primeiro tenta criar a tela principal.
        # ----------------------------------------------------

        nova_tela = None

        try:

            print(
                "Criando ColetaView..."
            )

            nova_tela = ColetaView(
                self
            )

            print(
                "ColetaView criada com sucesso."
            )

            nova_tela.pack(
                expand=True,
                fill="both",
                padx=15,
                pady=15
            )

            print(
                "ColetaView adicionada à janela."
            )

            self.update_idletasks()

        except Exception as e:

            erro = traceback.format_exc()

            print(
                "=========================================="
            )

            print(
                "ERRO AO CARREGAR TELA PRINCIPAL"
            )

            print(
                erro
            )

            print(
                "=========================================="
            )

            # ------------------------------------------------
            # Se falhou, não destrói o login.
            # ------------------------------------------------

            if nova_tela is not None:

                try:
                    nova_tela.destroy()
                except:
                    pass

            messagebox.showerror(
                "Erro ao carregar a tela principal",
                "Não foi possível carregar a tela principal.\n\n"
                f"Erro:\n{e}\n\n"
                f"Detalhes técnicos:\n{erro}"
            )

            return

        # ----------------------------------------------------
        # Somente agora removemos o login.
        # ----------------------------------------------------

        print(
            "Removendo tela de login..."
        )

        if self.login_view is not None:

            try:

                self.login_view.destroy()

            except Exception as e:

                print(
                    f"Erro ao remover login: {e}"
                )

        self.login_view = None
        self.coleta_view = nova_tela

        self.update_idletasks()

        print(
            "=========================================="
        )

        print(
            "TELA PRINCIPAL CARREGADA COM SUCESSO"
        )

        print(
            "=========================================="
        )

    # ========================================================
    # FECHAR
    # ========================================================

    def fechar_aplicacao(self):

        try:

            self.destroy()

        except Exception:

            sys.exit(0)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    try:

        # ----------------------------------------------------
        # CONFIGURAÇÕES CUSTOMTKINTER
        # ----------------------------------------------------

        ctk.set_appearance_mode(
            "System"
        )

        ctk.set_default_color_theme(
            "blue"
        )

        # ----------------------------------------------------
        # CRIA APP
        # ----------------------------------------------------

        app = App()

        # ----------------------------------------------------
        # LOOP PRINCIPAL
        # ----------------------------------------------------

        app.mainloop()

    except Exception:

        erro = traceback.format_exc()

        print(
            "=========================================="
        )

        print(
            "ERRO FATAL DO APLICATIVO"
        )

        print(
            erro
        )

        print(
            "=========================================="
        )

        try:

            messagebox.showerror(
                "Erro fatal - AutoJuris IA",
                erro
            )

        except:

            pass