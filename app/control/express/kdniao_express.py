# -*- coding: utf-8 -*-
"""
Project: EverydayWechat-Github
Creator: DoubleThunder
Create time: 2019-09-04 12:24
Introduction: 快递鸟（http://www.kdniao.com/） 快递查询
"""

import json
import hashlib
import base64
import requests
# from app import config

# 此处为快递鸟官网申请的帐号和密码

URL = 'http://api.kdniao.com/Ebusiness/EbusinessOrderHandle.aspx'
HEADERS = {
    "Accept": "application/x-www-form-urlencoded;charset=utf-8",
    "Accept-Encoding": "utf-8"
}
# 2-在途中,3-签收,4-问题件
EXPRESS_STATE_DICT = {'0': '无物流', '2': '在途中', '3': '签收', '4': '问题件'}
__all__ = ['get_express_info']


def encrypt(origin_data, app_key):
    """
    数据内容签名：把(请求内容(未编码) + AppKey)进行 MD5 加密，然后 Base64 编码
    :param origin_data: str, 请求的数据
    :param app_key:
    :return: 加密后的数据
    """
    encodestr = hashlib.md5(
        (origin_data + app_key).encode("UTF-8")).hexdigest()  # MD5 加密
    base64_text = base64.b64encode(
        encodestr.encode(encoding='utf-8'))  # Base64 加密
    return base64_text.decode()  # 再次编码


def get_company_info(express_code, app_id, app_key):
    """
    单号识别 API 接口。地址：http://www.kdniao.com/api-recognise
    查询订单号的归属物流公司信息
    :param express_code: str 订单号
    :return: str 订单信息
    """
    data1 = {'LogisticCode': express_code}
    d1 = json.dumps(data1, sort_keys=True)
    post_data = {
        'RequestData': d1,
        'EBusinessID': app_id,
        'RequestType': '2002',
        'DataType': '2',
        'DataSign': encrypt(d1, app_key)
    }
    try:
        resp = requests.post(URL, data=post_data, headers=HEADERS)
        print(resp.text)
        if resp.status_code == 200:
            content_dict = resp.json()
            if not content_dict['Success']:
                print('出错原因：{}'.format(content_dict['Reason']))
                return None
            elif not any(content_dict['Shippers']):
                print("未查到该快递信息，请检查快递单号是否有误！")
                return None
            else:
                shipper_info = content_dict['Shippers'][0]
                shipper_name = shipper_info['ShipperName']
                shipper_code = shipper_info['ShipperCode']
                xx = '快递单号 {ecode} 的快递公司是：{sname}({scode})'.format(
                    sname=shipper_name,
                    scode=shipper_code,
                    ecode=express_code)
                print(xx)
                return {'shipper_code': shipper_code, 'shipper_name': shipper_name}

    except Exception as exception:
        print(str(exception))

    return None


def get_logistic_info(logistic_code, shipper_code, app_id, app_key):
    """
    即时查询 api 接口。地址：http://www.kdniao.com/api-track
    对单个订单号进行查询详细的物流信息
    :param logistic_code: str, 订单号
    :param shipper_code: str, 快递公司编号
    :return:
    """
    data1 = {'OrderCode': '', 'LogisticCode': logistic_code,
             'ShipperCode': shipper_code}
    d1 = json.dumps(data1, sort_keys=True)
    post_data = {
        'RequestData': d1,
        'EBusinessID': app_id,
        'RequestType': '1002',
        # 'RequestType': '1008',
        'DataType': '2',
        'DataSign': encrypt(d1, app_key)
    }
    try:
        resp = requests.post(URL, data=post_data, headers=HEADERS)
        print(resp.text)
        if resp.status_code == 200:
            content_dict = resp.json()
            if not content_dict['Success']:
                print('出错原因：{}'.format(content_dict['Reason']))
                return None
            elif not any(content_dict['Traces']):
                print("未查询到该快递物流轨迹！")
                return None
            else:
                return content_dict
    except Exception as exception:
        print(str(exception))
    return None


def get_express_info(express_code, shipper_code='', shipper_name=''):
    """
    查询快递物流信息
    :param express_code: str,快递单号
    :param shipper_code: str,快递公司简称代号
    :param shipper_name: str,快递公司名称（用于结果显示）
    :return:
    """
    express_config_info = {'app_id':'test1612876','app_key':'0d77a9d2-f856-4386-aeff-523115eb29e3'}
    app_id = express_config_info['app_id']
    app_key = express_config_info['app_key']
    if not shipper_code or not shipper_name:
        company_info = get_company_info(express_code, app_id, app_key)
        # print(company_info)
        if not company_info:
            return
        shipper_code = company_info['shipper_code']
        shipper_name = company_info['shipper_name']
    trace_data = get_logistic_info(express_code, shipper_code, app_id, app_key)
    print(trace_data)
    if not trace_data:
        return
    state_code = trace_data['State']
    express_state = EXPRESS_STATE_DICT.get(state_code, '未知状态')

    info = []
    express_base_info = '物流公司：{shipper_name}\n物流单号：{express_code}\n物流状态：{express_state}'.format(
        shipper_name=shipper_name,
        express_code=express_code,
        express_state=express_state)
    info.append(express_base_info)
    info.append('------物流详情------')
    traces = trace_data['Traces']
    for i, item in enumerate(traces[::-1]):
        bb = '{index}. {time} {station}'.format(
            index=str(i + 1),
            time=item['AcceptTime'],
            station=item['AcceptStation'])
        # print(bb)
        info.append(bb)
    return_info = {
        'express_code': express_code,
        'shipper_code': shipper_code,
        'shipper_name': shipper_name,
        'info': '\n'.join(info),
        'state': True if state_code == '3' else False
    }
    return return_info


if __name__ == '__main__':
    # code = '78109182715352'
    # code = '78109356970791'
    # code = '9860572561560'
    code = 'JD0001855864185'
    cc = get_express_info(code)
    print(cc)
    if cc:
        print(cc['info'])



# 快递100查询爬虫接口：
# 1.由单号匹配快递公司
# Cookie: WWWID=WWWA108ECEE63632B12FEA875741EDD0B9B; Hm_lvt_22ea01af58ba2be0fec7c11b25e88e6c=1577692772; Hm_lpvt_22ea01af58ba2be0fec7c11b25e88e6c=1577693248
# Request URL: https://www.kuaidi100.com/autonumber/autoComNum?resultv2=1&text=单号(int)
# repone:{"comCode":"","num":"78109356970791","auto":[{"comCode":"zhongtong","lengthPre":14,"noCount":816,"noPre":"781093"}]}

# 2.由单号+快递公司搜索快递信息
# Cookie: csrftoken=PfH37dAexuVOD7y8zmh_yOri6nrJCCDnvT1PBSMFMYc; WWWID=WWWA108ECEE63632B12FEA875741EDD0B9B; Hm_lvt_22ea01af58ba2be0fec7c11b25e88e6c=1577692772; Hm_lpvt_22ea01af58ba2be0fec7c11b25e88e6c=1577693248
# type:快递公司
# postid：单号(int)
# temp：可能是cookie的时间差
# Request URL: https://www.kuaidi100.com/query?type=zhongtong&postid=单号(int)&temp=0.29522739847850366&phone=
# repone:
# {"message":"ok","nu":"78109356970791","ischeck":"1","condition":"F00","com":"zhongtong","status":"200","state":"3","data":[{"time":"2019-09-06 18:58:15","ftime":"2019-09-06 18:58:15","context":"【北京市】 快件已由【菜鸟的北京市朝阳区南湖中园1区【自提柜】】代签收, 如有问题请电联（18910380939 / 057126883287）, 感谢您使用中通快递, 期待再次为您服务!","location":""},{"time":"2019-09-06 14:47:13","ftime":"2019-09-06 14:47:13","context":"【北京市】 【望京】 的孙立平18910380939（18910380939） 正在第1次派件, 请保持电话畅通,并耐心等待（95720为中通快递员外呼专属号码，请放心接听）","location":""},{"time":"2019-09-06 14:42:10","ftime":"2019-09-06 14:42:10","context":"【北京市】 快件已经到达 【望京】","location":""},{"time":"2019-09-06 11:47:18","ftime":"2019-09-06 11:47:18","context":"【北京市】 快件离开 【北京】 已发往 【望京】","location":""},{"time":"2019-09-06 11:04:15","ftime":"2019-09-06 11:04:15","context":"【北京市】 快件已经到达 【北京】","location":""},{"time":"2019-09-05 01:38:18","ftime":"2019-09-05 01:38:18","context":"【中山市】 快件离开 【中山中心】 已发往 【北京】","location":""},{"time":"2019-09-05 01:34:53","ftime":"2019-09-05 01:34:53","context":"【中山市】 快件已经到达 【中山中心】","location":""},{"time":"2019-09-04 21:41:18","ftime":"2019-09-04 21:41:18","context":"【中山市】 快件离开 【中山新古镇】 已发往 【北京】","location":""},{"time":"2019-09-04 21:37:22","ftime":"2019-09-04 21:37:22","context":"【中山市】 【中山新古镇】（0760-23705006） 的 公司王科伟（18825441118） 已揽收","location":""}]}
