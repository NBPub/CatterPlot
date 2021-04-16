# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 12:25:31 2021

@author: NBPub
"""

# libraries
import os
os.chdir(os.path.dirname(__file__))

from guizero import App, Text, PushButton, Picture, Window
import pickle as pickle
import requests as re
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import pi


def CatAPI_fetch():
    cats = re.get("https://api.thecatapi.com/v1/breeds").json() # import data as JSON file
    cat = pd.DataFrame(cats) # convert to data frame
    
    # fix formatting of column names
    fix =  [cat.columns[i].replace("_", ' ') for i in range(0,len(cat.columns))]
    cat.columns = fix
    
    # description data to be used for fancy charting
    # for catone, ignoring: hairless, indoor
    catinfo = cat.loc[:,['name','temperament', 'image', 'alt names', 'description', 'weight', 'origin']].set_index('name')
    catone = cat.loc[:, ['name',  'short legs','hypoallergenic','suppressed tail', 'lap', 'hairless', 'natural']].set_index('name')
    
    # things to maybe remove from drop later
    # weight, life_span
    
    # dropping adaptability, affection_level due to lack of spread and to reduce clutter
    # dropping bidability and cat_friendly due to lack of data
    
    cat = cat.drop(columns = [ 'bidability', 'cat friendly', 'adaptability', 'affection level',
            'weight', 'temperament', 'origin', 'life span',
            'id','cfa url','vetstreet url', 'vcahospitals url', 'lap', 'experimental',
            'country codes', 'country code', 'description', 'natural', 'rex', 'suppressed tail',
            'alt names', 'indoor', 'hairless', 'rare', 'short legs','hypoallergenic',
            'wikipedia url',  'reference image id', 'image',])
    cat = cat.set_index('name')
    
    
    
    
    # extract means for background shading
    attributes = cat.columns
    catmeans = [round(np.mean(cat[attributes[i]])) for i in range(len(attributes))]
    
    
    # angles for each category, reduce amount of categories if it looks cluttered
    # calculates position/portion of perimeter (2*pi*r, where r = 1) for each category
    angles = [x / len(catmeans) * 2 * pi for x in range(len(catmeans))]
    angles2 = np.append(angles, angles[0]) # repeat first value to close circle 
    catmeans = np.append(catmeans, catmeans[0]) # again, append last values to close
    
    with open('cats.pkl', 'wb') as f:
        pickle.dump([cat, catinfo, catone, catmeans, attributes, angles2, angles], f)
    
    try:
        getdata.destroy()
        PLOTbutton = PushButton(app, command = CatterPlot, text = 'Generate Cat plot?', align = 'right', height = 'fill')
        PLOTbutton.text_size = 16
        PLOTbutton.bg = 'SpringGreen3'
        PLOTbutton.focus()
    except:
        pass
    
def CatterPlot():
    with open('cats.pkl', 'rb') as f:
        cat, catinfo, catone, catmeans, attributes, angles2, angles = pickle.load(f)
    sample = cat.sample()
    values = sample.to_numpy()[0]
    values = np.append(values, values[0])
    samplename = sample.index[0]
    
    if (catinfo.loc[samplename, 'alt names']) == '' or pd.isnull(catinfo.loc[samplename, 'alt names']):
        AKAtext = '(no alt names)'
    else:
        AKAtext = 'AKA: ' + catinfo.loc[samplename, 'alt names']
        
    checks = catone.loc[samplename,:]
    checkprint = checks[checks>0]
    bullet_txt = ''
    for i,val in enumerate(checkprint.index):
        bullet_txt = bullet_txt + '• ' + val + '  '
    
    
    # define figure and axes
    plt.figure(figsize = (12,8))
    
    # Image
    ax1 = plt.subplot(121)
    plt.plot()
    ax1.axis('off')
    
    if catinfo.loc[samplename, 'image'] == {} or pd.isna(catinfo.loc[samplename, 'image']):
        disclaimer = 'No image for ' + samplename
        ax1.set_title(disclaimer)
        ax1.text(0, 0.05, AKAtext)
        ax1.text(-.05, 0.05, catinfo.loc[samplename, 'weight']['metric'] + ' kg')
        ax1.text(-0.5, 0.035, bullet_txt)
        d = ax1.text(-0.5, 0, catinfo.loc[samplename,'description'], wrap = True)
    else:
        sampleimg = Image.open(re.get(catinfo.loc[samplename, 'image']['url'], stream=True).raw)
        ax1.imshow(sampleimg)
        imgtitle = samplename + ' (' + catinfo.loc[samplename, 'origin'] + ')'
        ax1.set_title(imgtitle, fontsize = 14, fontweight = 'heavy')
        x,y = sampleimg.size
        if y > x:
            delta = y/6
            uppers = (14,10)
        else:
            delta = y/3
            uppers = (8,5)
        ax1.text(-0.5, -y/uppers[0], catinfo.loc[samplename, 'weight']['metric'] + ' kg')
        a = ax1.text(x/5, -y/uppers[0], AKAtext, wrap = True)
        ax1.text(-0.5, -y/uppers[1], bullet_txt)
        d = ax1.text(0, y+delta, catinfo.loc[samplename,'description'],wrap = True, fontsize = 'small')
        a._get_wrap_line_width = lambda : 275
        
    d._get_wrap_line_width = lambda : 350  #  wrap to 300 screen pixels
    
    # Radar Plot
    ax = plt.subplot(122, polar = "True")
    ax.spines['polar'].set_visible(False)
    
    # plot sample data over mean as background
    plt.polar(angles2,values, marker = 'o') # sample dots
    plt.fill(angles2,values,alpha = 0.2) # sample fill
    plt.fill(angles2,catmeans,alpha = 0.2, color = 'grey') # mean background fill
    
    # ticks
    plt.xticks(angles,attributes, color = 'black') # changes lines to match up with number of values, adds label to each one
    ax.set_rlabel_position(15)
    plt.yticks([1,3,5], fontweight = 'bold') # reduce y ticks an labels
    plt.ylim(0,6)
    
    plt.title(catinfo.loc[samplename,'temperament'], fontweight = 'bold', fontsize = 10)
    catcount = 'CatAPI avg (n=' + str(len(cat)) + ')'
    plt.text(1,5.85,catcount, color = 'grey')
    plt.text(1.05,6.25,samplename,color = 'blue')
    plt.savefig('cat.png')
    window = Window(app, title = samplename + 'Cat', width = 1200, height = 900)
    picture = Picture(window, image = 'cat.png')
    plt.close()

app = App(title = 'The Cat API Explorer', bg = 'linen', width = 500, height = 300)
description = Text(app, text = 'Welcome to the Cat API explorer. \n \n Take data from TheCatAPI.com and discover some cats!', align = 'top', width = 'fill')
description.font = 'Arial Narrow'

APIbutton = PushButton(app, command = CatAPI_fetch, text = 'Retrieve Cat API data', align = 'left', height = 'fill')
APIbutton.text_size = 16
APIbutton.bg = 'indian red'

if os.path.exists('cats.pkl'):
    PLOTbutton = PushButton(app, command = CatterPlot, text = 'Generate Cat plot?', align = 'right', height = 'fill')
    PLOTbutton.text_size = 16
    PLOTbutton.bg = 'SpringGreen3'
else:
    getdata = Text(app, text = 'Data fetch required to generate plots.', align = 'right')

app.display()
