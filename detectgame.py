import cv2
import numpy as np

# =========================
# LOAD IMAGE
# =========================
image = cv2.imread('images/3.png')

if image is None:
    print("❌ Image not found")
    exit()

# =========================
# CROP IMPORTANT REGION
# =========================
cropped = image[0:230, 0:263]

# =========================
# ZOOM FACTOR
# =========================
ZOOM = 3

zoomed = cv2.resize(
    cropped,
    (cropped.shape[1]*ZOOM, cropped.shape[0]*ZOOM),
    interpolation=cv2.INTER_NEAREST  # مهم جدا لعدم تشويه البكسلات
)

def mouse_callback(event, x, y, flags, param):
    global zoomed, cropped

    # تحويل من الإحداثيات المكبرة إلى الأصلية
    real_x = x // ZOOM
    real_y = y // ZOOM

    if event == cv2.EVENT_MOUSEMOVE:
        display = zoomed.copy()
        cv2.putText(display,
                    f"X:{real_x} Y:{real_y}",
                    (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,255,0),
                    2)
        cv2.imshow("Zoomed Dashboard", display)

    if event == cv2.EVENT_LBUTTONDOWN:

        b, g, r = cropped[real_y, real_x]
        rgb = (int(r), int(g), int(b))

        hsv = cv2.cvtColor(
            np.uint8([[[b, g, r]]]),
            cv2.COLOR_BGR2HSV
        )[0][0]

        h, s, v = map(int, hsv)

        print("="*50)
        print(f"Coordinates: ({real_x}, {real_y})")
        print(f"RGB: {rgb}")
        print(f"HSV: ({h}, {s}, {v})")
        print("="*50)

cv2.imshow("Zoomed Dashboard", zoomed)
cv2.setMouseCallback("Zoomed Dashboard", mouse_callback)

print("Move mouse to see coordinates.")
print("Click to get pixel color.")
print("Press any key to exit.")

cv2.waitKey(0)
cv2.destroyAllWindows()