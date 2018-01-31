# -*- coding: utf-8 -*-
import os
from pathlib import Path
import sys
from setuptools import setup
from setuptools import Command


class InitVsCode(Command):
    """VSCode のワークスペース設定に virtualenv の Python executable を設定する

    ワークスペース設定（./.vscode/settings.json）に対して、下記のキーを設定する
        "python.pythonPath": "$PYTHON_EXECUTABLE"

    $PYTHON_EXECUTABLE は pipenv が作成した python executable のパス
    """
    user_options: list = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _python_path(self):
        import subprocess
        venv_dir = subprocess.check_output("pipenv --venv").decode(sys.getdefaultencoding()).strip()
        return Path(venv_dir, "Scripts", "python")

    def run(self):
        import json

        curdir = Path(__file__).resolve().parent
        os.chdir(curdir)

        settings_dir = curdir / ".vscode"
        settings_path = settings_dir / "settings.json"

        settings_dir.mkdir(parents=True, exist_ok=True)
        values = {}
        if settings_path.is_file():
            with open(settings_path) as fp:
                values = json.load(fp)

        values["python.pythonPath"] = self._python_path().as_posix()
        with open(settings_path, "w", encoding="utf-8", newline="\n") as fp:
            json.dump(values, fp, indent=4)


setup(
    name="google_input",
    version="0.1",
    author='tomoemon',
    packages={'google_input': 'google_input'},
    package_data={'google_input': ['data/*.txt']},
    cmdclass={"vscode": InitVsCode}


)
