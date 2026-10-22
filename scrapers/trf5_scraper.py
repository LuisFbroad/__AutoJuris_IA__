"""Scraper de RPVs/precatórios do TRF5 por CPF/CNPJ."""

from __future__ import annotations

import logging
import math
import os
import re
from time import perf_counter
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from scrapers.processo_scraper import ProcessoScraper
from scrapers.trf5_rss_scraper import TRF5RSSScraper

load_dotenv()
logger = logging.getLogger(__name__)
TRF5_BASE_URL = os.getenv("TRF5_BASE_URL", "https://cp.trf5.jus.br").rstrip("/")
TIMEOUT = (8, 30)

PROCESSO_RE = re.compile(r"\b\d{7}-\d{2}\.\d{4}\.4\.05\.\d{4}\b")
RPV_RE = re.compile(r"\bRPV\s*\d+\s*-\s*[A-Z]{2}\b", re.I)
DATA_RE = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
HORA_RE = re.compile(r"\b\d{2}:\d{2}\b")
TOTAL_RE = re.compile(r"\bTotal\s*:\s*([\d.]+)", re.I)


class TRF5Scraper:
    """Busca processos no TRF5 e opcionalmente complementa com RSS."""

    def __init__(
        self,
        documento,
        tipo_documento="CPF",
        max_threads=5,
        *,
        session=None,
        timeout=TIMEOUT,
        processos_por_pagina=10,
    ):
        self.documento = re.sub(r"\D", "", str(documento or ""))
        if not self.documento:
            raise ValueError("Documento não informado ou inválido.")
        tipo = (tipo_documento or "CPF").upper()
        if tipo not in {"CPF", "CNPJ"}:
            raise ValueError("tipo_documento deve ser CPF ou CNPJ.")
        if int(max_threads) < 1 or int(processos_por_pagina) < 1:
            raise ValueError("max_threads e processos_por_pagina devem ser positivos.")

        self.tipo_documento = tipo
        self.max_threads = int(max_threads)
        self.base_url = TRF5_BASE_URL
        self.timeout = timeout
        self.processos_por_pagina = int(processos_por_pagina)
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9",
            }
        )

    def fechar(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.fechar()

    def montar_url(self, pagina=1):
        pagina = int(pagina)
        if pagina < 1:
            raise ValueError("A numeração das páginas começa em 1.")
        return (
            f"{self.base_url}/processo/rpvprec/filtroRPVPrec/cpfcnpj/porData/"
            f"tiporpv/ativos/vinculados/{self.documento}//{pagina - 1}"
        )

    @staticmethod
    def _texto(elemento):
        return elemento.get_text(" ", strip=True) if elemento else ""

    def extrair_total(self, soup):
        match = TOTAL_RE.search(soup.get_text(" ", strip=True))
        if not match:
            return 0
        try:
            return int(match.group(1).replace(".", ""))
        except ValueError:
            logger.warning("Total de resultados em formato inesperado.")
            return 0

    def extrair_processos(self, soup):
        processos, vistos = [], set()
        for link in soup.find_all("a", href=True):
            href = str(link.get("href", "")).strip()
            match = PROCESSO_RE.search(self._texto(link)) or PROCESSO_RE.search(href)
            if not match:
                continue
            numero = match.group(0)
            if numero in vistos:
                continue
            vistos.add(numero)

            linha = link.find_parent("tr")
            texto_linha = self._texto(linha)
            contexto = texto_linha or self._texto(link.parent)
            rpv_match = RPV_RE.search(contexto)
            data_match = DATA_RE.search(texto_linha)
            hora_match = HORA_RE.search(texto_linha)
            situacao = ""
            if re.search(r"\bprocesso\s+arquivado\b", contexto, re.I):
                situacao = "Processo Arquivado"
            elif re.search(r"\bprocesso\s+ativo\b", contexto, re.I):
                situacao = "Processo Ativo"

            processos.append(
                {
                    "link": urljoin(self.base_url + "/", href),
                    "processo": numero,
                    "processo_originario": "",
                    "rpv": (
                        re.sub(r"\s+", "", rpv_match.group(0)).upper()
                        if rpv_match
                        else ""
                    ),
                    "nome": "",
                    "vara": "",
                    "banco": "",
                    "data_decisao": "",
                    "data_movimento": data_match.group(0) if data_match else "",
                    "hora_movimento": hora_match.group(0) if hora_match else "",
                    "situacao": situacao,
                }
            )
        return processos

    def buscar_pagina(self, pagina=1):
        url = self.montar_url(pagina)
        inicio = perf_counter()
        logger.info("Consultando TRF5: página %s", pagina)
        try:
            resposta = self.session.get(url, timeout=self.timeout)
            resposta.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("Falha ao consultar página %s do TRF5", pagina)
            raise RuntimeError(
                f"Falha ao consultar página {pagina} do TRF5: {exc}"
            ) from exc

        soup = BeautifulSoup(resposta.text, "html.parser")
        total = self.extrair_total(soup)
        processos = self.extrair_processos(soup)
        logger.info(
            "Página %s: %s processo(s), total=%s, duração=%.2fs",
            pagina,
            len(processos),
            total,
            perf_counter() - inicio,
        )
        return {"pagina": pagina, "total": total, "processos": processos}

    @staticmethod
    def _mesclar_detalhes(originais, completos):
        """Mescla detalhes pelo número do processo, evitando depender da ordem."""
        completos = completos or []
        por_numero = {
            item.get("processo"): item
            for item in completos
            if isinstance(item, dict) and item.get("processo")
        }
        resultado = []
        for original in originais:
            numero = original.get("processo")
            detalhe = por_numero.get(numero, {})
            item = dict(original)
            item.update(
                {
                    chave: valor
                    for chave, valor in detalhe.items()
                    if valor not in (None, "")
                }
            )
            for chave, valor in original.items():
                if item.get(chave) in (None, "") and valor not in (None, ""):
                    item[chave] = valor
            resultado.append(item)
        return resultado

    def buscar_pagina_com_detalhes(self, pagina=1):
        resultado = self.buscar_pagina(pagina)
        processos = resultado.get("processos") or []
        if not processos:
            return resultado
        scraper = ProcessoScraper(session=self.session, max_threads=self.max_threads)
        completos = scraper.extrair_detalhes_em_lote(processos)
        resultado["processos"] = self._mesclar_detalhes(processos, completos)
        return resultado

    def enriquecer_com_rss(self, processos):
        """Adiciona dados RSS sem apagar os campos já obtidos pelo HTML."""
        rss_scraper = TRF5RSSScraper(session=self.session, timeout=(5.0, 20.0))
        try:
            for processo in processos:
                numero = str(processo.get("processo") or "").strip()
                if not PROCESSO_RE.fullmatch(numero):
                    processo["erro_rss"] = "Número CNJ ausente ou inválido."
                    continue

                url_rss = f"{self.base_url}/processo/rss/{numero}"
                try:
                    dados = rss_scraper.buscar_feed(url_rss).to_dict()
                    if dados["numero_processo"] != numero:
                        processo["erro_rss"] = (
                            "O RSS retornou outro número de processo."
                        )
                        continue

                    processo["dados_rss"] = dados
                    processo["movimentacoes_rss"] = dados.get("movimentacoes") or []
                    for campo in ("requerente", "requerido", "advogado", "escritorio"):
                        valor = dados.get(campo)
                        if valor:
                            processo[f"{campo}_rss"] = valor

                    if not processo.get("rpv") and dados.get("numero_rpv"):
                        processo["rpv"] = dados["numero_rpv"]
                    processo["erro_rss"] = ""
                except Exception as exc:
                    processo["erro_rss"] = str(exc)
                    logger.warning("Falha no RSS do processo %s: %s", numero, exc)
            return processos
        finally:
            # Não fecha a sessão compartilhada com o scraper principal.
            pass

    def buscar_todas_paginas(
        self,
        max_paginas=None,
        extrair_detalhes=True,
        enriquecer_rss=False,
    ):
        if max_paginas is not None and int(max_paginas) < 1:
            raise ValueError("max_paginas deve ser positivo ou None.")
        buscar = (
            self.buscar_pagina_com_detalhes if extrair_detalhes else self.buscar_pagina
        )
        primeira = buscar(1)
        total = int(primeira.get("total") or 0)
        paginas_estimadas = (
            math.ceil(total / self.processos_por_pagina)
            if total
            else (1 if primeira.get("processos") else 0)
        )
        total_paginas = (
            min(paginas_estimadas, int(max_paginas))
            if max_paginas is not None
            else paginas_estimadas
        )

        todos = list(primeira.get("processos") or [])
        por_numero = {p.get("processo"): p for p in todos if p.get("processo")}
        for pagina in range(2, total_paginas + 1):
            resultado = buscar(pagina)
            for processo in resultado.get("processos") or []:
                numero = processo.get("processo")
                if numero and numero in por_numero:
                    existente = por_numero[numero]
                    for chave, valor in processo.items():
                        if existente.get(chave) in (None, "") and valor not in (
                            None,
                            "",
                        ):
                            existente[chave] = valor
                else:
                    todos.append(processo)
                    if numero:
                        por_numero[numero] = processo
            logger.info(
                "Progresso: página %s/%s; acumulado=%s",
                pagina,
                total_paginas,
                len(todos),
            )

        if enriquecer_rss and todos:
            todos = self.enriquecer_com_rss(todos)

        return {"total": total, "total_paginas": total_paginas, "processos": todos}

    @staticmethod
    def comparar_resultados(primeira_busca, segunda_busca):
        mapa1 = {p.get("processo"): p for p in primeira_busca if p.get("processo")}
        mapa2 = {p.get("processo"): p for p in segunda_busca if p.get("processo")}
        ids1, ids2 = set(mapa1), set(mapa2)
        return {
            "igual": ids1 == ids2,
            "adicionados": sorted(ids2 - ids1),
            "removidos": sorted(ids1 - ids2),
            "mantidos": sorted(ids1 & ids2),
            "total_primeira": len(ids1),
            "total_segunda": len(ids2),
        }
