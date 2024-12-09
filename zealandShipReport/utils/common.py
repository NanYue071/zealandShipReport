#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime
import re


def base62_decode(string):
    """
    base
    """
    alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    string = str(string)
    num = 0
    idx = 0
    for char in string:
        power = (len(string) - (idx + 1))
        num += alphabet.index(char) * (len(alphabet) ** power)
        idx += 1

    return num


def reverse_cut_to_length(content, code_func, cut_num=4, fill_num=7):
    """
    url to mid
    """
    content = str(content)
    cut_list = [content[i - cut_num if i >= cut_num else 0:i] for i in range(len(content), 0, (-1 * cut_num))]
    cut_list.reverse()
    result = []
    for i, item in enumerate(cut_list):
        s = str(code_func(item))
        if i > 0 and len(s) < fill_num:
            s = (fill_num - len(s)) * '0' + s
        result.append(s)
    return ''.join(result)


def url_to_mid(url: str):
    """>>> url_to_mid('z0JH2lOMb')
    3501756485200075
    """
    result = reverse_cut_to_length(url, base62_decode)
    return int(result)


def parse_time(str_time):
    # 解析日期字符串，指定输入格式
    date_obj = datetime.strptime(str_time, "%d/%m/%Y %H:%M")

    # 格式化为所需的输出格式
    formatted_date = date_obj.strftime("%Y/%m/%d")
    return formatted_date


def parse_date(str_time):
    # 解析日期字符串，指定输入格式
    date_obj = datetime.strptime(str_time, "%d/%m/%Y")

    # 格式化为所需的输出格式
    formatted_date = date_obj.strftime("%Y/%m/%d")
    return formatted_date


# 时间戳转换为日期
def timestamp_to_date(str_time):
    # 1. 使用正则表达式去掉转义字符 \/ 和 /Date()，提取时间戳
    match = re.search(r"\/Date\((\d+)\)\/", str_time)
    if match:
        timestamp = int(match.group(1))

        # 2. 将时间戳从毫秒转换为秒
        timestamp = timestamp / 1000

        # 3. 转换为标准日期
        date_time = datetime.fromtimestamp(timestamp)

        # 格式化为所需的输出格式
        formatted_date = date_time.strftime("%Y/%m/%d")
        return formatted_date
