<template>
  <div class="dashboard-container">
    <div class="video-wrapper" style="position: relative; display: inline-block">
      <!-- 1. 비디오 엘리먼트 -->
      <video
        ref="videoRef"
        src="/road2.mp4"
        muted
        loop
        controls
        width="1280"
        @play="onVideoPlay"
      ></video>

      <!-- 2. 박스를 그릴 투명 캔버스 (영상 위에 겹침) -->
      <canvas
        ref="overlayRef"
        style="position: absolute; top: 0; left: 0; pointer-events: none"
      ></canvas>
    </div>

    <!-- 상태 표시 및 OCR 결과 확인용 (선택) -->
    <div class="info-panel">
      <p v-if="isLoading">모델 로딩 중...</p>
      <p v-else-if="isReady">✅ 번호판 감지 시스템 가동 중</p>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import { useYoloDetect } from "@/composables/useYoloDetect"; // 경로 확인

const videoRef = ref(null);
const overlayRef = ref(null);
const { isReady, isLoading, error, loadModel, detect } = useYoloDetect();

let animationId = null;

onMounted(async () => {
  // 1. 모델 로드 (public/models 폴더에 파일이 있어야 함)
  await loadModel("/models/plate_detect.onnx");
});

const onVideoPlay = () => {
  renderLoop();
};

const renderLoop = async () => {
  if (!videoRef.value || videoRef.value.paused || videoRef.value.ended) return;

  const video = videoRef.value;
  const canvas = overlayRef.value;
  const ctx = canvas.getContext("2d");

  // 캔버스 크기를 비디오 실제 크기에 맞춤
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // 2. YOLO 탐지 실행
  const boxes = await detect(video);

  // 3. 결과 그리기
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  boxes.forEach((box) => {
    // 박스 그리기
    ctx.strokeStyle = "#00ff00"; // 형광 녹색
    ctx.lineWidth = 4;
    ctx.strokeRect(box.x1, box.y1, box.x2 - box.x1, box.y2 - box.y1);

    // 라벨 표시 (신뢰도)
    ctx.fillStyle = "#00ff00";
    ctx.font = "20px Arial";
    ctx.fillText(
      `Plate: ${Math.round(box.conf * 100)}%`,
      box.x1,
      box.y1 > 20 ? box.y1 - 5 : box.y1 + 20
    );
  });

  // 다음 프레임 요청 (실시간 루프)
  animationId = requestAnimationFrame(renderLoop);
};

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId);
});
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #1a1a1a;
  padding: 20px;
  border-radius: 12px;
}

.error {
  color: #ff4444;
}
.info-panel {
  margin-top: 15px;
  color: white;
}
</style>
