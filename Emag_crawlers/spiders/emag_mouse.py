import scrapy
import re
from ..items import MouseItem

class EmagMouseSpider(scrapy.Spider):
    name = 'emag_mouse'
    allowed_domains = ['emag.ro']
    start_urls = [
        'https://www.emag.ro/mouse/filter/tip-f7857,gaming-v-12266988/pret,intre-8-si-600/c'
    ]

    def parse(self, response):
        mice = response.css('div.card-item.js-product-data')
        
        for mouse in mice:
            name = mouse.css('a.card-v2-title::text').get()
            url = mouse.css('a.card-v2-title::attr(href)').get()

            main_price = mouse.css('p.product-new-price::text').get()
            decimal_price = mouse.css('p.product-new-price sup::text').get()

            if main_price and decimal_price:
                main_price_clean = ''.join(filter(str.isdigit, main_price))
                decimal_price_clean = ''.join(filter(str.isdigit, decimal_price))
                try:
                    price = float(f"{main_price_clean}.{decimal_price_clean}")
                except ValueError:
                    price = None
            else:
                price = None

            if url:
                yield response.follow(url, callback=self.parse_mouse_page, meta={
                    'name': name.strip() if name else None,
                    'price': price,
                    'url': response.urljoin(url)
                })

        next_page = response.css('a.js-change-page[aria-label="Next"]::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def extract_brand_from_product_page(self, response): 
        brand = response.css("div.disclaimer-section p a::text").get()
        if brand and brand.strip():
            return brand.strip()
        
    def parse_mouse_page(self, response):
        in_stock = response.css('span.label-in_stock')
        out_of_stock = response.css('span.label-out_of_stock')
        
        if out_of_stock:
            return
        
        item = MouseItem()
        item['name'] = response.meta.get('name')
        item['URL'] = response.meta.get('url')
        item['price'] = response.meta.get('price')
        
        # Extract brand from product page
        item['brand'] = self.extract_brand_from_product_page(response)
        
        # If still no brand, try extracting from product name
        if not item['brand']:
            page_name = response.css('h1.page-title::text').get() or response.css('h1::text').get()
            if page_name:
                item['brand'] = self.extract_brand_from_name(page_name)
            elif item['name']:
                item['brand'] = self.extract_brand_from_name(item['name'])

        # Clean specification extraction function
        def clean_info(xpath_expr):
            text = response.xpath(xpath_expr).get()
            return text.strip() if text else None
        
        # Extract specifications
        item['tip'] = clean_info("//tr[td[contains(text(), 'Tip')]]/td[2]/text()")
        item['interfata_mouse'] = clean_info("//tr[td[contains(text(), 'Interfata mouse')]]/td[2]/text()")
        item['interfata_receiver'] = clean_info("//tr[td[contains(text(), 'Interfata receiver')]]/td[2]/text()")
        item['tehnologie'] = clean_info("//tr[td[contains(text(), 'Tehnologie')]]/td[2]/text()")
        item['culoare'] = clean_info("//tr[td[contains(text(), 'Culoare')]]/td[2]/text()")

        yield item