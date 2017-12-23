# -*- coding: utf-8 -*-
import scrapy

from portais.tools.text import normalize_string, maiorTextoFromList
from .steps import consulta


class VivarealSpider(scrapy.Spider):
    name = 'vivareal'
    allowed_domains = ['www.vivareal.com.br']
    initial_step = consulta.consultar_portal
    required_args = ['cidade']
    optional_args = ['tipo_consulta', 'estado']
    start_urls = ['https://www.vivareal.com.br/venda/pernambuco/recife/apartamento_residencial/']
    pagina = 1

    def parse(self, response):
        imoveis = response.xpath('//article[contains(@class, "property-card")]')
        paginacao = response.xpath('//nav[contains(@class, "pagination")]')
        if not paginacao:
            return
        else:
            self.pagina += 1
            for imovel in imoveis:
                url = imovel.xpath('.//h2/a/@href').extract_first()
                url = response.urljoin(url)
                yield scrapy.Request(url=url, callback=self.detalhe_imovel)
            url_proxima_pag = self.start_urls[0] + '?pagina={}'.format(self.pagina)
            yield scrapy.Request(url=url_proxima_pag, callback=self.parse)

    def detalhe_imovel(self, response):
        _base_xpath = ('//div[@class="tV"]{}').format
        titulo = response.xpath(
            _base_xpath('//h1//span[contains(@class, "title-main")]//text()')
        ).extract_first()
        id_ = response.xpath(
            _base_xpath('//h1//span[contains(@class, "title-code")]//text()')
        ).extract_first()
        endereco = response.xpath(
            _base_xpath('//h1//a[contains(@class, "title-location")]//text()')
        ).extract_first()

        links_imagens = response.css('.tA .tC .bk li')
        lista_link_imagens = []
        for imagem in links_imagens:
            link_imagem = imagem.xpath('.//@src').extract_first()
            lista_link_imagens.append(link_imagem)

        item = {
            'id_': id_,
            'imagens': lista_link_imagens,
            'titulo': titulo,
            'endereco': endereco
        }

        dict_infos = {}
        infos = response.css('ul.bx li.by')
        contador = 0
        for idx, info in enumerate(infos):
            if idx == 0:
                # valor do imóvel
                lista = info.xpath(
                    './/span[contains(@class, "b")]//text()').extract()
                lista_chaves = ['_'.join(normalize_string(chave.lower()).split(' ')) for chave in lista[::2]]
                lista_valores = [valor for valor in lista[1::2]]
                infos_valores = dict(zip(lista_chaves, lista_valores))
                item.update(**infos_valores)
            else:
                contador += 1
                lista_chave_valor = info.xpath('.//span//text()').extract()
                if contador <= 2:
                    chave = normalize_string(lista_chave_valor[0].lower())
                    chave = '_'.join(chave.split(' '))
                    valor = ' '.join(lista_chave_valor[1::])
                else:
                    valor = ' '.join(lista_chave_valor)
                    if contador == 3:
                        chave = 'quartos'
                    elif contador == 4:
                        chave = 'banheiros'
                    elif contador == 5:
                        chave = 'vagas'
                dict_infos[chave] = valor

        _xpath_base_add = ('//section[contains(@class, '
                           '"description-and-features")]{}').format
        dict_infos_adicionais = {
            'descricao': {
                'titulo': response.xpath(
                    _xpath_base_add('//h2//text()')).extract_first(),
                'texto': '. '.join(
                    response.xpath(_xpath_base_add('//div//p//text()')).extract())  # noqa
            },
            'caracteristicas': response.xpath(
                _xpath_base_add('//div//ul//li//text()')).extract()
        }

        item.update(**dict_infos)
        item.update(**dict_infos_adicionais)

        yield item
