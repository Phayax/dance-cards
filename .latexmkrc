# we want to create a pdf
$pdf_mode = 1;
# cleanup except .dvi, .ps and .pdf files
$cleanup_mode = 2;

# enabling shell escape because we use tikz
$pdflatex = 'pdflatex --shell-escape %O %S';

# put the aux files in a separate directory
$out_dir = ".build";

# set OS specific settings
if ($^O =~ /darwin/) {
	print "DIAGNOSTICS = Operating System Detected: Mac OSX\n";
} elsif ($^O =~ /MSWin32/) {
	#print "DIAGNOSTICS = Operating System Detected: Windows\n";
	# copy pdf from build directory to .tex file directory
	$success_cmd = "copy %D %R.pdf;";
} elsif ($^O =~ /linux/) {
	print "DIAGNOSTICS = Operating System Detected: Linux\n";
	# copy pdf from build directory to .tex file directory
	$success_cmd = "cp %D %R.pdf";
	# set the default pdf viewer for linux (ubuntu)
	$pdf_previewer = "start evince %O %S";
}

# examples from https://github.com/nasa/nasa-latex-docs/blob/master/support/latexmk/latexmkrc
#$success_cmd = "python $ENV{'BUILDPDF_PATH'} '$ENV{'INPUT_SOURCE_PATH'}' --latexmk-passthrough-success -o '$ENV{'OUTPUT_PDF_NAME'}'";
#$compiling_cmd = "";
#$failure_cmd = "python $ENV{'BUILDPDF_PATH'} '$ENV{'INPUT_SOURCE_PATH'}' --latexmk-passthrough-fail";
