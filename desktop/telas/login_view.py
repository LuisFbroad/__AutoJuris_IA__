import customtkinter as ctk

from auth.auth_service import autenticar


class LoginView(ctk.CTkFrame):

    def __init__(self, parent, on_login):
        super().__init__(
            parent,
            corner_radius=0
        )

        self.parent = parent
        self.on_login = on_login

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.criar_interface()

    # ========================================================
    # INTERFACE
    # ========================================================

    def criar_interface(self):

        self.card = ctk.CTkFrame(
            self,
            width=420,
            height=500,
            corner_radius=15
        )

        self.card.grid(
            row=0,
            column=0,
            padx=20,
            pady=20
        )

        self.card.grid_columnconfigure(
            0,
            weight=1
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = ctk.CTkLabel(
            self.card,
            text="AutoJuris IA",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        titulo.grid(
            row=0,
            column=0,
            padx=40,
            pady=(45, 5)
        )

        subtitulo = ctk.CTkLabel(
            self.card,
            text="Acesso ao sistema",
            font=ctk.CTkFont(
                size=14
            )
        )

        subtitulo.grid(
            row=1,
            column=0,
            padx=40,
            pady=(0, 30)
        )

        # ----------------------------------------------------
        # USUÁRIO
        # ----------------------------------------------------

        self.usuario_entry = ctk.CTkEntry(
            self.card,
            width=300,
            height=42,
            placeholder_text="Usuário"
        )

        self.usuario_entry.grid(
            row=2,
            column=0,
            padx=40,
            pady=10
        )

        # ----------------------------------------------------
        # SENHA
        # ----------------------------------------------------

        self.senha_entry = ctk.CTkEntry(
            self.card,
            width=300,
            height=42,
            placeholder_text="Senha",
            show="*"
        )

        self.senha_entry.grid(
            row=3,
            column=0,
            padx=40,
            pady=10
        )

        # ----------------------------------------------------
        # MENSAGEM
        # ----------------------------------------------------

        self.mensagem = ctk.CTkLabel(
            self.card,
            text="",
            wraplength=300
        )

        self.mensagem.grid(
            row=4,
            column=0,
            padx=40,
            pady=10
        )

        # ----------------------------------------------------
        # BOTÃO ENTRAR
        # ----------------------------------------------------

        self.botao_entrar = ctk.CTkButton(
            self.card,
            text="ENTRAR",
            width=300,
            height=42,
            command=self.entrar
        )

        self.botao_entrar.grid(
            row=5,
            column=0,
            padx=40,
            pady=(10, 20)
        )

        # ----------------------------------------------------
        # ENTER
        # ----------------------------------------------------

        self.senha_entry.bind(
            "<Return>",
            lambda event: self.entrar()
        )

        self.usuario_entry.bind(
            "<Return>",
            lambda event: self.senha_entry.focus()
        )

        self.usuario_entry.focus()

    # ========================================================
    # LOGIN
    # ========================================================

    def entrar(self):

        usuario = self.usuario_entry.get().strip()
        senha = self.senha_entry.get()

        if not usuario or not senha:

            self.mostrar_mensagem(
                "Informe usuário e senha."
            )

            return

        # Desabilita o botão enquanto processa
        self.botao_entrar.configure(
            state="disabled"
        )

        try:

            resultado = autenticar(
                usuario,
                senha
            )

            if resultado:

                self.mensagem.configure(
                    text=""
                )

                print("================================")
                print("LOGIN REALIZADO COM SUCESSO")
                print(f"Usuário: {usuario}")
                print("Chamando tela principal...")
                print("================================")

                # IMPORTANTE:
                # A troca para a tela principal
                # será feita pelo main.py
                self.on_login(usuario)

            else:

                print("Login recusado.")

                self.mostrar_mensagem(
                    "Usuário ou senha inválidos."
                )

                self.senha_entry.delete(
                    0,
                    "end"
                )

                self.senha_entry.focus()

                self.botao_entrar.configure(
                    state="normal"
                )

        except Exception as e:

            print("================================")
            print("ERRO DURANTE O LOGIN")
            print(type(e).__name__)
            print(str(e))
            print("================================")

            self.mostrar_mensagem(
                f"Erro ao realizar login:\n{e}"
            )

            self.botao_entrar.configure(
                state="normal"
            )

    # ========================================================
    # MENSAGEM
    # ========================================================

    def mostrar_mensagem(self, mensagem):

        self.mensagem.configure(
            text=mensagem
        )