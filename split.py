import subprocess
import shutil
from pathlib import Path
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

#from tqdm import tqdm

#from dances import DANCES
from tqdm import tqdm

#PATCH = "% CONTENT HERE"

BASE_TEX_FILE = "./cards.tex"

TEMP_DIR = "./split/"


def sanitize_filenames(name):
    name = name.replace("\\", "")
    name = name.replace("/", "")
    name = name.replace("\"", "")
    name = name.replace("'", "")
    name = name.replace(r"{", "")
    name = name.replace(r"}", "")

    name = name.replace(" ", "_")

    name = name.replace("normalsize", "")
    name = name.replace("scriptsize", "")
    name = name.replace("nicefrac", "")

    return name


def dance_contains_tex_code(content: str) -> bool:
    # check if it is the last empty page:
    # in that case return false
    if r"\ClearShipoutPictureBG" in content:
        return False

    lines = content.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if not line.startswith("%")]
    lines = [line for line in lines if line != ""]

    if len(lines) > 0:
        return True
    else:
        return False


def extract_filename(dance):
    # remove leading and trailing whitespaces so we can easily search
    # for the first line break
    dance = dance.strip("\n")

    ret = dance.find(r"\dancename")
    if ret >= 0:
        # searching for the open bracket of \dancename>{<
        start = dance.find(r"{", ret) + 1
        # searching for the end of the line
        end = dance.find("\n", ret)
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
    with open(base_tex_file, "r", encoding="utf-8") as f:
        file_content = f.readlines()
        file_content = [line for line in file_content if not line.strip().startswith(r"%")]
        # ignore lines that specify the compilespeed option 
        # \fastrue or \fastfalse
        file_content = [line for line in file_content if not line.strip().startswith(r"\fast")]
    # join the lines (keeping newlines)
    file_content = "".join(file_content)

    header, content = file_content.split(r"\begin{document}")
    header += r"\begin{document}"
    dance_content, end = content.split(r"\end{document}")
    end = "\n" + r"\end{document}" + end
    dances = dance_content.split(r"\newpage")

    for idx, dance in enumerate(dances):
        # first check if there is content once all spaces and comments are removed:
        if not dance_contains_tex_code(dance):
            continue
        name = extract_filename(dance)
        # add an index so we know in which order they appear in the main document.
        dance_file = target_file_path / f"{idx:03d}_{name}"
        with open(dance_file, "w", encoding="utf-8") as f:
            dance_text = header + dance + end
            f.write(dance_text)
        print(f"\t{dance_file.name}")


def compile_dance(file: Path):
    working_dir = file.parent
    try:
        subprocess.run(['tectonic', file.name],
                       cwd=working_dir,
                       check=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        return (file, True, "")
    except subprocess.CalledProcessError as e:
        return (file, False, e.stderr.decode())

def compile_dances_parallel(target_path: Path):
    dance_files = [file for file in sorted(target_path.iterdir()) if file.is_file and file.suffix == ".tex"]

    max_workers = cpu_count()

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(compile_dance, dance_files)
        for result in tqdm(futures, total=len(dance_files), desc="Compiling .tex files"):
            results.append(result)

    # Optionally print failed files
    failed = [r for r in results if not r[1]]
    if failed:
        print("\n⚠️ Some files failed to compile:")
        for f in failed:
            print(f"- {f[0]}:\n{f[2]}")

    # with Pool() as pool:
    #     pool.map(compile_dance, dance_list)
    #     joblist = []
    #     for file in dance_list:
    #         joblist.append(pool.apply_async(compile_dance, file))
        
    #     for job in tqdm(joblist):
    #         # wait for the job to finish
    #         job.wait()

def compile_dance_serial():
    dance_list = [file for file in p.iterdir() if file.is_file and file.suffix == ".tex"]
    for file in (pbar := tqdm(sorted(dance_list))):

        pbar.set_postfix_str("%s" % file.name)
        ret = subprocess.run(["latexmk", file.name], cwd=p, capture_output=True)
        if ret.returncode == 0:
            pdf_path = p / ".build" / f"{file.stem}.pdf"
            shutil.copy(pdf_path, TEMP_DIR / pdf_path.name)
        else:
            print(f"Warning latexmk returned with non-zero Returncode {ret.returncode} on file {file}!")

    # once we're done remove all files from build dir
    #for file in p.iterdir():
    #    file.unlink()

if __name__ == '__main__':
    # remove potential old build data
    if Path(TEMP_DIR).exists():
        pass
        shutil.rmtree(Path(TEMP_DIR))

    print("="*60)
    print("Splitting tex file.")
    print("Generated files:")
    print("-"*30)
    # create build directory
    p = Path(TEMP_DIR)
    p.mkdir(exist_ok=False)
    #shutil.copy(".latexmkrc", str(p / ".latexmkrc"))
    shutil.copytree(Path("./img"), p / "img")
    split_file(base_tex_file=Path(BASE_TEX_FILE), target_file_path=p)
    #compile_dance(
    #    list(sorted(p.glob("*.tex")))[0]
    #)
    compile_dances_parallel(target_path=p)
    #single_pdf_target = Path("./single/")
    #single_pdf_target.mkdir(exist_ok=True, parents=False)

    print("="*60)
    # then call latexmk on build-single-temp
