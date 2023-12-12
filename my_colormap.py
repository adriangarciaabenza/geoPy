from matplotlib.colors import ListedColormap

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors

def getRGBfromI(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return (red, green, blue)

def getRGBfromI_norm1(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return (red/255, green/255, blue/255)

def getIfromRGB(rgb):
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    print(red, green, blue)
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

newcolors = [""] * 310
for i in range(10) : newcolors[i] = "w"
newcolors[10] = "darkorange"
for i in range(11,16) : newcolors[i] = "burlywood"
for i in range(16,21) : newcolors[i] = "moccasin"
for i in range(21,31) : newcolors[i] = "lightyellow"
for i in range(31,41) : newcolors[i] = "palegreen"
for i in range(41,61) : newcolors[i] = "greenyellow"
for i in range(61,81) : newcolors[i] = "lightskyblue"
for i in range(81,111) : newcolors[i] = "dodgerblue"
for i in range(111,161) : newcolors[i] = "royalblue"
for i in range(161,211) : newcolors[i] = "darkblue"
for i in range(211,310) : newcolors[i] = "magenta"
#print(newcolors)
newcmp = ListedColormap(newcolors)


i1 = 16747263
colr1 = getRGBfromI(i1)
print(colr1) # returns (255,255,255)

i2 =getIfromRGB(colr1)
print(i1, i2) # returns 2147483647 16777215



#Precipitation scale 
levels = [-100, 10, 50, 100, 200, 300, 500, 700, 1000, 1500, 2000, 3000, 5000]

colors = ['#F76209',
          '#FF9D3C',
          '#FBD744',
          '#FFFFA4',
          '#C9FD82',
          '#80FF48',
          '#80FFFF',
          '#82BFFD',
          '#2991F8',
          '#006AD5',
          '#A217FD',
          '#FF8AFF'
          ]

precipitation_cmap, precipitation_norm = matplotlib.colors.from_levels_and_colors(levels, 
                                                      colors)

monthly_levels = [lev/1.0 for lev in levels]
monthly_ticks = [str(lev/10.0)+ " mm" for lev in levels]
monthly_ticks[0] = "0 mm"

daily_levels = [lev/5.0 for lev in levels]
daily_ticks = [str(lev/10.0)+ " mm" for lev in daily_levels]
daily_ticks[0] = "0 mm"

daily_precipitation_cmap, daily_precipitation_norm = matplotlib.colors.from_levels_and_colors(daily_levels, 
                                                      colors)