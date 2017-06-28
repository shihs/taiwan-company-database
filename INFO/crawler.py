# -*- coding: utf-8 -*-
from co_fun import SaveData
from co_fun import CrawledDataGUI
from trade_fun import DownloadTWCompany
from trade_fun import TradeCrawler
from gcis_fun import GcisCrawler
import time
import os


def trade(date, year, latest_month):
	'''爬取國貿局資料
	Args:
		date:本次爬取存的檔案名稱的日期
		year:the last year of trade data
		latest_month:the last month of trade data
		
	'''

	### 全國營業登記檔案下載
	#DownloadTWCompany()


	# 國貿局有資料
	colnames = ["GUI", "總機構GUI", "中文名稱", "英文名稱", "地址", "設立日期", "代表人", "資本額", "使用統一發票", "行業代碼與名稱",\
				"進出口原始登記日期", "電話1", "電話2", "傳真", "網址", "email", "進口資格", "出口資格"]	

	# 國貿局進出口實績最多有五年的資料，所有進出口額年份，儲存在header
	# 最新一年
	header = [str(year) + "-01-" + str(latest_month).zfill(2) + "進口", str(year) + "-01-" + str(latest_month).zfill(2) + "出口"]
	# 前四年
	for i in range(4):
		header.append(str(year - i - 1) + "-01-12進口")
		header.append(str(year - i - 1) + "-01-12出口")

	# 加上進出口額年份colnames
	colnames.extend(header)
	crawled_data = CrawledDataGUI(trade, colnames = colnames)


	# 國貿局無資料
	colnames = ["GUI", "總機構GUI", "中文名稱", "地址", "設立日期", "資本額", "使用統一發票", \
				"行業代碼1", "名稱1", "行業代碼2", "名稱2", "行業代碼3", "名稱3", "行業代碼4", "名稱4"]
	crawled_data.extend(CrawledDataGUI(no_trade, colnames = colnames))


	### 國貿局網站爬取
	trade = "../raw data/trade_" + date + ".csv"		# 國貿局有資料的檔案名稱
	no_trade = "../raw data/no_trade_" + date + ".csv"  # 國貿局無資料的檔案名稱

	# 開始爬取
	TradeCrawler(crawled_data, trade, no_trade, year)




def gcis(date, last_date):
	'''爬取經濟部商業司公示資料
	Args:
		date:本次爬取的將存的檔案名稱的日期
		last_date:本次爬取存的檔案名稱的日期
		
	'''

	trade = "../raw data/trade_" + date + ".csv"			# 本次爬取國貿局有資料的檔案名稱
	last_file = "../raw data/tw_data_" + last_date + ".csv"	# 上次全台公司資料庫統整的檔案名稱
	file_name = "../raw data/gcis_" + date + ".csv"  	# 本次爬取經濟部商業司有資料的檔案名稱
	
	# 開始爬取
	GcisCrawler(trade, last_file, file_name)



				
if __name__ == '__main__':

	start = time.time()

	# year = input("please enter last year of trade data:")
	# latest_month = input("please enter last month of trade data:")
	last_date = str(input("please enter date for last saved file name:")).zfill(4)
	date = str(input("please enter date for saved file name:")).zfill(4)

	trade = "../raw data/trade_" + date + ".csv"		# 國貿局有資料的檔案名稱
	if not os.path.exists(trade):
		trade(date, year, latest_month)

	gcis(date, last_date)

	end = time.time()
	elapsed = end - start

	print "Time taken: ", elapsed, "seconds."


