# we want to create a pdf
$pdf_mode = 1;
# 
$cleanup_mode = 2;

$pdflatex = 'pdflatex --shell-escape %O %S';

# put the aux files in a separate directory
$out_dir = ".build"
