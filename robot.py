from wxpy import *
import wx_reply
import time
import wx_command
import load
from app import config

# bot = Bot(cache_path=True)
bot = Bot(cache_path=True, console_qr=2)
bot.enable_puid()
# 加载配置信息到机器人
load.load_config_to_bot(bot)

print(wx_reply.get_msg_chinese_type('Text'))

"""好友功能"""
@bot.register(msg_types=FRIENDS)
def auto_accept_friends(msg):
    """自动接受好友请求"""
    wx_reply.auto_accept_friends(msg)


@bot.register(chats=Friend)
def friend_msg(msg):
    """接收好友消息"""
    if not msg.bot.is_friend_auto_reply:
        return None
    if msg.type == TEXT:
        wx_reply.auto_reply(msg, 'other')
        return None
    elif msg.type == RECORDING:
        return '不停不停，王八念经'
    else:
        pass


"""群功能"""
@bot.register(chats=Group)
def group_msg(msg):
    """接收群消息"""
    groups_list = [bot.groups().search(v)[0]
                   for v in config.listen_zy_groups.keys()]
    key = config.group_type[config.listen_zy_groups[msg.chat.name]]
    print(groups_list, key)
    # 群@转发功能
    if bot.is_forward_mode:
        if msg.is_at and msg.bot.is_forward_group_at_msg:
            for item in bot.forward_groups:
                msg.forward(item, prefix='「{0}」在群「{1}」中艾特了你：'.format(
                    msg.member.name, msg.chat.name))

        # 监听销售资源-群聊，如xx资源群
        if msg.bot.is_listen_zy_groups and msg.chat in groups_list:
            for ci in config.keyword[key]:
                if ci in msg.text:
                    for item in bot.forward_groups:
                        msg.forward(item, prefix='监听指定销售资源-群消息：「{0}」在「{1}」发了消息：'.format(
                            msg.member.is_friend.remark_name or msg.member.nick_name, msg.chat.name))

        # 监听好友群聊，如老板讲话
        if msg.bot.is_listen_friend and msg.chat in msg.bot.listen_friend_groups and msg.member.is_friend in msg.bot.listen_friends:
            for item in bot.forward_groups:
                msg.forward(item, prefix='监听指定好友群消息：「{0}」在「{1}」发了消息：'.format(
                    msg.member.is_friend.remark_name or msg.member.nick_name, msg.chat.name))

    if msg.type == TEXT:
        # 是否所有群自动回复:否
        if not msg.bot.is_group_reply:
            # print(msg.chat, msg.chat in msg.bot.white_list, msg.chat not in msg.bot.black_list,msg.bot.white_list, msg.bot.black_list)
            if msg.chat in msg.bot.white_list and msg.chat not in msg.bot.black_list:
                if len(msg.text) < 50:
                    if msg.bot.is_group_at_reply:
                        # @机器人才回复
                        if msg.is_at:
                            # 监听销售资源-群聊，如xx资源群
                            if msg.bot.is_listen_zy_groups and msg.chat in groups_list:
                                wx_reply.auto_reply(msg, 'zy', key)
                            else:
                                wx_reply.auto_reply(msg, 'other', key)
                    else:
                        # 不用@直接回复
                        if msg.bot.is_listen_zy_groups and msg.chat in groups_list:
                            wx_reply.auto_reply(msg, 'zy', key)
                        else:
                            wx_reply.auto_reply(msg, 'other')
        # 是否所有群自动回复:是
        else:
            if msg.chat in msg.bot.black_list:
                if len(msg.text) < 50:
                    if msg.bot.is_group_at_reply:
                        # @机器人才回复
                        if msg.is_at:
                            # 监听销售资源-群聊，如xx资源群
                            if msg.bot.is_listen_zy_groups and msg.chat in groups_list:
                                wx_reply.auto_reply(msg, 'zy', key)
                            else:
                                wx_reply.auto_reply(msg, 'other')
                    else:
                        # 不用@直接回复
                        if msg.bot.is_listen_zy_groups and msg.chat in groups_list:
                            wx_reply.auto_reply(msg, 'zy', key)
                        else:
                            wx_reply.auto_reply(msg, 'other')
    # 群分享监控
    elif msg.type == SHARING and msg.bot.is_listen_sharing and msg.chat in msg.bot.listen_sharing_groups:
        # 群分享转发监控，防止分享广告
        msg.forward(msg.bot.master, prefix='分享监控：「{0}」在「{1}」分享了：'.format(
            msg.member.name, msg.chat.name))
    return None


@bot.register(msg_types=NOTE)
def system_msg(msg):
    """接收系统消息"""
    wx_reply.handle_system_msg(msg)


"""管理员功能"""
@bot.register(chats=bot.master)
def do_command(msg):
    """执行管理员命令"""
    wx_command.do_command(msg)


# 堵塞进程，直到结束消息监听 (例如，机器人被登出时)
# embed() 互交模式阻塞，电脑休眠或关闭互交窗口则退出程序
bot.join()
