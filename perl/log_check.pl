#!/usr/bin/perl
use strict;
use warnings;

my $dir = $ARGV[0];

open(FIND,'>./mda_log.log')or die "$!";
	system("find ./$dir -name \"mda_check_cnt.log\" > ./mda_log.log");
close(FIND);

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














