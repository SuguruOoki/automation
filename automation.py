#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2, os, sys, glob, re, requests, json, datetime, shutil, csv, xlsxwriter, pickle, pandas as pd
from collections import Counter
from collections import OrderedDict
import logging,subprocess,time
import numpy as np
global excel_extention
global csv_extention
import xlrd

excel_extention = '.xlsx'
csv_extention = '.csv'
tsv_extention = '.tsv'

class PerlProcess():
    # この関数は以前使われていたperlのプログラムにあったため一応実装したが、現在(20170918)は使われていない。
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
                if ext == excel_extention or ext == csv_extention:
                    ren = pattern.sub(u'', file)
                    args = ['mv', file, ren]
                    subprocess.check_call(args);
        except ValueError:
            logging.error('value error')

    # target_directoryはフルパスでの指定
    def mdaCheckCnt(target_directory, media_name):
        # 高速化のためになんども使う関数に関して変数に保存しておく
        output_excel = OutputExcel.dataframe_output
        contentscontrol = ContentsControl
        length = len
        chdir = os.chdir
        fillblanks = FillBlanks

        # 変数
        company_name_search = re.compile('会社名*')
        posting_start_date_search = re.compile('掲載開始日*')
        areacode_file_name = 'areacode2.pkl'
        tel_key = 'TEL'
        postal_code_key = '郵便番号'
        prefecture_key = '都道府県'
        address1_key = '住所1'
        address2_key = '住所2'
        address3_key = '住所3'
        log_file = 'mda_check_cnt.log'
        files = []

        # editディレクトリの作成
        # target_directory => 処理を行うファイルを格納する
        # output_path => 処理が終わった結果のファイルを格納する
        # error_path => エラーであった行を取り出したファイルを格納する
        # media_path => メディア毎の問い合わせ済みのファイルを格納しておく
        print(target_directory)
        chdir(target_directory)
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
        print(os.getcwd())
        target_files = FileControl.get_find_all_files_name(target_path, excel_extention) # excelファイルのロード
        tsv_target_files = FileControl.get_find_all_files_name(target_path, tsv_extention) # tsvファイルのロード
        target_files = target_files + tsv_target_files
        print(target_files)
        # target_files.extend(tsv_target_files)
        inquired_dataframe = PerlProcess.inquired_row_to_dataframe(inquired_path, media_name) # 問い合わせ済みのファイルを読み込む
        inquired_dataframe = inquired_dataframe.fillna('') # 残っているNaNを削除

        exit(1)

        # 後の処理でinquired_dataframeの列名とファイルから読み込んだdataframeの列名が同じものを比べて
        # 問い合わせ済みの企業の情報を削除したいのでinquired_dataframe側の列名を変更しておく
        inquired_dataframe = inquired_dataframe.rename(columns={prefecture_key: prefecture_key+'(修正後)', prefecture_key+'(修正前)':prefecture_key,
                                address1_key: address1_key+'(修正後)', address1_key+'(修正前)':address1_key,
                                address2_key: address2_key+'(修正後)', address2_key+'(修正前)':address2_key,
                                address3_key: address3_key+'(修正後)', address3_key+'(修正前)':address3_key,
                                })

        # target_filesのファイルを読み込み、配列に入れてerrorを確認して修正する。
        # ここでは読み込んだレコードから改行コードと先頭末尾のダブルクォーテーションの削除,
        # データ取得日の入力などを行う
        if target_files:
            for target_file in target_files:
                # tsvとexcelファイルで処理を変更する
                extention = os.path.splitext(target_file)[1]
                print(target_file)
                if extention == excel_extention:
                    contents = ContentsControl.excel_file_insert_dataframe(target_file) # excelファイルをデータフレームにする
                elif extention == tsv_extention:
                    contents = ContentsControl.tsv_file_insert_dataframe(target_file) # tsvファイルをデータフレームにする
                else:
                    logging.error("this extention is not compatible! =>「{}」 ")

                # データフレームのヘッダーを取得
                columns = contents.columns.tolist()

                # ヘッダーの検索 => 会社と掲載開始日についてはkeyがブレるので正規表現でヘッダーを検索する
                company_name_key = [x for x in columns if company_name_search.match(x)][0]
                posting_start_date_key = [x for x in columns if posting_start_date_search.match(x)][0]

                # 問い合わせ済み企業の行を削除
                contents = pd.concat([contents, inquired_dataframe]).drop_duplicates(subset=[prefecture_key, address1_key, address2_key, address3_key], keep=False)

                # 全体の余計な記号などを削除する
                contents = contentscontrol.contents_strip(columns, contents)

                # 電話番号による都道府県を補完処理
                print(target_file)
                chdir(target_directory)
                areacode_dataframe = fillblanks.pickle_to_dataframe(areacode_file_name)
                chdir(target_path)
                contents = fillblanks.fill_prefecture_by_phone_number(areacode_dataframe, contents)

                # 会社名のところにあるアスタリスクなどの削除を行う。
                contents = contentscontrol.replace_company_contents(contents, company_name_key)

                # 掲載開始日の週の月曜日を取得し、加工する
                posting = ContentsControl.getDateMonday(contents[posting_start_date_key].values[0])
                output_name_date = posting.replace('/', '')
                if not posting == contents[posting_start_date_key].values[0]:
                    contents[posting_start_date_key] = posting
                    print("posting date is changed!")

                # エラーの検出処理
                tel_error, company_name_error, postal_code_error, postal_prefecture_error, address3_error = contentscontrol.error_detection(contents, tel_key=tel_key, company_name_key=company_name_key, postal_code_key=postal_code_key, prefecture_key=prefecture_key, address3_key=address3_key)

                # 掲載開始日の修正
                # いらない行を削ぎ落として問い合わせを行う行のみを抽出する
                drop_index = list(set(postal_code_error.index.tolist() + address3_error.index.tolist() + tel_error.index.tolist()))
                right_contents = contents.drop(drop_index)
                contents_length = length(right_contents)
                updated_inquired_dataframe = OutputExcel.add_row_inquired_dataframe(right_contents, inquired_dataframe)

                # 正常行とエラー行をそれぞれexcel出力する
                output_name = target_file.split(".")[0]
                chdir(inquired_path)
                output_excel(media_name, updated_inquired_dataframe) # 問い合わせファイルをアップデートする。
                chdir(output_path)
                output_excel(output_name+'_'+str(contents_length)+'_'+output_name_date+'_'+output_name_date, right_contents)
                chdir(error_path)
                if length(company_name_error) > 0:
                    output_excel(output_name+'_company_name_error', company_name_error)
                if length(address3_error) > 0:
                    output_excel(output_name+'_address3_error', address3_error)
                if length(postal_code_error) > 0:
                    output_excel(output_name+'_postal_code_error', postal_code_error)
                if length(tel_error) > 0:
                    output_excel(output_name+'_tel_error', tel_error)
                if length(postal_prefecture_error) > 0:
                    output_excel(output_name+'_postal_prefecture_error', postal_prefecture_error)
        else:
            print('target files is not found in edited folder!')
            exit(1)

    def inquired_row_to_dataframe(target_directory, media_name):
        inquired_file_search_name = '*' + media_name + '*.*'
        inquired_file = glob.glob(target_directory+'/'+inquired_file_search_name)
        print(inquired_file)
        if inquired_file:
            contents = ContentsControl.excel_file_insert_dataframe(inquired_file[0])
            return contents
        else:
            logging.error('inquired_file is not found')


class FillBlanks():
    # 市外局番ファイルをpickle化するための関数
    def dataframe_to_pickle(file_name, dataframe, file_path=None, save_path=None):
        chdir = os.chdir
        if file_path:
            chdir(file_path)
        else:
            chdir(os.path.dirname(os.path.abspath(__file__)))

        with open(file_name, 'wb') as f1:
            if save_path:
                chdir(save_path)
            else:
                chdir(os.path.dirname(os.path.abspath(__file__)))

            if os.path.exists(file_name):
                dataframe.to_pickle(file_name)
            else:
                logging.error("「{}」 is not found!".format(file_name))

    # 市外局番一覧ファイルをpickle化したものを読み込む関数
    def pickle_to_dataframe(file_name):
        dataframe = pd.read_pickle(file_name)
        dataframe = dataframe.dropna()
        pd.options.display.precision = 4
        dataframe['市外局番'] = dataframe['市外局番'].astype(int).astype(str).str.zfill(4)
        return dataframe

    # 電話番号の市外局番で埋める処理を入れる
    def fill_prefecture_by_phone_number(area_code_dataframe, fill_dataframe):
        print("fix the prefecture errors by area code...")
        phone_number_key = 'TEL'
        prefecture_key = '都道府県'

        # 都道府県埋めが必要な県のみに行を絞る
        # dataframe = fill_dataframe[(fill_dataframe[prefecture_key] == '') or (fill_dataframe[prefecture_key].str.isnull())]
        dataframe = fill_dataframe[fill_dataframe[prefecture_key] == ''].values
        data = fill_dataframe[fill_dataframe[prefecture_key].isnull()]
        exit(1)


class ContentsControl():
    # contents:dataframe
    def replace_company_contents(contents, company_name_key):
        name_replace = contents[company_name_key].replace
        contents[company_name_key] = name_replace('\*', ' ', regex=True)
        contents[company_name_key] = name_replace('\＊', ' ', regex=True)
        contents[company_name_key] = name_replace('(株)', '株式会社', regex=True)
        contents[company_name_key] = name_replace('（株）', '株式会社', regex=True)
        contents[company_name_key] = name_replace('㈱', '株式会社', regex=True)
        contents[company_name_key] = name_replace('(有)', '有限会社', regex=True)
        contents[company_name_key] = name_replace('（有）', '有限会社', regex=True)
        contents[company_name_key] = name_replace('㈲', '有限会社', regex=True)

        return contents

    def contents_strip(columns, contents):
        for column in columns:
            contents[column] = contents[column].astype(str)
            contents[column] = contents[column].map(lambda x: x.strip().strip('\"'))
            contents[column] = contents[column].map(lambda x: x.strip('=')) # 「=」を削除
            contents[column] = contents[column].map(lambda x: x.replace('\n','')) # 「\n」(改行)を削除

        return contents

    # 取ってきた日付の内容が条件に合わない場合その週の月曜日の日付を取得する
    # date:str
    def getDateMonday(date):
        # date = datetime.date.today()
        get_date = datetime.datetime.strptime(date, "%Y/%m/%d")
        day = get_date.weekday()

        if day == 0:
            return date
        else:
            mondaydate = get_date - datetime.timedelta(days=day)
            return mondaydate.strftime("%Y%m%d")

    # target_file(csv)の内容をarrayにinsert
    # 現在は使う予定なし。
    def csv_file_insert_dataframe(target_file):
        print("csv file is loading...")
        try:
            data_df = pd.read_csv(target_file, encoding="utf8", engine="python", na_values='')
            # data_df.columns
            columns = data_df.columns
            # いらない列の削除
            drop_col = columns[36:]
            data_df = data_df.drop(drop_col, axis=1)
            print("csv file is converted to dataframe!")
            return data_df
        except ValueError:
            # 読み込めないということはカラムがおかしいということなので。
            logging.error("csv file : Columns Mistake error")
            exit(1)

    def excel_file_insert_dataframe(target_file):
        print("excel file is loading...")
        try:
            df = pd.read_excel(target_file, sheet_name='Sheet1')
            columns = df.columns
            drop_col = columns[36:]
            data_df = df.drop(drop_col, axis=1)
            print("excel file is converted to dataframe!")
            print(data_df)
            return data_df
        except ValueError:
            # 読み込めないということはカラムがおかしいということなので。
            logging.error("excel file : Columns Mistake error")
            exit(1)
        except xlrd.biffh.XLRDError:
            logging.error("excel file : XLRDError")
            exit(1)

    def tsv_file_insert_dataframe(target_file):
        print("tsv file is loading...")
        header = ['No', '媒体名', '掲載開始日＝データ取得日', '事業内容', '職種','会社名(詳細ページの募集企業名)',
        '郵便番号', '都道府県', '住所1', '住所2', '住所3', 'TEL','担当部署', '担当者名', '上場市場','従業員数',
        '資本金', '売上高', '広告スペース', '大カテゴリ','小カテゴリ', '掲載案件数', '派遣', '紹介', 'フラグ数',
        'FAX', 'データ取得日', '版', '企業ホームページ','版コード', '広告サイズコード', '最寄り駅', '給与欄',
        '勤務時間欄', '詳細ページ\u3000キャッチコピー','電話番号（TWN記載ママ）']
        try:
            use_cols = range(0,36)
            data_df = pd.read_csv(target_file, sep='\t', names=header, usecols=use_cols, engine='python', encoding='utf-8')
            print("tsv file is converted to dataframe!")
            return data_df
        except IndexError:
            # 読み込めないということはカラムがおかしいということなので。この後に処理を続けるのはクソだがこの処理でやってみる
            # カラムとカラムの間にある改行一つまでならこのエラー処理で対応可能。
            data = []
            length = len
            import_default_column_num = 52
            use_default_column_num = 36

            # 列ずれの修正処理
            with open(target_file, "r") as f:
                reader = csv.reader(f, delimiter='\t')
                data = [x for x in reader]
                save_index = []

                for index, row in enumerate(data):
                    if length(row) < import_default_column_num:
                        if data[index+1][0] == '':
                            del data[index + 1][0]
                        row.extend(data[index+1])
                        # save_index.append(index+1)
                        del data[index+1]

                # 使うのは37列だけなのでそれ以降の列は削除する
                for index, d in enumerate(data):
                    if length(d) > use_default_column_num:
                        del d[use_default_column_num:]
                data.insert(0, header)
                contents = pd.DataFrame(data[1:], columns=data[0])
                print("tsv file is converted to dataframe!")

                return contents

    def get_tel(tel_list):
        if len(tel_list) == 0:
            return None
        else:
            return tel_list[0]

    # contents:dataframe
    def error_detection(contents, tel_key=None, company_name_key=None, postal_code_key=None, address3_key=None, prefecture_key=None):
        get_phone_number = ContentsControl.get_tel

        if tel_key:
            contents[tel_key] = contents[tel_key].str.findall('\d{2,4}-\d{2,4}-\d{2,4}')
            contents[tel_key] = contents[tel_key].apply(get_phone_number)
            tel_error = contents[(contents[tel_key].astype('str').str.len() < 12) | (contents[tel_key].astype('str').str.len() > 13)] # 電話番号が不適切
        else:
            tel_error = contents
        if company_name_key:
            company_name_error = contents[(contents[company_name_key].str.len() < 3)]
        else:
            company_name_error = contents
        if postal_code_key:
            postal_code_error = contents[(contents[postal_code_key].astype('str').str.len() < 7) | (contents[postal_code_key].astype('str').str.len() > 8)] # 郵便番号がない行
            print(postal_code_error[postal_code_key])
            if prefecture_key:
                postal_prefecture_error = postal_code_error[postal_code_error[prefecture_key].astype('str').str.len() <= 2] # 郵便番号も都道府県もない
            else:
                postal_prefecture_error = contents
        else:
            postal_code_error = contents
            postal_prefecture_error = contents
        if address3_key:
            address3_error = contents.loc[contents[address3_key].astype('str').str.len() <= 3] # 住所がない
        else:
            address3_error = contents

        return tel_error, company_name_error, postal_code_error, postal_prefecture_error, address3_error


class OutputExcel():
    def dataframe_output(output_name, contents):
        headers = contents.columns
        writer = pd.ExcelWriter('{}.xlsx'.format(output_name), engine='xlsxwriter')
        contents.to_excel(writer, sheet_name='Sheet1',index=False)
        writer.save()
        writer.close()

    def add_row_inquired_dataframe(right_dataframe, inquired_dataframe):
        prefecture_before_key = '都道府県(修正前)'
        address1_before_key = '住所1(修正前)'
        address2_before_key = '住所2(修正前)'
        address3_before_key = '住所3(修正前)'
        prefecture_key = '都道府県'
        address1_key = '住所1'
        address2_key = '住所2'
        address3_key = '住所3'

        columns = right_dataframe.columns

        for column in columns:
            if (column == prefecture_key):
                continue
            elif (column == address1_key):
                continue
            elif (column == address2_key):
                continue
            elif (column == address3_key):
                continue
            else:
                right_dataframe = right_dataframe.drop(column, axis=1)
        updated_inquired_dataframe = pd.concat([right_dataframe, inquired_dataframe])

        return updated_inquired_dataframe


class FileControl():
    # ターゲットディレクトリに入っているファイル名を全て取ってくる関数
    # target_directory: フルパス, target_extention: extentionを指定する。基本はglobal変数のものを使用
    def get_find_all_files_name(target_directory, target_extention):
        files = os.listdir(target_directory)
        return_files = []
        for file in files:
            if not target_extention == '': # target_extentionが空ではない時
                root, ext = os.path.splitext(file)
                print(root)
                print(ext)
                print(ext is target_extention)
                if ext is target_extention: # target_extentionが一致した時
                    return_files.append(file)
        return return_files


if __name__ == '__main__':
    # args = sys.argv
    media_name = 'フロムエー' # args[1] # 第一引数は処理を行うメディアの名前
    # dataframe = ContentsControl.excel_file_insert_dataframe('error_test.xlsx')

    # 市外局番一覧を都道府県と結びつけるエクセルファイルをpickle化することで高速化を図る
    #FillBlanks.dataframe_to_pickle('areacode2.pkl', dataframe)
    # areacode = FillBlanks.pickle_to_dataframe('areacode2.pkl')
    # FillBlanks.fill_prefecture_by_phone_number(areacode, dataframe)
    target = PerlProcess.mdaCheckCnt(os.getcwd(), media_name)
