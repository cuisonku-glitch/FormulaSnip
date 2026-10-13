import importlib.metadata as meta,pathlib,urllib.request,hashlib,json,concurrent.futures,time
root=pathlib.Path(__file__).parent/'FormulaSnip'
out=root/'licenses';out.mkdir(exist_ok=True)
names=['PySide6','PySide6-Essentials','PySide6-Addons','shiboken6','onnxruntime','tokenizers','Pillow','numpy','rapidocr-onnxruntime','opencv-python','pypdfium2','python-docx','latex2mathml','mathml2omml','requests','lxml','shapely','pyclipper','PyYAML','pyinstaller']
report=[]
for name in names:
    dist=meta.distribution(name)
    saved=0
    for f in dist.files or []:
        if ('license' in str(f).lower() or 'copying' in f.name.lower() or 'copyright' in f.name.lower()) and f.suffix.lower() not in ['.dll','.pyd','.pyc','.py']:
            path=pathlib.Path(dist.locate_file(f))
            if path.is_file():
                target=out/name/f.name;target.parent.mkdir(exist_ok=True);target.write_bytes(path.read_bytes());saved+=1
    report.append({'name':name,'version':dist.version,'license_files':saved,'homepage':dist.metadata.get('Home-page','')})
def fetch(item):
    name,url=item
    for i in range(5):
        try:
            data=urllib.request.urlopen(url,timeout=30).read();(out/name).write_bytes(data);return
        except Exception:time.sleep(2)
    raise RuntimeError(name)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(fetch,[('Pix2Text-MIT.txt','https://raw.githubusercontent.com/breezedeus/Pix2Text/main/LICENSE'),('Qt-LGPL-3.0.txt','https://raw.githubusercontent.com/qt/qtbase/6.8/LICENSES/LGPL-3.0-only.txt'),('Qt-GPL-3.0.txt','https://raw.githubusercontent.com/qt/qtbase/6.8/LICENSES/GPL-3.0-only.txt'),('RapidOCR-Apache-2.0.txt','https://raw.githubusercontent.com/RapidAI/RapidOCR/main/LICENSE'),('PaddleOCR-Apache-2.0.txt','https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/main/LICENSE')]))
(out/'MathJax-Apache-2.0.txt').write_bytes((root/'ui/vendor/MathJax-LICENSE').read_bytes())
(out/'components.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
manifest=[]
for p in (root/'models').rglob('*.onnx'):
    manifest.append({'file':str(p.relative_to(root)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'models/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2),flush=True)
