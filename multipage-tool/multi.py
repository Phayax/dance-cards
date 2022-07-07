from pathlib import Path
from pprint import pprint
from typing import Literal

import PyPDF2


TARGET_FOLDER = "../single"


def get_page_indices(single_pdf_path: Path, full_pdf_path: Path):
    # get the lengths for all single_files:
    single_list = [file for file in single_pdf_path.iterdir() if file.suffix == ".pdf"]
    single_list.sort()
    length_dict = {}
    total_page_count = 0
    for file in single_list:
        reader = PyPDF2.PdfFileReader(str(file))
        length = reader.numPages
        total_page_count += length
        if length in length_dict.keys():
            length_dict[length].append(file)
        else:
            length_dict.update({length: [file]})


    full_pdf_length = PyPDF2.PdfFileReader(str(full_pdf_path)).numPages
    if not full_pdf_length == total_page_count + 1:
        raise ValueError(f"Expected exactly one more page in the full pdf, but got {full_pdf_length - total_page_count} more pages.\n\tFull pdf: {full_pdf_length},\n\tCumulative Single Page Count: {total_page_count}.")
    return length_dict


class NupTexDocument:
    NUP_HEAD_CODE = r"""\documentclass[12pt,a4paper,landscape]{scrartcl}
    \usepackage[a6paper]{geometry}
    \usepackage{pdfpages}
    \usepackage{xcolor}
    %\geometry{showframe}
    %\geometry{left=1.2cm,right=1.2cm,top=1.5cm,bottom=1.5cm}
    \pagestyle{empty}
    % Define very light gray color so as to be nearly invisible
    \definecolor{ultra-light-gray}{gray}{0.98}
    % since pdfpages uses fbox to draw the frames lets change the stroke color
    % to the desired value
    \renewcommand\fbox{\fcolorbox{ultra-light-gray}{white}}

    \begin{document}"""

    NUP_FOOT_CODE = r"""\end{document}
    """
    def __init__(self, dance_list, ):
        pass


class NupPage:

    NUP_TEX_START = r"\includepdf[pages={"
    # double braces (<{{> and <}}>) here for when it is actually tex code,
    # to make it work with python string formatting (the second brace is the escape sequence)
    NUP_TEX_END = "}}, frame=true, nup={nup_factor}x{nup_factor}, angle={angle}]{{{pdfpath}}}\n"

    def __init__(self, fold_edge: Literal['long', 'short'], nup_factor: int = 2):
        self.nup_factor = nup_factor
        self.fold_edge = fold_edge

        self.slots_front = [None] * int(nup_factor ** 2)
        self.slots_back = [None] * int(nup_factor ** 2)

    def __len__(self) -> int:
        return int(self.nup_factor ** 2)

    def replace_none_pages(self, empty_page_idx: int) -> None:
        """
        Replaces all nones in slots with the empty page index given.
        :param empty_page_idx:
        :return:
        """
        for idx in range(len(self.slots_front)):
            if self.slots_front[idx] is None:
                self.slots_front[idx] = empty_page_idx

        for idx in range(len(self.slots_back)):
            if self.slots_back[idx] is None:
                self.slots_back[idx] = empty_page_idx

    def get_tex_code(self, pdf_path: Path) -> str:
        """
        This method outputs pdfpages code to plot on front and one back of a page.
        :param pdf_path: path to the pdf file from which to take pages
        :return:
        """
        angle = 0 if self.fold_edge == 'short' else 180
        tex_str = ""
        tex_str += self.NUP_TEX_START
        tex_str += ", ".join([str(x) for x in self.slots_front])
        # We have an angle of 0 here (normal orientation):
        tex_str += self.NUP_TEX_END.format(nup_factor=self.nup_factor, angle=0, pdfpath=str(pdf_path.resolve()))
        tex_str += self.NUP_TEX_START
        tex_str += ", ".join([str(x) for x in self.slots_back])
        # apply angle here because the back side needs to be in the same format as the front
        tex_str += self.NUP_TEX_END.format(nup_factor=self.nup_factor, angle=angle, pdfpath=str(pdf_path.resolve()))
        return tex_str

if __name__ == '__main__':
    #n = NupPage('long', 2)
    #n.replace_none_pages(empty_page_idx=4)
    #print(n.get_tex_code(Path("test.pdf")))
    #exit()

    SINGLE_PATH = Path("../dev-debug/single")
    FULL_PATH = Path("../dev-debug/Tanzkarten.pdf")

    l = get_page_indices(single_pdf_path=SINGLE_PATH, full_pdf_path=FULL_PATH)
    pprint(l, indent=4)