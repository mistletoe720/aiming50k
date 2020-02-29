#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/2/21 18:21
# @Author  : Qiaozhi


import pandas as pd
import os
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
from wordcloud import WordCloud
from matplotlib.font_manager import fontManager
import jieba

# f = open('./jieba/userdict.txt', 'rb')
# f = open('./data/Boss直聘数据2.csv', 'rb')
# f.close()
# 读取个性词库
jieba.load_userdict('./jieba/userdict.txt')

# 更改画图字体以免乱码
mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']

# 定义文件路径变量
path = ['./data/Boss直聘数据{0}.csv'.format(i) for i in range (0,3)]
header = ['title', 'company',  'location', 'salary', 'exper', 'edu', 'abi', 'indus', 'cap', 'ppl']


def load_data(filepath):
    """
    读取文件，合并，最后去重
    :param filepath: 文件路径
    :return: dataframe格式的数据
    """
    file = pd.DataFrame(columns=header)
    for p in filepath:
        df = pd.read_csv(p, header=0, names=header)
        file = pd.concat([file, df], axis=0)
    file.drop_duplicates(inplace=True)
    return file


# 处理薪资字段
def salary(word1):
    """
    薪资字段格式标准化
    :param word1:
    :return:
    """
    post = word1.find('K')
    clear = word1[:post+1]
    return clear

def b_salary(word2):
    """
    抓取最低工资
    :param word2:
    :return:
    """
    post = word2.find('-')
    bottom = word2[:post]
    return bottom

def t_salary(word3):
    """
    抓取最高工资
    :param word3:
    :return:
    """
    post1 = word3.find('-')
    post2 = word3.find('K')
    top = word3[post1+1:post2]
    return top

def reform_salary(df):
    """
    处理数据中心薪资字段数据
    :param df:
    :return:
    """
    # 计算平均工资
    # df['clear_salary'] = df['salary'].apply(salary)
    df['low_salary'] = df['salary'].apply(b_salary).astype(int)
    df['high_salary'] = df['salary'].apply(t_salary).astype(int)
    df['avg_salary'] = df.apply(lambda x: (x.low_salary+x.high_salary)/2, axis=1)
    # df['avg_salary'].value_counts().plot.bar()
    print(df['avg_salary'].describe())

    # 重新对工资进行分箱，因为原来工资范围参差不齐
    bins = [0, 45, 55, 65, 100]
    level = ['35-45', '45-55', '55-65', '65-100']
    df['level'] = pd.cut(df['avg_salary'], bins=bins, labels=level)
    df_level = df.groupby(['company','level']).avg_salary.count().unstack()
    # 画图看看哪家高工资职位多
    ax = df_level.plot.bar(stacked=True, figsize=(14,6))
    plt.show()
    # df_level_prop = df_level.apply(lambda x:x/x.sum(), axis=1)
    # ax = df_level_prop.plot.bar(stacked=True, figsize=(14,6))

    # 去除"35-45"一级后，重新画图再看看
    df_real_level = df_level.drop('35-45', axis=1)
    bx = df_real_level.plot.bar(stacked=True, figsize=(14,6))
    plt.show()


def reform_abi(df):
    """
    处理技能标签字段，词云画图
    :param df:
    :return:
    """
    # 拆分字段并计数
    word = df['abi'].dropna().str.split(',').apply(pd.value_counts)
    word_counts = word.unstack().dropna().reset_index().groupby('level_0').count()
    word_counts.index = word_counts.index.str.replace("'", "")
    # 词云画图
    wordcloud = WordCloud(font_path='C:\Windows\Fonts\simhei.ttf',
                          width=900, height=400, background_color= 'white')
    f, axs = plt.subplots(figsize=(15,15))
    wordcloud.fit_words(word_counts.level_1)
    axs = plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()
    # 技能平均工资作图
    # skill = pd.concat([word, df['avg_salary']], axis=1)
    # skill2 = pd.DataFrame(word.values.T, index=word.columns, columns=word.index)
    # skill3 = skill2.mul(df['avg_salary'])
    # 去掉一些无用的词
    # skill3.drop(['IT','互联网','文档'], inplace=True)
    # 作图
    # skill3.mean(1).sort_values(ascending=False).head(15).plot.bar()
    # plt.show()


def reform_title(df):
    """
    jieba分词职位分析
    :param df:
    :return:
    """
    # 遍历分词
    # for i in data['title']:
    #     seg_list = jieba.cut(i)
    #     print(", ".join(seg_list))
    # 用apply处理jieba.cut
    data['segtitle'] = data['title'].apply(jieba.cut).apply(list).apply(','.join)
    # 脏数据稍微处理
    data['segcleartitle'] = data['segtitle'].replace([' ','-','/','）','（','【','】'],'',regex=True).\
        replace(['\(','\)','，'],'',regex=True).apply(str.upper)
    # 计数
    seg = data['segcleartitle'].str.split(',').apply(pd.value_counts)
    seg.drop(['','工程师','开发','广州','微信','腾讯','杭州'],axis=1, inplace=True)
    seg_counts = seg.unstack().dropna().reset_index().groupby('level_0').count().sort_values('level_1',ascending=False)
    # 词云画图
    word_cloud = WordCloud(font_path='C:\Windows\Fonts\simhei.ttf',
                          width=900, height=400, background_color= 'white')
    f, axs = plt.subplots(figsize=(15,15))
    word_cloud.fit_words(seg_counts.level_1)
    axs = plt.imshow(word_cloud)
    plt.axis('off')
    plt.show()
    # 职位名称平均工资图
    # title = pd.concat([seg, df['avg_salary']], axis=1)
    # title2 = pd.DataFrame(seg.values.T, index=seg.columns, columns=seg.index)
    # title3 = title2.mul(df['avg_salary'])
    # 去掉一些无用的词
    # title3.drop([], inplace=True)
    # 作图
    # title3.mean(1).sort_values(ascending=False).head(15).plot.bar()
    # plt.show()


if __name__ == '__main__':
    data = load_data(path)
    # 发布高于50K薪资的公司频率图
    data['company'].value_counts().plot.bar()
    plt.show()
    reform_salary(data)
    reform_abi(data)
    reform_title(data)
