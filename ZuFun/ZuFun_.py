"""
利用Python爬虫爬取租房网深圳前5页的房源数据：
1.爬取楼盘信息，租金，面积大小，房源描述等
2.分析网站的结构
3.使用scrapy实现
4.excel表格构建字段
5.Python如何连接excel表格
需求：
1.存入到excel表格中
2.爬取楼盘信息，租金，大小，类型等
https://sz.zufun.cn/
学员提供：
1. 代码(注释)
2. 文章(整洁)
积分：500
"""
import requests
import xlwt
from fake_useragent import FakeUserAgent
from lxml import etree


class ZuFun:

    def __init__(self):
        self.page = 1  # 当前页数
        self.url = f"https://sz.zufun.cn/zufang-list/page{self.page}/"  # 第page页
        self.user_agent = FakeUserAgent().random  # User-Agent 池
        self.headers_ = {'User-Agent': self.user_agent}
        self.row = 0  # 总信息数

    def Go(self):

        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet('租房网深圳房源数据', cell_overwrite_ok=True)

        col = ("楼盘", "地址", "底价(元/月起)", "出租房源(套)", "租房信息")
        for j in range(len(col)):
            sheet.write(0, j, col[j])  # 构建表头

        for i in range(5):

            title, addr, price, num, Info = self.pares_page()

            for k in range(1, len(title) + 1):  # 一行行写入数据
                sheet.write(k + self.row, 0, title[k - 1])  # 楼盘
                sheet.write(k + self.row, 1, addr[k - 1])  # 地址
                sheet.write(k + self.row, 2, price[k - 1])  # 底价
                sheet.write(k + self.row, 3, num[k - 1])  # 租房个数
                sheet.write(k + self.row, 4, Info[k - 1])  # 租房信息

            self.row += len(title)
            self.page += 1

        book.save('租房网深圳房源数据.xls')

        print(f"\033[1;36m>>租房网深圳房源数据下载完毕...\033[0m")

    def pares_page(self):
        """解析单页数据"""
        response_ = requests.get(self.url, headers=self.headers_)
        str_data = response_.content
        html_obj = etree.HTML(str_data)  # 得到一个html对象

        title = html_obj.xpath('//div[@class="title-wrap"]/a/text()')  # 获取楼盘名
        addr_1 = html_obj.xpath('//p[@class="ppt-addr"]/a[1]/text()')  # 获取楼盘地址前段
        addr_2 = html_obj.xpath('//p[@class="ppt-addr"]/a[2]/text()')  # 获取楼盘地址后段
        addr = []
        for j in range(10):
            addr.append(str(addr_1[j]) + '-' + str(addr_2[j]))

        price = html_obj.xpath('//p[@class="price"]/span/text()')  # 获取低价

        num = html_obj.xpath('//p[@class="num"]/span/text()')  # 获取租房个数

        Info = []
        for j in range(1, 11):

            room = html_obj.xpath(f'//div[@class="building-item"][{j}]//a/ul/li[1]/text()')
            area = html_obj.xpath(f'//div[@class="building-item"][{j}]//a/ul/li[2]/text()')
            floor = html_obj.xpath(f'//div[@class="building-item"][{j}]//a/ul/li[3]/text()')
            r_price = html_obj.xpath(f'//div[@class="building-item"][{j}]//a/ul/li[4]/span/text()')
            for r in range(len(r_price)):
                r_price[r] += "元/月"

            info_ = []
            for j in range(len(room)):
                info_.append(room[j] + " " + area[j] + " " + floor[j] + " " + r_price[j])

            info = ""
            for j in range(len(info_)):
                info += " | " + info_[j]

            Info.append(info)

        return title, addr, price, num, Info


if __name__ == '__main__':
    Spider = ZuFun()
    Spider.Go()
