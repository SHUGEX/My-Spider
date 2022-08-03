from fake_useragent import FakeUserAgent
import requests
from lxml import etree
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)

url_ = "https://www.qfnu.edu.cn/system/resource/code/news/click/dynclicks.jsp?clickid=17996&owner=1310414041&clicktype=wbnews"

user_agent = FakeUserAgent().random

context = ssl._create_unverified_context()

headers_ = {
    "User-Agent": user_agent,
    'Cookie': 'Hm_lvt_56826aaa17b4c3ce4280b3d20836936c=1658833930,1658890000,1658921103,1658933273; JSESSIONID=0E357CC5DC458BF05EA32AB80284A080; Hm_lpvt_56826aaa17b4c3ce4280b3d20836936c=1658938530',
    "Referer": "https://www.qfnu.edu.cn/xxyw/286.htm"
    }

response_ = requests.get(url_, headers=headers_,verify=False)

str_data = response_.content
print(int(str_data),type(str_data))
#
# html_obj = etree.HTML(str_data)  # 得到一个html对象
# #
# title_list = html_obj.xpath('//div[@class="v_news_content"]/p//span/text()')  # 得到的结果是一个列表
#
# xsg_html_obj = etree.HTML(str_data)
#
#
# xsg_content_chap = xsg_html_obj.xpath(
#     '//div[@class="v_news_content"]/p//span/text()')  # @@@@@@@@@@@@@@@@@@@@@@@@@@   BUG
#
# xsg_checker = ""
# for xsg_del in range(-1, -3, -1):
#     if xsg_content_chap[xsg_del].find("：") | xsg_content_chap[xsg_del].find("："):
#         xsg_check = xsg_content_chap[xsg_del].split("：")[-1].replace("\\0xa0", " ").split(":")[-1]
#         if 2 <= len(xsg_check) <= 3:
#             xsg_checker = xsg_check
#             xsg_content_chap.pop(xsg_del)
#     elif xsg_content_chap[xsg_del] == "\\0xa0":
#         xsg_content_chap.pop(xsg_del)
#
# xsg_content = ""
# for xsg_lj in xsg_content_chap:  # 将列表格式的段落转化为字符串
#     if xsg_lj.find(".mp4"):
#         xsg_content_chap.remove(xsg_lj)
#     xsg_content += (xsg_lj.replace(" ", "")
#                     .replace("\\0xa0", " ")
#                     .replace("\"", "")
#                     .replace("\'", "")
#                     .replace("\\", "/")
#                     + "_/")
#
#
#
#
# print(xsg_content)
# #
# # with open(f'text.txt', 'w', encoding="utf-8") as f:
# #     f.write(str(title_list))
#
# with open(f'page.html', 'w', encoding="utf-8") as f:
#     f.write(str(str_data))
