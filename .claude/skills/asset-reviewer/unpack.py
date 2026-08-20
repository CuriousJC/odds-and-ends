#!/usr/bin/env python3
"""Unpack .unitypackage archives without Unity.

A .unitypackage is a gzipped tar of one directory per asset, named by GUID:

    <guid>/asset        the file bytes
    <guid>/asset.meta   Unity metadata
    <guid>/pathname     the original project-relative path, e.g. Assets/Art/x.png
    <guid>/preview.png  thumbnail Unity generated (optional)

This rebuilds the original tree by reading each `pathname` and writing `asset`
there. Entries with no `asset` are folder records and are skipped.
"""

import argparse
import os
import posixpath
import sys
import tarfile

SKIP_EXT = {".meta"}


def safe_join(dest, rel):
    """Reject absolute paths and traversal before joining."""
    rel = rel.replace("\\", "/").strip().lstrip("/")
    if not rel or rel.startswith("../") or "/../" in rel or rel == "..":
        return None
    if posixpath.isabs(rel) or (len(rel) > 1 and rel[1] == ":"):
        return None
    out = os.path.normpath(os.path.join(dest, *rel.split("/")))
    if not os.path.abspath(out).startswith(os.path.abspath(dest) + os.sep):
        return None
    return out


def unpack(pkg, dest, keep_meta=False, dry_run=False):
    written = skipped = folders = 0
    with tarfile.open(pkg, "r:gz") as tf:
        members = {m.name: m for m in tf.getmembers() if m.isfile()}

        guids = sorted({n.split("/")[0] for n in members if "/" in n})
        for guid in guids:
            pn = members.get("%s/pathname" % guid)
            asset = members.get("%s/asset" % guid)
            if pn is None:
                skipped += 1
                continue
            if asset is None:
                folders += 1          # folder record, no payload
                continue

            raw = tf.extractfile(pn).read().decode("utf-8", "replace")
            rel = raw.splitlines()[0] if raw.splitlines() else ""
            target = safe_join(dest, rel)
            if target is None:
                print("  ! refusing unsafe path from %s: %r" % (guid, rel))
                skipped += 1
                continue
            if os.path.splitext(target)[1].lower() in SKIP_EXT and not keep_meta:
                skipped += 1
                continue

            if dry_run:
                print("  %s" % rel)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "wb") as fh:
                    fh.write(tf.extractfile(asset).read())
                if keep_meta and members.get("%s/asset.meta" % guid):
                    with open(target + ".meta", "wb") as fh:
                        fh.write(tf.extractfile("%s/asset.meta" % guid).read())
            written += 1
    return written, skipped, folders


def main():
    ap = argparse.ArgumentParser(description="Unpack a .unitypackage without Unity.")
    ap.add_argument("package", help=".unitypackage file")
    ap.add_argument("-d", "--dest", help="output directory (default: alongside, "
                                        "named <package stem>_unpacked)")
    ap.add_argument("--keep-meta", action="store_true", help="also write .meta files")
    ap.add_argument("--dry-run", action="store_true", help="list paths, write nothing")
    args = ap.parse_args()

    pkg = os.path.abspath(args.package)
    if not os.path.isfile(pkg):
        sys.exit("no such file: %s" % pkg)

    dest = os.path.abspath(args.dest) if args.dest else os.path.join(
        os.path.dirname(pkg), os.path.splitext(os.path.basename(pkg))[0] + "_unpacked")
    if not args.dry_run:
        os.makedirs(dest, exist_ok=True)

    print("%s -> %s" % (os.path.basename(pkg), dest))
    written, skipped, folders = unpack(pkg, dest, args.keep_meta, args.dry_run)
    print("%d files%s, %d folder records, %d skipped"
          % (written, " (dry run)" if args.dry_run else " written", folders, skipped))


if __name__ == "__main__":
    main()
