import subprocess
from pathlib import Path


def run(cmd):
    subprocess.run(cmd, check=True)


build_folder = Path("build_tools").resolve()

pyinstaller_folder = build_folder / "PYINSTALLER"
pyinstaller_folder.mkdir(exist_ok=True, parents=True)

spec_file = build_folder / "inkpull-win.spec"

run([
    "python", "-m", "PyInstaller",
    "-y",
    "--workpath", str(pyinstaller_folder / "build"),
    "--distpath", str(pyinstaller_folder / "dist"),
    str(spec_file)
])
