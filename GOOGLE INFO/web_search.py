# -*- coding: utf-8 -*-
#google map api for company's address and tel

from bs4 import BeautifulSoup
import requests
import urllib
import json
import csv
import random
import time
import os.path


# 讀取keys檔案中api所需的key
def GetKeys():
	'''讀取keys檔案中api所需的key
	Return:
		keys:list of keys
	'''
	with open("key.txt", "r") as f:
		keys = [_.strip() for _ in f.readlines()]
	return keys


# get company infomation by google api
def GetCompanyInfo(key, company_name):
	'''爬取google api，獲得公司電話與地址
	Args:
		key:爬取api所需的金鑰
		company_name:公司名稱
	Return:
		address:搜尋結果地址
		tel:搜尋結果電話
	'''
	repeat_time = 0
	while True:
		repeat_time += 1
		# autocomplete api for place id
		place_id_api = "https://maps.googleapis.com/maps/api/place/autocomplete/json?input=" + urllib.quote(company_name)  + "&key=" + key
		res = requests.get(place_id_api)
		js = json.loads(res.text)
		
		print js["status"]
		# get company place id
		if js["status"] == "OK": # 指出未發生任何錯誤，並且已至少傳回一個結果
			place_id = js["predictions"][0]["place_id"]
	
		elif js["status"] == "ZERO_RESULTS": # 指出搜尋成功，但是未傳回任何結果。如果傳遞了遠端位置中的 bounds 給搜尋，就可能發生這種情況
			return "", ""
		
		elif js["status"] == "REQUEST_DENIED":  # 指出您的要求已被拒絕，通常是因為缺少無效的key參數
			return "REQUEST_DENIED"
	
		elif js["status"] == "OVER_QUERY_LIMIT": # 指出已超出您的配額
			return "OVER_QUERY_LIMIT", ""

		else: # INVALID_REQUEST 通常指出缺少 input 參數
			return "", ""

		# details api for company infomaiton
		info_api = "https://maps.googleapis.com/maps/api/place/details/json?placeid=" + place_id + "&key=" + key
		
		headers = {"accept-language":"zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4"}  # 地址顯示中文
		res = requests.get(info_api, headers = headers)
		js = json.loads(res.text)
		
		print js["status"]
		# 如果狀態不是Ok則重新爬取該間公司
		if js["status"] == "NOT_FOUND":
			return "", ""

		elif js["status"] != "OK":			
			if repeat_time == 10:
				return "", ""

			continue

		else:
			print "OK"
		
		# check if the result is Taiwanese company
		country = js["result"]["address_components"]
		
		# 檢查抓取到的是否為台灣公司
		if country[-2]["types"][0] == "country" or country[-1]["types"][0] == "country":
			if country[-2]["short_name"] != "TW" and country[-1]["short_name"] != "TW":
				return "", ""
	
		# get address and tel data
		address = js["result"]["formatted_address"].encode("big5", "ignore")
		
		try:
			tel = js["result"]["formatted_phone_number"]
		except:
			tel = ""

		return address, tel

# # 存檔
# def SaveFile(file_name, data):
# 	'''如果檔案存在存檔，如果檔案不存在建立一個含有欄位名稱的新檔案
# 	Args:
# 		file_name:檔案名稱
# 		data:要儲存的data list
# 	Return:
# 		data:an empty list
# 	'''
# 	if os.path.exists(file_name) is False:
# 		data.insert(0, ["company name", "GUI", "google address", "google tel"])
# 		#data.append(["company name", "google address", "google tel"])

# 	with open(file_name, "ab") as f:
# 		w = csv.writer(f)
# 		w.writerows(data)

# 	data = []
# 	return data

# # 檔案中的公司名稱
# # 
# def CompanyCollection(file_name, company_GUI_col):
# 	'''蒐集檔案中的GUI
# 	Args:
# 		file_name:檔案名稱
# 		company_GUI_col:公司GUI所在行數位置
# 	Return:
# 		li:List of GUI
# 	'''
# 	li = []
# 	if os.path.exists(file_name) is True:
# 		with open(file_name, "r") as f:
# 			reader = csv.reader(f, delimiter = ",")
# 			next(reader, None)  # ignore column name
# 			for i in reader:
# 				li.append(i[company_GUI_col - 1])

# 	return li


# def main():
# 	# google api keys
# 	keys = GetKeys()
# 	key = random.choice(keys)
# 	file_name = "../raw data/google_info.csv"
	
# 	# tw company
# 	# company_names = CompanyCollection("..\\raw data\BGMOPEN1.csv", 4, 4, 2)
# 	company_names = {}
# 	with open("../raw data/BGMOPEN1.csv", "r") as f:
# 			reader = csv.reader(f, delimiter = ",")
# 			for i in range(3):
# 				next(reader, None)  # ignore column name
# 			for i in reader:
# 				try:
# 					i = i[0].split(";")
# 					# if i[1] not in google_info:
# 					company_names[i[1]] = i[3]
# 				except:
# 					continue
# 	print len(company_names)

# 	# company has been crawled
# 	google_info = CompanyCollection(file_name, 2)
# 	print len(google_info)
	
# 	# data for saving
# 	data = []
	
# 	count = 0

# 	limit_time = 0
	
# 	# 爬取全台公司名稱搜尋結果
# 	for GUI in company_names.keys():
# 		#print GUI
# 		# 如果該GUI已爬取過，則跳下一個GUI
# 		if GUI in google_info:
# 			continue
# 		company_name = company_names[GUI]
# 		count = count + 1

# 		while True:
# 			try:
# 				# address, tel = GetCompanyInfo(key, company_name.decode("big5").encode("utf-8"))
# 				address, tel = GetCompanyInfo(key, company_name)
				
# 				# 可能是key無效，重新抓一個key
# 				if address == "REQUEST_DENIED":
# 					print "request_denied"
# 					keys.remove(key)  # 刪除失效的key
# 					key = random.choice(keys)
# 					continue

# 				if address == "OVER_QUERY_LIMIT":
# 					if limit_time == 100:
# 						break
# 					limit_time += 1
# 					time.sleep(300)
# 					continue

# 			except:
# 				data = SaveFile(file_name, data)

# 			break

# 		# 超過當日抓取配額則存擋跳出迴圈
# 		if address == "OVER_QUERY_LIMIT":
# 			data = SaveFile(file_name, data)
# 			break

# 		data.append([company_name.decode("utf-8").encode("big5", "ignore"), GUI, address, tel])		
# 		print str(count) + " is done!" 
		
# 		#time.sleep(random.randint(3, 5))

# 		if count%10000 == 0:
# 			SaveFile(file_name, data)

# 	SaveFile(file_name, data)
	


# if __name__ == '__main__':
#  	main()


#web = ["arkdan.com.tw", "aromalife.com.tw", "arolite.com.tw","artco.com.tw", "artemis.com.tw"]
web = ["aromalife.com.tw"]
# web = ["ame"]
keys = GetKeys()
key = random.choice(keys)
print key

for i in web:
	print GetCompanyInfo(key, i)

