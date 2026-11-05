"""Compile using an installed, official Garmin SDK; never report a host proof as a build."""
import argparse
import os
import shutil
import subprocess
from pathlib import Path

from tools.content import ROOT
from tools.generate import generate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', required=True, choices=['fr970', 'venu2'])
    parser.add_argument('--key', type=Path, required=True, help='Local developer DER key; never commit it')
    parser.add_argument('--release', action='store_true', help='Requires all three verified texts')
    parser.add_argument('--tests', action='store_true', help='Compile native CIQ unit tests')
    args = parser.parse_args()
    sdk = os.environ.get('CONNECTIQ_HOME')
    compiler = str(Path(sdk) / 'bin/monkeyc') if sdk else shutil.which('monkeyc')
    if not compiler or not Path(compiler).is_file():
        parser.exit(2, 'Official Connect IQ SDK missing. Install it and both device packages; set CONNECTIQ_HOME or PATH.\n')
    if not args.key.is_file():
        parser.exit(2, 'Developer signing key not found. See docs/INSTALL.md.\n')
    generate(ROOT / 'generated', args.release)
    directory = ROOT / 'build'
    directory.mkdir(exist_ok=True)
    stem = args.device + ('.tests' if args.tests else '.prototype' if not args.release else '')
    pending = directory / f'{stem}.pending.prg'
    pending.unlink(missing_ok=True)
    command = [compiler, '-f', 'monkey.jungle', '-d', args.device, '-y', str(args.key.resolve()), '-o', str(pending), '-w']
    if args.tests:
        command += ['-t']
    subprocess.run(command, cwd=ROOT, check=True)
    if not pending.is_file():
        raise RuntimeError('Compiler did not produce a fresh PRG')
    final = directory / f'{stem}.prg'
    pending.replace(final)
    print(final)


if __name__ == '__main__':
    main()
