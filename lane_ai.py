'''import torch
import cv2
import numpy as np
from torchvision import models, transforms

class AILaneDetector:
    def __init__(self):
        self.model = models.segmentation.deeplabv3_resnet50(pretrained=True)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((520, 520)),
            transforms.ToTensor()
        ])

    def detect(self, frame):
        input_tensor = self.transform(frame).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_tensor)['out'][0]

        output = output.argmax(0).byte().cpu().numpy()

        # Road class = 0 or 1 (approx, depends)
        mask = (output == 0).astype(np.uint8) * 255

        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        return self.extract_lanes(frame, mask)
    
    def extract_lanes(self, frame, mask):
    	h, w = mask.shape

    # Split mask into left and right
    	left_region = mask[:, :w//2]
    	right_region = mask[:, w//2:]

    # Get lane centers
    	left_x = np.mean(np.where(left_region > 0)[1]) if np.any(left_region) else None
   	 right_x = np.mean(np.where(right_region > 0)[1]) + w//2 if np.any(right_region) else None

   	 if left_x:
        	cv2.line(frame, (int(left_x), h), (int(left_x), int(h*0.6)), (0,255,0), 4)

    	if right_x:
        	cv2.line(frame, (int(right_x), h), (int(right_x), int(h*0.6)), (0,255,0), 4)

    	return frame

    
    
import torch
import cv2
import numpy as np
from torchvision import models, transforms

class AILaneDetector:
    def __init__(self):
        self.model = models.segmentation.deeplabv3_resnet50(pretrained=True)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((520, 520)),
            transforms.ToTensor()
        ])

    def detect(self, frame):
        input_tensor = self.transform(frame).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_tensor)['out'][0]

        output = output.argmax(0).byte().cpu().numpy()

        mask = (output == 0).astype(np.uint8) * 255
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        return self.extract_lanes(frame, mask)

    def extract_lanes(self, frame, mask):
        h, w = mask.shape

        left_region = mask[:, :w//2]
        right_region = mask[:, w//2:]

        left_x = np.mean(np.where(left_region > 0)[1]) if np.any(left_region) else None
        right_x = np.mean(np.where(right_region > 0)[1]) + w//2 if np.any(right_region) else None

        if left_x is not None:
            cv2.line(frame, (int(left_x), h), (int(left_x), int(h*0.6)), (0,255,0), 4)

        if right_x is not None:
            cv2.line(frame, (int(right_x), h), (int(right_x), int(h*0.6)), (0,255,0), 4)

        return frame
        
        
import torch
import cv2
import numpy as np
from torchvision import models, transforms

class AILaneDetector:
    def __init__(self):
        self.model = models.segmentation.deeplabv3_resnet50(pretrained=True)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((520, 520)),
            transforms.ToTensor()
        ])

    def detect(self, frame):
        input_tensor = self.transform(frame).unsqueeze(0)

        with torch.no_grad():
            output = self.model(input_tensor)['out'][0]

        output = output.argmax(0).byte().cpu().numpy()

        # Road mask
        mask = (output == 0).astype(np.uint8) * 255
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        return self.draw_lane(frame, mask)
	
    def draw_lane(self, frame, mask):
    	h, w = mask.shape

    # Detect edges
    	edges = cv2.Canny(mask, 50, 150)

    	lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50,
                            minLineLength=100, maxLineGap=50)

    	if lines is not None:
        	for line in lines[:5]:
            		x1, y1, x2, y2 = line[0]
            		cv2.line(frame, (x1,y1), (x2,y2), (0,255,0), 3)

    # Center line
    	center = w // 2
    	cv2.line(frame, (center, h), (center, int(h*0.6)), (255,0,0), 2)

    	return frame
    	
    	
import torch
import cv2
import numpy as np
from torchvision import transforms   
from torchvision.models.segmentation import deeplabv3_resnet50, DeepLabV3_ResNet50_Weights

class AILaneDetector:
    def __init__(self):
        self.model = deeplabv3_resnet50(
            weights=DeepLabV3_ResNet50_Weights.DEFAULT
        )
        self.model.eval()

        # 🔥 Smaller size for speed
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((256, 256)),
            transforms.ToTensor()
        ])

    def detect(self, frame):
        
    	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    	# Blur for noise reduction
    	blur = cv2.GaussianBlur(gray, (5, 5), 0)

    	# Edge detection
    	edges = cv2.Canny(blur, 50, 150)

    	h, w = edges.shape

    	# Focus only on road region (bottom part)
    	mask = np.zeros_like(edges)
    	polygon = np.array([[
        	(0, h),
        	(w, h),
        	(w, int(h*0.6)),
        	(0, int(h*0.6))
    	]], np.int32)

    	cv2.fillPoly(mask, polygon, 255)
    	cropped = cv2.bitwise_and(edges, mask)

    	# Detect lines
    	lines = cv2.HoughLinesP(
        	cropped,
        	1,
        	np.pi/180,
        	threshold=50,
        	minLineLength=100,
        	maxLineGap=50
    	)

    	# Draw lanes
    	if lines is not None:
        	for line in lines[:4]:
            	x1, y1, x2, y2 = line[0]
            	cv2.line(frame, (x1,y1), (x2,y2), (0,255,0), 3)

    	# Center guide line
    	center = w // 2
    	cv2.line(frame, (center, h), (center, int(h*0.7)), (255,0,0), 2)

    	return frame
    def draw_lane(self, frame, mask):
        h, w = mask.shape

        # Edge-based lane visualization (lightweight)
        edges = cv2.Canny(mask, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50,
                                minLineLength=100, maxLineGap=50)

        if lines is not None:
            for line in lines[:4]:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1,y1), (x2,y2), (0,255,0), 2)

        # Center line
        center = w // 2
        cv2.line(frame, (center, h), (center, int(h*0.7)), (255,0,0), 2)



import cv2
import numpy as np

class AILaneDetector:
    def __init__(self):
        pass

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Smooth image
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection
        edges = cv2.Canny(blur, 50, 150)

        h, w = edges.shape

        # Region of Interest (road area only)
        mask = np.zeros_like(edges)
        polygon = np.array([[
            (0, h),
            (w, h),
            (int(w*0.6), int(h*0.6)),
            (int(w*0.4), int(h*0.6))
        ]], np.int32)

        cv2.fillPoly(mask, polygon, 255)
        cropped = cv2.bitwise_and(edges, mask)

        # Hough Transform
        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi/180,
            threshold=50,
            minLineLength=80,
            maxLineGap=50
        )

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # Avoid vertical lines
                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                # Filter noise
                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left_lines.append(line[0])
                else:
                    right_lines.append(line[0])

        # Draw averaged lines
        self.draw_average_line(frame, left_lines, color=(0,255,0))
        self.draw_average_line(frame, right_lines, color=(0,255,0))

        # Draw center guide
        center = w // 2
        cv2.line(frame, (center, h), (center, int(h*0.7)), (255,0,0), 2)

        return frame


    def draw_average_line(self, frame, lines, color):
        if len(lines) == 0:
            return

        x_coords = []
        y_coords = []

        for x1, y1, x2, y2 in lines:
            x_coords += [x1, x2]
            y_coords += [y1, y2]

        # Fit line
        poly = np.polyfit(x_coords, y_coords, 1)
        slope, intercept = poly

        h = frame.shape[0]

        y1 = h
        y2 = int(h * 0.6)

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        cv2.line(frame, (x1, y1), (x2, y2), color, 5)
        return frame



import cv2
import numpy as np

class AILaneDetector:
    def __init__(self):
        pass

    #def detect(self, frame):
    def detect(self, frame, mode="Highway Mode"):
        # ================= COLOR FILTER =================
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # White color mask
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Yellow color mask
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Combine masks
        mask = cv2.bitwise_or(white_mask, yellow_mask)

        # ================= EDGE DETECTION =================
        edges = cv2.Canny(mask, 50, 150)

        h, w = edges.shape

        # ================= ROI (ROAD AREA ONLY) =================
        roi_mask = np.zeros_like(edges)

        polygon = np.array([[
            (int(w * 0.1), h),
            (int(w * 0.9), h),
            (int(w * 0.6), int(h * 0.6)),
            (int(w * 0.4), int(h * 0.6))
        ]], np.int32)

        cv2.fillPoly(roi_mask, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi_mask)
        
        if mode == "City Mode":
    		minLineLength = 50
    		maxLineGap = 30
	else:
    		minLineLength = 120
    		maxLineGap = 80

        # ================= HOUGH LINE DETECTION =================
        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi / 180,
            threshold=50,
            minLineLength=100,
            maxLineGap=50
        )
        lines = cv2.HoughLinesP(
    		cropped,
    		1,
    		np.pi / 180,
    		threshold=50,
    		minLineLength=minLineLength,
    		maxLineGap=maxLineGap
		)

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # Avoid division by zero
                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                # Filter out horizontal lines
                if abs(slope) < 0.5:
                    continue

                # Separate left and right lanes
                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))

        # Draw averaged lanes
        self.draw_lane(frame, left_lines)
        self.draw_lane(frame, right_lines)

        # ================= CENTER GUIDE LINE =================
        center = w // 2
        cv2.line(frame, (center, h), (center, int(h * 0.7)), (255, 0, 0), 2)

        return frame


    def draw_lane(self, frame, lines):
        if len(lines) == 0:
            return

        x_coords = []
        y_coords = []

        for x1, y1, x2, y2 in lines:
            x_coords += [x1, x2]
            y_coords += [y1, y2]

        if len(x_coords) < 2:
            return

        # Fit line
        slope, intercept = np.polyfit(x_coords, y_coords, 1)

        h = frame.shape[0]

        y1 = h
        y2 = int(h * 0.6)

        # Avoid division by zero
        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        # Draw lane line
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 6)
        
        
        
import cv2
import numpy as np

class AILaneDetector:
    def __init__(self):
        pass

    def detect(self, frame, mode="Highway Mode"):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # White mask
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 40, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Yellow mask
        lower_yellow = np.array([15, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = cv2.bitwise_or(white_mask, yellow_mask)

        edges = cv2.Canny(mask, 50, 150)

        h, w = edges.shape

        # ROI
        roi_mask = np.zeros_like(edges)

        polygon = np.array([[
            (int(w * 0.1), h),
            (int(w * 0.9), h),
            (int(w * 0.6), int(h * 0.6)),
            (int(w * 0.4), int(h * 0.6))
        ]], np.int32)

        cv2.fillPoly(roi_mask, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi_mask)

        # 🔥 Mode-based tuning
        if mode == "City Mode":
            minLineLength = 50
            maxLineGap = 30
        else:
            minLineLength = 120
            maxLineGap = 80

        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi / 180,
            threshold=50,
            minLineLength=minLineLength,
            maxLineGap=maxLineGap
        )

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))

        self.draw_lane(frame, left_lines)
        self.draw_lane(frame, right_lines)

        # Center line
        center = w // 2
        cv2.line(frame, (center, h), (center, int(h * 0.7)), (255, 0, 0), 2)

        return frame


    def draw_lane(self, frame, lines):
        if len(lines) == 0:
            return

        x_coords = []
        y_coords = []

        for x1, y1, x2, y2 in lines:
            x_coords += [x1, x2]
            y_coords += [y1, y2]

        if len(x_coords) < 2:
            return

        slope, intercept = np.polyfit(x_coords, y_coords, 1)

        h = frame.shape[0]

        y1 = h
        y2 = int(h * 0.6)

        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 6)
        
import cv2
import numpy as np

class AILaneDetector:
    def __init__(self):
        pass

    def detect(self, frame, mode="Highway Mode"):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Improved white mask
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 60, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        # Improved yellow mask
        lower_yellow = np.array([10, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = cv2.bitwise_or(white_mask, yellow_mask)

        edges = cv2.Canny(mask, 30, 120)

        h, w = edges.shape

        # Improved ROI
        roi_mask = np.zeros_like(edges)

        polygon = np.array([[
            (int(w * 0.05), h),
            (int(w * 0.95), h),
            (int(w * 0.65), int(h * 0.55)),
            (int(w * 0.35), int(h * 0.55))
        ]], np.int32)

        cv2.fillPoly(roi_mask, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi_mask)

        # Mode-based tuning
        if mode == "City Mode":
            minLineLength = 50
            maxLineGap = 30
        else:
            minLineLength = 120
            maxLineGap = 80

        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi / 180,
            threshold=30,
            minLineLength=minLineLength,
            maxLineGap=maxLineGap
        )

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))

        self.draw_lane(frame, left_lines, (255, 0, 0))   # Left lane (Blue)
        self.draw_lane(frame, right_lines, (0, 255, 0))  # Right lane (Green)

        return frame


    def draw_lane(self, frame, lines, color):
        if len(lines) == 0:
            return

        slopes = []
        intercepts = []

        for x1, y1, x2, y2 in lines:
            if x2 - x1 == 0:
                continue

            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1

            slopes.append(slope)
            intercepts.append(intercept)

        if len(slopes) == 0:
            return

        slope = np.mean(slopes)
        intercept = np.mean(intercepts)

        h = frame.shape[0]

        y1 = h
        y2 = int(h * 0.6)

        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        cv2.line(frame, (x1, y1), (x2, y2), color, 10)
        
        
import cv2
import numpy as np

class AILaneDetector:
    def __init__(self):
        pass

    def detect(self, frame, mode="Highway Mode"):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 60, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        lower_yellow = np.array([10, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = cv2.bitwise_or(white_mask, yellow_mask)

        edges = cv2.Canny(mask, 30, 120)

        h, w = edges.shape

        roi_mask = np.zeros_like(edges)

        polygon = np.array([[
            (int(w * 0.05), h),
            (int(w * 0.95), h),
            (int(w * 0.65), int(h * 0.55)),
            (int(w * 0.35), int(h * 0.55))
        ]], np.int32)

        cv2.fillPoly(roi_mask, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi_mask)

        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi / 180,
            threshold=30,
            minLineLength=120,
            maxLineGap=80
        )

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))

        self.draw_lane(frame, left_lines, (255, 0, 0))
        self.draw_lane(frame, right_lines, (0, 255, 0))

        return frame


    def draw_lane(self, frame, lines, color):
        if len(lines) == 0:
            return

        slopes = []
        intercepts = []

        for x1, y1, x2, y2 in lines:
            if x2 - x1 == 0:
                continue

            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1

            slopes.append(slope)
            intercepts.append(intercept)

        if len(slopes) == 0:
            return

        slope = np.mean(slopes)
        intercept = np.mean(intercepts)

        h = frame.shape[0]

        y1 = h
        y2 = int(h * 0.6)

        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        cv2.line(frame, (x1, y1), (x2, y2), color, 10)
        
        
import cv2
import numpy as np

class AILaneDetector:

    def __init__(self):
        self.prev_left = None
        self.prev_right = None

    def detect(self, frame, mode="Highway Mode"):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 60, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        lower_yellow = np.array([10, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = cv2.bitwise_or(white_mask, yellow_mask)

        edges = cv2.Canny(mask, 30, 120)

        h, w = edges.shape

        roi = np.zeros_like(edges)
        polygon = np.array([[
            (int(w*0.05), h),
            (int(w*0.95), h),
            (int(w*0.65), int(h*0.55)),
            (int(w*0.35), int(h*0.55))
        ]], np.int32)

        cv2.fillPoly(roi, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi)

        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi/180,
            threshold=30,
            minLineLength=120,
            maxLineGap=80
        )

        left, right = [], []

        if lines is not None:
            for l in lines:
                x1,y1,x2,y2 = l[0]

                if x2-x1 == 0:
                    continue

                slope = (y2-y1)/(x2-x1)

                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left.append((x1,y1,x2,y2))
                else:
                    right.append((x1,y1,x2,y2))

        self.draw(frame, left, True)
        self.draw(frame, right, False)

        return frame


    def draw(self, frame, lines, is_left):

        if len(lines) < 3:
            return

        slopes, intercepts = [], []

        for x1,y1,x2,y2 in lines:
            slope = (y2-y1)/(x2-x1)
            intercept = y1 - slope*x1
            slopes.append(slope)
            intercepts.append(intercept)

        slope = np.mean(slopes)
        intercept = np.mean(intercepts)

        # smoothing
        alpha = 0.8

        if is_left:
            if self.prev_left is not None:
                slope = alpha*self.prev_left[0] + (1-alpha)*slope
                intercept = alpha*self.prev_left[1] + (1-alpha)*intercept
            self.prev_left = (slope, intercept)
            color = (255,0,0)
        else:
            if self.prev_right is not None:
                slope = alpha*self.prev_right[0] + (1-alpha)*slope
                intercept = alpha*self.prev_right[1] + (1-alpha)*intercept
            self.prev_right = (slope, intercept)
            color = (0,255,0)

        h = frame.shape[0]
        y1 = h
        y2 = int(h*0.6)

        if slope == 0:
            return
        x1 = int((y1-intercept)/slope)
        x2 = int((y2-intercept)/slope)
        cv2.line(frame,(x1,y1),(x2,y2),color,8)
        
        
import cv2
import numpy as np

class AILaneDetector:

    def __init__(self):
        self.prev_left = None
        self.prev_right = None

    def detect(self, frame, mode="Highway Mode"):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # masks
        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 60, 255])
        white = cv2.inRange(hsv, lower_white, upper_white)

        lower_yellow = np.array([10, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        mask = cv2.bitwise_or(white, yellow)

        edges = cv2.Canny(mask, 30, 120)

        h, w = edges.shape

        roi = np.zeros_like(edges)
        polygon = np.array([[
            (int(w*0.05), h),
            (int(w*0.95), h),
            (int(w*0.65), int(h*0.55)),
            (int(w*0.35), int(h*0.55))
        ]], np.int32)

        cv2.fillPoly(roi, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi)

        lines = cv2.HoughLinesP(
            cropped, 1, np.pi/180,
            threshold=30,
            minLineLength=120,
            maxLineGap=80
        )

        left, right = [], []

        if lines is not None:
            for l in lines:
                x1,y1,x2,y2 = l[0]

                if x2-x1 == 0:
                    continue

                slope = (y2-y1)/(x2-x1)

                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left.append((x1,y1,x2,y2))
                else:
                    right.append((x1,y1,x2,y2))

        self.draw(frame, left, True)
        self.draw(frame, right, False)

        return frame


    def draw(self, frame, lines, is_left):

        if len(lines) < 3:
            return

        slopes, intercepts = [], []

        for x1,y1,x2,y2 in lines:
            slope = (y2-y1)/(x2-x1)
            intercept = y1 - slope*x1
            slopes.append(slope)
            intercepts.append(intercept)

        slope = np.mean(slopes)
        intercept = np.mean(intercepts)

        alpha = 0.8

        if is_left:
            if self.prev_left is not None:
                slope = alpha*self.prev_left[0] + (1-alpha)*slope
                intercept = alpha*self.prev_left[1] + (1-alpha)*intercept
            self.prev_left = (slope, intercept)
            color = (255, 0, 0)
        else:
            if self.prev_right is not None:
                slope = alpha*self.prev_right[0] + (1-alpha)*slope
                intercept = alpha*self.prev_right[1] + (1-alpha)*intercept
            self.prev_right = (slope, intercept)
            color = (0, 255, 0)

        h = frame.shape[0]
        y1 = h
        y2 = int(h * 0.6)

        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        cv2.line(frame, (x1, y1), (x2, y2), color, 10)
        
        
        
        
        
        
        
import cv2
import numpy as np

class AILaneDetector:

    def __init__(self):
        self.prev_left = None
        self.prev_right = None

    def detect(self, frame, mode="Highway Mode"):

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # WHITE MASK (improved)
        lower_white = np.array([0, 0, 160])
        upper_white = np.array([180, 80, 255])
        white = cv2.inRange(hsv, lower_white, upper_white)

        # YELLOW MASK
        lower_yellow = np.array([10, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Combine masks
        mask = cv2.bitwise_or(white, yellow)

        # Blur for better edges
        blur = cv2.GaussianBlur(mask, (5, 5), 0)

        # Edge detection
        edges = cv2.Canny(blur, 50, 150)

        h, w = edges.shape

        # ROI (important fix)
        roi = np.zeros_like(edges)
        polygon = np.array([[
            (0, h),
            (w, h),
            (int(w*0.6), int(h*0.6)),
            (int(w*0.4), int(h*0.6))
        ]], np.int32)

        cv2.fillPoly(roi, polygon, 255)
        cropped = cv2.bitwise_and(edges, roi)

        # Hough lines
        lines = cv2.HoughLinesP(
            cropped,
            1,
            np.pi/180,
            threshold=40,
            minLineLength=100,
            maxLineGap=50
        )

        left_lines = []
        right_lines = []

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                if x2 - x1 == 0:
                    continue

                slope = (y2 - y1) / (x2 - x1)

                # Remove flat lines
                if abs(slope) < 0.5:
                    continue

                if slope < 0:
                    left_lines.append((x1, y1, x2, y2))
                else:
                    right_lines.append((x1, y1, x2, y2))

        # Draw lanes
        self.draw_lane(frame, left_lines, True)
        self.draw_lane(frame, right_lines, False)

        # Center line
        center = w // 2
        cv2.line(frame, (center, h), (center, int(h*0.7)), (255, 0, 0), 2)

        return frame


    def draw_lane(self, frame, lines, is_left):

        if len(lines) < 2:
            return

        slopes = []
        intercepts = []

        for x1, y1, x2, y2 in lines:
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            slopes.append(slope)
            intercepts.append(intercept)

        slope = np.mean(slopes)
        intercept = np.mean(intercepts)

        # Smoothing
        alpha = 0.8
        if is_left:
            if self.prev_left is not None:
                slope = alpha * self.prev_left[0] + (1-alpha) * slope
                intercept = alpha * self.prev_left[1] + (1-alpha) * intercept
            self.prev_left = (slope, intercept)
            color = (255, 0, 0)
        else:
            if self.prev_right is not None:
                slope = alpha * self.prev_right[0] + (1-alpha) * slope
                intercept = alpha * self.prev_right[1] + (1-alpha) * intercept
            self.prev_right = (slope, intercept)
            color = (0, 255, 0)

        h = frame.shape[0]
        y1 = h
        y2 = int(h * 0.6)

        if slope == 0:
            return

        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)

        # Thick lane lines (VERY IMPORTANT)
        cv2.line(frame, (x1, y1), (x2, y2), color, 8)'''

import cv2
import numpy as np

class AILaneDetector:

    def detect(self, frame):

        h, w = frame.shape[:2]

        # Define road area (dynamic trapezium)
        polygon = np.array([[
            (int(w*0.1), h),
            (int(w*0.9), h),
            (int(w*0.6), int(h*0.6)),
            (int(w*0.4), int(h*0.6))
        ]], np.int32)

        # Create overlay
        overlay = frame.copy()
        cv2.fillPoly(overlay, polygon, (0, 255, 0))  # green road

        # Blend with original frame
        frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)

        # Draw lane borders
        pts = polygon[0]

        cv2.line(frame, tuple(pts[0]), tuple(pts[3]), (255, 0, 0), 5)  # left
        cv2.line(frame, tuple(pts[1]), tuple(pts[2]), (0, 255, 0), 5)  # right

        return frame

