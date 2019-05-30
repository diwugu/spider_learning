# _author:Danny
# date:2019-05-30
# 该段代码主要查询深圳地区（网站编码为040000），后续可在url内设置代码更改为变量，自由输入选定区域

import csv
from urllib.parse import quote
import requests
from lxml import etree
import time

def get_url(keyword,page):
    try:
        keyword = quote(keyword)
        url = "https://search.51job.com/list/040000,000000,0000,00,9,99,{},2,{}.html".format(keyword,page)
        return url
    except:
        print("获取不到链接，已处理")

def pase_page(keyword):
    headers = {
        "cache-control": "no-cache",
        "postman-token": "72a56deb-825e-3ac3-dd61-4f77c4cbb4d8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
    }
    try:
        for page in range(2):
            url = get_url(keyword,page)
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.content.decode('gbk'))  # 解码成gbk后输出，请求的是gbk，但是python默认的是
            lists = html.xpath("//div[@id='resultList']//div[@class='el']")
            for list in lists:
                item = {}
                item["职位"] = "".join(list.xpath("./p/span/a/text()")).replace('\r\n', '').replace(' ', '')
                item["公司名称"] = "".join(list.xpath("./span[@class='t2']/a/text()")).replace('\r\n', '').replace(' ', '')
                item["职位链接"] = "".join(list.xpath("//a[@onmousedown=""]/@href")).replace('\r\n', '').replace(' ', '')
                item["工作地点"] = "".join(list.xpath("./span[@class='t3']/text()")).replace('\r\n', '').replace(' ', '')
                item["薪资"] = "".join(list.xpath("./span[@class='t4']/text()")).replace('\r\n', '').replace(' ', '')
                item["发布时间"] = "".join(list.xpath("./span[@class='t5']/text()")).replace('\r\n', '').replace(' ', '')
                yield item
            print("已爬取完成第%d页",page)
            time.sleep(1)
    except:
        print("返回数据异常，已处理")

def save_excel(keyword):
    try:
        header = ['职位', '公司名称', '职位链接','工作地点', '薪资', '发布时间']
        with open(keyword + '前程无忧职位信息.csv', 'w', newline='') as f:  # w是写入
            # 标头在这里传入，作为第一行数据
            writer = csv.DictWriter(f, header)
            writer.writeheader()
        for i in pase_page(keyword):
            item = i
            header = ['职位', '公司名称', '职位链接','工作地点', '薪资', '发布时间']
            with open(keyword + '前程无忧职位信息.csv', 'a', newline='') as f:  # a是追加
                writer = csv.DictWriter(f, header)
                writer.writerow(item)
                # print(item)
    except:
        print("保存数据异常，已处理")


if __name__ == '__main__':
    keyword = input('请输入要爬取的职位：')
    save_excel(keyword)

