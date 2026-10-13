import pathlib,sys,threading,io,json,zipfile
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).parent/'FormulaSnip'))
from core import *
from lxml import etree

root=pathlib.Path(__file__).parent/'test-results';root.mkdir(exist_ok=True)
results=[]
def check(name,fn):
    try:fn();results.append({'test':name,'passed':True});print('PASS',name,flush=True)
    except Exception as e:results.append({'test':name,'passed':False,'error':str(e)});print('FAIL',name,str(e),flush=True)

def docx_check():
    cases=[r'x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}',r'A=\begin{pmatrix}a&b\\c&d\end{pmatrix}',r'\int_0^\infty e^{-x^2}\,dx=\frac{\sqrt\pi}{2}']
    ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    for i,c in enumerate(cases):
        p=root/f'export-{i}.docx';export_docx({'title':'公式导出验证','kind':'formula','content':c},p)
        with zipfile.ZipFile(p) as z:
            xml=etree.fromstring(z.read('word/document.xml'));assert xml.xpath('count(//m:oMath)',namespaces=ns)==1
            if i==0:assert xml.xpath('count(//m:f)',namespaces=ns)>0
            if i==1:assert xml.xpath('count(//m:m)',namespaces=ns)>0
    export_docx({'title':'中英图文','kind':'mixed','content':'中文测试 Chinese\n\n\\(x^2+y^2=1\\)'},root/'mixed-export.docx')
check('DOCX editable fractions, matrices, integrals and mixed text',docx_check)

def storage_check():
    store=Store(root/'unit-store')
    im=Image.new('RGB',(160,80),'white')
    ident=store.add({'content':'x^2','kind':'formula'},im,'example')
    assert store.image(store.get(ident)).startswith('data:image/png;base64,')
    store.favorite(ident);assert store.get(ident)['favorite']==1
    store.update(ident,'y=1','edited','formula');assert store.get(ident)['content']=='y=1'
    filename=store.get(ident)['image'];store.delete(ident)
    assert not (store.root/'images'/filename).exists()
    store.db.close()
check('SQLite save edit favorite delete image cleanup',storage_check)

def encryption_check():
    value='synthetic-test-key-1234'
    sealed=protect_secret(value);assert value not in sealed
    assert protect_secret(sealed,True)==value
    s=Store(root/'secret-store');s.save_settings({'provider':'compatible','api_key':value});assert s.settings(secret=True)['api_key']==value
    assert 'api_key' not in s.settings() and s.settings()['has_key']
    s.save_settings({'provider':'mathpix','api_key':'separate-key'})
    s.save_settings({'provider':'compatible'});assert s.settings(secret=True)['api_key']==value
    s.save_settings({'provider':'compatible','clear_key':True});assert not s.settings()['has_key']
    s.db.close()
check('Windows DPAPI encryption and separate provider keys',encryption_check)

def cloud_check():
    class Reply:
        status_code=200
        def json(self):return {'choices':[{'message':{'content':'```latex\nx^2\n```'},'finish_reason':'stop'}]}
    cfg={'provider':'compatible','endpoint':'http://127.0.0.1:9999/v1/chat/completions','model':'test-vision','api_key':'synthetic'}
    with patch('requests.post',return_value=Reply()) as post:
        r=cloud_recognize(Image.new('RGB',(10,10),'white'),cfg,'formula');assert r['content']=='x^2'
        args=post.call_args.kwargs;assert args['headers']['Authorization']=='Bearer synthetic'
        assert args['json']['messages'][0]['content'][1]['image_url']['url'].startswith('data:image/png;base64,')
    cfg['endpoint']='http://remote.example/v1/chat/completions'
    try:cloud_recognize(Image.new('RGB',(10,10),'white'),cfg,'formula');raise AssertionError('accepted insecure remote')
    except ValueError:pass
    class MathReply:
        status_code=200
        def json(self):return {'latex_styled':'y=x^2','confidence':.98}
    with patch('requests.post',return_value=MathReply()) as post:
        r=cloud_recognize(Image.new('RGB',(10,10)),{'provider':'mathpix','mathpix_id':'synthetic-id','api_key':'synthetic-key'},'formula')
        assert r['content']=='y=x^2' and post.call_args.args[0]=='https://api.mathpix.com/v3/text'
check('Both cloud adapters request and response contracts (mocked)',cloud_check)

def cancel_check():
    e=FormulaEngine();cancel=threading.Event();cancel.set()
    try:e.recognize(Image.new('RGB',(100,100),'white'),cancel);raise AssertionError('not cancelled')
    except Cancelled:pass
check('Offline inference cancellation',cancel_check)

def tidy_check():
    spaced=r"E _ { y ^ { \prime } } = b \sin ( \tau + \delta _ { 0 } \pm \frac { \pi } { 2 } ) \! = \! \pm \mathrm { b } \cos ( \tau \! + \! \delta _ { 0 } )"
    compact=r"E_{y^{\prime}}=b \sin \left(\tau+\delta_0 \pm \frac{\pi}{2}\right)=\pm \mathrm{b} \cos(\tau+\delta_0)"
    assert tidy_latex(spaced)==compact,tidy_latex(spaced)
    cases=[spaced,r"x = \frac { - b \pm \sqrt { b ^ { 2 } \: - \: 4 a c } } { 2 a }",r"A = \left( \begin{array} { c c } a & b \\ c & d \end{array} \right)",
           r"f ( x ) = \left\{ \begin{array} { l l } ( \frac { 1 } { x } ) & \text { if } x > 0 \\ 0 & \text { otherwise } \end{array} \right.",
           r"\sqrt [ 3 ] { \frac { a } { b } } [ \frac { 1 } { 2 } , 1 )",r"\int _ { 0 } ^ { \infty } e ^ { - x ^ { 2 } } \, d x",r"x _ { 1 } 2 + \sin x \alpha \ b"]
    for case in cases:
        once=tidy_latex(case)
        assert tidy_latex(once)==once,once
        assert mathml(once),once
    assert tidy_latex(cases[1])==r"x=\frac{-b \pm \sqrt{b^2-4ac}}{2a}"
    assert r"\text{ if }" in tidy_latex(cases[3]) and r"\left(\frac{1}{x}\right)" in tidy_latex(cases[3])
    assert tidy_latex(cases[4])==r"\sqrt[3]{\frac{a}{b}}[\frac{1}{2},1)"
    assert tidy_latex(cases[6])==r"x_{1}2+\sin x \alpha\ b"
    assert tidy_content(r"设 \( x _ { 0 } \! = \! 1 \)，价格 $5",'mixed')==r"设 \(x_0=1\)，价格 $5"
    assert tidy_content('a  b','text')=='a  b'
    assert wrap_formula('x','formula','inline')=='$x$' and wrap_formula('x','text','inline')=='x'
check('LaTeX tidy: spacing, scripts, left/right, idempotent, still converts',tidy_check)

(root/'unit-report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
sys.exit(0 if all(x['passed'] for x in results) else 1)
