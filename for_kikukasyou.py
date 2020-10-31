import requests
from bs4 import BeautifulSoup
import time
import datetime
import numpy as np
from tqdm import tqdm
import re

def get_horse_url():
    url = "https://race.netkeiba.com/race/shutuba.html?race_id=202004040611"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    horse_names = []
    for i in soup.find_all(class_='HorseName'):
        try:
            horse_names.append(i.contents[0].get('href'))
        except AttributeError:
            pass
    return horse_names

def get_horse_data(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    race_name = soup.select('#contents > div.db_main_race.fc > div > table > tbody')
    horse_name = soup.select('#db_main_box > div.db_head.fc > div.db_head_name.fc > div.horse_title > h1')
    result = []
    for n in race_name[0].contents:
        try:
            #日付、開催地、レース名、頭数、着順、斤量、距離、タイム
            result.append([n.contents[1].get_text(), re.search(r'[^0-9]+', n.contents[3].get_text()).group(), n.contents[9].get_text(), n.contents[13].get_text(), n.contents[23].get_text(), n.contents[27].get_text(), int(re.search(r'[0-9]+', n.contents[29].get_text()).group()), n.contents[35].get_text()])
        except AttributeError:
            pass
    return [''.join(horse_name[0].get_text().split()), result]
 
def calc_score(number_of_horse, order_of_arrival):
    result = (1 - (order_of_arrival / number_of_horse)) * 100
    return result

def string_to_datetime(string):
    return datetime.datetime.strptime(string, "%Y/%m/%d")

def calc_distance_index(standrd_time):
    #１秒÷基準タイム×1000
    return 1 / standrd_time * 1000

def calc_time(standrd_time):
    #１秒÷基準タイム×1000
    try:
        run_time = float(standrd_time.split(':')[0]) * 60.0 + float(standrd_time.split(':')[1])
    except ValueError:
        return False
    
    return run_time

def calc_speed_index(standrd_time, run_time, weight):
    #(基準タイムー走破タイム)×距離指数＋馬場指数＋（斤量ー55）×2＋80
    # 馬場指数は入手困難（有料）なので、とりあえず無視する（可算なのである程度無視しても大丈夫なはず）
    return (standrd_time - run_time)*calc_distance_index(standrd_time) + (weight-55)*2 + 80

if __name__ == "__main__":
    tokyo =     {1000: 54.4, 1200: 68.3, 1400: 81.6, 1600: 94.8, 1700: 102.4, 1800: 109.4, 2000: 121.6, 2200: 134.9, 2400: 149.2, 2500: 154.7, 3000: 188.6, 3200: 199.6, 3600: 226.9}
    nakayama =  {1000: 55.3, 1200: 69.2, 1400: 82.5, 1600: 95.7, 1700: 103.3, 1800: 110.3, 2000: 122.5, 2200: 135.8, 2400: 150.1, 2500: 155.5, 3000: 189.5, 3200: 200.4, 3600: 227.8}
    kyoto =     {1000: 54.3, 1200: 68.2, 1400: 81.5, 1600: 94.7, 1700: 102.2, 1800: 109.3, 2000: 121.4, 2200: 134.8, 2400: 149.1, 2500: 154.5, 3000: 188.5, 3200: 199.4, 3600: 226.8}
    hanshin =   {1000: 54.7, 1200: 68.7, 1400: 81.9, 1600: 95.2, 1700: 102.7, 1800: 109.7, 2000: 121.9, 2200: 135.2, 2400: 149.5, 2500: 155.0, 3000: 189.0, 3200: 199.9, 3600: 227.2}
    cyukyo =    {1000: 55.0, 1200: 68.9, 1400: 82.1, 1600: 95.4, 1700: 102.9, 1800: 109.9, 2000: 122.1, 2200: 135.4, 2400: 149.7, 2500: 155.2, 3000: 189.2, 3200: 200.1, 3600: 227.5}
    sapporo =   {1000: 55.0, 1200: 68.9, 1400: 82.2, 1600: 95.4, 1700: 103.0, 1800: 110.0, 2000: 122.2, 2200: 135.5, 2400: 149.8, 2500: 155.2, 3000: 189.2, 3200: 200.1, 3600: 227.5}
    hakodate =  {1000: 55.7, 1200: 69.6, 1400: 82.9, 1600: 96.1, 1700: 103.7, 1800: 110.7, 2000: 122.9, 2200: 136.2, 2400: 150.5, 2500: 156.0, 3000: 189.9, 3200: 200.9, 3600: 228.2}
    hukushima = {1000: 54.9, 1200: 68.8, 1400: 82.0, 1600: 95.3, 1700: 102.8, 1800: 109.8, 2000: 122.0, 2200: 135.3, 2400: 149.6, 2500: 155.1, 3000: 189.1, 3200: 200.0, 3600: 227.3}
    nigata =    {1000: 54.4, 1200: 68.3, 1400: 81.5, 1600: 94.8, 1700: 102.3, 1800: 109.3, 2000: 121.5, 2200: 134.8, 2400: 149.2, 2500: 154.6, 3000: 188.6, 3200: 199.5, 3600: 226.9}
    kokura =    {1000: 54.3, 1200: 68.2, 1400: 81.4, 1600: 94.7, 1700: 102.2, 1800: 109.2, 2000: 121.4, 2200: 134.7, 2400: 149.1, 2500: 154.5, 3000: 188.5, 3200: 199.4, 3600: 226.8}
    standard_index = {'東京': tokyo, '中山': nakayama, '京都': kyoto, '阪神': hanshin, '中京': cyukyo, '札幌': sapporo, '函館': hakodate, '福島': hukushima, '新潟':nigata, '小倉': kokura}

    result = []
    for url in tqdm(get_horse_url()):
        time.sleep(1)#一応サーバーのために１秒待ってあげる
        horse_data = get_horse_data(url)
        #日付、開催地、レース名、頭数、着順、斤量、距離、タイム
        rece_data = horse_data[1]
        print(horse_data[0])
        score = []
        non_flag = 0
        first_race_flag = 0
        for data in rece_data:
            date = data[0]
            place = data[1]
            race = data[2]
            horse_number = data[3]
            rank = data[4]
            weight = data[5]
            distance = data[6]
            run_time = calc_time(data[7])
            if string_to_datetime(date) < string_to_datetime('2020/10/25'):
                first_race_flag += 1
                if first_race_flag == 1:
                    try:
                        if int(rank) > 4:
                            non_flag = 1
                            break
                    except ValueError:
                        break

            if run_time == False:
                continue
            else:
                try:
                    score.append(calc_speed_index(standard_index[place][distance], run_time, float(weight)))
                except KeyError:
                    continue
        if non_flag == 0:
            result.append([horse_data[0], np.average(score)])
        else:
            result.append([horse_data[0], 0])
    li = sorted(result, reverse=True, key=lambda x: x[1])
    for i in li:
        print(i[0] + ': ' + str(i[1]))