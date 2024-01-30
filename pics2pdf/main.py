import sys
from fpdf import FPDF
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

usage = """
使用方式：
pics2pdf 压缩包/文件夹路径 [-o <输出文件名>]
输出文件名默认为文件夹名或压缩包名
"""


def build_from_dir(pdf: FPDF, dir: Path):
    pic_paths = []
    for pic in dir.iterdir():
        pic_paths.append(pic.name)
    pic_paths.sort()
    for pic_path in pic_paths:
        pdf.add_page()
        pdf.image(str(dir) + '/' + pic_path, 0, 0, 210, 297)


if __name__ == '__main__':
    pdf = FPDF()
    pics = Path(sys.argv[1])
    if Path.is_dir(pics):
        build_from_dir(pdf, pics)
        pdf.output(pics.name + ".pdf", "F")
    elif ".zip" in pics.suffixes:
        zp = ZipFile(pics)
        with TemporaryDirectory() as tempdir:
            zp.extractall(tempdir)
            build_from_dir(pdf, Path(tempdir))
            pdf.output(pics.stem + ".pdf", "F")
    else:
        print(usage)
