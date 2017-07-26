# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

from co_fun import ReadParameter
from co_fun import CrawledDataGUI
from co_fun import SaveData
import csv
import requests
import sys
import os.path
import re
import random
import time
import datetime


def GcisCrawler(done_file, lastest_file, save_file):
	'''Crawl 經濟部商業司 商工登記公示資料
	Args:
		done_file:已爬取過國貿局資料的檔案名稱
		lastest_file:上一季爬取的檔案名稱
		save_file:此次要儲存的檔案名稱

	'''

	
	data = []

	# 本次要儲存的檔案已爬過的GUI
	crawled_data = CrawledDataGUI(save_file, colnames = ["GUI", "data type", "status", "codes", "factory", "new"])

	# 已爬取過國貿局資料的GUI
	print "Reading GUI of crawled file..."
	GUIs = CrawledDataGUI(done_file)
	for i in crawled_data:
		GUIs.remove(i)

	# 上一季爬取過的GUI
	print "Reading GUI of last file ..."
	lastest_GUI = CrawledDataGUI(lastest_file)
	lastest_GUI = set(lastest_GUI)



	for i in crawled_data:
		if i in lastest_GUI:
			lastest_GUI.remove(i)

	USER_AGENT = ReadParameter("user_agents.txt")  # get user_agent list
	s = requests.Session()

	# GUI搜尋頁面網址
	url = "http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"

	headers = {
		"User-Agent":random.choice(USER_AGENT),
		"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do"
	}

	print "start crawling......"
	count = 0
	for GUI in GUIs:
		count = count + 1
		if count == 30:
			break
		data_type = ""  # 資料種類，公司、分公司、商業、工廠
		codes = ""  	# 公司營業項目
		status = ""  	# 公司營運狀態
		factory = "0"	# 該公司行號是否有工廠
		new = "1"		# 是否為新建立公司


		if GUI in lastest_GUI:
			new = "0"
			lastest_GUI.remove(GUI)

		payload = {
			"validatorOpen":"N",
			"rlPermit":"0",
			"qryCond":GUI,
			"infoType":"infoDefault",
			"infoDefault":"true",
			"infoAddr":"",
			"qryType":"cmpyType",
			"cmpyType":"true",
			"qryType":"brCmpyType",
			"brCmpyType":"true",
			"qryType":"busmType",
			"busmType":"true",
			"qryType":"factType",
			"factType":"true",
			"qryType":"lmtdType",
			"lmtdType":"true",
			"isAlive":"all"
		}
		
		for i in range(5):
			try:
				res = s.post(url, headers = headers, data = payload, timeout = 30)
				break
	
			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  # 執行程式檔名
				print "GUI:" + GUI + ", " + str(datetime.datetime.now())
				print(exc_type, exc_tb.tb_lineno)
				data = SaveData(save_file, data)
				time.sleep(random.randint(30, 45))
	
				headers = {
					"User-Agent":random.choice(USER_AGENT),
					"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do"
				}

				continue
				
		soup = BeautifulSoup(res.text, "html.parser")
		
		try:
			# 資料框
			data_infos = soup.select(".panel-body")

			# 詳細資料連結
			moreLinkMouseOut = soup.select(".moreLinkMouseOut")
			
			# 搜尋結果只有一筆符合條件
			if len(data_infos) == 2:
				data_info = data_infos[0]
				data_info = data_info.text.encode("big5", "ignore").split(",")
				
				# 無法找到符合條件的查詢結果
				if len(data_infos[0].select("font")) != 0:
					data.append([GUI, data_type, status, codes, factory, new])
					continue

				# 搜尋結果不正確
				if data_info[0].replace("統一編號:".decode("utf-8").encode("big5"), "").strip() != GUI and data_info[1].replace("統一編號:".decode("utf-8").encode("big5"), "").strip() != GUI:
					data.append([GUI, data_type, status, codes, factory, new])
					continue

				# 獲取公司詳細資料網址
				objectId = moreLinkMouseOut[0]["onclick"][11:-2]

									
			# 若搜尋結果有多個，選擇資料種類為"公司"或"商號"的資料框
			else:
				for i in range(len(data_infos)-1):
					data_info_temp = data_infos[i].text.encode("big5", "ignore").split(",")
					if data_info_temp[0].replace("統一編號:".decode("utf-8").encode("big5"), "").strip() == GUI or data_info_temp[1].replace("統一編號:".decode("utf-8").encode("big5"), "").strip() == GUI:
						if moreLinkMouseOut[i]["onclick"][11:-2][0:2] in ["HC", "HB"]:
							data_info = data_infos[i].text.encode("big5", "ignore").split(",")
							# 獲取公司詳細資料post所需資訊
							objectId = moreLinkMouseOut[i]["onclick"][11:-2]
						# 如果有其中一個資料框的資料種類為工廠
						if moreLinkMouseOut[i]["onclick"][11:-2][0:2] == "HF":
							factory = "1"
				
			# 網址參數代碼前兩碼，公司、分公司or商業
			entity_type = objectId[0:2]	
			# print entity_type

			# 資料種類
			if entity_type == "HC":  # 公司
				data_type = "公司".decode("utf-8").encode("big5", "ignore")

			elif entity_type == "BC":  # 分公司
				data_type = "分公司".decode("utf-8").encode("big5", "ignore")
				data.append([GUI, data_type, status, codes, factory, new])

				print "GCIS:" + str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())
				continue

			elif entity_type == "HB":  # 商號
				data_type = "商號".decode("utf-8").encode("big5", "ignore")

			elif entity_type == "HF":  # 工廠
				data_type = "工廠".decode("utf-8").encode("big5", "ignore")
				status = data_info[4].replace("登記現況:".decode("utf-8").encode("big5"), "").strip()
				factory = "1"
				data.append([GUI, data_type, status, codes, factory, new])

				print "GCIS:" + str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())
				continue
			
			else:  # 其他
				data_type = data_info[6].replace("資料種類:".decode("utf-8").encode("big5"), "").strip()

			status = data_info[3].replace("登記現況:".decode("utf-8").encode("big5"), "").strip()

		except Exception as e:
			print "data type..."
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  # 執行程式檔名
			print "GUI:" + GUI + ", " + str(datetime.datetime.now())
			print(exc_type, exc_tb.tb_lineno)
			data.append([GUI, data_type, status, codes, factory, new])
			data = SaveData(save_file, data)
			continue
		
		# 公司
		if entity_type == "HC":
			detail_url = "http://findbiz.nat.gov.tw/fts/query/QueryCmpyDetail/queryCmpyDetail.do"
			banKey = ""
			banNo = GUI
			banId = "#tabCmpyContent"
	
		# 商業
		if entity_type == "HB":
			detail_url = "http://findbiz.nat.gov.tw/fts/query/QueryBusmDetail/queryBusmDetail.do"
			banKey = objectId[10:]
			banNo = GUI
			banId = "#tabBusmContent"
	
		# payload for company detail page
		detail_payload = {
			"banNo":banNo,
			"banKey":banKey,
			"objectId":objectId,
		}
	
		# headers for company detail page
		detail_headers = {
			"User-Agent":random.choice(USER_AGENT),
			"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
		}
	
		# company detail page crawling
		for i in range(3):
			try:
				detail_res = s.post(detail_url, data = detail_payload, headers = detail_headers, timeout = 30)
				break

			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  # 執行程式檔名
				print "GUI:" + GUI + ", " + str(datetime.datetime.now())
				print(exc_type, exc_tb.tb_lineno)
				data = SaveData(save_file, data)
				time.sleep(random.randint(30, 45))
	
				detail_headers = {
					"User-Agent":random.choice(USER_AGENT),
					"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
				}
				continue
	
	
		soup = BeautifulSoup(detail_res.text, "html.parser")
	
		try:
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
				
			# 多個營業項目
			if entity_type == "HC":  # 公司
				code = code.encode(formatter = "html")  # 利用&nbsp;分行
				pos = code.find("&nbsp;")
				while pos != -1:
					code = code[pos+6:]
					pos = code.find("&nbsp;")
					codes = codes + code[(pos-7):pos] + "\n"
				codes = codes.replace("/>", "").replace("</td", "").replace("br>", "").strip()

			if entity_type == "HB":  # 商業
				code = code.text.split("	")
				for c in code:
					pos = re.search("[A-Z]", c)
					if pos != None:
						pos = pos.group()
						pos = c.find(pos)
						codes = codes + c[pos:pos+7] + "\n"
				codes = codes.strip()
										
		except:
			print "other info..."
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  # 執行程式檔名
			print "GUI:" + GUI + ", " + str(datetime.datetime.now())
			print(exc_type, exc_tb.tb_lineno)
			#data.append([GUI, data_type, status, codes, factory, new])
			#data = SaveData(save_file, data)
			continue

		data.append([GUI, data_type, status, codes, factory, new])

		print "GCIS:" + str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())

		# 每一千筆資料儲存一次檔案
		if str(count)[-4:] == "0000":
			#存檔
			data = SaveData(save_file, data)
			print "files have been saved!"
			# time.sleep(random.randint(90, 150))
			time.sleep(random.randint(30, 60))

		time.sleep(1)  # 每一筆結束後休息1秒

	SaveData(save_file, data)

	print "GUI in last TW data..."
	for i in lastest_GUI:
		data.append([i, "", "", "", "", "-1"])

	SaveData(save_file, data)

	print "Finally, done!"


	