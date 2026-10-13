r"""Run component checks on the shipped application without a visible window.

Usage: FormulaSnip.exe --self-test C:\path\to\test-output
Only synthetic formulas are used. No network requests are made.
"""
import json,sys,time,traceback,os
from pathlib import Path

# Exercise the actual rendering entry points, including a cold first conversion.
# A single SVG alone is not enough: unstyled assistive MathML used to draw a
# second, native-math copy beneath it.
PREVIEW_REGRESSION = r"""
window.__previewRegression = null;
(async()=>{
 const cases=[];
 const check=(name,selector,expected)=>{
  const nodes=[...document.querySelectorAll(selector+' mjx-container')];
  if(nodes.length!==expected)throw Error(name+': unexpected formula count '+nodes.length);
  for(const node of nodes){
   if(node.querySelectorAll('svg').length!==1)throw Error(name+': duplicate SVG');
   const a=node.querySelector('mjx-assistive-mml');
   if(!a || !a.querySelector('math'))throw Error(name+': missing accessible math');
   const s=getComputedStyle(a);
   if(s.position!=='absolute' || s.clip!=='rect(1px, 1px, 1px, 1px)'){
    throw Error(name+': assistive MathML is visible ('+s.position+', '+s.clip+')');
   }
  }
  if(document.querySelectorAll('#MJX-SVG-styles').length!==1)throw Error(name+': invalid stylesheet count');
  cases.push(name);
 };
 const formula=String.raw`E_{y'}=b\sin\left(\tau+\delta_0\pm\frac{\pi}{2}\right)=\pm b\cos(\tau+\delta_0)`;
 newSnippet();$('editor').value=formula;renderPreview();await renderQueue;
 check('Cold-start formula preview','#rendered-content',1);
 $('editor').value=String.raw`\frac{1}{2}+\sqrt{x}`;renderPreview();await renderQueue;
 zoom(.5);check('Edit and zoom','#rendered-content',1);zoom(-.5);
 $('content-kind').value='mixed';$('editor').value=String.raw`文字与公式 \(x^2+1\)`;
 renderPreview();await renderQueue;check('Mixed-text preview','#rendered-content',1);
 $('content-kind').value='formula';$('editor').value=formula;renderPreview();await renderQueue;
 check('Return from mixed text to formula','#rendered-content',1);
 rows=[{id:'preview-test',title:'预览回归测试',content:formula,kind:'formula',favorite:0,created:'2026-10-13'}];
 showLibrary();await renderQueue;check('Formula gallery','.card-formula',1);
 rows=[];dirty=false;showLibrary();await renderQueue;
 window.__previewRegression={passed:true,cases};
})().catch(e=>{window.__previewRegression={passed:false,error:String(e)};});
"""

def run(output):
    os.environ['FORMULASNIP_DEBUG']='1'
    from PySide6.QtWidgets import QApplication,QFileDialog
    from PySide6.QtCore import QTimer,Qt
    from main import MainWindow
    from core import load_image,export_docx
    import zipfile
    from lxml import etree
    root=Path(output).resolve();root.mkdir(parents=True,exist_ok=True)
    app=QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window=MainWindow(root/'data')
    window.tray.hide()
    window.resize(1120,740)
    window.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
    window.show()
    window.store.save_settings({'provider':'offline','mode':'formula','auto_copy':False})
    report={'tests':[],'started':time.time()}
    stage=-2;in_flight=False;rowid=None;started=time.monotonic()
    def write():
        (root/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    def fail(message):
        report['error']=str(message);report['passed']=False;write()
        if window.job:window.job.cancel.set()
        QTimer.singleShot(100,app.quit)
    def preview_callback(value):
        nonlocal stage,in_flight
        in_flight=False
        value=json.loads(value or 'null')
        if value is None:return
        if not value.get('passed'):
            fail(value.get('error','Preview regression failed'));timer.stop();return
        report['tests'].append({'name':'No duplicate visual math; screen-reader MathML retained','passed':True,'cases':value['cases']})
        stage=0
    def callback(value):
        nonlocal stage,in_flight,rowid
        in_flight=False
        try:
            if isinstance(value,str) and value:
                value=json.loads(value)
            if not isinstance(value,dict) or not value.get('svg'):
                report['render_state']=value;write();return
            if stage==1:
                report['tests'].append({'name':'Bundled Qt + local MathJax render + QWebChannel save','passed':True})
                row=window.store.rows()[0];rowid=row['id']
                original=QFileDialog.getSaveFileName
                try:
                    for kind in ('png','svg','docx','latex','markdown','mathml'):
                        path=root/('formula.'+{'latex':'tex','markdown':'md','mathml':'mml'}.get(kind,kind))
                        QFileDialog.getSaveFileName=lambda *args, p=path, **kwargs:(str(p),'')
                        window.export({'id':rowid,'format':kind,'svg':value['svg']})
                        assert path.exists() and path.stat().st_size>30,kind
                    report['tests'].append({'name':'PNG SVG DOCX TEX Markdown MathML exports','passed':True})
                finally:QFileDialog.getSaveFileName=original
                with zipfile.ZipFile(root/'formula.docx') as z:
                    xml=etree.fromstring(z.read('word/document.xml'))
                    ns={'m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
                    assert xml.xpath('count(//m:f)',namespaces=ns)>0
                stage=2
                window.enqueue(load_image(root/'formula.png'),'离线识别回归测试')
            elif stage==3:
                row=window.store.rows()[0]
                for token in ('sqrt','frac'):
                    assert token in row['content'],row['content']
                report['tests'].append({'name':'Rendered formula image -> offline ONNX -> persisted LaTeX -> preview','passed':True,'content':row['content'],'seconds':row['elapsed']})
                import threading
                from PySide6.QtGui import QImage,QPainter,QFont,QPdfWriter
                from PySide6.QtCore import Qt
                from main import qimage_to_pil
                text_image=QImage(600,100,QImage.Format.Format_RGB32);text_image.fill(Qt.GlobalColor.white)
                painter=QPainter(text_image);painter.setPen(Qt.GlobalColor.black);painter.setFont(QFont('Arial',30));painter.drawText(20,65,'Hello Formula 123');painter.end()
                text_result=window.engine.recognize(qimage_to_pil(text_image),'text',threading.Event(),lambda s:None)
                assert '123' in text_result['content'],text_result['content']
                report['tests'].append({'name':'Bundled RapidOCR text recognition','passed':True,'content':text_result['content']})
                mixed=window.engine.recognize(load_image(root/'formula.png'),'mixed',threading.Event(),lambda s:None)
                assert mixed['content'] and window.engine.layout is not None
                report['tests'].append({'name':'Bundled formula detector and mixed OCR','passed':True,'content':mixed['content']})
                pdf_path=root/'sample.pdf';writer=QPdfWriter(str(pdf_path));painter=QPainter(writer);painter.drawText(100,200,'PDF test');painter.end();del writer
                import pypdfium2 as pdfium
                doc=pdfium.PdfDocument(str(pdf_path));pdf_page=doc[0];bitmap=pdf_page.render(scale=1);assert bitmap.width>100;bitmap.close();pdf_page.close();doc.close()
                report['tests'].append({'name':'Bundled PDFium page import','passed':True})
                stage=4
                # Retain the rendered view for inspection without capturing the desktop.
                window.view.grab().save(str(root/'ui-render.png'))
                report['passed']=True;report['elapsed']=time.time()-report['started'];write()
                QTimer.singleShot(500,app.quit)
        except Exception as e:fail(str(e)+'\n'+traceback.format_exc())
    def tick():
        nonlocal stage,in_flight
        if time.monotonic()-started>100:fail('Self-test timed out');timer.stop();return
        if stage==-2 and window.ready:
            stage=-1
            window.view.page().runJavaScript(PREVIEW_REGRESSION)
        if stage==-1 and not in_flight:
            in_flight=True
            window.view.page().runJavaScript('JSON.stringify(window.__previewRegression)',preview_callback)
        if stage==0 and window.ready:
            stage=1
            window.view.page().runJavaScript('newSnippet(true); saveCurrent();')
        if stage==2 and not window.job and len(window.store.rows())>=2:stage=3
        if stage in (1,3) and not in_flight:
            in_flight=True
            window.view.page().runJavaScript("JSON.stringify((()=>{let n=document.querySelector('#rendered-content svg');if(!n)return {html:document.querySelector('#rendered-content').innerHTML,mathjax:typeof MathJax,renderer:typeof MathJax.tex2svgPromise};let c=n.cloneNode(true),r=n.getBoundingClientRect();c.setAttribute('xmlns','http://www.w3.org/2000/svg');c.setAttribute('width',r.width||600);c.setAttribute('height',r.height||100);return {svg:new XMLSerializer().serializeToString(c).replaceAll('currentColor','#213b30')};})())",callback)
    timer=QTimer();timer.timeout.connect(tick);timer.start(300)
    write();app.exec()
    if window.job:window.job.cancel.set();window.job.wait(10000)
    return 0 if report.get('passed') else 1
