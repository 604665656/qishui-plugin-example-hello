# -*- coding: utf-8 -*-
"""示例插件 —— 也是写新插件的模板。

它把所有该会的东西都演示了一遍，且都只有几行：
    1. build(ctx) 返回一个 QWidget  → 宿主把它变成页签
    2. 读当前账号（ctx.uid / ctx.account()）
    3. 插件私有数据（ctx.store）
    4. 账号级数据（ctx.account_path）
    5. 调接口（ctx.api）
    6. 注册每日任务（ctx.schedule.daily）
    7. 响应账号切换（ctx.on_account_switch）
    8. 独立运行（同目录 __main__.py）

注意几件"不要做"的事
    · 不要 import 宿主任何模块；你拿不到也不该拿。
    · 不要自己拼 accounts/<uid>/ 路径；用 ctx.account_path()。
    · 不要 assume 浏览器开着；接口调用一律 try/except 并 ctx.warn()。
"""
from __future__ import annotations

import time


class HelloPlugin(object):
    """宿主不要求继承任何基类——方法都按需实现，缺了就是"不响应"。"""

    # ------------------------------------------------ 无界面初始化
    def setup(self, ctx):
        """拿到 ctx 就存下来。**无界面任务（--task）只有这一步**，
        所以只要插件有后台活儿，就必须实现它。"""
        self.ctx = ctx
        ctx.log("setup：uid=%s 端口=%s" % (ctx.uid, ctx.port))

    # ------------------------------------------------ 页签
    def build(self, ctx):
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton,
                                       QVBoxLayout, QWidget)

        self.ctx = ctx
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(10)

        self.lb_uid = QLabel()
        self.lb_uid.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lay.addWidget(self.lb_uid)

        self.lb_data = QLabel()
        self.lb_data.setWordWrap(True)
        self.lb_data.setStyleSheet("color:#5c636e;")
        lay.addWidget(self.lb_data)

        row = QHBoxLayout()
        b1 = QPushButton("点我记一次（写私有数据）")
        b1.clicked.connect(self._bump)
        row.addWidget(b1)
        b2 = QPushButton("调一次接口（余额）")
        b2.clicked.connect(self._api)
        row.addWidget(b2)
        b3 = QPushButton("注册每日 07:30")
        b3.clicked.connect(self._sched)
        row.addWidget(b3)
        row.addStretch(1)
        lay.addLayout(row)
        lay.addStretch(1)

        ctx.on_account_switch(lambda uid: self.refresh())
        self.refresh()
        return w

    # ------------------------------------------------ 展示
    def refresh(self):
        ctx = self.ctx
        acc = ctx.account() or {}
        ctx.api.use_port(ctx.port)
        self.lb_uid.setText("当前账号：<b>%s</b>　端口 %s"
                            % (acc.get("name") or ctx.uid or "（未登录）",
                               ctx.port or "自动"))
        n = (ctx.store.load_json("counter.json", {}) or {}).get("n", 0)
        self.lb_data.setText(
            "私有数据：plugin_data/%s/counter.json → n=%s\n"
            "账号数据目录：%s\n"
            "契约版本：api_version=%s"
            % (ctx.pid, n, ctx.account_dir(), (ctx.meta.api_version
                                               if ctx.meta else "?")))

    # ------------------------------------------------ 动作
    def _bump(self):
        ctx = self.ctx
        d = ctx.store.load_json("counter.json", {}) or {}
        d["n"] = int(d.get("n", 0)) + 1
        d["at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        ctx.store.save_json("counter.json", d)
        ctx.log("记了一次，n=%s" % d["n"])
        self.refresh()

    def _api(self):
        ctx = self.ctx
        try:
            j = ctx.api.can_create()
            ctx.notify("接口通了", "今日剩余可发：%s" % j.get("data", j))
        except Exception as e:
            ctx.warn("接口失败：%s" % e)
            ctx.notify("接口没通", str(e), "warn")
        self.refresh()

    def _sched(self):
        ctx = self.ctx
        ctx.schedule.daily(self._daily_job, "07:30", name="daily",
                           title="示例每日任务")
        ctx.log("已注册每日 07:30")
        ctx.notify("已注册", "每天 07:30 跑一次（宿主开着时生效）")

    # ------------------------------------------------ 定时 / 事件
    def _daily_job(self):
        ctx = self.ctx
        ctx.log("每日任务跑了")
        ctx.store.append_jsonl("daily.jsonl",
                               {"date": time.strftime("%Y-%m-%d"),
                                "at": time.strftime("%Y-%m-%d %H:%M:%S")},
                               keep_days=30)

    def run_task(self):
        """给 `--task example-hello` 用的无界面入口。"""
        self._daily_job()

    def on_account_switch(self, uid):
        try:
            self.refresh()
        except Exception:
            pass

    def on_unload(self):
        try:
            self.ctx.log("卸载收尾")
        except Exception:
            pass

    def summary(self):
        return {"作者": "qishui-toolkit", "用途": "模板"}
