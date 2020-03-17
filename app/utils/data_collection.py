# coding=utf-8
"""
获取各种请求的调度管理中心
"""
import importlib
import re
from datetime import datetime
from datetime import timedelta
# 单列测试导包依赖
# import sys
# import os
# BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# BASE = 'D:\\下载\\微信机器人\\wxrobot-master'
# sys.path.insert(0, BASE_DIR)
# sys.path.insert(0, BASE)
# print(sys.path)

from app import config
from app.control.onewords.acib import get_one_words
# from app.control.calendar.sojson_calendar import get_sojson_calendar
from app.control.calendar.rt_calendar import get_rtcalendar
from app.control.horoscope.xzw_horescope import get_today_horoscope
from app.utils.common import (get_constellation_name)
# from app.control.weather.rtweather import get_today_weather
from app.control.weather.sojson import get_sojson_weather
from app.control.rubbish.atoolbox_rubbish import get_atoolbox_rubbish
from app.control.moviebox.maoyan_movie_box import get_maoyan_movie_box
from app.control.airquality.air_quality_aqicn import get_air_quality


__all__ = [
    'get_dictum_info', 'get_weather_info', 'get_bot_info',
    'get_diff_time', 'get_constellation_info', 'get_calendar_info',
    'DICTUM_NAME_DICT', 'BOT_NAME_DICT'
]

DICTUM_NAME_DICT = {
    1: 'wufazhuce', 2: 'acib', 3: 'lovelive', 4: 'hitokoto',
    5: 'rtjokes', 6: 'juzimi', 7: 'caihongpi'
}
BOT_NAME_DICT = {
    1: 'tuling123', 2: 'yigeai', 3: 'qingyunke', 4: 'qq_nlpchat',
    5: 'tian_robot', 6: 'ruyiai', 7: 'ownthink_robot'
}
# 用于星座的正则表达式
BIRTHDAY_COMPILE = re.compile(
    r'\-?(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$')


def get_rubbish(key=''):
    """
    垃圾分类接口
    :param key:
    :return: _type(分类结果), return_list(垃圾分类列表), other(相关垃圾分类)
    """
    if key != '':
        data = get_atoolbox_rubbish(key)
        res = "\n分类结果:" + data[0] + "\n相关垃圾:"
        for rubbish in data[1]:
            # print(rubbish)
            res = res + rubbish['name'] + '->' + rubbish['type'] + '；'
        return res


def get_movie_box(key=''):
    """
     获取特定日期的实时票房日期
    :param date: str 日期 格式 yyyyMMdd
    :param is_expired
    :rtype str
    """
    if key != '':
        return get_maoyan_movie_box(key)


def get_dictum_info(channel=''):
    """
    获取每日一句。
    channel:格言渠道（1 : ONE●一个，2 : 词霸（每日英语，双语）3: 土味情话 4 : 一言，5：笑话，6 民国情书,7彩虹屁)
    :return:str
    """
    if channel != '':
        source = DICTUM_NAME_DICT.get(channel, '')
        if source:
            addon = importlib.import_module(
                'app.control.onewords.' + source, __package__)
            dictum = addon.get_one_words()
            # print(dictum)
            return dictum
    else:
        return get_one_words()


def get_weather_info(cityname, is_tomorrow=False):
    """
    获取天气
    :param cityname:str,城市名称
    :return: str,天气情况
    """
    if not cityname:
        return '-1'
    # return get_today_weather(cityname)
    return get_sojson_weather(cityname, is_tomorrow)


def get_diff_time(start_date, start_msg=''):
    """
    # 在一起，一共多少天了; 或认识，接触了多少天了
    :param start_date:str,日期
    :return: str,eg（宝贝这是我们在一起的第 111 天。）
    """
    if not start_date:
        return None
    start_date = ('-').join(start_date.split('.'))
    rdate = r'^[12]\d{3}[ \/\-](?:0?[1-9]|1[012])[ \/\-](?:0?[1-9]|[12][0-9]|3[01])$'
    start_date = start_date.strip()
    if not re.search(rdate, start_date):
        print('日期填写出错..')
        return
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    day_delta = (datetime.now() - start_datetime).days + 1
    if start_msg and start_msg.count('{}') == 1:
        delta_msg = start_msg.format(day_delta)
    else:
        delta_msg = '您好，这是我们认识的第 {} 天。'.format(day_delta)
    return delta_msg


def get_constellation_info(birthday_str, is_tomorrow=False):
    """
    获取星座运势
    :param birthday_str:  "10-12" 或  "1980-01-08" 或 星座名
    :return:
    """
    if not birthday_str:
        return
    const_name = get_constellation_name(birthday_str)
    if not const_name:
        print('星座名填写错误')
        return
    return get_today_horoscope(const_name, is_tomorrow)


def get_calendar_info(calendar=True, is_tomorrow=False, _date=''):
    """ 获取万年历 """
    if not calendar:
        return None
    if not is_tomorrow:
        date = datetime.now().strftime('%Y%m%d')
    else:
        date = datetime.now().strftime('%Y%m%d')
    if not _date:
        if '-' in _date:
            date = ('').join(_date.split('-'))
        else:
            date = _date
    return get_rtcalendar(date)


def get_airquality(cityname=''):
    """
    通过城市名获取空气质量
    :param city: 城市
    :return:
    """
    if cityname != '':
        return get_air_quality(cityname)


if __name__ == '__main__':
    print(
        get_rubbish('苹果'),
        get_dictum_info(5),
        get_weather_info('南昌', is_tomorrow=False),
        get_diff_time('2017-10-18', start_msg=''),
        get_constellation_info('1-27', is_tomorrow=False),
        get_calendar_info(calendar=True, is_tomorrow=False, _date='20200111'))
    pass


# def get_bot_info(message, userId=''):
#     """
#     跟机器人互动
#     # 优先获取图灵机器人API的回复，但失效时，会使用青云客智能聊天机器人API(过时)
#     :param message:str, 发送的话
#     :param userId: str, 好友的uid，作为请求的唯一标识。
#     :return:str, 机器人回复的话。
#     """

#     channel = config.get('auto_reply_info').get('bot_channel', 7)
#     source = BOT_NAME_DICT.get(channel, 'ownthink_robot')
#     # print(source)
#     if source:
#         addon = importlib.import_module(
#             'app.control.bot.' + source, __package__)
#         reply_msg = addon.get_auto_reply(message, userId)
#         return reply_msg
#     # reply_msg = get_tuling123(message)
#     # if not reply_msg:
#     #     # reply_msg = get_qingyunke(message)
#     #     reply_msg = get_yigeai(message)

#     return None
