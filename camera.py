import cv2

def capture_photo(filename="capture.jpg"):
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Cannot access the camera")
        return

    print("Press 'Space' to capture the photo or 'Esc' to cancel.")
    while True:
        ret, frame = camera.read()
        cv2.imshow("Preview", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            cv2.imwrite(filename, frame)
            print(f"Image saved as {filename}")
            break

    camera.release()
    cv2.destroyAllWindows()
