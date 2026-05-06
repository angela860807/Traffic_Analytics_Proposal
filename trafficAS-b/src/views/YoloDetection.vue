<template>
  <div class="dashboard-card">
    <h3>실시간 객체 검출 대시보드</h3>

    <!-- 이미지 업로드 -->
    <input type="file" @change="handleFileUpload" accept="image/*" />

    <div class="canvas-container" style="position: relative; margin-top: 20px">
      <!-- 원본 이미지 표시용 (숨김 처리 가능) -->
      <img ref="imageRef" :src="imageSrc" @load="detect" v-show="false" />

      <!-- 결과 출력용 캔버스 -->
      <canvas ref="canvasRef"></canvas>
    </div>

    <p v-if="isLoading">모델 로딩 중...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import * as ort from "onnxruntime-web";

const imageRef = ref(null);
const canvasRef = ref(null);
const imageSrc = ref("");
const isLoading = ref(true);
let session = null;

// 1. 컴포넌트 마운트 시 모델 로드
onMounted(async () => {
  try {
    // public/models/your_model.onnx 경로에 파일이 있어야 함
    session = await ort.InferenceSession.create("/models/your_model.onnx", {
      executionProviders: ["wasm"],
      graphOptimizationLevel: "all",
    });
    isLoading.value = false;
    console.log("모델 로드 완료");
  } catch (e) {
    console.error("모델 로드 실패:", e);
  }
});

// 2. 파일 업로드 핸들러
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file) {
    imageSrc.value = URL.createObjectURL(file);
  }
};

// 3. 추론 및 결과 그리기
const detect = async () => {
  if (!session || !imageRef.value) return;

  const canvas = canvasRef.value;
  const ctx = canvas.getContext("2d");
  const img = imageRef.value;

  // 캔버스 크기를 이미지에 맞춤
  canvas.width = img.width;
  canvas.height = img.height;
  ctx.drawImage(img, 0, 0);

  // --- 전처리 및 추론 로직 (이전 답변 코드 참고) ---
  // const input = await preprocess(img, 640, 640);
  // const results = await session.run({ [session.inputNames[0]]: input });
  // renderBoxes(results, ctx);
};
</script>

<style scoped>
.canvas-container canvas {
  max-width: 100%;
  border: 1px solid #ddd;
  border-radius: 8px;
}
</style>
