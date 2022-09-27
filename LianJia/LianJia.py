"""
利用python爬取链家网二手房数据
1.包括标题，位置，布局，总价，均价
2.可以自定义城市名称来数据获取。
3.实现按指定页数爬取
4.爬取的数据必须存入excel表格，连同代码一块发送。
需求：
1.代码编写方式不限
2.可以使用scrapy或者selenium
3.数据量不少于1000条
4.爬取的数据数目必须准确文章要讲明自己爬取的思路过程，最好配图
https://cs.lianjia.com/
学员提供：
1. 代码(注释)
2. 文章(整洁)
积分：500
"""
import requests
import xlwt
from fake_useragent import FakeUserAgent
from lxml import etree


class LianJia_Spider:
    """爬取链家网任意城市二手房数据"""

    def __init__(self):
        self.cityList_url = "https://www.lianjia.com/city/"  # 选择城市入口url地址
        self.cityUrl = None  # 待爬取城市url
        self.city = None  # 待爬取城市名称
        self.page = 35  # 爬取页数
        self.row = 0  # 总信息数
        self.user_agent = FakeUserAgent().random  # User-Agent 池
        self.headers_ = {'User-Agent': self.user_agent}

    def get_cityList(self):
        """获取所有城市的首页Url"""

        response_ = requests.get(self.cityList_url, headers=self.headers_)
        str_data = response_.content
        html_obj = etree.HTML(str_data)  # 得到一个html对象

        cityName = html_obj.xpath('//ul[@class="city_list_ul"]//li/a/text()')  # 获取所有城市名称列表
        cityUrl = html_obj.xpath('//ul[@class="city_list_ul"]//li/a/@href')  # 获取所有城市对应url列表

        cityList = dict(zip(cityName, cityUrl))

        return cityList

    def get_cityUrl(self):
        """选择需要爬取的城市"""

        cityList = self.get_cityList()
        for i in cityList:
            print(i, cityList[i])
        while not self.cityUrl:
            try:
                self.city = input("请选取上述城市名称之一并输入来获取数据：")
                self.page = int(input("请输入爬取页数：")) + 1
                self.cityUrl = cityList[self.city]
            except Exception as e:
                print("抱歉，该城市信息暂未收录或名称输入错误，请重新输入！")
                continue

    def Go(self):
        """开始运行程序爬取并存入某一城市二手房信息"""

        self.get_cityUrl()

        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet(f'{self.city}二手房信息', cell_overwrite_ok=True)

        col = ("标题", "地址", "简介", "总价", "均价")
        for j in range(len(col)):
            sheet.write(0, j, col[j])  # 构建表头

        for page in range(1, self.page):

            title, position, house, totalPrice, unitPrice = self.pares_page(page)

            for k in range(1, len(title) + 1):  # 一行行写入数据
                sheet.write(k + self.row, 0, title[k - 1])  # 标题
                sheet.write(k + self.row, 1, position[k - 1])  # 位置
                sheet.write(k + self.row, 2, house[k - 1])  # 简介
                sheet.write(k + self.row, 3, totalPrice[k - 1])  # 总价
                sheet.write(k + self.row, 4, unitPrice[k - 1])  # 均价

            self.row += len(title)

        book.save(f'{self.city}二手房信息.xls')

        print(f"\033[1;36m>>\n共{self.row}条{self.city}二手房信息数据下载完毕...\033[0m")

    def pares_page(self, page):
        """解析单页数据"""

        response_ = requests.get(self.cityUrl + f"ershoufang/pg{page}", headers=self.headers_)
        print("正在解析" , self.cityUrl + f"ershoufang/pg{page}")
        str_data = response_.content
        html_obj = etree.HTML(str_data)  # 得到一个html对象

        title = html_obj.xpath('//div[@class="title"]/a/text()')  # 标题

        position1 = html_obj.xpath('//div[@class="positionInfo"]/a[1]/text()')  # 位置1
        position2 = html_obj.xpath('//div[@class="positionInfo"]/a[2]/text()')  # 位置2
        position = []
        for i in range(len(position1)):
            position.append(position1[i] + '-' + position2[i])  # 位置拼接

        house = html_obj.xpath('//div[@class="houseInfo"]/text()')  # 简介

        totalPrice = html_obj.xpath('//div[@class="totalPrice totalPrice2"]/span/text()')  # 总价
        for i in range(len(totalPrice)):
            totalPrice[i] += "万"
        unitPrice = html_obj.xpath('//div[@class="unitPrice"]/span/text()')  # 均价

        for i in range(len(title)):
            print(i + self.row + 1, title[i], position[i], house[i], totalPrice[i], unitPrice[i], '\n')

        return title, position, house, totalPrice, unitPrice


if __name__ == '__main__':
    Spider = LianJia_Spider()
    Spider.Go()
