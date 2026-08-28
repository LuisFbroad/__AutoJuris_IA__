from scrapers.trf5_scraper import TRF5Scraper
from scrapers.processo_scraper import ProcessoScraper


class TRF5Service:

    def __init__(
        self,
        documento=None,
        tipo_documento="CPF",
        max_threads=5
    ):
        """
        Serviço responsável por controlar a coleta do TRF5.

        O documento é opcional no construtor para permitir:

            service = TRF5Service(
                documento="12345678900",
                tipo_documento="CPF"
            )

        ou:

            service = TRF5Service(
                max_threads=5
            )

        e informar o documento posteriormente.
        """

        self.documento = documento
        self.tipo_documento = tipo_documento or "CPF"
        self.max_threads = max_threads

        self.scraper = None
        self.processo_scraper = None

        # Se o documento já foi informado,
        # podemos criar o scraper imediatamente.
        if self.documento:
            self._criar_scrapers()

    # ============================================================
    # CRIAR SCRAPERS
    # ============================================================

    def _criar_scrapers(self):
        """
        Cria os scrapers necessários para a consulta.
        """

        if not self.documento:
            raise ValueError(
                "Documento não informado."
            )

        self.scraper = TRF5Scraper(
            documento=self.documento,
            tipo_documento=self.tipo_documento,
            max_threads=self.max_threads
        )

        # O ProcessoScraper utiliza a mesma sessão HTTP
        # do TRF5Scraper quando os detalhes forem necessários.
        self.processo_scraper = None

    # ============================================================
    # CONFIGURAR CONSULTA
    # ============================================================

    def configurar(
        self,
        documento,
        tipo_documento="CPF"
    ):
        """
        Permite configurar ou alterar o documento da consulta.
        """

        if not documento:
            raise ValueError(
                "Documento não informado."
            )

        self.documento = documento
        self.tipo_documento = tipo_documento or "CPF"

        self._criar_scrapers()

    # ============================================================
    # GARANTIR SCRAPER
    # ============================================================

    def _garantir_scraper(
        self,
        documento=None,
        tipo_documento=None
    ):
        """
        Garante que o scraper esteja configurado.
        """

        if documento:
            self.documento = documento

        if tipo_documento:
            self.tipo_documento = tipo_documento

        if not self.documento:
            raise ValueError(
                "Documento não informado."
            )

        if self.scraper is None:
            self._criar_scrapers()

    # ============================================================
    # COLETAR PROCESSOS
    # ============================================================

    def coletar_processos(
        self,
        documento=None,
        tipo_documento=None,
        limite_paginas=None,
        extrair_detalhes=True
    ):
        """
        Realiza a coleta dos processos.

        Parâmetros:

            documento:
                CPF/CNPJ utilizado na consulta.

            tipo_documento:
                CPF ou CNPJ.

            limite_paginas:
                Número máximo de páginas a consultar.

                Exemplo:
                    1  -> somente página 1
                    5  -> páginas 1 até 5
                    None -> todas as páginas

            extrair_detalhes:
                Se True, acessa os processos para buscar
                informações adicionais.
        """

        self._garantir_scraper(
            documento=documento,
            tipo_documento=tipo_documento
        )

        print()
        print("=" * 60)
        print("INICIANDO COLETA TRF5")
        print("=" * 60)

        print(
            f"Documento: {self.documento}"
        )

        print(
            f"Tipo: {self.tipo_documento}"
        )

        print(
            f"Páginas: "
            f"{limite_paginas if limite_paginas is not None else 'TODAS'}"
        )

        print()

        # ========================================================
        # TODAS AS PÁGINAS
        # ========================================================

        resultado = self.scraper.buscar_todas_paginas(
            max_paginas=limite_paginas,
            extrair_detalhes=extrair_detalhes
        )

        # ========================================================
        # RESULTADO
        # ========================================================

        processos = resultado.get(
            "processos",
            []
        )

        total = resultado.get(
            "total",
            0
        )

        total_paginas = resultado.get(
            "total_paginas",
            0
        )

        print()
        print("=" * 60)
        print("COLETA FINALIZADA")
        print("=" * 60)

        print(
            f"Total informado pelo TRF5: {total}"
        )

        print(
            f"Páginas processadas: {total_paginas}"
        )

        print(
            f"Processos coletados: {len(processos)}"
        )

        print("=" * 60)

        return resultado

    # ============================================================
    # BUSCAR UMA PÁGINA
    # ============================================================

    def buscar_pagina(
        self,
        pagina=1,
        documento=None,
        tipo_documento=None,
        extrair_detalhes=False
    ):
        """
        Busca somente uma página específica.

        Exemplo:

            service.buscar_pagina(
                pagina=3
            )
        """

        self._garantir_scraper(
            documento=documento,
            tipo_documento=tipo_documento
        )

        if extrair_detalhes:
            return self.scraper.buscar_pagina_com_detalhes(
                pagina=pagina
            )

        return self.scraper.buscar_pagina(
            pagina=pagina
        )

    # ============================================================
    # BUSCAR DETALHES DE UM PROCESSO
    # ============================================================

    def buscar_detalhes_processo(
        self,
        link
    ):
        """
        Busca os detalhes de um processo específico.
        """

        if not link:
            raise ValueError(
                "Link do processo não informado."
            )

        # Se já temos scraper, aproveitamos a sessão HTTP.
        if self.scraper is not None:

            if self.processo_scraper is None:
                self.processo_scraper = ProcessoScraper(
                    session=self.scraper.session,
                    max_threads=self.max_threads
                )

        else:
            # Caso o método seja chamado antes de uma coleta,
            # cria um ProcessoScraper independente.
            self.processo_scraper = ProcessoScraper(
                max_threads=self.max_threads
            )

        return self.processo_scraper.extrair_detalhes_processo(
            link
        )