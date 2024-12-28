# Pythonのイメージ
FROM python

#ディレクトリを作成する
RUN mkdir /app

# 作業ディレクトリを設定する
WORKDIR /app

# 必要なパッケージをインストールする
COPY requirements.txt ./ 
RUN pip install --no-cache-dir -r requirements.txt

# ローカルのソースコードをコピーする
COPY app.py ./
COPY ./src /app/src

# 実行するコマンドを指定
CMD ["python", "./app.py"]