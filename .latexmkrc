# we want to create a pdf
$pdf_mode = 1;
# 
$cleanup_mode = 2;

# enabling shell escape because we use tikz
$pdflatex = 'pdflatex --shell-escape %O %S';

# put the aux files in a separate directory
$out_dir = ".build";

# set OS specific settings
if ($^O =~ /darwin/) {
	print "DIAGNOSTICS = Operating System Detected: Mac OSX\n";
} elsif ($^O =~ /MSWin32/) {
	print "DIAGNOSTICS = Operating System Detected: Windows\n";
} elsif ($^O =~ /linux/) {
	print "DIAGNOSTICS = Operating System Detected: Linux\n";
	$pdf_previewer = "start evince %O %S";
}
