import subprocess
import shutil
from pathlib import Path

from dances import DANCES

PATCH = "% CONTENT HERE"

BASE_TEX_FILE = "./cards.tex"


def sanitize_filenames():
    # TODO: implement me
    raise NotImplementedError()


def patch_tex_content(base_tex_file, target_tex_file, content):
    with open(base_tex_file, "r") as f:
        file_content = f.readlines()
    # join the lines (keeping newlines)
    file_content = "".join(file_content)

    ret = file_content.find(PATCH)
    print(ret, file_content[ret-20:ret+20])
    file_content = file_content[:ret] + content + file_content[ret + len(PATCH):]

    file_content = file_content
    # the encoding here is important because windows is annoying
    with open(target_tex_file, "w", encoding="utf-8") as f:
        f.write(file_content)



if __name__ == '__main__':
    if Path("./build-temp/").exists():
        shutil.rmtree(Path("./build-temp/"))


    # create build directory
    p = Path("./build-temp/")
    p.mkdir(exist_ok=False)
    shutil.copy(".latexmkrc", str(p / ".latexmkrc"))
    shutil.copytree(Path("./img"), p / "img")
    for dance in DANCES:
        target_tex_path = p / f"{dance['name']}.tex"
        #target_pdf_name = f"{dance['name'].pdf}"
        patch_tex_content(BASE_TEX_FILE, target_tex_path, dance['tex-content'])

    for file in p.iterdir():
        if file.is_file() and file.suffix == ".tex":
            print("compiling {file.name}...")
            ret = subprocess.run(["latexmk", file.name], cwd=p)
            print(f"Return Code: {ret.returncode}")


    # once we're done remove all files from build dir
    #for file in p.iterdir():
    #    file.unlink()
