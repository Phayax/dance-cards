from pathlib import Path
from pprint import pprint

import PyPDF2


TARGET_FOLDER = "../single"


def arrange_pdfs_for_nupping():
    pass


def create_latex_nup_file():
    pass


def create_empty_latex_file():
    pass

if __name__ == '__main__':
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
