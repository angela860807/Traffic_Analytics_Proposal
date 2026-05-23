<template>
  <div class="chat">
    <div class="online-bar">
      <span class="olabel"><span class="odot"></span>AI 어시스턴트 연결됨</span>
      <span class="meta">· LLaMA 3.3 · Groq · 실시간</span>
      <button class="reset-btn" @click="resetChat" title="대화 초기화">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <polyline points="1 4 1 10 7 10" />
          <path d="M3.51 15a9 9 0 1 0 .49-3.75" />
        </svg>
        초기화
      </button>
    </div>

    <div class="msgs" ref="msgsEl">
      <template v-for="m in messages" :key="m.id">
        <div class="sys" v-if="m.type === 'sys'">{{ m.text }}</div>
        <div class="msg" :class="{ mine: m.mine }" v-else>
          <div class="av">{{ m.avatar }}</div>
          <div class="body">
            <div class="name">{{ m.name }}</div>
            <div class="bubble" :class="{ error: m.error }">{{ m.text }}</div>
            <div class="time">{{ m.time }}</div>
          </div>
        </div>
      </template>

      <!-- 타이핑 인디케이터 -->
      <div class="msg" v-if="thinking">
        <div class="av">🤖</div>
        <div class="body">
          <div class="name">AI 어시스턴트</div>
          <div class="bubble typing"><span></span><span></span><span></span></div>
        </div>
      </div>
    </div>

    <!-- API 키 미설정 경고 -->
    <div class="no-key" v-if="!hasKey">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span
        ><code>.env</code> 파일에 <code>VITE_GROQ_API_KEY</code>를 설정해야
        합니다.</span
      >
    </div>

    <div class="bar">
      <input
        class="ci"
        v-model="input"
        placeholder="TrafficAS에 대해 무엇이든 질문하세요... (Enter)"
        @keyup.enter="send"
        :disabled="thinking || !hasKey"
      />
      <button class="sbtn" @click="send" :disabled="thinking || !hasKey">
        <svg
          v-if="thinking"
          class="spin-icon"
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M21 12a9 9 0 1 1-6.219-8.56" />
        </svg>
        <span v-else>전송</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from "vue";

const API_KEY = import.meta.env.VITE_GROQ_API_KEY;
const hasKey = computed(() => !!API_KEY && API_KEY.startsWith("gsk_"));

const SYSTEM_PROMPT = `당신은 TrafficAS 고객지원 AI 어시스턴트입니다.

[절대 규칙]
- 반드시 한국어로만 답변하세요. 영어, 중국어, 일본어 등 어떤 외국어도 섞지 마세요.
- 답변은 핵심만 간결하게 2~4문장으로 작성하세요.
- 친절하고 전문적인 톤을 유지하세요.

TrafficAS 교통 관제 시스템 정보:
- 실시간 차량 감지 및 분류 (YOLO 기반)
- OCR 번호판 자동 인식 (97%+ 정확도)
- 구역별 유입·유출 통계 대시보드
- 시간대별 혼잡도 히트맵 시각화
- 기술 스택: Spring Boot + Vue.js 3 + PostgreSQL`;

const msgsEl = ref(null);
const input = ref("");
const thinking = ref(false);
const history = ref([]); // 대화 히스토리 (OpenAI 형식)
let seq = 10;

const messages = ref([
  { id: 1, type: "sys", text: "AI 어시스턴트와 대화를 시작하세요." },
  {
    id: 2,
    type: "msg",
    mine: false,
    avatar: "🤖",
    name: "AI 어시스턴트",
    text:
      "안녕하세요! TrafficAS AI 어시스턴트입니다. 시스템 사용법, 설치, 오류 해결 등 무엇이든 질문해 주세요.",
    time: now(),
  },
]);

function now() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(
    2,
    "0"
  )}`;
}

async function scrollBottom() {
  await nextTick();
  if (msgsEl.value) msgsEl.value.scrollTop = msgsEl.value.scrollHeight;
}

async function send() {
  const text = input.value.trim();
  if (!text || thinking.value || !hasKey.value) return;

  // 내 메시지 추가
  messages.value.push({
    id: ++seq,
    type: "msg",
    mine: true,
    avatar: "😀",
    name: "나",
    text,
    time: now(),
  });
  input.value = "";
  thinking.value = true;
  await scrollBottom();

  try {
    const reply = await callGroq(text);
    messages.value.push({
      id: ++seq,
      type: "msg",
      mine: false,
      avatar: "🤖",
      name: "AI 어시스턴트",
      text: reply,
      time: now(),
    });
  } catch (e) {
    console.error("[Groq Error]", e);
    messages.value.push({
      id: ++seq,
      type: "msg",
      mine: false,
      avatar: "🤖",
      name: "AI 어시스턴트",
      text: `오류: ${e.message || "알 수 없는 오류"}`,
      time: now(),
      error: true,
    });
  } finally {
    thinking.value = false;
    await scrollBottom();
  }
}

async function callGroq(userText) {
  history.value.push({ role: "user", content: userText });

  const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${API_KEY}`,
    },
    body: JSON.stringify({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        ...history.value,
      ],
      max_tokens: 512,
      temperature: 0.3,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error?.message || `HTTP ${res.status}`);
  }

  const data = await res.json();
  const reply = data.choices?.[0]?.message?.content ?? "응답을 받지 못했습니다.";

  history.value.push({ role: "assistant", content: reply });

  return reply;
}

function resetChat() {
  history.value = [];
  messages.value = [
    { id: 1, type: "sys", text: "대화가 초기화되었습니다." },
    {
      id: 2,
      type: "msg",
      mine: false,
      avatar: "🤖",
      name: "AI 어시스턴트",
      text:
        "안녕하세요! TrafficAS AI 어시스턴트입니다. 시스템 사용법, 설치, 오류 해결 등 무엇이든 질문해 주세요.",
      time: now(),
    },
  ];
  seq = 10;
}
</script>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
}

/* ── 상단바 ── */
.online-bar {
  padding: 10px 20px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
  display: flex;
  align-items: center;
  gap: 8px;
}
.olabel {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: var(--in);
  display: flex;
  align-items: center;
  gap: 5px;
}
.odot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--in);
  animation: livePulse 1.5s ease-in-out infinite;
}
.meta {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  flex: 1;
}
.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  background: none;
  border: 1px solid var(--b);
  border-radius: 4px;
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  cursor: pointer;
  transition: all 0.2s;
  letter-spacing: 0.04em;
}
.reset-btn:hover {
  border-color: var(--ba);
  color: var(--a);
}

/* ── 메시지 영역 ── */
.msgs {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msgs::-webkit-scrollbar {
  width: 3px;
}
.msgs::-webkit-scrollbar-thumb {
  background: var(--b);
  border-radius: 2px;
}

.sys {
  text-align: center;
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: var(--t3);
  display: flex;
  align-items: center;
  gap: 8px;
}
.sys::before,
.sys::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--b);
}

.msg {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.msg.mine {
  flex-direction: row-reverse;
}
.av {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--b);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  flex-shrink: 0;
  background: var(--bg2);
}
.body {
  max-width: 72%;
}
.name {
  font-family: "JetBrains Mono", monospace;
  font-size: 10px;
  color: var(--t3);
  margin-bottom: 4px;
}
.msg.mine .name {
  text-align: right;
}

.bubble {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  line-height: 1.7;
  background: var(--card);
  border: 1px solid var(--b);
  color: var(--t);
  white-space: pre-wrap;
  word-break: break-word;
}
.msg.mine .bubble {
  background: var(--a);
  border-color: var(--a);
  color: #fff;
}
.bubble.error {
  border-color: rgba(248, 113, 113, 0.3);
  color: #f87171;
  background: rgba(248, 113, 113, 0.06);
}

/* 타이핑 인디케이터 */
.bubble.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  min-width: 52px;
}
.bubble.typing span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--t3);
  animation: bounce 1.2s ease-in-out infinite;
}
.bubble.typing span:nth-child(2) {
  animation-delay: 0.2s;
}
.bubble.typing span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes bounce {
  0%,
  60%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-5px);
    opacity: 1;
  }
}

.time {
  font-family: "JetBrains Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  margin-top: 4px;
}
.msg.mine .time {
  text-align: right;
}

/* API 키 없음 경고 */
.no-key {
  margin: 0 20px 0;
  padding: 10px 14px;
  background: rgba(251, 146, 60, 0.08);
  border: 1px solid rgba(251, 146, 60, 0.25);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #fb923c;
}
.no-key code {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  background: rgba(251, 146, 60, 0.12);
  padding: 1px 5px;
  border-radius: 3px;
}

/* ── 입력바 ── */
.bar {
  padding: 14px 20px;
  border-top: 1px solid var(--b);
  display: flex;
  gap: 10px;
  background: var(--bg2);
}
.ci {
  flex: 1;
  background: var(--bg);
  border: 1px solid var(--b);
  border-radius: 6px;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--t);
  font-family: "Noto Sans KR", sans-serif;
  outline: none;
  transition: border-color 0.2s;
}
.ci:focus {
  border-color: var(--ba);
}
.ci::placeholder {
  color: var(--t3);
}
.ci:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.sbtn {
  padding: 10px 20px;
  background: var(--a);
  color: var(--bg);
  border: none;
  border-radius: 6px;
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  transition: opacity 0.2s;
}
.sbtn:hover:not(:disabled) {
  opacity: 0.87;
}
.sbtn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.spin-icon {
  animation: spin 0.9s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
