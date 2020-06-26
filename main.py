# coding: utf-8
# using : flake8, autopep8
import requests
from bs4 import BeautifulSoup
from PIL import Image
import PIL
import io
import time
import os
import datetime
import sys
# requests = webアクセス
# csv は csvファイル操作
# bs4 は データ整形
# PIL は 画像表示する


global _imgNum  # 画像枚数カウント用変数


def get_sources(img_name="", save_limit=1, start=0):
    # -------------------------------------------------------------- #
    # google 画像検索結果より，画像のurlのリストを取得
    # name =   検索内容
    # limits = 取得上限数
    # -------------------------------------------------------------- #

    if img_name == "":
        return -1

    sources = []
    """url = "https://www.google.com/search?hl=jp&q=" + \
        img_name + "&btnG=Google+Search&tbs=0&safe=off&tbm=isch"
        https://search.yahoo.co.jp/image/search?p=good&ei=UTF-8
        """

    # http通信では一回に20枚しか取れないので，繰り返し通信する
    # start で　取り初めの枚数を指定
    for start in range(0, save_limit + 19, 20):
        time.sleep(1)
        url = "https://search.yahoo.co.jp/image/search"
        # html 取得
        p = {"p": img_name,
             "ei": "UTF-8",
             "b": start,
             "save": 0
             }
        html = requests.get(url, params=p)
        # 整形
        soup = BeautifulSoup(html.text, "lxml")

        # limit枚分画像url取得
        if start > 0:
            imgs = soup.find_all("img")
            # limit つけると死ぬ
            for imgUrl in imgs[:-1]:
                sources.append(imgUrl.get("src"))
                if len(sources) >= save_limit:
                    return sources
        else:
            imgs = soup.find_all("img")
            for imgUrl in imgs[:-1]:
                # imgs[0]はよくわからんgifだったので無視しました．
                sources.append(imgUrl.get("src"))
                if len(sources) >= save_limit:
                    return sources

    return sources


def get_img_from_url(url=None):
    # -------------------------------------------------------------- #
    # 画像url より，画像のオブジェクトを取得
    # url = 画像url
    # -------------------------------------------------------------- #

    if url is None:
        return -1

    try:
        # f に 画像urlより取得したバイナリデータのオブジェクトを格納，.openで開く
        file = io.BytesIO(requests.get(url).content)
        img = Image.open(file)
    except FileNotFoundError:
        print("img load error", file=sys.stderr)
        return -1
    except ValueError:
        print("img load error", file=sys.stderr)
        return -1
    except PIL.UnidentifiedImageError:
        print("img load error", file=sys.stderr)
        return -1

    return img


def img_save(img=None, folder_name=datetime.datetime.now().strftime("%Y-%m-%d[%H:%M:%S]"), logs=False):
    # -------------------------------------------------------------- #
    # imgを保存
    # img =  画像オブジェクト
    # logs = logの出力
    # -------------------------------------------------------------- #
    global _imgNum
    _imgNum += 1
    if img is None:
        return -1

    folder_path = "./data/" + folder_name
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    if not os.path.isdir(folder_path):
        folder_path = "./data/" + \
            datetime.datetime.now().strftime("%Y-%m-%d[%H:%M:%S]")
        os.mkdir(folder_path)

    try:
        # jpg として扱うためにRGBに変換
        img = img.convert("RGB")
        img.save(folder_path + "/" + str(_imgNum) + ".jpg")
        if logs is True:
            print("save : " + folder_path + "/" + str(_imgNum) + ".jpg")
    except ValueError:
        print("img save error", file=sys.stderr)
        return -1
    except IOError:
        print("img save error", file=sys.stderr)
        return -1
    return 0


def init_img_num():
    global _imgNum
    _imgNum = 0


def img_show(img=None):
    # -------------------------------------------------------------- #
    # imgを出力
    # img = 画像オブジェクト
    # -------------------------------------------------------------- #

    if img is None:
        return -1

    img.show()
    return 0


def main_script(img_name="", save_limit=1, img_show_flag=False, logs=False):
    # -------------------------------------------------------------- #
    # メイン処理
    # name =   画像名
    # limits = 画像の上限枚数
    # img_show_flag = ダウンロードした画像の表示
    # logs =   logの出力
    # -------------------------------------------------------------- #

    # 画像URLリストの取得
    sources = get_sources(img_name, save_limit)

    # NOTE logs = Falseならいらんかも？
    print("start " + img_name + " : " + str(len(sources)) + "枚")

    # 画像枚数カウンタのリセット
    init_img_num()

    for url in sources:
        time.sleep(1)
        img = get_img_from_url(url)

        # 画像処理するならここでやる-------------------------------------- #
        # resize (xxx, xxx) -> (224, 224) for VGG16
        img = img.resize((224, 224), resample=Image.BILINEAR)
        # ----------------------------------------------------------- #
        # 保存
        img_save(img, img_name, logs=logs)

        # 表示
        if img_show_flag is True:
            img_show(img)

    # NOTE logs = Falseならいらんかも？
    print("finish : " + img_name)


if __name__ == "__main__":

    names = []  # 検索名格納

    # 検索ファイル名指定, 改行コード一応削除
    # NOTE logs = Falseならいらんかも？ -> 出力が
    # TODO
    filename = input("検索内容ファイル名を指定 :").rstrip("\n")

    # 各画像の最大保存枚数を指定
    # NOTE logs = Falseならいらんかも？ -> 出力が
    try:
        limit = int(input("取得画像数を指定 :"))
    except TypeError:
        limit = 1

    # 検索内容ファイルの中身を配列に格納
    path = filename
    with open(path, "r", encoding="utf-8") as f:
        # with open() as f : について
        # try resource と同じ感じでここを抜けると自動でfが閉じられる
        try:
            # 1行ずつ読んでく, names に 格納
            line = f.readline()
            while line:
                names.append(line.rstrip("\n"))
                line = f.readline()

            # 検索する画像一覧表示
            # log = False　なら いらんかも？
            print("\nsearch " + str(len(names)) + " contents.")
            for name in names:
                print(name)
            print()

        except OSError:
            print("error can't open", filename, file=sys.stderr)

    for name in names:
        main_script(name, limit)

    print("all correct")
