from PIL import Image

print("--- HCNC's Goofy Image Resizer For Photo Class Because For Some Reason Everything Has To Be 1500px On The Long Side And At 300 DPI - Version 1 ---")
print ("(HCNCGIRFPCBFSREHTB1500pxOTLSAA300DPI)")
infile = input("filename > ")
im = Image.open(infile)
if (im.height > im.width):
    size = int((im.width/im.height)*1500), 1500
    print("portrait")
else:
    size = 1500, int((im.height/im.width)*1500)
    print("landscape")

im.thumbnail(size, Image.Resampling.LANCZOS)
im = im.convert('RGB')
im.save(infile + "-new.jpg", dpi=(300,300))