# -*- coding: utf-8 -*-
###爬取全台公司資訊###
# 1.下載「財政部財政資訊中心-全國營業(稅籍)登記資料集」(全國營業中公司資料)
# 2.利用全國資料集的公司統編查詢在國貿局的廠商進出口實績，將公司分為在國貿局有資料與在國貿局無資料兩種
# 3.抓取在國貿局有資料的公司在國貿局網站的資料
import csv
import urllib2 #urllib2.urlopen 
import zipfile #zipfile.ZipFile
import requests
from bs4 import BeautifulSoup
requests.packages.urllib3.disable_warnings()
import time
import datetime
import os.path
import sys
import random
from co_fun import SaveData


#下載 財政部財政資訊中心-全國營業(稅籍)登記資料集 http://data.gov.tw/node/9400
def DownloadTWCompany():
	'''
	Download and extract 財政部財政資訊中心-全國營業(稅籍)登記資料集 to get GUI
	for crawling data from Bureau of Foreign Trade
	'''
	print "下載全國營業(稅籍)登記資料集...".decode("utf-8").encode("big5")
	downloadurl = urllib2.urlopen('http://www.fia.gov.tw/opendata/bgmopen1.zip')
	zipcontent= downloadurl.read()
	with open("TWRAW.zip", 'wb') as f:
	    f.write(zipcontent)
	print "下載全國營業(稅籍)登記資料集完成".decode("utf-8").encode("big5")
	
	# 解壓縮檔案
	print "資料解壓縮...".decode("utf-8").encode("big5")
	with zipfile.ZipFile(open('TWRAW.zip', 'rb')) as f:
		f.extractall(".", pwd = "1234")
	
	print "資料解壓縮完成".decode("utf-8").encode("big5")





#利用全國營業登記資料中的統編欄位爬取國貿局網站進出口資料
def TradeCrawler(crawled_data, trade_file, no_trade_file, year):
	'''爬取國貿局進出口值與公司資訊
	Args:
		crawled_data:已爬取過的GUI list
		trade_file:國貿局有資料的檔案名稱
		no_trade_file:國貿局無資料的檔案名稱
		year:the last year of trade data

	'''

	trade_data = [] 	# 國貿局有資料
	no_trade_data = []  # 國貿局無資料
	last_GUI = ""  		# 最後爬取的GUI
	count = 0  			# 計數

	# 開啟全國營業登記資料檔
	with open("../raw data/BGMOPEN1.csv", "r") as f:
		
		reader = csv.reader(f, delimiter = ';')
		#skip前三列
		for i in range(3):
			next(reader, None)
		
		# 利用國貿局網站抓取廠商進出口登記資料，若不存在網站中則另外儲存
		for row in reader:
			count = count + 1
			# if count == 30:
			# 	break
			for try_time in range(100):  # 連線嘗試一百次
				try:
					data = []   # 暫存資料
					level = []  # 儲存實績值
					
					# 廠商進出口實績級距
					GUI = str(row[1].strip().zfill(8))  # 廠商統編				
					
					# GUI不存在在已儲存的檔案中
					if GUI not in crawled_data:
						url = "https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbji150Q2.asp?uni_no=" + GUI  # 實績查詢網站

						res = requests.get(url, verify = False, timeout = 30)			
						soup = BeautifulSoup(res.text, "html.parser")
				
						# 確認廠商資料是否存在，存在才抓取資料
						if soup.select("td ")[0].text.encode("iso-8859-1", "replace").strip().replace("　","") != "找不到查詢資料":
							note = True
							
							# 進出口值級距
							table = soup.select(".table1")[0]							
							if len(table.select("tr")) > 3:
								# 進出口統計年度
								tr = table.select("tr")[3:]
						
								years_value = {}  # 以年為key，進出口值為value
								for i in tr:
									y = i.select("td")[0].text.strip()[0:3]
									io_value = [i.select("td")[1].text.encode("iso-8859-1").decode("utf-8").encode("big5"), i.select("td")[2].text.encode("iso-8859-1").decode("utf-8").encode("big5")]
									years_value[y] = io_value
								
								# 將
								for i in range(5):
									if years_value.get(str(year-i)) == None:
										level.append("NA")
										level.append("NA")
										continue
									level.extend(years_value.get(str(year-i)))
						
							else:
								level = ["NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "NA"]
							
							# 公司英文名稱
							en_name = str(table.select(".td2bg1")[0].text.encode("iso-8859-1", "replace")).decode("utf-8", "replace").encode("big5", "replace") 

							###抓取廠商基本資訊###
							# 紀錄cookie以開啟廠商資料頁面
							cok = res.cookies
				
							headers = {'Cookie':cok.keys()[0] + '=' + cok.values()[0] + ';' + cok.keys()[1] + '=' + cok.values()[1] + ';CheckCode=53mzkh',
									   'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
							}
				
							pcy = soup.select(".arWebFont")[0].select('a')[0]['href'][-6:-2]  # 抓取廠商資料網址的pcy
							
							url = "https://fbfh.trade.gov.tw/rich/text/fbj/asp/fbje140Q2.asp?uni_no=" + GUI + "%20&pcy=" + pcy  # 廠商資料網址
							res = requests.get(url, verify = False, headers = headers, timeout = 30)
							soup = BeautifulSoup(res.text, "html.parser")
				
							#爬取網站頁面
							td2bg1 = soup.select(".td2bg1")
							register_date = str(td2bg1[1].text.strip().encode("iso-8859-1")) 	 # 國貿局進出口原始登記日期
							tel1 = str(td2bg1[7].text.strip().encode("iso-8859-1")) 			 # 電話號碼1
							tel2 = str(td2bg1[8].text.strip().encode("iso-8859-1")) 			 # 電話號碼2
							fax = str(td2bg1[9].text.strip().encode("iso-8859-1"))   			 # 傳真號碼
							web = str(td2bg1[12].text.strip().encode("iso-8859-1")) 			 # 網址
							mail = str(td2bg1[13].text.strip().encode("iso-8859-1", "replace"))  # mail
							import_q = str(td2bg1[14].text.strip().encode("iso-8859-1"))         # 進口資格
							export_q = str(td2bg1[15].text.strip().encode("iso-8859-1"))         # 出口資格
							boss = str(soup.select(".arWebFont")[2].text.encode("iso-8859-1", "replace")) # 代表人				

						else:
							note = False
				
						# colnames:營業地址;統一編號;總機構統一編號;營業人名稱;資本額;設立日期;使用統一發票;行業代號;名稱;行業代號;名稱;行業代號;名稱;行業代號;名稱
						# 營業登記資料
						head_gui = row[2] # 總機構統一編號
						address = row[0]  # 公司地址
						cn_name = row[3]  # 公司名稱
						capital = row[4]  # 資本額
						establish_date = row[5]		
						gui = row[6]  # 是否使用統一發票
						industry_code1 = row[7]  # 行業代碼1
						industry_name1 = row[8]  # 名稱1
						industry_code2 = row[9]  # 行業代碼2
						industry_name2 = row[10] # 名稱2
						industry_code3 = row[11] # 行業代碼3
						industry_name3 = row[12] # 名稱3
						industry_code4 = row[13] # 行業代碼4
						industry_name4 = row[14] # 名稱4
						industry = industry_code1 + " " + industry_name1 + "\n" + industry_code2 + " " + industry_name2 + "\n" + industry_code3 + " " + industry_name3 + "\n" + industry_code4 + " " + industry_name4
				
						# 依據是否存在進出口資料儲存資料
						if note == True:
							data = [GUI, head_gui, cn_name, en_name, address, establish_date, boss, capital, gui, industry.strip(), \
							register_date, tel1, tel2, fax, web, mail, import_q, export_q]
							for i in range(len(data)):
								data[i] = data[i].decode("utf-8", "replace").encode("big5", "replace")
							data.extend(level)
							# 將資料加入所有存在的資料中
							trade_data.append(data)
				
						else:
							data = [GUI, head_gui, cn_name, address, establish_date, capital, gui, \
							industry_code1, industry_name1, industry_code2, industry_name2, industry_code3, industry_name3]
							for i in range(len(data)):
								data[i] = data[i].decode("utf-8", "replace").encode("big5", "replace")
							no_trade_data.append(data)

				
						# 每一萬筆資料儲存一次檔案
						if str(count)[-4:] == "0000":
							#存檔
							trade_data = SaveData(trade_file, trade_data)
							no_trade_data = SaveData(no_trade_file, no_trade_data)	
						
							print "files have been saved!"
							
							time.sleep(random.randint(90, 150))
				
		
					print str(count) + "......is done!  GUI:" + GUI + "  " +  str(datetime.datetime.now())
					
					break

				except Exception as e:
					print "something is wrong......"
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]  # 執行程式檔名
					print "GUI:" + GUI + ", " + str(datetime.datetime.now())
					print url
					print(exc_type, exc_tb.tb_lineno)

					trade_data = SaveData(trade_file, trade_data)
					no_trade_data = SaveData(no_trade_file, no_trade_data)	
					#res = requests.get(url, headers = {"Connection":"close"})
					print "files have been saved!"
					time.sleep(random.randint(30, 60))

					if last_GUI != GUI:
						# 紀錄錯誤訊息
						log = open("log.txt", "ab")
						log.write(str(datetime.datetime.now()) + ", GUI:" + GUI + ", " + url + \
							"file name:" + str(fname) + ", " + \
							"status:" + str(res.status_code) + ", " + \
							"line: " + str(exc_tb.tb_lineno) + ", " + str(exc_type) + ", " + str(e) + "\n")
						log.close()

					last_GUI = GUI
					continue

	trade_data = SaveData(trade_file, trade_data)
	no_trade_data = SaveData(no_trade_file, no_trade_data)

	print "There are " + str(count) + " companies have been crawled."


