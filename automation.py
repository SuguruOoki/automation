#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json,datetime,shutil,csv
global file_extention

file_extention = '.csv'

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


class ContentsControl():
    def replace_company_name(company):

        if "(株)" in company:
            regular_expression = re.compile(r'\(株\)')
            dst = re.sub(regular_expression, '株式会社',company)
        elif "（株）" in company:
            regular_expression = re.compile(r'（株）')
            dst = re.sub(regular_expression, "株式会社",company)
        elif "(有)" in company:
            regular_expression = re.compile(r'\(有\)')
            dst = re.sub(regular_expression, "有限会社",company)
        elif "（有）" in company:
            regular_expression = re.compile(r'（有）')
            dst = re.sub(regular_expression, "有限会社",company)

        return dst


    # 取ってきた日付の内容が条件に合わない場合その週の月曜日の日付を取得する
    def getDateMonday(date):
        # date = datetime.date.today()
        getdate = datetime.datetime.strptime(date, "%Y%m%d")
        day = getdate.weekday()

        if day == 0:
            return date
        else:
            mondaydate = getdate - datetime.timedelta(days=day)
            return mondaydate.strftime("%Y%m%d")


class FileControl():
    def file_copy(bef, aft):
        shutil.copyfile(bef,aft)

    def get_find_all_files(self,target_directory):
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
            if ext == file_extention:
                # print("read!")
                # print(data)
                # print("\n")

                # 一行ずつ取得するパターン
                with csv.open(file, 'r') as f:
                    # reader = bz2.BZ2File.readlines(f)
                    # header = bz2.next(reader)  # ヘッダーを読み飛ばしたい時
                    data = [[str(elm) for elm in v] for v in csv.reader(f)]

                    for row in data:
                        print(row)          # 1行ずつ取得できる


    def rename_files(self,target_directory):
        os.chdir(target_directory)
        files = os.listdir(target_directory)
        date = datetime.datetime.today().strftime("%Y%m%d")

        for file in files:
            root, ext = os.path.splitext(file)
            print(file)
            if ext == file_extention:
                # ファイル名の日付が違った場合renameする
                if "_" in root:
                    namelist = root.split("_")
                    # 普通ならnamelistの長さは4となる
                    if len(namelist) >= 4:
                        if namelist[3] != date:
                            namelist[3] = date
                        if namelist[4] != date:
                            namelist[4] = date

                else:
                    print("root:"+root)
                # f = bz2.open(file, "r")
                # # data = [[str(elm) for elm in v] for v in csvmodule.reader(f)]
                # data = [[str(elm) for elm in v] for v in bz2.BZ2File.read(f)]
                # print(data)
                # print("\n")
            else:
                continue


    # target_directoryに存在するbz2で圧縮されたcsvの内容をarrayにinsert
    def csv_insert_to_array(self,target_directory):
        os.chdir(target_directory)
        files = os.listdir(target_directory)

        for file in files:
            root, ext = os.path.splitext(file)
            print(file)
            if ext == file_extention:
                # ファイル名の日付が違った場合renameする
                if "_" in root:
                    namelist = root.split("_")
                    # 普通ならnamelistの長さは4となる
                    if len(namelist) >= 4:
                        if namelist[3] != date:
                            namelist[3] = date
                        if namelist[4] != date:
                            namelist[4] = date

                else:
                    print("root:"+root)
                f = open(file, "r")
                data = [[str(elm) for elm in v] for v in csvmodule.reader(f)]
                print(data)
                print("\n")
            else:
                continue


if __name__ == '__main__':
    company = 'プログラミング(有)'
    result = ContentsControl.replace_company_name(company)
    print(result)
    # date = '2017/07/13'
    # print(CsvProcess.getDateMonday(date))
    # Postal.getAdressByPostalCode("164-0014")
    # root_folder = os.getcwd()
    # base_folder = "/t_townwork"
    # # print(root_folder)
    # csv = CsvProcess()
    # csv.get_files(root_folder+base_folder)
    # csv.rename_files(root_folder+base_folder)
