---
name: asset-reviewer
description: Build browsable HTML catalogs of game-asset packs — one page per pack plus an index — with file paths, dimensions, and a written per-pack assessment of what the art actually is, plus per-pack sections that play the pack's own art: frame-sequence players, sprite-sheet players that slice the grid, and transform demos for packs that ship one static pose per subject. Use when someone has a directory of downloaded asset bundles (Humble, itch, GameDev Market, Unity Asset Store) and wants to see what they've got, or wants to understand how a given pack would actually be used, without opening hundreds of folders by hand.
---

# asset-reviewer

Turns a directory of asset packs into local HTML pages you can browse: every image
shown inline, every path copyable, plus prose describing what each pack contains and
whether it's usable.

## When this applies

A directory whose immediate subdirectories are each one asset pack. Layout *inside*
each pack is arbitrary and varies by vendor — the script doesn't assume a structure.

**Check that level is really the pack level before you run.** Bundles sell
"collections" that unzip to a single directory holding twenty-odd separate packs, and
pointing ROOT at the bundle then treats the whole collection as one pack: one enormous
page, no index, no per-pack prose. One archive here expanded to
`allinonepackrpgmaker/ALL-IN-ONE COLLECTION 2.4 Neonpixel/` with 27 vendor packs
inside it. Point ROOT at the directory whose children are the packs, even when that is
two or three levels down.

Two consequences of running a nested ROOT, both worth knowing before you do it:

- That run writes its own `index.html` and `_previews/` **inside** the collection
  directory. A later run at the parent level will then catalog those previews as if
  they were art. Run the parent level first, or `--exclude` the preview directory.
- The parent index still lists the collection as one pack. Say in that pack's blurb
  where the real per-pack index lives, or the nested pages are undiscoverable.

## How to run it

`catalog.py`, `unpack.py` and `motion.py` sit next to this file. All need Python 3.8+;
`catalog.py` and `motion.py` also need Pillow.

```bash
python catalog.py <ROOT>                       # pages into ROOT
python catalog.py <ROOT> --sheets-dir <TMP>    # also build contact sheets for review
python catalog.py <ROOT> --pack <name>         # one pack only, repeatable
python catalog.py <ROOT> --exclude 'ITS-*'     # skip matching dirs, repeatable
python catalog.py <ROOT> --prune               # delete pages+previews whose pack is gone
python catalog.py <ROOT> --no-collapse         # keep every resolution variant separate
python catalog.py <ROOT> --inline-limit 0      # inline even huge sheets (default 4M px)
```

**Never combine `--prune` with `--pack` or a filter that narrows the pack list.**
"Stale" means "a generated page for a pack not in this run", so filtering to one pack
makes every *other* page look stale and `--prune` deletes them all — pages and
`_previews/` directories both. Prune from a full, unfiltered run only.

To unpack a `.unitypackage` first — it's a gzipped tar of GUID directories, no Unity
needed:

```bash
python unpack.py <PACKAGE>              # -> <stem>_unpacked/Assets/...
python unpack.py <PACKAGE> --dry-run    # list the paths, write nothing
```

Ask before unpacking. These bundles run to gigabytes and the user may not want the
disk hit.

Every pack page opens with a "how these are used" section — frame players, sprite-sheet
players, and a live transform demo, whichever the pack's art calls for. Built by
default:

```bash
python catalog.py <ROOT> --motion off       # suppress those sections
python motion.py <SPRITE.png> --out <ROOT>  # standalone page for one sprite
```

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

Each pack also takes `"sheet_layout"` (`{"rows": [...], "note": "..."}`) to label the
sprite-sheet player's rows, `"sheet_sprites"` (pack-relative paths) to choose which
sheets get a player instead of letting it sample, and `"demo_sprite"`: a path **relative to that pack** naming the
sprite its transform demo should use. Set it once you've seen a sprite that makes a
good example — auto-pick optimises for how much artwork is in the file, which is not
the same as being legible or characteristic, and without this the choice changes
whenever the pack does. A `demo_sprite` that doesn't resolve is a hard error, not a
silent fallback.

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

## "How much of this is actually different art?"

For a big bundle this is the question the file count actively obscures, and it is the
one the user is really asking. Vendors pad by shipping the same drawing repeatedly:
time-of-day grades (`_DAY` / `_NIGHT` / `_SUNSET`), colour grades (`CALM` / `CHROMO` /
`VINTAGE`), team and elemental colourways. It is all cheap to measure and the numbers
are far more useful than an impression.

Three checks, cheapest first. Run them *before* writing prose about size.

**Byte-identical duplicates, within and across packs.** Hash every file. This is
decisive — no judgement involved — and it catches whole redundant packs, not just
stray files. In one collection, all 38 files of `INDUSTRIAL PROPS` were byte-identical
to files in `STEAMPUNK PACK-V2`: one of the twenty-seven "packs" was a complete
duplicate shipped under a second name. Report the pack pair and the count.

**Recolour families, by alpha silhouette.** Group images by (exact dimensions, hash of
a downscaled binarised alpha channel). Recolouring never touches alpha, so this is
colour-invariant by construction. Restrict it to images that actually have
transparency — a fully opaque tileset has no silhouette and will group with every
other opaque image of the same size.

**Then spot-check the biggest group before quoting the number.** Take the greyscale
correlation of a few members against the first. ≥0.98 means the same drawing
recoloured; 0.6 means two different sprites that merely share an outline. Both happen:

- In a medieval pack, the largest group was 44 files on one silhouette, correlating
  0.98–0.996 — genuinely one drawing in 44 palettes, and the pack was 91% repeats.
- In a sports pack, the same method said 73%, but correlations inside the top group
  ran 0.60–0.96, because *every* character sheet shares roughly the same silhouette.
  That number was inflated and saying so mattered.

So: report silhouette grouping as an **upper bound**, and say which packs you verified.

**A failure worth not repeating.** My first attempt at this signature mixed the alpha
silhouette with a luminance-edge map. It reported 4% redundancy across a collection
that was visibly full of recolours — because recolouring *changes luminance*, so the
signature could not detect the thing it was built to detect. If a similarity measure
includes any colour- or brightness-derived term, it cannot find recolours. Check that
a measurement can express the answer before trusting a low number from it.

Filename heuristics (stripping `-NIGHT`, `-DAY`, …) are a useful cross-check but
undercount badly, because plenty of recolours are named `DINO1A`, `DINO2A` with no
suffix to strip. Use them to corroborate, not to measure.

## Cheap checks that beat guessing

Each of these answers a question you would otherwise hedge on, for almost no cost.

- **Is the PSD a master or a banner?** Parse the header and layer records directly —
  `8BPS`, then dimensions, then walk the layer records for names and bounds. One
  14 MB PSD looked like editable source and was a 2848×2410 **store banner**: a
  background, a ribbon, a title layer, and the 60 avatars sitting as flat 256px
  layers. That settles "can I get these bigger?" — no — which no amount of looking at
  the PNGs would have.
- **Are the two variant folders actually two things?** A pack shipping `bg/` and
  `transparent/` may just be one set composited over a colour. Composite the cutout
  over black and diff it against the `bg` file: a max delta of ~4/255 is
  premultiplied-alpha rounding, i.e. identical. Then say the `bg/` folder is
  redundant, rather than reporting twice the assets.
- **What does the pack's own code say?** Covered under grid layout below, and it
  generalises: vendor scripts, `.meta` files and ReadMes state intent outright.
  One ReadMe admitted its 21 animations were "not viewable in the provided scene".

## Showing how a pack would be used

Cataloguing answers "what do I have". It doesn't answer "what do I do with it", and
for some packs that second question is the one blocking the user. Each pack page
carries a **"how these are used" section** at the top, built by `catalog.py` from
`motion.py`, before the asset grids. The index stays a plain list of packs.

Two halves apply independently, so a pack can get either, both, or neither:

**Frame players**, for packs that ship real animation frames. `find_sequences` spots
folders of numbered PNGs and builds a player per sequence — play/pause, step, an fps
slider and a frame counter. Every frame is in the page and playback toggles which one
is visible, so it never stalls on a fetch. Up to eight players, spread across the
pack. Note in the prose that **the frame rate is a guess**: vendors almost never ship
timing data, and 12 fps is just a common hand-animation default.

**Sheet players**, for packs that ship one grid image per character instead of loose
frames. `detect_grid` finds the cell size from the fully transparent seams between
cells — take the square cell sizes that divide both dimensions and keep the *smallest*
whose boundary rows and columns are empty, since every multiple of the true cell also
has clean boundaries. Only the boundary strips are read, so it stays cheap on a
2048×8192 sheet. The player then steps `background-position` across a row, which is
what an engine does. Sheets are downscaled into `_previews/_sheets/` first; a 16.7 Mpx
sheet as a live CSS background is the difference between a page that opens and one
that doesn't.

**The transform demo**, for packs that are mostly small single poses — one pose per
creature and no frames, which looks unusable until you know the sprite is meant to be
moved rather than redrawn. It runs one sprite through idle bob, breathe, hover, fake
walk, attack lunge, hit flash and death, with the CSS printed under each panel, plus a
combat loop and live scale/filtering controls.

`--motion off` suppresses all of them. Pin the demo sprite with `demo_sprite` in that
**pack's** notes entry once you've seen the art; auto-pick optimises for how much
artwork is in the file, which is not the same as being a good example.

### Grid layout is detectable; what the rows *mean* is not

`detect_grid` can tell you a sheet is 4×16 of 512px cells. It cannot tell you that row
6 is "Up · Attack". Do not guess that from looking — I guessed "columns are facing
directions" from a contact sheet and the vendor's own code said the opposite.

**Read the engine code the pack ships.** These bundles routinely include Unity, Godot,
Phaser or Cocos integration, and it states the layout outright. In one pack here:

```gdscript
enum SpriteFacing { Down=0, Up=1, Left=2, Right=3 }
enum AnimFlag     { Idle=0, Run=1, Attack=2, Ded=3 }
var Frames = 4;   var ARows = 4;
cFrameRow = (direction * ARows) + state;
```

That is 16 rows of 4 frames, not 4 directions of many frames. Put the result in the
pack's `sheet_layout.rows`, and say in `note` where it came from so the claim is
traceable. The same file usually carries the intended frame rate — and its own
inconsistencies worth flagging, like `FrameRateMS = 1 / 4.0` sitting beside a comment
claiming 8 per second.

### RPG Maker packs are a fixed format — read the filenames, don't guess

A large share of Humble/itch bundles is RPG Maker MV/MZ art, and that engine fixes
sizes and naming so tightly that dimensions alone identify what a file is. Recognising
it turns a wall of anonymous PNGs into a structured inventory for free:

| What | Size | Notes |
|---|---|---|
| Tileset `A1`–`A5` | 768×576 | autotiles; `A1` is animated water |
| Tileset `B`–`E` | 768×768 | 16×16 grid of 48px tiles |
| Faceset (packed) | 576×288 | 4×2 grid of 144×144 faces |
| Faceset (single) | 144×144 | MV reads it as a one-face set — valid, just wasteful |
| Character sheet | 3×4 cells | `$` = one character; default is 8 in a 12×8 grid |
| Parallax | 816×624 and up | 816×624 is the default MV screen |

The filename prefixes are load-bearing and are the thing to explain in the prose,
because they are invisible to anyone who has not used the engine:

- **`!`** — ground-aligned: no floating offset and no step bob. Used for doors,
  bushes, chests.
- **`$`** — the file holds a single character, so the whole image is one 3×4 grid.
- **`!$`** together — one ground-aligned object as a 3×4 sheet. This is how the
  "animated flora" packs work: a swaying bush or a waving flag placed as an event.

In one collection, 928 of 2,555 files were `!$` sheets at 468×636 — 36% of the whole
thing, and its most distinctive asset type. Also worth flagging in the prose: swapping
a tileset for a `-NIGHT` copy is a worse way to do night than tinting the screen, so
those grades are mostly weight rather than value.

### Numbered files are ambiguous — three rules disagree with you

Vendors number files for frames, for tiers, and for unrelated assets. `find_sequences`
requires all three of these, and each one exists because a real pack broke the others:

- **Starts at 0 or 1, contiguous.** `jungle_201.png`–`jungle_212.png` are twelve
  different monsters, not a twelve-frame animation.
- **Small enough to play.** `30MonsterPack/01.png`–`30.png` at 2048×8192 each is a
  monster roster, and could not be animated in a browser anyway.
- **Dominates its directory.** `Stat_Attack_01..03` sitting among eighty other icons
  are upgrade tiers. Frames are what their folder is *for*. Measured collectively per
  directory, so one folder holding both a walk cycle and an idle cycle still counts.

If a pack still trips it, say so in the notes rather than trusting the label.

### Keep an eye out for the single-pose case

`catalog.py` prints a hint when a pack is mostly small sprites:

```
384 of 386 assets are <=128px -- likely one pose per subject; check whether any
animation frames exist at all
```

That is a prompt to look, not a verdict — the heuristic is only size. Confirm against
the sequence detection above, then say plainly in the notes which it is. When it *is*
single-pose, name the genre it suits rather than calling it limited. A pack of small
single poses grouped into families is a bestiary, and that is the JRPG battle model:
NES-era Final Fantasy enemies are single static images, and the whole attack readout
is the party member stepping forward, the enemy flashing, and a damage number. Modern
equivalents are deckbuilders, auto-battlers and idle games.

One detail worth getting right, because it is easy to overclaim: **constant idle
motion is not the retro part.** Those sprites sit perfectly still; the budget went
into spell effects. The bob is a later mobile/idle-game habit. The hit flash *is* the
old part, and it survived because on that hardware it was a palette swap.

Also reach for this when the user has called a pack useless or limited, or when you're
explaining scaling — the slider plus the "integer scale only" and "smooth filtering"
toggles demonstrate pixel shimmer and bilinear blur far faster than prose.

### Terminology

Use the standard terms and say when a term isn't one. **Squash and stretch**,
**anticipation** and **follow-through** are three of the twelve principles of
animation; **hitstun**, **knockback**, **easing** and **tweening** are real terms of
art. "Bob" and "fake walk" are just descriptions with no accepted name. The umbrella
terms are **procedural animation** and **game feel** / **juice**. The generated page
prints the term under each panel label, so keep those two in sync.

Check the vendor's intent before writing about it, since it's cheap to do and it's
evidence rather than assertion. Unity `.meta` files carry the import settings —
`filterMode: 0` is Point, meaning the artist expected nearest-neighbour upscaling.
`unpack.py --keep-meta` retains them, and they can also be read straight out of an
unextracted `.unitypackage` with `tarfile`.

State the limits alongside it: transform animation cannot change silhouette, and
mixing tweened sprites with hand-animated ones reads as unfinished. The page says
both, but say it in the notes too.

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
- **The transform demo sizes itself from the sprite.** Scale factors are integers
  chosen to bring the art to a readable size, so a 32 px sprite lands at 4–6× and a
  512 px icon stays at 1×. Anything over 512 px still renders but is letterboxed.
- **Frame players render smooth unless the frames are small.** These are usually
  being scaled *down* to fit a card, and nearest-neighbour downsampling of vector art
  just adds aliasing. Only frames ≤128 px get `pixelated`.
- **`--prune` also clears orphaned previews.** `_previews/<pack>/` and
  `_previews/_sheets/<pack>/` survive their pack being deleted and run to tens of
  megabytes. They are reported on every run and removed with `--prune`.
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
Zip archives are still listed rather than opened, which is the biggest gap: a bundle
is mostly `.zip` until someone extracts it by hand.

Sheets are sliced for *display* only — nothing exports the cells as loose frames, and
the catalog still shows one card per sheet rather than per animation.

Grid detection assumes square cells on a uniform grid with transparent seams. Packed
atlases, trimmed cells and non-square frames all defeat it, and there is no fallback
to a hand-specified cell size in the notes.

**This is the largest practical gap, and RPG Maker triggers it every time.** Those
`!$` sheets are 3×4 grids of *non-square* cells — 468×636 divides into 156×159 — so
`detect_grid` returns `None` and every one of them renders as a still card. In one
27-pack collection that silently disabled the sheet player for 928 files, 36% of the
art, with nothing on the page saying why. A `sheet_grid` override in the pack's notes
entry (explicit cols × rows, or an explicit cell size) would fix the whole class at
once, since the layout is a fixed engine convention rather than something to detect.
Until that exists: **say in the notes when a pack's sheets are non-square**, so the
static cards read as a known limitation rather than as the art being static.

Frame timing is guessed — 12 fps for sequences, 8 for sheets. Some packs ship a
`.json`, `.anim`, `.fla` or engine script carrying the real rate; only the last is
read, and only by you, by hand.
