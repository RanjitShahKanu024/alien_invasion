import cv2
import mediapipe as mp

class HandController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.current_gesture = None
        self.cap = cv2.VideoCapture(0)  # Open default camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def get_hand_landmarks(self):
        """Processes a frame and returns hand landmarks if detected."""
        ret, frame = self.cap.read()
        if not ret:
            return None, None
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        # Draw hand landmarks if detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self._draw_hand_feedback(frame, hand_landmarks)
            return results.multi_hand_landmarks[0], frame
        return None, frame

    def _draw_hand_feedback(self, frame, landmarks):
        """Draws hand landmarks and additional visual feedback."""
        # Draw basic hand landmarks
        self.mp_drawing.draw_landmarks(
            frame, landmarks, self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
            self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
        )
        
        # Get wrist and index finger positions
        h, w, c = frame.shape
        wrist = landmarks.landmark[0]
        index_tip = landmarks.landmark[8]
        
        # Draw gesture-specific feedback
        if self.current_gesture:
            cv2.putText(frame, f"Gesture: {self.current_gesture}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (255, 255, 255), 2)
            
        # Draw connection line between wrist and index finger
        wrist_pos = (int(wrist.x * w), int(wrist.y * h))
        index_pos = (int(index_tip.x * w), int(index_tip.y * h))
        cv2.line(frame, wrist_pos, index_pos, (0, 255, 255), 2)

    def release(self):
        """Release camera resources."""
        self.cap.release()
        cv2.destroyAllWindows()
