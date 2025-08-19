"""util format"""

import math
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from urllib.parse import parse_qs, urlparse


@dataclass
class Link:
    """Telegram Link"""

    group_id: Union[str, int, None] = None
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    topic_id: Optional[int] = None


def format_byte(size: float, dot=2):
    """format byte"""

    # pylint: disable = R0912
    if 0 <= size < 1:
        human_size = str(round(size / 0.125, dot)) + "b"
    elif 1 <= size < 1024:
        human_size = str(round(size, dot)) + "B"
    elif math.pow(1024, 1) <= size < math.pow(1024, 2):
        human_size = str(round(size / math.pow(1024, 1), dot)) + "KB"
    elif math.pow(1024, 2) <= size < math.pow(1024, 3):
        human_size = str(round(size / math.pow(1024, 2), dot)) + "MB"
    elif math.pow(1024, 3) <= size < math.pow(1024, 4):
        human_size = str(round(size / math.pow(1024, 3), dot)) + "GB"
    elif math.pow(1024, 4) <= size < math.pow(1024, 5):
        human_size = str(round(size / math.pow(1024, 4), dot)) + "TB"
    elif math.pow(1024, 5) <= size < math.pow(1024, 6):
        human_size = str(round(size / math.pow(1024, 5), dot)) + "PB"
    elif math.pow(1024, 6) <= size < math.pow(1024, 7):
        human_size = str(round(size / math.pow(1024, 6), dot)) + "EB"
    elif math.pow(1024, 7) <= size < math.pow(1024, 8):
        human_size = str(round(size / math.pow(1024, 7), dot)) + "ZB"
    elif math.pow(1024, 8) <= size < math.pow(1024, 9):
        human_size = str(round(size / math.pow(1024, 8), dot)) + "YB"
    elif math.pow(1024, 9) <= size < math.pow(1024, 10):
        human_size = str(round(size / math.pow(1024, 9), dot)) + "BB"
    elif math.pow(1024, 10) <= size < math.pow(1024, 11):
        human_size = str(round(size / math.pow(1024, 10), dot)) + "NB"
    elif math.pow(1024, 11) <= size < math.pow(1024, 12):
        human_size = str(round(size / math.pow(1024, 11), dot)) + "DB"
    elif math.pow(1024, 12) <= size:
        human_size = str(round(size / math.pow(1024, 12), dot)) + "CB"
    else:
        raise ValueError(
            f'format_byte() takes number than or equal to 0, " \
            " but less than 0 given. {size}'
        )
    return human_size


class SearchDateTimeResult:
    """search result for datetime"""

    def __init__(
        self,
        value: str = "",
        right_str: str = "",
        left_str: str = "",
        match: bool = False,
    ):
        self.value = value
        self.right_str = right_str
        self.left_str = left_str
        self.match = match


def get_date_time(text: str, fmt: str) -> SearchDateTimeResult:
    """Get first of date time,and split two part

    Parameters
    ----------
    text: str
        ready to search text

    Returns
    -------
    SearchDateTimeResult

    """
    res = SearchDateTimeResult()
    search_text = re.sub(r"\s+", " ", text)
    regex_list = [
        # 2013.8.15 22:46:21
        r"\d{4}[-/\.]{1}\d{1,2}[-/\.]{1}\d{1,2}[ ]{1,}\d{1,2}:\d{1,2}:\d{1,2}",
        # "2013.8.15 22:46"
        r"\d{4}[-/\.]{1}\d{1,2}[-/\.]{1}\d{1,2}[ ]{1,}\d{1,2}:\d{1,2}",
        # "2014.5.11"
        r"\d{4}[-/\.]{1}\d{1,2}[-/\.]{1}\d{1,2}",
        # "2014.5"
        r"\d{4}[-/\.]{1}\d{1,2}",
    ]

    format_list = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m",
    ]

    for i, value in enumerate(regex_list):
        search_res = re.search(value, search_text)
        if search_res:
            time_str = search_res.group(0)
            try:
                res.value = datetime.strptime(
                    time_str.replace("/", "-").replace(".", "-").strip(), format_list[i]
                ).strftime(fmt)
            except Exception:
                break
            if search_res.start() != 0:
                res.left_str = search_text[0 : search_res.start()]
            if search_res.end() + 1 <= len(search_text):
                res.right_str = search_text[search_res.end() :]
            res.match = True
            return res

    return res


def replace_date_time(text: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Replace text all datetime to the right fmt

    Parameters
    ----------
    text: str
        ready to search text

    fmt: str
        the right datetime format

    Returns
    -------
    str
        The right format datetime str

    """

    if not text:
        return text
    res_str = ""
    res = get_date_time(text, fmt)
    if not res.match:
        return text
    if res.left_str:
        res_str += replace_date_time(res.left_str)
    res_str += res.value
    if res.right_str:
        res_str += replace_date_time(res.right_str)

    return res_str


_BYTE_UNIT = ["B", "KB", "MB", "GB", "TB"]


def get_byte_from_str(byte_str: str) -> Optional[int]:
    """Get byte from str

    Parameters
    ----------
    byte_str: str
        Include byte str

    Returns
    -------
    int
        Byte
    """
    search_res = re.match(r"(\d{1,})(B|KB|MB|GB|TB)", byte_str)
    if search_res:
        unit_str = search_res.group(2)
        unit: int = 1
        for it in _BYTE_UNIT:
            if it == unit_str:
                break
            unit *= 1024

        return int(search_res.group(1)) * unit

    return None


def truncate_filename(path: str, limit: int = 230) -> str:
    """Truncate filename to the max len.

    Parameters
    ----------
    path: str
        File name path

    limit: int
        limit file name len(utf-8 byte)

    Returns
    -------
    str
        if file name len more than limit then return truncate filename or return filename

    """
    p, f = os.path.split(os.path.normpath(path))
    f, e = os.path.splitext(f)
    f_max = limit - len(e.encode("utf-8"))
    f = unicodedata.normalize("NFC", f)
    f_trunc = f.encode()[:f_max].decode("utf-8", errors="ignore")
    return os.path.join(p, f_trunc + e)


def extract_info_from_link(link: str) -> Link:
    """Extract info from link"""
    if link in ("me", "self"):
        return Link(group_id=link)

    try:
        u = urlparse(link)
        paths = [p for p in u.path.split("/") if p]
        query = parse_qs(u.query)
    except ValueError:
        return Link()

    result = Link()

    if "comment" in query:
        result.group_id = paths[0]
        result.comment_id = int(query["comment"][0])
    elif len(paths) == 1 and paths[0] != "c":
        result.group_id = paths[0]
    elif len(paths) == 2:
        if paths[0] == "c":
            result.group_id = int(f"-100{paths[1]}")
        else:
            result.group_id = paths[0]
            result.post_id = int(paths[1])
    elif len(paths) == 3:
        if paths[0] == "c":
            result.group_id = int(f"-100{paths[1]}")
            result.post_id = int(paths[2])
        else:
            result.group_id = paths[0]
            result.topic_id = int(paths[1])
            result.post_id = int(paths[2])
    elif len(paths) == 4 and paths[0] == "c":
        result.group_id = int(f"-100{paths[1]}")
        result.topic_id = int(paths[2])
        result.post_id = int(paths[3])

    return result


def validate_title(title: str) -> str:
    """Fix if title validation fails

    Parameters
    ----------
    title: str
        Chat title

    """

    r_str = r"[/\\:*?\"<>|\n]"  # '/ \ : * ? " < > |'
    new_title = re.sub(r_str, "_", title)
    return new_title


def validate_title_with_one_underline(title: str) -> str:
    """Fix if title validation fails and condense multiple underscores into one

    Parameters
    ----------
    title: str
        Chat title
    """
    # 定义不允许的字符正则表达式
    r_str = r"[/\\:*?\"<>|\n]"  # '/ \ : * ? " < > |'

    # 用下划线替换不允许的字符
    new_title = re.sub(r_str, "_", title)

    # 将多个连续的下划线替换为一个下划线
    new_title = re.sub(r"_+", "_", new_title)

    return new_title


def create_progress_bar(progress, total_bars=10):
    """
    example
    progress = 50
    progress_bar = create_progress_bar(progress)
    print(f'Progress: [{progress_bar}] ({progress}%)')
    """
    completed_bars = int(progress * total_bars / 100)
    remaining_bars = total_bars - completed_bars
    progress_bar = "█" * completed_bars + "░" * remaining_bars
    return progress_bar
