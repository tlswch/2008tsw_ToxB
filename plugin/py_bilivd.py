#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import json
from requests import session, utils
import os
import time
import base64

class Spider(Spider):  # 元类 默认的元类 type
	def getName(self):
		return "B站视频"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"搞笑": "搞笑",
			"美食": "美食",
			"科普": "科普",
			"橙子": "半个橙子",
			"纪录片": "纪录片",
			"演唱会": "演唱会",
			"动物世界": "动物世界",
			"相声小品": "相声小品",
			"假窗-白噪音": "窗+白噪音"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		result = {
			'list':[]
		}
		return result
	cookies = ''
	def getCookie(self):
		cookies_str ="CURRENT_FNVAL=4048; buvid3=08C842FA-A150-2969-C730-3AB8D6523A8D32523infoc; rpdid=|(JY)J~ukkkk0J'uYlJYllJJR; CURRENT_BLACKGAP=0; blackside_state=0; sid=87yqqygc; innersign=0; i-wanna-go-back=-1; fingerprint=e4bfcb5fe4ce5693c744f8a5294c4501; buvid_fp=08C842FA-A150-2969-C730-3AB8D6523A8D32523infoc; buvid_fp_plain=undefined; _jct=c63db990fe9c11ecab088acda368e806; DedeUserID=454318234; DedeUserID__ckMd5=df1eb9df81545b79; SESSDATA=529f3b0e%2C1672823016%2Cc1568*71; bili_jct=7648a6f663b0953663bd58ae51e71dc1; b_ut=5" #填入大会员Cookies
		cookies_dic = dict([co.strip().split('=') for co in cookies_str.split(';')])
		rsp = session()
		cookies_jar = utils.cookiejar_from_dict(cookies_dic)
		rsp.cookies = cookies_jar
		self.cookies = rsp.cookies
		return rsp.cookies
	def categoryContent(self,tid,pg,filter,extend):		
		result = {}
		url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}&page={1}'.format(tid,pg)
		if len(self.cookies) <= 0:
			self.getCookie()
		rsp = self.fetch(url,cookies=self.cookies)
		content = rsp.text
		jo = json.loads(content)
		if jo['code'] != 0:			
			rspRetry = self.fetch(url,cookies=self.getCookie())
			content = rspRetry.text		
		jo = json.loads(content)
		videos = []
		vodList = jo['data']['result']
		for vod in vodList:
			aid = str(vod['aid']).strip()
			title = vod['title'].strip().replace("<em class=\"keyword\">","").replace("</em>","")
			img = 'https:' + vod['pic'].strip()
			remark = str(vod['duration']).strip()
			videos.append({
				"vod_id":aid,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":remark
			})
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = 9999
		result['limit'] = 90
		result['total'] = 999999
		return result
	def cleanSpace(self,str):
		return str.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
	def detailContent(self,array):
		aid = array[0]
		url = "https://api.bilibili.com/x/web-interface/view?aid={0}".format(aid)

		rsp = self.fetch(url,headers=self.header)
		jRoot = json.loads(rsp.text)
		jo = jRoot['data']
		title = jo['title'].replace("<em class=\"keyword\">","").replace("</em>","")
		pic = jo['pic']
		desc = jo['desc']
		timeStamp = jo['pubdate']
		timeArray = time.localtime(timeStamp)
		year = str(time.strftime("%Y-%m-%d %H:%M", timeArray)).replace(" ","/")
		dire = jo['owner']['name']
		typeName = jo['tname']
		remark = str(jo['duration']).strip()
		vod = {
			"vod_id":aid,
			"vod_name":title,
			"vod_pic":pic,
			"type_name":typeName,
			"vod_year":year,
			"vod_area":"",
			"vod_remarks":remark,
			"vod_actor":"",
			"vod_director":dire,
			"vod_content":desc
		}
		ja = jo['pages']
		playUrl = ''
		for tmpJo in ja:
			cid = tmpJo['cid']
			part = tmpJo['part']
			playUrl = playUrl + '{0}${1}_{2}#'.format(part,aid,cid)

		vod['vod_play_from'] = 'B站视频'
		vod['vod_play_url'] = playUrl

		result = {
			'list':[
				vod
			]
		}
		return result
	def searchContent(self,key,quick):
		url = 'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={0}'.format(key)
		if len(self.cookies) <= 0:
			self.getCookie()
		rsp = self.fetch(url,cookies=self.cookies)
		content = rsp.text
		jo = json.loads(content)
		if jo['code'] != 0:
			rspRetry = self.fetch(url, cookies=self.getCookie())
			content = rspRetry.text
		jo = json.loads(content)
		videos = []
		vodList = jo['data']['result']
		for vod in vodList:
			aid = str(vod['aid']).strip()
			title = vod['title'].strip().replace("<em class=\"keyword\">", "").replace("</em>", "")
			img = 'https:' + vod['pic'].strip()
			remark = str(vod['duration']).strip()
			videos.append({
				"vod_id": aid,
				"vod_name": title,
				"vod_pic": img,
				"vod_remarks": remark
			})
		result = {
			'list': videos
		}
		return result


	def playerContent(self,flag,id,vipFlags):
		result = {}

		ids = id.split("_")
		url = 'https://api.bilibili.com:443/x/player/playurl?avid={0}&cid={1}&qn=116'.format(ids[0],ids[1])
		if len(self.cookies) <= 0:
			self.getCookie()
		rsp = self.fetch(url,cookies=self.cookies)
		jRoot = json.loads(rsp.text)
		jo = jRoot['data']
		ja = jo['durl']
		
		maxSize = -1
		position = -1
		for i in range(len(ja)):
			tmpJo = ja[i]
			if maxSize < int(tmpJo['size']):
				maxSize = int(tmpJo['size'])
				position = i

		url = ''
		if len(ja) > 0:
			if position == -1:
				position = 0
			url = ja[position]['url']

		result["parse"] = 0
		result["playUrl"] = ''
		result["url"] = url
		result["header"] = {
			"Referer":"https://www.bilibili.com",
			"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
		}
		result["contentType"] = 'video/x-flv'
		return result

	config = {
		"player": {},
		"filter": {}
	}
	header = {}

	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
