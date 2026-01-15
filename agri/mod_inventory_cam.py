from ultralytics import YOLO
import cv2
import logging

# Reduce YOLO logging noise
logging.getLogger("ultralytics").setLevel(logging.ERROR)

class InventoryCam:
    def __init__(self):
        print("[Vision] Loading YOLOv8-Nano (Edge Optimized)...")
        # Downloads 'yolov8n.pt' automatically on first run (6.2 MB)
        self.model = YOLO('yolov8n.pt') 

    def count_stock(self, image_path, target_class="orange"):
        """
        Detects objects and counts instances of a specific class.
        """
        # Run inference
        results = self.model(image_path)
        
        count = 0
        detected_items = []
        
        # Parse results
        for r in results:
            for box in r.boxes:
                # Get Class ID and Name
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                
                detected_items.append(class_name)
                
                # Filter for the specific item (e.g., counting only 'oranges')
                # If target_class is 'all', count everything.
                if target_class == "all" or class_name == target_class:
                    count += 1

        print(f"[Vision] Detected: {detected_items}")
        return count

    def capture_and_count(self):
        """
        Opens camera, takes a snap, and counts immediately.
        """
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite("temp_inventory.jpg", frame)
            return self.count_stock("temp_inventory.jpg", target_class="all")
        else:
            return 0

# --- Test Block ---
if __name__ == "__main__":
    cam = InventoryCam()
    # count = cam.count_stock("market_stall.jpg", target_class="apple")
    # print(f"Inventory Count: {count}")