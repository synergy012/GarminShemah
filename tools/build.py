"""Compile using an installed, official Garmin SDK; never report a host proof as a build."""
import argparse
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.content import ROOT
from tools.generate import generate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='fr970', choices=['fr970'])
    parser.add_argument('--key', type=Path, required=True, help='Local developer DER key; never commit it')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--release', action='store_true', help='Requires all three verified texts')
    mode.add_argument('--review', action='store_true', help='Build all three source-mapped prayer documents, visibly marked REVIEW COPY')
    parser.add_argument('--tests', action='store_true', help='Compile native CIQ unit tests')
    parser.add_argument('--sdk-user-home', type=Path,
                        default=Path(os.environ.get('CIQ_RUNTIME_STATE', '/workspace/.toolchains/garmin/runtime/state')),
                        help='User home containing .Garmin/ConnectIQ/Devices (existing normal SDK home is used if target is absent here)')
    args = parser.parse_args()
    sdk = os.environ.get('CONNECTIQ_HOME')
    compiler = str(Path(sdk) / 'bin/monkeyc') if sdk else shutil.which('monkeyc')
    if not compiler or not Path(compiler).is_file():
        parser.exit(2, 'Official Connect IQ SDK missing. Install it and both device packages; set CONNECTIQ_HOME or PATH.\n')
    if not args.key.is_file():
        parser.exit(2, 'Developer signing key not found. See docs/INSTALL.md.\n')
    generate(ROOT / 'generated', args.release, review=args.review, reuse=True)
    directory = ROOT / 'build'
    directory.mkdir(exist_ok=True)
    # An SDK without the other device package rejects even unused Jungle
    # qualifiers. Scope generated build metadata, leaving shared sources intact.
    target_dir = directory / 'targets' / args.device
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest = ET.parse(ROOT / 'manifest.xml')
    ET.register_namespace('iq', 'http://www.garmin.com/xml/connectiq')
    products = manifest.find('.//{http://www.garmin.com/xml/connectiq}products')
    for product in list(products):
        if product.get('id') != args.device:
            products.remove(product)
    manifest.write(target_dir / 'manifest.xml', encoding='unicode')
    jungle = target_dir / 'monkey.jungle'
    jungle.write_text('\n'.join([
        f'project.manifest = {target_dir / "manifest.xml"}',
        f'base.sourcePath = {ROOT / "source"};{ROOT / "generated" / args.device}',
        f'base.resourcePath = {ROOT / "resources"};{ROOT / "generated" / args.device / "resources"}',
        '',
    ]))
    stem = args.device + ('.tests' if args.tests else '.review' if args.review else '.prototype' if not args.release else '')
    pending = directory / f'{stem}.pending.prg'
    pending.unlink(missing_ok=True)
    pending_debug = Path(str(pending) + '.debug.xml')
    pending_debug.unlink(missing_ok=True)
    command = [compiler, '-f', str(jungle), '-d', args.device, '-y', str(args.key.resolve()), '-o', str(pending), '-w']
    if args.tests:
        command += ['-t']
    build_env = os.environ.copy()
    if (args.sdk_user_home / '.Garmin/ConnectIQ/Devices' / args.device / 'compiler.json').is_file():
        home_option = '-Duser.home="' + str(args.sdk_user_home.resolve()) + '"'
        build_env['JAVA_TOOL_OPTIONS'] = (build_env.get('JAVA_TOOL_OPTIONS', '') + ' ' + home_option).strip()
    subprocess.run(command, cwd=ROOT, env=build_env, check=True)
    if not pending.is_file():
        raise RuntimeError('Compiler did not produce a fresh PRG')
    final = directory / f'{stem}.prg'
    pending.replace(final)
    if pending_debug.exists():
        pending_debug.replace(Path(str(final) + '.debug.xml'))
    print(final)


if __name__ == '__main__':
    main()
