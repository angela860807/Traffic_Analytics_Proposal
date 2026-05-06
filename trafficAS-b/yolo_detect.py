# ============================================================
#  FastAPI — 차량 탐지 최적화 버전
#  EasyOCR은 5번에 1번만 실행 (속도 ↑↑)
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64, cv2, numpy as np, os, time
from ultralytics import YOLO

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 모델 로드 ──
MODEL_PATH = "best.pt"
TEMP_MODEL = "yolov8n.pt"
model = YOLO(MODEL_PATH) if os.path.exists(MODEL_PATH) else YOLO(TEMP_MODEL)

# EasyOCR — 느리므로 지연 로드
_reader = None
def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['ko', 'en'], gpu=False)
    return _reader

VEHICLE_CLASSES = {2:'승용차', 3:'오토바이', 5:'버스', 7:'트럭'}

# 세그먼트별 호출 카운터 (5번에 1번만 OCR)
call_count = {}
# 세그먼트별 마지막 번호판 캐시
plate_cache = {}

class DetectRequest(BaseModel):
    image: str
    seg_id: str

class Detection(BaseModel):
    x: float
    y: float
    w: float
    h: float
    conf: float
    plate: str
    type: str

@app.post("/detect", response_model=list[Detection])
async def detect(req: DetectRequest):
    seg_id = req.seg_id
    call_count[seg_id] = call_count.get(seg_id, 0) + 1
    do_ocr = (call_count[seg_id] % 5 == 0)  # 5번에 1번만 OCR

    # base64 → numpy (320px로 더 작게)
    img_bytes = base64.b64decode(req.image.split(",")[-1])
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return []

    H, W = img.shape[:2]

    # YOLO 추론 (이미지 크기 320으로 줄여서 빠르게)
    preds = model(img, conf=0.30, imgsz=320, verbose=False)
    results = []

    for pred in preds:
        for box in pred.boxes:
            cls_id = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])

            if os.path.exists(MODEL_PATH):
                vtype = '번호판'
            else:
                vtype = VEHICLE_CLASSES.get(cls_id)
                if not vtype:
                    continue

            # OCR — 5번에 1번만 실행, 나머지는 캐시 사용
            box_key = f"{seg_id}_{len(results)}"
            if do_ocr:
                plate_text = ""
                try:
                    crop_y1 = y1 + int((y2 - y1) * 0.65)
                    crop = img[crop_y1:y2, x1:x2]
                    if crop.size > 100:
                        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                        sharp = cv2.convertScaleAbs(gray, alpha=1.8, beta=30)
                        # 이미지 확대 (OCR 정확도 ↑)
                        sharp = cv2.resize(sharp, None, fx=2, fy=2)
                        ocr_res = get_reader().readtext(sharp, detail=0)
                        candidates = [t.strip() for t in ocr_res if len(t.strip()) >= 4]
                        plate_text = candidates[0][:12] if candidates else ""
                except:
                    plate_text = ""
                plate_cache[box_key] = plate_text or "인식 중..."
            else:
                plate_text = plate_cache.get(box_key, "인식 중...")

            results.append(Detection(
                x=x1/W, y=y1/H,
                w=(x2-x1)/W, h=(y2-y1)/H,
                conf=round(conf*100, 1),
                plate=plate_text,
                type=vtype,
            ))

    return results

@app.get("/health")
def health():
    m = MODEL_PATH if os.path.exists(MODEL_PATH) else TEMP_MODEL
    return {"status": "ok", "model": m}

# ── ITS CCTV 프록시 (브라우저 CORS 우회) ──
import requests as req_lib
from fastapi.responses import JSONResponse

@app.get("/cctv")
def cctv_proxy(key: str, minX: float=126.7, maxX: float=127.4, minY: float=37.3, maxY: float=37.7):
    try:
        url = (
            f"https://openapi.its.go.kr:9443/cctvInfo"
            f"?apiKey={key}&type=its&cctvType=1&getType=json"
            f"&minX={minX}&maxX={maxX}&minY={minY}&maxY={maxY}"
        )
        res  = req_lib.get(url, timeout=10)
        data = res.json()
        return data
    except Exception as e:
        return JSONResponse({"error": str(e), "cctvList": []}, status_code=200)

# ── WebSocket ──
from fastapi import WebSocket
import asyncio

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(data)  # echo (라즈베리파이 연동 시 교체)
    except:
        pass