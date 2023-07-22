#!/usr/bin/env python
# coding: utf-8

# In[46]:


"""
Author: Jason Greaves-Taylor

Created: 2023-07-18

Last Modified:

Purpose: This module contains functions for the purpose of simulating network traffic in various configurations for the purpose of modeling. It is similar the network simulation library in MatLab. It utilizes the random as well as the numpy and string libraries for data generation and distibution fitting.
"""

import random
import numpy as np
import string

def timeDiff(mu):
    """
    generates a time delay using the exponetial distrubiton based on inputted mu.
    
    returns:
        delay: generated time delay
    """
    lambd = 1/mu
    
    delay = round(random.expovariate(lambd))
    
    return delay

def trafficFTP():
    """
    Generate network traffic similar to FTP using an exponential distribution for the time delay and a lognormal diribution for the payload.
    
    returns:
        payload: Generated network traffic as a string of ASCI characters.
        timedelay: the delay of time before sending to the socket
        
    """
    
    #hard coded parameters 
    mu_payload = 3.90406
    sigma = 0.155111
    mu = 164.488
    
    #generate payload
    packet_size = round(10*(random.lognormvariate(mu_payload, sigma))) #this determines the size of the packets in the payload
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=packet_size)).encode() #this is the actual payload
    
    #generate time delay
    timedelay = timeDiff(mu)
    
    return (payload, timedelay)
    
def videoConferencing():
    """
    This funtion generates video conferencing data for modeling. It determines if the frame is full or not and returns a packet size , generated from a weibull distribution if not full and a time delay.
    
    returns:
        packet_size: the size of the packets returned in the video conference
        timedelay: the delay of time before sending to the socket
        
    """
    
    #hard coded parameters
    n = 1 #number of trials
    p = 0.7211 #probablity of success
    alpha = 769.826
    beta = 1.51123
    mu = 6.6584
    
    #check if frame is full
    isFullFrame = np.random.binomial(n, p, 1)
    if isFullFrame == True:
        packet_size = 1500
    else:
        packet_size = int(random.weibullvariate(alpha, beta))
        if packet_size > 1500:
            packet_size = 1500
    
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=packet_size)).encode() #this is the actual payload
    #timedelay
    timedelay = timeDiff(mu)
        
    return (payload, timedelay)

def webBrowsing():
    """
    This funtion generates web browsing data for modeling. It determines if the frame is full or not and returns a packet size , generated from a weibull distribution if not full and a time delay.
    
    returns:
        packet_size: the size of the packets returned in the video conference
        timedelay: the delay of time before sending to the socket
        
    """
    #hard coded parametes
    n = 1
    p1 = 0.3836 #probability of 1500 bytes
    p2 = 0.5458 #probability of 576
    p3 = 0.0706 #probability of neither 1500 nor 576
    alpha = 2.13486
    beta = 304.27
    mu = 26.6506
    
    #check if frame is full
    isFullFrame = np.random.multinomial(1, [p1, p2, p3], size = 1)
    if isFullFrame[0,0] == True: #checks if frame is at 1500 bytes
        packet_size = 1500
    elif isFullFrame[0,1] == True: #checks if frame is at 567 bytes
        packet_size = 576
    else:
        packet_size = int(random.gammavariate(alpha, beta)) #checks if frame is neither 1500 bytes nor 576 bytes
        if packet_size > 1500:
            packet_size = 1500
    payload = ''.join(random.choices(string.ascii_letters + string.digits, k=packet_size)).encode() #this is the actual payload
    #time delay
    timedelay = timeDiff(mu)
    
    return (payload, timedelay)

