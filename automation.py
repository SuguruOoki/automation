#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json
import csv as csvmodule

class Postal():
    def getAdressByPostalCode(postal_code):
        url = 'http://geoapi.heartrails.com/api/json'
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


class CsvProcess():
    def find_all_files(self,target_directory):
        print(directory)
        for root, dirs, files in os.walk(target_directory):
            print(root)
            print(dirs)
            print(files)
            yield root
            for file in files:
                yield os.path.join(root, file)
                print(file)

        for file in fild_all_files(root_folder):
            root, ext = os.path.splitext(file)
            print(file)

    def get_files(self,target_directory):
        os.chdir(target_directory)
        files = os.listdir(target_directory)
        for file in files:
            root, ext = os.path.splitext(file)
            print(file)
            if ext == '.csv':
                f = open(file, "r")
                data = [[str(elm) for elm in v] for v in csvmodule.reader(f)]
                print(data)
                print("\n")

            # 一行ずつ取得するパターン
            # with open('some.csv', 'r') as f:
            #     reader = csv.reader(f)
            #     header = next(reader)  # ヘッダーを読み飛ばしたい時
            #
            #     for row in reader:
            #         print row          # 1行づつ取得できる

            # if ext == '.bz2':
            #     print(os.path.basename(file))
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
    # Postal.getAdressByPostalCode("164-0014")
    root_folder = os.getcwd()
    base_folder = "/master"
    # print(root_folder)
    csv = CsvProcess()
    csv.get_files(root_folder+base_folder)
