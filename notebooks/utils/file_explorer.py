"""Warehouse 디렉토리 탐색 유틸리티."""

import os


def show_tree(path, prefix="", max_depth=5, _depth=0):
    """디렉토리 트리를 파일 크기와 함께 출력한다.

    Usage::

        from utils.file_explorer import show_tree
        show_tree("/home/jovyan/data/warehouse/lab/my_table")
    """
    if _depth >= max_depth:
        return

    try:
        items = sorted(
            item for item in os.listdir(path) if not item.startswith(".")
        )
    except PermissionError:
        return

    for i, item in enumerate(items):
        item_path = os.path.join(path, item)
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "

        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            if size >= 1024 * 1024:
                size_str = f"{size / 1024 / 1024:.1f} MB"
            elif size >= 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size} B"
            print(f"{prefix}{connector}{item}  ({size_str})")
        else:
            print(f"{prefix}{connector}{item}/")
            next_prefix = prefix + ("    " if is_last else "│   ")
            show_tree(item_path, next_prefix, max_depth, _depth + 1)


def snapshot_tree(path):
    """디렉토리의 파일 목록과 크기를 dict로 반환한다 (diff용).

    Returns
    -------
    dict[str, int]
        상대 경로 → 파일 크기(bytes) 매핑.
    """
    result = {}
    for root, _dirs, files in os.walk(path):
        for fname in files:
            if fname.startswith("."):
                continue
            full = os.path.join(root, fname)
            rel = os.path.relpath(full, path)
            result[rel] = os.path.getsize(full)
    return result


def diff_tree(before, after):
    """두 snapshot_tree 결과를 비교하여 추가/삭제/변경된 파일을 출력한다.

    Usage::

        from utils.file_explorer import snapshot_tree, diff_tree

        before = snapshot_tree(table_path)
        # ... 어떤 작업 수행 ...
        after = snapshot_tree(table_path)
        diff_tree(before, after)
    """
    before_keys = set(before.keys())
    after_keys = set(after.keys())

    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    common = sorted(before_keys & after_keys)

    changed = [k for k in common if before[k] != after[k]]

    if not added and not removed and not changed:
        print("(변화 없음)")
        return

    if added:
        print(f"\n[+] 추가된 파일 ({len(added)}개):")
        for f in added:
            size = after[f]
            print(f"    + {f}  ({_fmt_size(size)})")

    if removed:
        print(f"\n[-] 삭제된 파일 ({len(removed)}개):")
        for f in removed:
            print(f"    - {f}")

    if changed:
        print(f"\n[~] 크기 변경된 파일 ({len(changed)}개):")
        for f in changed:
            print(f"    ~ {f}  ({_fmt_size(before[f])} -> {_fmt_size(after[f])})")

    print(
        f"\n요약: +{len(added)} 추가, -{len(removed)} 삭제, ~{len(changed)} 변경"
    )


def count_files(path, ext=".parquet"):
    """특정 확장자의 파일 수를 반환한다."""
    count = 0
    for _root, _dirs, files in os.walk(path):
        for f in files:
            if f.endswith(ext):
                count += 1
    return count


def total_size(path, ext=None):
    """디렉토리 내 파일들의 총 크기를 반환한다."""
    total = 0
    for root, _dirs, files in os.walk(path):
        for f in files:
            if f.startswith("."):
                continue
            if ext and not f.endswith(ext):
                continue
            total += os.path.getsize(os.path.join(root, f))
    return total


def _fmt_size(size):
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"
