"""
爬取中机昌盛商城，以型号，品牌或货位仓码为查询条件(例如GP)来获取结果页面的商品数据。要求如下(2和4选择其一实现即可，选择第四项可加分)：
1.需要获取的数据有商品、产地、库存、发货地、发货仓
2.搜索结果的每一页数据都要爬取，至少要有20个品牌(20个搜索结果)的数据量，或者五大地区的搜索结果页面数据。
3.可任意选择爬虫框架，但使用selenium扣300分。
4.做成动态搜索程序，即由用户选择搜索的内容(当用户输入GP时，返回GP搜索页的数据，其它同理)，并给出提示，而不是代码固定搜索的内容。
5.数据存储于MongoDB或MySQL中。
6.提交的文章需要有环境分析、页面分析与代码分析，否则相应扣分，文章内容要满足初学者小白可阅读，优秀文章加分
学员提供：
1. 代码(注释)
2. 文章(代码实现)  文章要整洁，要讲明自己爬取的思路过程，最好配图
3. 文档(整洁)      描述自身使用的环境分析、网站页面分析与代码分析
4. 数据库备份文件
5.视频文件
如果有云数据库或者云服务器的，提交数据时可直接提供可访问的服务器IP
https://www.zjshop.com.cn
功能完美加分：150
文章完美加分：150
积分：1000
"""
import requests
from fake_useragent import FakeUserAgent
from lxml import etree
from pymysql import connect  # Mysql数据库连接


class ZJshop:

    def __init__(self, wd):
        self.wd = wd
        self.page = 1  # 当前页数
        self.Success_Num = 0  # 下载成功的信息条数
        self.url = f"https://www.zjshop.com.cn/products?pbrandName={self.wd}&page={self.page}"  # 首页
        self.user_agent = FakeUserAgent().random  # User-Agent 池
        self.headers_ = {'User-Agent': self.user_agent}
        self.row = 0  # 总信息数

    def mysql_obj(self):
        """与MySQL数据库进行连接,创建一个MySQL连接对象"""

        con_obj = connect(host="127.0.0.1", user="root",
                          password="123456", database="spider_zjshop",
                          port=3306, charset='utf8mb4')
        print('\033[1;36m>> MySQL 数据库连接成功...\033[0m')
        mysql_cur = con_obj.cursor()  # 创建一个 MySQL 连接对象

        mysql_cur.execute("DROP TABLE IF EXISTS zjshop")  # 如果存在zjshop表，则删除

        # 自动创建zjshop的数据表格，只需要提前创建一个数据库即可

        mysql_cur.execute("""CREATE TABLE zjshop (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          title VARCHAR(500) not null, 
                          house VARCHAR(50) not null, 
                          add1 VARCHAR(50) not null, 
                          add2 VARCHAR(50)  not null,
                          pack VARCHAR(50)  not null,
                          num VARCHAR(50)  not null
                          )""")
        print('\033[1;36m>> MySQL 数据表创建成功...\033[0m')

        return mysql_cur, con_obj

    def get_page(self):

        response_ = requests.get(self.url, headers=self.headers_)
        str_data = response_.text
        html_obj = etree.HTML(str_data)  # 得到一个html对象

        page_ = html_obj.xpath('//ul[@class="pagination"]/li[last()]/a/@href')[0]  # 获取末页Url
        page_ = int(''.join(filter(str.isdigit, page_)))  # 获取末页Url中的页数，只提取数字

        return page_

    def Go(self):

        mysql_cur, con_obj = self.mysql_obj()  # 获取一个 MySQL 连接对象
        page = self.get_page()
        print(f"\033[1;36m>> 中机昌盛商城商品{self.wd}共{page}页解析中...\033[0m")

        for i in range(page):
            title, house, add1, add2, pack, num = self.pares_page()
            mysql_cur, con_obj = \
                self.save_data(title, house, add1, add2, pack, num, mysql_cur, con_obj)

            print(f"\033[1;36m>> 第{self.page}页商品数据下载完毕...\033[0m")
            self.page += 1

        print(f"\033[1;36m>> 中机昌盛商城共{self.Success_Num}条商品数据下载完毕...\033[0m")

        mysql_cur.close()  # 关闭与数据表的连接
        con_obj.close()  # 关闭跟mysql数据库的连接

    def pares_page(self):
        """解析单页数据"""
        response_ = requests.get(self.url, headers=self.headers_)
        str_data = response_.text
        html_obj = etree.HTML(str_data)  # 得到一个html对象

        title_ = html_obj.xpath('//span[@class="mar_lef"]//text()')  # 获取商品名
        for t in range(len(title_)):  # 清洗数据，去除换行符、空格、空字符
            title_[t] = title_[t] \
                .replace("\n", "") \
                .replace(" ", "") \
                .strip()
        title = []
        for t in range(int(len(title_) / 3)):
            t_num = t * 3  # 将数据3个3个拼接在一起
            title.append(title_[t_num] + " "
                         + title_[t_num + 1] + " "
                         + title_[t_num + 2])

        house = html_obj.xpath('//td[2]//span/text()')  # 获取发货仓
        add1 = html_obj.xpath('//td[3]//span/text()')  # 获取发货地

        add2 = []  # 获取产地
        for a in range(1, len(title) + 1):
            add_ = html_obj.xpath(f'//tr[{a}]/td[4]/div/text()')  # 获取产地
            if len(add_) == 0:
                add2.append("无")  # 添加无地址信息
            else:
                add2.append(add_[0])

        pack = []  # 获取包装
        for p in range(1, len(title) + 1):
            pack_ = html_obj.xpath(f'//tr[{p}]/td[5]/div/text()')  # 获取包装
            if len(pack_) == 0:
                pack.append("无")  # 添加无地址信息
            else:
                pack.append(pack_[0])

        num = html_obj.xpath('//td[6]//span/text()')  # 获取库存

        return title, house, add1, add2, pack, num

    def save_data(self, title, house, add1, add2, pack, num, mysql_cur, con_obj):
        """存储数据到 Mysql 数据库"""

        for i in range(len(title)):
            print(f"商品{i}: 商品:{title[i]} | 发货仓:{house[i]} | 发货地:{add1[i]}"
                  f" | 产地:{add2[i]} | 包装:{pack[i]} | 库存:{num[i]}  已存入数据库!")

            self.Success_Num += 1  # 下载一条数据 +1
            mysql_cur.execute(
                """insert into zjshop(id,title,house,add1,add2,pack,num) 
                values(0,"%s","%s","%s","%s","%s","%s")"""
                % (
                    title[i],
                    house[i],
                    add1[i],
                    add2[i],
                    pack[i],
                    num[i]
                ))
            con_obj.commit()

        return mysql_cur, con_obj


if __name__ == '__main__':
    wd = input("请输入搜索的内容：")
    Spider = ZJshop(wd)
    Spider.Go()
