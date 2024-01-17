import sys
from typing import Tuple, Optional
from pypdf import PdfWriter


class TocItem:
    def __init__(self, level: int, page: int, content: str):
        self.level = level
        self.page = page
        self.content = content
        self.sublist = []

    def __repr__(self):
        return f"{self.page} {self.content}"

    def add_sub(self, item):
        if item.level != self.level + 1:
            raise RuntimeError(f"expect level {self.level + 1}, but get {item.level}")
        self.sublist.append(item)


class TocCreator:
    toc_list = []
    toc_cursor = 0

    @staticmethod
    def space_cnt_to_level(space_cnt: int) -> int:
        if space_cnt % 4 != 0:
            raise RuntimeError(f"bad indent, get {space_cnt} space")
        return space_cnt // 4 + 1

    # leading space, page number, item name
    @staticmethod
    def split_toc_item(toc_item: str) -> Tuple[int, int, str]:
        space_cnt = 0
        for idx, c in enumerate(toc_item):
            if c == ' ':
                space_cnt += 1
            else:
                break
        name_start = -1
        page = 0
        for idx, c in enumerate(toc_item[space_cnt:]):
            if c == ' ':
                page = int(toc_item[space_cnt:space_cnt + idx])
                name_start = space_cnt + idx + 1
                break

        return space_cnt, page, toc_item[name_start:]

    def __init__(self, toc_file):
        toc = open(toc_file, "r")
        for line in toc.readlines():
            leading_space_cnt, page_num, name = TocCreator.split_toc_item(line.rstrip())
            toc_item = TocItem(TocCreator.space_cnt_to_level(leading_space_cnt), page_num, name)
            self.toc_list.append(toc_item)

    def peek_toc_item(self) -> Optional[TocItem]:
        if self.toc_cursor < len(self.toc_list):
            return self.toc_list[self.toc_cursor]
        return None

    def get_next_toc_item(self) -> Optional[TocItem]:
        if self.toc_cursor < len(self.toc_list):
            toc_item = self.toc_list[self.toc_cursor]
            self.toc_cursor += 1
            return toc_item
        return None

    def build_toc_tree(self, parent):
        next_toc_item = self.peek_toc_item()
        while next_toc_item:
            if not next_toc_item:
                return
            if parent.level + 1 == next_toc_item.level:
                parent.add_sub(self.get_next_toc_item())
            elif len(parent.sublist) > 0 and parent.sublist[-1].level + 1 == next_toc_item.level:
                self.build_toc_tree(parent.sublist[-1])
            elif next_toc_item.level <= parent.level:
                return
            else:
                raise RuntimeError("bad level")
            next_toc_item = self.peek_toc_item()

    # get toc root, its level = 0
    def create_toc(self) -> TocItem:
        root = TocItem(0, 0, "")
        self.build_toc_tree(root)
        return root


def install_toc(pdf_path: str, toc_root: TocItem):
    pdf_writer = PdfWriter(clone_from=pdf_path)
    pdf_writer.get_outline_root().empty_tree()

    def inner(toc_item: TocItem, parent):
        for toc_item in toc_item.sublist:
            # TODO -- add flag to clear existing toc
            new_parent = pdf_writer.add_outline_item(toc_item.content, toc_item.page - 1, parent)
            if len(toc_item.sublist) > 0:
                inner(toc_item, new_parent)

    inner(toc_root, None)
    pdf_writer.write(f"{pdf_path}.toc")


if __name__ == '__main__':
    toc_root = TocCreator(sys.argv[1]).create_toc()
    pdf_path = sys.argv[2]
    install_toc(pdf_path, toc_root)
