#!/usr/bin/perl
use strict;
use warnings;

my $dir = $ARGV[0];

# フォルダを引数にしてそのフォルダにmda_log.logをfindコマンドを実行した上で作成する。これは取り込み対象外のファイルのリストらしい。
open(FIND,'>./mda_log.log')or die "$!"; # 書き込みモードでmda_log.logを開く、もしFindなどがダメだったらエラーを出す
	system("find ./$dir -name \"mda_check_cnt.log\" > ./mda_log.log"); # target_directoryの中からmda_check_cnt.logファイルを探し、mda_log.logを出力
close(FIND);

# 取り込み対象外のファイルを読み込み
open(LOGFILE,'./mda_log.log')or die "$!";
while(my $logfile = <LOGFILE>){
	open(FILE,$logfile)or die "$!";
	while(my $line = <FILE>){
		next unless($line =~ /^TABAITAI/);
		next unless($line =~ /corp_asuta/ or $line =~ /corp_name/ or $line =~ /post_date_error/ or $line =~ /space_data_error/ or $line =~ /corp_address_error/);
		print $line;
	} #while $line
	close(FILE);
} #while $logfile
close(LOGFILE);
