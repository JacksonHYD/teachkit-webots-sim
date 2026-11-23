import argparse
from pathlib import Path
import re
import shutil
from zipfile import ZIP_DEFLATED, ZipFile

from labs import LABS


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def exclude(path, names):
    return {name for name in names
            if name in ('__pycache__', '.git') or name.endswith(('.pyc', '.pyo', '.wbproj'))
            or (Path(path).name == 'msys64' and name == 'tmp')}


def build(stage, python_home, webots_home, webots_license, template):
    if stage.exists():
        raise FileExistsError(f'Use a fresh staging path: {stage}')
    stage.mkdir(parents=True)
    kit = stage / 'kit'
    runtime = stage / 'runtime'
    tools = stage / 'tools'
    docs = stage / '资料'
    tools.mkdir()
    docs.mkdir()
    for part in ('controllers', 'protos', 'worlds'):
        shutil.copytree(PROJECT / 'kit' / part, kit / part, ignore=exclude)
    (kit / 'shared').mkdir()
    shutil.copy2(PROJECT / 'kit' / 'shared' / 'eye2arm.json', kit / 'shared')
    assert {path.name for path in (kit / 'worlds').glob('*.wbt')} == {lab[2] for lab in LABS}

    for world in (kit / 'worlds').glob('*.wbt'):
        text = world.read_text(encoding='utf-8')
        for controller in re.findall(r'\bcontroller\s+"([^"]+)"', text):
            controller_dir = kit / 'controllers' / controller
            assert (controller_dir / (controller + '.py')).is_file(), controller
    for asset in [*kit.joinpath('worlds').glob('*.wbt'), *kit.joinpath('protos').rglob('*.proto')]:
        contents = asset.read_text(encoding='utf-8-sig')
        for external in re.findall(r'EXTERNPROTO\s+"([^"]+)"', contents):
            assert (asset.parent / external).is_file(), (asset, external)

    for script in (kit / 'controllers').glob('*/*.py'):
        if script.stem == script.parent.name:
            script.with_name('runtime.ini').write_text(
                '[python]\nCOMMAND = $(ROBO_KIT_PYTHON)\n', encoding='ascii')

    for directory in ('DLLs', 'Lib', 'tcl'):
        shutil.copytree(python_home / directory, runtime / 'python' / directory, ignore=exclude)
    for asset in [*python_home.glob('*.dll'), *python_home.glob('python*.exe'),
                  python_home / 'LICENSE.txt', python_home / 'NEWS.txt']:
        shutil.copy2(asset, runtime / 'python')
    assert (webots_home / 'resources' / 'version.txt').read_text().strip() == 'R2023b'
    for directory in ('include', 'lib', 'msys64', 'projects', 'resources', 'scripts', 'src'):
        shutil.copytree(webots_home / directory, runtime / 'webots' / directory, ignore=exclude)
    shutil.copy2(webots_license, runtime / 'webots' / 'LICENSE.txt')

    for filename in ('launch.py', 'labs.py'):
        shutil.copy2(HERE / filename, tools)
    (stage / '开始实验.cmd').write_bytes((HERE / 'start.cmd').read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
    (stage / '使用说明.txt').write_text((HERE / 'guide.txt').read_text(encoding='utf-8'), encoding='utf-8-sig')
    (docs / '软件来源.txt').write_text((HERE / 'sources.txt').read_text(encoding='utf-8'), encoding='utf-8-sig')
    shutil.copy2(PROJECT / 'manual.pdf', docs / '实验指导书-仿真设计篇.pdf')
    shutil.copy2(template, docs / '实验报告模板.docx')
    for label in ('实验二（实验十）', '实验三（实验十一）'):
        reference = PROJECT / (label + '实验报告.docx')
        shutil.copy2(reference, docs / (label + '参考报告.docx'))


def archive(stage, output):
    partial = output.with_suffix('.zip.part')
    with ZipFile(partial, 'w', ZIP_DEFLATED, compresslevel=4) as bundle:
        for path in sorted(stage.rglob('*')):
            if path.is_file() and path.relative_to(stage).parts[0] not in ('logs', 'screenshots'):
                bundle.write(path, (Path('RoboKit_Labs') / path.relative_to(stage)).as_posix())
    with ZipFile(partial) as bundle:
        damaged = bundle.testzip()
        if damaged:
            raise OSError(f'Damaged archive member: {damaged}')
    partial.replace(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    parser.add_argument('--python', required=True, type=Path)
    parser.add_argument('--webots', required=True, type=Path)
    parser.add_argument('--webots-license', required=True, type=Path)
    parser.add_argument('--template', required=True, type=Path)
    parser.add_argument('--zip', required=True, type=Path)
    args = parser.parse_args()
    build(args.stage, args.python, args.webots, args.webots_license, args.template)
    archive(args.stage, args.zip)
    print(f'{args.zip}: {args.zip.stat().st_size:,} bytes')
