﻿


<b>﻿<h1>全台公司資料爬蟲程式</br></h1></b>

<b>環境</b><p>
Windows7/python2.7<p>
</br>
</br>
</br>
<b>全台公司資料來源共有四個部份</b>

1.<a href="http://data.gov.tw/node/9400">財政部財政資訊中心-全國營業(稅籍)登記資料集 </a>(open data)</br>
&nbsp;&nbsp;&nbsp;獲得全台目前營業登記中的公司名稱、GUI、行業代碼</br>

2.<a href="https://fbfh.trade.gov.tw/rich/text/indexfbOL.asp">國貿局進出口資料 </a></br>
&nbsp;&nbsp;&nbsp;透過GUI爬取有進出口值的公司資訊，包含公司英文名稱與電話

3.<a href = "http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do">商工登記公示資料查詢服務 </a></br>
&nbsp;&nbsp;&nbsp;透過GUI爬取公司的種類、營業狀態與營業項目</br>
&nbsp;&nbsp;&nbsp;公司種類分為：公司、分公司、工廠、商業及有限合夥

4.Google API
<a href="https://developers.google.com/places/web-service/autocomplete?hl=zh-tw">地點自動完成 </a>、
<a href="https://developers.google.com/places/web-service/details?hl=zh-tw">地點詳細資料 </a></br>
&nbsp;&nbsp;&nbsp;國貿局網站上的公司資訊有些未被更新，利用Google API獲取最新的公司電話與地址
(需要申請key才能使用)</br>

</br>
</br>
</br>

<b>程式分為兩個部份</b>

1.公開資料，<a href="https://github.com/shihs/taiwan-company-database/tree/master/INFO">公司基本資訊</a></br>
&nbsp;&nbsp;&nbsp;來源是
<a href="http://data.gov.tw/node/9400">財政部財政資訊中心-全國營業(稅籍)登記資料集</a>、
<a href="https://fbfh.trade.gov.tw/rich/text/indexfbOL.asp">國貿局進出口資料 </a>、
<a href = "http://findbiz.nat.gov.tw/fts/query/QueryBar/queryInit.do">商工登記公示資料查詢服務 </a>


2.GOOGLE API <a href="https://github.com/shihs/taiwan-company-database/tree/master/GOOGLE%20INFO">公司電話與地址</a></br>
&nbsp;&nbsp;&nbsp;<a href="https://developers.google.com/places/web-service/autocomplete?hl=zh-tw">地點自動完成 </a>、
<a href="https://developers.google.com/places/web-service/details?hl=zh-tw">地點詳細資料 </a></br>

</br>
</br>