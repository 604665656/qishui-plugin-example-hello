# -*- coding: utf-8 -*-
"""build_exe.py —— 把「示例插件」插件打成**能独立运行的 EXE**

    python build_exe.py            # 单文件
    python build_exe.py --onedir   # 目录版（热更新用这个）

同一份 `hello/plugin.py`，宿主加载和独立运行都在跑它。
这里的 EXE 只是"自带 ctx 的启动器"——见 `qishui_core.standalone`。
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "示例插件"
ENTRY = os.path.join(HERE, "hello", "__main__.py")
CORE = os.path.abspath(os.path.join(HERE, "..", "..", "core"))

HIDDEN = [
    "qishui_core.api", "qishui_core.auth", "qishui_core.store",
    "qishui_core.paths", "qishui_core.context", "qishui_core.standalone",
    "qishui_core.cdp_lite", "qishui_core.updater", "qishui_core.schedule",
]


def main(argv):
    onedir = "--onedir" in argv
    if "--clean" in argv:
        for d in ("build", "dist"):
            shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
        print("已清理 build/dist")

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed",
           "--name", NAME]
    cmd += (["--onedir"] if onedir else ["--onefile"])
    for h in HIDDEN:
        cmd += ["--hidden-import", h]
    if os.path.isdir(CORE):
        cmd += ["--paths", CORE]
    cmd += ["--distpath", os.path.join(HERE, "dist"),
            "--workpath", os.path.join(HERE, "build"),
            ENTRY]
    print(" ".join(cmd))
    rc = subprocess.call(cmd, cwd=HERE)
    if rc == 0:
        print("\n完成：%s" % os.path.join(HERE, "dist", NAME))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
