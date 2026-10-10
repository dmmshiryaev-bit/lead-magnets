from pathlib import Path
import re, sys
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, Polygon, Group
from reportlab.graphics import renderPDF, renderSVG

BASE=Path(__file__).resolve().parent
OUT=BASE.parents[1]/'pdfs'
W,H=A4; M=48; CW=W-2*M
BG='#FAF9FF'; INK='#211A33'; VIOLET='#6D28D9'; LIME='#D9F75B'; PALE='#EEE8FA'; BORDER='#C8BFD8'
F=BASE/'fonts'
for name,file in [('Golos','Golos-Regular.ttf'),('GolosBold','Golos-Semibold.ttf'),('Unbounded','Unbounded-Medium.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(F/file)))
pdfmetrics.registerFontFamily('Golos',normal='Golos',bold='GolosBold',italic='Golos',boldItalic='GolosBold')
raw=(BASE/'content.txt').read_text(encoding='utf-8')
parts=re.split(r'### Страница \d+\. ',raw)[1:]
pages=[]
for part in parts:
 title,body=part.split('\n',1)
 pages.append((title.strip(),[b.strip() for b in body.strip().split('\n\n') if b.strip()]))
def rich(s):
 s=escape(s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 return s.replace('\n','<br/>')
def para(s,width=CW,size=11,leading=None,font='Golos',color=INK):
 return Paragraph(rich(s),ParagraphStyle('p',fontName=font,fontSize=size,leading=leading or size*1.27,textColor=HexColor(color),splitLongWords=True))
c=canvas.Canvas(str(OUT/'content-plan-week.pdf'),pagesize=A4,pageCompression=1)
c.setTitle('План постов на неделю'); c.setAuthor('Дмитрий Ширяев'); c.setSubject('Рабочая тетрадь для экспертов, продающих консультации')
def box(x,y,w,h,fill='#FFFFFF',stroke=BORDER,r=6):
 c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor(stroke)); c.setLineWidth(.6)
 c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=fill!=stroke)
def text(s,x,y,w=CW,size=11,leading=None,font='Golos',color=INK):
 p=para(s,w,size,leading,font,color); _,h=p.wrap(w,H)
 p.drawOn(c,x,H-y-h)
 if y+h>H-38: print('OVERFLOW',s[:40],y+h)
 return y+h
def field(s,y,h=34,x=M,w=CW):
 box(x,y,w,h)
 text(s,x+9,y+7,w-18,10,color='#796D8D')
 if h>=39:
  c.setStrokeColor(HexColor(PALE)); c.line(x+9,H-y-h+10,x+w-9,H-y-h+10)
 return y+h
def begin(n,title,tag=None,size=22):
 c.setFillColor(HexColor(BG)); c.rect(0,0,W,H,fill=1,stroke=0)
 text('ПЛАН ПОСТОВ НА НЕДЕЛЮ',M,23,CW-50,7.5,10,'GolosBold',VIOLET)
 text(f'{n:02d} / 06',W-M-48,23,50,8,10,'Golos',VIOLET)
 y=text(title,M,52,CW,size,size*1.23,'Unbounded',VIOLET)+13
 if tag:
  box(M,y,146,22,LIME,LIME,11)
  text(tag,M+11,y+4,128,9.5,12,'GolosBold'); y+=34
 return y
def end(n):
 c.setStrokeColor(HexColor(BORDER)); c.setLineWidth(.5); c.line(M,33,W-M,33)
 for i in range(6):
  c.setFillColor(HexColor(VIOLET if i==n-1 else PALE)); c.circle(M+3+i*11,20,2.5,fill=1,stroke=0)
 c.showPage()
def art(kind):
 d=Drawing(400,230)
 def rect(x,y,w,h,fill,r=10,stroke=None):
  d.add(Rect(x,y,w,h,rx=r,ry=r,fillColor=HexColor(fill),strokeColor=HexColor(stroke) if stroke else None,strokeWidth=1.2))
 if kind=='cover':
  d.add(Circle(250,115,107,fillColor=HexColor(PALE),strokeColor=None))
  for i in range(5):
   x=24+i*67; y=45+(i%2)*20
   rect(x+4,y-5,60,105,'#DCD2EE',8);rect(x,y,60,105,'#FFFFFF',8,BORDER)
   rect(x+10,y+79,40,9,VIOLET if i==2 else PALE,4)
  g=Group();g.add(Rect(0,0,155,14,fillColor=HexColor(VIOLET),strokeColor=None));g.add(Polygon([155,0,174,7,155,14],fillColor=HexColor(INK),strokeColor=None));g.rotate(-24);g.translate(174,194);d.add(g)
  d.add(Circle(335,55,27,fillColor=HexColor(LIME),strokeColor=None))
  d.add(Line(322,55,332,45,strokeColor=HexColor(INK),strokeWidth=5));d.add(Line(332,45,351,66,strokeColor=HexColor(INK),strokeWidth=5))
 elif kind=='questions':
  rect(60,34,145,170,'#FFFFFF',12,BORDER)
  for x,y,fill in [(126,127,PALE),(242,115,VIOLET),(170,35,LIME)]:
   rect(x,y,94,64,fill,18);d.add(Polygon([x+15,y+7,x+9,y-13,x+36,y+7],fillColor=HexColor(fill),strokeColor=None))
  d.add(Circle(104,101,36,fillColor=None,strokeColor=HexColor(VIOLET),strokeWidth=12));d.add(Line(78,76,44,42,strokeColor=HexColor(VIOLET),strokeWidth=13))
 elif kind=='topics':
  for i in range(3): rect(18+i*12,70+i*12,55,85,PALE,6)
  d.add(Line(106,113,170,113,strokeColor=HexColor(VIOLET),strokeWidth=3))
  d.add(Polygon([158,122,174,113,158,104],fillColor=HexColor(VIOLET),strokeColor=None))
  for i in range(5): rect(189+i*38,76+(i%2)*8,32,70,LIME if i==2 else '#FFFFFF',5,BORDER)
 elif kind=='finish':
  rect(80,36,242,141,VIOLET,12);rect(96,164,95,25,VIOLET,8)
  for i in range(3):rect(132+i*11,62+i*14,150,130,PALE if i<2 else '#FFFFFF',6,BORDER)
  rect(268,133,28,70,LIME,3)
 return d
arts={name:art(name) for name in ['cover','questions','topics','finish']}
for name,d in arts.items(): renderSVG.drawToFile(d,str(BASE/(name+'.svg')))
def ill(name,x,y,w):
 d=arts[name]; c.saveState();c.translate(x,H-y-w*230/400);c.scale(w/400,w/400);renderPDF.draw(d,c,0,0);c.restoreState()

# Page 1
t,b=pages[0]; y=begin(1,'План постов\nна неделю',size=34)
y=text(b[0],M,y,CW,15,20,'GolosBold')+16
y=text(b[1],M,y)+16
box(M,y,CW,64,PALE,PALE,10);text(b[2],M+14,y+13,CW-28,11,14);y+=81
y=text(b[3],M,y)+18
y=text(b[4],M,y,font='GolosBold')+8
y=field(b[5],y,48)
ill('cover',W-M-272,y+19,272)
text(b[6],M,692,CW,11,14)
end(1)

# Page 2
t,b=pages[1];y=begin(2,t,b[0].strip('*'))
y=text(b[1],M,y)+7;y=text(b[2],M,y,font='GolosBold')+12
blocks=re.split(r'(?=\*\*[1-4]\. )','\n\n'.join(b[3:]))
for idx,block in enumerate([z for z in blocks if z.strip()]):
 items=block.strip().split('\n\n')
 y=text(items[0],M,y,CW,11.5,14.5,'GolosBold',VIOLET)+4
 y=text(items[1],M,y,CW,11,13.8)+4
 if idx<3:
  y=text(items[2],M,y,CW,11,13.8,color='#5F526E')+5
  y=field(items[3],y,30)+11
 else:
  y=text(items[2],M,y,CW,11,13.8,color='#5F526E')+2
  y=text(items[3].replace('- ','• '),M,y,CW,11,13.8,color='#5F526E')+5
  y=text(items[4],M,y,CW,11,14,'GolosBold')+5
  y=field(items[5],y,60)+8
  y=text(items[6],M,y,CW,10.5,13.2)
print('PAGE 2 bottom',y)
ill('questions',W-M-64,106,64)
end(2)

# Page 3
t,b=pages[2];y=begin(3,t,b[0].strip('*'))
ill('topics',W-M-106,82,106)
y=text(b[1],M,y,CW,11,13.8)+12
blocks=re.split(r'(?=\*\*Тема \d)','\n\n'.join(b[2:]))
for i,block in enumerate([z for z in blocks if z.strip()]):
 items=block.strip().split('\n\n')
 if i:
  c.setStrokeColor(HexColor(BORDER));c.setLineWidth(.5);c.line(M,H-y+4,W-M,H-y+4)
 y=text(items[0],M,y,CW,11.5,14.3,'GolosBold',VIOLET)+3
 y=text(items[1],M,y,CW,11,13.75)+3
 y=text(items[2],M,y,CW,11,13.75)+3
 y=text(items[3],M,y,CW,11,13.75,color='#5F526E')+4
 y=field(items[4],y,27)+10
print('PAGE 3 bottom',y)
end(3)

def markdown_table(s):
 rows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in s.splitlines()]
 return [rows[0]]+rows[2:]
def table(rows,y,widths,heights=None,size=10,leading=12.5):
 cells=[[para(cell,widths[j]-12,size,leading,'GolosBold' if i==0 else 'Golos', '#FFFFFF' if i==0 else INK) for j,cell in enumerate(row)] for i,row in enumerate(rows)]
 tb=Table(cells,colWidths=widths,rowHeights=heights)
 tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor(VIOLET)),('ROWBACKGROUNDS',(0,1),(-1,-1),[white,HexColor(PALE)]),('GRID',(0,0),(-1,-1),.5,HexColor(BORDER)),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
 _,h=tb.wrap(CW,H);tb.drawOn(c,M,H-y-h)
 return y+h

# Page 4
t,b=pages[3];y=begin(4,t,b[0].strip('*'))
y=text(b[1],M,y,CW,11,14)+12
rows=markdown_table(b[2]); y=table(rows,y,[42,112,82,160,CW-396],size=10,leading=12.5)+12
y=text(b[3],M,y,CW,11,14)+10
y=text(b[4],M,y,CW,11,14,'GolosBold')+7
y=field(b[5],y,40)
print('PAGE 4 bottom',y)
end(4)

# Page 5
t,b=pages[4];y=begin(5,t,b[0].strip('*'))
for p in b[1:4]:y=text(p,M,y,CW,11,13.8)+7
y+=5
rows=markdown_table(b[4])
for row in rows[1:]: row[3]=row[3].replace(' 2.', '\n2.').replace(' 3.', '\n3.')
y=table(rows,y,[48,105,82,158,CW-393],heights=[41]+[62]*5,size=10,leading=12.5)+14
y=text(b[5],M,y,CW,11.5,14.5,'GolosBold',VIOLET)+9
for i,p in enumerate(b[6:11]):
 c.acroForm.checkbox(name=f'check_{i+1}',tooltip=p.replace('☐','').strip(),x=M,y=H-y-12,size=11,borderWidth=.8,borderColor=HexColor(BORDER),fillColor=white,textColor=HexColor(VIOLET),buttonStyle='check',checked=False,forceBorder=True)
 y=text(p.replace('☐ ','',1),M+20,y,CW-20,11,13.8)+7
y+=3;y=text(b[11],M,y,CW,11,13.8)
print('PAGE 5 bottom',y)
end(5)

# Page 6
t,b=pages[5];y=begin(6,t)
for p in b[:3]:y=text(p,M,y,CW,11.5,15.2)+12
y=text(b[3],M,y,CW,13,17,'GolosBold',VIOLET)+9
for p in b[4].splitlines():y=text(p.replace('- ','• ',1),M,y,CW,11.5,15.2)+7
y+=5;y=text(b[5],M,y,CW,11,14)+20
y=text(b[6],M,y,CW,13,17,'GolosBold',VIOLET)+10
y=text(b[7],M,y)+8
for p in b[8].splitlines():y=text(p.replace('- ','• ',1),M,y,CW-125,11,14)+6
y+=18
box(M,y,CW,58,VIOLET,VIOLET,10)
text('Написать: Dimitryi7510@yandex.ru',M+16,y+19,CW-32,11.5,15,'GolosBold','#FFFFFF')
c.linkURL('mailto:Dimitryi7510@yandex.ru',(M,H-y-58,M+CW,H-y),relative=0)
ill('finish',W-M-155,640,155)
print('PAGE 6 bottom',y+58)
end(6)
c.save()
print(OUT/'content-plan-week.pdf')

