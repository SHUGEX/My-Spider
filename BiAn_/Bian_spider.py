import asyncio
import aiohttp
import random
from fake_useragent import FakeUserAgent
from lxml import etree


class Bian_Spider:

    def __init__(self, max_page):
        self.max_page = max_page                    # 爬取图片数量
        self.url = "http://pic.netbian.com/"        # 初始url
        self.user_agent = FakeUserAgent().random    # User-Agent 池
        self.CONCURRENCY = 100                      # 并发量控制
        self.semaphore = asyncio.Semaphore(self.CONCURRENCY)
        self.page = 1                               # 翻页
        self.headers_ = {
            'User-Agent': FakeUserAgent().random,
            "Cookie": "__yjs_duid=1_bb9a9216ef8b70d9caa44759f0eaa3431658747201780; Hm_lvt_c59f2e992a863c2744e1ba985abaea6c=1658747216; Hm_lpvt_c59f2e992a863c2744e1ba985abaea6c=1658750521",
            "Referer": "http://pic.netbian.com/"
        }

    async def SendRequest_Index(self):
        """发送请求，获取当前页面响应信息"""
        async with self.semaphore:
            await asyncio.sleep(random.randint(0, 2))
            async with aiohttp.ClientSession() as session:
                async with await session.get(self.url, headers=self.headers_) as response_:
                    str_data = await response_.text()
                    return str_data

    async def Get_img_url(self):
        """解析图片的标题以及所在的url地址"""
        index_text = await self.SendRequest_Index()

        await asyncio.sleep(random.randint(0, 2))
        tree = etree.HTML(index_text)

        img_titles_ = tree.xpath('//ul[@class="clearfix"]/li/a/b/text()')  # 图片名称解析

        img_urls_ = tree.xpath('//ul[@class="clearfix"]/li/a//img/@src')   # 图片url解析
        for i in range(len(img_urls_)):
            img_urls_[i] = "http://pic.netbian.com/" + img_urls_[i]  # 将不完整的url拼接成完整的url

        res = dict(zip(img_titles_, img_urls_))    # 合成为字典{"图片名称":"图片url" ....}

        return res

    async def download_img(self, url):
        """向图片所在的url发起请求，以获取图片的字节(二进制)数据"""
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with await session.get(url, headers=self.headers_) as response:
                    content_ = await response.read()

                    return content_

    async def Save_Img(self):
        """保存所有图片"""
        dic_img_data = await self.Get_img_url()

        await asyncio.sleep(random.randint(0, 2))
        for k, v in dic_img_data.items():

            print(f"图片\"{k}\" 下载中...\n")
            content_ = await self.download_img(v)

            with open('Pictures/' + k + '.jpg', 'wb') as f:
                f.write(content_)

        # 当上方循环结束，意味着一页的图片全部爬取完毕

        print(f"\n\033[1;36m第{self.page}页爬取完毕！\n\t\t已下载{self.page * 20}张照片！\n\033[0m")

        self.page += 1
        self.url = f"http://pic.netbian.com/index_{self.page}.html"
        if self.page <= self.max_page:
            return await self.Save_Img()


if __name__ == '__main__':
    page = input("请输入爬取图片数量：")

    while not (page.isdigit() and int(page) >= 20):
        print("请输入20的倍数！")
        page = input("请输入爬取图片数量：")

    page = int(int(page) / 20)

    Spider = Bian_Spider(int(page))

    task = asyncio.ensure_future(Spider.Save_Img())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
