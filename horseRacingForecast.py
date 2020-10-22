'''このプログラムについて
【プログラムの概要】
競馬の過去データから、レース結果を予想するプログラム。
入力となるレースのURLはnetkeiba.comのものを使用すること。（例：https://db.netkeiba.com/race/xxxxxxxxxxxxx/）
出力はレースの予想順。おそらく上位２〜３位を当てに行く賭け方が良さそう。
賭け方の参考サイトはこちら：https://www.jra.go.jp/kouza/beginner/baken/

【大まかな処理の流れ】
１：レースのURLをコマンドラインから受け取る
２：受け取ったURLの馬のリスト（馬の名前がデータへのリンクになっている）から、過去の戦歴をスクレイピングする
３：集めたデータをもとに予想順位を算出する
４：算出した予想順位を出力する

【予想順位の決定方法】
・過去のデータをもとに、馬にスコアをつける。
・予想順位は、スコアの高い順とする。
・スコアの計算は２通りの方法で行う。
・各馬のデータの形は以下の通り
    {
        horse-name: "",
        father-name: "",
        mather-name: "",
        rece-result: [
            [
                racename, number_of_horse, order_of_arrival, distance
            ]
        ]
    }
   

【スコアの計算方式その１】
・レースごとに各パラメータから求めたスコアの”加重平均”を馬のスコアとする。
・レースごとのスコアの計算式は次の通り。
    スコア＝（１ー順位÷頭数）×100
・スコアを求める際は、パラメータによっては重みをつける。
    ・前走のレースはそれ以外のものに比べて重みが２倍
    ・直近半年のレースで、前走でないものはそれ以前のものに比べて重みが1.5倍
・以上のレース毎のスコアを、上記の重みにしたがって平均する。
・父と母の成績も、同様にして算出する。
・子と父と母のスコアを８：１：１の重みで平均したものを最終スコアとする。

'''

import requests
from bs4 import BeautifulSoup
import time
import datetime
import numpy as np
from tqdm import tqdm

def get_horse_url(url):
    selector = '#umalink_' + url
    url = 'https://db.netkeiba.com/race/' + url + '/'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    horse_names = [n.get('href') for n in soup.select(selector)]
    return horse_names

def get_horse_data(url):
    base_url = 'https://db.netkeiba.com'
    res = requests.get(base_url + url)
    soup = BeautifulSoup(res.content, 'html.parser')
    race_name = soup.select('#contents > div.db_main_race.fc > div > table > tbody')
    horse_name = soup.select('#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1')
    result = []
    for n in race_name[0].contents:
        try:
            result.append([n.contents[1].get_text(), n.contents[9].get_text(), n.contents[13].get_text(), n.contents[23].get_text()])
        except AttributeError:
            pass
    return [''.join(horse_name[0].get_text().split()), result]
 
def calc_score(number_of_horse, order_of_arrival):
    result = (1 - (order_of_arrival / number_of_horse)) * 100
    return result

def string_to_datetime(string):
    return datetime.datetime.strptime(string, "%Y/%m/%d")

if __name__ == "__main__":
    score = []
    for url in tqdm(get_horse_url('201708040711')):
        #print('wait...')
        time.sleep(1)#一応サーバーのために１秒待ってあげる
        data = get_horse_data(url)
        horse_name = data[0]
        scores = []
        wight = []
        flag = 0
        counter = 0
        for i in range(1, len(data[1])):
            if string_to_datetime(data[1][i][0]) < string_to_datetime('2017/10/22'):#レースの日
                counter += 1
                if counter == 1:
                    if int(data[1][i][3]) > 4:
                        break
                try:
                    scores.append(calc_score(int(data[1][i][2]), int(data[1][i][3])))
                except ValueError:
                    continue
                if counter == 1:
                    wight.append(2)
                elif string_to_datetime(data[1][i][0]) > string_to_datetime('2020/4/22'):#レースの半年前
                    wight.append(1.5)
                else:
                    wight.append(1)
        try:
            score.append([horse_name, np.average(scores, weights=wight)])
        except ZeroDivisionError:
            continue

    score = sorted(score, reverse=True, key=lambda x: x[1]) 
    for i in score:
        print('馬名：　', end='')
        print(i[0], end='')
        print(' スコア：　', end='')
        print(i[1])
        
                



        
