#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json,datetime,shutil,csv,xlsxwriter,pandas as pd
import logging,subprocess,time
import numpy as np
global file_extention
global excel_extention
global csv_extention

file_extention = '.txt'
excel_extention = '.xlsx'
csv_extention = '.csv'
tsv_extention = '.tsv'

class PerlProcess():
    def logCheck(target_directory):
        log_file = 'mda_log.log'
        try:
            if target_directory:
                check = commands.getoutput("find ./{} -name \"mda_check_cnt.log\" > ./mda_log.log".format(target_directory))
        except ValueError:
            logging.error("Not Found Target Directory or mda_check_cnt.log")

        try: # os.path.exists(log_file)
            f = open(log_file, 'r')
            logfile_list = f.readlines()
            f.close()
            pattern1 = '/TABAITAI/'
            pattern2 = '/corp_asuta/'
            logfile_list = [x for x in logfile_list if pattern1 in x]
            logfile_list = [x for x in logfile_list\
             if pattern2 or pattern3 or pattern4 or pattern5 or pattern6 in x]
            print(logfile_list)
        except ValueError:
            logging.error('Not Found {}'.format(log_file))

    # ファイルネームの中に特定の記号が入っていた場合の置き換えを行う関数
    def renProcess(target_directory):
        pattern = re.compile(u'[ \[\]\(\)\{\}]')
        try:
            files = os.listdir(target_directory)
            os.chdir(target_directory)
            for file in files:
                root, ext = os.path.splitext(file)
                #print(file)
                if ext == excel_extention or ext == csv_extention:
                    ren = pattern.sub(u'', file)
                    args = ['mv', file, ren]
                    subprocess.check_call(args);
        except ValueError:
            logging.error('value error')

    # target_directoryはフルパスでの指定
    def mdaCheckCnt(target_directory, media_name):
        start = time.time()
        get_phone_number = ContentsControl.get_tel
        output_excel = OutputExcel.dataframe_output
        company_name_search = re.compile('会社名*')
        posting_start_date_search = re.compile('掲載開始日*')
        tel_key = 'TEL'
        postal_code = '郵便番号'
        prefecture = '都道府県'
        address3 = '住所3'
        log_file = 'mda_check_cnt.log'
        files = []

        # editディレクトリの作成
        # target_directory => 処理を行うファイルを格納する
        # output_path => 処理が終わった結果のファイルを格納する
        # error_path => エラーであった行を取り出したファイルを格納する
        # media_path => メディア毎の問い合わせ済みのファイルを格納しておく
        print(target_directory)
        os.chdir(target_directory)
        target_path = target_directory+'/'+'test'
        output_path = target_directory+'/'+'edited'
        error_path = target_directory+'/'+'error'
        inquired_path = target_directory+'/'+'inquired'

        if not os.path.exists(output_path):
            args = ['mkdir', 'edited']
            subprocess.check_call(args)
        if not os.path.exists(error_path):
            args = ['mkdir', 'error']
            subprocess.check_call(args)
        os.chdir(target_path)

        target_files = FileControl.get_find_all_files_name(target_path, excel_extention)
        tsv_target_files = FileControl.get_find_all_files_name(target_path, tsv_extention)
        inquired_dataframe = PerlProcess.inquired_row_to_dataframe(inquired_path, media_name)# 問い合わせ済みのファイルを読み込む

        # print(inquired_dataframe)
        # elapsed_time = time.time() - start
        # print ("処理時間:{0}".format(elapsed_time) + "[sec]")
        exit(1)
        if target_files:
            # target_filesのファイルを読み込み、配列に入れてerrorを確認して修正する。
            # ここでは読み込んだレコードから改行コードと先頭末尾のダブルクォーテーションの削除,
            # データ取得日の入力などを行う
            for target_file in target_files:
                os.chdir(target_path)
                contents = ContentsControl.excel_file_insert_dataframe(target_file) # excelファイルをデータフレームにする
                # なんでかNaNが残っている時があるので念のため。
                contents = contents.fillna('')
                columns = contents.columns.tolist()
                company_name_key = [x for x in columns if company_name_search.match(x)][0]
                posting_start_date_key = [x for x in columns if posting_start_date_search.match(x)][0]
                name_replace = contents[company_name_key].replace
                posting = ContentsControl.getDateMonday(contents[posting_start_date_key][1])
                output_name_date = posting.replace('/', '')

                for column in columns:
                    contents[column] = contents[column].astype(str)
                    contents[column] = contents[column].map(lambda x: x.strip().strip('\"'))
                    contents[column] = contents[column].map(lambda x: x.strip('=')) # 「=」を削除
                    contents[column] = contents[column].map(lambda x: x.replace('\n','')) # 「\n」(改行)を削除

                # 会社名のところにあるアスタリスク削除を行う。
                contents[company_name_key] = name_replace('\*', ' ', regex=True)
                contents[company_name_key] = name_replace('\＊', ' ', regex=True)
                contents[company_name_key] = name_replace('(株)', '株式会社', regex=True)
                contents[company_name_key] = name_replace('（株）', '株式会社', regex=True)
                contents[company_name_key] = name_replace('(有)', '有限会社', regex=True)
                contents[company_name_key] = name_replace('（有）', '有限会社', regex=True)

                if not posting == contents[posting_start_date_key][1]:
                    contents[posting_start_date_key] = posting
                    print("changed!")

                # 電話番号処理
                contents[tel_key] = contents[tel_key].str.findall('\d{2,4}-\d{2,4}-\d{2,4}')
                contents[tel_key] = contents[tel_key].apply(get_phone_number)
                postal_code_error = contents[contents[postal_code] == ''] # 郵便番号がない行
                address3_error = contents[contents[address3]==''] # 住所がない
                tel_error = contents[contents[tel_key]==''] # 電話番号がない
                postal_prefecture_error = postal_code_error[postal_code_error[prefecture] == ''] # 郵便番号も都道府県もない

                # 掲載開始日の取得と修正
                # ContentsControl.getDateMonday(right_contents[])

                # いらない行を削ぎ落として問い合わせを行う行のみを抽出する
                drop_index = list(set(postal_code_error.index.tolist() + address3_error.index.tolist() + tel_error.index.tolist()))
                right_contents = contents.drop(drop_index)
                contents_length = len(right_contents)

                # データ取得日についての処理を入れる
                # データ掲載開始日を月曜に直す処理を入れる
                # 途中のカラム数が違うものについてはDataframeに入らないのでそのエラー処理はここには入れない
                output_name = target_file.split(".")[0]
                os.chdir(output_path)
                # OutputExcel.dataframe_output(output_name, contents)
                output_excel(output_name+'_'+str(contents_length)+'_'+output_name_date+'_'+output_name_date, right_contents)
                os.chdir(error_path)
                output_excel(output_name+'_address3_error', address3_error)
                output_excel(output_name+'_postal_code_error', postal_code_error)
                output_excel(output_name+'_tel_error', tel_error)
                output_excel(output_name+'_postal_prefecture_error', postal_prefecture_error)
        else:
            print('target files is not found in edited folder!')
            exit(1)

        if tsv_target_files:
            # target_filesのファイルを読み込み、配列に入れてerrorを確認して修正する。
            # ここでは読み込んだレコードから改行コードと先頭末尾のダブルクォーテーションの削除,
            # データ取得日の入力などを行う
            for tsv_target_file in tsv_target_files:
                os.chdir(target_path)
                contents = ContentsControl.tsv_file_insert_dataframe(tsv_target_file) # excelファイルをデータフレームにする
                # なんでかNaNが残っている時があるので念のため。
                contents = contents.fillna('')
                columns = contents.columns.tolist()
                company_name_key = [x for x in columns if company_name_search.match(x)][0]
                posting_start_date_key = [x for x in columns if posting_start_date_search.match(x)][0]
                name_replace = contents[company_name_key].replace
                posting = ContentsControl.getDateMonday(contents[posting_start_date_key][2])
                output_name_date = posting.replace('/', '')

                for column in columns:
                    contents[column] = contents[column].astype(str)
                    contents[column] = contents[column].map(lambda x: x.strip().strip('\"'))
                    contents[column] = contents[column].map(lambda x: x.strip('=')) # 「=」を削除
                    contents[column] = contents[column].map(lambda x: x.replace('\n','')) # 「\n」(改行)を削除

                # 会社名の置き換え処理
                contents[company_name_key] = name_replace('\*', ' ', regex=True)
                contents[company_name_key] = name_replace('\＊', ' ', regex=True)
                contents[company_name_key] = name_replace('(株)', '株式会社', regex=True)
                contents[company_name_key] = name_replace('（株）', '株式会社', regex=True)
                contents[company_name_key] = name_replace('(有)', '有限会社', regex=True)
                contents[company_name_key] = name_replace('（有）', '有限会社', regex=True)

                if not posting == contents[posting_start_date_key][1]:
                    contents[posting_start_date_key] = posting
                    print("changed!")

                # 電話番号の置き換え処理
                contents[tel_key] = contents[tel_key].str.findall('\d{2,4}-\d{2,4}-\d{2,4}')
                contents[tel_key] = contents[tel_key].apply(get_phone_number)
                pd.set_option('display.width', 1)
                postal_code_error = contents[contents[postal_code] == ''] # 郵便番号がない行
                address3_error = contents[contents[address3]==''] # 住所がない
                tel_error = contents[contents[tel_key]==''] # 電話番号がない
                postal_prefecture_error = postal_code_error[postal_code_error[prefecture] == ''] # 郵便番号も都道府県もない

                # いらない行を削ぎ落として問い合わせを行う行のみを抽出する
                drop_index = list(set(postal_code_error.index.tolist() + address3_error.index.tolist() + tel_error.index.tolist()))
                right_contents = contents.drop(drop_index)

                # データ取得日についての処理を入れる
                # データ掲載開始日を月曜に直す処理を入れる
                # 途中のカラム数が違うものについてはDataframeに入らないのでそのエラー処理はここには入れない
                os.chdir(output_path)
                output_name = tsv_target_file.split(".")[0]
                output_excel(output_name+'_'+str(contents_length)+'_'+output_name_date+'_'+output_name_date, right_contents)
                os.chdir(error_path)
                output_excel(output_name+'_address3_error', address3_error)
                output_excel(output_name+'_postal_code_error', postal_code_error)
                output_excel(output_name+'_tel_error', tel_error)
                output_excel(output_name+'_postal_prefecture_error', postal_prefecture_error)
        else:
            print('target files is not found in edited folder!')
            exit(1)
        # elapsed_time = time.time() - start
        # print ("処理時間:{0}".format(elapsed_time) + "[sec]")

    def inquired_row_to_dataframe(target_directory, media_name):
        inquired_file_search_name = '*' + media_name + '*.*'
        inquired_file = glob.glob(target_directory+'/'+inquired_file_search_name)
        if inquired_file:
            contents = ContentsControl.excel_file_insert_dataframe(inquired_file[0])
            if 'KEY' in contents.columns:
                return contents['KEY']
            else:
                logging.error('inquired_file don`t have a search key. So we can`t keep processing')
        else:
            logging.error('inquired_file is not found')

class SearchPostalCode():

    def showAddress(self, input_postal_code):
        postal_code_file_name = "zenkoku.csv"
        postal_code_data = pd.read_csv(postal_code_file_name)
        print(postal_code_data.head())
        address = self.getAddress(inputZipCode)
        if address == "":
            dlg = print(u"データベースには存在しません")
        else:
            addr = address.decode(sys.stdin.encoding)


    def getAddress(self, inputZipCode):
        indata = open(file_name, 'r')
        dataList = indata.read().splitlines()
        totalDataNumber = len(dataList)
        address = ""

        for i in xrange(totalDataNumber):
            zipCode = dataList[i].split('","')[1]
            if zipCode == inputZipCode:
                address = dataList[i].split('","')[5]+\
                          dataList[i].split('","')[6]+\
                          dataList[i].split('","')[7].split('"')[0]
        return address



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


    # 取ってきた日付の内容が条件に合わない場合その週の月曜日の日付を取得する
    # date:str
    def getDateMonday(date):
        # date = datetime.date.today()
        get_date = datetime.datetime.strptime(date, "%Y/%m/%d")
        day = get_date.weekday()

        if day == 0:
            return date
        else:
            mondaydate = getdate - datetime.timedelta(days=day)
            return mondaydate.strftime("%Y%m%d")


    # target_file(csv)の内容をarrayにinsert
    def csv_file_insert_dataframe(target_file):
        try:
            data_df = pd.read_csv(target_file, encoding="utf8", engine="python", na_values='')
            # data_df.columns
            columns = data_df.columns
            # いらない列の削除
            drop_col = columns[36:]
            data_df = data_df.drop(drop_col, axis=1)
            return data_df
        except ValueError:
            # 読み込めないということはカラムがおかしいということなので。
            logging.error("csv file : Columns Mistake error")
            exit(1)

    def excel_file_insert_dataframe(target_file):
        try:
            df = pd.read_excel(target_file, sheet_name='Sheet1')
            columns = df.columns
            drop_col = columns[36:]
            data_df = df.drop(drop_col, axis=1)
            return data_df
        except ValueError:
            # 読み込めないということはカラムがおかしいということなので。
            logging.error("excel file : Columns Mistake error")
            exit(1)


    def tsv_file_insert_dataframe(target_file):
        try:
            header = ['No', '媒体名', '掲載開始日＝データ取得日', '事業内容', '職種','会社名(詳細ページの募集企業名)',
             '郵便番号', '都道府県', '住所1', '住所2', '住所3', 'TEL','担当部署', '担当者名', '上場市場','従業員数',
             '資本金', '売上高', '広告スペース', '大カテゴリ','小カテゴリ', '掲載案件数', '派遣', '紹介', 'フラグ数',
             'FAX', 'データ取得日', '版', '企業ホームページ','版コード', '広告サイズコード', '最寄り駅', '給与欄',
             '勤務時間欄', '詳細ページ\u3000キャッチコピー','電話番号（TWN記載ママ）']
            use_cols = range(0,36)
            data_df = pd.read_csv(target_file, sep='\t', names=header, usecols=use_cols, engine='python', encoding='utf8')
            return data_df
        except ValueError:
            # 読み込めないということはカラムがおかしいということなので。
            logging.error("tsv file : Columns Mistake error")
            exit(1)


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

    def get_tel(tel_list):
        if len(tel_list) == 0:
            return None
        else:
            return tel_list[0]




class AbnormalityDetection():
    def abnormal_detection(contents):
        for key, row in contents.iterrows():
            # print(row)
            print(row['データ取得日'])


    def phone_number_detection(num_wrong):

        pattern = r"0\d{1,4}-\d{1,4}-\d{4}"
        matchOB = re.match(pattern , num_wrong)
        if matchOB:
            print(matchOB.group())


    def add_color_flg(contents):
        flg_list = [0] * len(contents) # 色付け用フラグ列の追加
        contents['フラグ'] = flg_list
        return contents


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

    def postal_code_detection2(contents):
        pattern = r"\d{3}-\d{4}"
        matchOB = re.match(pattern , num_wrong)
        if matchOB:
            print(matchOB.group())


class OutputExcel():
    def dataframe_output(output_name, contents):
        # start = time.time()
        headers = contents.columns
        writer = pd.ExcelWriter('{}.xlsx'.format(output_name), engine='xlsxwriter')
        contents.to_excel(writer, sheet_name='Sheet1',index=False)
        writer.save()
        writer.close()
        # elapsed_time = time.time() - start
        # print("描き込み時間:{0}".format(elapsed_time) + "[sec]")



class FileControl():
    def file_copy(bef, aft):
        shutil.copyfile(bef,aft)

    def get_find_all_files_name(target_directory, target_extention):
        files = os.listdir(target_directory)
        return_files = []
        for file in files:
            if not target_extention == '': # target_extentionが空ではない時
                root, ext = os.path.splitext(file)
                if ext == target_extention: # target_extentionが一致した時
                    return_files.append(file)

        if len(return_files) <= 0:
            return files
        else:
            return return_files

    # ファイルの内容までを取得する
    def get_files(target_directory, target_extention=''):
        os.chdir(target_directory)
        files = os.listdir(target_directory)
        for file in files:
            root, ext = os.path.splitext(file)
            print(file)
            if ext == target_extention:
                # 一行ずつ取得するパターン
                with csv.open(file, 'r') as f:
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
                # target_file = 'sample_20170725.txt'
                data_df = pd.read_csv(file,encoding="utf8", engine="python")
                print(data_df)
                print("\n")
            else:
                continue


    def dataframe_to_excel(fileName):
        writer = pd.ExcelWriter(fileName,engine='xlsxwriter')
        csv_contents.to_excel(writer)
        writer.save()



if __name__ == '__main__':
    # args = sys.argv
    media_name = 'フロムエー' # args[1] # 第一引数は処理を行うメディアの名前
    target = PerlProcess.mdaCheckCnt(os.getcwd(), media_name)
