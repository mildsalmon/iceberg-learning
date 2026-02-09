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


def show_metadata_hierarchy(table_path):
    """Iceberg 메타데이터 계층 구조를 시각화한다.

    metadata.json → manifest list → manifest files → data files
    전체 체인을 트리 형태로 출력한다.

    Usage::

        from utils.file_explorer import show_metadata_hierarchy
        show_metadata_hierarchy("/home/jovyan/data/warehouse/lab/my_table")
    """
    import json

    try:
        import fastavro
    except ImportError:
        print("fastavro가 필요합니다: pip install fastavro")
        return

    def _strip_uri(p):
        return p.replace("file:///", "/").replace("file:/", "/")

    STATUS = {0: "EXISTING", 1: "ADDED", 2: "DELETED"}

    # 1. version-hint → metadata.json
    hint = os.path.join(table_path, "metadata", "version-hint.text")
    if not os.path.exists(hint):
        print("(테이블이 아직 생성되지 않았습니다)")
        return

    with open(hint) as f:
        ver = f.read().strip()

    with open(os.path.join(table_path, "metadata", f"v{ver}.metadata.json")) as f:
        meta = json.load(f)

    snap_id = meta.get("current-snapshot-id")
    if snap_id is None:
        print(f"v{ver}.metadata.json  (스냅샷 없음)")
        return

    snap = next(
        (s for s in meta.get("snapshots", []) if s["snapshot-id"] == snap_id), None
    )
    if not snap:
        print("현재 스냅샷을 찾을 수 없습니다.")
        return

    ml_path = _strip_uri(snap["manifest-list"])
    operation = snap.get("summary", {}).get("operation", "?")

    # 2. Read manifest list (snap-*.avro)
    with open(ml_path, "rb") as f:
        manifests = list(fastavro.reader(f))

    # 3. Print tree
    print(f"v{ver}.metadata.json  (operation: {operation})")
    print("│")
    print(f"└─▶ {os.path.basename(ml_path)}  [Manifest List]")

    for mi, m in enumerate(manifests):
        m_path = _strip_uri(m["manifest_path"])
        m_name = os.path.basename(m_path)
        m_last = mi == len(manifests) - 1
        m_content = m.get("content", 0)

        # Build stats string
        if m_content == 0:  # DATA manifest
            keys = [
                ("added_data_files_count", "ADDED"),
                ("existing_data_files_count", "EXISTING"),
                ("deleted_data_files_count", "DELETED"),
            ]
        else:  # DELETES manifest
            keys = [
                ("added_delete_files_count", "ADDED"),
                ("existing_delete_files_count", "EXISTING"),
                ("deleted_delete_files_count", "DELETED"),
            ]
        parts = []
        for key, label in keys:
            n = m.get(key, 0) or 0
            if n > 0:
                parts.append(f"{n} {label}")
        stats = ", ".join(parts) if parts else "empty"
        type_label = "DATA" if m_content == 0 else "DELETES"

        mc = "└─▶" if m_last else "├─▶"
        indent = "        " if m_last else "    │   "

        print(f"    {mc} {m_name}  [Manifest — {type_label}: {stats}]")

        # Read manifest file entries
        try:
            with open(m_path, "rb") as f:
                entries = list(fastavro.reader(f))
        except Exception:
            print(f"    {indent}(읽기 실패)")
            continue

        for ei, entry in enumerate(entries):
            e_last = ei == len(entries) - 1
            status = STATUS.get(entry.get("status", 0), "?")

            df = entry.get("data_file", {})
            fp = _strip_uri(df.get("file_path", "?"))
            rc = df.get("record_count", "?")
            fc = df.get("content", 0)

            # Shorten path: keep data/partition/filename
            if "/data/" in fp:
                fp = "data/" + fp.split("/data/", 1)[1]

            ec = "└── " if e_last else "├── "

            tag = ""
            if fc == 1:
                tag = "  [DELETE FILE]"
            elif fc == 2:
                tag = "  [EQ DELETE]"

            print(f"    {indent}{ec}{fp}  ({rc}행, {status}){tag}")


def _fmt_size(size):
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size} B"
