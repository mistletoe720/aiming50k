#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/20 19:40
# @Author  : Qiaozhi

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random
from requests.exceptions import RequestException


def get_one_page(url):
    """
    获取单独一个页面
    :param url: 网址
    :return: 解析后的beautifulsoup类型文件
    """
    try:
        # 解析boss直聘网址必须带zp_stoken，否则request失败
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'cookie': '__zp_stoken__=2e9cMtsy%2FjxGQiNDvrr7W74JTW1CE%2BWbVtmUjZYEURcotrAQBmNSp4Tfb8FldCreRURAeFoVrpwuZb6K4mI9CLCD2VtlZbjDq50mpijnJqVpdR8SH%2BS89joQwqP1EZO73zFT'
        }
        res = requests.get(url, headers=headers)
        # 使用beautifulsoup lxml格式解析网页
        soup = BeautifulSoup(res.text, 'lxml')
        if res.status_code == 200:
            return soup
    except RequestException:
        print('Attention!!!Request Error!!!')
        return None


def parse_one_page(soup):
    """
    把所需要的数据单独从soup中提取出来
    :param soup: 解析后的beautifulsoup类型文件
    :return:
    """
    # 单独提取每一个职位的内容
    jobs = soup.select('div.job-list > ul > li > div.job-primary')
    # part = jobs[1]
    for part in jobs:
        # 职位名称
        title = part.find(class_="job-name").text
        # 职位薪酬
        salary = part.find(class_="red").text
        # 工作地点
        location = part.find(class_="job-area").text
        # 职位学历要求
        raw_require = part.find(class_="job-limit clearfix").p
        require = re.match('<p>(.*?)<em class="vline"></em>(.*?)</p>', str(raw_require))
        exper = require.group(1)
        edu = require.group(2)
        # 公司名
        company = part.find(class_="company-text").a.text
        # 公司基本资料
        raw_info = part.find(class_="company-text").p
        info = re.match('<p>(.*?)<em class="vline"></em>(.*?)<em class="vline"></em>(.*?)</p>', str(raw_info))
        indus = info.group(1)
        cap = info.group(2)
        ppl = info.group(3)
        # 职位所需要的技能标签
        ability = ''
        for i in part.find_all('span', class_="tag-item"):
            ability = ability + ',' + i.text
        abi = ability[1:]
        # 数据写入excel
        writer.writerow((title, company, location, salary, exper, edu, abi, indus, cap, ppl))
        print(title, company,  location, salary, exper, edu, abi, indus, cap, ppl)
        time.sleep(6)


def main():
    """
    主要执行函数
    :return:
    """
    # URL取的是薪资高于50k的数据
    urls = ['https://www.zhipin.com/c101280100/y_8/?page={0}&ka=page-{1}'.format(i, i) for i in range(1, 30)]
    for url in urls:
        html = get_one_page(url)
        parse_one_page(html)


if __name__ == '__main__':
    # 创建了多个数据文件以备不时之需
    file = open('./data/Boss直聘数据2.csv', 'wt', newline='', encoding='UTF-8')
    writer = csv.writer(file)
    writer.writerow(('职位', '公司简称', '工作地点', '薪资', '工作经验', '学历', '技能标签', '行业', '融资状况', '公司人数'))
    main()
