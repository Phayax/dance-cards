from pathlib import Path
from pprint import pprint
from typing import Literal

import PyPDF2


TARGET_FOLDER = "../single"



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
    n = NupPage('long', 2)
    n.replace_none_pages(empty_page_idx=4)
    print(n.get_tex_code(Path("test.pdf")))
    exit()
    length_dict = {}
    p = Path(TARGET_FOLDER)
    for file in p.iterdir():
        if file.suffix != ".pdf":
            continue

        reader = PyPDF2.PdfFileReader(str(file))
        length = reader.numPages

        if length in length_dict.keys():
            length_dict[length].append(file)
        else:
            length_dict.update({length: [file]})

    pprint(length_dict, indent=4)
