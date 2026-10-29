import cv2
from src.config import COLOR_PALETTE


class CanvasHUD:
    @staticmethod
    def draw_interface(frame, active_tool, mode_text, fps):
        h, w, _ = frame.shape
        overlay = frame.copy()

        # Header Bar & Status Panel
        cv2.rectangle(overlay, (16, 16), (w - 16, 76), (18, 18, 22), -1)
        cv2.rectangle(overlay, (16, h - 54), (430, h - 16), (18, 18, 22), -1)
        cv2.addWeighted(overlay, 0.82, frame, 0.18, 0, frame)

        cv2.rectangle(frame, (16, 16), (w - 16, 76), (82, 82, 91), 1)
        cv2.rectangle(frame, (16, h - 54), (430, h - 16), (82, 82, 91), 1)

        # Title & Telemetry
        cv2.putText(
            frame, "AIR_CANVAS // STUDIO CORE",
            (30, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (250, 250, 250), 1, cv2.LINE_AA
        )
        cv2.putText(
            frame, f"MODE: {mode_text}  |  TOOL: {active_tool}",
            (30, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (16, 185, 129), 1, cv2.LINE_AA
        )

        # Palette Buttons
        tools = [
            ("EMERALD", 340, COLOR_PALETTE["EMERALD"]),
            ("CYAN", 450, COLOR_PALETTE["CYAN"]),
            ("AMBER", 560, COLOR_PALETTE["AMBER"]),
            ("ERASER", 670, (161, 161, 170))
        ]

        for name, x_center, color in tools:
            is_selected = (active_tool == name)
            x1, y1, x2, y2 = x_center - 48, 26, x_center + 48, 66
            cv2.rectangle(frame, (x1, y1), (x2, y2), (28, 28, 34), -1)
            cv2.rectangle(
                frame, (x1, y1), (x2, y2),
                color if is_selected else (82, 82, 91),
                2 if is_selected else 1
            )
            cv2.putText(
                frame, name,
                (x1 + 12, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.38,
                (250, 250, 250) if is_selected else (161, 161, 170), 1, cv2.LINE_AA
            )

        # FPS & Controls
        cv2.putText(
            frame, f"FPS: {int(fps):02d}",
            (w - 110, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (16, 185, 129), 1, cv2.LINE_AA
        )
        cv2.putText(
            frame, "[1 FINGER] DRAW   [2 FINGERS] SELECT   [C] CLEAR   [S] SAVE   [Q] EXIT",
            (28, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (212, 212, 216), 1, cv2.LINE_AA
        )

        return frame