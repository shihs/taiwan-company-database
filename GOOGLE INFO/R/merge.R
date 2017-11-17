

setwd("D:/workplace_milly/TW Database/COMPANY INFO")

library(plyr)
library(stringr)



# google資料
google_info <- read.csv("raw data/google_info.csv", stringsAsFactors = FALSE)
google_info <- unique(google_info)
google_info$GUI <- sprintf("%08d", google_info$GUI)

# 刪除地址與GUI共同重覆的列
# GUI重複的位置
double_GUI <- data.frame(table(google_info$GUI))
double_GUI <- as.character(double_GUI[which(double_GUI$Freq != 1), "Var1"])
pos_double_GUI <- which(google_info$GUI %in% double_GUI)
# 地址重複的位置
double_add <- data.frame(table(google_info$google.address))
double_add <- as.character(double_add[which(double_add$Freq != 1), "Var1"])
pos_double_add <- which(google_info$google.address %in% double_add)
# intersect of address and GUI
pos <- intersect(pos_double_GUI, pos_double_add)
if (length(pos) != 0) {
  google_info <- google_info[-pos, ]
}

t <- data.frame(table(google_info$GUI))
t <- as.character(t[which(t$Freq != 1), "Var1"])
pos <- which(google_info$GUI %in% t)
if (length(pos) != 0) {
  google_info <- google_info[-pos, ]
}
google_info <- google_info[, -1]



# 國貿局資料
trade <- list.files("raw data/", "trade")
trade <- trade[length(trade)]
trade <- read.csv(paste0("raw data/", trade), stringsAsFactors = FALSE)

# 經濟部財政司資料
gcis <- list.files("raw data/", "gcis")
#gcis <- gcis[1]
gcis <- read.csv(paste0("raw data/", gcis), stringsAsFactors = FALSE)
gcis <- unique(gcis)
names(gcis) <- c("GUI", "組織類型", "公司狀態", "營業項目", "New.Company")

# 合併
# tw_data <- join(gcis, trade)
tw_data <- join(trade, gcis)

# 增加縣市欄位
tw_data$`縣市` <- substr(tw_data$`地址`, 1, 3)

# mappping google information
tw_data <- join(tw_data, google_info)



# 調整欄位名稱與欄位順序
names(tw_data)[which(names(tw_data) == "中文名稱") ] <- "company"



# 欄位名稱順序
nm <- c(names(tw_data)[1:5], "google.address", names(tw_data)[6:13], "google.tel", names(tw_data)[14:28], "縣市", names(tw_data)[29:32])
tw_data <- tw_data[, nm]

# 存檔
# write.csv(tw_data, "../tw_data_0522.csv", row.names = FALSE, na = "")
write.csv(tw_data, paste0("../", gsub("gcis", "tw_data", list.files("raw data/", "gcis"))), na = "", row.names = FALSE)
rm(gcis, trade)




# 合併國貿局無資料公司
# 國貿局無資料公司
tw_data_no <- list.files("raw data/", "no_trade")
tw_data_no <- read.csv(paste0("raw data/", tw_data_no), stringsAsFactors = FALSE)
tw_data_no$`行業代碼與名稱` <- paste0(tw_data_no$`行業代碼1`, " ", tw_data_no$`名稱1`, "\n",
                               tw_data_no$`行業代碼2`, " ", tw_data_no$`名稱2`, "\n",
                               tw_data_no$`行業代碼3`, " ", tw_data_no$`名稱3`)

tw_data_no$`行業代碼與名稱` <- str_trim(gsub("NA", "", tw_data_no$`行業代碼與名稱`))

#刪除分開的行業代碼與名稱欄位
for (i in paste0(c("行業代碼", "名稱"), rep(1:4, each =2))) {
  tw_data_no[, i] <- NULL
}

# mapping google information
tw_data_no <- join(tw_data_no, google_info)
#tw_data_no$company.name <- NULL

names(tw_data_no)[which(names(tw_data_no) == "中文名稱")] <- "company"
#將無國貿局資料的欄位補齊與國貿局登記資料相同
for (i in setdiff(names(tw_data), names(tw_data_no))) {
  tw_data_no[, i] <- NA
}

# 合併國貿局有資料與國貿局屋資料
tw_data_all <- rbind(tw_data, tw_data_no)
# 存檔
write.csv(tw_data_all, paste0("../", gsub("gcis", "tw_data_all", list.files("raw data/", "gcis"))), row.names = FALSE, na = "")










