# 一念小沙弥 v1.0.3

一个安静待在桌面的陪伴型小沙弥。它会用偈语、观息、钟声和“记一念”，帮你轻轻回到当下。

## 下载

- macOS：下载 `mindful-monk-macos-*.zip`，解压后打开“一念小沙弥.app”。当前为临时签名、未经 Apple 公证；若系统拦截，请右键应用并选择“打开”。
- Windows：下载 `mindful-monk-windows-x64.zip`，解压后运行 `Mindful-Monk.exe`。

> **Windows 版本尚未经过实际使用测试，可能存在兼容性问题或 bug。欢迎通过 GitHub Issues 反馈。**

## 主要功能

- 桌面常驻小沙弥与四组动作动画
- 144 条偈语，包括 110 条《杂阿含经》《金刚般若波罗蜜经》节录
- 一分钟观息、轻柔钟声、随机与定时提醒
- “记一念”与“看念迹”：状态、文字、近期回看和简单统计
- 自定义偈语、静默时段、大小与动画速度设置
- 数据仅保存在本机

## 本次改进

- 修复“唤钟一下”播放成功但钟声过轻、几乎听不见的问题
- 修复自动偈语提示导致当前绘图、写作或编辑应用失去前台焦点的问题
- 修复偈语去重池耗尽后可能跳出已选类别的问题
- 记录、设置或自定义偈语文件损坏时保留 `.broken*.json` 原始备份
- 修复连续气泡可能被上一条计时器提前关闭的问题
- 删除念迹或自定义偈语前增加确认
- 增加 Windows、macOS、Linux 三系统持续集成与依赖更新检查

---

# Mindful Monk v1.0.3

A quiet desktop companion that uses short reflections, breathing, a gentle bell,
and mindful notes to help you return to the present moment.

> **The Windows build has not been tested in day-to-day use. It may contain
> compatibility issues or bugs. Feedback through GitHub Issues is very welcome.**

The macOS build is ad-hoc signed and not Apple-notarized. If Gatekeeper blocks
it, right-click the app and choose **Open**.

## Improvements in this release

- Fix the bell sound being technically played but almost inaudible
- Prevent automatic reflections from taking focus away from drawing, writing, or editing apps
- Keep reflection category filters intact when the recent-item pool is exhausted
- Preserve broken settings, notes, and custom reflections as `.broken*.json` backups
- Prevent an older message timer from hiding a newer message
- Confirm before deleting thought traces or custom reflections
- Add CI across Windows, macOS, and Linux, plus dependency update monitoring
