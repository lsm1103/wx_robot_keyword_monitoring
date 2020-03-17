import hashlib
import time
import random
import string
import requests
import json
import re
from wxpy import *
from urllib import parse
from app import config
from app.utils.common import (md5_encode)


def auto_reply(msg):
    """回复消息，并返回答复文本"""
    if config.bot_channel == 'tuling':
        return get_tuling_robot(msg).do_reply(msg)
    """回复消息，并返回答复文本"""
    if config.bot_channel == 'ownthink':
        back_text = get_ownthink_robot(msg)
        return msg.reply(back_text)
    """回复消息，并返回答复文本"""
    if config.bot_channel == 'tuling':
        back_text = get_tuling_robot(msg)
        return msg.reply(back_text)


def get_tuling_robot(msg):
    """
    免费申请图灵机器人，获取api_key
    图灵机器人免费申请地址 http://www.tuling123.com
    apikey = '7c8cdb56b0dc4450a8deef30a496bd4c'
    """
    tuling = Tuling(api_key=config.robot_list['tuling']['api_key'])
    return tuling


def get_ownthink_robot(msg):
    """
    思知机器人，接口地址:<https://www.ownthink.com/>
    https://api.ownthink.com/bot?appid=xiaosi&userid=msg.chat.puid&spoken=姚明多高啊？
    :param msg.text: 请求的话
    :param msg.chat.puid: 用户标识
    :return:
    """
    try:
        # import config
        info = config.robot_list['ownthink']
        app_key = info['api_key']
        if not re.findall(r'^[0-9a-z]{20,}$', app_key):  # 验证 app_key 是否有效
            app_key = ''

        params = {
            'appid': app_key,
            'userid': md5_encode(msg.chat.puid),
            'spoken': msg.text
        }
        url = 'https://api.ownthink.com/bot'
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            # print(resp.text)
            content_dict = resp.json()
            if content_dict['message'] == 'success':
                data = content_dict['data']
                if data['type'] == 5000:
                    return data['info']['msg.text']
                else:
                    print('返回的数据不是文本数据！')
            else:
                print('思知机器人获取数据失败:{}'.format(content_dict['msg']))

        print('获取数据失败')
        return None
    except Exception as exception:
        print(str(exception))


def get_nlp_textchat(msg):
    """
    智能闲聊（腾讯）<https://ai.qq.com/product/nlpchat.shtml>
    接口文档：<https://ai.qq.com/doc/nlpchat.shtml>
    :param msg.text: 请求的话
    :param msg.chat.puid: 用户标识
    :return: str
    """
    URL = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat'

    try:
        info = config.robot_list['qqnlpchat']
        app_id = info['app_id']
        app_key = info['app_key']
        if not app_id or not app_key:
            print('app_id 或 app_key 为空，请求失败')
            return

        # 产生随机字符串
        nonce_str = ''.join(random.sample(
            string.ascii_letters + string.digits, random.randint(10, 16)))
        time_stamp = int(time.time())  # 时间戳
        params = {
            'app_id': app_id,  # 应用标识
            'time_stamp': time_stamp,  # 请求时间戳（秒级）
            'nonce_str': nonce_str,  # 随机字符串
            'session': md5_encode(msg.chat.puid),  # 会话标识
            'question': msg.text  # 用户输入的聊天内容
        }
        # 签名信息
        params['sign'] = getReqSign(params, app_key)
        resp = requests.get(URL, params=params)
        if resp.status_code == 200:
            # print(resp.text)
            content_dict = resp.json()
            if content_dict['ret'] == 0:
                data_dict = content_dict['data']
                return data_dict['answer']
            print('智能闲聊 获取数据失败:{}'.format(content_dict['msg']))
            return None
    except Exception as exception:
        print(str(exception))


def getReqSign(parser, app_key):
    '''
    获取请求签名，接口鉴权 https://ai.qq.com/doc/auth.shtml
    1.将 <key, value> 请求参数对按 key 进行字典升序排序，得到有序的参数对列表 N
    2.将列表 N 中的参数对按 URL 键值对的格式拼接成字符串，得到字符串 T（如：key1=value1&key2=value2），
        URL 键值拼接过程 value 部分需要 URL 编码，URL 编码算法用大写字母，例如 %E8，而不是小写 %e8
    3.将应用密钥以 app_key 为键名，组成 URL 键值拼接到字符串 T 末尾，得到字符串 S（如：key1=value1&key2=value2&app_key = 密钥)
    4.对字符串 S 进行 MD5 运算，将得到的 MD5 值所有字符转换成大写，得到接口请求签名
    :param parser: dect
    :param app_key: str
    :return: str,签名
    '''
    params = sorted(parser.items())
    uri_str = parse.urlencode(params, encoding="UTF-8")
    sign_str = '{}&app_key={}'.format(uri_str, app_key)
    # print('sign =', sign_str.strip())
    hash_md5 = hashlib.md5(sign_str.encode("UTF-8"))
    return hash_md5.hexdigest().upper()


if __name__ == '__main__':
    apikey = 'c6c83055db1a45c1b54ad5f125096a50'
    api_url = 'http://www.tuling123.com/openapi/api'
    data = {'key': apikey, 'info': '你好'}
    req = requests.post(api_url, data=data).text
    replys = json.loads(req)['text']
    print(req, replys)
