#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json,datetime,shutil,csv,xlsxwriter,pandas as pd
global file_extention

file_extention = '.txt'



class Postal():
    def getAdressByPostalCode(self,postal_code):
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


    def replace_equal(self,target):
        regular_expression = re.compile(r'.=.')
        dst = re.sub(regular_expression, '', target) if "=" in target else target
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


    # target_file(csv)の内容をarrayにinsert
    def csv_file_insert_to_array(target_file):
        # data = ""
        # count = 0
        print(target_file)
        # f = open(target_file, "r")
        # data = [[str(elm) for elm in v] for v in csv.reader(f)]
        data_df = pd.read_csv(target_file,encoding="utf8", engine="python")
        # data_df.columns
        columns = data_df.columns
        print(columns)
        drop_col = columns[36:]
        data_df = data_df.drop(drop_col, axis=1)
        print(data_df.head())
        exit(1)
        # del data[:][36:] # 募集企業名（TWN記載ママ）以降の要素の削除
        return data_df


    # からもじ、またはスペースがあった行を削除する関数
    def delete_row(contents, check_column):
        for i, row in enumerate(contents):
            if row[check_column] == "":
                contents.pop(i)
            elif row[check_column] == " ":
                contents.pop(i)

        return contents


    # 36列目以降を削除する関数
    def delete_columns(contents,target_column):
        for i, column in enumerate(contents):
            del column[target_column:]
        return contents


    # ファイルからとったdateをlistの先頭に挿入
    def insert_date(contents,date):
        for i, row in enumerate(contents):
            row.insert(0,date)

        return contents


    # Y列がスペースしかなかった場合にそれを空文字列に置換する関数
    def delete_empty(contents,target_column):
        for i, column in enumerate(contents):
            if column[target_column] == " ":
                column[target_column] = ""
            elif column[target_column] == "　":
                column[target_column] = ""
        return contents



class AbnormalityDetection():
    def abnormal_detection(data_df):
        for key, row in data_df.iterrows():
            print(row)
            print(row['データ取得日'])
            break

    def phone_number_detection(num_wrong):

        pattern = r"0\d{1,4}-\d{1,4}-\d{4}"
        matchOB = re.match(pattern , num_wrong)
        if matchOB:
            print(matchOB.group())


    def add_color_flg(contents):
        flg_list = [0] * len(data_df) # 色付け用フラグ列の追加
        contents['フラグ'] = flg_list


    def address3_detection(contents):
        # address3's index =>
        detection_index = 11 # 住所3は11
        color_index = []
        color_append = color_index.append
        for i, content in contents:
            if len(content[detection_index]) < 2:
                color_append(i)
        return color_index


    def postal_code_detection(contents):
        detection_index = 7 # 郵便番号は7
        length = len
        find_all = re.findall
        for postal_code in contents[detection_index]:
            postal_code_length = length(find_all('\d',postal_code))
        # 郵便番号のバリデーション
        if postal_code_length == 7:
            print("Postal Code is Good!")
        else:
            print("Postal Code is Bad!")
            return ''


class OutputExcel():
    def output(output_name, contents):
        # 新しいファイルとワークシートを作成
        workbook = xlsxwriter.Workbook('{}.xlsx'.format(output_name))
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        for line in contents:
            # Write any other lines to the worksheet.
            for col, t in enumerate(line):
                worksheet.write(row, col, t)
            row += 1
            col = 0
        workbook.close()



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


    def rename_files(target_directory):
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
            else:
                continue


    # ファイル名から日付を取る
    def get_date_from_file(target_file):
        root, ext = os.path.splitext(target_file)
        if ext == file_extention:
            # ファイル名の日付が違った場合renameする
            if "_" in root:
                namelist = root.split("_")
                # 普通ならnamelistの長さは2となるのでその２番目を日付の文字列として返す
                return namelist[1]
            else:
                return ""
        else:
            return ""


    # target_directoryに存在するbz2で圧縮されたcsvの内容をarrayにinsert
    def csv_insert_dataframe(self,target_directory):
        os.chdir(target_directory)
        files = os.listdir(target_directory)

        for file in files:
            root, ext = os.path.splitext(file)
            print(file)
            if ext == file_extention:
                target_file = 'sample_20170725.txt'
                data_df = pd.read_csv(target_file,encoding="utf8", engine="python")
                print(data_df)
                print("\n")
            else:
                continue



if __name__ == '__main__':

    target_file = 'sample_20170725.txt'
    file_date = FileControl.get_date_from_file(target_file) # ファイルから日付の文字列を取得
    csv_contents = ContentsControl.csv_file_insert_to_array(target_file) # ファイルの内容を配列に入れておく
    #print(csv_contents[0])
    flg_index = []
    csv_contents = AbnormalityDetection.add_color_flg(csv_contents, flg_index)
    print(csv_contents[0])
    OutputExcel.output(file_date, csv_contents)
    # ContentsControl.insert_date(csv_contents,file_date)
    # contents = ContentsControl.delete_row(csv_contents,5) # F列(会社名)が空の行を削除する
    # contents = ContentsControl.delete_row(contents,5) # K列が空の行を削除する
    # count = 0
    # contents = ContentsControl.delete_columns(csv_contents, 36) # AK列以降の列を削除する

        # else:
        #     continue

    # date = '2017/07/13'
    # print(CsvProcess.getDateMonday(date))
    # Postal.getAdressByPostalCode("164-0014")
    # root_folder = os.getcwd()
    # base_folder = "/t_townwork"
    # # print(root_folder)
    # csv = CsvProcess()
    # csv.get_files(root_folder+base_folder)
    # csv.rename_files(root_folder+base_folder)
