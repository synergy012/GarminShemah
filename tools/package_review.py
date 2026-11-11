"""Package the existing FR970 review build for direct GitHub download."""
import hashlib
import subprocess
import zipfile
from pathlib import Path

from tools.content import ROOT


def main():
    binary = ROOT / 'build/fr970.review.prg'
    data = binary.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # Packaging follows the source commit, so the bundled commit is reproducible.
    readme = f'''Garmin Bedtime Shema — FR970 REVIEW COPY

Source commit: {source}
Forerunner 970 only. Extract fr970.review.prg before copying it to GARMIN/APPS
using Garmin's supported USB/file-transfer method. Safely disconnect afterward.
To update an existing installation, close the app first and use the same transfer
process. The installed app uses the same application ID and development key.

Use left-side UP/DOWN to scroll. Bottom-right BACK saves your place and exits
immediately. Top-right START does not scroll; it selects items inside menus.
Hold the middle-left UP/MENU button while reading to open settings.
Scrolling: By screen (default, immediate steps with a line of overlap) / By line.
Instructions: Hidden (default) / Shown.
Shema paragraphs 2 + 3: Shown (default) / Hidden.
All three nuschaos and font sizes remain available. Settings are saved.
Selections stay in settings; press BACK to return. Font/nusach submenus remain
open after selection; BACK returns to the main settings menu, then to reading.
Return to beginning closes settings and opens the document at its start.
Brightness offers System, 10%, 25%, 50%, or 100%; Garmin retains display timeout
and protection. The selected level is applied on reader entry and selection.
The left-side progress arc fills as you move through the selected document.
Prayer text in small print and conditional prayer passages remain included when
instructions are hidden. Source text is retained; visibility changes only reading.

Development-signed review build, pending editorial approval; not a store release.
The selected Edot source abbreviates Yoshev Beseter. No missing verses were filled
from another edition. Physical-watch update acceptance remains to be checked.

Display changes: markup parsed, whitespace collapsed, instructions separated and
labelled; reader settings can hide instructions or Shema paragraphs 2 and 3.
Divine Names are displayed as ה׳ (he followed by Hebrew geresh); attached
prefixes and other wording/pointing are retained. Original source records remain
unchanged in the repository. See DIVINE-NAMES.md for the substitution audit.
See TEXT-NOTICES.md and the included font licenses. Offline source attribution is
also available through the app's Text sources setting.

Repository: https://github.com/synergy012/GarminShemah
'''
    target = ROOT / 'downloads/fr970-review.zip'
    target.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('fr970.review.prg', data)
        archive.writestr('README.txt', readme)
        archive.writestr('SHA256SUMS', checksum + '  fr970.review.prg\n')
        for name, dest in [('content/acquired/NOTICE.md', 'TEXT-NOTICES.md'), ('docs/DIVINE-NAMES.md', 'DIVINE-NAMES.md'), ('fonts/OFL.txt', 'fonts/OFL.txt'),
                           ('fonts/README.md', 'fonts/README.md'), ('fonts/DEBIAN-COPYRIGHT', 'fonts/DEBIAN-COPYRIGHT')]:
            archive.write(ROOT / name, dest)
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() or hashlib.sha256(archive.read('fr970.review.prg')).hexdigest() != checksum:
            raise RuntimeError('Review package failed verification')
    print(f'{target}: {target.stat().st_size} bytes; PRG SHA-256 {checksum}')


if __name__ == '__main__':
    main()
