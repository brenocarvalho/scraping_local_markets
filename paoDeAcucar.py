import scrapy
from re import compile


f_out = open("test.txt", "w")
class PaoDeAcucarSpider(scrapy.Spider):
    name = 'paoAcucar'
    start_urls = ['http://www.paodeacucar.com.br/']
    #pagination_parser = compile("[^?]*(?:\\?([^ ]*)&p=(\\d+)([^ ]*))?")

    def parse(self, response):
        for a in response.css("#nhgpa_submenu_1 a"):
            href = a.css("::attr(href)")[0]            #Selector
            category = a.css("::text")[0].extract() #text
            full_url = response.urljoin(href.extract())
            f_out.write("CATEGORY1:"+category+"\n")
            yield scrapy.Request(full_url, callback=self.parse_category)


    def parse_category(self, response):
        category = response.css(".showcase-header__info h2::text")[0].extract()
        f_out.write("CATEGORY2:"+category+"\n")
        f_out.flush()
        #TODO check if empty
        empty = False
        if empty:
            return
        for product_box in response.css('.boxProduct.showcase-item.content-box'):
            yield PaoDeAcucarSpider.parse_product(category, product_box)

        next_url_select = response.css(".pageSelect.nextPage a::attr(href)")
        if len(next_url_select) > 0:
            next_url = response.urljoin(next_url_select[0].extract())
            yield scrapy.Request(next_url, callback=self.parse_category)

    @classmethod
    def parse_product(self, category, product_box):
        f_out.write("CATEGORY3:"+category)
        f_out.flush()
        try:
            price_select = product_box.css(".showcase-item__price")[-1]
            currency = price_select.css(".currency::text")[0].extract().encode(encoding = "utf-8")
            value    = price_select.css(".value::text")[0].extract().encode(encoding = "utf-8")
        except:
            value = "0"
            currency = "R$"

        return {
            'description': product_box.css("h3.showcase-item__name a::attr(title)").extract()[0].encode(encoding = "utf-8").strip(),
            'price': value,
            'currency': currency,#TODO
            'category': category
        }

    @classmethod
    def getQuantity(self, product_description):
        measures = ["litro", "mililitro", "centimetro", "quilo", "grama"]
        measure_parser = lambda text: compile(".*(\\d+)\\s*((?:litro)|(?:metro)|(?:\\w\\w?)).*").match(text)
        unity_parser   = lambda text: compile(".*(\\d+)\\s*(?:(?:unidade)|(?:pacote)|(?:pct))?.*").match(text.lower())
