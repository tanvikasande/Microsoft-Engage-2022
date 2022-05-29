from PIL import Image, ImageTk
import cv2
from pandastable import Table
import cv2
from PIL import Image, ImageTk
import os
from matplotlib import pyplot as plt
import numpy as np
from tkvideo import tkvideo
from tkinter import *
import tkinter as tk
import tkinter.font as font
import csv
import os
import shutil
import boto3
import cv2
from PIL import Image, ImageTk
from tkvideo import tkvideo
import pandas as pd
import random

Attributes = []

# for accessing aws Rekognition
with open('new_user_credentials.csv', 'r') as inp:
    next(inp)  # skip the first row
    reader = csv.reader(inp)
    for line in reader:
        access_key_id = line[2]
        secret_access_key = line[3]

client = boto3.client('rekognition',
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key,
                      region_name='ap-south-1')

# folder for temporarily storing image frames
if not os.path.exists('images'):
    os.makedirs('images')
    path = os.getcwd()
    my_folder = "images"
    images_folder = os.path.join(path, my_folder)
else:
    images_folder = "./images"

# connecting to webcam
cap = cv2.VideoCapture(0)


# function for showing webcam frame
def show_vid():
    i = 0
    if not cap.isOpened():  # checks for the opening of camera
        print("CANNOT OPEN CAMERA")
    else:
        flag, frame = cap.read()
        frame = cv2.resize(frame, (600, 400))

        if not flag:
            print("ERROR")
        elif flag:
            # global last_frame
            last_frame = frame.copy()

            # Image format for Tkinter
            pic = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(pic)
            imgtk = ImageTk.PhotoImage(image=img)
            cam_label.imgtk = imgtk
            cam_label.configure(image=imgtk)

            # Storing frames temporarily in a folder
            filename = images_folder + 'Frame' + str(i) + '.jpg'
            cv2.imwrite('./images/' + filename, frame)

            # AWS Rekognition detects faces and attributes from stored images
            with open('./images/' + filename, 'rb') as source_image:  # common for all images in local storage
                source_bytes = source_image.read()
            response = client.detect_faces(Image={'Bytes': source_bytes},
                                           Attributes=['ALL'])

            for faceDetail in response['FaceDetails']:
                # Access predictions for individual face details and print them
                # Age: faceDetail['AgeRange']['Low']) -  str(faceDetail['AgeRange']['High']))
                # Gender: faceDetail['Gender']['Value']
                # Smile: faceDetail['Smile']['Value']
                # Emotions: faceDetail['Emotions'][0]['Type']
                Attributes.append([faceDetail['AgeRange']['Low'], faceDetail['AgeRange']['High'],
                                   faceDetail['Gender']['Value'], faceDetail['Emotions'][0]['Type']])

                # Delete images from folder as soon as attributes are extracted
                for files in os.listdir(images_folder):
                    path_for_folder = os.path.join(images_folder, files)
                    try:
                        shutil.rmtree(path_for_folder)
                    except OSError:
                        os.remove(path_for_folder)

            i = i + 1

            # call the function after fixed intervals
            cam_label.after(10, show_vid)


# function for showing the advertisement frame
def show_vid2():
    videos_list = ['Cred_Kapil_Dev.mp4', 'Cred_Ravi_Shastri.mp4', 'Heinz.mp4', 'Nike.mp4']
    audio_list = ['Cred_Kapil_Dev.mp3', 'Cred_Ravi_Shastri.mp3', 'Heinz.mp3', 'Nike.mp3']

    # Choosing a random video from the above videos
    a = random.randint(0, (len(videos_list) - 1))
    vid = tkvideo(videos_list[a], vid_label, loop=1)
    vid.play()
    # playsound(audio_list[a])


# Analysis of data extracted from the model
def show_analysis():
    attr_stats = pd.DataFrame(columns=['Age lower limit', 'Age upper limit', 'Gender', 'Emotions'])
    for attributes in Attributes:
        attr_stats.loc[len(attr_stats)] = attributes
    print(attr_stats)

    male_count = female_count = 0
    data_for_gender = []

    for i in attr_stats['Gender']:
        if i == "Male":
            male_count = male_count + 1
        else:
            female_count = female_count + 1

    data_for_gender.append(male_count)
    data_for_gender.append(female_count)
    label = ['MALE', 'FEMALE']

    plt.pie(data_for_gender, labels=label)
    plt.show()


if __name__ == '__main__':
    root = tk.Tk()
    root.configure(bg='black')  # assigning root variable        for Tkinter as tk

    cam_label = tk.Label(master=root, bg='black', width=600, height=400)
    cam_label.place(x=830, y=200)

    vid_label = tk.Label(master=root, bg='black', width=600, height=400)
    vid_label.place(x=50, y=200)
    # lmain.Frame= Frame(width=768, height=576)
    # framex.grid(column=3,rowspan=2,padx=5, pady=5)

    root.title("Ad Testing")  # you can give any title
    root.geometry("900x700+100+10")
    root.iconbitmap("icon.ico")  # size of window , x-axis, yaxis
    buttonFont = font.Font(family='Times', size=16, slant='roman')
    exit_button = Button(root, text='VIEW ANALYSIS', font=buttonFont, fg='white', bg='gray',
                         command=lambda: [root.destroy(), show_analysis()], width=15, height=4)
    exit_button.place(x=650, y=650)

    show_vid()
    show_vid2()

    root.mainloop()  # keeps the application in an infinite loop so it works continuosly
    cap.release()
