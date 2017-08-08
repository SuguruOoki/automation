#!/usr/bin/perl
# 処理がうまくいかなかったファイルが処理済みかどうかを調べる

use strict;
use warnings;

# 処理前のディレクトリと処理後のディレクトリをしている引数
my $before = $ARGV[0];
my $after = $ARGV[1];
my $mv_flg = $ARGV[2];

# これは処理をするディレクトリとやるかどうかのフラグだと思われる。
my $before_dir = '/home/lamp_app/crm_source/codes/tmp/csv/Import/before/';
my $after_dir = '/home/lamp_app/crm_source/codes/tmp/csv/Import/after/';
my $exist_after = 0;

# 処理をする前のディレクトリを開き、その中に処理後のディレクトリが存在したら処理後だと判断しexist_afterのフラグを立てる。
opendir(NEW,$before_dir)or die "$!";
while(my $dir_1 = readdir(NEW)){
	next unless($dir_1 eq $after);
	$exist_after = 1;
} #while $dir_1
close(NEW);

# 処理後でなければ、まず処理後のものを入れるディレクトリを作成する。
unless($exist_after){
	system("mkdir $before_dir"."$after");
} #unless

my @aray;

# before_dirディレクトリ内にあるbeforeのディレクトリの中を見てTABAITAIと接頭辞が付いているxlsxファイルがあればaray配列に保存する。
opendir(BEFORE,$before_dir.$before)or die "$!";
while(my $dir_before = readdir(BEFORE)){
	next unless($dir_before =~ /TABAITAI.*\.xlsx?/);
	push(@aray,$dir_before);
} #while $dir_before
close(BEFORE);

my @list;
my %debug; # %debugってなんだ？？？

# リネームをしているらしい。
# after_dirディレクトリ内にあるbeforeディレクトリを開く。
# 開いたディレクトリを読んでTABAITAIと付いているcsvファイルがあれば
# listに何やらファイル名と共にフラグを入れているらしい。
opendir(AFTER,$after_dir.$before)or die "$!";
while(my $dir_after = readdir(AFTER)){
	next unless($dir_after =~ /TABAITAI.*\.csv/);
	for(my $i=0;$i<@aray;$i++){
	my $excel;
	my $csv;

	# 扱っているのは二次元配列の模様。四つのunlessを乗り越えてから色々処理が走るらしい。
	# definedは定義済みならtrueを返す
	# unlessは条件式が偽の時に{}内の処理を走らせる。
	unless(defined($list[$i]->[0])){$list[$i]->[0] = $aray[$i]}; # listの[0]が未定義なら定義する
	unless(defined($list[$i]->[1])){$list[$i]->[1] = '0'}; # listの[1]が未定義なら定義する。これは処理後かどうかを調べる際のフラグと思われる。
	unless(defined($csv)){$csv = 'undef'}; # csvが未定義ならundefを代入
	unless(defined($excel)){$excel = 'undef'}; # excelが未定義ならundefを代入

	$debug{$list[$i]->[0]} = 0; # 連想配列を定義する。listに入れたファイル名をキーにしてフラグを0に設定する。
	$debug{$dir_after} = 1; # 処理後のファイルを入れるディレクトリパスをキーにしてフラグを立てておく。

		if($list[$i]->[0] =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,}_[0-9]{1,}_[0-9]{1,})/){#
			$excel = $1;
		}elsif($list[$i]->[0] =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,}_[0-9]{1,})/){
			$excel = $1;
		}elsif($list[$i]->[0] =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,})/){
			$excel = $1;
		} #if excel

		if($dir_after =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,}_[0-9]{1,}_[0-9]{1,})/){
			$csv = $1;
		}elsif($dir_after =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,}_[0-9]{1,})/){
			$csv = $1;
		}elsif($dir_after =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,})/){
			$csv = $1;
		} #if excel

		if($excel eq $csv){
			$list[$i]->[1] = '1'; # csvとexcelファイルでファイル名が同じものが存在するようならばフラグを立てておく。
		} #if
	} #for
} #while $dir_before
close(BEFORE);

my $border = '-' x 100; # printの際にファイル名の間に入れるボーダーと思われる。
foreach my $key (sort(keys(%debug))){
	if($key =~ /\.xls/){
		print $border,"\n";
		print $key,"\n";
	}else{
		print"⇒",$key,"\n";
	}#if
}#foreach


if($mv_flg){
for(my $j=0;$j<@list;$j++){
	if($list[$j]->[1] == '0'){
		system("mv ".$before_dir.$before."/".$list[$j]->[0]." ".$before_dir.$after."/");
	} #if
} #for
}#if
