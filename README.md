# CadQuery 设计项目模板（Windows）

把整个模板复制到你想要的目录，双击初始化，即可开始设计。模板不包含虚拟环境，每个新项目都会建立自己的 `.venv`，不会向全局 Python 安装依赖。

## 第一次：用模板新建项目

### 1. 复制并命名

复制整个 `CadQuery-Template` 文件夹到目标位置，然后改成项目名称，例如：

```text
D:\机械设计\气室支架
```

请复制整个文件夹，保留其中的 `.vscode` 文件夹。不要把自己的设计直接写在模板原件里。

### 2. 双击 Initialize.cmd

在新项目文件夹中双击 `Initialize.cmd`。

它会调用本机 Python 3.12，在此项目建立 `.venv`，安装已固定版本的 CadQuery 和 OCP 预览依赖，并检查测试模型。第一次需要联网，通常需要几分钟。看到 `Setup complete` 即表示成功；出错时窗口会保留错误信息。

同一项目通常只需初始化一次。重复运行会复用已有环境，并按照锁定版本检查或安装依赖。

如果更喜欢命令行，在新项目文件夹的终端运行：

```powershell
py -3.12 setup_project.py
```

### 3. 打开项目

双击 `Design.code-workspace`，用 VS Code 打开。你可以将它改名为 `气室支架.code-workspace`，无需修改里面的内容。

首次出现工作区信任提示时，确认路径是自己创建的项目，再信任它。

本机已安装所需 VS Code 扩展：Python、Python Debugger、Pylance、OCP CAD Viewer。换电脑时需要先安装 Python 3.12（含 Python Launcher）、VS Code，以及这些扩展；模板不会安装这些系统软件。固定依赖面向 Windows x64 / Python 3.12。

### 4. 选择项目解释器

打开 `model.py`，按 `Ctrl+Shift+P`，执行 `Python: Select Interpreter`，选择当前项目下的：

```text
.venv\Scripts\python.exe
```

项目已提供默认解释器设置。若列表里没有该环境，选择输入解释器路径并找到这个文件。

### 5. 开启实时预览

按 `Ctrl+Shift+P`，执行 `OCP CAD Viewer: Open viewer`，打开三维查看器；如果查看器已自动出现，则跳过此步。

按 `Ctrl+F5`，运行 `CAD: Live preview`。每次工作会话启动一次即可，不要重复启动。

修改 `model.py` 顶部的尺寸并保存。模型会自动重建，包括 Codex/Claude 在外部保存文件的情况。鼠标可在查看器中旋转、缩放模型；更新时尽量保留观察角度。

首次启动会加载几何内核，后续改动复用常驻进程。更新速度取决于模型复杂度，不是逐帧连续求解。

## 平常怎么使用

1. 打开这个设计自己的 workspace 文件。
2. 打开查看器，按 `Ctrl+F5` 启动预览。
3. 自己或让 AI 编辑 `model.py`，保存后查看变化。
4. 满意后按 `Ctrl+Shift+B` 导出。
5. 停止预览时，在对应预览终端按 `Ctrl+C`。重新打开 VS Code 后重新启动预览。

不需要再次初始化，也不需要手动激活虚拟环境或修改 PowerShell 执行策略。

## 如何让 AI 帮你设计

在这个项目的 AI 对话中说明要修改 `model.py`，例如：

> 请修改当前项目的 model.py：把板厚改为 6 mm，中心孔改为直径 12 mm，保留四个安装孔。保留 build() 接口，保存文件，让已有预览自动更新。

所有长度默认使用毫米。复杂结构可分几次描述，先看大致形状，再逐步补充孔位、圆角、壁厚。位置说不清时，可提供带标记的截图。

`AGENTS.md` 提供给支持该文件的 AI 编程工具。无论使用什么 AI，实际被保存的文件都需要位于当前项目中。

## 导出 STEP / STL

按 `Ctrl+Shift+B` 执行 `CAD: Export STEP and STL`，或从“终端 → 运行任务”中选择同名任务。导出文件位于：

```text
exports/
  model.step       供 CAD 软件交换使用
  model.stl        供切片/3D 打印使用
  validation.json 导出验证结果
```

预览不会自动导出。每次确认设计后重新导出，避免使用旧文件。导出脚本默认检查单一实体、STEP 回读体积及 STL 文件结构；若以后设计多零件装配，需要相应调整导出脚本。

## 文件结构

| 文件 | 用途 |
|---|---|
| `model.py` | 设计源文件；尺寸参数和 `build()` 建模函数 |
| `preview.py` | 监听保存并更新预览 |
| `export.py` | 导出及基础有效性检查 |
| `Initialize.cmd` / `setup_project.py` | 双击初始化入口和环境安装程序 |
| `requirements-lock.txt` | 已验证的 Python 依赖版本 |
| `Design.code-workspace` | VS Code 项目入口，可重命名 |
| `.vscode/` | 解释器、预览、导出任务配置 |
| `AGENTS.md` | AI 项目约定 |
| `.venv/` | 初始化后生成的隔离环境，不作为模板复制 |
| `exports/` | 导出时生成的结果 |

模板示例为 60 × 40 × 8 mm 圆角板，中心孔 Ø10，四个安装孔 Ø4.5。它用于试运行，不代表已经完成工程设计或制造校核。

## 常见问题

**提示找不到 py 或 Python 3.12**：先安装含 Python Launcher 的 Python 3.12 x64。此电脑已经具备。

**依赖下载失败**：检查网络，再次双击初始化即可。不会自动删除已有项目文件。

**找不到 cadquery / ocp_vscode**：先确认初始化成功，再选择当前项目的 `.venv` 解释器。若 VS Code 在安装完成前已打开，执行 `Developer: Reload Window` 刷新扩展状态。

**保存后不更新**：确认预览进程仍在运行，修改的是当前项目的 `model.py`，并查看终端错误。修正错误后保存重试；必要时停止并重新启动预览。当前仅监听 `model.py`；若拆成多个模块，需要扩展监听和模块重载逻辑。

**连接不到查看器**：先打开 OCP 查看器，再启动预览。默认端口为 3939。如果同时打开多个 CAD 项目，查看器可能使用 3940 等其他端口；可在 `.vscode/launch.json` 的预览配置里增加 `"args": ["--port", "3940"]`，填写状态栏显示的实际端口。通过任务启动时，相应修改 `.vscode/tasks.json` 中预览任务的参数。初学时建议一次打开一个 CAD 项目。

**文件夹搬家后无法运行**：关闭预览和 VS Code，将旧 `.venv` 改名为 `.venv-old`，在新位置重新初始化。验证成功后可自行删除旧环境；不要把旧虚拟环境直接当作可搬移文件使用。

**分享项目或再做模板**：复制源文件和配置，排除 `.venv`、`.venv-old`、`__pycache__`。别人可在自己的目录重新初始化。

## 版本与参考

基于 2026-09-29 本机验证的 Python 3.12.10、CadQuery 2.8.0、OCP CAD Viewer 4.1.0；全部 Python 依赖版本见 `requirements-lock.txt`。

- [CadQuery 官方安装文档](https://cadquery.readthedocs.io/en/latest/installation.html)
- [OCP CAD Viewer 官方项目](https://github.com/bernhard-42/vscode-ocp-cad-viewer)
