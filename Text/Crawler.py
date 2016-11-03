from scrapy.http import HtmlResponse
from scrapy.selector import Selector

response = HtmlResponse("http://www3.nhk.or.jp/news/easy/k10010747251000/k10010747251000.html")
print Selector(response).xpath('//div[@id="newstitle"]')

print response.css('body')
#s = response.xpath('//body')
s = response.selector.xpath('//div[@id="newstitle"]')#.extract_first()
print s