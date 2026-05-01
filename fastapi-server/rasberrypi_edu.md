Python 3.10 직접 설치하기

cd ~
sudo apt update

sudo apt install -y build-essential wget libssl-dev zlib1g-dev \
libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
libffi-dev libbz2-dev liblzma-dev

cd /usr/src

sudo wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz

sudo tar xzf Python-3.10.14.tgz

cd Python-3.10.14

sudo ./configure --enable-optimizations

sudo make -j4

sudo make altinstall 

python3.10 --version
AI풀스택개발자 — 2026-04-21 오후 3:28
---------------------------------------------------
카메라 케이블 연결과 설정
2.1 카메라 케이블 연결
만약, 가장 끝(SD 메모리 탑재위치 바로 위)에 있는 포트가 제대로 인식되지 않는 경우에는
중간에 포트에 연결합니다. 
카메라 케이블 방향은 라즈베리파이 보드의 CSI 포트에 꽂힌 파란색 테이프 부분이 
이더넷/USB 포트 방향을 향하고 있는지 확인하세요. (반대로 꽂으면 절대 인식되지 않습니다.)
2.2 카메라 케이블 설정
라즈베리 파이를 새롭게 기동하고, ssh 연결 후 /boot/firmware/config.txt  파일의 내용을
자동 감지를 끄고 수동으로 설정합니다.
AI풀스택개발자 — 2026-04-21 오후 3:44
sudo nano /boot/firmware/config.txt
자동 감지 끄기: camera_auto_detect=1을 찾아 앞에 #을 붙입니다.
camera_auto_detect=1
카메라 수동 지정: 그 바로 아래줄에 본인이 사용 중인 카메라 모델명을 입력합니다. (가장 흔한 v1.3 카메라 기준)
dtoverlay=ov5647
AI풀스택개발자 — 2026-04-21 오후 3:56
dtparam=audio=on

dtoverlay=ov5647

display_auto_detect=1

auto_initramfs=1

dtoverlay=vc4-kms-v3d

max_framebuffers=2

disable_fw_kms_setup=1

arm_64bit=1

disable_overscan=1

[cm4]
otg_mode=1

[cm5]
dtoverlay=dwc2,dr_mode=host

[all]
enable_uart=1
AI풀스택개발자 — 2026-04-21 오후 4:10
---------------------------------------------------
v4l2-ctl --list-devices
sudo apt install -y python3-libcamera

sudo apt install -y python3-kms++

sudo apt install -y python3-picamera2 

sudo apt install -y libcamera-tools
--------------------------------------------------
cd ~/projects/iot

rm -rf venv

python3  -m venv --system-site-packages venv

source venv/bin/activate 
AI풀스택개발자 — 2026-04-21 오후 4:20
----------------------------------------
(venv) lector@lector:~/projects/iot $ pip install opencv-python
현재 터미널 세션에 디스플레이 경로 지정
export DISPLAY=:0
Qt의 공유 메모리 오류 방지
export QT_X11_NO_MITSHM=1
---------------------------------------
opencv_test.py
import cv2

print(cv2.version)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 쓸수 없습니다.")
    exit()

print("웹캠 해상도:", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
AI풀스택개발자 — 2026-04-21 오후 4:34
-----------------------------------
opencv_test2.py
------------------------------------
import sys
라즈베리파이 시스템 패키지 경로를 리스트에 추가
sys.path.append('/usr/lib/python3/dist-packages')
import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
설정 생성 (640x480, RGB888 형식)
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

print("드디어 화면이 나옵니다! 종료하려면 ESC를 누르세요.")

try:
    while True:
        # 프레임 캡처 (NumPy 배열 형태)
        frame = picam2.capture_array()

RGB를 BGR로 변환 (OpenCV 표준)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        cv2.imshow("Raspberry Pi AI Camera", frame_bgr)

        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()


import cv2
from picamera2 import Picamera2

# 1. Picamera2 초기화
picam2 = Picamera2()

# 2. 설정 생성 (640x480, RGB888 형식)
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)

# 3. 카메라 시작
picam2.start()

print("카메라 실행 성공! 종료하려면 ESC를 누르세요.")

try:
    while True:
        # 프레임 캡처 (NumPy 배열 형태)
        frame = picam2.capture_array()
        
        # RGB를 BGR로 변환 (OpenCV 표준)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        cv2.imshow("Raspberry Pi AI Camera", frame_bgr)
        
        # ESC 키(27) 누르면 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    # 자원 해제
    picam2.stop()
    cv2.destroyAllWindows()

import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

# 1. YOLOv8 Nano 모델 로드
model = YOLO('yolov8n.pt')

# 2. Picamera2 설정
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

print("YOLOv8 객체 탐지 시작... 종료하려면 ESC를 누르세요.")

try:
    while True:
        # 카메라 프레임 획득
        frame = picam2.capture_array()
        
        # YOLOv8 추론 (실시간 분석)
        # stream=True 옵션은 메모리 관리에 효율적입니다.
        results = model(frame, stream=True, conf=0.5) 
        
        # 결과 시각화 (Bounding Box 그리기)
        for r in results:
            annotated_frame = r.plot() # 탐지된 객체가 그려진 이미지 반환
            
        # OpenCV는 BGR을 사용하므로 변환
        final_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)
        
        cv2.imshow("YOLOv8 Real-time Detection", final_frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
finally:
    picam2.stop()
    cv2.destroyAllWindows()