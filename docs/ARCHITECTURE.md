# Rendering and reader design

## Decision and limits

Native Garmin fonts have not been proven to shape pointed Hebrew on either target.
The initial host prototype preceded SDK installation. SDK 9.3.0 now runs, but the
target device packages are unavailable. No claim is made that native fonts fail;
they still need a representative on-device comparison before the final rendering
decision. Their API availability, font coverage and nikud positioning must be inspected
in the installed SDK, not inferred from a successful compilation.

The implemented alternative shapes each logical-order line **off-device** using
Pillow/libraqm, HarfBuzz and FriBidi. It wraps whole words before shaping and never
reverses strings. A word too wide for the column, missing glyph, unsupported control,
or clipped ink bounds is a build failure. Original content is preserved separately
from the derived visual assets.

The vendored Noto Serif Hebrew lacks ASCII punctuation. `tools/prepare_font.py` merges
it with Noto Serif and renames the derivative **Siddur Serif** under OFL 1.1. This
retains Hebrew shaping and adds punctuation. The original font binaries and Debian
copyright record are included. Every generated manifest records the derivative hash.
Host inspection is evidence for this shaping pipeline only; actual resource decoding,
nikud appearance, punctuation, and screen legibility still need simulator screenshots
and Hebrew-reader review.

## Device resources

Each device has its own column width, viewport, three font sizes, and generated resource
directory. FR970 uses 454 pixels with a 320 × 310 reading rectangle; Venu 2 uses 416
pixels with 288 × 282. Rectangle corners fit inside the round display. The conservative
rectangle prevents round-edge word clipping throughout scrolling. More aggressive
chord-dependent wrapping is deliberately deferred until device proof.

Each rendered line is a 16-level indexed PNG with black background and warm white ink.
This preserves antialiasing. Flash size, compiler resource limits, decoder pixel format
and actual heap usage for complete texts remain unknown. The manifest estimates visible
pixel storage at four bits per pixel; it does not include VM data, bitmap overhead or
firmware conversion. Full-text, all-nusach resource capacity is an open release risk.

## Continuous document

Section and paragraph gaps are positions inside one global document, not navigable
pages. `ReaderState` clamps the pixel offset and binary-searches the first visible line.
`ReaderView` evicts hidden resources before loading visible lines, clips to the reading
rectangle, and draws only the visible window. The source text is never shaped on-watch.
Button/swipe steps animate in eight-pixel increments at about 30 Hz; dragging updates
position directly. No perpetual redraw timer or network service is used.

Input callback behavior and event ordering are **unverified** until both target packages
and simulator are available. In particular, test duplicate drag/swipe delivery, drag
start/end behavior, rapid button presses, menu mapping, and system back navigation.

## Preferences and reading position

Versioned application storage holds the selected nusach and size. A separate record per
document stores pixel position, size, timestamp, and a section/paragraph/word anchor.
Font changes relocate the word anchor rather than reusing an unrelated pixel offset.
Changed content falls back to that section's heading, then the start if it no longer exists.

Interrupted reading resumes automatically if reopened within **45 minutes**. A longer
gap or backward clock change starts at the beginning. The timeout is evaluated at app
startup only, so reading or visiting a menu cannot reset an active session. The menu
also offers a direct return to the beginning. Position writes are debounced for 1.5
seconds after scrolling and saved on hide/exit. OS termination without callbacks can
lose the most recent unsaved movement. Persistence across app updates is supported only
as far as Garmin retains application storage; uninstall may erase it.

Text color is fixed warm white. System brightness is left to Garmin. Optional sections
are represented in the schema and remain included; no minhag filtering is implemented.
