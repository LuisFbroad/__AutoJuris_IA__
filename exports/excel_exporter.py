from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Exporta processos do TRF5 para Excel, incluindo informações do RSS."""

    COLUNAS = [
        "Nome",
        "Número Processo",
        "Proc. Originário",
        "Vara",
        "Banco",
        "Nº RPV",
        "Fase Atual",
        "Requerente (RSS)",
        "Requerido (RSS)",
        "Advogado (RSS)",
        "Escritório (RSS)",
        "Nº RPV (RSS)",
        "Movimentações (RSS)",
        "Status RSS",
        "Coletado em",
    ]

    LARGURAS = {
        "Nome": 32,
        "Número Processo": 28,
        "Proc. Originário": 28,
        "Vara": 20,
        "Banco": 30,
        "Nº RPV": 22,
        "Fase Atual": 24,
        "Requerente (RSS)": 32,
        "Requerido (RSS)": 32,
        "Advogado (RSS)": 32,
        "Escritório (RSS)": 32,
        "Nº RPV (RSS)": 22,
        "Movimentações (RSS)": 65,
        "Status RSS": 32,
        "Coletado em": 22,
    }

    def __init__(self, pasta_saida: str | Path = "output"):
        self.pasta_saida = Path(pasta_saida)

    @staticmethod
    def _texto(valor: Any) -> str:
        """Converte valores em texto sem exibir None ou estruturas cruas."""
        if valor is None:
            return ""

        if isinstance(valor, (dict, list, tuple)):
            return ""

        return str(valor).strip()

    @staticmethod
    def _primeiro(*valores: Any) -> Any:
        """Retorna o primeiro valor preenchido."""
        for valor in valores:
            if valor is not None and str(valor).strip():
                return valor
        return ""

    @staticmethod
    def _normalizar_chave(chave: Any) -> str:
        return re.sub(
            r"[^a-z0-9]",
            "",
            str(chave)
            .lower()
            .replace("á", "a")
            .replace("ã", "a")
            .replace("â", "a")
            .replace("é", "e")
            .replace("ê", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ô", "o")
            .replace("õ", "o")
            .replace("ú", "u")
            .replace("ç", "c"),
        )

    @classmethod
    def _obter(cls, dados: dict, *nomes: str) -> Any:
        """Localiza uma chave aceitando variações de acentuação e escrita."""
        for nome in nomes:
            if nome in dados and dados[nome] not in (None, ""):
                return dados[nome]

        normalizados = {
            cls._normalizar_chave(chave): valor for chave, valor in dados.items()
        }

        for nome in nomes:
            chave = cls._normalizar_chave(nome)
            valor = normalizados.get(chave)
            if valor not in (None, ""):
                return valor

        return ""

    @classmethod
    def _dados_rss(cls, processo: dict) -> dict:
        dados = processo.get("dados_rss")

        if isinstance(dados, dict):
            return dados

        # Compatibilidade caso os campos RSS estejam no próprio processo.
        return processo

    @staticmethod
    def _formatar_movimentacoes(valor: Any) -> str:
        """Converte movimentações em texto legível dentro da célula."""
        if not valor:
            return ""

        if isinstance(valor, str):
            return valor.strip()

        if isinstance(valor, dict):
            valor = [valor]

        if not isinstance(valor, (list, tuple)):
            return str(valor)

        linhas = []

        for movimento in valor:
            if isinstance(movimento, str):
                texto = movimento.strip()
                if texto:
                    linhas.append(texto)
                continue

            if not isinstance(movimento, dict):
                linhas.append(str(movimento))
                continue

            data = (
                movimento.get("data")
                or movimento.get("data_movimento")
                or movimento.get("data_movimentacao")
                or movimento.get("dataHora")
                or ""
            )

            descricao = (
                movimento.get("descricao")
                or movimento.get("descrição")
                or movimento.get("texto")
                or movimento.get("movimento")
                or movimento.get("conteudo")
                or movimento.get("conteúdo")
                or movimento.get("titulo")
                or movimento.get("title")
                or ""
            )

            data = str(data).strip()
            descricao = str(descricao).strip()

            if data and descricao:
                linhas.append(f"{data} — {descricao}")
            elif data or descricao:
                linhas.append(data or descricao)
            else:
                # Preserva o conteúdo de estruturas desconhecidas.
                partes = [
                    f"{chave}: {conteudo}"
                    for chave, conteudo in movimento.items()
                    if conteudo not in (None, "")
                ]
                if partes:
                    linhas.append(" | ".join(partes))

        return "\n".join(linhas)

    @classmethod
    def _preparar_linha(cls, processo: dict) -> dict:
        rss = cls._dados_rss(processo)

        numero_processo = cls._primeiro(
            processo.get("numero"),
            processo.get("processo"),
            processo.get("numero_processo"),
        )

        movimentacoes = cls._primeiro(
            processo.get("movimentacoes_rss"),
            rss.get("movimentacoes"),
            rss.get("movements"),
        )

        status_rss = cls._primeiro(
            processo.get("erro_rss"),
            rss.get("status"),
            rss.get("situacao"),
        )

        if not status_rss:
            status_rss = (
                "RSS consultado" if processo.get("dados_rss") else "Sem dados RSS"
            )

        return {
            "Nome": cls._primeiro(
                processo.get("nome"),
                processo.get("beneficiario"),
                processo.get("parte"),
            ),
            "Número Processo": numero_processo,
            "Proc. Originário": cls._primeiro(
                processo.get("processo_originario"),
                processo.get("proc_originario"),
            ),
            "Vara": processo.get("vara", ""),
            "Banco": cls._formatar_banco(
                cls._primeiro(
                    processo.get("banco"),
                    processo.get("instituicao_bancaria"),
                )
            ),
            "Nº RPV": cls._primeiro(
                processo.get("rpv"),
                processo.get("numero_rpv"),
            ),
            "Fase Atual": cls._primeiro(
                processo.get("fase_atual"),
                processo.get("fase"),
            ),
            "Requerente (RSS)": cls._primeiro(
                processo.get("requerente_rss"),
                rss.get("requerente"),
            ),
            "Requerido (RSS)": cls._primeiro(
                processo.get("requerido_rss"),
                rss.get("requerido"),
            ),
            "Advogado (RSS)": cls._primeiro(
                processo.get("advogado_rss"),
                rss.get("advogado"),
            ),
            "Escritório (RSS)": cls._primeiro(
                processo.get("escritorio_rss"),
                rss.get("escritorio"),
            ),
            "Nº RPV (RSS)": cls._primeiro(
                rss.get("numero_rpv"),
                rss.get("rpv"),
                processo.get("rpv"),
            ),
            "Movimentações (RSS)": cls._formatar_movimentacoes(movimentacoes),
            "Status RSS": status_rss,
            "Coletado em": cls._primeiro(
                processo.get("data_hora_coleta"),
                processo.get("coletado_em"),
                datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            ),
        }

    @staticmethod
    def _formatar_banco(valor: Any) -> str:
        texto = str(valor or "").strip()

        if not texto:
            return ""

        chave = texto.upper().replace("Ã", "A").replace("Õ", "O").replace("Ç", "C")

        if "CAIXA" in chave:
            return "CAIXA ECONÔMICA FEDERAL"

        if "BANCO DO BRASIL" in chave:
            return "BANCO DO BRASIL"

        return texto

    def exportar(self, processos: Any) -> str:
        """Gera o Excel e retorna o caminho do arquivo criado."""
        if isinstance(processos, dict):
            processos = processos.get("processos", [])

        if not isinstance(processos, (list, tuple)):
            raise TypeError(
                "Os processos devem ser uma lista ou um dicionário "
                "contendo a chave 'processos'."
            )

        self.pasta_saida.mkdir(parents=True, exist_ok=True)

        agora = datetime.now()
        nome_arquivo = f"relatorio_rpv_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        caminho = self.pasta_saida / nome_arquivo

        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório RPV"

        ws.append(self.COLUNAS)

        # Cabeçalho.
        preenchimento_cabecalho = PatternFill(
            fill_type="solid",
            fgColor="17365D",
        )
        fonte_cabecalho = Font(
            name="Calibri",
            size=11,
            bold=True,
            color="FFFFFF",
        )

        for celula in ws[1]:
            celula.fill = preenchimento_cabecalho
            celula.font = fonte_cabecalho
            celula.alignment = Alignment(
                horizontal="center",
                vertical="center",
                wrap_text=True,
            )

        # Linhas de dados.
        for processo in processos:
            if not isinstance(processo, dict):
                logger.warning(
                    "Registro ignorado: esperado dict, recebido %s",
                    type(processo).__name__,
                )
                continue

            linha = self._preparar_linha(processo)
            ws.append([linha.get(coluna, "") for coluna in self.COLUNAS])

            numero_linha = ws.max_row

            # Destaca o número do processo como link, quando disponível.
            numero = str(linha.get("Número Processo") or "").strip()
            url = self._primeiro(
                processo.get("link"),
                processo.get("url"),
                processo.get("url_processo"),
            )

            if url and numero:
                celula = ws.cell(
                    row=numero_linha,
                    column=self.COLUNAS.index("Número Processo") + 1,
                )
                celula.hyperlink = str(url)
                celula.style = "Hyperlink"
            elif numero:
                # O padrão de consulta do TRF5 utiliza o número CNJ.
                if re.fullmatch(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}", numero):
                    celula = ws.cell(
                        row=numero_linha,
                        column=self.COLUNAS.index("Número Processo") + 1,
                    )
                    celula.hyperlink = "https://cp.trf5.jus.br/processo/" + quote(
                        numero, safe="-."
                    )
                    celula.style = "Hyperlink"

            for celula in ws[numero_linha]:
                celula.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

            # Alternância visual das linhas.
            if numero_linha % 2 == 0:
                preenchimento = PatternFill(
                    fill_type="solid",
                    fgColor="EAF0F7",
                )
                for celula in ws[numero_linha]:
                    celula.fill = preenchimento

        # Ajustes gerais.
        ws.freeze_panes = "A2"
        ws.sheet_view.showGridLines = False
        ws.row_dimensions[1].height = 32

        for indice, coluna in enumerate(self.COLUNAS, start=1):
            ws.column_dimensions[get_column_letter(indice)].width = self.LARGURAS.get(
                coluna, 20
            )

        # Filtro automático.
        if ws.max_row >= 1:
            ws.auto_filter.ref = ws.dimensions

        # Permite que as movimentações sejam lidas sem expandir demais
        # todas as linhas da planilha.
        for numero_linha in range(2, ws.max_row + 1):
            ws.row_dimensions[numero_linha].height = 45

        # Metadados do arquivo.
        wb.properties.title = "Relatório de processos e RPVs - TRF5"
        wb.properties.subject = "Dados coletados via HTML e RSS"
        wb.properties.creator = "AutoJuris IA"

        try:
            wb.save(caminho)
        except PermissionError as exc:
            raise PermissionError(
                "Não foi possível salvar o Excel. Verifique se o arquivo "
                "está aberto no Excel e se a pasta de saída permite gravação."
            ) from exc

        logger.info(
            "Relatório Excel criado: %s (%s processos)",
            caminho,
            ws.max_row - 1,
        )

        return str(caminho)

    def exportar_processos(self, processos: Any) -> str:
        """Alias para compatibilidade com chamadas antigas."""
        return self.exportar(processos)
