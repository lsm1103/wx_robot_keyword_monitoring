# 好友功能
import re
import robot_tool
from app import config
import time
import random
from app.utils.data_collection import (
    get_rubbish,
    get_dictum_info,
    get_weather_info,
    get_diff_time,
    get_constellation_info,
    get_calendar_info,
    get_movie_box,
    get_airquality
)


def auto_accept_friends(msg):
    """自动接受好友"""
    # 接受好友请求
    new_friend = msg.card.accept()
    # 向新的好友发送消息
    new_friend.send(config.new_friend_first_greeting)


def auto_reply(msg, type, key='keyword_data'):
    """
    关键字回复 or 机器人回复
    msg.chat.name 当前聊天对象【好友/群聊】的昵称/备注
    """
    print('auto_reply', msg.text, msg.chat.puid)
    if type == 'zy':
        for ci in config.keyword[ key ]:
            if ci in msg.text:
                # time.sleep(0.4)  # 休眠一秒保安全，想更快可以直接注释。
                msg.reply('杭州首选【{0}】专业高效，出证速度快，联系电话：130-5682-2334！'.format(ci))
        if '你是' in msg.text or '你叫啥' in msg.text:
            msg.reply('杭州首选企业管理有限公司')
    else:
        print("收到一条群信息：", ci, msg)
        keyword_reply(msg, type)
        # keyword_reply(msg, type) or robot_reply(msg)


def check_key_work(msg, res_text):
    '''
    确保关键词服务正确运行
    msg:聊天对象
    right_key：正确关键词
    res_text：回复的话
    '''
    type = msg.text.split('-')[0]
    text = msg.text.split('-')[1]
    print('check_key_work', text, type, res_text, len(text))
    if len(text) > 0:
        try:
            if type == '天气':
                res = get_weather_info(text)
            if type == '票房':
                res = get_movie_box(text)
            if type == '垃圾分类':
                res = get_rubbish(text)
            if type == '万年历':
                res = get_calendar_info(_date=text)
            if type == '空气质量':
                res = get_airquality(text)
            if type == '星座':
                res = get_constellation_info(text)
            if type == '一句话':
                res = get_dictum_info(text)
            if type == '时间计算':
                res = get_diff_time(text)
            # if type == '快递':
            #     res = get_kuaidi_info()
        except Exception as e:
            print(e)
            return msg.reply('{}，格式：{}'.format(e, res_text))
        else:
            print(res)
            return msg.reply(res)
    else:
        return msg.reply('未输入，格式：{}'.format(res_text))


def keyword_reply(msg, type):
    """关键字回复"""
    print('关键字回复', msg)
    try:
        ci = msg.text.split('-')[0]
    except Exception as e:
        print(e)
    else:
        if ci in config.search_dict.keys():
            return check_key_work(msg, config.search_dict[ci])
        else:
            return robot_reply(msg)


def robot_reply(msg):
    """机器人回复"""
    time.sleep(0.2)  # 休眠一秒，保安全。想更快的，可以直接注释。
    robot_tool.auto_reply(msg)


def handle_system_msg(msg):
    """处理系统消息"""
    raw = msg.raw
    # 4表示消息状态为撤回
    if raw['Status'] == 4 and msg.bot.is_forward_revoke_msg:
        # 转发撤回的消息
        forward_revoke_msg(msg)


def forward_revoke_msg(msg):
    """转发撤回的消息"""
    # 获取被撤回消息的ID
    revoke_msg_id = re.search('<msgid>(.*?)</msgid>',
                              msg.raw['Content']).group(1)
    # bot中有缓存之前的消息，默认200条
    for old_msg_item in msg.bot.messages[::-1]:
        # 查找撤回的那条
        if revoke_msg_id == str(old_msg_item.id):
            # 判断是群消息撤回还是好友消息撤回
            if old_msg_item.member:
                sender_name = '群「{0}」中的「{1}」'.format(
                    old_msg_item.chat.name, old_msg_item.member.name)
            else:
                sender_name = '「{}」'.format(old_msg_item.chat.name)
            # 名片无法转发
            if old_msg_item.type == 'Card':
                sex = '男' if old_msg_item.card.sex == 1 else '女' or '未知'
                msg.bot.master.send('「{0}」撤回了一张名片：\n名称：{1}，性别：{2}'.format(
                    sender_name, old_msg_item.card.name, sex))
            else:
                # 转发被撤回的消息
                old_msg_item.forward(msg.bot.master, prefix='{1}撤回了一条消息：{2}'.format(
                    sender_name, get_msg_chinese_type(old_msg_item.type)))
            return None


def get_msg_chinese_type(msg_type):
    """转中文类型名"""
    if msg_type == 'Text':
        return '文本'
    if msg_type == 'Map':
        return '位置'
    if msg_type == 'Card':
        return '名片'
    if msg_type == 'Note':
        return '提示'
    if msg_type == 'Sharing':
        return '分享'
    if msg_type == 'Picture':
        return '图片'
    if msg_type == 'Recording':
        return '语音'
    if msg_type == 'Attachment':
        return '文件'
    if msg_type == 'Video':
        return '视频'
    if msg_type == 'Friends':
        return '好友请求'
    if msg_type == 'System':
        return '系统'
