# Windows 源码运行与构建

在 Windows x64 上使用 Python 3.12。以下命令均从仓库根目录执行。

## 环境

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r FormulaSnip\requirements-lock.txt
.\.venv\Scripts\python.exe download_assets.py
```

`requirements-lock.txt` 是当前发布环境的依赖快照。`requirements.txt` 给出直接依赖的兼容范围，适用于依赖升级；升级后请重新测试。

下载脚本获取 Pix2Text MFR 1.5、MFD 1.5 与 MathJax 3.2.2。模型必须匹配 `FormulaSnip/models/manifest.json` 内的 SHA-256。下载中断可重新执行；校验不符时停止使用并核对上游版本。

## 运行与打包

```powershell
.\.venv\Scripts\python.exe FormulaSnip\main.py
.\build.ps1 -Python .\.venv\Scripts\python.exe -SkipInstall
```

`build.ps1` 下载并检查缺失资源，生成 `dist/FormulaSnip.exe`，中间文件放在 `build/`。程序、模型和运行库均打入 exe，文件较大；无需为已安装的依赖重复传输。

也可以直接运行：

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist --workpath build FormulaSnip\FormulaSnip.spec
```

若电脑的 PowerShell 执行策略限制脚本，可使用上述等价 Python 命令，无需修改全局执行策略。

## 验证

```powershell
.\.venv\Scripts\python.exe validate_core.py
.\.venv\Scripts\python.exe FormulaSnip\main.py --self-test source-self-test-results
Start-Process -FilePath .\dist\FormulaSnip.exe -ArgumentList '--self-test', 'self-test-results' -Wait
```

核心测试覆盖 Word 公式导出、本地资料库、Windows DPAPI、联网接口的模拟请求、取消识别和 LaTeX 整理。程序自检还覆盖 Qt 界面、预览不重复、离线识别、导出与 PDFium。

`--self-test` 使用指定目录中的测试资料库；建议每次用空目录，并查看生成的 `report.json`。它不会使用正常资料库或联网 OCR。核心测试的合成数据写入 `test-results/`。

## 更新依赖、图标与许可证

```powershell
.\.venv\Scripts\python.exe make_icon.py
.\.venv\Scripts\python.exe collect_licenses.py
```

发布仓库已经包含所需的图标、第三方许可证和模型校验清单。修改图标或升级依赖后可重新生成。

`collect_licenses.py` 会重新记录当前模型文件的哈希；它用于维护发布清单，不能替代对新模型来源的审查。Qt / PySide6 组件可以替换后重新构建，发布时须保留其适用许可。

## 发布内容

Git 保存应用源码、构建脚本、模型清单、文档和截图。ONNX 权重、exe、资料库和密钥不进入 Git。将测试通过的 exe、源码压缩包和 SHA-256 清单作为 GitHub Release 附件。
