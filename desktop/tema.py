"""Tema visual institucional do GAGC Advogados e Associados.

Mantém CustomTkinter e centraliza as cores, fontes, espaçamentos
e dimensões da aplicação, sem alterar a lógica de negócio.
"""

import customtkinter as ctk

# ============================================================
# IDENTIDADE VISUAL — GAGC ADVOGADOS E ASSOCIADOS
# ============================================================

CORES = {
    # Navegação
    "sidebar": "#142B4A",
    "sidebar_hover": "#203F66",
    "sidebar_selected": "#B49355",
    # Superfícies
    "fundo": ("#F4F6F9", "#101923"),
    "superficie": ("#FFFFFF", "#192635"),
    "superficie_secundaria": ("#E9EEF4", "#202F40"),
    # Textos
    "texto": ("#172B43", "#F2F5F8"),
    "texto_secundario": ("#607086", "#AAB7C7"),
    # Bordas
    "borda": ("#DCE4EE", "#2B3B4D"),
    # Cores institucionais
    "primaria": "#17365D",
    "primaria_hover": "#244B76",
    "dourado": "#B49355",
    "dourado_hover": "#9C7B40",
    # Estados
    "sucesso": "#23845B",
    "aviso": "#B7791F",
    "erro": "#C44545",
    "informacao": "#3B75A5",
    # Neutras
    "branco": "#FFFFFF",
    "preto": "#000000",
}


# ============================================================
# TIPOGRAFIA
# ============================================================

FONTES = {
    "familia": "Segoe UI",
    "titulo": 24,
    "subtitulo": 16,
    "corpo": 13,
    "pequena": 11,
    "botao": 13,
    "destaque": 20,
}


# ============================================================
# ESPAÇAMENTOS
# ============================================================

ESPACAMENTOS = {
    "xs": 4,
    "sm": 8,
    "md": 14,
    "lg": 20,
    "xl": 28,
}


# ============================================================
# DIMENSÕES DA JANELA
# ============================================================

DIMENSOES = {
    "largura_sidebar": 220,
    "largura_janela": 1180,
    "altura_janela": 760,
    "largura_minima": 960,
    "altura_minima": 620,
}


def configurar_tema():
    """Configura o modo visual institucional do aplicativo."""

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def obter_fonte(tamanho=None, peso="normal"):
    """Retorna uma fonte padronizada para os componentes da interface."""

    if tamanho is None:
        tamanho = FONTES["corpo"]

    return (FONTES["familia"], tamanho, peso)
