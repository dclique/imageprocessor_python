
# Name: Alexander Ding
#



import math
import struct


# PROBLEM 1

# parse the file named fname into a dictionary of the form 
# {'width': int, 'height' : int, 'max' : int, 'pixels' : (int * int * int) list}
def parsePPM(fname):
    dict = {}
    f = open(fname, 'rb')

    #the first line is the 'magic number'
    line = f.readline()
    if line != "P6\n":
        return "NOT A SUPPORTED PPM FILE"
    
    #the second line contains width and height separated by a space
    line = f.readline()
    widthheight = line.split()

    #the third line contains the max pixel value
    line = f.readline()
    maxpixvalue = line.split()

    #fourth line contains binary pixel values that must be unpacked
    line = f.read()
    line2 = struct.unpack("{0}B".format(len(line)), line)
    
    #add all the different elements to dict
    dict["width"] = int(widthheight[0])
    dict["height"] = int (widthheight[1])
    dict["max"] = int(maxpixvalue[0])

    pixels = []
    for x in range(0, len(line2)-2, 3):
        pixels += [(line2[x],line2[x+1],line2[x+2])]
        
    dict["pixels"] = pixels

    f.close()

    return dict



# a test to make sure you have the right format for your dictionaries
def testParsePPM():
    return parsePPM("example.ppm") == {'width': 2, 'max': 255, 'pixels': [(10, 23, 52), (82, 3, 215), (30, 181, 101), (33, 45, 205), (40, 68, 92), (111, 76, 1)], 'height': 3}

# write the given ppm dictionary as a PPM image file named fname
# the function should not return anything
def unparsePPM(ppm, fname):

    f = open(fname, 'w')

    #write the 'magic number' to the first line
    f.write("P6\n")

    #write the width, height, and max value in the correct format
    width = ppm["width"]
    height = ppm["height"]
    max = ppm["max"]
    f.write("{0} {1}\n{2}\n".format(width,height,max))

    #pack into binary form and write to file
    pixels = ppm["pixels"]
    packedline = ""
    for tuple in pixels:
        for value in tuple:
            packedline += struct.pack("B", value)    
    f.write(packedline)
    
    f.close()
    

    

# PROBLEM 2
def negate(ppm):

    #replace each pixel with (max - pixel)
    max = ppm["max"]
    for x in range(len(ppm["pixels"])):
        ppm["pixels"][x] = (max - ppm["pixels"][x][0], max - ppm["pixels"][x][1], max - ppm["pixels"][x][2])

    return ppm




# PROBLEM 3
def mirrorImage(ppm):

    #set up new dict
    dict = {}
    width = ppm["width"]
    height = ppm["height"]
    dict["width"] = width
    dict["height"] = height
    dict["max"] = ppm["max"]
    dict["pixels"] = []

    for y in range(height):
        for x in range(width):
            dict["pixels"] += [ppm["pixels"][y*(width) + width-1-x]]

    return dict


# PROBLEM 4

# produce a greyscale version of the given ppm dictionary.
# the resulting dictionary should have the same format, 
# except it will only have a single value for each pixel, 
# rather than an RGB triple.
def greyscale(ppm):

    #set up new dict
    dict = {}
    width = ppm["width"]
    height = ppm["height"]
    dict["width"] = width
    dict["height"] = height
    dict["max"] = ppm["max"]
    dict["pixels"] = []

    #iterate through pixels, adding the 'average' of the RGB values to the dict
    for x in range(len(ppm["pixels"])):
        value = 0.299 * ppm["pixels"][x][0] + 0.587 * ppm["pixels"][x][1] + 0.114 * ppm["pixels"][x][2]
        value2 = int(round(value))
        dict["pixels"] += [value2]
        
    return dict
    

# take a dictionary produced by the greyscale function and write it as a PGM image file named fname
# the function should not return anything
def unparsePGM(pgm, fname):

    f = open(fname, 'w')

    #write the 'magic number' to the first line
    f.write("P5\n")

    #write the width, height, and max value in the correct format
    width = pgm["width"]
    height = pgm["height"]
    max = pgm["max"]
    f.write("{0} {1}\n{2}\n".format(width,height,max))

    #pack into binary form and write to file
    pixels = pgm["pixels"]
    
    packedline = ""
    for value in pixels:
        packedline += struct.pack("B", value)
    
    f.write(packedline)
    
    f.close()



# PROBLEM 5

# gaussian blur code adapted from:
# http://stackoverflow.com/questions/8204645/implementing-gaussian-blur-how-to-calculate-convolution-matrix-kernel
def gaussian(x, mu, sigma):
  return math.exp( -(((x-mu)/(sigma))**2)/2.0 )

def gaussianFilter(radius, sigma):
    # compute the actual kernel elements
    hkernel = [gaussian(x, radius, sigma) for x in range(2*radius+1)]
    vkernel = [x for x in hkernel]
    kernel2d = [[xh*xv for xh in hkernel] for xv in vkernel]

    # normalize the kernel elements
    kernelsum = sum([sum(row) for row in kernel2d])
    kernel2d = [[x/kernelsum for x in row] for row in kernel2d]
    return kernel2d

# blur a given ppm dictionary, returning a new dictionary  
# the blurring uses a gaussian filter produced by the above function
def gaussianBlur(ppm, radius, sigma):
    # obtain the filter
    gfilter = gaussianFilter(radius, sigma)

    #size of 2D array gfilter
    filtersize = 2* radius + 1

    #set up new dict
    dict = {}
    width = ppm["width"]
    height = ppm["height"]
    dict["width"] = width
    dict["height"] = height
    dict["max"] = ppm["max"]
    dict["pixels"] = []

    #iterate through each pixel
    for y in range(height):
        for x in range(width):

            #calculate RGB values for a pixel after applying blur
            pixvalueR = 0
            pixvalueG = 0
            pixvalueB = 0
            
            #iterate through each element in gfilter matrix
            for j in range(filtersize):
                for i in range(filtersize):

                    #clamp out of bound coords
                    xcoord = x - radius + i
                    if xcoord < 0:
                        xcoord = 0
                    elif xcoord >= width:
                        xcoord = width-1
                            
                    ycoord = y - radius + j
                    if ycoord < 0:
                        ycoord = 0
                    elif ycoord >= height:
                        ycoord = height-1

                    #add the product of gfilter value and corresponding coordinate to pixvalue for each color
                    pixvalueR += gfilter[i][j] * ppm["pixels"][ycoord*width + xcoord][0]
                    pixvalueG += gfilter[i][j] * ppm["pixels"][ycoord*width + xcoord][1]
                    pixvalueB += gfilter[i][j] * ppm["pixels"][ycoord*width + xcoord][2]

                    red = int(round(pixvalueR))
                    green = int(round(pixvalueG))
                    blue = int(round(pixvalueB))
            dict["pixels"] += [(red,green,blue)]

    return dict
