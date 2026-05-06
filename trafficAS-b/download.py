import urllib.request

url = 'https://github.com/Muhammad-Zeerak-Khan/Automatic-License-Plate-Recognition-using-YOLOv8/raw/main/license_plate_detector.pt'
print('다운로드 중...')
urllib.request.urlretrieve(url, 'best.pt')
print('완료! best.pt 저장됨')