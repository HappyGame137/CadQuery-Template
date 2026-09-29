# CadQuery 设计项目模板（Windows）

参考 CPTMagnetometerPhysicalComponent 的目录组织：建模入口保留在根目录，零件、装配、验证报告和运行日志分别存放。直接用 VS Code 打开项目文件夹。

## 项目目录

```text
CadQuery-Template/
├─ model.py                  参数化几何；必须保留 build()
├─ preview.py                保存后刷新预览，默认端口 3939
├─ export.py                 导出 STEP / STL 并验证
├─ Initialize.cmd            Windows 双击初始化入口
├─ setup_project.py          创建项目独立的 Python 环境
├─ requirements-lock.txt     固定依赖版本
├─ AGENTS.md                 AI 编辑约定
├─ README.md
├─ .gitignore
├─ .vscode/                  文件夹级 VS Code 配置
│  ├─ extensions.json
│  ├─ settings.json
│  ├─ launch.json
│  └─ tasks.json
├─ exports/
│  ├─ parts/                 独立零件 STEP / STL
│  ├─ assemblies/            可选装配 STEP / STL
│  └─ reports/               validation.json
├─ logs/                     preview.log 及轮转日志
└─ .venv/                    初始化后生成，不随模板分发
```

空目录通过 `.gitkeep` 保留。生成的导出文件、报告、日志和虚拟环境默认不进入 Git；需要交付时可单独打包 `exports/`。

## 从模板新建项目

1. 复制源文件及 `.vscode`、`exports`、`logs` 中的 `.gitkeep`，将文件夹改为新项目名称。不要复制 `.git`、`.venv`、`.venv-old`、`__pycache__` 或已有导出和日志。
2. 安装 Python 3.12 x64（含 Python Launcher）、VS Code，以及 `.vscode/extensions.json` 推荐的 Python、Python Debugger、Pylance、OCP CAD Viewer 扩展。
3. 在新项目中双击 `Initialize.cmd`，或在终端执行：

   ```powershell
   py -3.12 setup_project.py
   ```

   初始化会在本项目创建 `.venv`、安装锁定依赖、检查依赖和示例模型、补齐输出目录。不会向全局 Python 安装依赖；重复运行会复用已有环境。
4. 在 VS Code 选择“文件 → 打开文件夹”，选择新项目的根目录。也可以在项目终端运行 `code .`。确认信任提示中的路径后再信任。
5. 执行 `Python: Select Interpreter`，选择 `.venv\Scripts\python.exe`。项目已设置该默认路径，无需手动激活环境或修改 PowerShell 执行策略。

## 日常建模与预览

1. 打开项目文件夹，执行 `OCP CAD Viewer: Open viewer`；已有查看器时直接使用。
2. 按 `Ctrl+F5` 启动 `CAD: Live preview`，或从“终端 → 运行任务”启动同名任务。两种方式选择一种，每个项目仅运行一个监听进程。
3. 修改并保存 `model.py`。预览自动重建，尽量保留相机角度；AI 在外部保存文件也会触发刷新。
4. 设计确认后按 `Ctrl+Shift+B` 导出。
5. 在预览终端按 `Ctrl+C` 停止监听。

预览只监听 `model.py`。零件函数和装配函数也放在此文件；拆分模块前需要扩展依赖监听与重载逻辑。预览错误记录在终端及 `logs/preview.log`，修正并保存后重试。日志达到约 2 MB 时轮转，最多保留两份备份。预览不会自动导出。

默认示例保持为 60 × 40 × 8 mm 圆角安装板，中心孔 Ø10，四个安装孔 Ø4.5，`build()` 返回 CadQuery Workplane。示例用于验证流程，不代表制造校核完成。

## 零件与装配接口

只有 `build()` 时，导出脚本将其作为单实体零件，生成 `exports/parts/model.step` 和 `model.stl`。可在 `model.py` 设置 `MODEL_NAME` 修改零件文件名和预览标签。

多零件项目可在同一个 `model.py` 中添加以下接口：

```python
MODEL_NAME = "mounting_plate"
ASSEMBLY_NAME = "mounting_assembly"


def build_parts():
    # 每个值必须是包含一个有效实体的 Workplane 或 Shape。
    # 独立零件使用自身坐标，装配位置在 build_assembly() 中设置。
    return {"mounting_plate": build_plate(), "spacer": build_spacer()}


def build_assembly():
    assembly = cq.Assembly(name=ASSEMBLY_NAME)
    assembly.add(build_plate(), name="mounting_plate")
    assembly.add(build_spacer(), name="spacer", loc=cq.Location(cq.Vector(0, 0, 8)))
    return assembly


def build():
    return cq.Workplane("XY").newObject([build_assembly().toCompound()])
```

这是接口示意，需自行实现 `build_plate()` 和 `build_spacer()`。始终保留 `build()`，并让它与 `build_assembly()` 表示同一模型。导出脚本使用 `build_parts()` 的字典键命名各零件，名称应在 Windows 下唯一、可作为文件名，支持中文。

存在 `build_assembly()` 时，预览显示装配，导出同时生成 `exports/assemblies/<ASSEMBLY_NAME>.step` 和 `.stl`；未指定装配名称时使用 `assembly`。STEP 保留零件名称、颜色和位置，STL 仅保留网格几何。单零件模板默认不生成重复的装配文件。

## 导出与验证

在项目根目录运行，或按 `Ctrl+Shift+B`：

```powershell
.\.venv\Scripts\python.exe export.py
```

验证报告位于 `exports/reports/validation.json`，包含单位、文件相对路径、实体数、包围盒尺寸、体积、STEP 回读结果和 STL 三角形数量。

导出会检查有效实体、独立零件的单实体约束、STEP 回读实体数量与体积，以及二进制 STL 的长度和三角形数量。导出过程出错会记录 `valid: false` 并以失败状态退出。上述检查不等同于制造校核或 STL 完整网格质量检查；多零件项目需按实际设计增加装配干涉检查。

每次确认几何修改后重新导出。同名输出会覆盖，已改名或移除的零件旧文件不会自动删除；本次有效输出以成功报告列出的路径为准。

## 常见问题

- **找不到 `py` 或 Python 3.12**：安装 Python 3.12 x64 及 Python Launcher。
- **依赖下载失败**：检查网络后重新运行初始化，不必删除项目。
- **找不到 `cadquery` / `ocp_vscode`**：确认初始化成功并选中当前项目的解释器。必要时执行 `Developer: Reload Window`。
- **保存后不刷新**：查看预览终端和 `logs/preview.log`，确认监听仍运行且修改的是当前项目的 `model.py`。
- **连接不到查看器**：先打开查看器，确认它显示的端口。默认使用 3939；需要其他端口时，在 `.vscode/launch.json` 添加 `"args": ["--port", "3940"]`，任务启动方式则在 `.vscode/tasks.json` 的预览参数中添加相同选项。不要无意间启动第二个查看器。
- **项目搬家后环境失效**：停止预览，将旧 `.venv` 改名为 `.venv-old`，在新位置重新初始化；虚拟环境不应直接搬移复用。

## AI 编辑约定

可以直接说明：“修改 model.py 的板厚为 6 mm，保留 build()，让现有预览自动更新，完成后重新导出并检查报告。”

所有尺寸使用毫米，关键尺寸应定义为命名参数。具体建模和目录约定见 `AGENTS.md`。Python 依赖版本以 `requirements-lock.txt` 为准。
