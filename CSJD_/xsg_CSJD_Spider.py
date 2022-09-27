import random
from selenium import webdriver
import time  # 计时
from pymysql import *  # MySQL数据库
from lxml import etree  # 解析html
from selenium.webdriver.chrome.options import Options  # 无头模式
from selenium.common.exceptions import TimeoutException  # 页面加载等待的异常处理
from selenium.webdriver.common.by import By


class CSJD:
    def __init__(self, Page):
        self.Page = Page  # 爬取 新闻页数  15 条新闻/页
        self.Error_Num = 0  # 累计新闻正文下载失败个数
        self.Success_Num = 0  # 累计下载成功的新闻数
        pass

    def chrome_obj(self):
        """创建一个Chrome对象并进入主页"""

        options = webdriver.ChromeOptions()
        options.add_argument(f"--proxy-server=http://115.239.102.149:4214")  # 使用代理
        options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_argument('--start-maximized')
        options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 手动指定使用的浏览器位置
        options.add_argument('disable-infobars')
        options.add_argument("--disable-blink-features=AutomationControlled")

        # xsg_options_ = Options()  # 设置无界面模式
        # xsg_options_.add_argument('--headless')
        chrome_obj = webdriver.Chrome(options=options)  # 无界面模式

        chrome_obj.maximize_window()

        chrome_obj.get(
            'https://hotel.fliggy.com/hotel_list3.htm?_input_charset=utf-8&cityName=%E9%95%BF%E6%B2%99%E5%B8%82&city=430100&keywords=&checkIn=2022-08-04&checkOut=2022-08-05&ttid=seo.000000574&_output_charset=utf8')

        print('\033[1;36m\n> 已进入目标网址...\033[0m')
        print('\033[1;36m\n> 登陆完成后按Enter键继续 ...\033[0m')
        login_ = input()
        item_page = chrome_obj.page_source

        html_obj = etree.HTML(item_page)

        warn_list = html_obj.xpath('//div[@class="warnning-text"]/text()')

        if len(warn_list) > 0:
            click_obj = chrome_obj.find_element(By.ID, "nc_1_n1z")  # 定位滑块按钮
            chrome_obj, html_obj = self.slide_block(chrome_obj, click_obj)

        return chrome_obj

    def mysql_obj(self):
        """与MySQL数据库进行连接,创建一个MySQL连接对象"""

        con_obj = connect(host="127.0.0.1", user="root",
                          password="123456", database="my_spider_db", port=3306, charset='utf8mb4')
        print('\033[1;36m>> MySQL 数据库连接成功...\033[0m')

        mysql_cur = con_obj.cursor()  # 创建一个 MySQL 连接对象
        mysql_cur.execute("DROP TABLE IF EXISTS csjd_tb")  # 如果存在student表，则删除
        try:
            mysql_cur.execute("""CREATE TABLE csjd_tb (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              hotel_ VARCHAR(255) not null, 
                              score_ VARCHAR(50) not null, 
                              num_ VARCHAR(50) not null, 
                              commentator_ VARCHAR(50)  not null,
                              data_ VARCHAR(50)  not null,
                              clear_ VARCHAR(50)  not null,
                              local_ VARCHAR(50)  not null,
                              server_ VARCHAR(50)  not null,
                              cost_ VARCHAR(50)  not null,
                              comment_ VARCHAR(10000)  not null
                              )""")
            print('\033[1;36m>>> MySQL 数据表创建成功...\033[0m\n')
        except Exception as e:
            print('\033[1;36m>>> MySQL 数据表创建失败...\033[0m\n')

        return mysql_cur, con_obj

    def Go(self):
        """开始爬取新闻"""

        chrome_obj = self.chrome_obj()  # 获取一个 Chrome 对象

        mysql_cur, con_obj = self.mysql_obj()  # 获取一个 MySQL 连接对象

        t0 = time.time()  # 记录 程序 开始时间

        for j in range(self.Page):  # 翻页

            t1 = time.time()  # 记录爬取 当前页面 开始时间

            print(f"\033[1;36m>>> 长沙酒店 第{j + 1}页 解析中...\033[0m")  # @@@@@@@@@@@@@@@@   页 解析中...

            chrome_obj, hotel_list, score_list, num_list, url_list \
                = self.parse_page(chrome_obj)  # 解析 酒店名称 酒店评分 酒店评论数

            for i in range(len(url_list)):  # 下一家 酒店

                chrome_obj.set_page_load_timeout(4)  # @@@@@@@@@@@@@@@@@@@ 延时等待
                try:
                    chrome_obj.get(url_list[i])
                except TimeoutException:
                    print('超时了.....')

                chrome_obj, commentator_list, data_list, clear_list, \
                local_list, server_list, cost_list, comment_list = \
                    self.parse_detail(chrome_obj)  # 解析 酒店评论信息

                mysql_cur, con_obj = self.save_data(i, j, hotel_list, score_list, num_list,
                                                    commentator_list, data_list, clear_list,
                                                    local_list, server_list, cost_list,
                                                    comment_list, mysql_cur, con_obj)

                try:  # 异常捕捉，防止回退失败
                    chrome_obj.back()  # 读新闻后 点击退出
                except Exception as e:
                    time.sleep(random.randint(2, 3))
                    chrome_obj.back()  # 异常捕捉，防止回退失败

                if i == len(hotel_list) - 1:  # 循环 翻页

                    t2 = time.time()  # 记录爬取 当前页面 结束时间
                    print(
                        f"\033[1;36m本页用时%.2f秒,共用时%.2f秒 {self.Error_Num}条酒店信息下载失败,"
                        f"共{self.Success_Num}条酒店信息下载成功!\n\033[0m" % (t2 - t1, t2 - t0))  # 结算 用时 下载成功个数

                    chrome_obj = self.next_page(chrome_obj)  # 调用 点击 下页 函数

        chrome_obj.quit()  # 结束 关闭 虚拟 Chrome
        mysql_cur.close()  # 关闭与数据表的连接
        con_obj.close()  # 关闭跟mysql数据库的连接

    def next_page(self, chrome_obj):
        """点击下一页"""

        item_page = chrome_obj.page_source

        html_obj = etree.HTML(item_page)

        warn_list = html_obj.xpath('//div[@class="warnning-text"]/text()')

        if len(warn_list) > 0:
            click_obj = chrome_obj.find_element(By.ID, "nc_1_n1z")  # 定位滑块按钮
            chrome_obj, html_obj = self.slide_block(chrome_obj, click_obj)
        chrome_obj.set_page_load_timeout(3)  # @@@@@@@@@@@@@@@@ 延时等待
        try:

            click_obj = chrome_obj.find_element(By.LINK_TEXT, "下一页")  # 定位 下页
            click_obj.click()  # 点击
        except TimeoutException:
            print('点击下一页超时.....')
            pass

        return chrome_obj

    def slide_block(self, chrome_obj, click_obj):

        action_obj = webdriver.ActionChains(chrome_obj)  # 创建一个动作链对象
        action_obj.click_and_hold(click_obj)  # 点击并且按住
        action_obj.move_by_offset(300, 0).perform()  # 定位滑动坐标
        action_obj.release()  # 松开滑动
        time.sleep(3)
        item_page = chrome_obj.page_source
        html_obj = etree.HTML(item_page)

        return chrome_obj, html_obj

    def parse_page(self, chrome_obj):
        """解析新闻列表页面"""

        item_page = chrome_obj.page_source

        html_obj = etree.HTML(item_page)

        warn_list = html_obj.xpath('//div[@class="warnning-text"]/text()')

        if len(warn_list) > 0:
            print("出错了！！")
            click_obj = chrome_obj.find_element(By.ID, "nc_1_n1z")  # 定位滑块按钮
            chrome_obj, html_obj = self.slide_block(chrome_obj, click_obj)

        hotel_list = html_obj.xpath('//div[@id="J_List"]/div/@data-name')  # 酒店信息的获取

        score_list = html_obj.xpath('//p[@class="score"]/span[1]/text()')  # 酒店评分信息的获取

        num_list = html_obj.xpath('//p[@class="comment"]/span/text()')  # 酒店评论个数的获取

        url_list = html_obj.xpath('//h5/a/@href')  # 酒店评论个数的获取

        for u in range(len(url_list)):
            url_list[u] = "https:" + url_list[u]

        for i in range(random.randint(4, 8)):  # @@@@@@@@@@@@@@@@@@ 滑动延时 模仿读新闻列表
            time.sleep(1)
            try:  # 捕捉异常，排除因为没有加载进度条而报错的bug
                chrome_obj.execute_script(
                    f'document.documentElement.scrollTop={(i + 1) * 1000}')  # 滑动列表
            except Exception as e:
                continue

        return chrome_obj, hotel_list, score_list, num_list, url_list  # 返回Chrome对象和数据列表

    def parse_detail(self, chrome_obj):
        """解析新闻详情页面"""

        for i in range(random.randint(4, 8)):  # @@@@@@@@@@@@@@@@@@ 滑动延时 模仿读新闻
            time.sleep(1)
            try:  # 捕捉异常，排除因为没有加载进度条而报错的bug
                chrome_obj.execute_script(
                    f'document.documentElement.scrollTop={(i + 1) * 1000}')
            except Exception as e:
                continue

        item_page = chrome_obj.page_source

        html_obj = etree.HTML(item_page)

        warn_list = html_obj.xpath('//div[@class="warnning-text"]/text()')

        if len(warn_list) > 0:
            click_obj = chrome_obj.find_element(By.ID, "nc_1_n1z")
            chrome_obj, html_obj = self.slide_block(chrome_obj, click_obj)

        # 获取评论客户名字
        commentator_list = html_obj.xpath("//ul[@class='review-list']//@title")

        # 评论时间
        data_list = html_obj.xpath('//ul//div[@class="tb-r-info"][1]/span/text()')
        for i in range(len(data_list)):
            data_list[i] = data_list[i].replace("[", "").replace("]", "")

        # 评论星级
        clear_list = html_obj.xpath('//ul//ul/li[1]//em/text()')
        local_list = html_obj.xpath('//ul//ul/li[2]//em/text()')
        server_list = html_obj.xpath('//ul//ul/li[3]//em/text()')
        cost_list = html_obj.xpath('//ul//ul/li[4]//em/text()')

        comment_list1 = html_obj.xpath('//div[@class="comment-name"]/text()')  # 客户评论
        comment_list2 = html_obj.xpath('//div[@class="tb-r-cnt"]/text()')  # 客户评论
        comment_list = []
        for i in range(len(comment_list1)):
            comment_list.append(comment_list1[i - 1] + comment_list2[i - 1].replace("\n", ""))

        return chrome_obj, commentator_list, data_list, clear_list, \
               local_list, server_list, cost_list, comment_list  # 返回Chrome对象和数据列表

    def save_data(self, i, j, hotel_list, score_list, num_list, commentator_list,
                  data_list, clear_list, local_list, server_list, cost_list,
                  comment_list, mysql_cur, con_obj):
        """存储数据到 Mysql 数据库"""

        print(f"\033[1;36m>>>>> 长沙酒店评论信息 "
              f""
              f"第{j + 1}页第{i + 1}家酒店评论信息解析完毕  {i + 1}/20   准备下载...\033[0m")  # @@@@@@@@@@ 页完

        for k in range(len(comment_list)):  # 循环 存入 一个酒店 15 条评论 的数据

            print(
                hotel_list[i],
                score_list[i],
                num_list[i],
                commentator_list[k],
                data_list[k],
                clear_list[k],
                local_list[k],
                server_list[k],
                cost_list[k],
                comment_list[k]
            )

            # try:  # 异常捕捉，防止正文中出现 歧义(转义) 字符 导致 上传MySQL 语句 命令 错误
            self.Success_Num += 1  # 下载一条新闻 +1
            mysql_cur.execute(
                """insert into xsg_news(id,hotel_,score_,num_,commentator_,data_,
                clear_,local_,server_,cost_,comment_) 
                values(0,"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")"""
                % (
                    hotel_list[i],
                    score_list[i],
                    num_list[i],
                    commentator_list[k],
                    data_list[k],
                    clear_list[k],
                    local_list[k],
                    server_list[k],
                    cost_list[k],
                    comment_list[k]
                ))
            con_obj.commit()

            print(f"评论{self.Success_Num}:\n\t\"{hotel_list[i]}\""
                  f"--评分:{score_list[i]}"
                  f"--评论:{num_list[i]} 第{k + 1}条评论 下载成功...")

            # except Exception as e:
            #     commentator_list[k] = "***"
            #     comment_list[k] = "***"
            #     print(f"\033[1;31m评论{self.Success_Num}:\n\t\"{hotel_list[i]}\""
            #           f"--评分:{score_list[i]}"
            #           f"--评论:{num_list[i]} 第{k + 1}条评论 下载失败...失败{self.Error_Num}次\033[0m")
            #     self.Error_Num += 1  # 下载失败的个数  一条下载失败 +1
            #     self.Success_Num -= 1  # 下载成功的个数  一条下载失败 -1
            #     continue  # 一条下载失败 继续下载下一条

        return mysql_cur, con_obj


if __name__ == '__main__':

    Page = input("\033[1;36m请输入爬取页数：\033[0m")
    while not Page.isdigit():
        Page = input("\033[1;36m请输入爬取页数：\033[0m")
    Page = int(Page)

    t1 = time.time()
    Spider = CSJD(Page)
    Spider.Go()
    t2 = time.time()

    print("\n\033[1;36m>>>>> 共%d条新闻爬取完毕，共用时%.2f秒！\033[0m" % (Page * 20, t2 - t1))
