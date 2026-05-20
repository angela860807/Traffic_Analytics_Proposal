// 관제센터 → 단속관리팀 위반 전송 큐 (프론트엔드 전용)
// 캡처 이미지 + 메타데이터를 localStorage에 푸시 → 단속관리팀이 마운트 시 흡수
import { ref } from "vue";

const STORAGE_KEY = "tas_violation_queue";
const MAX_ITEMS = 20;

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

const queue = ref(loadFromStorage());

function saveToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(queue.value));
  } catch (e) {
    // localStorage 용량 초과 시 가장 오래된 항목 제거
    console.warn("[violation queue] storage full, dropping oldest", e);
    queue.value = queue.value.slice(0, Math.floor(MAX_ITEMS / 2));
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(queue.value));
    } catch {}
  }
}

function pad(n) { return String(n).padStart(2, "0"); }
function nowStr() {
  const d = new Date();
  return `${d.getHours()}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}
function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// 가상 한국 번호판 생성 (시연용)
const HANGUL_PLATE_LETTERS = ["가", "나", "다", "라", "마", "바", "사", "아", "자", "허", "호", "더", "루"];
function genFakePlate() {
  const a = 10 + Math.floor(Math.random() * 89);
  const b = HANGUL_PLATE_LETTERS[Math.floor(Math.random() * HANGUL_PLATE_LETTERS.length)];
  const c = 1000 + Math.floor(Math.random() * 9000);
  return `${a}${b} ${c}`;
}

function submitViolation(payload) {
  const time = nowStr();
  const dateStr = todayStr();
  const item = {
    id: `RT-${Date.now()}`,
    evtId: `EVT-${dateStr.replace(/-/g, "")}-${time.replace(/:/g, "")}`,
    time,
    date: dateStr,
    place: payload.place || "관제센터 전송 영상",
    type: "속도 위반",
    typeTone: "tg-rd",
    plate: payload.plate || genFakePlate(),
    conf: payload.conf ?? (90 + Math.floor(Math.random() * 9)),
    st: "검토 대기",
    detectSpeed: payload.detectSpeed ?? (85 + Math.floor(Math.random() * 45)),
    limitSpeed: payload.limitSpeed ?? 80,
    camera: payload.camera || "CTRL-AUTO",
    lane: payload.lane ?? Math.ceil(Math.random() * 3),
    image: payload.image || "",
    source: "control",
    submittedAt: Date.now(),
  };
  queue.value.unshift(item);
  if (queue.value.length > MAX_ITEMS) {
    queue.value = queue.value.slice(0, MAX_ITEMS);
  }
  saveToStorage();
  return item;
}

function clearQueue() {
  queue.value = [];
  saveToStorage();
}

export function useViolationQueue() {
  return { queue, submitViolation, clearQueue };
}
