# coding=utf-8
"""
@author:diwugu
@data:2019/5/25
@version:Python3.7
源码来源于网上，经过修改调整，框架比较清晰，而且提供三种网页解析提取方法选择，适合学习，而且可以尝试修改成一个招聘网站类的爬虫框架，
但是运行速度稍慢，待后期优化
"""
import xlwt
from bs4 import BeautifulSoup
import re
import time
from lxml import etree
from urllib import parse
import abc
import requests
from urllib.parse import quote

class ExeclUtils(object):
    @staticmethod
    def create_execl(sheet_name,row_titles):
        """
        sheet_name:表格名
        row_titles:行标题
        """
        f = xlwt.Workbook()
        sheet_info = f.add_sheet(sheet_name,cell_overwrite_ok=True)
        for i in range(0,len(row_titles)):
            sheet_info.write(0,i,row_titles[i])
        return f, sheet_info

    @staticmethod
    def write_execl(execl_file,execl_sheet,count,data,execl_name):
        """
        execl_file:文件对象
        execl_sheet:表格名
        count:数据插入到哪一行
        data:传入的数据 []类型
        execl_name:execl文件名
        """
        for j in range(len(data)):
            execl_sheet.write(count,j,data[j])
        execl_file.save(execl_name)

# abstract class
class Spider(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.row_title = ['标题', '待遇', '地区', '学历要求', '经验', '公司名称', '所属行业', '职位描述']
        sheet_name = "猎聘网"
        self.execl_f, self.sheet_info = ExeclUtils.create_execl(sheet_name, self.row_title)
        # add element in one data
        self.job_data = []
        # the data added start with 1
        self.count = 0

    def crawler_data(self):
        """
        crawler data
        """
        keyword = input('请输入查询职位:')
        keyword = quote(keyword)
        page = input('请输入爬取页数:')
        page = int(page)
        for i in range(0, page):
            """
            url = 'https://www.liepin.com/zhaopin/?industryType=&jobKind=&sortFlag=15&degradeFlag=0&industries=&salary=&compscale=&key={}' \
                  '&clean_condition=&headckid=4a4adb68b22970bd&d_pageSize=40&siTag=p_XzVCa5J0EfySMbVjghcw~fA9rXquZc5IkJpXC-Ycixw&d_headId' \
                  '=62ac45351cdd7a103ac7d50e1142b2a0&d_ckId=62ac45351cdd7a103ac7d50e1142b2a0&d_sfrom=search_fp&d_curPage=0&curPage={}'.format(keyword,i)
            """
            url = "https://www.liepin.com/zhaopin/?init=-1&headckid=4a4adb68b22970bd&fromSearchBtn=2&dqs=050090&salary=&sortFlag=15&" \
                  "degradeFlag=0&ckid=9ff79b8db0def83a&industryType=&jobKind=2&industries=&compscale=&key={}&clean_condition=" \
                  "&siTag=4N1aKWTD0M8alp0XOKF4Mg~rM22-1egSu-XqEHDTXvufA&d_sfrom=search_prime&d_ckId=065ef2eb67584c130bdd2db595fdb380&d_curPage=0" \
                  "&d_pageSize=40&d_headId=29234aed2604885a1e14d3118a201a70&curPage={}".format(keyword, i)
            self.request_job_list(url)
            time.sleep(1)

    def request_job_list(self, url):
        """
        get the job data by request url
        """
        try:
            headers = {
                'Referer': 'https://www.liepin.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }
            reponse = requests.get(url, headers=headers)
            # utf-8
            if reponse.status_code != 200:
                return
            self.parse_job_list(reponse.text)
        except Exception as e:
            # raise e
            if e == IndexError:
                pass
            else:
                print('request_job_list error : {}'.format(e))

    @abc.abstractmethod
    def parse_job_list(self, text):
        """
        parsing the data from the response
        """
        pass

    def request_job_details(self, url):
        """
        request thr job detail's url
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
            }
            response = requests.get(url, headers=headers);
            # utf-8
            if response.status_code != 200:
                return
            self.parse_job_details(response.text)
        except Exception as e:
            # raise e
            print('request_job_details error : {}'.format(e))

    @abc.abstractmethod
    def parse_job_details(self, text):
        """
        parsing the job details from text
        """
        pass

    def append(self, title, salary, region, degree, experience, name, industry):
        self.job_data.append(title)
        self.job_data.append(salary)
        self.job_data.append(region)
        self.job_data.append(degree)
        self.job_data.append(experience)
        self.job_data.append(name)
        self.job_data.append(industry)

    def data_clear(self):
        self.job_data = []

    def extract(self, data):
        return data[0] if len(data) > 0 else ""

#Xpath
class JobXpath(Spider):
    def __init__(self):
        super(JobXpath, self).__init__()

    def parse_job_list(self, text):
        try:
            selector = etree.HTML(text)
            divs = selector.xpath('//div[@class="sojob-item-main clearfix"]')
            for div in divs:
                title = self.extract(div.xpath('./div[1]/h3/@title'))
                data = self.extract(div.xpath('./div[1]/p[1]/@title'))
                data = data.split("_")
                salary = data[0]
                region = data[1]
                degree = data[2]
                experience = data[3]
                name = self.extract(div.xpath('./div[2]/p[1]/a/text()'))
                industry = self.extract(div.xpath('./div[2]/p[2]/span/a/text()'))
                href = self.extract(div.xpath('./div[1]/h3/a/@href'))

                self.append(title, salary, region, degree,experience, name, industry)
                print(self.job_data)
                self.request_job_details(parse.urljoin('https://www.liepin.com', href))
                time.sleep(1)
        except Exception as e:
            print('parse_job_list error : {}'.format(e))

    def parse_job_details(self, text):
        try:
            selector = etree.HTML(text)
            data = selector.xpath('//div[@class="about-position"]/div[3]')
            # strip()不管用？
            detail = data[0].xpath('string(.)').replace(" ", "")
            if detail is "":
                self.job_data.append("职位无介绍")
            else:
                self.job_data.append(detail)
            self.count += 1
            ExeclUtils.write_execl(self.execl_f, self.sheet_info, self.count, self.job_data, "猎聘网_xpath.xlsx")
            print("crawel ", self.count, "条数据")
            self.data_clear()
        except Exception as e:
            print('parse_job_details error : {}'.format(e))

# bs
class JobBs(Spider):
    def __init__(self):
        super(JobBs, self).__init__()

    def parse_job_list(self, text):
        try:
            soup = BeautifulSoup(text, 'lxml')
            divs = soup.select('.sojob-item-main.clearfix')
            for div in divs:
                title = self.extract(div.select('.job-info > h3'))['title']
                href = self.extract(div.select('.job-info > h3 a'))['href']

                result = self.extract(div.select('.job-info > p'))
                if hasattr(result, 'title'):
                    result = result['title'].split('_')
                else:
                    # 虽然不会出现
                    result = ['', '', '']
                salary = result[0]
                region = result[1]
                degree = result[2]
                experience = result[3]
                name = self.extract(div.select('.company-info.nohover > p a')).string
                industry = self.extract(div.select('.company-info.nohover .field-financing span a')).string
                self.append(title, salary, region, degree, experience, name, industry)
                print(self.job_data)
                self.request_job_details(parse.urljoin('https://www.liepin.com', href))
                time.sleep(1)
        except Exception as e:
            print("parse_job_list error :", str(e))

    def parse_job_details(self, text):
        try:
            soup2 = BeautifulSoup(text, 'lxml')
            detail = soup2.select('.content.content-word')
            if detail:
                self.job_data.append(detail[0].get_text())
            else:
                self.job_data.append("暂无信息")
            self.count += 1
            ExeclUtils.write_execl(self.execl_f, self.sheet_info, self.count, self.job_data, "猎聘网_bs.xlsx")
            print("crawel ", self.count, "条数据")
            self.data_clear()
        except Exception as e:
            print("parse_job_details error : ", str(e))


# re
class JobRe(Spider):
    def __init__(self):
        super(JobRe, self).__init__()

    def parse_job_list(self, text):
        try:
            pattern = re.compile('<div class="job-info">.*?<h3.*?title="(.*?)">.*?<a href="(.*?)".*?title="(.*?)">.*?'
                                 '<p class="company-name">.*?>(.*?)</a>.*?<p class="field-financing">.*?target="_blank">'
                                 '(.*?)</a>.*?</span>', re.S)
            datas = re.findall(pattern, text)
            for data in datas:
                title = data[0]
                href = data[1]
                result = data[2].split('_')
                salary = result[0]
                region = result[1]
                degree = result[2]
                experience = result[3]
                name = data[3]
                industry = data[4]
                self.append(title, salary, region, degree,
                            experience, name, industry)
                print(self.job_data)
                self.request_job_details(parse.urljoin(
                    'https://www.liepin.com', href))
                time.sleep(1)
        except Exception as e:
            print("re parse_job_list error : ", str(e))

    def parse_job_details(self, text):
        try:
            pattern = re.compile('<div class="content content-word">(.*?)</div>.*?<div class="job-item main.*?">', re.S)
            text = re.search(pattern, text)
            detail = re.sub(re.compile('<[^>]+>', re.S), '', text.group(1))
            if detail:
                self.job_data.append(detail)
            else:
                self.job_data.append("暂无职位信息")
            self.count += 1
            ExeclUtils.write_execl(self.execl_f, self.sheet_info, self.count, self.job_data, "猎聘网_re.xlsx")
            print("crawel ", self.count, "条数据")
            self.data_clear()
        except Exception as e:
            print("re parse_job_list error : ", str(e))

class Main():
    @staticmethod
    def select_type():
        typemethod = input('请输入爬虫类型:\n1.xpath\n2.BeatuifulSoup4\n3.re\n')
        typemethod = int(typemethod)
        print("您已输入 ", typemethod)
        if typemethod == 1:
            print("开始xpath爬取数据....")
            xpath = JobXpath()
            xpath.crawler_data()
        elif typemethod == 2:
            print("开始bs4爬取数据....")
            bs = JobBs()
            bs.crawler_data()
        else:
            print("开始re爬取数据")
            remethod = JobRe()
            remethod.crawler_data()
        print("爬取完毕")


if __name__ == '__main__':

    Main.select_type()
