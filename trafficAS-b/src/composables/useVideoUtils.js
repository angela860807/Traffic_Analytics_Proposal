// 시간/비디오 공용 유틸 — ControlView · ReviewView 공유

export function padNum(n) {
  return String(n).padStart(2, "0");
}

export function fmtDateTime(d = new Date()) {
  return `${d.getFullYear()}-${padNum(d.getMonth() + 1)}-${padNum(d.getDate())} ${padNum(d.getHours())}:${padNum(d.getMinutes())}:${padNum(d.getSeconds())}`;
}

export function fmtDate(d = new Date()) {
  return `${d.getFullYear()}-${padNum(d.getMonth() + 1)}-${padNum(d.getDate())}`;
}

export function fmtTime(d = new Date()) {
  return `${padNum(d.getHours())}:${padNum(d.getMinutes())}:${padNum(d.getSeconds())}`;
}

export function enterFullscreen(el) {
  const target = el?.value || el;
  if (!target) return;
  const req =
    target.requestFullscreen ||
    target.webkitRequestFullscreen ||
    target.msRequestFullscreen;
  if (req) req.call(target).catch(() => {});
}

// 비디오 프레임을 dataURL로 캡처 (옵션: 크롭 영역)
export function captureFrameDataURL(videoEl, opts = {}) {
  const v = videoEl?.value || videoEl;
  if (!v || !v.videoWidth) return "";
  const {
    outWidth = 640,
    crop = null,        // { x, y, w, h } - 비디오 좌표 기준
    quality = 0.9,
  } = opts;
  try {
    const vw = v.videoWidth;
    const vh = v.videoHeight;
    const sx = crop ? crop.x : 0;
    const sy = crop ? crop.y : 0;
    const sw = crop ? crop.w : vw;
    const sh = crop ? crop.h : vh;
    const outW = outWidth;
    const outH = Math.round(outW * (sh / sw));
    const canvas = document.createElement("canvas");
    canvas.width = outW;
    canvas.height = outH;
    const ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(v, sx, sy, sw, sh, 0, 0, outW, outH);
    return canvas.toDataURL("image/jpeg", quality);
  } catch {
    return "";
  }
}

// 비디오 seek (Promise로 wrap)
export function seekVideo(videoEl, t) {
  const v = videoEl?.value || videoEl;
  if (!v) return Promise.resolve();
  return new Promise((resolve) => {
    const handler = () => {
      v.removeEventListener("seeked", handler);
      resolve();
    };
    v.addEventListener("seeked", handler);
    v.currentTime = Math.max(0, Math.min(v.duration || 0, t));
  });
}
