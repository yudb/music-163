"""
根据歌曲 ID 获得所有的歌曲所对应的评论信息
"""

import requests
from music_163 import sql
import time
import threading
import pymysql.cursors
import base64
#安装pycryptodome这个包即可
from Crypto.Cipher import AES
import json


headers = {
        'Host': 'music.163.com',
        'Connection': 'keep-alive',
        'Content-Length': '484',
        'Cache-Control': 'max-age=0',
        'Origin': 'http://music.163.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cookie': 'JSESSIONID-WYYY=b66d89ed74ae9e94ead89b16e475556e763dd34f95e6ca357d06830a210abc7b685e82318b9d1d5b52ac4f4b9a55024c7a34024fddaee852404ed410933db994dcc0e398f61e670bfeea81105cbe098294e39ac566e1d5aa7232df741870ba1fe96e5cede8372ca587275d35c1a5d1b23a11e274a4c249afba03e20fa2dafb7a16eebdf6%3A1476373826753; _iuqxldmzr_=25; _ntes_nnid=7fa73e96706f26f3ada99abba6c4a6b2,1476372027128; _ntes_nuid=7fa73e96706f26f3ada99abba6c4a6b2; __utma=94650624.748605760.1476372027.1476372027.1476372027.1; __utmb=94650624.4.10.1476372027; __utmc=94650624; __utmz=94650624.1476372027.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    }

# 获取params
def get_params(first_param, forth_param):
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param, first_key.encode(), iv.encode())
    h_encText = AES_encrypt(h_encText.decode(), second_key.encode(), iv.encode())
    return h_encText.decode()


# 获取encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


# 解AES秘
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text.encode())
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


# 获取json数据
def get_json(url, data):

    response = requests.post(url, headers=headers, data=data)
    return response.content


# 传入post数据
def crypt_api(id, offset):
    #下面注释的是获取所有评论的接口
    # url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token=" % id
    curr_time = int(time.time() * 1000)
    rid="R_SO_4_%s" % id
    threadId=rid
    url = "http://music.163.com//weapi/comment/resource/comments/get?csrf_token=06423fc605203c00895c2657ad6d1424"
    first_param = "{rid:\"%s\", offset:\"%s\", total:\"true\", limit:\"20\", csrf_token:\"\", cursor:\"%s\", threadId:\"%s\"}" % (rid,offset,curr_time,threadId)
    forth_param = "0CoJUm6Qyw8W8jud"
    params = get_params(first_param, forth_param)

    encSecKey = get_encSecKey()

    data = {
        "params": params,
        "encSecKey": encSecKey
    }
    return url, data


# 获取评论
def get_comment(id,connection0):
    try:
        offset = 0
        url, data = crypt_api(id, offset)
        json_text = get_json(url, data)
        # print(json_text)
        json_dict = json.loads(json_text.decode("utf-8"))
        json_dict_data=json_dict['data']
        comments_sum = json_dict_data['totalCount']
        json_comments = json_dict_data['hotComments']
        for json_comment in json_comments:
            user_id = json_comment['user']['userId']
            user_name = json_comment['user']['nickname']
            comment = json_comment['content']
            likedCount=json_comment['likedCount']
            # 添加评论的ID，名字以及评论到数据库中
            # sql.insert_commnet(user_id, user_name, comment)
            sql.insert_comments(id, comments_sum, comment,likedCount,connection0)
            print('id = ', end="")
            print(user_id, end="")
            print(':', end="")
            print(user_name, end="")
            # print(':', end="")
            # print(comment)
            print(',喜欢他的评论的人有%d个,已经添加到comments数据库中啦' % likedCount)
            time.sleep(1)
    except Exception as e:
        print('出现错误啦~错误是:', e)
        pass



if __name__ == '__main__':

    def save_comments(musics, flag, connection0):
        for i in musics:
            my_music_id = i['MUSIC_ID']
            try:
                get_comment(my_music_id,connection0)
            except Exception as e:
                # 打印错误日志
                print(my_music_id)
                print(e)
                time.sleep(5)


    music_before = sql.get_before_music()
    music_after = sql.get_after_music()

    # pymysql 链接不是线程安全的
    connection1 = pymysql.connect(host='localhost',
                                  user='root',
                                  password='123456',
                                  db='metadata',
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)

    connection2 = pymysql.connect(host='localhost',
                                  user='root',
                                  password='123456',
                                  db='metadata',
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)

    t1 = threading.Thread(target=save_comments, args=(music_before, True, connection1))
    t2 = threading.Thread(target=save_comments, args=(music_after, False, connection2))
    t1.start()
    t2.start()
