#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json

class Postal():
    def getAdressByPostalCode(postal_code):
        url = 'http://geoapi.heartrails.com/api/json'
        postal_code = "999-2224"
        postal_code_length = len(re.findall('\d',postal_code))

        # 郵便番号のバリデーション
        if postal_code_length == 7:
            print("Postal Code is Good!")
        else:
            print("Postal Code is Bad!")
            return ''

        payload = {'method':'searchByPostal'}
        payload['postal']= postal_code
        res = requests.get(url, params=payload).json()['response']['location'][0]
        address = res['prefecture']+res['city']+res['town']
        print(address)
        return address

class ExcelProcess():
    root_folder = os.getcwd()
    def program():
        print("test")
    #  フォルダ内のファイルを全て表示する関数
    def fild_all_files(directory):
        for root, dirs, files in os.walk(directory):
            yield root
            for file in files:
                yield os.path.join(root, file)

    # for file in fild_all_files(root_folder):
        # root, ext = os.path.splitext(file)

        # if ext == '.bz2':
        #     # print(os.path.basename(file))
        #     print(file)
        #     f = bz2.BZ2File(file).read()
            # src ="" # これが置き換え用の変数
            # if "(株)" in src:
            #     dst = src.replace("(株)", "株式会社")
            # elif "（株）" in src:
            #     dst = src.replace("(株)", "株式会社")
            # elif "(有)" in src:
            #     dst = src.replace("(有)", "有限会社")
            # elif "（有）" in src:
            #     dst = src.replace("(有)", "有限会社")
            # print(f)
            # f.close()

if __name__ == '__main__':
    Postal.getAdressByPostalCode("999-2224")
