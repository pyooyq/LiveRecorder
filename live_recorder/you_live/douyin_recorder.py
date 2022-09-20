# coding=utf-8
import requests
from ._base_recorder import BaseRecorder, recorder

@recorder(liver = 'douyin')
class BiliRecorder(BaseRecorder):
    
    def __init__(self, short_id, **args):
        BaseRecorder.__init__(self, short_id, **args)
        
    
    def getRoomInfo(self):
        roomInfo = {}
        roomInfo['short_id'] = self.short_id
        
        url = "https://live.douyin.com/webcast/web/enter/?aid=6383&web_rid=%s"%self.short_id
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            "sec-ch-ua":'"Microsoft Edge";v="105", " Not;A Brand";v="99", "Chromium";v="105"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.42',
        }

        msToken=requests.get(url, timeout=10, headers=headers).headers.get("set-cookie").split(';')[0]
        headers["cookie"]=msToken
        ttwid=requests.get("https://live.douyin.com/favicon.ico", timeout=10, headers=headers).headers.get("set-cookie").split(';')[0]
        headers["cookie"]=msToken+";"+ttwid
        
        data_json = requests.get(url, timeout=10, headers=headers).json()['data']['data'][0]
        roomInfo['room_id'] = str(data_json["id_str"])
        roomInfo['live_status'] = str(data_json['status'])
        if roomInfo['live_status']=="2":
            roomInfo['live_status'] ="1"
            roomInfo['room_title'] = data_json['title']
            roomInfo['room_description'] = ""
            roomInfo['room_owner_id'] = data_json['owner']['id_str']
            roomInfo['room_owner_name'] = data_json['owner']['nickname']
            quality = {}
            multirates = data_json["stream_url"]["live_core_sdk_data"]["pull_data"]["options"]["qualities"]
            for rate in multirates:
                rate_format=""
                if str(rate['sdk_key']) =="origin":
                    rate_format ="FULL_HD1"
                if str(rate['sdk_key']) =="hd":
                    rate_format ="HD1"
                if str(rate['sdk_key']) =="sd":
                    rate_format ="SD1"
                if str(rate['sdk_key']) =="ld":
                    rate_format ="SD2"
                quality[rate_format] = rate['name']
            roomInfo['live_rates'] = quality
            roomInfo["stream_url"]=data_json["stream_url"]["flv_pull_url"]



        self.headers = headers    
        self.roomInfo = roomInfo    
        return roomInfo       


    def getLiveUrl(self, qn):
        if not hasattr(self, 'roomInfo'):
            self.getRoomInfo()
        if self.roomInfo['live_status'] != '1':
            print('当前没有在直播')
            return None
        
        self.live_url = self.roomInfo["stream_url"][qn]
        self.live_qn = qn

        print("申请清晰度 %s的链接，得到清晰度 %s的链接"%(qn, self.live_qn))

        return self.live_url