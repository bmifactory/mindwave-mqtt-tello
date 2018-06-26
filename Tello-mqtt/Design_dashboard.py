'''
Created on 2018. 6. 10.
@author: Kipom
This program is based on
'''
# -*- coding: utf-8 -*-
import pygame
import random
import sys
import numpy
from numpy import *
from pygame import *
#from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
#from startup_sub import *
#from tello import *
#import paho.mqtt.client as mqtt

description = """Tello Neurosky
"""
raw_eeg = True
gain = 1.0
attention_value = 50.1
Th_attention = 50
Th2_attention = 90
attention_duration = 21
duration_off = 21
duration_level1 = 21
duration_level2 = 61
duration_level3 = 85

# Set pygame parameter
fullscreen = False
bg_file = "KBRI_background_1360x768_start.jpg"
bg_file_close = "KBRI_background_1360x768_start.jpg"
bg_file_open = "KBRI_background_1360x768_open.jpg"
message_range = 20
message_list = list(range(message_range))
m_event = 0
takeoff_flag = False

def setup():
    global tello, window, fullscreen, fpsClock, address_txt_img, font, background_img
    global blackColor, redColor, whiteColor, blueColor, greenColor, attentionColor, eegColor
    global mqttClient, mqtt_connected, takeoff_flaq

    pygame.init()
    font = pygame.font.Font("freesansbold.ttf", 20)
    blackColor = pygame.Color(0, 0, 0)
    redColor = pygame.Color(255, 0, 0)
    blueColor = pygame.Color(0, 0, 255)
    whiteColor = pygame.Color(255, 255, 255)
    greenColor = pygame.Color(0, 255, 0)
    eegColor = pygame.Color(255, 255, 0)
    attentionColor = pygame.Color(10, 85, 145)

    fpsClock = pygame.time.Clock()
    pygame.display.set_caption("Tello Neurosky")
    if fullscreen is True:
        window = pygame.display.set_mode((1360, 768), pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode((1360, 768), pygame.RESIZABLE)
    background_img = pygame.image.load(bg_file)
    pygame_update(m_event)

def pygame_update(message_lane):
    global message_list, window, message_img, background_img
    global attention_duration, attention_value, control_mode
    global takeoff_flag
    font = pygame.font.Font("bgothl.ttf", 30)
    window.blit(background_img, (0, 0))
    for i in range(20):
        if i < message_lane - 1:
            message_img = font.render("# "+str(message_list[i]), False, whiteColor)
            window.blit(message_img, (1100, 100 + i * 30))
        elif i == message_lane - 1:
            message_img = font.render("# "+str(message_list[i]), False, greenColor)
            window.blit(message_img, (1100, 100 + i * 30))
        else:
            message_img = font.render("", False, whiteColor)
            window.blit(message_img, (1100, 80 + i * 30))

    #attention_value = 50
    attention_duration = 21 #duration_off
    if int(attention_value) > 100:
        attention_value = 100
        pygame.draw.circle(window, attentionColor, (680, 395), 100, 2)
    elif int(gain*attention_value) < 8:
        # attention_value = 0
        pygame.draw.circle(window, attentionColor, (680, 395), 8, 2)
    else:
        pygame.draw.circle(window, attentionColor, (680, 395), int(attention_value), 2)

    if takeoff_flag is True:
        attention_value_img = font.render(str(attention_value), False, whiteColor)
        attention_txt_img = font.render("Attantion", False, whiteColor)
        duration_value_img = font.render(str(attention_duration), False, whiteColor)
        duration_txt_img = font.render("Charging", False, whiteColor)
        window.blit(attention_txt_img, (280, 700))
        window.blit(attention_value_img, (320, 650))
        window.blit(duration_txt_img, (930, 700))
        window.blit(duration_value_img, (970, 650))
        angle_attention = (2*attention_value-130+random.randint(0, 5))*0.01745329252
        draw_gauge_needle(358, 582, angle_attention, 160, 6)
        angle_duration = (2*attention_duration-42)*0.01745329252
        draw_gauge_needle(1005, 582, angle_duration, 160, 6)
    else:
        attention_value_img = font.render(str(attention_value), False, blackColor)
        attention_txt_img = font.render("Attantion", False, blackColor)
        duration_value_img = font.render(str(attention_duration), False, blackColor)
        duration_txt_img = font.render("Charging", False, blackColor)
        window.blit(attention_txt_img, (280, 600))
        window.blit(attention_value_img, (320, 550))
        window.blit(duration_txt_img, (930, 600))
        window.blit(duration_value_img, (970, 550))
        length_attention = 2*attention_value+random.randint(0, 5)
        draw_gauge_bar(358, 532, 1, length_attention, 100)
        if attention_duration >= 21.1:
            attention_duration = 21.1
        length_duration = 10*(attention_duration+1)
        draw_gauge_bar(1005, 532, 1, length_duration, 100)
        mode_img = font.render("press F1 for BMI control mode", False, whiteColor)
        window.blit(mode_img, (800, 700))
    pygame.display.update()

def draw_gauge_needle(center_x, center_y, ang, length, width):
    '''
    a = (2 * 0 - 42) * 0.01745329252
    end_x = center_x + length * sin(a)
    end_y = center_y - length * cos(a)
    pygame.draw.line(window, blueColor, (center_x, center_y), (end_x, end_y), 2)
    a = (2 * 21 - 42) * 0.01745329252
    end_x = center_x + length * sin(a)
    end_y = center_y - length * cos(a)
    pygame.draw.line(window, blueColor, (center_x, center_y), (end_x, end_y), 2)
    a = (2 * 66 - 42) * 0.01745329252
    end_x = center_x + length * sin(a)
    end_y = center_y - length * cos(a)
    pygame.draw.line(window, blueColor, (center_x, center_y), (end_x, end_y), 2)
    a = (2 * 84 - 42) * 0.01745329252
    end_x = center_x + length * sin(a)
    end_y = center_y - length * cos(a)
    pygame.draw.line(window, blueColor, (center_x, center_y), (end_x, end_y), 2)
    '''
    end_x = center_x + length * sin(ang)
    end_y = center_y - length * cos(ang)
    pygame.draw.line(window, redColor, (center_x, center_y), (end_x, end_y), width)

def draw_gauge_bar(center_x, center_y, dir, length, width):
    if dir is 0:
        end_x = center_x + length
        end_y = center_y
    else :
        end_x = center_x
        end_y = center_y - length
    pygame.draw.line(window, redColor, (center_x, center_y), (end_x, end_y), width)

def m_event_update(message):
    global m_event, message_list
    message_list[m_event] = message
    pygame_update(m_event)
    if m_event >= message_range - 1:
        m_event = 0
    else:
        m_event = m_event + 1

def main():
    global battary, m_event, tello, iteration, background_img, mqttClient
    global attention_duration, attention_value, control_mode, takeoff_flag
    # spectra = []
    quit = False
    takeoff_flag = False
    iteration = 0
    while quit is False:
        # Get pygame event
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print('quit program')
                    quit = True
                elif event.key == K_F1:
                    mqtt_command = 'takeoff'
                    takeoff_flag = True
                    background_img = pygame.image.load(bg_file_open)
                    m_event_update(mqtt_command)
        # Display update
        pygame.display.update()
        fpsClock.tick(10)

if __name__ == '__main__':
    try:
        setup()
        main()
    finally:
        pygame.quit()