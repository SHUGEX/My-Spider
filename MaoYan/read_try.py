import re

import requests
from fontTools.ttLib import TTFont
from lxml import etree

with open("paiofang.html", 'r', encoding="utf-8") as f:
    str_data = f.read()

print(str_data)

html_obj = etree.HTML(str_data)
font_url = html_obj.xpath('//style[@id="font-style-sheet"]/text()')[0]
font_url = "https:" + re.findall('"\),url\("(.*?)"\);}', font_url)[0]

response_font = requests.get(font_url)
with open('font.woff', 'wb') as f:
    f.write(response_font.content)


# font_obj = TTFont('font.woff')
font_obj = TTFont('0e44556e.eot')
font_obj.saveXML('font.xml')

# font_ = font_obj.getGlyphOrder()
font_ = font_obj.getBestCmap()
print('\n字体加密:', font_, "\n")

cmap_list = {}
for i, k in enumerate(font_):
    cmap_list[str(i)] = k.replace("uni", "").lower()
cmap_list['.'] = '.'

print('\n字体加密映射关系表:', cmap_list, "\n")

movie_ = html_obj.xpath('//div[@class="movielist"]//td/@title')
pf_ = html_obj.xpath('//div[@class="movielist"]//td[2]/text()')

zb_ = html_obj.xpath('//div[@class="movielist"]//td[3]/text()')
cc_ = html_obj.xpath('//div[@class="movielist"]//td[4]/text()')
print("\n", "\n", movie_, "\n", pf_, "\n", zb_, "\n", cc_)
