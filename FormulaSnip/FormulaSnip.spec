from PyInstaller.utils.hooks import collect_data_files, copy_metadata
from pathlib import Path

root=Path(SPECPATH)
data=[(str(root/'ui'),'ui'),(str(root/'models'),'models'),(str(root/'assets'),'assets'),(str(root/'licenses'),'licenses')]
for package in ['rapidocr_onnxruntime','latex2mathml','mathml2omml','pypdfium2','docx']:
    data+=collect_data_files(package)
for package in ['tokenizers','onnxruntime','pypdfium2','pypdfium2_raw']:
    try:data+=copy_metadata(package)
    except Exception:pass
a=Analysis([str(root/'main.py')],pathex=[str(root)],binaries=[],datas=data,
 hiddenimports=['rapidocr_onnxruntime','onnxruntime','tokenizers','pypdfium2','mathml2omml','latex2mathml.converter','PIL.Image','PySide6.QtSvg','PySide6.QtNetwork'],
 excludes=['torch','tensorflow','matplotlib','scipy','pandas','IPython','jupyter','tkinter','pytest'],noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,a.binaries,a.datas,[],name='FormulaSnip',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False,icon=str(root/'assets'/'icon.ico'),version=str(root/'version_info.txt'))
