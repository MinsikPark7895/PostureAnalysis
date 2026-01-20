"""
자세 분석 및 점수 계산 모듈
"""
import numpy as np
from typing import Dict, List, Optional

class PostureAnalyzer:
    def __init__(self):
        # MediaPipe Pose 관절 인덱스
        self.LEFT_SHOULDER = 11
        self.RIGHT_SHOULDER = 12
        self.LEFT_HIP = 23
        self.RIGHT_HIP = 24
        self.LEFT_KNEE = 25
        self.RIGHT_KNEE = 26
        self.LEFT_ANKLE = 27
        self.RIGHT_ANKLE = 28
        self.NOSE = 0
    
    def calculate_score(self, landmarks: Dict) -> float:
        """
        관절 좌표를 기반으로 자세 점수를 계산합니다.
        
        Args:
            landmarks: 관절 좌표 딕셔너리
        
        Returns:
            점수 (0-100)
        """
        scores = []
        
        # 1. 어깨 정렬도 (0-25점)
        shoulder_score = self._check_shoulder_alignment(landmarks)
        scores.append(shoulder_score * 0.25)
        
        # 2. 척추 정렬도 (0-25점)
        spine_score = self._check_spine_alignment(landmarks)
        scores.append(spine_score * 0.25)
        
        # 3. 무릎 각도 (0-25점)
        knee_score = self._check_knee_angle(landmarks)
        scores.append(knee_score * 0.25)
        
        # 4. 목 각도 (0-25점)
        neck_score = self._check_neck_angle(landmarks)
        scores.append(neck_score * 0.25)
        
        total_score = sum(scores) * 100
        return max(0, min(100, total_score))
    
    def _check_shoulder_alignment(self, landmarks: Dict) -> float:
        """어깨 정렬도 확인"""
        left_shoulder = landmarks.get(self.LEFT_SHOULDER)
        right_shoulder = landmarks.get(self.RIGHT_SHOULDER)
        
        if not left_shoulder or not right_shoulder:
            return 0.0
        
        # 어깨 높이 차이 계산
        height_diff = abs(left_shoulder['y'] - right_shoulder['y'])
        # 정규화 (0-1 범위)
        score = max(0, 1 - height_diff * 10)
        return score
    
    def _check_spine_alignment(self, landmarks: Dict) -> float:
        """척추 정렬도 확인"""
        left_shoulder = landmarks.get(self.LEFT_SHOULDER)
        right_shoulder = landmarks.get(self.RIGHT_SHOULDER)
        left_hip = landmarks.get(self.LEFT_HIP)
        right_hip = landmarks.get(self.RIGHT_HIP)
        
        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return 0.0
        
        # 어깨 중심점
        shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
        # 골반 중심점
        hip_center_x = (left_hip['x'] + right_hip['x']) / 2
        
        # 중심점 차이 (측면 기울기)
        alignment_diff = abs(shoulder_center_x - hip_center_x)
        score = max(0, 1 - alignment_diff * 5)
        return score
    
    def _check_knee_angle(self, landmarks: Dict) -> float:
        """무릎 각도 확인"""
        left_hip = landmarks.get(self.LEFT_HIP)
        left_knee = landmarks.get(self.LEFT_KNEE)
        left_ankle = landmarks.get(self.LEFT_ANKLE)
        
        if not all([left_hip, left_knee, left_ankle]):
            return 0.0
        
        # 무릎 각도 계산
        angle = self._calculate_angle(
            left_hip, left_knee, left_ankle
        )
        
        # 이상적인 무릎 각도: 160-180도
        if 160 <= angle <= 180:
            return 1.0
        elif 140 <= angle < 160:
            return 0.7
        else:
            return 0.3
    
    def _check_neck_angle(self, landmarks: Dict) -> float:
        """목 각도 확인"""
        nose = landmarks.get(self.NOSE)
        left_shoulder = landmarks.get(self.LEFT_SHOULDER)
        right_shoulder = landmarks.get(self.RIGHT_SHOULDER)
        
        if not all([nose, left_shoulder, right_shoulder]):
            return 0.0
        
        shoulder_center_y = (left_shoulder['y'] + right_shoulder['y']) / 2
        # 고개 숙임 정도
        head_drop = nose['y'] - shoulder_center_y
        
        # 정규화
        score = max(0, min(1, 1 - head_drop * 2))
        return score
    
    def _calculate_angle(self, point1: Dict, point2: Dict, point3: Dict) -> float:
        """세 점 사이의 각도를 계산합니다."""
        a = np.array([point1['x'], point1['y']])
        b = np.array([point2['x'], point2['y']])
        c = np.array([point3['x'], point3['y']])
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        
        return angle
