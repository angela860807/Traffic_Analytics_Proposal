from dataclasses import dataclass
from datetime import datetime
from threading import Lock

@dataclass
class LatestFrame:
    camera_code: str
    captured_at: datetime
    content_type: str
    image_bytes: bytes
    
class FrameBuffer:
    def __init__(self) -> None:
        self._lock = Lock()
        self._latest_frame: LatestFrame | None = None
        
    def set_frame(self, frame: LatestFrame) -> None:
        with self._lock:
            self._latest_frame = frame
            
    def get_frame(self) -> LatestFrame | None:
        with self._lock:
            return self._latest_frame
        
frame_buffer = FrameBuffer()