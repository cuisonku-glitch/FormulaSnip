from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QImage,QPainter
from PySide6.QtSvg import QSvgRenderer
from PIL import Image
root=Path(__file__).parent/'FormulaSnip'/'assets'
app=QApplication([])
renderer=QSvgRenderer(QByteArray((root/'icon.svg').read_bytes()))
im=QImage(256,256,QImage.Format.Format_ARGB32)
im.fill(0)
p=QPainter(im);renderer.render(p);p.end()
im.save(str(root/'icon.png'))
Image.open(root/'icon.png').save(root/'icon.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
