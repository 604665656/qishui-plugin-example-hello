# -*- coding: utf-8 -*-
"""示例插件的**独立形态**入口：`python -m hello` 或打成 独立的 exe。

独立运行时它自己造 ctx（自带定时器、自己取当前账号），
跟被宿主加载时跑的是**同一份 plugin.py**，一行没改。
"""
import sys

from qishui_core import standalone as SA

from .plugin import HelloPlugin


def main():
    return SA.run_plugin_window(HelloPlugin, "example-hello",
                                argv=sys.argv, size=(820, 560))


if __name__ == "__main__":
    sys.exit(main())
