import cv2
import face_recognition
import os
import time
import numpy as np


print("Loading the faces")
known_faces_dir ="known_faces"
video_dir ="videos"

known_face_encodings =[]
known_face_names =[]

for file in os.listdir(known_faces_dir):
    if file.lower().endswith((".jpg",".jpeg",".png")):
        path =os.path.join(known_faces_dir, file)
        image =face_recognition.load_image_file(path)
        encodings =face_recognition.face_encodings(image)

        if encodings:
            known_face_encodings.append(encodings[0])
            name = os.path.splitext(file)[0]
            known_face_names.append(name)
            print(f"Loaded face: {name}")
        else:
            print(f"Couldn't find a face in {file}")

# starting the webcam

print("Opening webcam")
camera =cv2.VideoCapture(0)

if not camera.isOpened():
    print("Webcam failed to start. Bummer.")
    exit()

start_time =time.time()
detection_mode =False
already_played =set()

while True:
    ret, frame =camera.read()
    if not ret:
        print("Can't read from webcam.")
        break

    current_time =time.time()

    if not detection_mode:
        cv2.putText(frame,"scanning will start in 5 sec",(30,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)
        cv2.imshow("Webcam", frame)

        if current_time-start_time>=5:
            detection_mode=True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("You quit before scanning started.")
            break
        continue

    #Face detection 
    small_frame =cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
    rgb_small_frame =cv2.cvtColor(small_frame,cv2.COLOR_BGR2RGB)

    face_locations =face_recognition.face_locations(rgb_small_frame)
    face_encodings =face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        name = "Unknown"
        matches =face_recognition.compare_faces(known_face_encodings,face_encoding)
        distances =face_recognition.face_distance(known_face_encodings,face_encoding)

        if distances.size>0:
            best_match =np.argmin(distances)
            if matches[best_match] and distances[best_match]<0.5:
                name =known_face_names[best_match]

        top,right,bottom,left =[coord * 4 for coord in face_location]
        color = (0, 255, 0) if name !="Unknown" else (0, 0, 255)

        cv2.rectangle(frame,(left,top),(right,bottom),color,2)
        cv2.putText(frame,name,(left,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.9,color,2)

        if name !="Unknown" and name not in already_played:
            print(f"\n image: {name}")
            print(f"Playing your video: {name}_video.mp4")
            time.sleep(2)

            video_path = os.path.join(video_dir, f"{name}_video.mp4")
            if os.path.exists(video_path):
                os.system(f'start "" "{video_path}"') 
            else:
                print(f"Couldn't find {name}_video.mp4")

            already_played.add(name)

            print("Done with detection. Closing webcam now.")
            camera.release()
            cv2.destroyAllWindows()
            exit()

    cv2.imshow("Webcam",frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting early.")
        break

camera.release()
cv2.destroyAllWindows()
