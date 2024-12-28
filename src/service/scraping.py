import urllib.request
from bs4 import BeautifulSoup
import io
import boto3
    
## webサイトページの情報を取得する
def news_scraping(url,href):
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    title_list = []
    titles = soup.select(f'article a[href*="{href}"] .tit')
    
    for title in titles:
        title_list.append(title.text)
    
    url_list = []   
    urls = soup.select(f'article a[href*="{href}"]')
        
    for urlname in urls:
            url_list.append(urlname.get('href'))
       
    return title_list,url_list

def get_s3file(bucket_name, key):
    s3 = boto3.resource('s3')
    s3obj = s3.Object(bucket_name, key).get()
    
    return io.TextIOWrapper(io.BytesIO(s3obj['Body'].read()))
        
def write_df_to_s3(csv_list,key):
        csv_buffer = io.StringIO()
        csv_list.to_csv(csv_buffer,index=False,encoding='utf-8-sig')
        s3_resource = boto3.resource('s3')
        s3_resource.Object("バケット名", key).put(Body=csv_buffer.getvalue())
        