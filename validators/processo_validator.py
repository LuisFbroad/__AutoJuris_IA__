import re


class ProcessoValidator:
    """
    Valida os dados extraídos dos processos do TRF5
    e calcula um score de confiança.
    """

    PADRAO_CNJ = re.compile(
        r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"
    )

    PADRAO_RPV = re.compile(
        r"^RPV\d+-[A-Z]{2}$",
        re.IGNORECASE
    )

    ESTADOS_VALIDOS = {
        "AL",
        "PE",
        "CE",
        "PB",
        "RN",
        "SE",
    }

    # =========================================================
    # PROCESSO
    # =========================================================

    @classmethod
    def validar_processo(cls, processo):
        if not processo:
            return False

        processo = processo.strip()

        return bool(
            cls.PADRAO_CNJ.match(processo)
        )

    # =========================================================
    # RPV
    # =========================================================

    @classmethod
    def validar_rpv(cls, rpv):
        if not rpv:
            return False

        rpv = rpv.strip().upper()

        if not cls.PADRAO_RPV.match(rpv):
            return False

        estado = rpv[-2:]

        return estado in cls.ESTADOS_VALIDOS

    # =========================================================
    # NOME
    # =========================================================

    @staticmethod
    def validar_nome(nome):
        if not nome:
            return False

        nome = nome.strip()

        if len(nome) < 3:
            return False

        palavras_invalidas = {
            "PROCESSO",
            "BANCO",
            "VARA",
            "RPV",
        }

        if nome.upper() in palavras_invalidas:
            return False

        return True

    # =========================================================
    # DATA
    # =========================================================

    @staticmethod
    def validar_data(data):
        if not data:
            return False

        padrao = re.compile(
            r"^\d{2}/\d{2}/\d{4}"
            r"(?:\s+\d{2}:\d{2})?$"
        )

        return bool(padrao.match(data.strip()))

    # =========================================================
    # CONFIANÇA
    # =========================================================

    @classmethod
    def calcular_confianca(cls, dados):
        """
        Calcula a confiança da extração entre 0 e 1.
        """

        pontos = 0
        total = 0

        # -----------------------------------------------------
        # PROCESSO
        # -----------------------------------------------------

        total += 30

        if cls.validar_processo(
            dados.get("processo", "")
        ):
            pontos += 30

        # -----------------------------------------------------
        # RPV
        # -----------------------------------------------------

        total += 25

        if cls.validar_rpv(
            dados.get("rpv", "")
        ):
            pontos += 25

        # -----------------------------------------------------
        # NOME
        # -----------------------------------------------------

        total += 20

        if cls.validar_nome(
            dados.get("nome", "")
        ):
            pontos += 20

        # -----------------------------------------------------
        # VARA
        # -----------------------------------------------------

        total += 10

        if dados.get("vara"):
            pontos += 10

        # -----------------------------------------------------
        # BANCO
        # -----------------------------------------------------

        total += 5

        if dados.get("banco"):
            pontos += 5

        # -----------------------------------------------------
        # DATA
        # -----------------------------------------------------

        total += 10

        if cls.validar_data(
            dados.get("data_decisao", "")
        ):
            pontos += 10

        # -----------------------------------------------------
        # RESULTADO
        # -----------------------------------------------------

        if total == 0:
            return 0.0

        return round(
            pontos / total,
            2
        )
