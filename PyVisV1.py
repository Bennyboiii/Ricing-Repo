'''
PyVis developed by Ben Cochrane

This program is a visualizer which
does not require an audio processing server
(like MPD or pulseaudio), instead running on
a 3rd party driver (Virtual Audio Cable)
which does not require any configuration.
It only works on Windows for now, however
it has the potential to be compatible with
MacOS and most Linux Distros. I may add
an ANSI Terminal mode for ricing as well.

INSTRUCTIONS:
First, Type the width and the height of the
window you want into the dialog box
(tuple separated by a comma, no parentheses)
Type a 3 number RGB value in the window
(Individual numbers separated by a comma)
, and press ENTER to change the Bar Colour,
or press RSHIFT to change the background
colour. The J, K and L buttons change the
placement of the bars, and the D button
makes it go disco. 

'''



import pygame, sys, random, math, pyaudio, time, tkinter as tk, os
import numpy as np
from tkinter import simpledialog
pygame.init()


application_window = tk.Tk()
application_window.withdraw()

(w,h)= (0,0)
while (w,h) == (0,0):
    answer = simpledialog.askstring("Size", "Input Window Size (e.g.640,480)?")
    try:
        (w,h) = answer.split(",")
    except ValueError:
        (w,h)= (0,0)
        
(x,y)= (0,0)
while (x,y) == (0,0):
    answer = simpledialog.askstring("Position", "Input Window Position (e.g.10,10)?")
    try:
        (x,y) = answer.split(",")
    except ValueError:
        (x,y)= (0,0)


os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (int(x),int(y))
    

    

              #Vis Config#
#---------------------------------------#

size = width, height = int(w), int(h)
screen = pygame.display.set_mode(size, pygame.NOFRAME)
pygame.display.set_caption('')

whitetxt = [255, 255, 255]
redtxt = [255, 0, 0]


               #Vis Vars#
#---------------------------------------#


#Change this stuff to change the look of the visualizer
bars = 16                  # Number of bars
barspacing = 5             # Spacing between bars (pixels)
barcolour = [(random.randint(0, 255)) for i in range(3)]  # Change the Bar Colour (RGB)
#[(random.randint(0, 255)) for i in range(3)] If you want random colours change the value to this
backcolour = [214,209,185]     # Use this to change the background colour (RGB)



initcolour = barcolour
barheights = [1 for i in range(bars)]
barwidth = (width // bars) - barspacing
visposY = height / 2
visposX = 2.5
CHUNK = 2048
bar = []
RATE = 44100
TARGETS = [20*math.pow(1000**(1/bars), i) for i in range(bars)]
count = 0
SIZE = 90
font = pygame.font.SysFont("Consolas", 14)
rainbow = -1
exceptiontext = ''
userinput=''

maxValue = 2**16
p=pyaudio.PyAudio()

info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,
              input=1, frames_per_buffer=CHUNK)

               #Functions#
#---------------------------------------#
def getrandomcolour():
    return[(random.randint(0, 255)) for i in range(3)]
            
        
              #Main Loop#
#---------------------------------------#

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

                #Control#
#---------------------------------------#

        if event.type == pygame.KEYDOWN:
            if event.unicode in ['0','1','2','3','4','5','6','7','8','9',',']:
                userinput=userinput+event.unicode
            if event.key == pygame.K_BACKSPACE:
                userinput = userinput[:-1]
            if event.key == pygame.K_RETURN:
                rgb=userinput.split(",")
                if len(rgb) != 3:
                    exceptiontext = 'Invalid Input(s), try again'
                    userinput = ''
                
                else:
                    red = int(rgb[0])
                    green = int(rgb[1])
                    blue = int(rgb[2])
                    initcolour = [red, green, blue]
                    userinput = ''
                    exceptioninput = ''
            if event.key == pygame.K_RSHIFT:
                rgb=userinput.split(",")
                if len(rgb) != 3:
                    exceptiontext = 'Invalid input(s), try again'
                    userinput = ''
                
                else:
                    red = int(rgb[0])
                    green = int(rgb[1])
                    blue = int(rgb[2])
                    backcolour = [red, green, blue]
                    userinput = ''
                    exceptioninput = ''
                    
               
                
            if event.key == pygame.K_d:
                rainbow = rainbow * -1

            elif event.key == pygame.K_j:
                visposY = height
                SIZE = 45

            elif event.key == pygame.K_k:
                visposY = 0
                SIZE = 45

            elif event.key == pygame.K_l:
                visposY = height / 2
                SIZE = 90
                
                


    data = np.frombuffer(stream.read(CHUNK),dtype=np.int16).astype(np.float)

          #Volume Measurement#
#---------------------------------------#
    count=0
    for TARGET in TARGETS:
        fft = abs(np.fft.fft(data).real)
        fft = fft[:int(len(fft)/2)] # keep only first half
        freq = np.fft.fftfreq(CHUNK,1.0/RATE)
        freq = freq[:int(len(freq)/2)] # keep only first half
        assert freq[-1]>TARGET, "ERROR: increase chunk size"
        val = fft[np.where(freq>TARGET)[0][0]]
        perc = (((round(val, 0)/maxValue) * 100)/SIZE)
        barheights[count] = (round(perc, 0))
        count = count + 1


                    


    
           #Bar Assignments#
#---------------------------------------#
    
    #print(barheights)

    bar=[]
    visposX = 2.5
    for barheight in barheights:
        bar.append(pygame.Rect(visposX,visposY-barheight, barwidth, barheight*2-1))

        
        visposX+=barspacing+barwidth


   
    screen.fill(backcolour)
    exceptiontext = ''
    try:
        if rainbow == 1:
            barcolour = getrandomcolour()
            for b in bar:
                pygame.draw.rect(screen, barcolour, b, 0)
    
        else:
            barcolour = initcolour
            for b in bar:
                pygame.draw.rect(screen, barcolour, b, 0)

    except TypeError:
            barcolour = getrandomcolour()
            exceptiontext = 'Invalid Input(s), try again'
            
    exptext=font.render(exceptiontext, True, redtxt)
    rgbchngtext=font.render(userinput,True,whitetxt)
    screen.blit(rgbchngtext,(10,10))
    screen.blit(exptext, (width - 230, 10))
    pygame.display.flip()
    time.sleep(0.01)

'''
THINGS TO DO:
- add an ANSI Terminal mode
- improving visualization in the higher frequencies
- adding more bars (does require a shit ton of data which could lag the computer)
- multithreading???????
THINGS TO REMEMBER:
- 214,209,185
- 153,197,233
'''
    
    
