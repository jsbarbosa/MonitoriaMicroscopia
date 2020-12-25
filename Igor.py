#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

from glob import glob


# In[1]:


def makePlot(filename, data, i = 0):
    fig, ax = plt.subplots(1)
    x = data[:, 3*i + 2]*1e6
    y = data[:, 3*i + 1]*1e9
    ax.plot(x, y, lw = 1)
    ax.invert_xaxis()
    ax.set_xlabel("ZSnsr ($\mu$m)")
    ax.set_ylabel("Defl (nm)")
    fig.savefig("Plots/%s.jpg"%filename, dpi = 300)
    plt.close()
    
    temp = np.zeros((x.shape[0], 2))
    temp[:, 0] = x
    temp[:, 1] = y
    np.savetxt("Data/%s.csv"%filename, temp, delimiter = "\t", newline="\r\n", header = "ZSnsr (um)\tDefl (nm)")
    
    del temp
    del fig
    del ax
    del x
    del y

def extractByName(name):
    with open(name) as file:
        text = file.readlines()
                
    files = []
    j = 0
    for i in range(len(text)):
        line = text[i]
        if line == "\n":
            temp = "".join(text[j:i-1])
            temp = temp.replace(",", ".")
            files.append(temp)
            j = i
            
    del text
            
    for i in range(len(files)):
        data = np.genfromtxt(StringIO(files[i]), delimiter = "\t", skip_header = 1)
        if i == 0:
            name_line = files[i].split("\n")[0]
        else:
            name_line = files[i].split("\n")[1]
            data = data[1:]
        parts = name_line.split("\t")
        if len(parts) == 3:
            name = parts[0].replace("Raw", "")
            makePlot(name, data)
        if len(parts) > 3:
            n = len(parts) // 3
            for i in range(n):
                name = parts[3*i].replace("Raw", "")
                makePlot(name, data[1:], i)
        del data
    del files
    print(name, "done")
# cols = ["Raw", "Defl", "ZSnsr"]


# In[2]:


# name = "fibrina0002Raw++.txt"

files = glob("*.txt")

print(files)


# In[ ]:



for file in files:
    extractByName(file)


# In[15]:





# In[16]:





# In[ ]:




