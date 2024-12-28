import json
from . import scraping
import itertools
import pandas as pd
import csv
from linebot.models import (CarouselColumn,URITemplateAction)

class handle_message_service :
	def generate_reply_message(receivedMessage) :
		json_file = open('/app/src/dict/mydict.json', 'r')
		mydict = json.load(json_file)
		send_line_flag = "No"

		for key in mydict :
			if (receivedMessage == key) :
				# ファイル名、url、hrefを取得する
				
				filename = mydict[key]["s3-filename"]
				url = mydict[key]["url"]
				href = mydict[key]["href"]
				
				#前回スクレイピング分のurlを入れる
				ex_csv =[]
				for rec in csv.reader(scraping.get_s3file("バケット名", filename)):
					ex_csv.append(rec)
				ex_csv = ex_csv[1:]
				ex_csv = list(itertools.chain.from_iterable(ex_csv))

				# スクレイピングを実行
				title,urlname = scraping.news_scraping(url,href)
				csv_list = urlname
				title_list = title
				
                # 更新分のurlとtitileを入れるリスト
				new_url = []
				new_title = []
				
				#ex_csvと比較して更新分を取り出していく
				for i in range(10):
					if csv_list[i] in ex_csv[0]:
						num = i
						#ex_csvの先頭にある記事がcsv_listの何番目の記事に当たるか調べる
						break
					else:
						num = "all"
			
				if num == 'all':
					new_url.append(urlname[0:10])
					new_title.append(title[0:10])

				else:
					new_url.append(urlname[:num])
					new_title.append(title[:num])
				
				#S3にcsv_listを書き込んで終了
				csv_list = pd.DataFrame(csv_list)
				scraping.write_df_to_s3(csv_list,filename)
				# ラインフラグを変更する
				send_line_flag = "Yes"
				break
		if send_line_flag == "Yes":
			if num == 0:
				columns_list = "新しいニュースはありません"
			else:
				#カルーセルテンプレートのリスト作成
				columns_list = []
				for i in range(len(new_title[0])):
					columns_list.append(
						CarouselColumn(title=new_title[0][i][0:10], text=new_title[0][i][0:60],
					 	actions=[{"type": "uri", "label": "サイトURL", "uri": new_url[0][i]},]
					))
			return columns_list
		else:
			return "返信できない形です"