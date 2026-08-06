# ai-film-skills

**A directing knowledge base for locally-generated AI short films** — six Claude Skills about *what to decide*, not *how to install things*.

[中文](./README.zh-CN.md) · [Gallery](./docs/gallery.md) · [Two kinds of skill](./docs/how-skills-differ.md) · [MiniMax H3 on 12 GB](./docs/minimax-h3-local-deploy.md) · [Attribution](./ATTRIBUTION.md)

> **Install it and it works.** Easiest path — paste this at Claude Code:
> *"Install this skill for me: https://github.com/L-Trunks/ai-film-skills — clone it and run install.sh"*
> Then say "make a short film." The skill itself is methodology and knowledge; it depends on no scripts, no models, no GPU.
>
> To run the reference implementations too, set three paths in `examples/scripts/config.py`
> and run `python doctor.py` first.

---

## Watch first

Two films, both produced on one **RTX 4070 Ti (12 GB)**. No cloud API in the generation path.

The clips below are silent GIFs. **Full versions with sound**:
▶ [Nine Tails](./docs/assets/jiuwei.mp4) · [Shan Hai](./docs/assets/shanhai.mp4)

### *Nine Tails* — long-shot, chained: 58 segments joined into one film

<img src="./docs/assets/jiuwei.gif" width="400">

Tail frame becomes the next head frame, one character throughout. Narration and subtitles
added in post; one BGM track across the whole film.
**57 generation runs / 5 GPU-hours**, of which 17 were thrown away and redone.

### *Shan Hai* — short-shot family, trailer

<img src="./docs/assets/shanhai.gif" width="400">

**Not one mythical beast appears in full** — only traces. That wasn't a style choice, it was
forced by the model: the creatures of the *Classic of Mountains and Seas* have no photographic
basis, so shooting them head-on always looks fake. Six shots out of thirty survived.

> More stills and breakdowns in the [gallery](./docs/gallery.md).

---

## The three problems this solves

Making short films with AI, the things that actually block you are never the API calls:

**① Every film comes out the same.**
Once you write one structure that works, you'll unconsciously reuse it forever. This happened to us: four trailers (one *Shan Hai* plus three SCP pieces) compared shot by shot, and shot 25 in all four is "takes off the face covering, near-total darkness," while shot 36 in all four is "extreme wide, empty landscape." Writing *"remember to vary it"* in the docs does nothing — we wrote exactly that, and still collided.

**② Nowhere to record what you learned the hard way.**
"Glow compositing in YUV tints the whole film magenta." "Any prompt describing *something absent that left a trace* will make the model draw the absent thing." You can't search for this. You buy it with GPU time, and if you don't write it down you buy it again three months later.

**③ Parameters welded to one model.**
"2.04 seconds per shot is a hard limit" — true only for LTX-2.3. Change models and it's worthless, but nothing in the docs tells you which numbers are laws of physics and which are just properties of one machine.

---

## The three answers

### Anti-homogenization: orthogonal variables + a two-layer fingerprint

Before writing any shot, you fill in five orthogonal dimensions and must differ from recent films:

| Dimension | Values |
|---|---|
| Time structure | linear / reverse / loop / parallel cut / single-moment slices |
| POV | omniscient / follow one person / surveillance·instrument / object's view / absent |
| Tempo | steady / accelerate-to-burst / front-loaded / two breaths / fully static |
| Audio | BGM throughout / SFX-driven / ambient only / total silence / desynced |
| Ending | empty wide / return to first shot / hard cut to black / unresolved / mundane |

But **checking that table alone will not catch real repetition.** Those three SCP films could each have filled it differently and still come out shot-for-shot identical, because the repetition lives one level down — at *section function → concrete shot design*.

So the fingerprint records two layers and blocks at each:

```
vars       ≥3 dimensions collide  →  reselect (hard block)
structure  same as any of last 3  →  requires an explicit justification
signature  ≥2 fields collide      →  redesign (regardless of vars)
```

`signature` holds opening framing, ending framing, peak device, and climax pattern — the concrete choices. That third rule is the one that actually catches the SCP problem.

Edit structures are demoted from *truth* to *one option among several*, stamped with a usage record:

```yaml
used_by: [Shan Hai, SCP-Breach, SCP-Archive, SCP-Field]
use_count: 4
```

Seeing `use_count: 4` makes you pick something else. Far more effective than writing "please do not reuse."

### Swapping models: profiles + self-calibration

Every model-dependent number moves out of the prose into a profile, and formulas take variables:

```
shot_count = (target_sec - transition) / (max_shot_sec - transition)
                                          ↑ a variable, no longer a hardcoded 2.0417
```

**Only one profile in this repo has real data** — `ltx-2.3-q4-12g`, which we measured. We do not ship numbers for Wan, HunyuanVideo, Kling or Jimeng, because we haven't run them; copying figures out of their docs would be fabrication, and getting caught fabricating costs more trust than the convenience is worth.

What you get instead is a blank template plus a **five-step calibration** to measure your own:

| To measure | How |
|---|---|
| `max_shot_sec` | Fix one keyframe, render at 2s/3.5s/5s, find where the subject drifts out, take the step before |
| `align_to` | Feed a non-divisible size and read the error, or read the VAE compression rate |
| `restart_each_shot` | Run two shots back to back; does the second OOM or slow down? |
| `text_sensitivity` | Put a signboard/menu in the subject, render 3×, count the garbled text |
| `motion_style` | Write "she slowly turns her head to the window" and see if it overshoots |

### Pitfalls: their own document, quotable directly

`knowledge/pitfalls.md` is the real asset here. A few samples:

- **Glow chains must run in RGB.** `blend=screen` is per-plane; in YUV it screens the U/V chroma planes too and tints everything magenta. Run the chain in `format=gbrp`, convert to `yuv420p` on the way out.
- **Absence cannot be prompted directly.** Ask for "a chair cushion with the dent of someone who sat there" and you get a person sitting in the chair. Negations must be enumerated: "nobody in the chair, no body, no limbs, no clothing anywhere in frame."
- **Keep text-bearing objects out of the subject.** A negative prompt for "no watermark" will not stop text the subject itself implies. Signs, menus, labels, packaging, road signs — **the fix is changing the subject, not adding negatives.**
- **The more dramatic, the faker.** Volcanoes and calving glaciers sit in the model's overfit zone: the training data is all render art, so it always looks AI. Ordinary moments read as real.
- **Face-consistency threshold is 0.28, not 0.5.** Embedding cosine similarity between two images of the same AI-generated character is inherently lower than for photos of real people. Borrowing the real-photo threshold rejects every good image you have.
- **Text in your prompt gets painted into the frame.** Not just quoted dialogue. One segment failed three times running, rendering in turn: the narration line, the words "twenty-five or so" from a supporting-character description, and the stage direction "bowed slightly." **Numerals are the highest risk**, and appending "no text, no watermark" does nothing — all three versions had that line.
- **Generic upscalers wreck small faces.** Below ~110px face width, ESRGAN melts features together and grows crosshatch artifacts on skin; above 150px it's harmless. Fix it at generation time — an upscaler cannot invent detail that was never generated. **Raising the generation resolution is the cheapest lever**: 0.3 MP → 0.5 MP is a 1.30× linear scale, turning an 86px face into 112px, and you only need to raise it for the shots that need it. Faces under ~60px need a different framing, not a different parameter. Deciding per shot in post is the last-resort fallback, and what it buys you is "stops inventing," not "fixed."
- **Face restoration is a liability for non-human characters.** CodeFormer turned pale amber fox-spirit irises grey-blue; `fidelity=0.9` didn't stop it. Its prior for "normal human face" is too strong.
- **Rebuild timestamps after concat.** Without `setpts=N/FPS/TB` the encoder silently drops frames (6062 → 6013 measured), and the loss accumulates — audio drifts further out of sync the longer the film runs.

Chained long-form (dozens of segments joined tail-to-head) has its own body of pitfalls in
`knowledge/chain-consistency.md`: character drift needs periodic re-anchoring, the anchor prompt
must carry the full character description, empty shots must never be anchored, and the lead's
"white hair" bleeds onto everyone else in frame.

---

## The six skills

One hub does the directing; five satellites each own a stage and can also be triggered on their own.

| Skill | Owns |
|---|---|
| **local-ai-film** ★ | The hub. Opening ritual (profile → variables → fingerprint), pitfalls, execution |
| emotion-to-camera-language | Translates "atmospheric" into light position / depth of field / camera position / subject state |
| lock-character-reference | Locking a character reference, and what to do when it won't stabilize |
| shot-breakdown | Filtering a batch of generations; when to stop rerolling |
| rhythm-density | Per-shot durations and density contrast |
| material-driven-storyboard | Reverse-engineering a storyboard when you lack the footage |

The opening flow:

```
1.  Pick a profile      → profiles/
2.  Roll the variables  → directing/variables.md
3.  Check fingerprints  → directing/fingerprint.md   ← collision means start over
4.  Pick/write skeleton → directing/structures/
5.  Compute shots/segs  → formula pulls from profile
6.  Write shots         → prompt-craft.md or shot-list-prompt.md
7.  Probe              → shot-breakdown
8.  Batch run          → examples/scripts/
9.  Post               → knowledge/post-production.md
10. Review             → knowledge/pitfalls.md, item by item
11. Write fingerprint  → films.jsonl                ← close the loop or it all stops working
```

Steps 1–3 gate step 6. Step 11 closes the loop — skip it and the whole mechanism silently dies.

### Two orthogonal forks

**By model family** (the profile's `family` field):

| | short-shot | long-shot |
|---|---|---|
| Examples | LTX, Wan | MiniMax H3 |
| One generation yields | one continuous shot, 2–5s | one segment of 1–3 shots, 5–15s |
| Hard cuts within a generation | impossible | works |

The two families' knowledge **contradicts each other** — action arcs, text-bearing objects, and
how to write relationships all flip between them. Know which family you're on before reading.

**By production mode**: one-off (atmospheric pieces, trailers) or chained (narrative films —
tail frame becomes the next head frame, one character throughout). Chaining works on both
families but requires reading `chain-consistency.md`.

---

## Usage

### Step 1 — install the skills (you're done here)

**Easiest path — paste this at Claude Code:**

```
Install this skill for me: https://github.com/L-Trunks/ai-film-skills
Clone it and run install.sh
```

It will clone the repo, run the installer, and drop all six skills into `~/.claude/skills/`.
Re-running is safe — an existing directory of the same name is backed up before it's replaced.

<details>
<summary>Prefer to do it yourself</summary>

```bash
git clone https://github.com/L-Trunks/ai-film-skills
cd ai-film-skills
bash install.sh                # Windows: powershell -ExecutionPolicy Bypass -File install.ps1
```

Pass `--project` to install into the current project's `.claude/skills/` instead of your home directory.

Or just copy them by hand:

```bash
cp -r skills/* ~/.claude/skills/
```

</details>

Then tell Claude Code "make a short film" or "batch-run some atmospheric videos."

> **Using Codex or another agent?**
> They don't have Claude Code's skill auto-triggering, but these documents are plain Markdown
> methodology — clone the repo, point your agent at `skills/local-ai-film/SKILL.md`, and it will
> still walk you through the whole process. You just have to name the file each time.

**That's it — the skill is fully usable at this point.** It walks you through the opening
ritual, blocks homogenization via the fingerprint, picks the route that matches your model,
writes the shot list, and steers you around the several dozen pitfalls in `knowledge/`.
None of that **needs scripts, models or a GPU** — it works just as well if you generate
through a cloud API.

### Step 2 (optional) — calibrate your own profile

```
Follow the five steps in profiles/calibration.md — about 40 minutes locally
```

It works without this, but **your shot counts and durations will be wrong**, because the
formulas read `max_shot_sec` out of a profile, and the shipped one was measured on my machine.

### Step 3 (optional) — run the reference scripts

`examples/scripts/` is my machine's implementation. Everything machine-specific lives in
`config.py`, so you never have to grep through the scripts:

```bash
# pick one
export AIFILM_COMFY=/path/to/ComfyUI          # 1. environment variables
export AIFILM_PY=/path/to/python
export AIFILM_ROOT=/path/to/output

cp config.py config_local.py                  # 2. a local override (already gitignored)
                                              # 3. or just edit config.py's defaults
```

Then check your setup:

```bash
python doctor.py
```

It verifies the ComfyUI directory, the interpreter, ffmpeg, the model files, whether ComfyUI
is actually running and whether you have enough VRAM — and for anything missing, tells you
which variable to change.

---

## Two kinds of skill live here, in two different formats

This is deliberate, not an oversight:

| | Distilled (RIA) | Hands-on |
|---|---|---|
| Which | The five satellites | local-ai-film |
| Source | Methodology distilled from others' published work | Measured by us |
| Format | R / I / A1 / A2 / E / B | Assembly flow + knowledge + profiles |
| Trust | `verified: secondhand` | `verified: measured here` + hardware stated |

Every number carries a `verified` field. **"I measured this" and "I heard this" must stay distinguishable** — that separation is what makes the rest of the repo trustworthy.

`local-ai-film` is deliberately *not* forced into the RIA format. It's firsthand experience with no source text to quote; applying the template would only manufacture a fake citation section.

---

## Attribution

The five satellite skills distill methodology from several creators' public work. The `R` sections have been rewritten in our own words; original sources are listed in [ATTRIBUTION.md](./ATTRIBUTION.md).

## License

Content is CC-BY-4.0. Code under `skills/local-ai-film/examples/scripts/` is MIT.
