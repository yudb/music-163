"""
根据上一步获取的歌手的 ID 来用于获取所有的专辑 ID
"""
import requests
from bs4 import BeautifulSoup
import time
from music_163 import sql
import brotli


class Album(object):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'cookie': '_ntes_nnid=b1931be17409d8b545fd6f8fa61d27a9,1587525297368; _ntes_nuid=b1931be17409d8b545fd6f8fa61d27a9; mail_psc_fingerprint=03447d78f954209d8e20a5e49c687753; NTES_CMT_USER_INFO=11458182%7C%E5%BF%AB%E4%B9%90%E8%9B%8B%E8%9B%8B%E9%A3%98%7Chttp%3A%2F%2Fcms-bucket.ws.126.net%2F2019%2F07%2F25%2F116d025214604296b0a0b41c574d5d56.jpg%7Cfalse%7CamF5eXVkYkAxMjYuY29t; __oc_uuid=cbaa4a00-a4cc-11ea-a520-118977c6e1c2; vjuids=-ed53003f.173382c50f7.0.6874fac64f19b; vjlast=1594375295.1608519545.12; _ga=GA1.2.992589715.1608519739; vinfo_n_f_l_n3=e211c83139082450.1.8.1590058643082.1604289992821.1608520482248; NTES_SESS=7wXettzFFpLbkWWlTo3XKi.jfntACem06K7CXO7EQkE5pvFRpWZ9_iWhWIIolBRCOPrGtFJMf8DJAmBnqFB1KExRbiu6OVXLp1_IicGm0Ty6N0toqho6iiLmI4XdePQ71Cmtn0gewuzoqr_yT1XMrVBw.Tkv7isiM4dIQLJHpbLHXbQv2EoVo1MyvB0jqVwYd9uT1d99Y6mhgUOBiSR1Q61qSr7ZaAyMDq1LZnTyeYMtN; S_INFO=1614331686|0|#3&80#|jayyudb@126.com; P_INFO=jayyudb@126.com|1614331686|0|mail126|11&17|gud&1611454336&note_client#gud&440100#10#0#0|189682&0||jayyudb@126.com; hb_MA-93D5-9AD06EA4329A_source=www.google.com; __root_domain_v=.163.com; _qddaz=QD.s6s6rv.dhi0nb.klqjxgtp; _iuqxldmzr_=32; NMTID=00ODHztXsaNWdeHFE-qp78rAox2Gp4AAAF39fcZWQ; WEVNSM=1.0.0; WNMCID=jjxvuv.1614739343878.01.0; WM_TID=6rmNZ%2FQf4jxEQQAEUQM7Qtf7%2FRaPZVv%2B; WM_NI=rmvvDbZbNGdxcFjMtyHnPfZCIxH%2FSKyi2h1fUzmM%2B5E1NjVECe2gCElWwnt49dA1vaKcsGTzpdOfherVMu7C8%2BYt7%2Brj5KRrophLWYzj3mPV8GC6XQgvJsiFZfdxolNlcTc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeb4e960ace988daf06081eb8ba6c45b928e9eaff448b7b1a3d8ec3385ea8f8ccd2af0fea7c3b92ab2b3ba97c76a9abe82a8e774a19aa6aef7738cb2a087d9498ba888d0d241bbb7fe89b46e97a6a3aeaa3f87ef828bd54f81bbfe88c24fb089b98ff740fbbc8fd2f56b89bdbda8d772b4bc8187eb6fb28a8396b649fcf59795b621b2b6fbacd17aadb0a8add653bab6fd8ed35efc998dd7db5ba5aa8694ec4e9abaac99ee688eb4adb5e237e2a3; csrfToken=o71NoW-gvyHdDJ4WQrIK0abY; __csrf=06423fc605203c00895c2657ad6d1424; __remember_me=true; MUSIC_U=df7509ba12ec2be41e3fc3588ab029085e9b5233b736633d94e2c6020cb98248cac627b400a64889cacfa2c173398bfe; ntes_kaola_ad=1; JSESSIONID-WYYY=%5CX08Uxz7DUtr4og49whnWAZxrz9vKmtWZ5xqy4pe7d1%2B2oYR%2FzWNTe66wEKVuf6%2BJWcB8Wo4GdCpvEoKU7Hymcub%5CyO1K7jz6WFNxyDApYJxqrXnIWHV5Ra5%5CVaBj0JmHo4fm%2FIMxzd8HJwpIzkIRjR8BozcbrW%5CPK7%5Cf7xo%2F5iVqBac%3A1614748106913',
        'Host': 'music.163.com',
        'Pragma': 'no-cache',
        'Referer': 'https://music.163.com/',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
    }

    def save_albums(self, artist_id):
        params = {'id': artist_id, 'limit': '200'}
        # 获取歌手个人主页

        r = requests.get('http://music.163.com/artist/album', headers=self.headers, params=params)
        print("当前正在爬取" + r.url + "页面")
        # 网页解析
        content=r.content

        soup = BeautifulSoup(content.decode(), 'html.parser')
        body = soup.body

        albums = body.find_all('a', attrs={'class': 'tit s-fc0'})  # 获取所有专辑
        print(albums)
        for album in albums:
            albume_id = album['href'].replace('/album?id=', '')
            sql.insert_album(albume_id, artist_id)


if __name__ == '__main__':
    artists = sql.get_all_artist()
    my_album = Album()

    for i in artists:
        try:
            my_album.save_albums(i['ARTIST_ID'])
            # my_album.save_albums(1876)
            # print(i)
        except Exception as e:
            # 打印错误日志
            print(str(i) + ': ' + str(e))
            time.sleep(5)
