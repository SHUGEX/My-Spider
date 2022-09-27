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
import re   # 正则提取
from pymysql import connect  # Mysql数据库连接
from selenium import webdriver  # 提取网页源代码
import time
from lxml import etree
from selenium.common.exceptions import TimeoutException
import requests
import os
from fontTools.ttLib import TTFont   # 字体反爬
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
        imagespath = 'woff_img'
        if not os.path.exists(imagespath):
            os.mkdir(imagespath)
        files = os.listdir(imagespath)
        for old in files:
            os.remove(imagespath + "/" + old)  # 删除旧文件
        self.__imgPath = imagespath + '/'

    def get_imagedir(self):
        return self.__imgPath

    def __get_woff(self):
        text = requests.get(self.__url).content
        with open("font.woff", 'wb') as f:
            f.write(text)

    def __woffToImage(self, fmt="png"):
        font = TTFont("font.woff")
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
        self.url = 'https://piaofang.maoyan.com/dashboard'
        self.Success_Num = 0
        pass

    def get_page_sourse(self):
        """创建一个Chrome对象并进入主页"""

        chrome_obj = webdriver.Chrome()

        chrome_obj.maximize_window()

        # 超时等待
        chrome_obj.set_page_load_timeout(6)
        try:
            chrome_obj.get(self.url)
        except TimeoutException:
            print('超时了.....')

        time.sleep(4)

        chrome_obj.save_screenshot('login.png')

        str_data = chrome_obj.page_source

        chrome_obj.quit()  # 结束 关闭 虚拟 Chrome

        html_obj = etree.HTML(str_data)

        return html_obj

    def mysql_obj(self):
        """与MySQL数据库进行连接,创建一个MySQL连接对象"""

        con_obj = connect(host="127.0.0.1", user="root",
                          password="123456", database="my_spider_db", port=3306, charset='utf8mb4')
        print('\033[1;36m>> MySQL 数据库连接成功...\033[0m')

        mysql_cur = con_obj.cursor()  # 创建一个 MySQL 连接对象
        mysql_cur.execute("DROP TABLE IF EXISTS maoyan_piaofang")  # 如果存在student表，则删除
        try:
            mysql_cur.execute("""CREATE TABLE maoyan_piaofang (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              movie_ VARCHAR(100) not null, 
                              score_ VARCHAR(50) not null, 
                              rate_ VARCHAR(50) not null, 
                              num_ VARCHAR(50)  not null
                              )""")
            print('\033[1;36m>> MySQL 数据表创建成功...\033[0m\n')
        except Exception as e:
            print('\033[1;36m>> MySQL 数据表创建失败...\033[0m\n')

        return mysql_cur, con_obj

    def pares_woff(self):
        """字体反爬"""

        font_obj = TTFont('font.woff')
        font_obj.saveXML('font.xml')
        font_ = font_obj.getGlyphOrder()[2:]

        cmap_list = dict()
        for i, k in enumerate(font_):
            key_ = k.replace("uni", "").lower()
            value_ = str(input(f"图片{i + 1}: {key_}-->"))
            cmap_list[value_] = key_
        cmap_list['.'] = '.'

        print('\n\033[1;36m>>校对完毕!\n>>字体加密映射关系表:', cmap_list, "\033[0m\n")
        return cmap_list

    def pares_(self):

        html_obj = self.get_page_sourse()

        # 字体反爬url
        font_url = html_obj.xpath('//style[@id="font-style-sheet"]/text()')[0]
        font_url = "https:" + re.findall('"\),url\("(.*?)"\);}', font_url)[0]

        img = WoffAndImg(font_url)

        path = img.get_imagedir()

        print("\033[1;36m>>请进入", path, "路径校对字体:\033[0m")  # woff_img/

        cmap_list = self.pares_woff()

        movie_ = html_obj.xpath('//div[@class="movielist"]//td/@title')
        pf_ = html_obj.xpath('//div[@class="movielist"]//td[2]/text()')
        zb_ = html_obj.xpath('//div[@class="movielist"]//td[3]/text()')
        cc_ = html_obj.xpath('//div[@class="movielist"]//td[4]/text()')

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

        for i in range(len(movie_)):
            print(f"\033[1;36m>>{i}: 电影《{movie_[i]}》-票房:{piao_f[i]}万-票房占比:{zb_[i]}-排片场次:{cc_[i]}\n\033[0m")

        mysql_cur, con_obj = self.mysql_obj()  # 获取一个 MySQL 连接对象

        mysql_cur, con_obj = self.save_data(movie_, piao_f, zb_, cc_, mysql_cur, con_obj)

        mysql_cur.close()  # 关闭与数据表的连接
        con_obj.close()  # 关闭跟mysql数据库的连接

    def save_data(self, movie_, piao_f, zb_, cc_, mysql_cur, con_obj):
        """存储数据到 Mysql 数据库"""

        for i in range(len(movie_)):
            print(f"\033[1;36m>>{i}: 电影《{movie_[i]}》-票房:{piao_f[i]}万-票房占比:{zb_[i]}-排片场次:{cc_[i]}  已存入数据库!\n\033[0m")

            self.Success_Num += 1  # 下载一条数据 +1
            mysql_cur.execute(
                """insert into maoyan_piaofang(id,movie_, score_, rate_, num_) 
                values(0,"%s","%s","%s","%s")"""
                % (
                    movie_[i],
                    piao_f[i],
                    zb_[i],
                    cc_[i]
                ))
            con_obj.commit()

            print(f"共{self.Success_Num}条票房数据下载成功!")

        return mysql_cur, con_obj


if __name__ == "__main__":
    PF = PiaoFang()
    PF.pares_()
