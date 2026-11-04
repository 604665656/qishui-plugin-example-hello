# qishui-plugin-example-hello

写新插件时**直接拿它当模板改**。它是一份能跑的最小实现，把该会的东西都演示了一遍，
每样都只有几行。

## 复制它

```bash
cp -r qishui-plugin-example-hello qishui-plugin-mything
cd qishui-plugin-mything
mv hello mything
```

然后改三处：

1. `plugin.json` —— `id` / `name` / `entry` / `tab`
2. `mything/plugin.py` 的类名（`HelloPlugin` → `MyThingPlugin`）
3. `mything/__main__.py` 里的 pid 和类名

跑起来：

```bash
python -m qishui_host.main --install .
python -m qishui_host.main --list
```

## 它演示了什么

| 演示点 | 代码在哪 |
|---|---|
| 返回一个 `QWidget` 变成页签 | `build(ctx)` |
| **无界面**初始化（计划任务只有这一步） | `setup(ctx)` |
| 读当前账号 | `ctx.uid` / `ctx.account()` |
| 插件私有数据（跨账号） | `ctx.store.load_json/save_json` |
| 账号级数据（跟着账号走） | `ctx.account_path()` |
| 调后台接口 + 失败降级 | `ctx.api.can_create()` + `try/except` |
| 注册每日任务 | `ctx.schedule.daily(fn, "07:30")` |
| 写行式日志（自动控体积） | `ctx.store.append_jsonl(..., keep_days=30)` |
| 响应账号切换 | `ctx.on_account_switch(cb)` |
| 弹提示 / 打开文件 | `ctx.notify()` / `ctx.open_path()` |
| 独立运行 | `hello/__main__.py` |

## 不要做的三件事

```python
# ✗ 不要 import 宿主
from qishui_host import plugin_host       # 违规

# ✗ 不要自己拼账号路径
p = os.path.join("accounts", uid, "x.json")   # 违规，换号必串

# ✓ 只能这样
p = ctx.account_path("x.json")
```

这三条不是洁癖。第一条会导致"宿主一改插件全崩"，第三条会导致"换号串数据"——
后者更危险，因为数据看起来是对的。

## 两种形态，一份代码

```bash
# 形态一：被宿主加载
python -m qishui_host.main --install .

# 形态二：自己就是主程序
pip install -e ../../core
python -m hello
```

`plugin.py` 一行都不用改。差别只在"谁来构造 ctx"：

- 宿主形态 → `host.context(pid)`，共享定时器、共享账号栏、有真实弹窗
- 独立形态 → `qishui_core.standalone.make_ctx(pid)`，自带定时器

## 打包

```bash
pyinstaller --noconfirm --windowed --name 示例插件 hello/__main__.py
```

## 许可

MIT。
