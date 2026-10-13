import concurrent.futures, hashlib, json, pathlib, time, urllib.request

ROOT = pathlib.Path(__file__).parent / 'FormulaSnip'
MODEL = ROOT / 'models' / 'formula'
MODEL.mkdir(parents=True, exist_ok=True)

def download(item):
    url, path = item
    if path.exists() and path.stat().st_size > 100:
        return str(path)
    for attempt in range(5):
        try:
            with urllib.request.urlopen(url, timeout=90) as r, path.with_suffix(path.suffix+'.part').open('wb') as f:
                while chunk := r.read(1024*1024):
                    f.write(chunk)
            path.with_suffix(path.suffix+'.part').replace(path)
            print(f'Downloaded {path.name}: {path.stat().st_size:,}', flush=True)
            return str(path)
        except Exception as e:
            print(f'Retry {path.name}: {e}', flush=True)
            time.sleep(2+attempt)
    raise RuntimeError(str(path))

if __name__ == '__main__':
    files = ['encoder_model.onnx','decoder_model.onnx','tokenizer.json','tokenizer_config.json','config.json','generation_config.json','preprocessor_config.json','special_tokens_map.json','README.md']
    jobs = [(f'https://huggingface.co/breezedeus/pix2text-mfr-1.5/resolve/main/{f}', MODEL/f) for f in files]
    (ROOT/'models'/'layout').mkdir(exist_ok=True)
    (ROOT/'ui'/'vendor').mkdir(parents=True, exist_ok=True)
    jobs += [(f'https://huggingface.co/breezedeus/pix2text-mfd-1.5/resolve/main/{f}', ROOT/'models'/'layout'/f) for f in ['pix2text-mfd-1.5.onnx','config.yaml','README.md']]
    jobs += [('https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js', ROOT/'ui'/'vendor'/'tex-svg-full.js'), ('https://raw.githubusercontent.com/mathjax/MathJax/3.2.2/LICENSE', ROOT/'ui'/'vendor'/'MathJax-LICENSE')]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(download,jobs))
    manifest=ROOT/'models'/'manifest.json'
    if manifest.exists():
        for item in json.loads(manifest.read_text(encoding='utf-8')):
            target=ROOT/item['file']
            digest=hashlib.sha256(target.read_bytes()).hexdigest()
            if digest!=item['sha256']:
                raise RuntimeError(f'Model checksum mismatch: {target.name}. Do not use this model without reviewing the upstream change.')
    for f in ['config.json','preprocessor_config.json','generation_config.json']:
        print(f, (MODEL/f).read_text())
