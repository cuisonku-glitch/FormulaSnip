拾式 FormulaSnip 1.1.0
Windows 10 / 11，64 位

1.1.0 更新
------------
界面重做：紧凑的顶部工具栏和截图视图，默认窗口更小，支持深色模式，会记住窗口大小和位置。
离线识别的 LaTeX 自动整理：去掉多余空格和间距符号，分式外的括号补全 \left \right。
启动后在后台预热公式模型，第一次截图不再等待加载。
新增 $ … $ 行内格式；可在设置中选择自动复制的格式。
导出和复制前自动保存未保存的修改。
升级时先保存修改，再右键系统托盘里的拾式图标，选择“退出”。
打开同一文件夹内的 FormulaSnip-1.1.0.exe（重新构建时文件名为 FormulaSnip.exe）。
保留旁边的 FormulaSnipData 文件夹，历史记录和设置会继续使用。
旧记录不会自动改写；打开记录后点“整理”即可得到整洁的 LaTeX。

运行
----
双击 FormulaSnip-1.1.0.exe（重新构建时为 FormulaSnip.exe）。无需安装 Python、LaTeX、Office 或独立显卡。
离线公式、公式定位和中英文文字模型都已经包含在 exe 中。
这是单文件便携版，首次启动需要解压运行库，可能需要约 10～30 秒。
建议把 exe 放入一个固定、可写的文件夹。不要在启动时重复双击。
程序没有数字签名；下载后的 Windows 提示取决于本机策略。

快速开始
--------
1. 启动后，按 Ctrl + Alt + S，拖动框选屏幕中的公式，松开鼠标开始识别。
2. 识别结果显示在窗口中，并默认自动复制到剪贴板。
3. 核对预览；需要修改时直接编辑右下方的 LaTeX，Ctrl + Enter 保存。
4. 点击需要的格式行即可复制，或使用预览下方的“导出”。
5. ← → 键翻看上一条 / 下一条；Ctrl + L 打开资料库；右下角切换深色 / 浅色。

输入方式
--------
• 截图：Ctrl + Alt + S。Esc 或鼠标右键取消。可在设置中改快捷键。
• 打开窗口：Ctrl + Alt + O。
• 图片导入：导入按钮 / Ctrl + O，可选多张。
• 图片粘贴：在非文本输入区域按 Ctrl + V，或点击“粘贴图片”。
• 图片和 PDF 拖入程序窗口。
• PDF：输入需要识别的页码，如 1-3,5，一次最多 50 页。
• 手写：在手写窗口中写公式，支持撤销、清空和识别。
• 新建公式：直接输入 LaTeX 或文字，也可打开内置编辑示例。

三种离线模式
------------
数学公式：适合一个公式、矩阵或一组多行公式，输出 LaTeX。
中英文文字：适合只有中文、英文的图片，输出文本。
图文混排：定位公式并识别其余文字，输出带公式的 Markdown。
在窗口底部的“公式 / 图文 / 文字”切换。截图请贴近内容，不要包含工具栏和无关区域。

结果与导出
----------
• 原图 / 识别预览 / 左右对照，预览可缩放。
• LaTeX 原文、$ … $、$$ … $$、\[ … \]、equation 环境，点击即可复制。
• “整理”把带空格的 LaTeX 改写为紧凑写法，含义不变；可在设置中关闭自动整理。
• LaTeX / Markdown / MathML 源文件。
• PNG / SVG 公式图像，或直接复制公式图片。
• DOCX：数学公式以 Word 的可编辑 OMML 公式保存，无需安装 Word 才能导出。
• “复制到 Word”复制 MathML，可粘贴到 Word 等支持 MathML 的编辑器；粘贴不成功时请导出 DOCX。
• 原始图片导出。
• 历史资料库支持搜索、收藏、删除和 ZIP 备份。

联网识别（可选）
----------------
默认完全离线，不上传图片。设置中可主动选择：
1. Mathpix OCR API：需要自己的 App ID 和 API Key。
   Mathpix Snip 的订阅与 OCR API 额度是独立的。
2. 兼容 Chat Completions 的视觉接口：填写完整 endpoint、支持图片的模型名和密钥。
   例如地址格式：https://你的服务地址/v1/chat/completions。
   本机服务允许 http://localhost 或 http://127.0.0.1；远程地址必须 HTTPS。
选择联网引擎后，随后识别的图片会发送到该服务；按服务商计费。
程序不会在离线失败时自动上传，也没有内置他人的 API 密钥。
密钥采用 Windows DPAPI 加密，各联网引擎分别保存；留空保留原密钥，可勾选清除。

数据与托盘
----------
历史和原图默认放在 exe 同目录的 FormulaSnipData 文件夹。
同目录不可写时，使用 %LOCALAPPDATA%\FormulaSnip。
“设置 → 本地资料库”显示实际保存位置。
移动到另一台电脑时，请一起复制 FormulaSnipData。API 密钥需在新 Windows 用户下重填。
ZIP 备份包含 history.json、图片和 Markdown 文本，不含密钥；没有自动备份恢复入口。
关闭窗口默认缩至托盘，双击托盘图标恢复；要完全退出，在设置或托盘菜单中点“退出”。
程序不会注册开机启动，不要求管理员权限。

已知边界
--------
• 离线准确率不等同于 Mathpix。手写、模糊图、长公式、多栏和复杂表格需要核对。
• 图文混排尽力按阅读顺序合并，不重建复杂页面原始版式，也不提供表格结构化重建。
• PDF 是选页渲染后 OCR，不是完整 PDF 转 Word 版式复刻。
• 一条公式最多生成 768 个 token；过长请拆分截图。
• 屏幕截图支持各个显示器分别框选，暂不支持跨显示器一次框选。
• 不包含云同步、在线图片链接、账号系统、Mathpix 的订阅服务。
• 某些 LaTeX 宏可预览但转换器不能导出为 Word，可改写宏或使用 PNG/SVG。
• “模型评分”只是模型输出分数，不是经过校准的正确率。
• 支持现代 64 位 Windows CPU；本次已在当前 Windows 电脑测试，未覆盖所有硬件。

许可与源码
----------
本程序独立开发，与 Mathpix 无隶属关系。
原创程序代码采用 MIT 许可；第三方库和模型保留各自许可证。
模型来自 Pix2Text MFR 1.5 / MFD 1.5，文字来自 RapidOCR。
界面为 PySide6/Qt，公式预览为 MathJax，推理为 ONNX Runtime。
第三方许可证位于源码包 licenses/，也被打包在 exe 的资源中。
Qt / PySide6 使用 LGPLv3 组件。可使用提供的源码与构建脚本替换库并重新打包。
源码包不重复包含大型模型；运行 download_assets.py 下载，manifest.json 提供 SHA-256。

参考
----
Mathpix 功能文档：https://mathpix.com/docs/snip/snipping-tool#windows
公式模型：https://huggingface.co/breezedeus/pix2text-mfr-1.5
定位模型：https://huggingface.co/breezedeus/pix2text-mfd-1.5
RapidOCR：https://github.com/RapidAI/RapidOCR
MathJax：https://github.com/mathjax/MathJax
