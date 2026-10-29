import cv2
import mediapipe as mp
import numpy as np
from src.config import COLOR_PALETTE, DEFAULT_BRUSH_SIZE, ERASER_BRUSH_SIZE


class AirCanvasEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.canvas = None
        self.prev_x, self.prev_y = 0, 0
        self.current_color = COLOR_PALETTE["EMERALD"]
        self.current_thickness = DEFAULT_BRUSH_SIZE
        self.active_tool = "EMERALD"

    def ensure_canvas(self, frame):
        h, w, _ = frame.shape
        if self.canvas is None or self.canvas.shape[:2] != (h, w):
            self.canvas = np.zeros((h, w, 3), dtype=np.uint8)

    def process_frame(self, frame):
        self.ensure_canvas(frame)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        index_tip = None
        middle_tip = None
        fingers_status = [0, 0, 0, 0, 0]

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]

            idx_lm = hand_landmarks.landmark[8]
            mid_lm = hand_landmarks.landmark[12]

            index_tip = (int(idx_lm.x * w), int(idx_lm.y * h))
            middle_tip = (int(mid_lm.x * w), int(mid_lm.y * h))

            if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:
                fingers_status[1] = 1
            if hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y:
                fingers_status[2] = 1

            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(240, 240, 240), thickness=1, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(16, 185, 129), thickness=2, circle_radius=1)
            )

        return index_tip, middle_tip, fingers_status

    def draw_on_canvas(self, x, y, mode):
        if mode == "SELECT":
            self.prev_x, self.prev_y = 0, 0
            return

        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = x, y

        if mode == "DRAW":
            color = (0, 0, 0) if self.active_tool == "ERASER" else self.current_color
            thickness = ERASER_BRUSH_SIZE if self.active_tool == "ERASER" else self.current_thickness
            cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), color, thickness)

        self.prev_x, self.prev_y = x, y

    def reset_canvas(self):
        if self.canvas is not None:
            self.canvas.fill(0)

    def set_tool(self, tool_name):
        self.active_tool = tool_name
        if tool_name in COLOR_PALETTE and tool_name != "ERASER":
            self.current_color = COLOR_PALETTE[tool_name]