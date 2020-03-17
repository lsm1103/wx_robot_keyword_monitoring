from wxpy import *
from app import config
import time
import datetime
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from app.control.airquality.air_quality_aqicn import get_air_quality
from app.utils.data_collection import (
    get_rubbish,
    get_dictum_info,
    get_weather_info,
    get_diff_time,
    get_constellation_info,
    get_calendar_info
)

logger = logging.getLogger('itchat')


def load_config_to_bot(bot):
    """加载配置项"""
    bot_status = '机器人登录成功！！！'
    bot.friends(update=True)  # 更新好友数据
    bot.groups(update=True)  # 更新群聊数据
    # 未定义机器人管理员
    if not config.bot_master_name:
        bot.master = bot.file_helper
        bot_status += '\n未设置机器人管理员，信息将发送至文件助手，不能使用远程命令控制机器人！\n\n'
    else:
        master = search_friend(bot, config.bot_master_name)
        # 查找管理员
        if master:
            bot.master = master
            bot_status += '\n机器人管理员成功设置为：「{0}」，这里查看管理员命令手册->'.format(
                              config.bot_master_name)
        else:
            bot.master = bot.file_helper
            bot_status += '\n在好友列表中未找到名为「{}」的好友，信息将发送至文件助手，不能使用远程命令控制机器人！\n\n'.format(
                config.bot_master_name)
    # 设置开关
    bot.is_friend_auto_reply = config.is_friend_auto_reply
    bot.is_group_reply = config.is_group_reply  # 此项表示是否所有群自动回复
    bot.is_group_at_reply = config.is_group_at_reply
    bot.is_listen_friend = config.is_listen_friend  # 要监听的朋友或群
    bot.is_listen_zy_groups = config.is_listen_zy_groups  # 要监听的销售资源群
    bot.is_forward_mode = config.is_forward_mode
    bot.is_listen_sharing = config.is_listen_sharing
    bot.is_forward_revoke_msg = config.is_forward_revoke_msg
    bot.is_forward_group_at_msg = config.is_forward_group_at_msg
    # 加载对应好友和群
    load_listen_friend(bot)
    # 加载需要转发的群
    load_forward_groups(bot)
    load_listen_sharing_groups(bot)

    # 提醒内容不为空时，启动定时任务
    alarm_dict = config.alarm_info
    if config.is_alarm:
        init_alarm(bot, alarm_dict)  # 初始化定时任务
        bot_status += '\n定时任务初始化成功~\n'
        print('定时任务初始化成功~')
    else:
        bot_status += '\n因定时任务为空，定时任务初始化失败~\n'
        print('因定时任务为空，定时任务初始化失败~')

    # 发送机器人状态信息
    bot_status = bot_status if '文件助手' in bot_status else bot_status + \
        bot_status_detail(bot)

    if not alarm_dict or not config.is_alarm:
        print('未开启每日提醒功能。')
    else:
        print('已开启定时发送提醒功能。')
        status = ''
        for item in alarm_dict:
            name_text = ''
            for name in alarm_dict[item]['name']:
                name_text += '给{name}，定时：{alarm_time}-{jitter}s的范围内，发送提醒内容一次。'.format(
                    name=name, alarm_time=('/').join(alarm_dict[item]['alarm_timed']), jitter=alarm_dict[item]['alarm_jitter'])
            status += name_text
        print(status)
        print('=' * 80)
        bot_status += status
    bot.master.send(bot_status)
    logger.info(bot_status)


def init_alarm(bot, alarm_dict):
    """
    初始化定时任务
    :param alarm_dict: 定时相关内容
    """
    # 定时任务
    scheduler = BackgroundScheduler()
    for item in alarm_dict:
        if not alarm_dict[item]['user_group']:
            print(alarm_dict[item]['name'])
            for group in [bot.groups().search(v)[0] for v in alarm_dict[item]['name']]:
                for v in alarm_dict[item]['alarm_timed']:
                    time_data = v.split(':')
                    scheduler.add_job(send_alarm_msg, 'cron', args=[bot, group, item, alarm_dict[item]['is_tomorrow']], hour=int(time_data[0]),
                                      minute=int(time_data[1]), id=make_md5(group.name+v), misfire_grace_time=600,
                                      jitter=alarm_dict[item]['alarm_jitter'])
    scheduler.start()
    print('已开启定时发送提醒功能...')
    print(scheduler.get_jobs())


def send_alarm_msg(bot, group, key, is_tomorrow):
    """ 发送定时提醒 """
    print('\n启动定时自动提醒...')
    conf = config.alarm_info
    data = conf[key]
    print(data)

    air_quality = get_air_quality(data['air_quality_city'])
    dictum = get_dictum_info(data['dictum_channel'])
    weather = get_weather_info(data['city_name'], is_tomorrow)
    diff_time = get_diff_time(data['start_date'], data['start_date_msg'])
    horoscope = get_constellation_info(data['horescope'], is_tomorrow)
    calendar_info = get_calendar_info( data['calendar'], is_tomorrow, _date='')
    sweet_words = data['sweet_words']
    send_msg = '\n'.join(x for x in [
                         calendar_info, weather, air_quality, horoscope, dictum, diff_time, sweet_words] if x)
    if not send_msg:
        return '出现了一点点问题，请稍等'
    time.sleep(1)
    group.send(send_msg)
    print('\n定时内容:\n{}\n发送成功...\n\n'.format(send_msg))
    print('自动提醒消息发送完成...\n')


def load_listen_friend(bot):
    """加载需要监听的人和群"""
    if bot.is_listen_friend:
        bot.listen_friends = search_friends(bot, config.listen_friend_names)
        if not bot.listen_friends:
            bot.listen_friends = []
            bot.is_listen_friend = False
            return '未在好友中找到备注为「{}」的监听对象！'.format(str(config.listen_friend_names))

        bot.listen_friend_groups = [bot.groups().search(
            v)[0] for v in config.listen_friend_groups]
        if len(bot.listen_friend_groups) < 1:
            bot.listen_friend_groups = []
            bot.is_listen_friend = False
            return '未找到群名包含「{}」的监听群！'.format(config.listen_friend_groups)

    print( [bot.groups().search(v)[0] for v in config.listen_zy_groups.keys() ] )
    if bot.is_listen_zy_groups:
        bot.listen_zy_groups = [bot.groups().search(v)[0] for v in config.listen_zy_groups.keys() ]
        if len(bot.listen_zy_groups) < 1:
            bot.listen_zy_groups = []
            bot.is_listen_zy_groups = False
            return '未找到群名包含「{}」的监听群！'.format(config.listen_zy_groups.keys() )
    if not bot.is_group_reply:
        bot.white_list = [bot.groups().search(v)[0] for v in config.white_list]
        bot.black_list = [bot.groups().search(v)[0] for v in config.black_list]
        if len(bot.white_list) < 1:
            bot.white_list = []
            return '未找到群名包含「{}」的白名单监听群！'.format(config.white_list)
        if len(bot.black_list) < 1:
            bot.black_list = []
            return '未找到群名包含「{}」的白名单监听群！'.format(config.black_list)
    return None


def load_forward_groups(bot):
    """加载需要转发的群"""
    if bot.is_forward_mode:
        bot.forward_groups = bot.groups().search(config.forward_groups)
        if len(bot.forward_groups) < 1:
            bot.forward_groups = []
            bot.is_forward_mode = False
            return '未找到群名包含「{}」的转发群！'.format(config.forward_groups)
    return None


def load_listen_sharing_groups(bot):
    """加载监控群"""
    if bot.is_listen_sharing:
        bot.listen_sharing_groups = bot.groups().search(config.listen_sharing_groups)
        if len(bot.listen_sharing_groups) < 1:
            bot.listen_sharing_groups = []
            bot.is_listen_sharing = False
            return '未找到群名包含「{}」的分享监控群！'.format(config.listen_sharing_groups)
    return None


def bot_status_detail(bot):
    """机器人配置状态"""
    bot_config_status = '机器人配置状态：'
    bot_config_status += '\n机器人管理员：{0}（{1}）'.format(
        bot.master.remark_name, bot.master.nick_name)
    if bot.is_forward_mode:
        bot_config_status += '\n转发模式已开启，您发送给我的任何信息都将被转发至:{}，您可发送命令：关闭转发模式 来关闭转发模式。'.format(
            str(bot.forward_groups))
    bot_config_status += '\n好友自动回复：{}'.format(
        ('是' if bot.is_friend_auto_reply else '否'))

    bot_config_status += '\n所有群自动回复：{}'.format(
        ('是' if bot.is_group_reply else '否'))
    if bot.is_group_reply:
        bot_config_status += '，是否需要@才回复：{}'.format(
            '是' if bot.is_group_at_reply else '否')

    bot_config_status += '\n是否开启转发群艾特模式：{}'.format(
        ('是' if bot.is_forward_group_at_msg else '否'))

    bot_config_status += '\n是否开启防撤回模式：{}'.format(
        ('是' if bot.is_forward_revoke_msg else '否'))

    bot_config_status += '\n是否开启监听模式：{}'.format(
        '是' if bot.is_listen_friend else '否')
    if bot.is_listen_friend:
        bot_config_status += '，在{0}中监听{1}'.format(
            str(bot.listen_friend_groups), str(bot.listen_friends))

    bot_config_status += '\n是否开启监听模式：{}'.format(
        '是' if bot.is_listen_zy_groups else '否')
    if bot.is_listen_zy_groups:
        bot_config_status += '，在{0}中监听{1}'.format(
            str(bot.listen_zy_groups), str(config.keyword['keyword_data'][:5])+'...')

    bot_config_status += '\n是否开启转发模式：否'

    bot_config_status += '\n是否开启监控模式：{}'.format(
        '是' if bot.is_listen_sharing else '否')
    if bot.is_listen_sharing:
        bot_config_status += '，将在以下群中监控分享：{}'.format(
            str(bot.listen_sharing_groups))
    return bot_config_status


def search_friend(bot, name):
    """查找某个好友
    优先级为：好友备注-好友昵称
    getattr() 函数用于返回一个对象属性值
    """
    nick_name_friend = None
    for friend in bot.friends():
        if getattr(friend, 'remark_name', None) == name:
            return friend
        elif not nick_name_friend and getattr(friend, 'nick_name', None) == name:
            nick_name_friend = friend
    return nick_name_friend or None


def search_friends(bot, names):
    """查找多个好友，用|分割
    匹配备注和微信昵称
    nick_name:昵称 ;remark_name:备注
    getattr(对象，对象的键，异常默认) 函数用于返回一个对象属性值    
    """
    result_list = []
    for friend in bot.friends():
        if getattr(friend, 'remark_name', None) in names:
            result_list.append(friend)
        elif getattr(friend, 'nick_name', None) in names:
            result_list.append(friend)
    return result_list


def make_md5(str):
    return hashlib.md5(str.encode(encoding='utf-8')).hexdigest()
