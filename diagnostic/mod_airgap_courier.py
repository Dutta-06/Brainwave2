import qrcode
import cv2
from pyzbar.pyzbar import decode
import json
import time

class AirGapCourier:
    def __init__(self):
        pass

    def generate_qr(self, payload_dict, filename="payload_qr.png"):
        """
        Takes a dictionary (order, contract, message), compresses it, 
        and generates a QR code image.
        """
        # Convert dict to string
        json_str = json.dumps(payload_dict)
        
        # Create QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json_str)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        print(f"[Courier] QR Code generated: {filename}")
        
        # In a real GUI, we would display this image on screen
        # img.show() 
        return filename

    def scan_qr(self):
        """
        Opens the camera to read a QR code from a traveler/courier.
        Returns the decoded JSON dictionary.
        """
        cap = cv2.VideoCapture(0)
        print("[Courier] Scanning for QR Code... (Press 'q' to quit)")

        detected_data = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Decode any QR codes in the frame
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                raw_data = obj.data.decode("utf-8")
                try:
                    detected_data = json.loads(raw_data)
                    print("[Courier] Data Received Successfully!")
                    # Draw a rectangle to show success
                    (x, y, w, h) = obj.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                except json.JSONDecodeError:
                    print("[Error] Invalid JSON in QR Code")

            cv2.imshow("AirGap Scanner", frame)

            if detected_data or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return detected_data

# --- Test Block ---
if __name__ == "__main__":
    courier = AirGapCourier()
    
    # 1. Sender Mode
    data = {"type": "seed_order", "item": "Wheat", "qty_kg": 50, "user": "Ramesh"}
    courier.generate_qr(data)
    
    # 2. Receiver Mode (Uncomment to test camera)
    # result = courier.scan_qr()
    # print("Payload:", result)