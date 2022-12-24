import argparse
import itertools
from pathlib import Path
from typing import Literal, Dict, List, Iterable, Sequence

import PyPDF2

TARGET_FOLDER = "../single"

NO_PAGE: int = -1


def chunker(seq: Sequence, size: int) -> Iterable:
    """
    Returns an iterator that goes over a list in chunks of size <size>.
    From: https://stackoverflow.com/a/434328
    :param seq: A Sequence (e.g. list, tuple) that will be split into chunks
    :param size: Number of elements per chunk
    :return: An Iterable that contains the chunks
    """
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def invert_list_dict(input_dict: Dict[int, List[Path]]) -> Dict[Path, int]:
    """
    Inverts a dictionary of the Type:
        {
            Hashable: [
                Hashable,
                Hashable,
                ...
                Hashable
            ],
        }
    All Items in the List will have the key as their value.
    :param input_dict:
    :return:
    """
    inv_dict = {}
    for key, values in input_dict.items():
        for value in values:
            inv_dict.update({value: key})
    # sort the dictionary
    inv_dict = dict(sorted(inv_dict.items()))
    return inv_dict


def convert_page_numbers_to_indices(page_no_dict: Dict[int, List[Path]]) -> Dict[Path, List[int]]:
    inv_dict = invert_list_dict(page_no_dict)
    counting_index = 1
    for key, value in inv_dict.items():
        # FIXME: check if it is fine that we change the type here from int to List[int]:
        inv_dict[key] = list(range(counting_index, counting_index + value))
        counting_index += value

    return inv_dict


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
        raise ValueError(f"Expected exactly one more page in the full pdf, but got {full_pdf_length - total_page_count}\
         more pages.\n\tFull pdf: {full_pdf_length},\n\tCumulative Single Page Count: {total_page_count}.")
    return length_dict


class NupTexDocument:
    NUP_HEAD_CODE = r"""\documentclass[12pt,a4paper,landscape]{scrartcl}
    \usepackage[a4paper]{geometry}
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

    def __init__(self, dance_dict: Dict[int, List[Path]], nup_pdf_source: Path):
        self.dance_dict = dance_dict
        self.source_pdf_path = nup_pdf_source

        self.empty_page_idx = self.get_last_page_idx(nup_pdf_source)

    @classmethod
    def get_last_page_idx(cls, pdf_path: Path) -> int:
        reader = PyPDF2.PdfFileReader(str(pdf_path))
        return reader.numPages

    @classmethod
    def split_into_front_back_pairs(cls, dance_idxs: List[int]) -> List[List[int]]:
        num_pages = len(dance_idxs)
        # make page count even
        if num_pages % 2 == 1:
            dance_idxs.append(NO_PAGE)
            num_pages += 1

        pages = []
        for idx in range(int(num_pages / 2)):
            pages.append([dance_idxs[idx], dance_idxs[idx+int(num_pages / 2)]])

        return pages

    def layout_dances(self, output_file: Path, dance_list: List[Path], fold_edge, nup_factor: int):
        # TODO: proper type for fold_edge, pull out to
        #       separate type def since it's used twice.
        page_list = []
        # create working copy of dance_dict with only the selected dances
        sel_dance_dict = self.copy_dict_and_drop_unlisted(self.dance_dict, dance_list)
        # we want to process dances from large to small
        # TODO: refactoring and cleanup
        sel_dance_dict = dict(reversed(sorted(sel_dance_dict.items())))
        all_dance_dict = dict(reversed(sorted(self.dance_dict.items())))
        # now let's iterate over the dances

        dance_idx_dict = convert_page_numbers_to_indices(all_dance_dict)

        for page_count, dances in sel_dance_dict.items():
            for dance in dances:
                split_pages = self.split_into_front_back_pairs(dance_idx_dict[dance])
                page_list.extend(split_pages)

        with open(output_file, "w") as out_file:
            out_file.write(self.NUP_HEAD_CODE)

            for chunk in chunker(page_list, int(nup_factor ** 2)):
                page = NupPage(fold_edge=fold_edge, nup_factor=nup_factor)
                for pair in chunk:
                    page.add_single_front_back(pair)
                page.replace_none_pages(self.empty_page_idx)
                out_file.write(page.get_tex_code(self.source_pdf_path))
            out_file.write(self.NUP_FOOT_CODE)

    @classmethod
    def copy_dict_and_drop_unlisted(cls, input_dict: Dict[int, List[Path]], target_list: List[Path]) -> Dict[int, List[Path]]:
        # TODO: create a class for dance_dict
        #       it is such an unwieldy data structure that it probably should be encapsulated in a class
        working_dict = input_dict.copy()
        for key, values in working_dict.items():
            # keep only the dances that also occur in the target_list
            # FIXME: the use of sets currently doesn't allow for the layouting
            #        of the same dance twice! fix this if necessary.
            new_values = list(set(values) & (set(target_list)))
            working_dict[key] = new_values
        return working_dict


class NupPage:

    NUP_TEX_START = r"\includepdf[pages={"
    # double braces (<{{> and <}}>) here for when it is actually tex code,
    # to make it work with python string formatting (the second brace is the escape sequence)
    NUP_TEX_END = "}}, frame=true, nup={nup_factor}x{nup_factor}, angle={angle}]{{{pdfpath}}}\n"

    def __init__(self, fold_edge: Literal['long', 'short'], nup_factor: int = 2):
        self.nup_factor = nup_factor
        self.fold_edge = fold_edge

        self.slots_front: List[int] = [NO_PAGE] * int(nup_factor ** 2)
        self.slots_back: List[int] = [NO_PAGE] * int(nup_factor ** 2)
        self.next_free_slot: int = 0

    def __len__(self) -> int:
        return int(self.nup_factor ** 2)

    def add_single_front_back(self, fb_pair: List[int]):
        self.slots_front[self.next_free_slot] = fb_pair[0]
        self.slots_back[self.next_free_slot] = fb_pair[1]
        self.next_free_slot += 1

    def replace_none_pages(self, empty_page_idx: int) -> None:
        """
        Replaces all nones in slots with the empty page index given.
        :param empty_page_idx:
        :return:
        """
        for idx in range(len(self.slots_front)):
            if self.slots_front[idx] == NO_PAGE:
                self.slots_front[idx] = empty_page_idx

        for idx in range(len(self.slots_back)):
            if self.slots_back[idx] == NO_PAGE:
                self.slots_back[idx] = empty_page_idx

    def get_arranged_back_numbers(self):
        arranged_numbers = []
        if self.fold_edge == "short":
            # Goal: Flip the indices horizontally:
            #   1  2  3     ->    3  2  1
            #   4  5  6     ->    6  5  4
            #   7  8  9     ->    9  8  7
            #
            #   1  2  3  4  ->  4  3  2  1
            #   5  6  7  8  ->  8  7  6  5
            #   9 10 11 12  -> 12 11 10  9
            #  13 14 15 16  -> 16 15 14 13

            # iterate over lines:
            for chunk in chunker(self.slots_back, self.nup_factor):
                # flip each line
                arranged_numbers.extend(reversed(chunk))
        else:
            # Goal: Flip the indices vertically:
            # Also: the pages need to be flipped by 180° degrees
            #   1  2  3     ->    7  8  9
            #   4  5  6     ->    4  5  6
            #   7  8  9     ->    1  2  3
            #
            #   1  2  3  4  -> 13 14 15 16
            #   5  6  7  8  ->  9 10 11 12
            #   9 10 11 12  ->  5  6  7  8
            #  13 14 15 16  ->  1  2  3  4
            for chunk in chunker(self.slots_back, self.nup_factor):
                arranged_numbers = chunk + arranged_numbers

        return arranged_numbers

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
        tex_str += self.NUP_TEX_END.format(nup_factor=self.nup_factor, angle=0, pdfpath=str(pdf_path.as_posix()))
        tex_str += self.NUP_TEX_START
        tex_str += ", ".join([str(x) for x in self.get_arranged_back_numbers()])
        # apply angle here because the back side needs to be in the same format as the front
        tex_str += self.NUP_TEX_END.format(nup_factor=self.nup_factor, angle=angle, pdfpath=str(pdf_path.as_posix()))
        return tex_str


def create_nup_tex_from_pdfs(
        single_pdf_path: Path,
        full_pdf_path: Path,
        nup_factor: int,
        output_path: Path,
        fold_edge: str) -> None:
    dance_dict = get_page_indices(single_pdf_path=single_pdf_path, full_pdf_path=full_pdf_path)
    ntc = NupTexDocument(dance_dict=dance_dict, nup_pdf_source=full_pdf_path)
    flat_dance_list = list(dance_dict.values())
    # flatten code from: https://stackoverflow.com/a/953097
    flat_dance_list = list(itertools.chain.from_iterable(flat_dance_list))
    flat_dance_list.sort()

    #p = Path("multipage-tool/")
    #p.mkdir(exist_ok=True, parents=False)
    Path(output_path.parent).mkdir(exist_ok=True, parents=False)
    ntc.layout_dances(output_file=output_path, dance_list=flat_dance_list, fold_edge=fold_edge,
                      nup_factor=nup_factor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--single_pdfs", type=Path, help="the path to the directory of all split-pdfs", required=True)
    parser.add_argument("--full_pdf", type=Path, help="the path to the full pdf with all dances", required=True)
    parser.add_argument("--nup_factor", type=int, help="How many rows and columns should there be on one a4 page.", required=True)
    parser.add_argument("--fold_edge", type=str, help="Either 'short' or 'long' depending on which edge you want to fold the pages for double sided printing.")
    parser.add_argument("--output_tex", type=Path, help="path to where the output tex file should be created.", required=True)
    args = parser.parse_args()

    # dance_dict = get_page_indices(single_pdf_path=SINGLE_PATH, full_pdf_path=FULL_PATH)
    # ntc = NupTexDocument(dance_dict=dance_dict, nup_pdf_source=FULL_PATH)
    # flat_dance_list = list(dance_dict.values())
    # # flatten code from: https://stackoverflow.com/a/953097
    # flat_dance_list = list(itertools.chain.from_iterable(flat_dance_list))
    # flat_dance_list.sort()
    #
    # p = Path("./")
    # p.mkdir(exist_ok=True, parents=False)

    out_path = Path(args.output_tex)#.resolve()
    single_path = Path(args.single_pdfs)#.resolve()
    full_path = Path(args.full_pdf)#.resolve()
    # TODO: make a check that ensures that the full file is correctly placed relative to the output file!

    create_nup_tex_from_pdfs(
        single_pdf_path=single_path,
        full_pdf_path=full_path,
        nup_factor=args.nup_factor,
        output_path=out_path,
        fold_edge=args.fold_edge
    )