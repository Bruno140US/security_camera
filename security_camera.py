import cv2
import time
import datetime
import pygame
from email.message import EmailMessage
import ssl
import smtplib

receiver_email = "the email to receive"
sender_email = "your email to send"
password = "your gmail key here"
subject = "MOVEMENT DETECTED!!!"
body = """
Moviment detected in your camera device!!

The video was saved and will be ready to review in your machine.

E.R.A Security Services®
"""
em = EmailMessage()

em['From'] = sender_email
em['To'] = receiver_email
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()


pygame.mixer.init()
pygame.mixer.music.load("cam_sound.mp3")

cap = cv2.VideoCapture(0)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_fullbody.xml")

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

while True:
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    bodies = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(
                f"{current_time}.mp4", fourcc, 20, frame_size)
            pygame.mixer.music.play()
            print("Movement detected! Recording now...")

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(sender_email, password)
                smtp.sendmail(sender_email, receiver_email, em.as_string())

    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print('Stop Recording!')
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord('q'):
        break

pygame.mixer.music.unload()
out.release()
cap.release()
cv2.destroyAllWindows()