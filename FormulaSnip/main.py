from __future__ import annotations
import base64
import ctypes
import io
import json
import os
import sys
import threading
import time
import traceback
from collections import deque
from pathlib import Path

# Keep browser caches under the app's own data directory, never online.
from PySide6.QtCore import (Qt,QObject,Signal,Slot,QUrl,QTimer,QPoint,QRect,QSize,QByteArray,QBuffer,QIODevice,QAbstractNativeEventFilter,QThread)
from PySide6.QtGui import (QColor,QPainter,QPen,QPixmap,QImage,QIcon,QAction,QKeySequence,QDesktopServices,QFont,QGuiApplication,QCursor)
from PySide6.QtWidgets import (QApplication,QMainWindow,QFileDialog,QMessageBox,QInputDialog,QDialog,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QWidget,QSystemTrayIcon,QMenu,QSpinBox)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage,QWebEngineSettings,QWebEngineUrlRequestInterceptor
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtSvg import QSvgRenderer
from PIL import Image
from core import (BASE,APP_VERSION,Store,OfflineEngine,load_image,cloud_recognize,Cancelled,formats,mathml,export_docx,image_data,tidy_content,wrap_formula)

def pil_to_qimage(im):
    im=im.convert('RGBA')
    return QImage(im.tobytes(),im.width,im.height,im.width*4,QImage.Format.Format_RGBA8888).copy()

def qimage_to_pil(image):
    data=QByteArray()
    buffer=QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer,'PNG')
    return load_image(io.BytesIO(bytes(data)))

def data_root():
    override=os.environ.get('FORMULASNIP_DATA_DIR')
    if override: return Path(override)
    home=Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent
    root=home/'FormulaSnipData'
    try:
        root.mkdir(parents=True,exist_ok=True)
        test=root/'.write-test'
        test.write_text('')
        test.unlink()
        return root
    except OSError:
        return Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'FormulaSnip'

class OfflineOnly(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        if info.requestUrl().scheme() not in ('file','qrc','data','about','blob'):
            info.block(True)

class Page(QWebEnginePage):
    def acceptNavigationRequest(self,url,nav,is_main):
        return url.scheme() in ('file','qrc','about','data')
    def javaScriptConsoleMessage(self,level,message,line,source):
        if os.environ.get('FORMULASNIP_DEBUG'):
            print(f'JS {line}: {message}',flush=True)

class View(QWebEngineView):
    files_dropped=Signal(list)
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: super().dragEnterEvent(event)
    def dragMoveEvent(self,event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
        else: super().dragMoveEvent(event)
    def dropEvent(self,event):
        if event.mimeData().hasUrls():
            self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()])
            event.acceptProposedAction()
        else: super().dropEvent(event)

class Job(QThread):
    done=Signal(object)
    failed=Signal(str)
    progress=Signal(str)
    def __init__(self,engine,im,settings):
        super().__init__()
        self.engine,self.im,self.settings=engine,im,settings
        self.cancel=threading.Event()
    def run(self):
        started=time.perf_counter()
        try:
            if self.settings['provider']=='offline':
                result=self.engine.recognize(self.im,self.settings['mode'],self.cancel,self.progress.emit)
            else:
                self.progress.emit('正在调用联网识别服务…')
                result=cloud_recognize(self.im,self.settings,self.settings['mode'])
            if self.cancel.is_set(): raise Cancelled()
            if self.settings['provider']=='offline' and self.settings.get('tidy',True):
                result['content']=tidy_content(result['content'],result['kind'])
            result['elapsed']=time.perf_counter()-started
            self.done.emit(result)
        except Cancelled: self.failed.emit('已取消识别')
        except Exception as e:
            self.failed.emit(str(e)[:700])

class CaptureOverlay(QWidget):
    captured=Signal(object)
    cancelled=Signal()
    def __init__(self,screen,pixmap):
        super().__init__(None,Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool)
        self.setGeometry(screen.geometry())
        self.pixmap=pixmap
        self.start=None
        self.end=None
        self.hover=None
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setMouseTracking(True)
        self.setWindowTitle('拾式 · 拖动选择识别区域')
    def pill(self,p,rect,text):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(16,42,36,235))
        p.drawRoundedRect(rect,rect.height()/2,rect.height()/2)
        p.setPen(QColor('white'))
        p.drawText(rect,Qt.AlignmentFlag.AlignCenter,text)
    def paintEvent(self,event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(QFont('Microsoft YaHei UI',10))
        p.drawPixmap(self.rect(),self.pixmap)
        p.fillRect(self.rect(),QColor(10,20,18,120))
        accent=QColor('#3ddbb4')
        if self.start and self.end:
            rect=QRect(self.start,self.end).normalized().intersected(self.rect())
            p.save()
            p.setClipRect(rect)
            p.drawPixmap(self.rect(),self.pixmap)
            p.restore()
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(accent,1.5))
            p.drawRect(rect)
            # Corner brackets make the selection edges easy to see on busy pages.
            arm=min(14,rect.width()//2,rect.height()//2)
            p.setPen(QPen(accent,4,Qt.PenStyle.SolidLine,Qt.PenCapStyle.SquareCap))
            for x,y,dx,dy in ((rect.left(),rect.top(),1,1),(rect.right(),rect.top(),-1,1),(rect.left(),rect.bottom(),1,-1),(rect.right(),rect.bottom(),-1,-1)):
                p.drawLine(x,y,x+dx*arm,y);p.drawLine(x,y,x,y+dy*arm)
            text=f'{rect.width()} × {rect.height()}   松开识别'
            width=p.fontMetrics().horizontalAdvance(text)+26
            top=rect.top()-34 if rect.top()>=40 else rect.bottom()+8
            self.pill(p,QRect(max(4,min(rect.left(),self.width()-width-4)),top,width,26),text)
        else:
            if self.hover:
                p.setPen(QPen(QColor(61,219,180,150),1,Qt.PenStyle.DashLine))
                p.drawLine(self.hover.x(),0,self.hover.x(),self.height())
                p.drawLine(0,self.hover.y(),self.width(),self.hover.y())
            text='拖动框选公式或文字   ·   Esc / 右键取消'
            width=p.fontMetrics().horizontalAdvance(text)+44
            self.pill(p,QRect((self.width()-width)//2,28,width,38),text)
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.RightButton:
            self.cancelled.emit()
            return
        self.start=event.position().toPoint()
        self.end=self.start
        self.update()
    def mouseMoveEvent(self,event):
        self.hover=event.position().toPoint()
        if self.start:self.end=self.hover
        self.update()
    def leaveEvent(self,event):
        self.hover=None;self.update()
    def mouseReleaseEvent(self,event):
        if event.button()!=Qt.MouseButton.LeftButton or self.start is None:return
        rect=QRect(self.start,event.position().toPoint()).normalized().intersected(self.rect())
        if rect.width()<6 or rect.height()<6:
            self.cancelled.emit()
            return
        # Geometry uses Qt logical coordinates; captured pixels use per-screen DPR.
        sx=self.pixmap.width()/self.width()
        sy=self.pixmap.height()/self.height()
        crop=QRect(round(rect.x()*sx),round(rect.y()*sy),round(rect.width()*sx),round(rect.height()*sy))
        self.captured.emit(qimage_to_pil(self.pixmap.copy(crop).toImage()))
    def keyPressEvent(self,event):
        if event.key()==Qt.Key.Key_Escape:self.cancelled.emit()

class InkCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(700,330)
        self.strokes=[]
        self.current=[]
        self.setCursor(Qt.CursorShape.CrossCursor)
    def paint(self,p):
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(),Qt.GlobalColor.white)
        p.setPen(QPen(QColor('#182c28'),3,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap,Qt.PenJoinStyle.RoundJoin))
        for stroke in self.strokes+[self.current]:
            for a,b in zip(stroke,stroke[1:]):p.drawLine(a,b)
    def paintEvent(self,event):self.paint(QPainter(self))
    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self.current=[event.position().toPoint()]
    def mouseMoveEvent(self,event):
        if event.buttons()&Qt.MouseButton.LeftButton:
            self.current.append(event.position().toPoint());self.update()
    def mouseReleaseEvent(self,event):
        if self.current:
            self.current.append(event.position().toPoint());self.strokes.append(self.current);self.current=[];self.update()
    def image(self):
        if not self.strokes:raise ValueError('请先写一个公式。')
        img=QImage(self.size(),QImage.Format.Format_RGB32)
        p=QPainter(img);self.paint(p);p.end()
        return qimage_to_pil(img)

class NativeHotkey(QAbstractNativeEventFilter):
    def __init__(self,window):super().__init__();self.window=window
    def nativeEventFilter(self,event_type,message):
        if event_type in (b'windows_generic_MSG',b'windows_dispatcher_MSG'):
            from ctypes import wintypes
            msg=wintypes.MSG.from_address(int(message))
            if msg.message==0x0312:
                if msg.wParam==0xF001:QTimer.singleShot(0,self.window.capture)
                if msg.wParam==0xF002:QTimer.singleShot(0,self.window.restore)
                return True,0
        return False,0

class Bridge(QObject):
    event=Signal(str)
    def __init__(self,window):super().__init__(window);self.window=window
    @Slot(str)
    def invoke(self,payload):
        try:self.window.dispatch(json.loads(payload))
        except Exception as e:self.window.notify(str(e),'error')

class MainWindow(QMainWindow):
    def __init__(self,root):
        super().__init__()
        self.store=Store(root)
        self.engine=OfflineEngine()
        self.queue=deque()
        self.job=None
        self.current_job=None
        self.overlays=[]
        self.quitting=False
        self.ready=False
        self.thumb_cache={}
        self.setWindowTitle('拾式 FormulaSnip · 离线公式识别')
        available=QApplication.primaryScreen().availableGeometry()
        self.setMinimumSize(620,470)
        self.resize(min(900,available.width()-50),min(680,available.height()-65))
        self.move(available.center()-self.rect().center())
        saved=self.store.settings().get('window')
        if isinstance(saved,list) and len(saved)==4:
            # Only reuse a saved position that is still on a connected screen.
            rect=QRect(*[int(v) for v in saved])
            if any(s.availableGeometry().intersects(rect.adjusted(60,10,-60,-rect.height()+50)) for s in QApplication.screens()):
                self.setGeometry(rect)
        self.setWindowIcon(QIcon(str(BASE/'assets'/'icon.ico')))
        self.view=View(self)
        self.setCentralWidget(self.view)
        page=Page(self.view)
        self.view.setPage(page)
        self.interceptor=OfflineOnly(self)
        page.profile().setUrlRequestInterceptor(self.interceptor)
        page.profile().setHttpCacheType(page.profile().HttpCacheType.NoCache)
        page.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,False)
        page.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,False)
        self.bridge=Bridge(self)
        self.channel=QWebChannel(page)
        self.channel.registerObject('bridge',self.bridge)
        page.setWebChannel(self.channel)
        self.view.files_dropped.connect(self.import_paths)
        # The page gets its theme in the URL so a dark window never flashes white.
        dark=self.dark_theme()
        page.setBackgroundColor(QColor('#101614' if dark else '#f3f6f4'))
        url=QUrl.fromLocalFile(str(BASE/'ui'/'index.html'))
        url.setQuery('theme='+('dark' if dark else 'light'))
        self.view.load(url)
        self.set_chrome(dark)
        QGuiApplication.styleHints().colorSchemeChanged.connect(lambda scheme:self.emit_settings() if self.ready else None)
        self.tray=QSystemTrayIcon(self.windowIcon(),self)
        menu=QMenu()
        menu.addAction('打开拾式',self.restore)
        menu.addAction('截图识别',self.capture)
        menu.addSeparator()
        menu.addAction('退出',self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip('拾式 FormulaSnip · 截图识别')
        self.tray.activated.connect(lambda reason:self.restore() if reason==QSystemTrayIcon.ActivationReason.DoubleClick else None)
        self.tray.show()
        self.native_filter=NativeHotkey(self)
        QApplication.instance().installNativeEventFilter(self.native_filter)
        self.hotkey_status=''
        self.register_hotkeys()
        self.test_mode=os.environ.get('FORMULASNIP_TEST_MODE')=='1'

    def emit(self,event_type,**payload):
        self.bridge.event.emit(json.dumps({'type':event_type,**payload},ensure_ascii=False))
    def notify(self,text,kind='success'):self.emit('toast',message=text,kind=kind)
    def restore(self):self.showNormal();self.raise_();self.activateWindow()
    def register_hotkeys(self):
        user=ctypes.windll.user32
        user.UnregisterHotKey(None,0xF001)
        user.UnregisterHotKey(None,0xF002)
        key=self.store.settings()['hotkey']
        choices={'Ctrl+Alt+S':(3,0x53),'Ctrl+Alt+M':(3,0x4D),'Ctrl+Shift+S':(6,0x53),'Ctrl+Alt+Q':(3,0x51)}
        mod,vk=choices.get(key,choices['Ctrl+Alt+S'])
        ok=user.RegisterHotKey(None,0xF001,mod|0x4000,vk)
        self.hotkey_status='' if ok else f'{key} 已被其他程序占用，请在设置中换一个快捷键。'
        user.RegisterHotKey(None,0xF002,3|0x4000,0x4F)
    def system_dark(self):
        return QGuiApplication.styleHints().colorScheme()==Qt.ColorScheme.Dark
    def dark_theme(self):
        theme=self.store.settings().get('theme','auto')
        return theme=='dark' or (theme=='auto' and self.system_dark())
    def set_chrome(self,dark):
        # Match the Windows title bar to the toolbar. Older Windows builds ignore the colour.
        try:
            from ctypes import wintypes
            dwm=ctypes.windll.dwmapi.DwmSetWindowAttribute
            dwm.argtypes=[wintypes.HWND,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD]
            hwnd=wintypes.HWND(int(self.winId()))
            flag=ctypes.c_int(1 if dark else 0)
            dwm(hwnd,20,ctypes.byref(flag),ctypes.sizeof(flag))
            colour=wintypes.DWORD(0x001D1F17 if dark else 0x00FFFFFF)
            dwm(hwnd,35,ctypes.byref(colour),ctypes.sizeof(colour))
        except Exception:pass
    def remember_geometry(self):
        if self.testAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen):return
        rect=self.normalGeometry() if self.isMaximized() else self.geometry()
        if rect.width()>=self.minimumWidth():self.store.put('window',[rect.x(),rect.y(),rect.width(),rect.height()])
    def emit_settings(self):
        self.emit('settings',settings=self.store.settings(),data_dir=str(self.store.root),version=APP_VERSION,hotkey_warning=self.hotkey_status,system_dark=self.system_dark())
    def state(self):
        self.emit_settings()
        self.history()
    def history(self):
        rows=self.store.rows()
        for index,row in enumerate(rows):
            if row['image'] and index<200:
                if row['image'] not in self.thumb_cache:self.thumb_cache[row['image']]=self.store.image(row,True)
                row['thumbnail']=self.thumb_cache[row['image']]
        self.emit('history',rows=rows)
    def detail(self,ident):
        row=self.store.get(ident)
        row['original']=self.store.image(row)
        self.emit('detail',row=row,formats=formats(row['content'],row['kind']))

    def dispatch(self,data):
        action=data.get('action')
        if action=='ready':
            self.ready=True;self.state()
            if self.hotkey_status:self.notify(self.hotkey_status,'info')
            # Load the formula model in the background so the first snip is not slowed by it.
            if self.store.settings()['provider']=='offline':QTimer.singleShot(1200,lambda:threading.Thread(target=self.engine.warm,daemon=True).start())
            initial=os.environ.get('FORMULASNIP_OPEN_IMAGE')
            if initial:QTimer.singleShot(350,lambda:self.import_paths([initial]))
        elif action=='capture':self.capture()
        elif action=='import':
            paths,_=QFileDialog.getOpenFileNames(self,'导入图片或 PDF','','图片与 PDF (*.png *.jpg *.jpeg *.bmp *.webp *.tif *.tiff *.pdf);;所有文件 (*)')
            if paths:self.import_paths(paths)
        elif action=='paste':
            clip=QApplication.clipboard()
            if clip.mimeData().hasImage():self.enqueue(qimage_to_pil(clip.image()),'粘贴图片')
            elif clip.mimeData().hasUrls():self.import_paths([u.toLocalFile() for u in clip.mimeData().urls() if u.isLocalFile()])
            else:self.notify('剪贴板里没有图片，请先复制一张图片。','info')
        elif action=='ink':self.handwrite()
        elif action=='detail':self.detail(data['id'])
        elif action=='copy':QApplication.clipboard().setText(data.get('text',''))
        elif action=='tidy':self.emit('tidied',text=tidy_content(data.get('text',''),data.get('kind','formula')))
        elif action=='quick':
            if data.get('key') in ('mode','theme','copy_format'):self.store.put(data['key'],data['value']);self.emit_settings()
        elif action=='chrome':self.set_chrome(bool(data.get('dark')))
        elif action=='copy_mathml':
            row=self.store.get(data['id'])
            if row['kind']!='formula':raise ValueError('MathML 复制仅适用于纯公式记录。')
            from PySide6.QtCore import QMimeData
            xml=mathml(row['content'])
            mime=QMimeData();mime.setText(xml);mime.setHtml(xml);mime.setData('application/mathml+xml',xml.encode('utf-8'))
            QApplication.clipboard().setMimeData(mime)
            self.notify('已复制 MathML，可直接粘贴到 Word')
        elif action=='save':
            if data.get('id'):self.store.update(data['id'],data['content'],data['title'],data['kind']);ident=data['id']
            else:ident=self.store.add({'content':data['content'],'kind':data['kind']},title=data['title'])
            self.history();self.detail(ident);self.notify('已保存')
        elif action=='favorite':self.store.favorite(data['id']);self.history();self.emit('favorite',id=data['id'],value=bool(self.store.get(data['id'])['favorite']))
        elif action=='delete':
            # The page asks for confirmation before sending this.
            self.thumb_cache.pop(self.store.get(data['id'])['image'],None)
            self.store.delete(data['id']);self.history();self.emit('deleted',id=data['id'])
        elif action=='settings':
            self.store.save_settings(data['settings']);self.register_hotkeys();self.state();self.notify('设置已保存'+('；'+self.hotkey_status if self.hotkey_status else ''))
        elif action=='retry':
            row=self.store.get(data['id'])
            if not row['image']:raise ValueError('手动创建的公式没有原图。')
            self.enqueue(load_image(self.store.root/'images'/row['image']),row['title']+' · 重新识别')
        elif action=='cancel':
            self.queue.clear()
            if self.job:self.job.cancel.set();self.emit('busy',message='正在取消，等待当前步骤结束…',remaining=0)
        elif action=='export':self.export(data)
        elif action=='data_dir':QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.store.root)))
        elif action=='backup':self.backup()
        elif action=='test_import' and self.test_mode:self.import_paths([data['path']])
        elif action=='quit':self.quit_app()

    def import_paths(self,paths):
        for path in paths:
            try:
                p=Path(path)
                if p.suffix.lower()=='.pdf':self.import_pdf(p)
                else:self.enqueue(load_image(p),p.stem)
            except Exception as e:self.notify(f'{Path(path).name}：{e}','error')
    def import_pdf(self,path):
        import pypdfium2 as pdfium
        doc=pdfium.PdfDocument(str(path))
        count=len(doc)
        value,ok=QInputDialog.getText(self,'导入 PDF 页面',f'共 {count} 页。输入页码，如 1-3,5。每页作为一张图片识别；建议使用“图文混排”模式。',text='1')
        if not ok:doc.close();return
        pages=set()
        try:
            for part in value.replace('，',',').split(','):
                part=part.strip()
                if '-' in part:
                    a,b=map(int,part.split('-'));pages.update(range(a,b+1))
                else:pages.add(int(part))
            if not pages or min(pages)<1 or max(pages)>count or len(pages)>50:raise ValueError()
        except Exception:
            doc.close();raise ValueError('请输入有效页码，一次最多导入 50 页。')
        for number in sorted(pages):
            # Render lazily while processing the queue to bound memory for long PDFs.
            self.queue.append({'pdf':str(path),'page':number-1,'title':f'{path.stem} · 第 {number} 页','settings':self.store.settings(secret=True)})
        doc.close()
        if not self.job:self.next_job()
    def enqueue(self,im,title):
        self.queue.append({'image':im,'title':title,'settings':self.store.settings(secret=True)})
        if not self.job:self.next_job()
        else:self.emit('busy',message='正在识别，已加入队列',remaining=len(self.queue))
    def next_job(self):
        if not self.queue:
            self.emit('idle');return
        item=self.queue.popleft()
        try:
            if 'pdf' in item:
                import pypdfium2 as pdfium
                doc=pdfium.PdfDocument(item['pdf']);page=doc[item['page']]
                scale=min(2.0,2400/max(page.get_size()))
                bitmap=page.render(scale=scale)
                item['image']=bitmap.to_pil().convert('RGB').copy()
                bitmap.close();page.close();doc.close()
            self.current_job=item
            self.job=Job(self.engine,item['image'],item['settings'])
            self.job.progress.connect(lambda msg:self.emit('busy',message=msg,remaining=len(self.queue)))
            self.job.done.connect(self.job_done)
            self.job.failed.connect(lambda error:self.notify(error,'error' if error!='已取消识别' else 'info'))
            self.job.finished.connect(self.job_finished)
            thumb=item['image'].copy();thumb.thumbnail((480,200))
            self.emit('busy',message='正在识别 '+item['title'],remaining=len(self.queue),preview=image_data(thumb))
            self.job.start()
        except Exception as e:
            self.notify(str(e),'error');QTimer.singleShot(0,self.next_job)
    def job_done(self,result):
        item=self.current_job
        engine={'offline':'离线 · Pix2Text / RapidOCR','mathpix':'联网 · Mathpix','compatible':'联网 · '+item['settings'].get('model','')}[item['settings']['provider']]
        ident=self.store.add(result,item['image'],item['title'],engine,result['elapsed'])
        if item['settings'].get('auto_copy'):QApplication.clipboard().setText(wrap_formula(result['content'],result['kind'],item['settings'].get('copy_format','latex')))
        self.history();self.detail(ident)
        self.notify(f'识别完成 · {result["elapsed"]:.1f} 秒'+(' · 已复制' if item['settings'].get('auto_copy') else ''))
    def job_finished(self):
        old=self.job
        self.job=None;self.current_job=None
        old.deleteLater()
        if self.quitting:QApplication.instance().quit()
        else:QTimer.singleShot(0,self.next_job)

    def capture(self):
        if self.overlays:return
        if self.isActiveWindow() and QApplication.activeModalWidget():return
        self.hide()
        QTimer.singleShot(260,self.start_capture)
    def start_capture(self):
        # One overlay per screen avoids assuming equal scaling on multiple monitors.
        shots=[(s,s.grabWindow(0)) for s in QApplication.screens()]
        if any(p.isNull() for s,p in shots):
            self.restore();self.notify('无法读取屏幕，请确认 Windows 桌面已解锁。','error');return
        for screen,pixmap in shots:
            overlay=CaptureOverlay(screen,pixmap)
            overlay.captured.connect(self.end_capture)
            overlay.cancelled.connect(lambda:self.end_capture(None))
            self.overlays.append(overlay)
        for overlay in self.overlays:overlay.show();overlay.raise_()
        focus=QApplication.screenAt(QCursor.pos())
        for overlay in self.overlays:
            if focus and overlay.geometry()==focus.geometry():overlay.activateWindow();overlay.setFocus()
    def end_capture(self,im):
        for overlay in self.overlays:overlay.close();overlay.deleteLater()
        self.overlays=[]
        self.restore()
        if im is not None:self.enqueue(im,'截图 '+time.strftime('%m-%d %H:%M:%S'))
    def handwrite(self):
        dialog=QDialog(self);dialog.setWindowTitle('手写公式 · 拾式')
        layout=QVBoxLayout(dialog)
        layout.addWidget(QLabel('用鼠标或触控笔书写。离线识别对清晰印刷体更准确，手写结果请核对。'))
        canvas=InkCanvas();layout.addWidget(canvas)
        bar=QHBoxLayout();layout.addLayout(bar)
        undo=QPushButton('撤销');clear=QPushButton('清空');run=QPushButton('识别公式');run.setObjectName('primary');run.setDefault(True)
        bar.addWidget(undo);bar.addWidget(clear);bar.addStretch();bar.addWidget(run)
        def undo_action():
            if canvas.strokes:canvas.strokes.pop();canvas.update()
        undo.clicked.connect(undo_action)
        clear.clicked.connect(lambda:(canvas.strokes.clear(),canvas.update()))
        def recognize():
            try:
                im=canvas.image();dialog.accept();cfg=self.store.settings(secret=True);cfg['mode']='formula'
                self.queue.append({'image':im,'title':'手写公式','settings':cfg})
                if not self.job:self.next_job()
            except Exception as e:QMessageBox.information(dialog,'提示',str(e))
        run.clicked.connect(recognize);dialog.exec()

    def export(self,data):
        row=self.store.get(data['id'])
        kind=data['format']
        if kind in ('png','svg','copy_png'):
            svg=data.get('svg','')
            if not svg:raise ValueError('预览尚未完成，或当前内容不支持公式图像导出。')
            renderer=QSvgRenderer(QByteArray(svg.encode('utf-8')))
            if not renderer.isValid():raise ValueError('无法生成公式图像，请检查 LaTeX 语法。')
            size=renderer.defaultSize()
            if size.isEmpty():size=QSize(800,240)
            scale=min(3,6000/max(size.width(),size.height()))
            size=QSize(max(1,int(size.width()*scale)),max(1,int(size.height()*scale)))
            img=QImage(size+QSize(48,48),QImage.Format.Format_ARGB32);img.fill(Qt.GlobalColor.white)
            p=QPainter(img);p.translate(24,24)
            from PySide6.QtCore import QRectF
            renderer.render(p,QRectF(0,0,size.width(),size.height()));p.end()
            if kind=='copy_png':QApplication.clipboard().setImage(img);self.notify('公式图片已复制');return
        if kind=='original':
            if not row['image']:raise ValueError('这条记录没有原图。')
            kind='original_png'
        ext={'latex':'tex','markdown':'md','docx':'docx','png':'png','svg':'svg','original_png':'png','mathml':'mml'}[kind]
        suggested=''.join(c for c in row['title'] if c not in '<>:"/\\|?*')[:80] or 'formula'
        path,_=QFileDialog.getSaveFileName(self,'导出文件',suggested+'.'+ext,f'{ext.upper()} (*.{ext})')
        if not path:return
        target=Path(path)
        if not target.suffix:target=target.with_suffix('.'+ext)
        if kind=='docx':export_docx(row,target)
        elif kind=='png':
            if not img.save(str(target),'PNG'):raise ValueError('PNG 保存失败。')
        elif kind=='svg':target.write_text(svg,encoding='utf-8')
        elif kind=='mathml':target.write_text(mathml(row['content']),encoding='utf-8')
        elif kind=='original_png':load_image(self.store.root/'images'/row['image']).save(target,'PNG')
        else:
            text=row['content']
            if kind=='markdown' and row['kind']=='formula':text='$$\n'+text+'\n$$\n'
            if kind=='latex' and row['kind']=='formula':text='\\documentclass{article}\n\\usepackage{amsmath,amssymb}\n\\begin{document}\n\\[\n'+text+'\n\\]\n\\end{document}\n'
            target.write_text(text,encoding='utf-8')
        self.notify('已导出：'+target.name)
    def backup(self):
        import zipfile
        path,_=QFileDialog.getSaveFileName(self,'备份资料库','FormulaSnip-'+time.strftime('%Y%m%d')+'.zip','ZIP (*.zip)')
        if not path:return
        # Credentials are deliberately excluded. The archive is for history portability.
        rows=self.store.rows()
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('history.json',json.dumps(rows,ensure_ascii=False,indent=2))
            for row in rows:
                if row['image']:
                    p=self.store.root/'images'/row['image']
                    if p.exists():z.write(p,'images/'+p.name)
            for i,row in enumerate(rows):z.writestr(f'text/{i+1:04d}.md',row['content'])
        self.notify('资料库已备份（不包含 API 密钥）')
    def closeEvent(self,event):
        self.remember_geometry()
        if not self.quitting and self.store.settings().get('close_to_tray'):
            event.ignore();self.hide()
            if not getattr(self,'tray_notice',False):self.tray.showMessage('拾式仍在运行','使用截图快捷键，或双击托盘图标打开。');self.tray_notice=True
        elif self.job:
            event.ignore();self.quit_app()
        else:
            ctypes.windll.user32.UnregisterHotKey(None,0xF001)
            ctypes.windll.user32.UnregisterHotKey(None,0xF002)
            event.accept()
            QTimer.singleShot(0,QApplication.instance().quit)
    def quit_app(self):
        if self.isVisible():self.remember_geometry()
        self.quitting=True;self.queue.clear()
        if self.job:
            self.job.cancel.set();self.emit('busy',message='正在结束识别，请稍候…',remaining=0)
        else:QApplication.instance().quit()

def run():
    app=QApplication(sys.argv)
    app.setApplicationName('FormulaSnip')
    app.setOrganizationName('FormulaSnip')
    app.setQuitOnLastWindowClosed(False)
    root=data_root()
    app.setStyle('Fusion')
    app.setFont(QFont('Microsoft YaHei UI',10))
    app.setStyleSheet("""
        QDialog,QMessageBox,QInputDialog { background:#f6f9f7; color:#15302a; }
        QLabel { color:#4d625b; }
        QPushButton { padding:8px 18px; border:1px solid #d5dfda; border-radius:8px; background:#ffffff; color:#15302a; }
        QPushButton:hover { background:#eef5f2; border-color:#12806a; }
        QPushButton:pressed { background:#e2f4ee; }
        QPushButton:default,QPushButton#primary { background:#12806a; border-color:#12806a; color:#ffffff; }
        QPushButton:default:hover,QPushButton#primary:hover { background:#0d6756; }
        QLineEdit,QComboBox { padding:7px 9px; border:1px solid #d5dfda; border-radius:8px; background:#ffffff; color:#15302a; }
        QLineEdit:focus { border-color:#12806a; }
        QMenu { background:#ffffff; color:#15302a; border:1px solid #dfe7e3; padding:5px; }
        QMenu::item { padding:7px 26px 7px 14px; border-radius:6px; }
        QMenu::item:selected { background:#e2f4ee; color:#0d6756; }
    """)
    from PySide6.QtNetwork import QLocalServer,QLocalSocket
    import hashlib
    server_name='FormulaSnip-'+hashlib.sha256(str(root.resolve()).encode()).hexdigest()[:14]
    sock=QLocalSocket();sock.connectToServer(server_name)
    if sock.waitForConnected(400):sock.write(b'open');sock.waitForBytesWritten(300);return 0
    server=QLocalServer();server.listen(server_name)
    window=MainWindow(root)
    def incoming():
        con=server.nextPendingConnection()
        if con:con.close();con.deleteLater()
        window.restore()
    server.newConnection.connect(incoming)
    window.show()
    def exception_hook(kind,value,tb):
        log=''.join(traceback.format_exception(kind,value,tb))
        try:(root/'last-error.log').write_text(log,encoding='utf-8')
        except OSError:pass
        window.notify('发生错误：'+str(value),'error')
    sys.excepthook=exception_hook
    code=app.exec()
    window.tray.hide()
    if window.job:window.job.cancel.set();window.job.wait(130000)
    return code

if __name__=='__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    if len(sys.argv)>2 and sys.argv[1]=='--self-test':
        from selftest import run as selftest_run
        sys.exit(selftest_run(sys.argv[2]))
    sys.exit(run())
