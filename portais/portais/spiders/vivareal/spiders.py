# -*- coding: utf-8 -*-
import scrapy

from .steps import consulta


class VivarealSpider(scrapy.Spider):
    name = 'vivareal'
    allowed_domains = ['www.vivareal.com.br']
    initial_step = consulta.consultar_portal
    required_args = ['cidade']
    optional_args = ['tipo_consulta', 'estado']
    start_urls = ['https://www.vivareal.com.br/venda/pernambuco/recife/apartamento_residencial/']

    def parse(self, response):
        imoveis = response.xpath('//article[contains(@class, "property-card")]')
        for imovel in imoveis:
            url = imovel.xpath('.//h2/a/@href').extract_first()
            url = response.urljoin(url)
            yield scrapy.Request(url=url, callback=self.detalhe_imovel)

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
        item = {
            'id_': id_,
            'titulo': titulo,
            'endereco': endereco
        }
        response.meta['item'] = item
        yield item
        # yield self.infos

    def infos(self, response):
        item = response.meta['item']
        import ipdb; ipdb.set_trace()