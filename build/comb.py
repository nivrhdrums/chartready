import sys
from PIL import Image
fs=sys.argv[2:]; ims=[Image.open(f) for f in fs]; w=max(i.width for i in ims); h=max(i.height for i in ims)
S=Image.new('RGB',(w*len(ims)+10*(len(ims)-1),h),'white')
for k,im in enumerate(ims): S.paste(im,(k*(w+10),0))
S.save(sys.argv[1])
