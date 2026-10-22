"""Coletor RSS/XML do acompanhamento processual do TRF5."""
from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urljoin

import requests

PROCESSO_RE = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}\b")
RPV_RE = re.compile(r"\bRPV\s*(\d+)\s*-\s*([A-Z]{2})\b", re.IGNORECASE)


class TRF5RSSException(Exception):
    """Erro-base do coletor RSS do TRF5."""


class TRF5RSSFetchError(TRF5RSSException):
    """Falha ao baixar o feed RSS."""


class TRF5RSSParseError(TRF5RSSException):
    """Falha ao interpretar o RSS/XML."""


@dataclass
class MovimentacaoProcessual:
    titulo: str
    data_publicacao: datetime | None
    link: str = ""
    guid: str = ""
    descricao: str = ""

    def to_dict(self) -> dict[str, Any]:
        dados = asdict(self)
        dados["data_publicacao"] = (
            self.data_publicacao.isoformat() if self.data_publicacao else None
        )
        return dados


@dataclass
class ProcessoRSS:
    numero_processo: str
    titulo_feed: str = ""
    requerente: str = ""
    requerido: str = ""
    advogado: str = ""
    escritorio: str = ""
    numero_rpv: str = ""
    link_processo: str = ""
    publicado_em: datetime | None = None
    atualizado_em: datetime | None = None
    movimentacoes: list[MovimentacaoProcessual] | None = None

    def __post_init__(self) -> None:
        if self.movimentacoes is None:
            self.movimentacoes = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "numero_processo": self.numero_processo,
            "titulo_feed": self.titulo_feed,
            "requerente": self.requerente,
            "requerido": self.requerido,
            "advogado": self.advogado,
            "escritorio": self.escritorio,
            "numero_rpv": self.numero_rpv,
            "link_processo": self.link_processo,
            "publicado_em": self.publicado_em.isoformat() if self.publicado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
            "movimentacoes": [m.to_dict() for m in self.movimentacoes or []],
        }


def _texto(elemento: ET.Element | None) -> str:
    """Extrai texto do elemento e remove marcação HTML eventualmente embutida."""
    if elemento is None:
        return ""
    bruto = "".join(elemento.itertext())
    bruto = html.unescape(bruto)
    bruto = re.sub(r"<br\s*/?>", "\n", bruto, flags=re.IGNORECASE)
    bruto = re.sub(r"</(?:p|div|li)\s*>", "\n", bruto, flags=re.IGNORECASE)
    bruto = re.sub(r"<[^>]+>", " ", bruto)
    return re.sub(r"[ \t\r\f\v]+", " ", bruto).strip()


def _data_rss(valor: str) -> datetime | None:
    if not valor.strip():
        return None
    try:
        return parsedate_to_datetime(valor.strip())
    except (TypeError, ValueError, OverflowError):
        try:
            return datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
        except ValueError:
            return None


def _campo_descricao(descricao: str, rotulo: str) -> str:
    rotulos = r"REQTE|REQDO|Advogado/Procurador|Escritório Advocatício"
    padrao = re.compile(
        rf"(?:^|\n|\s){re.escape(rotulo)}\s*:\s*(.*?)"
        rf"(?=\n\s*(?:{rotulos})\s*:|$)",
        re.IGNORECASE | re.DOTALL,
    )
    encontrado = padrao.search(descricao)
    if not encontrado:
        return ""
    return re.sub(r"\s+", " ", encontrado.group(1)).strip()


def parsear_rss_trf5(xml_texto: str, url_base: str = "") -> ProcessoRSS:
    """Interpreta um RSS 2.0 do TRF5."""
    try:
        raiz = ET.fromstring(xml_texto.lstrip("\ufeff \t\r\n"))
    except ET.ParseError as exc:
        raise TRF5RSSParseError(f"XML inválido: {exc}") from exc

    canal = raiz.find("channel")
    if canal is None:
        # Suporte básico a namespaces, caso o feed venha com prefixos XML.
        canal = next((el for el in raiz.iter() if el.tag.split("}")[-1] == "channel"), None)
    if canal is None:
        raise TRF5RSSParseError("Não foi encontrado o elemento <channel> do RSS.")

    def filho_texto(pai: ET.Element, nome: str) -> str:
        elemento = next(
            (el for el in list(pai) if el.tag.split("}")[-1] == nome),
            None,
        )
        return _texto(elemento)

    titulo = filho_texto(canal, "title")
    descricao = filho_texto(canal, "description")
    link_canal = filho_texto(canal, "link")
    numero_match = PROCESSO_RE.search(titulo) or PROCESSO_RE.search(link_canal)
    if not numero_match:
        raise TRF5RSSParseError(
            "Não foi possível identificar o número CNJ no título ou link do feed."
        )

    # Mantém as quebras de linha do HTML da descrição para identificar os rótulos.
    descricao_html = next(
        (el.text or "" for el in list(canal) if el.tag.split("}")[-1] == "description"),
        "",
    )
    descricao_normalizada = html.unescape(descricao_html)
    descricao_normalizada = re.sub(
        r"<br\s*/?>|</(?:p|div|li)\s*>",
        "\n",
        descricao_normalizada,
        flags=re.IGNORECASE,
    )
    descricao_normalizada = re.sub(r"<[^>]+>", "\n", descricao_normalizada)
    descricao_normalizada = re.sub(r"\r", "\n", descricao_normalizada)
    descricao_normalizada = re.sub(r"\n{2,}", "\n", descricao_normalizada).strip()

    rpv_match = RPV_RE.search(descricao)
    itens: list[MovimentacaoProcessual] = []

    for item in list(canal):
        if item.tag.split("}")[-1] != "item":
            continue
        item_titulo = filho_texto(item, "title")
        item_link = filho_texto(item, "link")
        item_guid = filho_texto(item, "guid")
        item_desc = filho_texto(item, "description")
        data = _data_rss(filho_texto(item, "pubDate"))
        if item_link:
            item_link = urljoin(url_base or link_canal, item_link)
        itens.append(
            MovimentacaoProcessual(
                titulo=item_titulo,
                data_publicacao=data,
                link=item_link,
                guid=item_guid,
                descricao=item_desc,
            )
        )

    return ProcessoRSS(
        numero_processo=numero_match.group(0),
        titulo_feed=titulo,
        requerente=_campo_descricao(descricao_normalizada, "REQTE"),
        requerido=_campo_descricao(descricao_normalizada, "REQDO"),
        advogado=_campo_descricao(descricao_normalizada, "Advogado/Procurador"),
        escritorio=_campo_descricao(descricao_normalizada, "Escritório Advocatício"),
        numero_rpv=(
            f"RPV{rpv_match.group(1)}-{rpv_match.group(2).upper()}"
            if rpv_match else ""
        ),
        link_processo=urljoin(url_base or link_canal, link_canal) if link_canal else "",
        publicado_em=_data_rss(filho_texto(canal, "pubDate")),
        atualizado_em=_data_rss(filho_texto(canal, "lastBuildDate")),
        movimentacoes=itens,
    )


class TRF5RSSScraper:
    """Cliente HTTP testável para obter o feed RSS de um processo."""

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: tuple[float, float] = (5.0, 20.0),
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.setdefault(
            "User-Agent",
            "Mozilla/5.0 (compatible; AutoJurisIA/1.0)",
        )

    def buscar_feed(self, url_rss: str) -> ProcessoRSS:
        if not url_rss or not url_rss.strip():
            raise ValueError("Informe a URL completa do feed RSS do processo.")
        try:
            resposta = self.session.get(url_rss, timeout=self.timeout)
            resposta.raise_for_status()
        except requests.RequestException as exc:
            raise TRF5RSSFetchError(
                f"Falha ao consultar o RSS do TRF5: {exc}"
            ) from exc

        texto_xml = resposta.text.lstrip("\ufeff \t\r\n")
        if not texto_xml.startswith("<"):
            content_type = resposta.headers.get("Content-Type", "não informado")
            raise TRF5RSSParseError(
                f"A resposta não parece ser XML (Content-Type: {content_type})."
            )
        return parsear_rss_trf5(texto_xml, url_base=url_rss)
