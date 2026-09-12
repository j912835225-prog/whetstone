# Posters

One landscape poster per skill, 1600×900, for a README header, a social card, or a slide.

Every one of them is drawn by `code-print`'s own engines - the same `woodcut.py` and
`printlab.py` that ship inside that skill. No image generation, no stock, no fonts beyond
what your system already has. Each build script carries its recipe in its docstring:
subject, inks, division of labour, layout family, focus, area of air - the same form the
skill asks of any other job.

```bash
python3 build_rough_cut.py                       # writes rough-cut.svg
rsvg-convert -w 1600 -h 900 rough-cut.svg -o png/rough-cut.png
python3 -c "import glob,subprocess,sys; [subprocess.run([sys.executable,f]) for f in sorted(glob.glob('build_*.py'))]"
```

`png/` holds the rendered versions, which is what you actually post. The `.svg` files are
the source: edit a build script, re-run it, and the poster changes. Same input, same file,
every time - which is the whole argument for drawing print in code.

Two inks and paper per poster, one focus, one area of air. If you fork these, the fastest
way to keep them honest is the six questions in `code-print/SKILL.md` §7 - starting with
the one that matters: shrink it to a thumbnail, and see whether the focus survives.
