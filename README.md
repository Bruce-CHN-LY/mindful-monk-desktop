# 一念小沙弥

[English](README_EN.md) | 中文

一个安静待在桌面的陪伴型小沙弥。它不会催促你完成更多，只会偶尔提醒：看见这一念，回到这一口呼吸。

![一念小沙弥与偈语](docs/images/quote-bubble.png)

## 功能

- 桌面常驻、无边框、可拖动的小沙弥
- 四组动作动画：待机、合十、观息与唤钟
- 144 条偈语，其中包括 110 条《杂阿含经》《金刚般若波罗蜜经》节录
- 经典节录保留经名、出处和节录标记，与内置提醒、自定义内容分开存放
- 一分钟观息、轻柔钟声、固定或随机提醒与静默时段
- “记一念”：选择当下状态，也可以补充一句自己的话
- “看念迹”：回看近期记录、简单统计或删除记录
- 自定义偈语、角色缩放、动画速度与点击穿透
- 所有设置和个人记录只保存在本机

![快捷菜单](docs/images/menu.png)
![偈语库](docs/images/quote-library.png)

## 下载

请前往 [最新 Release](https://github.com/Bruce-CHN-LY/mindful-monk-desktop/releases/latest) 下载适合系统的压缩包。

### macOS

下载 `mindful-monk-macos-*.zip`，解压后打开“一念小沙弥.app”。

当前 macOS 包使用临时签名，未经 Apple 公证。若 Gatekeeper 拦截，请右键应用、选择“打开”，再确认一次。

### Windows

下载 `mindful-monk-windows-x64.zip`，解压后运行 `Mindful-Monk.exe`。

> **Windows 版本尚未经过实际使用测试，可能存在兼容性问题或 bug。欢迎通过 [GitHub Issues](https://github.com/Bruce-CHN-LY/mindful-monk-desktop/issues) 反馈。**

## 使用

- 单击小沙弥：打开或收起菜单
- 拖动小沙弥：调整位置
- 双击小沙弥：唤钟并收到一句偈语
- 点击“听一句偈语”：立即得到一句观心提醒
- 点击“记一念”：记录此刻状态与可选文字
- 点击“看念迹”：回看、统计或删除记录
- 菜单栏图标：显示、隐藏、切换点击穿透或退出

“记一念”只为看见，不评价情绪好坏，也不设置连续打卡。

## 从源码运行

需要 Python 3.11、3.12 或 3.13。

```bash
git clone https://github.com/Bruce-CHN-LY/mindful-monk-desktop.git
cd mindful-monk-desktop
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m app.main
```

Windows PowerShell：

```powershell
git clone https://github.com/Bruce-CHN-LY/mindful-monk-desktop.git
cd mindful-monk-desktop
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m app.main
```

## 本地数据

- macOS：`~/Library/Application Support/Mindful Monk/`
- Windows：`%APPDATA%\Mindful Monk\`
- Linux：`$XDG_DATA_HOME/mindful-monk/` 或 `~/.local/share/mindful-monk/`

个人设置、念迹和自定义偈语不会提交到仓库，也不会上传到网络。

## 开发与打包

运行测试：

```bash
.venv/bin/python -m pytest -q
```

构建 macOS：

```bash
./scripts/build_macos.sh
```

构建 Windows：

```powershell
./scripts/build_windows.ps1
```

推送 `v*` 标签时，[GitHub Actions](.github/workflows/release.yml) 会分别在 Windows 与 macOS runner 上测试、打包并创建 Release。

## 内容说明

- 日常偈语：[app/assets/quotes.json](app/assets/quotes.json)
- 经典节录：[app/assets/scripture_quotes.json](app/assets/scripture_quotes.json)
- 自定义偈语：仅位于用户本机数据目录

经典节录用于个人观照与学习提示，不替代完整经文、专业校勘或宗教指导。发现出处或文字需要修订时，欢迎提交 Issue 或 Pull Request。

## 致谢

桌面陪伴物的最初灵感来自 [yumiaura/myCat](https://github.com/yumiaura/myCat)。本项目采用独立实现、不同角色素材与功能设计，详见 [第三方说明](THIRD_PARTY_NOTICES.md)。

## 许可证

本项目以 [MIT License](LICENSE) 开源。
