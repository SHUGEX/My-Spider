from selenium import webdriver
import time
from lxml import etree
from selenium.common.exceptions import TimeoutException

chrome_obj = webdriver.Chrome()

chrome_obj.set_page_load_timeout(5)
try:
    chrome_obj.get('https://www.qfnu.edu.cn/info/1034/18188.htm')
except TimeoutException:
    print('超时了.....')

str_data = chrome_obj.page_source
xsg_html_obj = etree.HTML(str_data)
xsg_content_chap = xsg_html_obj.xpath(
    '//div[@class="v_news_content"]/p//span/text()')  # @@@@@@@@@@@@@@@@@@@@@@@@@@   BUG

xsg_checker = ""
for xsg_del in range(-1, -3, -1):
    if xsg_content_chap[xsg_del].find("：") | xsg_content_chap[xsg_del].find("："):
        xsg_check = xsg_content_chap[xsg_del].split("：")[-1].replace("\\0xa0", " ").split(":")[-1]
        if 2 <= len(xsg_check) <= 3:
            xsg_checker = xsg_check
            xsg_content_chap.pop(xsg_del)
    elif xsg_content_chap[xsg_del] == "\\0xa0":
        xsg_content_chap.pop(xsg_del)

xsg_content = ""
for xsg_lj in xsg_content_chap:  # 将列表格式的段落转化为字符串
    if xsg_lj.find(".mp4"):
        xsg_content_chap.remove(xsg_lj)
    xsg_content += (xsg_lj.replace(" ", "")
                    .replace("\\0xa0", " ")
                    .replace("\"", "")
                    .replace("\'", "")
                    .replace("\\", "")
                    + "__")
print(xsg_content)
print(xsg_checker)

# str_data = chrome_obj.page_source
#
# html_obj = etree.HTML(str_data)
#
# title_list = html_obj.xpath('//div[@class="main_list"]/ul/li/a/@title')
#
# date_list = html_obj.xpath('//div[@class="main_list"]/ul/li/a/span/text()')
#
#
# url_list = html_obj.xpath('//div[@class="main_list"]/ul/li/a/@href')
# for i in range(len(url_list)):
#     url_list[i] = "https://www.qfnu.edu.cn/" + url_list[i].replace("..", "")  # 拼接成完整的url
#
# print(title_list)
# print(date_list)
# print(url_list)

# print(len(info_list))
