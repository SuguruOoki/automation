#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bz2,os,sys,glob,re,requests,json,datetime,shutil,csv,xlsxwriter,pandas as pd
import logging,subprocess
import numpy as np
global file_extention
global excel_extention
global csv_extention

file_extention = '.txt'
excel_extention = '.xlsx'
csv_extention = '.csv'

class PerlProcess():
    def logCheck(target_directory):
        log_file = 'mda_log.log'
        try:
            if target_directory:
                check = commands.getoutput("find ./{} -name \"mda_check_cnt.log\" > ./mda_log.log".format(target_directory))
        except ValueError:
            logger.error("Not Found Target Directory or mda_check_cnt.log")

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
            logger.error('Not Found {}'.format(log_file))

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
    def mdaCheckCnt(target_directory):
        column_cnt = 0
        log_file = 'mda_check_cnt.log'
        files = []
        # f = open(log_file, "wb") # ログファイルの初期化
        # f.close()

        # editディレクトリの作成
        os.chdir(target_directory)
        target_path = target_directory+'/'+'edited'
        if not os.path.exists(target_path):
            args = ['mkdir', 'edited']
            subprocess.check_call(args)
            os.chdir(target_path)
        else:
            os.chdir(target_path)

        csv_files = FileControl.get_find_all_files_name(target_path,'.csv')

        if csv_files:
            error_count = [0,0,0,0,0,0,0,0,0]
            count = 0
            # csv_filesのファイルを読み込み、配列に入れてerrorを確認して修正する。
            # ここでは読み込んだレコードから改行コードと先頭末尾のダブルクォーテーションの削除,
            # データ取得日の入力などを行う
            for target_file in csv_files:
                contents = ContentsControl.csv_file_insert_dataframe(target_file)
                # なんでかNaNが残っている時があるので念のため。
                contents = contents.fillna('')
                # contents = contents.apply(lambda row: contents[co].str.contains('\n') for col in range(len(contents[col].columns)))
                columns = contents.columns.tolist()
                for column in columns:
                    contents[column] = contents[column].astype(str)
                    contents[column] = contents[column].map(lambda x: x.strip().strip('\"'))
                    contents[column] = contents[column].map(lambda x: x.strip('=')) # 「=」を削除
                    # contents[column] = contents[column].map(lambda x: x.replace('\*.....',''))
                # print(contents[contents['会社名(詳細ページの募集企業名)'].str.contains('.....\＊......')])
                # print(contents['TEL'].astype(str).apply(lambda x: np.where((len(x)>=10)&set(list(x)).issubset(list('.0123456789')),
                #                                                       '('+x[:3]+')'+x[3:6]+'-'+x[6:10],
                #                                                       'Phone number not in record')))
                # print(contents[contents['TEL'].astype(str).str.extract('+x[:3]+'-'+x[3:6]+'-'+x[6:10])']))
                #print(asterisk)
                # データ取得日についての処理を入れる
                # データ掲載開始日を月曜に直す処理を入れる
                # 途中のカラム数が違うものについてはDataframeに入らないのでそのエラー処理はここには入れない
                # OutputExcel.dataframe_output('output', contents)
        else:
            print('csv files is not found in edited folder!')
            exit(1)


# while(my $dir = readdir(DIR)){
# 	#next unless(-f $dir);    #この行を有効にすると何故か対象ファイルが処理されない。謎。
# 	next unless($dir =~ /\.csv/);
# 	&debug_print(0,$dir);
#
# 	open(FILE,$dirname."/".$dir) or die "$!";
# 	#読み込み回数をカウントする。0のときヘッダ行。
# 	my $cnt = 0;
# 	#データ不備の件数をカウントする配列。
# 	my @error_cnt = (0,0,0,0,0,0,0,0,0);
# 	@nf = ();
# 	while(my $line = <FILE>){
# 		chomp($line);             #読み込んだレコードから改行コードを削除する。
# 		$line =~ s/^"(.*)"$/$1/g; #先頭末尾のダブルクォーテーションを削除。
# 		our $record = $line;     #デバッグに使用する。
# 		$record = "\"".$record."\"\n";
# 		#読み込んだレコードをカラム毎に分解して配列に格納擦る。
# 		our @row = split(/","/,$line,-1);
# 		#ヘッダを取得し、項目ごとに配列に格納する。
# 		our @header = &get_header(@row) if($cnt==0);
#
# 		#データ取得日対応 20170728
# 		@row = &date_edit($cnt,@row);
#
# 		#sub:debug_print の第一引数は制御文字 (1:on/0:off)
# 		&nf_varidation(@row);
# 		&debug_print(0,@row) if($cnt==0);
# 		&debug_print(0,$dir) if($cnt==0);
# 		&debug_print(0,@header) if($cnt==0);
# 		&debug_print(0,@row);
# 		#エラーデータ修正後の編集ファイルを作成する。
# 		&edit_new($dir,$cnt,@row) if($seigyo);
#
# 		#エラーデータを標準出力する。
# 		&error_list($dir,@row)unless($cnt==0);
# 		#エラー件数を計上する。
# 		@error_cnt = &varidation(@error_cnt,$dir,@row) unless($cnt==0);
# 		$cnt += 1;
# 	} #while file
# 	close(FILE);



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
    def csv_file_insert_dataframe(target_file):
        # data = ""
        # count = 0
        # f = open(target_file, "r")
        # data = [[str(elm) for elm in v] for v in csv.reader(f)]
        data_df = pd.read_csv(target_file,encoding="utf8", engine="python", na_values='')
        # data_df.columns
        columns = data_df.columns
        drop_col = columns[36:]
        data_df = data_df.drop(drop_col, axis=1)
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
        writer = pd.ExcelWriter('{}.xlsx'.format(output_name), engine='xlsxwriter')
        contents.to_excel(writer, sheet_name='Sheet1')
        writer.save()



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
    target = PerlProcess.mdaCheckCnt(os.getcwd())
