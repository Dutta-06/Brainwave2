import cv2
import numpy as np

class QualityGrader:
    def __init__(self):
        pass

    def grade_fruit(self, image_path):
        """
        Grades a fruit (e.g., Tomato) based on 'Redness' ratio.
        Grade A: > 70% Red
        Grade B: > 40% Red
        Grade C: Green/Unripe
        """
        img = cv2.imread(image_path)
        if img is None:
            return "Error: Load Failed"

        # 1. Convert to HSV Color Space (Better for color detection)
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 2. Define Red Color Range (in HSV)
        # Red wraps around 180, so we need two ranges
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        # 3. Create Masks
        mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)
        red_mask = mask1 + mask2

        # 4. Calculate Ratio
        total_pixels = img.shape[0] * img.shape[1]
        red_pixels = cv2.countNonZero(red_mask)
        red_ratio = red_pixels / total_pixels

        # 5. Assign Grade
        print(f"[Vision] Redness Ratio: {red_ratio:.2f}")
        
        if red_ratio > 0.6:
            return "GRADE A (Export Quality)"
        elif red_ratio > 0.3:
            return "GRADE B (Local Market)"
        else:
            return "GRADE C (Processing/Sauce)"

    def show_analysis(self, image_path):
        """Debug function to show what the computer sees."""
        grade = self.grade_fruit(image_path)
        img = cv2.imread(image_path)
        
        # Overlay text
        cv2.putText(img, grade, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2)
        
        cv2.imshow("Quality Analysis", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# --- Test Block ---
if __name__ == "__main__":
    grader = QualityGrader()
    # Create a red dummy image for testing
    dummy = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy[:] = (0, 0, 255) # Pure Red BGR
    cv2.imwrite("test_tomato.jpg", dummy)
    
    print(grader.grade_fruit("test_tomato.jpg"))