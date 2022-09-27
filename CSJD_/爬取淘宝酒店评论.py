# -- coding:utf-8 --
"""
要求：
1. 爬取飞猪酒店长沙地区评论数据
url = "https://hotel.fliggy.com/hotel_list3.htm?_input_charset=utf-8&cityName=%E9%95%BF%E6%B2%99%E5%B8%82&city=430100&keywords=&checkIn=2022-01-16&checkOut=2022-01-17&ttid=seo.000000574&_output_charset=utf8"
2. 数据缺失处理   正则清洗
3. 不少于2500条
4. 批量爬取会封IP  :构建IP池，放慢爬取速度
5. 存入mysql中


"""
from multiprocessing import Process

"""
1. 评论数据为ajax动态加载json格式数据
2. 改变url参数中的page可以实现翻页
3. cookie更新很快，爬取速度不能太快，否则会被反爬检测到
4. 批量爬取会封IP  (构建IP池每次爬取使用随机IP)
5. 数据保存到mysql中 

"""

import re
import requests
import time
import random
import pymysql


def hotel_spider(a):
    hotel_lists = []
    for j in range(a):
        url = f"https://hotel.fliggy.com/ajax/hotelList.htm?pageSize=20&currentPage={j + 1}&totalItem=11908&startRow=0&endRow=19&city=430100&tid=null&market=0&previousChannel=&u=null&detailLinkCity=430100&cityName=%E9%95%BF%E6%B2%99"
        # 网页抓包获取含有酒店名称和id的异步数据包， ajax动态加载， j变量控制其页数
        # 构建表单
        headers = {
            "x-requested-with": "XMLHttpRequest",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
            'referer': 'https://hotel.fliggy.com/hotel_list3.htm?_input_charset=utf-8&cityName=%E9%95%BF%E6%B2%99%E5%B8%82&city=430100&keywords=&checkIn=2022-01-16&checkOut=2022-01-17&ttid=seo.000000574&_output_charset=utf8',
            'cookie': 'lid=%E4%B8%80%E5%8F%AA%E5%8C%97%E8%BE%B0; enc=uh2XZ%2FdHLA5rsVfIj6WjDzK%2F3w7ljRu2d%2FHuryRJf2AB9j9IIweCn7U3rEkuHgxVsZ3r9EUvT%2FqHhbuw42MFuwPmruBB3mcYBJiTLdZjXwI%3D; cna=ZCiyGqkrPHQCATE0Y0qSEjyN; VISITED_HOTEL_TOKEN=f28571eb-188b-494f-97b0-99688939105d; t=b8ea9d1b47f4dcc66a925ea41758184d; tracknick=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; _tb_token_=ee10af0831d05; cookie2=1ea8631fc790242285e4643b91b0c3e7; chanelStat="NA=="; chanelStatExpire="2022-07-04 18:47:17"; xlly_s=1; dnk=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; uc1=cookie14=UoexND3h7Lf3LA%3D%3D&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&existShop=false&cookie21=URm48syIYn73&pas=0; _l_g_=Ug%3D%3D; unb=2209062900905; cookie1=URotYFYuJbW70BuNizn%2FHZhV4QpheErchsEVTVH4pzE%3D; login=true; cookie17=UUphw2VT5UDzvsP%2BuQ%3D%3D; _nk_=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; sgcookie=E100dNhXLqn0XZrTdyefgbJ9ztui7MgOEdcKsqLdsXtDk6lQBTW%2FAI8u09%2BCjcAQ9xoxnisvskc2JoF5eYMIYmja4tElLhtUHiC1gYjJK7HQfoI%3D; cancelledSubSites=empty; sg=%E8%BE%B053; csg=6ae461a3; x5sec=7b226873703b32223a226237313232626266363664323833616534353632356361383136373936363633434a584b2b355547454e43427963616f7149754451686f504d6a49774f5441324d6a6b774d446b774e5473784d4b3757344c76392f2f2f2f2f77453d222c22617365727665723b32223a226534633035613162303439363633623839333234656437653433316637633566434b6a4b2b355547454a372b32636e31744d757568414561447a49794d446b774e6a49354d4441354d4455374d54446a37507675417a6f43617a453d227d; tfstk=cBdABgTal0mchK_J8KHl_Xi8NuTAasaAjrsT6CaILJHa0oVT1sDvtBpUUx_NYi3R.; l=eBOcvWBRLohhQrshBO5aourza779iQRf1nVzaNbMiInca1oAwEKA3NCh8RjykdtjgtCFCexPUcfRbdeX8sUd_IiNWvaDcat-7xvO.; isg=BPT0KtN4Kpnvyr761VslfEM3xbJmzRi3sUzfco5XAX-z-ZdDtNxGR8z3eTEhNVAP'
        }
        proxies_list = [
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
        proxies = random.choice(proxies_list)  # 随机从列表中拿取一个IP
        # 传递proxies代理IP参数
        response = requests.get(url=url, headers=headers, proxies=proxies)
        # 构建请求头，发送请求
        data = response.content.decode(encoding="gbk")
        # print(data)
        # 正则表达式清洗数据
        names = re.findall('"shid":.*?,"name":"(.*?)","', data)
        shids = re.findall('"shid":(.*?),"name"', data)
        k = 0
        for n in names:
            hotel_list = {
                "name": n,
                "shid": shids[k]
            }
            k += 1
            hotel_lists.append(hotel_list)
        # 获取所有酒店名称以及对应的id用于评论爬取，保存在hotel_lists中
        time.sleep(random.randint(1, 3))
    #     随机睡眠放慢爬取速度，避免被淘宝检测到
    print(hotel_lists)
    # 打印以检验酒店名称和Id爬取结果
    return hotel_lists


def content_spider(a, shid):
    content_list = []
    for j in range(1, a + 1):
        url = f"https://hotel.fliggy.com/ajax/getHotelRates.htm?sellerId=&page={j}&showContent=0&shid={shid}"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0  Safari/537.36',
            'referer': 'https://hotel.fliggy.com/hotel_detail2.htm?spm=181.7087309.0.0.7a2569c35wOT2j&searchBy=&shid=54065021&city=430100&checkIn=2022-06-19&market=0&previousChannel=&checkOut=2022-06-20&searchId=425910a60a654a209f5a315c5d6dafbf&filterByRoomTickets=false&activityCode=&isFreeCancel=false&isInstantConfirm=false&roomNum=1&aNum_1=2&cNum_1=0&sellerId=&sellerIds=&ttid=seo.000000574&_output_charset=utf8&_input_charset=utf8',
            'cookie': 'lid=%E4%B8%80%E5%8F%AA%E5%8C%97%E8%BE%B0; enc=uh2XZ%2FdHLA5rsVfIj6WjDzK%2F3w7ljRu2d%2FHuryRJf2AB9j9IIweCn7U3rEkuHgxVsZ3r9EUvT%2FqHhbuw42MFuwPmruBB3mcYBJiTLdZjXwI%3D; cna=ZCiyGqkrPHQCATE0Y0qSEjyN; VISITED_HOTEL_TOKEN=f28571eb-188b-494f-97b0-99688939105d; t=b8ea9d1b47f4dcc66a925ea41758184d; tracknick=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; _tb_token_=ee10af0831d05; cookie2=1ea8631fc790242285e4643b91b0c3e7; chanelStat="NA=="; chanelStatExpire="2022-07-04 18:47:17"; xlly_s=1; dnk=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; uc1=cookie14=UoexND3h7Lf3LA%3D%3D&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&cookie16=V32FPkk%2FxXMk5UvIbNtImtMfJQ%3D%3D&existShop=false&cookie21=URm48syIYn73&pas=0; _l_g_=Ug%3D%3D; unb=2209062900905; cookie1=URotYFYuJbW70BuNizn%2FHZhV4QpheErchsEVTVH4pzE%3D; login=true; cookie17=UUphw2VT5UDzvsP%2BuQ%3D%3D; _nk_=%5Cu4E00%5Cu53EA%5Cu5317%5Cu8FB0; sgcookie=E100dNhXLqn0XZrTdyefgbJ9ztui7MgOEdcKsqLdsXtDk6lQBTW%2FAI8u09%2BCjcAQ9xoxnisvskc2JoF5eYMIYmja4tElLhtUHiC1gYjJK7HQfoI%3D; cancelledSubSites=empty; sg=%E8%BE%B053; csg=6ae461a3; x5sec=7b226873703b32223a226237313232626266363664323833616534353632356361383136373936363633434a584b2b355547454e43427963616f7149754451686f504d6a49774f5441324d6a6b774d446b774e5473784d4b3757344c76392f2f2f2f2f77453d222c22617365727665723b32223a226534633035613162303439363633623839333234656437653433316637633566434b6a4b2b355547454a372b32636e31744d757568414561447a49794d446b774e6a49354d4441354d4455374d54446a37507675417a6f43617a453d227d; tfstk=cBdABgTal0mchK_J8KHl_Xi8NuTAasaAjrsT6CaILJHa0oVT1sDvtBpUUx_NYi3R.; l=eBOcvWBRLohhQrshBO5aourza779iQRf1nVzaNbMiInca1oAwEKA3NCh8RjykdtjgtCFCexPUcfRbdeX8sUd_IiNWvaDcat-7xvO.; isg=BPT0KtN4Kpnvyr761VslfEM3xbJmzRi3sUzfco5XAX-z-ZdDtNxGR8z3eTEhNVAP',
            'x-requested-with': 'XMLHttpRequest'
        }
        proxies_list = [
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
        # 构建IP池防止爬取时封IP
        proxies = random.choice(proxies_list)
        response = requests.get(url, headers=headers, proxies=proxies).content.decode(
            encoding="gb18030", errors='ignore')
        # 获取响应，解码方式为gb18030
        print(url)
        print(response)
        contents = re.findall('"date":.*?","content":"(.*?)"', response)  # 正则清洗数据

        if contents == []:
            print(f"===酒店只有{j - 1}页数据！===")
            # 获取评论为空说明酒店没有数据或被反扒，直接跳出循环
            break
        # 有些酒店的数据很少
        for k in contents:
            if k != "":
                content_list.append(k)
        time.sleep(random.randint(1, 3))
        print(f"===第{j}页已爬取完毕！===")
    #     实时反馈爬取进度
    return content_list


if __name__ == '__main__':
    # cookie需要手动获取
    try:
        hotels_list = hotel_spider(2)
        # 爬取前两页酒店名称以及其对应的id
        # print(hotels_list)
        for i in hotels_list:
            print(f"正在爬取酒店{i['name']}")
            contents_list = content_spider(6, i['shid'])
            # 每个酒店爬取6页评论，一页15条
            content_lists = []
            for j in range(len(contents_list)):
                contents_list[j] = contents_list[j].replace("\\n", "")
                contents_list[j] = contents_list[j].replace(" ", "")
                # 清洗数据后并入content_lists
                content_lists.append(contents_list[j])
            with open("淘宝长沙地区酒店评论数据.txt", "a", encoding="utf-8")as file1:
                for k in content_lists:
                    file1.write(k)
                    file1.write("\n")
                # 将数据保存到txt文件中，检验清洗结果
                print(f"酒店{i['name']}已爬取完毕")
                time.sleep(random.randint(1, 3))
            #     设置等待时间，以免爬取速度过快导致被网站反爬
            time.sleep(random.randint(1, 3))
    except Exception as e:
        print(e)
        # 从txt文件中读取数据准备保存到mysql中

    with open("淘宝长沙地区酒店评论数据.txt", 'r', encoding='utf-8') as file2:
        con = file2.read()
        con1 = con.split("\n")
    #     从保存的txt文本数据中提取评论并以换行为分割点
    conn = pymysql.connect(host="localhost", port=3306, user="root", password="root",
                           database="python", charset="utf8")
    # 建立与数据库python的连接
    cur = conn.cursor()
    # cur.execute('use python1;')
    # 切换到名为python1的数据库中
    try:
        cur.execute('CREATE TABLE IF NOT EXISTS conm (id int Unsigned, content varchar(2000));')
        # 在数据库python1中构建表con(如果不存在)内容为ID以及长沙地区的酒店评论
        cur.execute('show tables')
        result = cur.fetchall()
        print(result)
        #     检验构建成果
    except:
        pass
        # 如果数据库已存在则跳过
    j = 1
    # 初始id为1
    for i in con1:
        print(j, i)
        cur.execute(f'INSERT INTO conm (id,content) VALUE ({j}, "{i}");')
        # 利用sql语句向MySQL中循环插入数据
        conn.commit()
        # 向数据库发送请求，不然数据不会存储到数据库中
        j += 1
        # 编号加1赋给下一个评论
    cur.close()
    conn.close()
        # 断开与数据库的连接
