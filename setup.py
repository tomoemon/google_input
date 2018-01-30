# -*- coding: utf-8 -*-
import os
from os import path
import sys
from setuptools import setup
from setuptools import Command


class InitVsCode(Command):
    """VSCode のワークスペース設定に virtualenv の Python executable を設定する

    ワークスペース設定（./.vscode/settings.json）に対して、下記のキーを設定する
        "python.pythonPath": "$PYTHON_EXECUTABLE"

    $PYTHON_EXECUTABLE は pipenv が作成した python executable のパス
    """
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _python_path(self):
        import subprocess
        venv_dir = subprocess.check_output("pipenv --venv").decode(sys.getdefaultencoding()).strip()
        return path.join(venv_dir, "Scripts", "python").replace('\\', '/')

    def run(self):
        import json

        curdir = path.abspath(path.dirname(__file__))
        os.chdir(curdir)

        settings_dir = path.join(curdir, ".vscode")
        settings_path = path.join(settings_dir, "settings.json")

        os.makedirs(settings_dir, exist_ok=True)
        values = {}
        if path.isfile(settings_path):
            with open(settings_path) as fp:
                values = json.load(fp)

        values["python.pythonPath"] = self._python_path()
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
