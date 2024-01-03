from PIL import Image
import numpy
import threading
from tqdm import tqdm

global pixAvg
# wooooo yeah multithreading
def calcPixAverages(hi):
    for wi in range(0, w):
        pixAvg[hi][wi] = numpy.average(imageArray[hi][wi])            

print("--- HCNC's Wacky Pixel Sorter - Version 1 ---")

# file
filename = input("filename > ")

with Image.open(filename) as image: 
    print("opened " + filename)
    imageArray = numpy.array(image)
    # ARRAY DIMENSIONS:
    # imageArray.shape[0] HEIGHT
    # imageArray.shape[1] WIDTH
    # imageArray.shape[2] CHANNELS
    w = imageArray.shape[1]
    h = imageArray.shape[0]
    c = imageArray.shape[2]
    print("image converted to np array (width:", str(imageArray.shape[1]) + ", height:", str(imageArray.shape[0]) + ", channels:", str(imageArray.shape[2]) + ")")
    pixAvg = numpy.zeros((h, w))

    pixelAverageThreads = []

    print("starting pixel average threads")
    for hi in tqdm(range(0, h)):
        pixelAverageThreads.append(threading.Thread(target=calcPixAverages, args=(hi,)))
        pixelAverageThreads[hi].start()
    print("started pixelaveragethreads for each column")


    shouldRotate = input("is image vertical (y/n) > ") == "y"

    # sorter settings
    contrastMap = float(input("pixel sort bound contrast > "))
    useMaxContrast = input("is bound maximum (y/n) >  ") == "y"

    pixelMask = numpy.zeros((h, w))

    print("waiting for pixel average threads to finish")
    for hi in tqdm(range(0, h)):
        pixelAverageThreads[hi].join()
    print("done! saved pixel averages to nparray")
    print("creating pixel brightness mask")
    if (useMaxContrast):
        for hi in tqdm(range(0, h)):
            for wi in range(0, w):
                pixelMask[hi][wi] = pixAvg[hi][wi] < contrastMap
    else:
        for hi in tqdm(range(0, h)):
            for wi in range(0, w):
                pixelMask[hi][wi] = pixAvg[hi][wi] > contrastMap

    print("created pixel brightness mask")

    spanMap = numpy.zeros((h, w))
    
    trackingSpan = False
    spanStartW = -1
    counter = 0

    # This method of keeping track of spans is straight from Acerola's video and has 
    # no major performance benefit here because it's not dealing with GPU threads being dispatched

    # TODO: Does this actually make it slower (can i do this better)?
    print("finding pixel spans")
    for hi in tqdm(range(0, h)):
            for wi in range(0, w):
                # If hasn't started, start
                if (pixelMask[hi][wi] and not trackingSpan):
                        spanStartW = wi
                        trackingSpan = True
                # Let it overflow into this so we get a counter = 1 to start without setting it 
                # (small performance boost, but hey we're sorting thousands of columns gimme a break)
                if (pixelMask[hi][wi] and trackingSpan): 
                        counter += 1                
                # if we didn't execute the above this means pcm[hi][wi] is false so the span is over
                elif (trackingSpan):
                        spanMap[hi][spanStartW] = counter
                        counter = 0
                        trackingSpan = False
    print("created span map")

    print("sorting spans")
    for hi in tqdm(range(0, h)):
            for wi in range(0, w):
                if (spanMap[hi][wi] != 0):
                    # TODO: Why does a weird type error require this?
                    intified_spanlen = int(spanMap[hi][wi])
                    # make span array
                    span = numpy.zeros((intified_spanlen, c))
                    for i in range(0, intified_spanlen):
                        span[i] = imageArray[hi][min(wi+i, w-1)]
                    # sort span array
                    span = span[numpy.argsort(span.sum(axis=1))]
                    # put new span array to image
                    for i in range(0, intified_spanlen):
                        imageArray[hi][min(wi+i, w-1)] = span[i]
    print("final array complete")

    sorted = Image.fromarray(imageArray)
    print("np array converted to image")

    name = "./output"

    if (shouldRotate): 
        sorted = sorted.rotate(90, expand=True)
        name += "-v"

    sorted.show()
    if (input("should rotate 180 (y/n) > ") == "y"): sorted = sorted.rotate(180)

    if (useMaxContrast): name += "-max"
    else: name += "-min"
    name += str(contrastMap)


    name += "-"
    sorted.save(name+filename)
    print("image saved")