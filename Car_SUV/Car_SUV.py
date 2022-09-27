"""
利用Python爬取汽车之家指定数据
1.介绍项目
2.分析网站结构
3.说明技术选择
4.excel表格构建字段
5.Python如何连接excel表格
需求：
1.获取口碑频道SUV紧凑型车全部的数据
2.车名，价格，特点，评分
https://k.autohome.com.cn/#pvareaid=6848948
学员提供：
1. 代码(注释)
2. 文章(说明自己爬取的思路和过程，图文并茂，docx文档)
积分：500
"""
import random
from selenium import webdriver
import time  # 计时
from lxml import etree  # 解析html
from selenium.webdriver.chrome.options import Options  # 无头模式
from selenium.webdriver.common.by import By
import xlwt


class SUV:
    def __init__(self):
        self.Page = 4  # 爬取 新闻页数  15 条新闻/页
        self.Error_Num = 0  # 累计新闻正文下载失败个数
        self.Success_Num = 0  # 累计下载成功的新闻数
        self.url = "https://k.autohome.com.cn/#pvareaid=6848948"
        pass

    def chrome_obj(self):
        """创建一个Chrome对象并进入主页"""

        options_ = Options()  # 设置无界面模式
        options_.add_argument('--headless')
        chrome_obj = webdriver.Chrome(options=options_)  # 无界面模式
        chrome_obj.get(self.url)
        print("\033[1;36m>>已进入目标网址...\033[0m")

        return chrome_obj

    def get_page_source(self, chrome_obj):
        """获取网页源码"""

        item_page = chrome_obj.page_source
        chrome_obj.quit()  # 结束 关闭 虚拟 Chrome
        html_obj = etree.HTML(item_page)

        return html_obj

    def next_page(self, chrome_obj):
        """加载更多数据"""

        print("\033[1;36m>>正在爬取数据...\033[0m")
        for j in range(self.Page):
            for i in range(4):  # 滑动延时 模仿读新闻
                time.sleep(random.randint(0, 1))
                try:  # 捕捉异常，排除因为没有加载进度条而报错的bug
                    chrome_obj.execute_script(
                        f'document.documentElement.scrollTop={(i + 1) * 2000}')
                except Exception as e:
                    continue
            try:
                click_obj = chrome_obj.find_element(By.ID, "sceneGetMore")  # 定位 下页
                click_obj.click()  # 点击
            except Exception as e:
                continue

        return chrome_obj

    def Go(self):
        """开始爬取新闻"""

        chrome_obj = self.chrome_obj()  # 获取一个 Chrome 对象

        chrome_obj = self.next_page(chrome_obj)

        html_obj = self.get_page_source(chrome_obj)

        car_, score_, price_, tags_ = self.parse_(html_obj)

        for i in range(len(car_)):
            print("\033[1;36m" + str(i + 1) + ". 车名:" + car_[i] + " 评分:" + score_[i] + " 价格:" + price_[i] + " 特点:" +
                  tags_[i] + "\033[0m")

        self.save_data(car_, score_, price_, tags_)

    def parse_(self, html_obj):
        """解析新闻列表页面"""

        print("\033[1;36m>>正在解析数据...\033[0m")

        car_ = html_obj.xpath('//li[@class="car-item"]/span[1]/text()')  # # 车名的获取

        score_ = html_obj.xpath('//div[@class="car-star"]/span[3]/text()')  # 评分的获取

        price_ = html_obj.xpath('//span[@class="car-price"]/text()')  # 价格的获取

        tags_1 = html_obj.xpath('//div[@class="car-tags"]/span[1]/text()')  # 评论1的获取
        tags_2 = html_obj.xpath('//div[@class="car-tags"]/span[2]/text()')  # 评论2的获取
        tags_3 = html_obj.xpath('//div[@class="car-tags"]/span[3]/text()')  # 评论3的获取
        tags_4 = html_obj.xpath('//div[@class="car-tags"]/span[4]/text()')  # 评论4的获取
        tags_5 = html_obj.xpath('//div[@class="car-tags"]/span[5]/text()')  # 评论5的获取
        tags_6 = html_obj.xpath('//div[@class="car-tags"]/span[6]/text()')  # 评论6的获取
        tags_ = []
        for i in range(len(tags_1)):
            tags_.append(tags_1[i] + "," + tags_2[i] + "," + tags_3[i] + ","
                         + tags_4[i] + "," + tags_5[i] + "," + tags_6[i])   # 合并6条评论

        print("\033[1;36m>>数据解析完毕...\033[0m")

        return car_, score_, price_, tags_  # 返回Chrome对象和数据列表

    def save_data(self, car_, score_, price_, tags_):
        """存储数据到 Excel 表格"""

        book = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = book.add_sheet('SUV紧凑型车', cell_overwrite_ok=True)

        col = ("车名", "评分", "价格", "特点")

        for j in range(len(col)):
            sheet.write(0, j, col[j])  # 构建表头

            for i in range(1, len(car_) + 1):  # 一列一列写入数据
                sheet.write(i, 0, car_[i - 1])  # 车名
                sheet.write(i, 1, score_[i - 1])  # 评分
                sheet.write(i, 2, price_[i - 1])  # 价格
                sheet.write(i, 3, tags_[i - 1])  # 特点

        book.save('SUV紧凑型车.xls')
        print("\033[1;36m>>数据下载完毕...\033[0m")


if __name__ == '__main__':
    Spider = SUV()
    Spider.Go()
