"""Minimal 'scan me' flyer: portrait + large QR code linking to the memorial site.
Same landing target as qr_landing (https://drtogbeyfelix.com/).
Outputs flyer_qr.png.  Deps: Pillow + qrcode.
"""
from PIL import Image, ImageDraw, ImageFont
import math

QR_URL = "https://drtogbeyfelix.com/"   # same as qr_landing

W = 1600
IVORY       = (251, 247, 238)
GOLD_DARK   = (158, 121, 56)
GOLD        = (196, 158, 86)
GOLD_PALE   = (224, 200, 148)
INK         = (44, 42, 42)
INK_SOFT    = (66, 64, 64)
SUBTLE      = (128, 124, 124)

SERIF  = "fonts/EBGaramond.ttf"
ITAL   = "fonts/EBGaramond-Italic.ttf"
SCRIPT = "fonts/PinyonScript-Regular.ttf"

def f(s):  return ImageFont.truetype(SERIF, s)
def fi(s): return ImageFont.truetype(ITAL, s)
def sc(s): return ImageFont.truetype(SCRIPT, s)
def fb(s):
    fnt = ImageFont.truetype(SERIF, s)
    try: fnt.set_variation_by_axes([700])
    except Exception: pass
    return fnt

# ---------- floral engine (same as the single flyers) ----------
SAGE_DARK=(96,116,86); SAGE=(142,165,128); SAGE_LIGHT=(180,195,162)
WHITE_PETAL=(252,248,240); PETAL_SHADOW=(210,198,178)
ROSE_PINK=(210,168,158); ROSE_PINK_D=(172,130,122)
SCALE=3

def _make_leaf(length,color,edge,variation=0):
    w=max(int(length*(0.50+variation)),10); h=max(int(length),16); pad=6
    leaf=Image.new("RGBA",(w+pad*2,h+pad*2),(0,0,0,0)); ld=ImageDraw.Draw(leaf)
    ld.ellipse([pad,pad,pad+w,pad+h],fill=color,outline=edge,width=2)
    ld.line([(pad+w/2,pad+4),(pad+w/2,pad+h-2)],fill=edge,width=1)
    hl=tuple(min(255,int(c*1.20)) for c in color)
    ld.arc([pad+1,pad+1,pad+w-1,pad+h-1],200,340,fill=hl,width=2); return leaf
def _paste_leaf(canvas,cx,cy,length,angle_deg,color=SAGE,edge=SAGE_DARK,var=0):
    rot=_make_leaf(length,color,edge,var).rotate(-angle_deg+90,resample=Image.BICUBIC,expand=True)
    canvas.paste(rot,(int(cx-rot.width/2),int(cy-rot.height/2)),rot)
def _make_petal(w,h,fill,edge):
    pad=4; p=Image.new("RGBA",(int(w)+pad*2,int(h)+pad*2),(0,0,0,0)); pd=ImageDraw.Draw(p)
    pd.ellipse([pad,pad,pad+w,pad+h],fill=fill,outline=edge,width=2)
    hl=tuple(min(255,int(c*1.06)) for c in fill[:3])
    pd.arc([pad+1,pad+1,pad+w-1,pad+h-1],200,340,fill=hl,width=1); return p
def _paste_petal(canvas,cx,cy,w,h,angle_deg,fill,edge):
    rot=_make_petal(w,h,fill,edge).rotate(-angle_deg+90,resample=Image.BICUBIC,expand=True)
    canvas.paste(rot,(int(cx-rot.width/2),int(cy-rot.height/2)),rot)
def _paste_rose(canvas,cx,cy,size,fill=WHITE_PETAL,edge=PETAL_SHADOW,center=ROSE_PINK,center_edge=ROSE_PINK_D):
    for ang in range(0,360,60):
        r=math.radians(ang); _paste_petal(canvas,cx+size*0.60*math.cos(r),cy+size*0.60*math.sin(r),size*0.55,size*0.80,ang+90,fill,edge)
    for ang in range(30,390,60):
        r=math.radians(ang); _paste_petal(canvas,cx+size*0.38*math.cos(r),cy+size*0.38*math.sin(r),size*0.46,size*0.62,ang+90,fill,edge)
    inner=tuple(int(c*0.96) for c in fill)
    for ang in range(0,360,72):
        r=math.radians(ang); _paste_petal(canvas,cx+size*0.20*math.cos(r),cy+size*0.20*math.sin(r),size*0.34,size*0.44,ang+90,inner,edge)
    dd=ImageDraw.Draw(canvas); bud=tuple(int(c*0.90) for c in fill)
    dd.ellipse([cx-size*0.22,cy-size*0.22,cx+size*0.22,cy+size*0.22],fill=bud,outline=edge,width=2)
    dd.ellipse([cx-size*0.14,cy-size*0.14,cx+size*0.14,cy+size*0.14],fill=center,outline=center_edge,width=2)
    dd.ellipse([cx-size*0.06,cy-size*0.06,cx+size*0.06,cy+size*0.06],fill=GOLD_PALE)
def _paste_bud(canvas,cx,cy,size,fill=ROSE_PINK,edge=ROSE_PINK_D):
    dd=ImageDraw.Draw(canvas); dd.ellipse([cx-size,cy-size,cx+size,cy+size],fill=fill,outline=edge,width=2)
    hl=tuple(min(255,int(c*1.18)) for c in fill); dd.arc([cx-size+2,cy-size+2,cx+size-2,cy+size-2],200,320,fill=hl,width=2)
def _stem_curve(start,ang_deg,length,curve=0.10,n=50):
    pts=[]; a=math.radians(ang_deg); perp=a+math.pi/2
    for i in range(n):
        u=i/(n-1); off=curve*length*math.sin(u*math.pi)
        pts.append((start[0]+length*u*math.cos(a)+off*math.cos(perp),start[1]+length*u*math.sin(a)+off*math.sin(perp)))
    return pts
def _draw_stem(canvas,pts,base_width=6):
    dd=ImageDraw.Draw(canvas); n=len(pts)
    for i in range(n-1):
        w=int(max(2,base_width-(i/n)*3)); dd.line([pts[i],pts[i+1]],fill=SAGE_DARK,width=w)
def _floral_corner(canvas,cx,cy,sx,sy):
    pts_h=_stem_curve((cx,cy),0 if sx>0 else 180,380*SCALE,curve=0.10*sx*sy,n=50); _draw_stem(canvas,pts_h,base_width=6*SCALE)
    for k,(t,length,side,var) in enumerate([(0.13,64,1,0.0),(0.27,82,-1,0.05),(0.42,98,1,-0.05),(0.58,92,-1,0.0),(0.74,80,1,0.05),(0.90,58,-1,-0.05)]):
        idx=int(t*(len(pts_h)-1)); lx,ly=pts_h[idx]; nxp=pts_h[min(idx+1,len(pts_h)-1)]
        ang=math.degrees(math.atan2(nxp[1]-ly,nxp[0]-lx)); color=SAGE if k%2==0 else SAGE_LIGHT
        _paste_leaf(canvas,lx,ly,length*SCALE,ang+side*65*sy,color=color,var=var)
    pts_v=_stem_curve((cx,cy),90 if sy>0 else -90,290*SCALE,curve=-0.10*sx*sy,n=50); _draw_stem(canvas,pts_v,base_width=6*SCALE)
    for k,(t,length,side,var) in enumerate([(0.16,66,-1,0.05),(0.34,86,1,-0.05),(0.52,92,-1,0.0),(0.72,78,1,0.05),(0.90,56,-1,-0.05)]):
        idx=int(t*(len(pts_v)-1)); lx,ly=pts_v[idx]; nxp=pts_v[min(idx+1,len(pts_v)-1)]
        ang=math.degrees(math.atan2(nxp[1]-ly,nxp[0]-lx)); color=SAGE_LIGHT if k%2==0 else SAGE
        _paste_leaf(canvas,lx,ly,length*SCALE,ang+side*65*sx,color=color,var=var)
    _paste_rose(canvas,cx+sx*28*SCALE,cy+sy*28*SCALE,54*SCALE)
    bx,by=pts_h[int(0.42*len(pts_h))]; _paste_rose(canvas,bx,by-sy*12*SCALE,38*SCALE)
    vx,vy=pts_v[int(0.46*len(pts_v))]; _paste_rose(canvas,vx+sx*12*SCALE,vy,34*SCALE,fill=ROSE_PINK,edge=ROSE_PINK_D,center=GOLD_DARK,center_edge=tuple(int(c*0.7) for c in GOLD_DARK))
    bx,by=pts_h[int(0.75*len(pts_h))]; _paste_bud(canvas,bx+sx*6*SCALE,by+sy*-20*SCALE,14*SCALE)
    bx,by=pts_v[int(0.72*len(pts_v))]; _paste_bud(canvas,bx+sx*-12*SCALE,by+sy*4*SCALE,14*SCALE)
    bx,by=pts_h[int(0.92*len(pts_h))]; _paste_bud(canvas,bx,by-sy*14*SCALE,11*SCALE,fill=WHITE_PETAL,edge=PETAL_SHADOW)
def make_sprig_layer(W_,H_,anchors):
    layer=Image.new("RGBA",(W_*SCALE,H_*SCALE),(0,0,0,0))
    for (cx,cy,sx,sy) in anchors: _floral_corner(layer,cx*SCALE,cy*SCALE,sx,sy)
    return layer.resize((W_,H_),Image.LANCZOS)

# ---------- clean gold-framed oval portrait (transparent outside ellipse) ----------
oval=Image.open("oval.png").convert("RGBA")
ow0,oh0=oval.size
mask=Image.new("L",(ow0,oh0),0); ImageDraw.Draw(mask).ellipse([2,2,ow0-3,oh0-3],fill=255)
oval.putalpha(mask)
pw=520; ph=int(pw*oh0/ow0); oval_r=oval.resize((pw,ph),Image.LANCZOS)

# ---------- big QR ----------
import qrcode
qr=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,border=2)
qr.add_data(QR_URL); qr.make(fit=True)
modules=qr.modules_count+2*qr.border
box=max(1,round(760/modules))
qr_img=qr.make_image(fill_color=INK,back_color=IVORY).convert("RGB").resize((modules*box,modules*box),Image.NEAREST)
qs=qr_img.width

# ---------- helpers ----------
def tw(draw,s,fn):
    b=draw.textbbox((0,0),s,font=fn); return b[2]-b[0]
def tracked(draw,cx,top,s,fn,fill,track):
    widths=[tw(draw,ch,fn) for ch in s]; total=sum(widths)+track*(len(s)-1); x=cx-total/2
    for ch,w in zip(s,widths): draw.text((x,top),ch,font=fn,fill=fill); x+=w+track
def divider(d,cx,y,half=200,fill=GOLD_DARK):
    d.line([(cx-half,y),(cx-26,y)],fill=fill,width=2); d.line([(cx+26,y),(cx+half,y)],fill=fill,width=2)
    d.polygon([(cx,y-9),(cx+11,y),(cx,y+9),(cx-11,y)],fill=fill)

# ---------- vertical layout ----------
m=60; CX=W//2; y=m+70
heights=[]  # measured as we go (we set H after)
def block(h):
    global y; y+=h

y_tag=y; y+=64
y_portrait=y; y+=ph+34
y_name=y; y+=74
y_dates=y; y+=58
y_rule=y; y+=58
y_qr=y; y+=qs+30
y_cap=y; y+=46
y_cap_en=y; y+=52
y_url=y; y+=58
y_rip=y; y+=86
H=y+m+30

# ---------- render ----------
img=Image.new("RGB",(W,H),IVORY); d=ImageDraw.Draw(img)
# frame
d.rectangle((m,m,W-m,H-m),outline=GOLD_DARK,width=2)
d.rectangle((m+12,m+12,W-m-12,H-m-12),outline=GOLD_PALE,width=1)
# floral corners
inset=m+30
sprig=make_sprig_layer(W,H,[(inset,inset,1,1),(W-inset,inset,-1,1),(inset,H-inset,1,-1),(W-inset,H-inset,-1,-1)])
img.paste(sprig,(0,0),sprig)
# tagline
d.text((CX,y_tag),"En Mémoire de Notre Très Cher et Regretté",font=fi(40),fill=INK_SOFT,anchor="ma")
# portrait
img.paste(oval_r,(CX-pw//2,y_portrait),oval_r)
# name + dates
tracked(d,CX,y_name,"Dr. TOGBEY Kwamy Maoussi Félix",fb(50),INK,track=4)
tracked(d,CX,y_dates,"20 novembre 1948  –  24 mai 2026",fi(34),SUBTLE,track=2)
# divider
divider(d,CX,y_rule,half=210)
# big QR with gold frame
qx=CX-qs//2; card=18
d.rounded_rectangle((qx-card,y_qr-card,qx+qs+card,y_qr+qs+card),radius=14,fill=IVORY,outline=GOLD_DARK,width=3)
img.paste(qr_img,(qx,y_qr))
# caption + url + tribute
d.text((CX,y_cap),"Scannez ce code pour en savoir plus",font=fb(40),fill=GOLD_DARK,anchor="ma")
d.text((CX,y_cap_en),"Scan the code to learn more about him",font=fi(32),fill=INK_SOFT,anchor="ma")
tracked(d,CX,y_url,"DRTOGBEYFELIX.COM",f(30),SUBTLE,track=8)
d.text((CX,y_rip),"Repose en paix.",font=sc(64),fill=GOLD_DARK,anchor="ma")

img.save("flyer_qr.png",dpi=(300,300))
print("flyer_qr",img.size,"QR px",qs,"->",QR_URL)
