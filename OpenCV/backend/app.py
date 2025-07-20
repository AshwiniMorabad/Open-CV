from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import numpy as np
import os
import base64
import cv2

app = Flask(__name__)
CORS(app)

known_faces_dir = "known_faces"
known_face_encodings = []
known_face_names = []

for file in os.listdir(known_faces_dir):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        image = face_recognition.load_image_file(os.path.join(known_faces_dir, file))
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(os.path.splitext(file)[0])

@app.route("/recognize", methods=["POST"])
def recognize():
    data = request.json
    img_data = data["image"]
    img_bytes = base64.b64decode(img_data.split(",")[1])
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, encoding)
        distances = face_recognition.face_distance(known_face_encodings, encoding)

        if distances.size > 0:
            best_match = np.argmin(distances)
            if matches[best_match] and distances[best_match] < 0.5:
                name = known_face_names[best_match]
                return jsonify({"status": "success", "name": name})

    return jsonify({"status": "unknown"})

if __name__ == "__main__":
    app.run(port=5000)