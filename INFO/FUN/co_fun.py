# -*- coding: utf-8 -*-
import os
import csv


#Save File
def SaveData(file_name, save_list):
	'''Save file 
	Args:
		file_name:File name for saving
		save_list:List of saving data

	Return:
		save_list:Empty list for saving new data
	'''
	with open(file_name, "ab") as f:
		w = csv.writer(f)
		w.writerows(save_list)
	save_list = []
	return save_list


#記錄新檔案中已爬取過的GUI，避免重複爬取
def CrawledDataGUI(file_name, **kwargs):
	'''Get crawled data list.
	Args:
		file_name:File name
		**kwargs: Headers of saving file.
	Return:
		crawled_data:Crawled data list.
	'''
	# 如果檔案存在，記錄所有GUI
	crawled_data = []
	if os.path.exists(file_name):
		with open(file_name, "r") as f:
			reader = csv.reader(f, delimiter = ",")
			next(reader, None)
			#儲存GUI
			for i in reader:
				crawled_data.append(i[0].strip().zfill(8)[0:8])

	# 如果檔案不存在，建立檔案，並寫上寫檔案的header
	else:
		#更改欄位編碼
		header = kwargs["colnames"]
		for i in range(len(header)):
			header[i] = header[i].decode("utf-8").encode("big5")
		
		#存檔
		SaveData(file_name, [header])

	return crawled_data


#read parameter file
def ReadParameter(file_name):
	'''讀取爬蟲所需參數的txt檔案
	Args:
		file_name:file name

	Return:
		result_list:參數list
	'''
	result_list = []
	with open(file_name, "r") as f:
		for line in f:
			result_list.append(line.replace("\n", ""))
	
	return result_list


