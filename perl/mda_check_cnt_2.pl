#!/usr/bin/perl
use strict;
use warnings;
use open IN => ':utf8';
use open OUT => ':utf8';
use open IO => ':utf8';
use Encode;
use Time::Local;
#use bytes;

package cnt;
{ #package cnt
#処理対象ファイルの格納されたディレクトリを標準入力から取得する。
#our $dirname = <STDIN>;
our $dirname = $ARGV[0];
chomp($dirname);
if($dirname !~ /^\.\//){
	$dirname = "./".$dirname;
} #標準入力チェック

if($dirname =~ /\/$/){
	$dirname =~ s/^(.*)\/$/$1/;
} #標準入力チェック

#ファイルのカラム数をカウントする。
our @nf;
#編集ファイルの出力先ディレクトリの作成,修正後ファイルの削除+新規作成を制御する。(1:on/0:off)
# seugyoってなんだ？数値っぽいが。もしかして整行？
#my $seigyo = 0;
my $seigyo = $ARGV[1];
#logfile の初期化
open(LOGFILE,">$dirname/mda_check_cnt.log") or die "$!";
print LOGFILE "";
close(LOGFILE);

#editディレクトリの作成コマンド
my $mk_dir = "mkdir $dirname/edited";
my $rm_dir = "rm -rf $dirname/edited";

opendir(DIR,$dirname) or die "$dirname:$!";

#編集ファイルの出力先ディレクトリの有無を確認する。
my $edited_exists = 0;
	if(-e $dirname.'/edited'){
		$edited_exists += 1;
	} # if

if($seigyo){
	if($edited_exists == 0){
		system($mk_dir);
	}else{
		system($rm_dir);
		system($mk_dir);
	} #if mkdir
} #if seigyo

# -------------------------------------------------------------------------------

while(my $dir = readdir(DIR)){
	#next unless(-f $dir);    #この行を有効にすると何故か対象ファイルが処理されない。謎。
	next unless($dir =~ /\.csv/);
	&debug_print(0,$dir);

	open(FILE,$dirname."/".$dir) or die "$!";
	#読み込み回数をカウントする。0のときヘッダ行。
	my $cnt = 0;
	#データ不備の件数をカウントする配列。
	my @error_cnt = (0,0,0,0,0,0,0,0,0);
	@nf = ();
	while(my $line = <FILE>){
		chomp($line);             #読み込んだレコードから改行コードを削除する。
		$line =~ s/^"(.*)"$/$1/g; #先頭末尾のダブルクォーテーションを削除。
		our $record = $line;     #デバッグに使用する。
		$record = "\"".$record."\"\n";
		#読み込んだレコードをカラム毎に分解して配列に格納擦る。
		our @row = split(/","/,$line,-1);
		#ヘッダを取得し、項目ごとに配列に格納する。
		our @header = &get_header(@row) if($cnt==0);

		#データ取得日対応 20170728
		@row = &date_edit($cnt,@row);

		#sub:debug_print の第一引数は制御文字 (1:on/0:off)
		&nf_varidation(@row);
		&debug_print(0,@row) if($cnt==0);
		&debug_print(0,$dir) if($cnt==0);
		&debug_print(0,@header) if($cnt==0);
		&debug_print(0,@row);
		#エラーデータ修正後の編集ファイルを作成する。
		&edit_new($dir,$cnt,@row) if($seigyo);

		#エラーデータを標準出力する。
		&error_list($dir,@row)unless($cnt==0);
		#エラー件数を計上する。
		@error_cnt = &varidation(@error_cnt,$dir,@row) unless($cnt==0);
		$cnt += 1;
	} #while file
	close(FILE);
	#ファイル名、レコード数、エラーデータ数を一覧で標準出力する。
	print "file_name:\"$dir\" rec:$cnt\n";
	&error_print(@error_cnt);
	for(my $i=0;$i<@cnt::nf;$i++){
		print "column_cnt[$cnt::nf[$i]->[0]] = [$cnt::nf[$i]->[1]]\n";
	} #for
	my $border = '-' x 150;
	print $border,"\n";
} #while dir
close(DIR);

#データ取得日調整案件20170728

sub date_edit{
	my $no = shift(@_);
	my @input = @_;

	my $start_date = $input[2];
	my $end_date = $input[26];
	$start_date =~ s/[^0-9]//g;
	$end_date =~ s/[^0-9]//g;

	#header 行は処理対象外
	if($no == 0){
		return @input;
	}

	#start_date end_date に空白が含まれる場合、或いは日付が前後する場合は何もしない。
	if($start_date eq '' or $end_date eq ''){
		return @input;
	}elsif($start_date > $end_date){
		return @input;
	} #if

	my $in_date = $input[26];
	my $inyear; my $inmonth; my $inday;
	if($in_date =~ /[0-9]{4}\/[0-9]{1,2}\/[0-9]{1,2}/){
		$in_date =~ s/([0-9]{4}\/[0-9]{1,2}\/[0-9]{1,2})/$1/;
		($inyear,$inmonth,$inday) = split('/',$in_date,-1);
	}elsif($in_date =~ /[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}/){
		$in_date =~ s/([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})/$1/;
		($inyear,$inmonth,$inday) = split('-',$in_date,-1);
	}elsif($in_date =~ /[0-9]{8}/){
		$in_date =~ s/([0-9]{4})([0-9]{2})([0-9]{2})/$1$2$3/;
		$inyear = $1; $inmonth = $2; $inday = $3;
	}elsif($in_date =~ /[0-9\/]{6,}/){
		$in_date =~ s/([0-9]{4})(.*)$/$1$2/;
		$inyear = $1;
		($inmonth,$inday) = split('/',$2,-1);
	}elsif($in_date =~ /[0-9\-]{6,}/){
		$in_date =~ s/([0-9]{4})(.*)$/$1$2/;
		$inyear = $1;
		($inmonth,$inday) = split('/',$2,-1);
	}

	$inmonth -= 1;
	$inmonth = 11 unless($inmonth >= 0);
	$inyear -= 1900;

	#データ取得日の曜日を取得する。
	return @input unless(defined($inyear) and defined($inmonth) and defined($inday) and $inday != 0);
	my $byo = Time::Local::timelocal('00','00','00',$inday,$inmonth,$inyear);
	my ($sec,$min,$hour,$day,$month,$year,$wdy,$yday) = localtime($byo);

	my $interval = $wdy - 1; #月曜基準で日付差分を得る。
	$interval = 6 if($interval == -1);

	#データ取得日が月曜の場合は編集せずに処理を抜ける。
	if($interval == 0){
		return @input;
	}

	my @week = qw(Sun Mon Tue Wed Thu Fri Sat);
	my $before_wdy = $week[$wdy];

	$byo -= 60*60*24*$interval;

	($sec,$min,$hour,$day,$month,$year,$wdy,$yday) = localtime($byo);

	#正規化する
	$year += 1900;
	$month += 1;
	$year = sprintf("%04s",$year);
	$month = sprintf("%02s",$month);
	$day = sprintf("%02s",$day);
	my $after_wdy = $week[$wdy];

	my $edit_date = $year."/".$month."/".$day;
	my $vari_date = $year.$month.$day;

	#データ取得日の編集が原因で前後した場合は掲載開始日も調整する。
	if($start_date > $vari_date){
		splice(@input,2,1,$edit_date);
		splice(@input,26,1,$edit_date);
	}else{
		splice(@input,26,1,$edit_date);
	}

	print "debug_print/////date_edit:$start_date($before_wdy) -> $vari_date($after_wdy)\n";

	return @input;

}


sub nf_varidation{
	my @in = @_;
	my $nfcnt = @in;
	my $col = @cnt::nf;
	my $flg = 1;

	for(my $i=0;$i<$col + 1;$i++){
		if($i < $col){
			if($nfcnt == $cnt::nf[$i]->[0]){
				$cnt::nf[$i]->[1] += 1;
				$flg = 0;
			} #if
		}else{
			if($flg){
				$cnt::nf[$i]->[0] = $nfcnt;
				$cnt::nf[$i]->[1] = 1;
			} #if
		} #if
	} #for
} #sub nf_varidation


#カラムズレデータを検出する為に導入。ブレイクポイントを設定する。
sub NF_cnt{
	my $head_cnt = @cnt::header;
	my @in = @_;
	my $NF_cnt = @in;

	if($head_cnt != $NF_cnt){
		#return "header_cnt:$head_cnt ::NF_cnt:$NF_cnt\n";
		return $NF_cnt;
	}else{
		#return 0;
		return $NF_cnt;
	} #if
} #sub NF_cnt


#ゼロパディング2桁の通し番号_[ヘッダ項目]の形でヘッダ配列の項目を作成するサブルーチン。
sub get_header{
my @head_in = @_;
my @head_out;
	for(my $i=0;$i<@head_in;$i++){
		my $no = sprintf("%02d",$i+1);
		push(@head_out,$no."_\[$head_in[$i]\]");
	} # for
return (@head_out);
} #sub get_header

#レコード単位でデータの検証を行い、エラーカウントを計上しながらログファイルにエラー内容を書き出してゆくサブルーチン。
sub varidation{
my @out = splice(@_,0,9);
my $dir = shift(@_);
my @in = @_;
#ここでデコードしないと出力された全角文字が何故か文字化けするので意味も解らずデコードしてます。
$dir = Encode::decode('utf8',$dir);

open(LOGFILE,">>$cnt::dirname/mda_check_cnt.log") or die "$!";

my $start_date = $in[2];
my $end_date = $in[26];
$start_date =~ s/[^0-9]//g;
$end_date =~ s/[^0-9]//g;

	if($start_date eq '' or $end_date eq ''){
		$out[0] += 1;
		print LOGFILE "$dir:post_date_error:$in[0]:start:\"$in[2]\":end\"$in[26]\"\n";
	}elsif($start_date > $end_date){
		$out[0] += 1;
		print LOGFILE "$dir:post_date_error:$in[0]:start:\"$in[2]\":end\"$in[26]\"\n";
	} #if

	if($in[18]=~/[^0-9\,]/){
		$out[1] += 1;
		print LOGFILE "$dir:space_data_error:$in[0]:\"$in[18]\"\n";
	} #if

	#全角文字を扱うときは内部文字コードにデコードしないとテキスト処理が行えない。
	#また、リクナビ派遣は料金計算にフラグを使用する唯一の媒体。
	my $rikunabi = Encode::decode('utf8','リクナビ派遣');
	my $media_name = $in[1];
	#$media_name = Encode::decode('utf8',$media_name);

	if(($in[24]=~/[^0-9\,]/ and $media_name eq $rikunabi) or ($in[24] ne '' and $media_name ne $rikunabi)){
		$out[2] += 1;
		print LOGFILE "$dir:flag_data_error:$in[0]:\"$in[24]\"\n";
	} #if

	if($in[6]=~/[^0-9\-]/){
		$out[3] += 1;
		print LOGFILE "$dir:zip_code_error:$in[0]:\"$in[6]\"\n";
	} #if

#	if($in[11]=~/[^0-9\-]/){
#		$out[4] += 1;
#		print LOGFILE "$dir:tel_error:$in[0]:\"$in[11]\"\n";
#	} #if

	if($in[11] =~ /[^0-9\-]/ or ($in[1] =~ /web.{0,1}an/ and $in[11] =~ /^050.{0,1}529/)){
		$out[4] += 1;
		if($in[11] =~ /[^0-9\-]/){
			print LOGFILE "$dir:tel_error:$in[0]:\"$in[11]\"\n";
		}elsif($in[1] =~ /web.{0,1}an/ and $in[11] =~ /^050.{0,1}529/){
			print LOGFILE "$dir:web_an_tel_error:$in[0]:\"$in[11]\"\n";
		}#if
	} #if

	#全角アスタリスクのデコード
	my $zen_asuta = '＊';
	$zen_asuta = Encode::decode('utf8',$zen_asuta);

	if($in[5] eq ''){
		$out[5] += 1;
		print LOGFILE "$dir:corp_name_error:$in[0]:\"$in[5]\"\n";
	}elsif(($in[5] =~ s/$zen_asuta/$zen_asuta/g) > 2){
		$out[5] += 1;
		print LOGFILE "$dir:corp_asuta_error:$in[0]:\"$in[5]\"\n";
	}elsif($in[5] =~ /\#N\/A/){
		$out[5] += 1;
		print LOGFILE "$dir:corp_asuta_error:$in[0];\"$in[5]\"\n";
	} #if

	if($in[7] eq '' or $in[8] eq '' or $in[9] eq ''){
		$out[6] += 1;
		print LOGFILE "$dir:corp_address_error:$in[0]:\"$in[7]\",\"$in[8]\",\"$in[9]\",\"$in[10]\"\n";
	}elsif($in[7] =~ /\#N\/A/ or $in[8] =~ /\#N\/A/ or $in[9] =~ /\#N\/A/ or $in[10] =~ /\#N\/A/){
		$out[6] += 1;
		print LOGFILE "$dir:corp_address_error:$in[0]:\"$in[7]\",\"$in[8]\",\"$in[9]\",\"$in[10]\"\n";
	} #if

	if(defined($in[36]) == 1){
		if($in[36] =~ /[^0-9]/){
			$out[7] += 1;
			print LOGFILE "$dir:seikyusaki_cord_error:$in[0]:\"$in[36]\"\n";
		} #if
	}else{
		$out[7] += 1;
		print LOGFILE "$dir:undefined_37_seikyusaki_cord:$in[0]\"undef\"\n";
	} #if

	if(defined($in[37]) == 1){
		if($in[37] =~ /[^0-9]/){
			$out[8] += 1;
			print LOGFILE "$dir:CompNo_error:$in[0]:\"$in[37]\"\n";
		} #if
	}else{
		$out[8] += 1;
		print LOGFILE "$dir:undefined_38_CompNo:$in[0]:\"undef\"\n";
	} #if

close(LOGFILE);
return @out;
} # sub varidation

#処理したファイル毎にエラー件数の内訳を標準出力するサブルーチン。
sub error_print{
my @error = @_;
my @error_list = ('post_date_error','space_data_error','flag_data_error','zip_code_error','tel_error','corp_name_error','corp_address_error','seikyuCD_error','CompNo_error');
	for(my $i=0;$i<@error;$i++){
		printf( "%02d_%-20s:%6d\n",$i+1,$error_list[$i],$error[$i]);
	} #for
} # sub error_print

#第一引数は制御文字。(1:on/0:off) 改修作業で使用する。
sub debug_print{
my $debug_print = shift(@_);
my @debug = @_;
	if($debug_print){
		for(my $i=0;$i<@debug;$i++){
			#printf("debug_print_%02s :\"%s\"\n",$i+1,$debug[$i]);
			my $no = sprintf("%02d",$i+1);
			#&Encode::encode('utf-8',$debug[$i]);
			print &Encode::encode('utf-8',"debug_print_$no:\"$debug[$i]\"\n");
		} # for
	} # if
} #sub debug_print

#処理対象のレコード情報をヘッダ毎に標準出力するサブルーチン。デバッグに使用する。
sub print{
my @list=@_;

	for(my $i=0;$i<@list;$i++){
		print &Encode::encode('utf-8',"$cnt::header[$i] = \"$list[$i]\"\n");
	} # for
} #sub print

#エラーデータを検出した際に該当レコードを標準出力に出力する。サブルーチンprint を内部で呼び出している。
sub error_list{
my $dir = shift(@_);
my @in = @_;

my $start_date = $in[2];
my $end_date = $in[26];
$start_date =~ s/[^0-9]//g;
$end_date =~ s/[^0-9]//g;

my $border = '-' x 150;

	if($start_date eq '' or $end_date eq ''){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	}elsif($start_date > $end_date){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	if($in[18]=~/[^0-9\,]/){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	my $rikunabi = Encode::decode('utf8','リクナビ派遣');
	my $media_name = $in[1];
	#$media_name = Encode::decode('utf8',$media_name);

	if(($in[24]=~/[^0-9\,]/ and $media_name eq $rikunabi) or ($in[24] ne '' and $media_name ne $rikunabi)){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	if($in[6]=~/[^0-9\-]/){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	if(($in[11]=~/[^0-9\-]/) or ($in[1] =~ /web.{0,1}an/ and $in[11] =~ /^050.{0,1}529/)){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	my $zen_asuta = '＊';
	$zen_asuta = Encode::decode('utf8',$zen_asuta);

	if($in[5] eq ''){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	}elsif(($in[5] =~ s/$zen_asuta/$zen_asuta/g) > 2){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	}elsif($in[5] =~ /\#N\/A/){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	if($in[7] eq '' or $in[8] eq '' or $in[9] eq ''){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	}elsif($in[7] =~ /\#N\/A/ or $in[8] =~ /\#N\/A/ or $in[9] =~ /\#N\/A/ or $in[10] =~ /\#N\/A/){
		print "$dir\n";
		&print(@in);
		print $border,"\n";
	} #if

	if(defined($in[36]) == 1 and defined($in[37]) == 1){
		if($in[36] =~ /[^0-9]/){
			print "$dir\n";
			&print(@in);
			print $border,"\n";
		} #if

		if($in[37] =~ /[^0-9]/){
			print "$dir\n";
			&print(@in);
			print $border,"\n";
		} #if
	} #ir

} # sub varidation

sub edit_new{
my $dir = shift(@_);
my $no = shift(@_);
my @in = @_;
open(EDIT,">>$cnt::dirname/edited/$dir");

my $start_date = $in[2];
my $end_date = $in[26];
$start_date =~ s/[^0-9]//g;
$end_date =~ s/[^0-9]//g;

	my $rikunabi = Encode::decode('utf8','リクナビ派遣');
	my $media_name = $in[1];
	#$media_name = Encode::decode('utf8',$media_name);
	my $zen_asuta = '＊';
	$zen_asuta = Encode::decode('utf8',$zen_asuta);

	if($no == 0){
	#ヘッダは無条件に出力
		#print EDIT "\"$cnt::record\"\n";
		my $out = join('","',@in);
		$out = '"'.$out."\"\n";
		print EDIT $out;
	}elsif($start_date eq '' or $end_date eq ''){
	#掲載開始日と掲載終了日(データ取得日)のエラーレコードは取込対象外。
		return;
	}elsif($start_date > $end_date){
	#掲載開始日と掲載終了日(データ取得日)のエラーレコードは取込対象外。
		return;
	}elsif($in[18]=~/[^0-9\,]/ or $in[18] eq ''){
	#スペースエラーレコードは取込対象外。
		return;
	}elsif($in[24]=~/[^0-9\,]/ and $media_name eq $rikunabi){
	#フラグエラーレコードはリクナビ派遣の場合は取込対象外。
		return;
#	}elsif($in[24] ne '' and $in[1] ne 'リクナビ派遣'){
#	#リクナビ派遣以外のフラグエラーレコードはカラムをブランクにして取り込む。
#		return;
#	}elsif($in[6]=~/[^0-9\-]/){
#	#郵便番号エラーレコードはカラムをブランクにして取り込む。
#		return;
#	}elsif($in[11]=~/[^0-9\-]/){
#	#電話番号エラーレコードはカラムをブランクにして取り込む。
#		return;
	}elsif($in[5] eq ''){
	#企業名エラーレコードは取込対象外。
		return;
	}elsif(($in[5] =~ s/$zen_asuta/$zen_asuta/g) > 2){
	#企業名エラーレコードは取込対象外。
		return;
	}elsif($in[5] =~ /\#N\/A/){
	#企業名エラーレコードは取込対象外。
		return;
	}elsif($in[7] eq '' or $in[8] eq '' or $in[9] eq ''){
	#住所エラーレコードは取込対象外。
		return;
	}elsif($in[7] =~ /\#N\/A/ or $in[8] =~ /\#N\/A/ or $in[9] =~ /\#N\/A/){
	#住所エラーレコードは取込対象外。
		return;
	}else{
		for(my $i=0;$i<@in;$i++){
			if($i == 6){
				if($in[$i] =~ /[^0-9\-]/){
					splice(@in,$i,1,'');
				}
			}elsif($i == 10){
				if($in[10] =~ /\#N\/A/){
					splice(@in,$i,1,'');
				}
			}elsif($i == 11){
				if($in[1] =~ /web.{0,1}an/ and $in[$i] =~ /^050.{0,1}529/){
					splice(@in,$i,1,'');
				}elsif($in[$i] =~ /[^0-9\-]/){
					splice(@in,$i,1,'');
				}
			}elsif($i == 24){
				if($media_name ne $rikunabi and $in[$i] ne ''){
					splice(@in,$i,1,'');
				}
			}elsif($i == 36){
				if($in[$i] =~ /[^0-9]/){
					splice(@in,$i,1,'');
				}
			}elsif($i == 37){
				if($in[$i] =~ /[^0-9]/){
					splice(@in,$i,1,'');
				}
			} #if
		} #for

		#ブレイクポイントの埋め込み
	#	my @NF = &NF_cnt(@in);
	#	my $b = $NF[0];
	#	if(defined($b) == 1 and $b != 36){
	#		$DB::single = 1;
	#	}

		#20170710 space must be error 対応 start
		for(my $k=0;$k<@in;$k++){
			$in[$k] =~ s/"//g;
		} #for
		#20170710 space must be error 対応 end
		my $out_0 = join('","',@in);
		$out_0 = '"'.$out_0."\"\n";
		#カラムズレがエンコードのせいかと疑った時に書き下したコード
		#$out_0 = Encode::encode('utf8',$out_0);
		print EDIT $out_0;
	} #if

close(EDIT);
return;
} # sub edit_new

} #package cnt
