# -*- coding: utf-8 -*-
'''
公司 vs 商業
公司係指依公司法規定組織登記成立之社團法人，股東就其出資額負責（無限公司除外）；
而商業登記法所稱之商業，也就是一般所指的商號（行號），是指以營利為目的之獨資或合夥經營事業，負責人或合夥人負無限責任。
而公司與商號雖然均是以營利為目的，二者除了名稱不同之外，所依據之法源、組成分子之責任負擔亦不相同
'''
from bs4 import BeautifulSoup
from PIL import Image
from co_fun import ReadParameter
from co_fun import CrawledDataGUI
from co_fun import SaveData
import requests
import random
import sys
import shutil
import pytesseract
import time
import re
import datetime







# GUI = "12041076"  #"94925188" # 商號
# GUI = "53988048"   #"16273940"  # 公司
# GUI = "29182774 "  #分公司
# GUI = "22954677" # 公司 and 分公司

# 16273940 公司      HC+GUI
# 12041076 商號      HB
# 29182774 分公司    BC+GUI
# GUI = "32010060" #工廠      HF
# 42904351 有限合夥  HL+GUI




# 公司 http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do
def company_crawler(GUI, detail_headers):

	entity_type = "HC"
	detail_url = "http://findbiz.nat.gov.tw/fts/query/QueryCmpyDetail/queryCmpyDetail.do"
	banKey = ""
	banNo = GUI
	banId = "#tabCmpyContent"
	objectId = entity_type + GUI

	# payload for company detail page
	detail_payload = {
		"banNo":banNo,
		"banKey":banKey,
		"objectId":objectId,
	}
	
	while True:
		try:
			detail_res = requests.post(detail_url, data = detail_payload, headers = detail_headers, timeout = 30)
			break
	
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print exc_obj
			print(exc_type, exc_tb.tb_lineno)
			detail_headers = {
				"User-Agent":random.choice(USER_AGENT),
				"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
			}

			time.sleep(10)
				
	soup = BeautifulSoup(detail_res.text, "html.parser")
	
	# 公司狀態
	try:
		status = soup.select(banId)[0].select("tbody")[0].select("tr")[1].select("td")[1].text.encode("big5", "ignore").strip()
	except:
		return "", "", ""

	if status == "":
		return

	# 營業項目
	code = soup.select(banId)[0].select("tbody")[0].select("tr")[-1].select("td")[1]
	# 若只有一個營業項目，直接抓取英文字的位置
	if len(code.select("br")) == 1:
		code = code.text.encode("utf-8")
		pos = re.search("[A-Z]", code)
		if pos != None:
			pos = pos.group()
			pos = code.find(pos)
			codes = code[pos:pos+7]
		else:
			codes = ""
		
	# 多個營業項目
	else:
		code = code.encode(formatter = "html")  # 利用&nbsp;分行
		pos = code.find("&nbsp;")
		codes = code[(pos-7):pos] + "\n"
		while pos != -1:				
			# print code
			code = code[pos+6:]
			pos = code.find("&nbsp;")
			codes = codes + code[(pos-7):pos] + "\n"
		codes = codes.replace("/>", "").replace("</td", "").replace("br>", "").strip()

	#print codes
	data_type = "公司".decode("utf-8").encode("big5", "ignore")

	return data_type, status, codes



# get captcha of 經濟部商業司商業資料頁面
def get_captcha_of_buss():

	s = requests.Session()
	#驗證碼網址
	res = s.get("http://gcis.nat.gov.tw/gps/kaptcha.jpg", stream = True, verify = False, timeout = 30)
	
	#儲存驗證碼圖片
	with open('pic.jpg','wb') as f:
		f.write(res.content)
		
	#讀取驗證碼
	image = Image.open('pic.jpg')
	#調整圖片大小，以利判讀
	image.resize((150, 50),Image.ANTIALIAS).save("pic.jpg")
	image = Image.open("pic.jpg")
	captcha = pytesseract.image_to_string(image).replace(" ", "").replace("-", "").replace("$", "")
	return s, captcha

# 商業 http://gcis.nat.gov.tw/gps/gpsBussInit/GpsBussInit/init.do
def bussiness_crawler(GUI):

	while True:
		try:
			s, captcha = get_captcha_of_buss()
		
			# 商業查詢首頁，獲得token
			url = "http://gcis.nat.gov.tw/gps/gpsBussInit/GpsBussInit/init.do"
			res = s.get(url, timeout = 30)
			soup = BeautifulSoup(res.text, "html.parser")

			token = soup.select(".col-sm-3")[13].select("input")[1]["value"]
			
			payload = {
				"type":"",
				"pageUtil.currPageNo":"",
				"pageUtil.totalPageNo":"",
				"qcVo.banNo":"",
				"qcVo.bussName":"",
				"qcVo.addressCodeLv1":"",
				"qcVo.addressCode":"",
				"qcVo.bussAddrComb":"",
				"bussVo.bussName":"",
				"bussVo.bussAddrComb":"",
				"tabStatus":"1", 
				"pageUtil.totalCount":"0",
				"selCmpyType":"1",
				"bussVo.banNo":GUI,
				"bussVo.addressCodeLv1":"1",
				"bussVo.addressCode":"1", 
				"imageCode":captcha,
				"struts.token.name":"token",
				"token":token
			}
			
			# 公司簡介頁面
			headers = {
				"Referer":"http://gcis.nat.gov.tw/gps/gpsBussInit/GpsBussInit/init.do",
				"User-Agent":random.choice(USER_AGENT)
			}
	
			url = "http://gcis.nat.gov.tw/gps/gpsBussInit/GpsBussInit/query.do"	
			res = s.post(url, headers = headers, data = payload, timeout = 30)
			soup = BeautifulSoup(res.text , "html.parser")

			#查無資料則跳出
			if ("查無資料！" in soup.select("table")[0].text.encode("utf-8").strip()) or ("很抱歉" in soup.select("table")[0].text.encode("utf-8").strip()):
				return
			
			# 參數 for 公司詳細資料頁面
			paras = soup.select("tbody")[0].select("td")[2].select("a")[0]["href"].replace("javascript:doQueryDetail(", "").replace(")", "")
			paras = paras.split("','")
			break
		
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print exc_obj
			print(exc_type, exc_tb.tb_lineno)
			time.sleep(10)

			
	# 參數 for 公司詳細資料頁面
	regUnitCode = paras[1]
	capital = paras[3]
	address = paras[4].replace("'", "")
	
	# 公司詳細資料頁面使用相同headers
	headers_query = {
		"Referer":"http://gcis.nat.gov.tw/gps/gpsBussInit/GpsBussInit/query.do",
		"User-Agent":random.choice(USER_AGENT)
	}
	
	# 從公司詳細資料頁面獲取公司資料所在javascript的參數
	# 抓取最終頁面，公司資料頁，以獲得參數 for javascript
	url = "http://gcis.nat.gov.tw/gps/gpsBussQuery/GpsBussQuery/init.do"
	
	payload = {
		"bussVo.banNo":GUI,
		"bussVo.regUnitCode":regUnitCode,
		"tabStatus":"1",
		"bussVo.bussName":"+",
		"bussVo.registerFunds":capital,
		"bussVo.bussAddrComb":address
	}
	
	# 爬取頁面
	for i in range(15):
		try:
			res = s.post(url, headers = headers_query, data = payload, timeout = 30)
			break
		except:
			time.sleep(random.randint(30, 60))
	
	soup = BeautifulSoup(res.text , "html.parser")
	
	# 欲獲取的資料在js裡頭，抓取需要的參數
	tbpk = soup.select("#mapResult_bussVo_tbpk")[0]["value"]
	
	# javascript頁面
	url = "http://gcis.nat.gov.tw/gps/gpsBussQuery/GpsBussQuery/query.do"
	
	payload = {
		"tabStatus":"1",
		"bussVo.banNo":GUI,
		"bussVo.regUnitCode":regUnitCode,
		"bussVo.registerFunds":capital,
		"bussVo.tbpk":tbpk,
	}
	res = s.post(url, headers = headers_query, data = payload, timeout = 30)
	soup = BeautifulSoup(res.text, "lxml")
	
	# 公司狀態
	status = soup.select("#tabcm")[0].select("tr")[6].select("td")[1].text.encode("big5", "ignore")
	
	# 營業項目	
	code = soup.select("#tabcm")[0].select("tr")[10].select("td")[1].text.encode("big5", "ignore")
	code = code.split(" ")
	codes = ""
	for i in range(len(code)):
		if i%2== 1:
			codes = codes + code[i] + "\n"

	data_type = "商業".decode("utf-8").encode("big5", "ignore")

	return data_type, status, codes



# 分公司 http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do
def branch_crawler(GUI, detail_headers):

	entity_type = "BC"
	detail_url = "http://findbiz.nat.gov.tw/fts/query/QueryBrCmpyDetail/queryBrCmpyDetail.do"
	brBanNo = GUI
	objectId = entity_type + GUI

	detail_payload = {
		"brBanNo":brBanNo,
		"objectId":objectId,
	}

	while True:
		try:
			detail_res = requests.post(detail_url, data = detail_payload, headers = detail_headers, timeout = 30)
			# print detail_res.text.encode("utf-8")
			break
	
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(exc_type, exc_tb.tb_lineno)
				
	soup = BeautifulSoup(detail_res.text, "html.parser")

	status = soup.select("#tabCmpyContent")[0].select("tbody")[0].select("tr")[1].select("td")[1].text.encode("big5", "ignore").strip()

	if status == "":
		return
	codes = ""

	data_type = "分公司".decode("utf-8").encode("big5", "ignore")

	return data_type, status, codes


# 工廠
def factory_crawler(GUI):
	
	url = "http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
	s = requests.Session()

	headers = {
		"User-Agent":random.choice(USER_AGENT),
		"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do"
	}
	
	payload = {
		"errorMsg":"",
		"validatorOpen":"N",
		"rlPermit":"0",
		"userResp":"",
		"cPage":"",
		"qryCond":GUI,
		"infoType":"D",
		"cmpyType":"",
		"brCmpyType":"",
		"busmType":"",
		"qryType":"factType",
		"factType":"true",
		"lmtdType":"",
		"isAlive":"all"
	}
	
	res = s.post(url, headers = headers, data = payload, timeout = 30)
	soup = BeautifulSoup(res.text, "html.parser")
	moreLinkMouseOut = soup.select(".moreLinkMouseOut")

	if moreLinkMouseOut == []:
		return
	objectId = moreLinkMouseOut[0]["onclick"].replace("javascript:qryDetail('", "").replace("', false)", "")

	url = "http://findbiz.nat.gov.tw/fts/query/QueryFactDetail/queryFactDetail.do"

	payload = {
		"estbId":objectId[2:],
		"objectId":objectId,
	}

	headers = {
		"User-Agent":random.choice(USER_AGENT),
		"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
	}

	res = s.post(url, headers = headers, data = payload, timeout = 30)
	soup = BeautifulSoup(res.text, "html.parser")

	codes = ""
	status = soup.select("#tabFactContent")[0].select("tbody")[0].select("tr")[11].select("td")[1].text.encode("big5", "ignore").strip()

	data_type = "工廠".decode("utf-8").encode("big5", "ignore")

	return data_type, status, codes




	
def GcisCrawler(done_file, lastest_file, save_file):
	'''Crawl 經濟部商業司 商工登記公示資料
	Args:
		done_file:已爬取過國貿局資料的檔案名稱
		lastest_file:上一季爬取的檔案名稱
		save_file:此次要儲存的檔案名稱

	'''
	data = []
	count = 0

	# 本次要儲存的檔案已爬過的GUI
	crawled_data = CrawledDataGUI(save_file, colnames = ["GUI", "data type", "status", "codes", "new"])

	# 已爬取過國貿局資料的GUI
	print "Reading GUI of crawled file..."
	GUIs = CrawledDataGUI(done_file)
	for i in crawled_data:
		GUIs.remove(i)

	# 上一季爬取過的GUI
	print "Reading GUI of last file ..."
	lastest_GUI = CrawledDataGUI(lastest_file)
	lastest_GUI = set(lastest_GUI)


	# 若本次已爬取過，且存在在上一季名單則刪除該GUI
	for i in crawled_data:
		if i in lastest_GUI:
			lastest_GUI.remove(i)
	

	global USER_AGENT 
	global detail_headers	
	USER_AGENT = ReadParameter("user_agents.txt")  # get user_agent list

	# headers for company detail page
	detail_headers = {
		"User-Agent":random.choice(USER_AGENT),
		"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
	}


	# 利用GUI爬取公司資訊
	for GUI in GUIs:
		print "GUI:" + GUI

		new = "1"
		if GUI in lastest_GUI:
			new = "0"
			lastest_GUI.remove(GUI)	

		count = count + 1

		# 爬取公司資訊
		# 公司
		result = company_crawler(GUI, detail_headers)
		if result == None:
			# 商業
			result = bussiness_crawler(GUI)
			if result == None:
				# 分公司
				result = branch_crawler(GUI, detail_headers)
				if result == None:
					result = factory_crawler(GUI)
					if result == None:
						result = "", "", ""
		
		data_type = result[0]
		status = result[1]
		codes = result[2]

		data.append([GUI, data_type, status, codes, new])

		print "GCIS:" + str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())

		# 每一萬筆資料儲存一次檔案
		if str(count)[-3:] == "000":
			#存檔
			data = SaveData(save_file, data)
			print "files have been saved!"
			time.sleep(random.randint(30, 60))
			#break

		time.sleep(1)  # 每一筆結束後休息1秒

	SaveData(save_file, data)

	print "GUI in last TW data..."
	for i in lastest_GUI:
		data.append([i, "", "", "", "", "-1"])

	SaveData(save_file, data)

	print "Finally, done!"

