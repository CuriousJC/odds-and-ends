---
name: asset-reviewer
description: Build browsable HTML catalogs of game-asset packs — one page per pack plus an index — with file paths, dimensions, and a written per-pack assessment of what the art actually is. Use when someone has a directory of downloaded asset bundles (Humble, itch, GameDev Market, Unity Asset Store) and wants to see what they've got without opening hundreds of folders by hand.
---

# asset-reviewer

Turns a directory of asset packs into local HTML pages you can browse: every image
shown inline, every path copyable, plus prose describing what each pack contains and
whether it's usable.

## When this applies

A directory whose immediate subdirectories are each one asset pack. Layout *inside*
each pack is arbitrary and varies by vendor — the script doesn't assume a structure.

## How to run it

`catalog.py` and `unpack.py` sit next to this file. Both need Python 3.8+; `catalog.py`
also needs Pillow.

```bash
python catalog.py <ROOT>                       # pages into ROOT
python catalog.py <ROOT> --sheets-dir <TMP>    # also build contact sheets for review
python catalog.py <ROOT> --pack <name>         # one pack only, repeatable
python catalog.py <ROOT> --exclude 'ITS-*'     # skip matching dirs, repeatable
python catalog.py <ROOT> --prune               # delete pages whose pack is gone
python catalog.py <ROOT> --no-collapse         # keep every resolution variant separate
python catalog.py <ROOT> --inline-limit 0      # inline even huge sheets (default 4M px)
```

To unpack a `.unitypackage` first — it's a gzipped tar of GUID directories, no Unity
needed:

```bash
python unpack.py <PACKAGE>              # -> <stem>_unpacked/Assets/...
python unpack.py <PACKAGE> --dry-run    # list the paths, write nothing
```

Ask before unpacking. These bundles run to gigabytes and the user may not want the
disk hit.

Pages are written **into ROOT** and reference images by relative path. That's
deliberate — they only work in place, and that's fine for local review. Don't move
them and don't commit them; asset art is usually licensed, and this repo is public.

## The two-phase workflow

Phase 1 and 2 are separate runs because the prose has to come from actually looking
at the art.

**Phase 1 — scan and sample.** Run with `--sheets-dir` pointed at a scratch
directory. The script writes the HTML *and* builds 1024×1024 contact sheets: up to
256 assets per pack, sampled evenly, tiled 8×8 on a mid-grey background with a yellow
index number on each tile. stdout carries a legend mapping each number back to its
path and dimensions.

**Phase 2 — look, then write notes.** Read the contact sheets, then write
`_catalog_notes.json` into ROOT and re-run without `--sheets-dir`. The prose gets
baked into the pages. Notes survive regeneration because the script reads the JSON
back every run.

### Token budget — read this before looking at anything

Image tokens are roughly `width × height / 750`. How the art reaches you dominates
the cost, by two orders of magnitude:

| Approach | Cost for ~1,000 assets |
|---|---|
| Every unique image individually | ~250k tokens |
| **Contact sheets, 1–2 per pack** | **~3–15k tokens** |
| One spot-check image per pack | ~3k tokens |

Use contact sheets. Read **1–2 sheets per pack**, not all of them — the script
generates up to four, and the later ones are usually more of the same. Only reach for
individual full-size images when a sheet leaves a specific question unanswered
(fine detail, transparency edges, exact palette).

Sheets have two known blind spots, so don't over-claim from them:

- **Animation frames flatten.** Twenty frames of a walk cycle become twenty
  near-identical tiles. Say "frame sequence", don't describe each one.
- **Fine detail is lost at 128 px.** Style, subject, palette and coherence read
  fine; halo artifacts, edge quality and small text don't.

The structural half — paths, dimensions, counts, grouping, duplicate detection — is
pure script output and costs nothing. Never hand-write catalog HTML; a 500-file pack
is tens of thousands of output tokens and you will mistype paths.

## `_catalog_notes.json`

```json
{
  "index": { "summary": "...", "highlights": ["..."] },
  "packs": {
    "<pack-dir-name>": {
      "blurb":     "one line, shown in the index table",
      "summary":   "paragraphs, split on blank lines",
      "highlights": ["bullets under the summary"]
    }
  }
}
```

Every field is optional. Unknown packs are ignored, so the file can run ahead of what
has actually been extracted.

## What to put in the prose

Aim at "should I use this, and for what" — the user can already see the pictures.

- **Style, named concretely.** "Glossy casual-mobile, thick outlines, saturated" beats
  "nice art". Say when two packs in the same bundle *won't* mix.
- **Structure that isn't obvious from filenames.** Numbered suffixes are often upgrade
  tiers rather than variants. Separate shadow layers, body-part rigs, and frame
  sequences all change how the pack gets used.
- **Coverage and gaps.** 30 skill icons is a prototype, not an ability tree. Say so.
- **Defects.** Missing files in one resolution folder, vendor typos in filenames,
  formats that need software the user may not have (`.fla` needs Adobe Animate).

## Behaviour worth knowing

- **Junk filtering.** `__MACOSX`, `.DS_Store`, `Thumbs.db`, `desktop.ini`, `._*` are
  excluded. This routinely halves the file count versus what Explorer shows — say so
  when reporting numbers, or they look wrong.
- **Resolution folding.** Purely numeric directory components are stripped when
  keying, so `Round/128/x.png` and `Round/512/x.png` fold into one card while
  `Square/128/x.png` stays separate. The card shows the largest and lists the other
  widths. `--no-collapse` turns it off. Only *numeric* folders fold — a pack using
  `default size/` and `min size/`, or `shadow/` and `no shadow/`, shows every copy.
  Say so in the notes rather than letting the count mislead.
- **Fold mismatches are findings, not bugs.** If a pack yields 82 assets from three
  80-file folders, some file is present in one resolution and not another. Check it
  and put it in the notes.
- **Archives are listed, never opened.** `.zip`, `.7z`, `.rar`, `.unitypackage`,
  `.tar`, `.gz` appear in a table with sizes. A pack that is only archives still gets
  a page so the index stays complete. `unpack.py` handles `.unitypackage`; nothing
  extracts zips yet.
- **Engine projects duplicate the art.** Bundles that ship per-engine sample projects
  (Unity, Godot, Phaser, Cocos) carry a full copy of the same PNGs in each. Check for
  this before cataloguing — one bundle here had 6,214 duplicate files across five
  copies — and pass `--exclude` so the page shows the art master once.
- **Tiny sprites get upscaled.** Anything ≤64 px on its long edge renders with
  `image-rendering: pixelated` filling the card, because a 32×32 sprite shown at
  native size in a 170 px box is unreadable and looks like a broken image. The
  threshold sits at 64 deliberately: true pixel art is in, 128 px icons stay out
  and keep smooth scaling. If a user calls a pack useless, check this first — it is
  usually the display, not the art.
- **Oversized images get previews.** Anything above `--inline-limit` (default 4 Mpx)
  is downscaled into `_previews/` and the card shows that instead, still linking the
  original. Sprite sheets of 2048×8192 are common and inlining them at full size will
  hang the browser. This is the one exception to "no thumbnails".
- **`--prune` only removes pages carrying the generator's marker comment**, so a
  hand-written `.html` sitting in ROOT is never at risk. Pages generated before the
  marker existed must be deleted by hand.
- **Paths are percent-encoded** in `src`/`href`; the visible path text and the
  click-to-copy value stay human-readable. Copy falls back to `execCommand` because
  the clipboard API is unavailable on `file://`.
- Pages are theme-aware via `prefers-color-scheme` and lazy-load images, so a
  500-image page opens immediately.

## Extending

`.zip` is still unhandled — `zipfile` can list entries without extracting, which
would let archive tables show contents rather than just a size. Sprite-sheet slicing
is the other obvious gap: sheets are catalogued as single images, so a pack of
2048×8192 sheets shows 182 cards rather than the thousands of frames inside them.
