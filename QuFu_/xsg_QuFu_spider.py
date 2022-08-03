import random
from selenium import webdriver
import time  # 计时
from pymysql import *  # MySQL数据库
from lxml import etree  # 解析html
from selenium.webdriver.chrome.options import Options  # 无头模式
from selenium.common.exceptions import TimeoutException  # 页面加载等待的异常处理


class xsg_QuFu:
    def __init__(self, xsg_page):
        self.xsg_page = xsg_page  # 爬取 新闻页数  15 条新闻/页
        self.xsg_content_error = 0  # 累计新闻正文下载失败个数
        self.xsg_news_num = 0      # 累计下载成功的新闻数
        pass

    def xsg_chrome_obj(self):
        """创建一个Chrome对象并进入主页"""

        xsg_options_ = Options()  # 设置无界面模式
        xsg_options_.add_argument('--headless')
        xsg_chrome = webdriver.Chrome(options=xsg_options_)  # 无界面模式

        xsg_chrome.set_page_load_timeout(5)  # 页面加载等待的异常处理
        try:
            xsg_chrome.get('https://www.qfnu.edu.cn/xxyw.htm')
        except TimeoutException:
            print('进入主页超时.....\n')

        print('\033[1;36m\n> 已进入目标网址...\033[0m')

        return xsg_chrome

    def xsg_mysql_obj(self):
        """与MySQL数据库进行连接,会创建一个MySQL连接对象"""

        xsg_con_obj = connect(host="127.0.0.1", user="root",
                              password="123456", database="xsg_qufu_spider", port=3306, charset='utf8mb4')
        print('\033[1;36m>> MySQL 数据库连接成功...\033[0m\n')

        xsg_mysql = xsg_con_obj.cursor()  # 创建一个 MySQL 连接对象

        return xsg_mysql, xsg_con_obj

    def xsg_Go(self):
        """开始爬取新闻"""

        xsg_chrome = self.xsg_chrome_obj()  # 获取一个 Chrome 对象

        xsg_mysql, xsg_con_obj = self.xsg_mysql_obj()  # 获取一个 MySQL 连接对象

        t0 = time.time()  # 记录 程序 开始时间

        for xsg_j in range(self.xsg_page):  # 翻页

            t1 = time.time()  # 记录爬取 当前页面 开始时间

            print(f"\033[1;36m>>> 曲阜师大学校要闻 第{xsg_j + 1}页 解析中...\033[0m")

            xsg_chrome, xsg_title_list, xsg_date_list, xsg_news_url \
                = self.xsg_parse_page(xsg_chrome)  # 解析 新闻 标题 日期 正文url

            xsg_clicks_list = []     # 浏览量 列表
            xsg_content_list = []    # 正文 列表
            xsg_checker_list = []    # 审核 列表

            for xsg_i in range(len(xsg_news_url)):  # 下一条 新闻

                xsg_chrome, xsg_clicks_list, xsg_content_list, xsg_checker_list = \
                    self.xsg_parse_news(xsg_chrome, xsg_news_url, xsg_i, xsg_clicks_list, xsg_content_list,
                                        xsg_checker_list)  # 解析 新闻 浏览量 正文 审核

                try:                   # 异常捕捉，防止回退失败
                    xsg_chrome.back()  # 读新闻后 点击退出
                except Exception as e:
                    time.sleep(random.randint(1,2))
                    xsg_chrome.back()  # 异常捕捉，防止回退失败

                if xsg_i == len(xsg_news_url) - 1:  # 循环 翻页

                    xsg_mysql, xsg_con_obj = self.xsg_save_data(xsg_title_list, xsg_date_list, xsg_clicks_list,
                                                                xsg_content_list, xsg_checker_list, xsg_j, xsg_mysql,
                                                                xsg_con_obj)

                    t2 = time.time()   # 记录爬取 当前页面 结束时间

                    print(
                        f"\033[1;36m本页用时%.2f秒,共用时%.2f秒 {self.xsg_content_error}条新闻下载失败,"
                        f"共{self.xsg_news_num}条新闻下载成功!\n\033[0m" % (t2 - t1, t2 - t0))  # 结算 用时 下载成功个数

                    xsg_chrome = self.xsg_next_page(xsg_chrome)  # 调用 点击 下页 函数

        xsg_chrome.quit()       # 结束 关闭 虚拟 Chrome
        xsg_mysql.close()       # 关闭与数据表的连接
        xsg_con_obj.close()     # 关闭跟mysql数据库的连接

    def xsg_next_page(self, xsg_chrome):
        """点击下一页"""

        xsg_chrome.set_page_load_timeout(3)  # @@@@@@@@@@@@@@@@ 延时等待
        try:
            xsg_click_obj = xsg_chrome.find_elements_by_link_text("下页")[0]  # 定位 下页
            xsg_click_obj.click()  # 点击
        except TimeoutException:
            print('点击下一页超时.....')
            pass

        return xsg_chrome

    def xsg_parse_page(self, xsg_chrome):
        """解析新闻列表页面"""

        xsg_item_page = xsg_chrome.page_source

        xsg_html_obj = etree.HTML(xsg_item_page)

        xsg_title_list = xsg_html_obj.xpath('//div[@class="main_list"]/ul/li/a/@title')  # 新闻标题列表

        xsg_date_list = xsg_html_obj.xpath('//div[@class="main_list"]/ul/li/a/span/text()')  # 新闻发布日期列表

        xsg_news_url = xsg_html_obj.xpath('//div[@class="main_list"]/ul/li/a/@href')  # 新闻详情页列表

        for i in range(random.randint(1, 3)):  # @@@@@@@@@@@@@@@@@@ 滑动延时 模仿读新闻列表
            time.sleep(0.05)
            try:                            # 捕捉异常，排除因为没有加载进度条而报错的bug
                xsg_chrome.execute_script(
                    f'document.documentElement.scrollTop={(i + 1) * 125}')  # 滑动列表
            except Exception as e:
                continue

        return xsg_chrome, xsg_title_list, xsg_date_list, xsg_news_url  # 返回Chrome对象和数据列表

    def xsg_parse_news(self, xsg_chrome, xsg_news_url, xsg_i, xsg_clicks_list, xsg_content_list, xsg_checker_list):
        """解析新闻详情页面"""

        xsg_chrome.set_page_load_timeout(3)  # @@@@@@@@@@@@@@@@@@@ 延时等待
        try:
            xsg_chrome.get(f'https://www.qfnu.edu.cn/{xsg_news_url[xsg_i].replace("..", "")}')
        except TimeoutException:
            print('超时了.....')

        for i in range(random.randint(1, 3)):  # @@@@@@@@@@@@@@@@@@ 滑动延时 模仿读新闻
            time.sleep(0.05)
            try:                            # 捕捉异常，排除因为没有加载进度条而报错的bug
                xsg_chrome.execute_script(
                    f'document.documentElement.scrollTop={(i + 1) * 700}')
            except Exception as e:
                continue

        xsg_news_page = xsg_chrome.page_source

        xsg_html_obj = etree.HTML(xsg_news_page)
        try:                                  # 捕捉异常，排除因为没有解析到内容而超出索引报错的bug
            xsg_clicks_list.append(xsg_html_obj.xpath('//p[@class="info"]/span/text()')[0])
        except Exception as e:
            xsg_clicks_list.append("错误")

        xsg_content_chap = xsg_html_obj.xpath(
            '//div[@class="v_news_content"]/p//span/text()')   # 获取 段落 列表

        xsg_checker = ""
        if len(xsg_content_chap) >= 2:              # 获取 段落 最后的 审核
            for xsg_del in range(len(xsg_content_chap) - 1, len(xsg_content_chap) - 2, -1):
                if xsg_content_chap[xsg_del].find("：") or xsg_content_chap[xsg_del].find("："):
                    xsg_check = xsg_content_chap[xsg_del].split("：")[-1].replace("\\0xa0", " ").split(":")[-1]
                    if 2 <= len(xsg_check) <= 3:
                        xsg_checker = xsg_check
                    xsg_content_chap.pop(xsg_del)
                elif xsg_content_chap[xsg_del] == "\\0xa0":
                    xsg_content_chap.pop(xsg_del)

        xsg_content = ""
        for xsg_lj in xsg_content_chap:  # 将 段落 列表 拼接 为整体
            if xsg_lj.find(".mp4"):
                xsg_content_chap.remove(xsg_lj)  # 清除 正文中 视频url
            xsg_content += (xsg_lj.replace(" ", "")  # 清除空格
                            .replace("\\0xa0", " ")  # 清除空格
                            .replace("\"", "”")      # 清除可能引起MySQL上传语法错误的符号
                            .replace("\'", "’")
                            .replace("\\", "、")
                            + "_/_")    # 在每段之间用 _/_ 连接

        xsg_content_list.append(xsg_content)  # 插入一篇正文

        xsg_checker_list.append(xsg_checker)  # 插入一个审核

        return xsg_chrome, xsg_clicks_list, xsg_content_list, xsg_checker_list  # 返回Chrome对象和数据列表

    def xsg_save_data(self, xsg_title_list, xsg_date_list,
                      xsg_clicks_list, xsg_content_list, xsg_checker_list, xsg_j, xsg_mysql, xsg_con_obj):
        """存储数据到 Mysql 数据库"""

        print(f"\033[1;36m>>>> 曲阜师大学校要闻 第{xsg_j + 1}页15条新闻解析完毕 准备下载...\033[0m")  # @@@@@@@@@@ 页完

        for xsg_i in range(len(xsg_title_list)):  # 循环 存入 一页 15 条新闻 的数据
            try:          # 异常捕捉，防止正文中出现 歧义(转义) 字符 导致 上传MySQL 语句 命令 错误
                self.xsg_news_num += 1   # 下载一条新闻 +1
                print(f"新闻{self.xsg_news_num}；\n\t\"{xsg_title_list[xsg_i]}\""  
                
                      f"--{xsg_date_list[xsg_i]}"
                      f"--浏览{xsg_clicks_list[xsg_i]}次 审核:{xsg_checker_list[xsg_i]} 下载成功...")
                xsg_mysql.execute(
                    """insert into xsg_news(id,xsg_title_list, xsg_date_list,xsg_clicks_list, xsg_content_list, xsg_checker_list) values(0,"%s","%s","%s","%s","%s")"""
                    % (
                        xsg_title_list[xsg_i],
                        xsg_date_list[xsg_i],
                        xsg_clicks_list[xsg_i],
                        xsg_con_obj.escape_string(xsg_content_list[xsg_i]),
                        xsg_con_obj.escape_string(xsg_checker_list[xsg_i])
                    ))
                xsg_con_obj.commit()

            except Exception as e:
                xsg_content_list[xsg_i] = "内容格式错误"
                print(f"\033[1;31m新闻{xsg_i + 1 + xsg_j * 15}；\n\t\"{xsg_title_list[xsg_i]}\""   # 打印 错误信息
                      f"--{xsg_date_list[xsg_i]}"
                      f"--浏览{xsg_clicks_list[xsg_i]}次 审核:{xsg_checker_list[xsg_i]} 下载失败...\033[0m")
                self.xsg_content_error += 1  # 下载失败的新闻个数  一条新闻下载失败 +1
                self.xsg_news_num -= 1  # 下载成功的新闻个数  一条新闻下载失败 -1
                continue   # 一条新闻下载失败 继续下载下一条新闻

        print(f"\033[1;36m>>>>> 曲阜师大学校要闻 第{xsg_j + 1}页15条新闻 下载成功...\033[0m", end="  ")

        return xsg_mysql, xsg_con_obj


if __name__ == '__main__':

    xsg_page = input("\033[1;36m请输入爬取页数：\033[0m")
    while not xsg_page.isdigit():
        xsg_page = input("\033[1;36m请输入爬取页数：\033[0m")
    xsg_page = int(xsg_page)

    t1 = time.time()
    xsg_Spider = xsg_QuFu(xsg_page)
    xsg_Spider.xsg_Go()
    t2 = time.time()

    print("\n\033[1;36m>>>>> 共%d条新闻爬取完毕，共用时%.2f秒！\033[0m" % (xsg_page * 15, t2 - t1))
