# -*- coding: utf-8 -*-
from co_fun import ReadParameter
from co_fun import CrawledDataGUI
from co_fun import SaveData
from bs4 import BeautifulSoup
import requests
import random
import time
import datetime
import sys
import os



def get_proxy():
	'''Get IPs from http://www.proxyserverlist24.top/

	Return:
		ips:dictaionary of IPs with ip keys and http values
	'''

	proxies = []
	url = "http://www.proxyserverlist24.top/"
	res = requests.get(url, timeout = 30)
	soup = BeautifulSoup(res.text, "lxml")

	for artical in soup.select(".post-title"):
		artical_url = artical.select("a")[0]["href"]
		# print artical_url
		time.sleep(1)
		artical_res = requests.get(artical_url, timeout = 30)
		artical_soup = BeautifulSoup(artical_res.text, "lxml")

		try:
			for proxy in artical_soup.select(".alt2")[0].text.encode("utf-8").split("\n"):
				if proxy in ["", "Check Report (IP:Port):"]:
					continue
				proxies.append(proxy)
		except:
			continue

	return proxies


def info_crawler(GUI, PROXY_LIST, ip, headers):
	'''以GUI爬取商工登記資料查詢(https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do)結果
	Args:
		GUI:公司統一編號
	'''
	s = requests.Session()
	s.keep_alive = False

	url = "https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do"
	s.get(url)

	url = "https://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
	payload = {
		"validatorOpen":"N",
		"rlPermit":"0",
		"qryCond":GUI,
		"infoType":"D",
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
		"isAlive":"all",
	}

	proxy = {"https":"https://" + ip}

	while True:
		try:
			# GUI 搜尋結果
			print ip
			res = s.post(url, data = payload, headers = headers, proxies = proxy, timeout = 10)
			break
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			
			PROXY_LIST.remove(ip)

			if len(PROXY_LIST) == 0:
				PROXY_LIST = get_proxy()

			ip = random.choice(PROXY_LIST)
			proxy = {"https":"https://" + ip}

			headers = {
				"User-Agent":random.choice(USER_AGENT),
				"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
			}

	soup = BeautifulSoup(res.text, "lxml")
	# 檢查是否被BANNED，recaptcha圖
	if len(soup.select(".g-recaptcha")) != 0:
		print "BANNED!"
		# return soup.select(".g-recaptcha")[0]["data-sitekey"]
		return "BANNED"

	# GUI搜尋是否有結果
	if len(soup.select(".hover")) == 0:
		return "", "", "", PROXY_LIST, ip

	# GUI搜尋有結果則抓取其他資料
	GUI_url = "https://findbiz.nat.gov.tw"+ soup.select(".hover")[0]["href"]
	# time.sleep(0.5)
	
	while True:
		try:
			print ip
			GUI_res = s.get(GUI_url, headers = headers, proxies = proxy, timeout = 10)
			break
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)
			
			PROXY_LIST.remove(ip)

			if len(PROXY_LIST) == 0:
				PROXY_LIST = get_proxy()

			ip = random.choice(PROXY_LIST)
			proxy = {"https":"https://" + ip}

			headers = {
				"User-Agent":random.choice(USER_AGENT),
				"Referer":"http://findbiz.nat.gov.tw/fts/query/QueryList/queryList.do"
			}

	GUI_soup = BeautifulSoup(GUI_res.text, "lxml")

	# 資料種類：公司、商業、分公司、工廠、有限合夥
	info = GUI_soup.select(".container-fluid")[0].select(".col-xs-12")[-1].select("span")[0].text.encode("utf-8").split("：")
	data_type = info[-2].replace("名稱", "").replace(GUI, "").strip()
	
	# 營業項目	
	bussiness_codes = ""
	table = GUI_soup.select(".padding_bo")[0].select(".table-striped")[0].select("tr")

	status = ""
	### 依資料種類抓取公司狀態及營業項目 ###
	if data_type == "公司":
		status = table[1].select("td")[1].text.encode("utf-8").strip()

		codes = table[-2].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\r", "").split("\n")
		for i in range(2, len(codes), 3):
			bussiness_codes = bussiness_codes + codes[i] + "\n"
		bussiness_codes = bussiness_codes.strip()
			
	elif data_type == "商業":
		if "現況" in table[10].select("td")[0].text.encode("utf-8"):
			status = table[10].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\n", "").strip()
		else:
			for i in range(11, len(table)):
				if "現況" in table[i].select("td")[0].text.encode("utf-8"):
					status = table[i].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\n", "").strip()

		codes = table[-1].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\r", "").split("\n")
		for i in range(3, len(codes), 4):
			bussiness_codes = bussiness_codes + codes[i-2] + "\n"
		bussiness_codes = bussiness_codes.strip()

	elif "工廠" in data_type:
		data_type = "工廠"
		status = table[11].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\n", "").strip()

	elif data_type == "分公司":
		status = table[1].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\n", "").strip()

	elif data_type == "有限合夥":
		status = table[6].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\n", "").strip()

		codes = table[-1].select("td")[1].text.encode("utf-8").replace("\t", "").replace("\r", "").split("\n")
		for i in range(3, len(codes), 4):
			bussiness_codes = bussiness_codes + codes[i-2] + "\n"
		bussiness_codes = bussiness_codes.strip()
	######

	return data_type, status, bussiness_codes, PROXY_LIST, ip

	





def GcisCrawler(done_file, save_file):
	'''Crawl 經濟部商業司 商工登記公示資料
	Args:
		done_file:已爬取過國貿局資料的檔案名稱
		save_file:此次要儲存的檔案名稱
	'''
	data = []
	count = 0

	# 本次要儲存的檔案已爬過的GUI
	crawled_data = CrawledDataGUI(save_file, colnames = ["GUI", "data type", "status", "codes"])

	# 已爬取過國貿局資料的GUI
	print "Reading GUI of crawled file..."
	GUIs = CrawledDataGUI(done_file)
	for i in crawled_data:
		GUIs.remove(i)

	global USER_AGENT 
	USER_AGENT = ReadParameter("user_agents.txt")  # get user_agent list
	headers = {
		"User-Agent":random.choice(USER_AGENT),
		"Referer":"https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do",
	}

	# get proxy
	PROXY_LIST = get_proxy()
	ip = random.choice(PROXY_LIST)

	# 利用GUI爬取公司資訊
	for GUI in GUIs:
		print "GUI:" + GUI

		count = count + 1

		# 爬取公司資訊
		while True:
			try:
				result = info_crawler(GUI, PROXY_LIST, ip, headers)
				# if len(result) != 1:
				# 	break
				if result != "BANNED":
					data_type = result[0].decode("utf-8", "ignore").encode("big5", "ignore")
					status = result[1].decode("utf-8", "ignore").encode("big5", "ignore")
					codes = result[2].decode("utf-8", "ignore").encode("big5", "ignore")
					PROXY_LIST = result[3]
					ip = result[4]
					break

				time.sleep(120)
				data = SaveData(save_file, data)
				print "file has been saved!"
				if len(PROXY_LIST) == 0:
					PROXY_LIST = get_proxy()
				ip = random.choice(PROXY_LIST)
				headers = {
					"User-Agent":random.choice(USER_AGENT),
					"Referer":"https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do",
				}

				
			except IndexError:
				print "IndexError!"
				data_type, status, codes = "", "", ""
				break

			except Exception as e:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				
				data = SaveData(save_file, data)
				print "file has been saved!"
				if len(PROXY_LIST) == 0:
					PROXY_LIST = get_proxy()
				ip = random.choice(PROXY_LIST)
				headers = {
					"User-Agent":random.choice(USER_AGENT),
					"Referer":"https://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do",
				}

		
		data.append([GUI, data_type, status, codes])

		print "GCIS:" + str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())

		# 每五千筆資料儲存一次檔案
		if count%5000 == 0:
			#存檔
			data = SaveData(save_file, data)
			print "files have been saved!"
			time.sleep(random.randint(5, 10))

		time.sleep(0.5)  # 每一筆結束後休息0.5秒

	SaveData(save_file, data)

	print "Finally, done!"

