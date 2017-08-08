#!/usr/bin/perl
use strict;
use warnings;

my $before = $ARGV[0];
my $after = $ARGV[1];
my $mv_flg = $ARGV[2];

my $before_dir = '/home/lamp_app/crm_source/codes/tmp/csv/Import/before/';
my $after_dir = '/home/lamp_app/crm_source/codes/tmp/csv/Import/after/';
my $exist_after = 0;

opendir(NEW,$before_dir)or die "$!";
while(my $dir_1 = readdir(NEW)){
	next unless($dir_1 eq $after);
	$exist_after = 1;
} #while $dir_1
close(NEW);

unless($exist_after){
	system("mkdir $before_dir"."$after");
} #unless

my @aray;

opendir(BEFORE,$before_dir.$before)or die "$!";
while(my $dir_before = readdir(BEFORE)){
	next unless($dir_before =~ /TABAITAI.*\.xlsx?/);
	push(@aray,$dir_before);
} #while $dir_before
close(BEFORE);

my @list;
my %debug;
opendir(AFTER,$after_dir.$before)or die "$!";
while(my $dir_after = readdir(AFTER)){
	next unless($dir_after =~ /TABAITAI.*\.csv/);
	for(my $i=0;$i<@aray;$i++){
	my $excel;
	my $csv;
	unless(defined($list[$i]->[0])){$list[$i]->[0] = $aray[$i]};
	unless(defined($list[$i]->[1])){$list[$i]->[1] = '0'};
	unless(defined($csv)){$csv = 'undef'};
	unless(defined($excel)){$excel = 'undef'};
	
	$debug{$list[$i]->[0]} = 0;
	$debug{$dir_after} = 1;

		if($list[$i]->[0] =~ /(TABAITAI__.*_[0-9]{1,}_[0-9]{1,}_[0-9]{1,}_[0-9]{1,})/){
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
			$list[$i]->[1] = '1';
		} #if
	} #for
} #while $dir_before
close(BEFORE);

my $border = '-' x 100;
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
























