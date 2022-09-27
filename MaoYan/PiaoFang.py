"""
# 利用python爬取猫眼电影今日票房数据
1.类比起点网，分析两个网站字体反爬的异同（写入文章即可）
2.学会如何使用第三方库去处理字体加密文件
3.该任务主要涉及到字体反爬
学员提供：
1.代码(注释)
2.文章(整洁)
学员提供：
1.代码(注释)
2.文章(整洁)
爬取地址：https://www.maoyan.com/
积分：700
"""
import re

import requests
from fontTools.ttLib import TTFont
from selenium import webdriver
import time
from lxml import etree
from selenium.common.exceptions import TimeoutException
import requests
import os
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing


class ReportLabPen(BasePen):
    """A pen for drawing onto a reportlab.graphics.shapes.Path object."""

    def __init__(self, glyphSet, path=None):
        BasePen.__init__(self, glyphSet)
        if path is None:
            path = Path()
        self.path = path

    def _moveTo(self, p):
        (x, y) = p
        self.path.moveTo(x, y)

    def _lineTo(self, p):
        (x, y) = p
        self.path.lineTo(x, y)

    def _curveToOne(self, p1, p2, p3):
        (x1, y1) = p1
        (x2, y2) = p2
        (x3, y3) = p3
        self.path.curveTo(x1, y1, x2, y2, x3, y3)

    def _closePath(self):
        self.path.closePath()


class WoffAndImg:

    def __init__(self, url):
        self.__url = url
        self.__create_path()
        self.__get_woff()
        self.__woffToImage()

    def __create_path(self):
        name = self.__url.split('/')[-1]
        filedir = 'woff_img/' + name.replace('.woff', '')
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        self.__woffPath = filedir + '/' + name
        imagespath = filedir + '/images'
        if not os.path.exists(imagespath):
            os.mkdir(imagespath)
        self.__imgPath = imagespath + '/'

    def get_imagedir(self):
        return self.__imgPath

    def __get_woff(self):
        text = requests.get(self.__url).content
        with open(self.__woffPath, 'wb') as f:
            f.write(text)
            f.close()

    def __woffToImage(self, fmt="png"):
        font = TTFont(self.__woffPath)
        gs = font.getGlyphSet()
        glyphNames = font.getGlyphNames()
        glyphNames.remove('glyph00000')
        glyphNames.remove('x')

        for i in glyphNames:
            if i[0] == '.':  # 跳过'.notdef', '.null'
                continue

            g = gs[i]
            pen = ReportLabPen(gs, Path(fillColor=colors.black, strokeWidth=1))
            g.draw(pen)
            w, h = g.width, g.width
            g = Group(pen.path)
            g.translate(w, h * 1.5)

            d = Drawing(w * 3, h * 4.5)
            d.add(g)
            imageFile = self.__imgPath + "/" + i.replace("uni", "").lower() + ".png"
            renderPM.drawToFile(d, imageFile, fmt)


class PiaoFang:

    def __init__(self):
        pass

    def response_(self):

        # Chrome 对象
        chrome_obj = webdriver.Chrome()

        chrome_obj.maximize_window()

        # 超时等待
        chrome_obj.set_page_load_timeout(5)
        try:
            chrome_obj.get('https://piaofang.maoyan.com/dashboard')
        except TimeoutException:
            print('超时了.....')

        time.sleep(4)

        chrome_obj.save_screenshot('login.png')

        str_data = chrome_obj.page_source

        with open("paiofang.html", 'w', encoding="utf-8") as f:
            f.write(str_data)

        # 格式化
        html_obj = etree.HTML(str_data)

        # 字体反爬url
        font_url = html_obj.xpath('//style[@id="font-style-sheet"]/text()')[0]
        font_url = "https:" + re.findall('"\),url\("(.*?)"\);}', font_url)[0]

        print("font_url:", font_url)

        response_font = requests.get(font_url)
        with open('new_1.woff', 'wb') as f:  # @@@@@@@@@@@@@@@@@@@@@@@@@@@
            f.write(response_font.content)

        font_obj = TTFont('new_1.woff')
        font_obj.saveXML('new_1.xml')
        font_ = font_obj.getGlyphOrder()[2:]
        cmap_list = dict()

        img = WoffAndImg(font_url)
        print("请进入下面路径校对字体", img.get_imagedir())  # woff_img/227e3c01/images/

        for i, k in enumerate(font_):
            key_ = k.replace("uni", "").lower()
            value_ = str(input(f"{key_}-->"))
            cmap_list[str(i)] = key_
        cmap_list['.'] = '.'

        print('\n字体加密映射关系表:', cmap_list, "\n")

        movie_ = html_obj.xpath('//div[@class="movielist"]//td/@title')
        pf_ = html_obj.xpath('//div[@class="movielist"]//td[2]/text()')
        list_ = []
        for i, u in enumerate(pf_):
            list_.append(u.replace("万", ""))

        piao_f = []
        for i in range(len(list_)):
            piao = ''
            for j in list_[i]:
                n = j.encode('raw_unicode_escape').decode('utf-8').replace("\\u", "")
                for k in cmap_list:
                    if cmap_list[k] == n:
                        piao += k
            piao_f.append(piao)

        zb_ = html_obj.xpath('//div[@class="movielist"]//td[3]/text()')
        cc_ = html_obj.xpath('//div[@class="movielist"]//td[4]/text()')

        for i in range(len(movie_)):
            print(f"\033[1;36m>>{i}: 电影《{movie_[i]}》-票房:{piao_f[i]}万-票房占比:{zb_[i]}-排片场次:{cc_[i]}\n\033[0m")


if __name__ == "__main__":
    PF = PiaoFang()
    PF.response_()
