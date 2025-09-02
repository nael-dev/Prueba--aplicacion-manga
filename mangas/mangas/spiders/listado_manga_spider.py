import scrapy
from urllib.parse import urljoin

class ListadoMangaPerfectoSpider(scrapy.Spider):
    name = "ListadoManga_scrapy"
    allowed_domains = ["listadomanga.es"]
    start_urls = ["https://www.listadomanga.es/lista.php"]

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "FEED_EXPORT_ENCODING": "utf-8",
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY": 1.5
    }

    def parse(self, response):
        for manga in response.xpath('//a[contains(@href, "coleccion.php")]'):
            yield response.follow(
                manga.xpath('@href').get(),
                callback=self.parse_detalle,
                meta={'titulo': manga.xpath('normalize-space(text())').get()}
            )

        next_page = response.xpath('//a[.//text()[contains(., "Siguiente")]]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_detalle(self, response):
        item = {
            'titulo': response.meta['titulo'],
            'url': response.url,
            'imagen': self.get_imagen(response),
            'sinopsis': self.get_sinopsis(response),
            'tomos': self.get_tomos_detalle(response)
        }

        td_izq = response.xpath('//td[@class="izq"]')[0]
        etiquetas = td_izq.xpath('.//b')

        for etiqueta in etiquetas:
            label = etiqueta.xpath('normalize-space(text())').get()
            valor = ''

            siblings_text = etiqueta.xpath('following-sibling::text()[1]').get()
            if siblings_text:
                valor = siblings_text.strip()

            a_text = etiqueta.xpath('following-sibling::*[1][self::a]/text()').get()
            if a_text:
                valor = a_text.strip()

            if label == 'Título original:':
                item['titulo_original'] = valor
            elif label == 'Guion:':
                item['guion'] = valor
            elif label == 'Dibujo:':
                item['dibujo'] = valor
            elif label == 'Traducción:':
                item['traduccion'] = valor
            elif label == 'Editorial japonesa:':
                item['editorial_japonesa'] = valor
            elif label == 'Editorial española:':
                item['editorial_espanola'] = valor
            elif label == 'Colección:':
                item['coleccion'] = valor
            elif label == 'Formato:':
                item['formato'] = valor
            elif label == 'Sentido de lectura:':
                item['sentido_lectura'] = valor
            elif label == 'Números en japonés:':
                item['tomos_japones'] = valor
            elif label == 'Números en castellano:':
                item['tomos_espanol'] = valor

        yield item

    def get_imagen(self, response):
        img = response.xpath('//td[contains(@class, "cen")]//img[contains(@class, "portada")]/@src').get()
        return urljoin(response.url, img) if img else None

    def get_sinopsis(self, response):
        sinopsis = response.xpath('//div[@id="sinopsis"]//text()').getall()
        if not sinopsis:
            sinopsis = response.xpath('//td[hr]/text() | //td[hr]//p//text()').getall()
        return ' '.join([t.strip() for t in sinopsis if t.strip()])

    def get_tomos_detalle(self, response):
        tomos = []
        for tomo_sel in response.xpath('//table[contains(@class,"ventana_id1")]'):
            portada = tomo_sel.xpath('.//img[contains(@class,"portada")]/@src').get()
            texto = tomo_sel.xpath('.//td[contains(@class,"cen")]//text()').getall()
            texto_limpio = [t.strip() for t in texto if t.strip()]

            numero = ''
            for t in texto_limpio:
                if 'nº' in t:
                    numero = t
                    break

            tomos.append({
                'numero': numero,
                'portada': urljoin(response.url, portada) if portada else None,
                'detalles': texto_limpio
            })
        return tomos
