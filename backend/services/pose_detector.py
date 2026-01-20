"""
MediaPipe를 사용한 자세 인식 모듈
"""
import mediapipe as mp
import cv2
import numpy as np
from typing import List, Dict, Optional

class PoseDetector:
    def __init__(self, model_complexity: int = 1):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect_pose(self, image: np.ndarray) -> Optional[Dict]:
        """
        이미지에서 자세를 감지합니다.
        
        Args:
            image: 입력 이미지 (BGR 형식)
        
        Returns:
            관절 좌표 딕셔너리 또는 None
        """
        # MediaPipe는 RGB 형식을 사용
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return None
        
        # 관절 좌표 추출
        landmarks = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks[idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        return {
            'landmarks': landmarks,
            'raw_landmarks': results.pose_landmarks
        }
    
    def draw_skeleton(self, image: np.ndarray, landmarks) -> np.ndarray:
        """
        이미지에 스켈리톤을 그립니다.
        """
        annotated_image = image.copy()
        self.mp_drawing.draw_landmarks(
            annotated_image,
            landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(
                color=(0, 255, 0), thickness=2, circle_radius=2
            ),
            self.mp_drawing.DrawingSpec(
                color=(0, 0, 255), thickness=2
            )
        )
        return annotated_image
    
    def __del__(self):
        if hasattr(self, 'pose'):
            self.pose.close()
