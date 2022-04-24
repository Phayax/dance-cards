import subprocess
import shutil
from pathlib import Path
from multiprocessing import Pool

from tqdm import tqdm

#from dances import DANCES

PATCH = "% CONTENT HERE"

BASE_TEX_FILE = "./cards.tex"

TEMP_DIR = "./build-single-temp/"


def sanitize_filenames(name):
    name = name.replace("\\", "")
    name = name.replace("/", "")
    name = name.replace("\"", "")
    name = name.replace("'", "")
    name = name.replace(r"{", "")
    name = name.replace(r"}", "")

    name = name.replace(" ", "_")

    # TODO: implement scanning for scriptsize and such
    return name


def extract_filename(dance):
    ret = dance.find(r"\dancename")
    if ret > 0:
        start = dance.find(r"{", ret) + 1
        end = dance.find(r"}", ret)
        raw_name = dance[start:end]
        name = sanitize_filenames(raw_name)
        return name + ".tex"
    else:
        raise ValueError("No dancename found in: \n" + dance)


def patch_tex_content(base_tex_file, target_tex_file, content):
    with open(base_tex_file, "r") as f:
        file_content = f.readlines()
        file_content = [line for line in file_content if not line.strip().startswith("%")]
    # join the lines (keeping newlines)
    file_content = "".join(file_content)

    ret = file_content.find(PATCH)
    print(ret, file_content[ret-20:ret+20])
    file_content = file_content[:ret] + content + file_content[ret + len(PATCH):]

    file_content = file_content
    # the encoding here is important because windows is annoying
    with open(target_tex_file, "w", encoding="utf-8") as f:
        f.write(file_content)


def split_file(base_tex_file: Path, target_file_path: Path):
    with open(base_tex_file, "r") as f:
        file_content = f.readlines()
    # join the lines (keeping newlines)
    file_content = "".join(file_content)

    header, content = file_content.split(r"\begin{document}")
    header += r"\begin{document}"
    dance_content, end = file_content.split(r"\end{document}")
    end = "\n" + r"\end{document}" + end
    dances = dance_content.split(r"\newpage")

    for dance in dances:
        name = extract_filename(dance)
        dance_file = target_file_path / name
        with open(dance_file, "w") as f:
            dance_text = header + dance + end
            f.write(dance_text)


def compile_dance(filename, working_dir):
    ret = subprocess.run(["latexmk", filename], cwd=working_dir)
    return ret

if __name__ == '__main__':
    if Path(TEMP_DIR).exists():
        shutil.rmtree(Path(TEMP_DIR))


    # create build directory
    p = Path(TEMP_DIR)
    p.mkdir(exist_ok=False)
    shutil.copy(".latexmkrc", str(p / ".latexmkrc"))
    shutil.copytree(Path("./img"), p / "img")
    split_file(Path(BASE_TEX_FILE), p)

    #for dance in DANCES:

        #target_tex_path = p / f"{dance['name']}.tex"
        #target_pdf_name = f"{dance['name'].pdf}"
        #patch_tex_content(BASE_TEX_FILE, target_tex_path, dance['tex-content'])


    # see if we can just call latexmk on the whole directory so it compiles everything in it
    #ret = subprocess.run(["latexmk"], cwd=p)
    #print(f"Return Code: {ret.returncode}")
    dance_list = [file for file in p.iterdir() if file.is_file and file.suffix == ".tex"]
    pool = Pool()
    joblist = []
    for file in dance_list:
        pool.apply_async(compile_dance, )


    dance_list = [file for file in p.iterdir() if file.is_file and file.suffix == ".tex"]
    for file in (pbar := tqdm(sorted(dance_list))):


        pbar.set_postfix_str("%s" % file.name)
        ret = subprocess.run(["latexmk", file.name], cwd=p, capture_output=True)
        #print(f"Return Code: {ret.returncode}")


    # once we're done remove all files from build dir
    #for file in p.iterdir():
    #    file.unlink()
