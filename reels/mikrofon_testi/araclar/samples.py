import cv2
from PIL import Image, ImageDraw, ImageFont
A0,CUT,B0=2.5,1.866667,5.433333
cap=cv2.VideoCapture("sdr_a.mp4")
picks=[(4,"0.13 sn"),(22,"0.73 sn"),(42,"1.40 sn"),(66,"2.20 sn"),(86,"2.87 sn"),(100,"3.33 sn")]
tiles=[]; f=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf",26)
for n,lab in picks:
    t=n/30; src=A0+t if t<CUT else B0+(t-CUT)
    cap.set(cv2.CAP_PROP_POS_FRAMES,round(src*30)); ok,fr=cap.read()
    bg=Image.fromarray(cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)).convert("RGBA")
    bg.alpha_composite(Image.open(f"work/ov/{n:04d}.png"))
    s=bg.convert("RGB").resize((432,768),Image.LANCZOS); d=ImageDraw.Draw(s)
    d.rectangle((0,0,140,40),fill=(0,0,0)); d.text((10,6),lab,font=f,fill="white"); tiles.append(s)
    if n==100:
        g=bg.copy(); gd=ImageDraw.Draw(g,"RGBA"); F=ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf",44)
        gd.rectangle((0,0,1080,230),fill=(255,0,0,90)); gd.rectangle((0,1500,1080,1920),fill=(255,0,0,90)); gd.rectangle((940,230,1080,1500),fill=(255,0,0,60))
        gd.text((30,90),"Instagram üst arayüz",font=F,fill="white"); gd.text((30,1680),"Instagram alt arayüz",font=F,fill="white")
        g.convert("RGB").resize((540,960),Image.LANCZOS).save("frames/guvenli_alan.jpg",quality=90)
sheet=Image.new("RGB",(432*3+20,768*2+10),"white")
for i,s in enumerate(tiles): sheet.paste(s,((i%3)*442,(i//3)*778))
sheet.save("frames/ornek_kareler.jpg",quality=90)
