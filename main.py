import os
import time
from datetime import datetime
import cv2

from src.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from src.canvas_core import AirCanvasEngine
from src.ui_renderer import CanvasHUD

OUTPUT_DIR = "outputs"


def main():
    # Menggunakan CAP_DSHOW agar inisialisasi webcam di Windows cepat & stabil
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[error] Kamera tidak dapat dibuka. Pastikan tidak dipakai aplikasi lain.")
        return

    engine = AirCanvasEngine()
    hud = CanvasHUD()
    prev_time = 0

    print("[canvas] Air Canvas Engine aktif. Jendela kamera sedang dibuka...")

    while True:
        success, frame = cap.read()
        if not success:
            print("[error] Gagal membaca frame dari kamera.")
            break

        frame = cv2.flip(frame, 1)
        index_tip, middle_tip, fingers = engine.process_frame(frame)
        mode_text = "STANDBY"

        # 2 Jari Terangkat (Telunjuk & Tengah) -> Mode Pilih Menu Warna
        if fingers[1] == 1 and fingers[2] == 1:
            mode_text = "SELECT_TOOL"
            engine.draw_on_canvas(0, 0, "SELECT")
            if index_tip:
                x, y = index_tip
                if 26 <= y <= 66:
                    if 292 <= x <= 388:
                        engine.set_tool("EMERALD")
                    elif 402 <= x <= 498:
                        engine.set_tool("CYAN")
                    elif 512 <= x <= 608:
                        engine.set_tool("AMBER")
                    elif 622 <= x <= 718:
                        engine.set_tool("ERASER")
                cv2.circle(frame, index_tip, 10, (250, 250, 250), 2)

        # 1 Jari Terangkat (Hanya Telunjuk) -> Mode Menggambar
        elif fingers[1] == 1 and fingers[2] == 0:
            mode_text = "DRAWING"
            if index_tip:
                engine.draw_on_canvas(index_tip[0], index_tip[1], "DRAW")
                cv2.circle(frame, index_tip, 8, engine.current_color, -1)
        else:
            engine.draw_on_canvas(0, 0, "SELECT")

        # Gabungkan layer lukisan dengan frame kamera
        gray_canvas = cv2.cvtColor(engine.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_canvas = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY_INV)
        inv_canvas = cv2.cvtColor(inv_canvas, cv2.COLOR_GRAY2BGR)

        frame = cv2.bitwise_and(frame, inv_canvas)
        frame = cv2.bitwise_or(frame, engine.canvas)

        # Hitung FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
        prev_time = curr_time

        frame = hud.draw_interface(frame, engine.active_tool, mode_text, fps)
        cv2.imshow("AIR_CANVAS // Studio Core", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            engine.reset_canvas()
            print("[canvas] Layar kanvas dibersihkan.")
        elif key == ord('s'):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            filename = os.path.join(
                OUTPUT_DIR,
                f"artwork_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            cv2.imwrite(filename, frame)
            print(f"[saved] Hasil gambar disimpan ke: {filename}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()