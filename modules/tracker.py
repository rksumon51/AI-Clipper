import cv2
import mediapipe as mp

class FaceTracker:
    def __init__(self, config):
        # MediaPipe ফেস ডিটেকশন ইনিশিয়ালাইজ করা
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1, # 0 = কাছের ফেস, 1 = দূরের ফেস (ভিডিওর জন্য ভালো)
            min_detection_confidence=0.5
        )
        # config.json থেকে টার্গেট রেশিও নেওয়া, যেমন: "9:16"
        self.target_ratio = config['settings'].get('aspect_ratio', '9:16')

    def get_crop_coordinates(self, video_path, start_time):
        print(f"[Tracker] ফেস পজিশন অ্যানালাইজ করা হচ্ছে (Time: {start_time}s)...")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("[Tracker Error] ভিডিও ওপেন করা যাচ্ছে না!")
            return None
        
        # ভিডিওকে ঠিক ক্লিপের শুরুর সময়ে (start_time) নিয়ে যাওয়া
        cap.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
        success, frame = cap.read()
        
        if not success:
            print("[Tracker Warning] ফ্রেম রিড করা যায়নি, ভিডিওর মাঝখান থেকে ক্রপ করা হবে।")
            cap.release()
            return self._get_center_crop(1920, 1080)

        h, w, _ = frame.shape
        
        # MediaPipe-এর জন্য BGR (OpenCV ডিফল্ট) থেকে RGB-তে কনভার্ট করা
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        face_center_x = w // 2 # ফেস না পেলে ডিফল্ট হিসেবে ভিডিওর মাঝখান
        
        if results.detections:
            # প্রথম ডিটেক্ট হওয়া ফেসটি নেবো
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            # MediaPipe relative ভ্যালু (0 to 1) দেয়, তাই আসল width (w) দিয়ে গুণ করতে হবে
            face_center_x = int((bbox.xmin + bbox.width / 2) * w)
            print(f"[Tracker] ফেস পাওয়া গেছে! Center X: {face_center_x}")
        else:
            print("[Tracker] ফেস পাওয়া যায়নি, সেন্টার ক্রপ ব্যবহার করা হচ্ছে।")
            
        cap.release()
        
        return self._calculate_crop(w, h, face_center_x)

    def _calculate_crop(self, w, h, center_x):
        # 16:9 কে 9:16 করতে হলে Height (h) ঠিক থাকবে, Width (w) কমবে
        target_h = h
        target_w = int(h * (9 / 16))
        
        # ক্রপ শুরুর X পজিশন (ফেসকে ঠিক মাঝখানে রাখার জন্য)
        start_x = center_x - (target_w // 2)
        
        # ক্রপ বক্স যেন ভিডিওর ফ্রেমের বাইরে চলে না যায় তার চেকিং
        if start_x < 0:
            start_x = 0
        elif start_x + target_w > w:
            start_x = w - target_w
            
        return {
            "w": target_w,
            "h": target_h,
            "x": start_x,
            "y": 0
        }
        
    def _get_center_crop(self, w, h):
        # ফেস ট্র্যাকিং ফেইল করলে ব্যাকআপ হিসেবে একদম মাঝখান থেকে ক্রপ করবে
        target_w = int(h * (9 / 16))
        return {
            "w": target_w,
            "h": h,
            "x": (w - target_w) // 2,
            "y": 0
        }
