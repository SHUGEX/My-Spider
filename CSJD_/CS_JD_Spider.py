import time
import random
from fake_useragent import FakeUserAgent
import requests
from lxml import etree
from pymysql import connect
import urllib3
urllib3.disable_warnings()


class CSJD_:
    """长沙酒店信息爬取"""

    def __init__(self, Page):
        self.Page = Page  # 爬取 新闻页数  15 条新闻/页
        self.Error_Num = 0  # 累计新闻正文下载失败个数
        self.Success_Num = 0  # 累计下载成功的新闻数
        proxies_list = [                        # 代理IP
            {'http': 'http://121.230.210.232:3256'},
            {'http': 'http://183.195.106.118:8118'},
            {'http': 'http://139.198.179.174:3128'},
            {'http': 'http://113.121.45.140:9999'},
            {'http': 'http://49.86.9.26:9999'},
            {'http': 'http://183.247.202.208:30001'},
            {'http': 'http://112.14.47.6:52024'},
            {'http': 'http://58.20.235.180:9091'},
            {'http': 'http://202.55.5.209:8090'},
            {'http': 'http://117.114.149.66:55443'},
            {'http': 'http://117.114.149.66:55443'},
            {'http': 'http://218.75.102.198:8000'},
            {'http': 'http://103.37.141.69:80'},
            {'http': 'http://202.55.5.209:8090'},
            {'http': 'http://58.20.235.180:9091	'},
            {'http': 'http://202.55.5.209:8090	'},
            {'http': 'http://103.37.141.69:80'},
            {'http': 'http://202.55.5.209:8090'},
            {'http': 'http://118.163.120.181:58837'},
            {'http': 'http://47.106.105.236:80'},
            {'http': 'http://218.89.51.167:9091'},
            {'http': 'http://39.175.75.144:30001'},
            {'http': 'http://110.53.52.148:9091'},
            {'http': 'http://64.119.29.22:8080'},
            {'http': 'http://43.132.200.137:9812'},
            {'http': 'http://115.211.35.42:9000'},
            {'http': 'http://183.147.31.138:9000'},
            {'http': 'http://45.83.123.8:3129'},
            {'http': 'http://120.79.136.134:8080'},
            {'http': 'http://61.183.234.226:9091'}
        ]
        self.proxies_ = random.choice(proxies_list)
        pass

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

    # def Go(self):
    #     log_url_ = "https://hotel.fliggy.com/hotel_list3.htm?_input_charset=utf-8&cityName=%E9%95%BF%E6%B2%99%E5%B8%82&city=430100&keywords=&checkIn=2022-08-04&checkOut=2022-08-05&ttid=seo.000000574&_output_charset=utf8"
    #
    #     headers_ = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    #         "cookie": 'cna=UF8BG0st1S4CAW8U4YxB0ePS; lid=%E5%9D%90%E5%B1%B1%E5%AE%A225; enc=zxTUrPzLx18McbATo2YYRmJSkn3OBHSYlRZCyqjHdAK2QtrKOhQYF3Oq6DItAtjvgw4eBa6lHOhX0iA8HrUQlA%3D%3D; VISITED_HOTEL_TOKEN=5cc5cea3-a9a4-46db-a0ad-4cd7dac7f237; t=caa40b05aa8e1a69fe0a9988ea91d63c; tracknick=%5Cu5750%5Cu5C71%5Cu5BA225; _tb_token_=53933953b3615; cookie2=145aff9404117ec6aefa974d6878bb1f; chanelStat="NA=="; chanelStatExpire="2022-08-15 13:34:36"; xlly_s=1; dnk=%5Cu5750%5Cu5C71%5Cu5BA225; cancelledSubSites=empty; uc1=cookie14=UoeyDt0s05Yh8g%3D%3D&pas=0&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21=URm48syIYn73&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D; _l_g_=Ug%3D%3D; unb=3496207830; cookie1=VvlxeQwr78HnlP9p0ObnNqFFddezJZSEk%2FxnvPhj3ks%3D; login=true; cookie17=UNQ%2Bps3DVUr95Q%3D%3D; _nk_=%5Cu5750%5Cu5C71%5Cu5BA225; sgcookie=E100rrN9Y%2BBRWnMfRc45glH7ToByWyQ6ATRHxQXn8aaewfBh4fI807ctCG4yVgAaoN4e7Ip3PooHC3jiQS9gEY%2BANJTz26FEtHdl%2B1MjHZjDhHQ%3D; sg=501; csg=73a173d8; x5sec=7b22617365727665723b32223a226561363637373366636562666331623161353736626439396362666263386430434b6e6c324a63474550504d714a626f686262424f526f4d4d7a51354e6a49774e7a677a4d44737a4d4d723832326b36416d737851414d3d227d; l=eBgTSz_cL80f73X9BOfZ-urza77OJIRY6uPzaNbMiOCPOA1w53idW6Yyw58eCnGVh6RvR35Wn1oBBeYBqQAonxvTlFoEvDMmn; isg=BKenjUPFiUj39w3Vu11XdwpqNttxLHsOLVaWiHkU8zZdaMcqgf1UXqFqjmh231OG; tfstk=cGIcBVgpNZ8j_O6FQitbjP0e1vscZmnwtGS54-Z4WIk64ESPiKgr8zo_EIfcXV1..'
    #     }
    #     # 2.发送网络请求，获取响应对象
    #
    #
    #     response_ = requests.get(log_url_, headers=headers_, verify=False)
    #     # response_ = requests.get(log_url_, headers=headers_, verify=False, proxies=self.proxies_)
    #     str_data = response_.text
    #     html_obj = etree.HTML(str_data)  # 得到一个html对象
    #
    #     hotel_list = html_obj.xpath('//div[@id="J_List"]/div/@data-name')  # 酒店信息的获取
    #
    #     score_list = html_obj.xpath('//p[@class="score"]/span[1]/text()')  # 酒店评分信息的获取
    #
    #     num_list = html_obj.xpath('//p[@class="comment"]/span/text()')  # 酒店评论个数的获取
    #
    #     url_list = html_obj.xpath('//h5/a/@href')  # 酒店评论个数的获取
    #
    #     for u in range(len(url_list)):
    #         url_list[u] = "https:" + url_list[u]
    #     with open('Tb00.html', 'w', encoding="utf-8") as f:
    #         f.write(str_data)
    #
    #     print(hotel_list, score_list, num_list, url_list)
    #
    #     url_ = url_list[0]
    #
    #     headers_ = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    #         "cookie": 'cna=UF8BG0st1S4CAW8U4YxB0ePS; lid=%E5%9D%90%E5%B1%B1%E5%AE%A225; enc=zxTUrPzLx18McbATo2YYRmJSkn3OBHSYlRZCyqjHdAK2QtrKOhQYF3Oq6DItAtjvgw4eBa6lHOhX0iA8HrUQlA%3D%3D; VISITED_HOTEL_TOKEN=5cc5cea3-a9a4-46db-a0ad-4cd7dac7f237; t=caa40b05aa8e1a69fe0a9988ea91d63c; tracknick=%5Cu5750%5Cu5C71%5Cu5BA225; _tb_token_=53933953b3615; cookie2=145aff9404117ec6aefa974d6878bb1f; chanelStat="NA=="; chanelStatExpire="2022-08-15 13:34:36"; xlly_s=1; dnk=%5Cu5750%5Cu5C71%5Cu5BA225; cancelledSubSites=empty; uc1=cookie14=UoeyDt0s05Yh8g%3D%3D&pas=0&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21=URm48syIYn73&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D; _l_g_=Ug%3D%3D; unb=3496207830; cookie1=VvlxeQwr78HnlP9p0ObnNqFFddezJZSEk%2FxnvPhj3ks%3D; login=true; cookie17=UNQ%2Bps3DVUr95Q%3D%3D; _nk_=%5Cu5750%5Cu5C71%5Cu5BA225; sgcookie=E100rrN9Y%2BBRWnMfRc45glH7ToByWyQ6ATRHxQXn8aaewfBh4fI807ctCG4yVgAaoN4e7Ip3PooHC3jiQS9gEY%2BANJTz26FEtHdl%2B1MjHZjDhHQ%3D; sg=501; csg=73a173d8; x5sec=7b22617365727665723b32223a226561363637373366636562666331623161353736626439396362666263386430434b6e6c324a63474550504d714a626f686262424f526f4d4d7a51354e6a49774e7a677a4d44737a4d4d723832326b36416d737851414d3d227d; tfstk=cHCABOTUcuqcXwJBCZekQC4IW-SAZwq9Vqti61k7Zm_xppcOivfh99kzhFteDzC..; l=eBgTSz_cL80f7CdzBOfalurza779xIRb6uPzaNbMiOCP_3fwlOD1W6YyNN8eCnGVn6R2R35Wn1oBB-LnAyUBlXtYOIAyMmJU3dTh.; isg=BFVVhxuQm2Jwgb8PlbNl7cwsZFEPUglkK1CEstf6Ukw2LnQgn6M2NKis_DKYcSEc',
    #         'referer': log_url_
    #     }
    #     # 2.发送网络请求，获取响应对象
    #     response_ = requests.get(url_, headers=headers_, verify=False, proxies=self.proxies_)
    #     str_data = response_.content.decode()
    #     html_obj = etree.HTML(str_data)  # 得到一个html对象
    #     with open('Tb.html', 'w', encoding="utf-8") as f:
    #         f.write(str_data)
    #
    #     commentator_list = html_obj.xpath('//ul//div[@class="taFrom"]//text()')  # 评论人
    #     data_list = html_obj.xpath('//ul//div[@class="tb-r-info"][1]/span/text()')  # 评论时间
    #     clear_list = html_obj.xpath('//ul//ul/li[1]//em/text()')  # 卫生
    #     local_list = html_obj.xpath('//ul//ul/li[2]//em/text()')  # 设施
    #     server_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 服务
    #     cost_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 性价比
    #     comment_list = html_obj.xpath('comment_list')  # 客户评论
    #
    #     print(commentator_list, data_list, clear_list, local_list, server_list, cost_list, comment_list)
    #
    #     url_ = url_list[1]
    #
    #     headers_ = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    #         "cookie": 'cna=UF8BG0st1S4CAW8U4YxB0ePS; lid=%E5%9D%90%E5%B1%B1%E5%AE%A225; enc=zxTUrPzLx18McbATo2YYRmJSkn3OBHSYlRZCyqjHdAK2QtrKOhQYF3Oq6DItAtjvgw4eBa6lHOhX0iA8HrUQlA%3D%3D; VISITED_HOTEL_TOKEN=5cc5cea3-a9a4-46db-a0ad-4cd7dac7f237; t=caa40b05aa8e1a69fe0a9988ea91d63c; tracknick=%5Cu5750%5Cu5C71%5Cu5BA225; _tb_token_=53933953b3615; cookie2=145aff9404117ec6aefa974d6878bb1f; chanelStat="NA=="; chanelStatExpire="2022-08-15 13:34:36"; xlly_s=1; dnk=%5Cu5750%5Cu5C71%5Cu5BA225; cancelledSubSites=empty; uc1=cookie14=UoeyDt0s05Yh8g%3D%3D&pas=0&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21=URm48syIYn73&existShop=false&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D; _l_g_=Ug%3D%3D; unb=3496207830; cookie1=VvlxeQwr78HnlP9p0ObnNqFFddezJZSEk%2FxnvPhj3ks%3D; login=true; cookie17=UNQ%2Bps3DVUr95Q%3D%3D; _nk_=%5Cu5750%5Cu5C71%5Cu5BA225; sgcookie=E100rrN9Y%2BBRWnMfRc45glH7ToByWyQ6ATRHxQXn8aaewfBh4fI807ctCG4yVgAaoN4e7Ip3PooHC3jiQS9gEY%2BANJTz26FEtHdl%2B1MjHZjDhHQ%3D; sg=501; csg=73a173d8; x5sec=7b22617365727665723b32223a226561363637373366636562666331623161353736626439396362666263386430434b6e6c324a63474550504d714a626f686262424f526f4d4d7a51354e6a49774e7a677a4d44737a4d4d723832326b36416d737851414d3d227d; tfstk=cHCABOTUcuqcXwJBCZekQC4IW-SAZwq9Vqti61k7Zm_xppcOivfh99kzhFteDzC..; l=eBgTSz_cL80f7CdzBOfalurza779xIRb6uPzaNbMiOCP_3fwlOD1W6YyNN8eCnGVn6R2R35Wn1oBB-LnAyUBlXtYOIAyMmJU3dTh.; isg=BFVVhxuQm2Jwgb8PlbNl7cwsZFEPUglkK1CEstf6Ukw2LnQgn6M2NKis_DKYcSEc',
    #         'referer': log_url_
    #     }
    #     # 2.发送网络请求，获取响应对象
    #     response_ = requests.get(url_, headers=headers_, verify=False, proxies=self.proxies_)
    #     str_data = response_.content.decode()
    #     html_obj = etree.HTML(str_data)  # 得到一个html对象
    #     with open('Tb.html', 'w', encoding="utf-8") as f:
    #         f.write(str_data)
    #
    #     commentator_list = html_obj.xpath('//ul//div[@class="taFrom"]//text()')  # 评论人
    #     data_list = html_obj.xpath('//ul//div[@class="tb-r-info"][1]/span/text()')  # 评论时间
    #     clear_list = html_obj.xpath('//ul//ul/li[1]//em/text()')  # 卫生
    #     local_list = html_obj.xpath('//ul//ul/li[2]//em/text()')  # 设施
    #     server_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 服务
    #     cost_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 性价比
    #     comment_list = html_obj.xpath('comment_list')  # 客户评论
    #
    #     print(commentator_list, data_list, clear_list, local_list, server_list, cost_list, comment_list)
    #
    #     pass

    def Go1(self):


        url_ = "https://hotel.fliggy.com/hotel_detail2.htm?searchBy=&market=0&previousChannel=&shid=65907102&city=430100&checkIn=2022-08-11&checkOut=2022-08-12&searchId=5f4b0ed6f92f4b64a57ad82540642536&filterByRoomTickets=false&activityCode=&roomNum=1&aNum_1=2&cNum_1=0&sellerId=&sellerIds=&_output_charset=utf8&_input_charset=utf8"

        headers_ = {
            "User-Agent": FakeUserAgent().random,
            "cookie": 'cna=UF8BG0st1S4CAW8U4YxB0ePS; lid=%E5%9D%90%E5%B1%B1%E5%AE%A225; enc=zxTUrPzLx18McbATo2YYRmJSkn3OBHSYlRZCyqjHdAK2QtrKOhQYF3Oq6DItAtjvgw4eBa6lHOhX0iA8HrUQlA%3D%3D; VISITED_HOTEL_TOKEN=5cc5cea3-a9a4-46db-a0ad-4cd7dac7f237; t=caa40b05aa8e1a69fe0a9988ea91d63c; tracknick=%5Cu5750%5Cu5C71%5Cu5BA225; _tb_token_=58e14e53f714d; cookie2=10057f8e08f162a7c5efb830c5241055; chanelStat="NA=="; chanelStatExpire="2022-08-12 23:57:56"; xlly_s=1; dnk=%5Cu5750%5Cu5C71%5Cu5BA225; uc1=pas=0&cookie21=UtASsssme%2BBq&cookie14=UoeyDt9EOsThlg%3D%3D&cookie15=UIHiLt3xD8xYTw%3D%3D&existShop=false&cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D; _l_g_=Ug%3D%3D; unb=3496207830; cookie1=VvlxeQwr78HnlP9p0ObnNqFFddezJZSEk%2FxnvPhj3ks%3D; login=true; cookie17=UNQ%2Bps3DVUr95Q%3D%3D; _nk_=%5Cu5750%5Cu5C71%5Cu5BA225; sgcookie=E100ZrhcAojdhiIMAc5O27t2bvn2mIzYVSpJ5KX2hu1iG8%2B1f%2F6NaKYItD%2FFynMtxxWCdjdNNmAOLMYdImJW2ryNooYHXrgCtsTv4e9orSDC2YU%3D; cancelledSubSites=empty; sg=501; csg=26960a67; x5sec=7b22617365727665723b32223a22346133306363333831393832653337653533376434663365373835323834623643504b647970634745492f55726f4445367032673667456144444d304f5459794d4463344d7a41374d5444356a4f4355416a6f43617a464141773d3d227d; tfstk=cUsNBQ0PDlEZuNQP8Ht4hMkb2VnOZ4BGnDJWS7MOkIASkF8GiHGvKRu6LKMEiFf..; l=eBgTSz_cL80f7-tSBOfZlurza77OSIRY6uPzaNbMiOCPO3C95qTfW6Y4ROYpC3GVh6FMR35Wn1oBBeYBqhcbIQtyKShJMIHmn; isg=BJ2drTHGo87EiEf3HQuttdQ0rHmXutEMI7hc6l9i2_QjFr1IJwrg3VKMQAoQienE',
            'referer': 'https://hotel.fliggy.com/hotel_list3.htm?_input_charset=utf-8&cityName=%E9%95%BF%E6%B2%99%E5%B8%82&city=430100&keywords=&checkIn=2022-08-04&checkOut=2022-08-05&ttid=seo.000000574&_output_charset=utf8'
        }
        # 2.发送网络请求，获取响应对象
        response_ = requests.get(url_, headers=headers_, verify=False, proxies=self.proxies_)
        str_data = response_.content.decode()
        html_obj = etree.HTML(str_data)  # 得到一个html对象
        with open('Tb.html', 'w', encoding="utf-8") as f:
            f.write(str_data)

        commentator_list = html_obj.xpath('//img/@nick')  # 评论人
        data_list = html_obj.xpath('//ul//div[@class="tb-r-info"][1]/span/text()')  # 评论时间
        clear_list = html_obj.xpath('//ul//ul/li[1]//em/text()')  # 卫生
        local_list = html_obj.xpath('//ul//ul/li[2]//em/text()')  # 设施
        server_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 服务
        cost_list = html_obj.xpath('//ul//ul/li[3]//em/text()')  # 性价比
        comment_list1 = html_obj.xpath('//div[@class="comment-name"]/text()')  # 客户评论
        comment_list2 = html_obj.xpath('//div[@class="tb-r-cnt"]/text()')  # 客户评论
        comment_list = []
        for i in range(len(comment_list1)):
            comment_list.append(comment_list1[i-1]+comment_list2[i-1].replace("\n", ""))

        print(commentator_list, data_list, clear_list, local_list, server_list, cost_list, comment_list)
        pass


if __name__ == '__main__':

    # Page = input("\033[1;36m请输入爬取页数：\033[0m")
    Page = "1"
    while not Page.isdigit():
        Page = input("\033[1;36m请输入爬取页数：\033[0m")
    Page = int(Page)

    t1 = time.time()
    Spider = CSJD_(Page)
    Spider.Go1()
    t2 = time.time()

    print("\n\033[1;36m>>>>> 共%d条新闻爬取完毕，共用时%.2f秒！\033[0m" % (Page * 20, t2 - t1))