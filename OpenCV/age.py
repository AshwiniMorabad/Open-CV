import cv2
import os
from datetime import datetime

def cartoonify(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(image, 9, 300, 300)
    return cv2.bitwise_and(color, color, mask=edges)

def sketch(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

def blur_filter(image):
    return cv2.GaussianBlur(image, (15, 15), 0)

def save_with_timestamp(image, filter_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filter_name}_{timestamp}.png"
    cv2.imwrite(filename, image)
    print(f"Saved: {filename}")
def change_skin_tone(image, tone="natural"):
    result = image.copy()

    if tone == "bright":
        # Strong brightening and color boost
        result = cv2.convertScaleAbs(result, alpha=1.5, beta=50)

    elif tone == "warm":
        # Apply warm filter: slightly reddish-yellow overlay
        overlay = result.copy()
        overlay[:] = (0, 50, 100)  # BGR tone
        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)

    elif tone == "dull":
        # Slightly darkened and desaturated
        result = cv2.convertScaleAbs(result, alpha=0.7, beta=-30)

    elif tone == "pale":
        # Desaturate + brighten
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
        hsv[..., 1] = hsv[..., 1] * 0.2  # Strong desaturation
        hsv[..., 2] = cv2.add(hsv[..., 2], 30)  # Slightly brighter
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return result



def apply_age_effect(image, age):
    if age <= 12:
        cartoon = cartoonify(image)
        return change_skin_tone(cartoon, tone="bright")

    elif age <= 25:
        sk = sketch(image)
        return change_skin_tone(sk, tone="warm")

    elif age <= 50:
        smooth = cv2.bilateralFilter(image, 15, 75, 75)
        return change_skin_tone(smooth, tone="dull")

    else:
        aged = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        aged = cv2.equalizeHist(aged)
        aged = cv2.cvtColor(aged, cv2.COLOR_GRAY2BGR)
        aged = change_skin_tone(aged, tone="pale")
        cv2.putText(aged, f"Age: {age}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 255), 2, cv2.LINE_AA)
        return aged




def process_image(image):
    try:
        age = int(input("Enter age: "))
        avatar = apply_age_effect(image, age)
        filter_name = f"age_avatar_{age}"
        save_with_timestamp(avatar, filter_name)
        cv2.imshow("Avatar by Age", avatar)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except ValueError:
        print("Invalid age entered.")

def from_webcam():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        process_image(frame)
    else:
        print("Failed to capture image.")

def from_file(path):
    if os.path.exists(path):
        img = cv2.imread(path)
        process_image(img)
    else:
        print(f"File not found: {path}")

print("Choose an option:")
print("1. Capture from webcam")
print("2. Upload image file")
choice = input("Enter 1 or 2: ")

if choice == '1':
    from_webcam()
elif choice == '2':
    path = input("Enter full image path: ")
    from_file(path)
else:
    print("Invalid choice.")
