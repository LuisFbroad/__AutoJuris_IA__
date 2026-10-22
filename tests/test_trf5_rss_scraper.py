import unittest
from scrapers.trf5_rss_scraper import parsear_rss_trf5, TRF5RSSParseError

XML_EXEMPLO = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title>Processo 0569496-72.2026.4.05.0000</title>
    <link>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000</link>
    <description>Acompanhamento do processo Nº 0569496-72.2026.4.05.0000&lt;br/&gt;REQUISIÇAO DE PEQUENO VALOR (RPV4453170-CE (@))&lt;br/&gt; REQTE: WESKLEY SOUZA DOS SANTOS&lt;br/&gt;Advogado/Procurador: ALAN SOUZA ARRUDA&lt;br/&gt;Escritório Advocatício: GERBASE, ARRUDA GAZZANEO E COUTINHO ADVOGADOS ASSOCIADOS&lt;br/&gt;REQDO: UFC - UNIVERSIDADE FEDERAL DO CEARÁ&lt;br/&gt;</description>
    <pubDate>Mon, 19 Oct 2026 16:27:25 -0300</pubDate>
    <lastBuildDate>Mon, 19 Oct 2026 16:29:25 -0300</lastBuildDate>
    <item>
      <title>Concluso para decisão a(o) Diretoria de Precatórios (Seção de RPV) para / por Secretaria Processante</title>
      <link>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_2</link>
      <description/>
      <pubDate>Mon, 19 Oct 2026 16:29:25 -0300</pubDate>
      <guid>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_2</guid>
    </item>
    <item>
      <title>Registro ao Desembargador(a) Federal Presidente</title>
      <link>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_1</link>
      <description>(M949)</description>
      <pubDate>Mon, 19 Oct 2026 16:28:25 -0300</pubDate>
      <guid>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_1</guid>
    </item>
    <item>
      <title>Individualização e Validação automatica de requisitos obrigatórios realizadas com sucesso - Requisição incluída na lista de ordem cronológica - Acompanhar tramitação pelo portal: http://rpvprecatorio.trf5.jus.br/. - Incluída em proposta - pagto em processamento - depósito previsto para o final do próximo mês - Acompanhar a tramitação e a data de liberação pelo portal: http://rpvprecatorio.trf5.jus.br/.</title>
      <link>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_0</link>
      <description>(M949)</description>
      <pubDate>Mon, 19 Oct 2026 16:27:25 -0300</pubDate>
      <guid>http://portal.trf5.jus.br/processo/0569496-72.2026.4.05.0000#mov_0</guid>
    </item>
  </channel>
</rss>
"""


class TestTRF5RSS(unittest.TestCase):
    def test_extrai_dados_da_capa_e_movimentacoes(self):
        processo = parsear_rss_trf5(XML_EXEMPLO)

        self.assertEqual(processo.numero_processo, "0569496-72.2026.4.05.0000")
        self.assertEqual(processo.numero_rpv, "RPV4453170-CE")
        self.assertEqual(processo.requerente, "WESKLEY SOUZA DOS SANTOS")
        self.assertEqual(processo.requerido, "UFC - UNIVERSIDADE FEDERAL DO CEARÁ")
        self.assertEqual(processo.advogado, "ALAN SOUZA ARRUDA")
        self.assertEqual(len(processo.movimentacoes), 3)
        self.assertIn("Diretoria de Precatórios", processo.movimentacoes[0].titulo)
        self.assertTrue(processo.movimentacoes[0].link.endswith("#mov_2"))
        self.assertEqual(
            processo.movimentacoes[0].data_publicacao.strftime("%Y-%m-%d"), "2026-10-19"
        )

    def test_xml_invalido_gera_erro_claro(self):
        with self.assertRaises(TRF5RSSParseError):
            parsear_rss_trf5("<rss><channel>")

    def test_xml_sem_numero_processo_gera_erro(self):
        xml = "<rss><channel><title>Processo sem número</title><link>http://exemplo.test</link></channel></rss>"
        with self.assertRaises(TRF5RSSParseError):
            parsear_rss_trf5(xml)


if __name__ == "__main__":
    unittest.main()
