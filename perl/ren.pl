#!/usr/bin/perl
my $dirname = $ARGV[0];
$dirname = './'.$dirname;
opendir(DIR,$dirname)or die "$!";
while(my $file = readdir(DIR)){
	next unless($file =~ /\.(xlsx?|csv)/);
	my $ren = $file;
	$ren =~ s/[ \[\]\(\)\{\}]//g;
	print "mv \"$dirname/$file\" \"$dirname/TABAITAI__$ren\"\n";
	system("mv \"$dirname/$file\" \"$dirname/TABAITAI__$ren\"");
} #while $file
close(DIR);
