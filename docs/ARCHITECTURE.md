# Rendering and reader design

## Decision and limits

The active target is FR970; Venu 2 was removed at the user's request. Native Garmin Hebrew shaping has not been assessed. The current review app uses the validated bitmap pipeline described below. Historical prototype evidence is in FR970-VALIDATION.md; current full-source evidence is in REVIEW-BUILD.md.

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

FR970 uses a 454-pixel display and a centered 320 × 310 reading rectangle. All three nuschaos and sizes are compiled into one app. Whole-word wrapping happens off-device.

Two adjacent rendered lines share one 16-level indexed PNG atlas. Identical atlases are deduplicated; 1,356 image resources fit the SDK's 2,047-resource ceiling. Lossless SDK compression reduces flash size. Each line stores its source-y offset. The renderer uses ordinary drawBitmap with destination clipping, because this SDK rejects indexed source cropping through drawBitmap2. The cache retains only currently visible atlas resources.

The generated manifest estimates visible atlas pixel storage at four bits per pixel, below 128 KB for these layouts. This excludes VM data and decoder overhead. Simulator memory samples and artifact sizes are evidence, not proof of physical-watch behavior or absence of long-term leaks.

## Continuous document

Section and paragraph gaps are positions inside one global document, not navigable
pages. `ReaderState` clamps the pixel offset and binary-searches the first visible line.
`ReaderView` evicts hidden resources before loading visible lines, clips to the reading
rectangle, and draws only the visible window. The source text is never shaped on-watch.
Button/swipe steps move immediately. Screen mode is the default and aligns steps to complete lines with a line of overlap; line mode advances by the current line height. Dragging updates position directly. No perpetual redraw timer or network service is used.

FR970 physical-button hit regions, touchscreen drag, menu mapping and size selection
have been exercised. Drag lifecycle uses the documented start/stop event types; the tap
callback is `onTap`. Rapid input edge cases remain under test. The older animation timer has been removed from reader movement.

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

Text color is fixed warm white. System brightness is left to Garmin. ReaderLayout filters instruction-flagged lines and explicitly mapped Shema paragraphs 2/3 according to saved preferences, compacting their spacing. Source resources stay bundled. Edot's separate closing repetition belongs to the same Shema toggle. Conditional prayer and source-small prayer text remain visible. Saved positions include the visibility settings; older positions migrate by word anchor. Hiding the current passage continues at the next visible passage.
