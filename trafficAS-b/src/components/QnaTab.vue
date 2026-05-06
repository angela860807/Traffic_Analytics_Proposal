<template>
  <div class="qna">
    <div class="top-row">
      <p class="info">궁금한 점을 질문하고 전문가 답변을 받으세요.</p>
      <button class="wbtn">질문하기</button>
    </div>

    <div class="search-bar">
      <span class="s-ico">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="13"
          height="13"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </span>
      <input
        v-model="query"
        type="text"
        placeholder="질문 제목 또는 작성자 검색..."
        class="s-input"
      />
      <button v-if="query" class="s-clear" @click="query = ''">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
      <span class="s-count" v-if="query">{{ filtered.length }}건</span>
    </div>

    <div class="tbl">
      <div class="th grid3"><span>질문</span><span>작성자</span><span>상태</span></div>
      <template v-if="filtered.length">
        <template v-for="q in filtered" :key="q.id">
          <div
            class="tr grid3"
            @click="toggle(q.id)"
            :class="{ active: expandedId === q.id }"
          >
            <span class="ttl">
              <svg
                class="chv"
                :class="{ open: expandedId === q.id }"
                width="10"
                height="10"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
              <span class="ttl-text">
                <template v-if="query"
                  ><span v-html="highlight(q.title)"></span
                ></template>
                <template v-else>{{ q.title }}</template>
              </span>
              <span class="nb" v-if="q.isNew">NEW</span>
            </span>
            <span class="sub">{{ q.author }}</span>
            <span
              ><span class="sts" :class="getStatusCls(q)">{{ getStatus(q) }}</span></span
            >
          </div>

          <!-- 답변 패널 -->
          <div class="apanel" v-if="expandedId === q.id" @click.stop>
            <!-- 질문 본문 -->
            <div class="qbody">
              <div class="qbody-head">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                질문
              </div>
              <p class="qbody-text">{{ q.body || q.title }}</p>
              <div class="qmeta">작성자: {{ q.author }}</div>
            </div>

            <!-- 기존 답변 표시 -->
            <div class="answer-box" v-if="getAnswer(q.id)">
              <div class="answer-head">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="9 11 12 14 22 4" />
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                </svg>
                관리자 답변
                <span class="answer-time">{{ getAnswer(q.id).time }}</span>
                <button class="cact" v-if="isAdmin" @click="startAnswerEdit(q.id)">
                  수정
                </button>
              </div>
              <div v-if="editingAnswerId !== q.id" class="answer-text">
                {{ getAnswer(q.id).text }}
              </div>
              <!-- 관리자 수정 폼 -->
              <div class="answer-form" v-else>
                <textarea
                  class="cta"
                  v-model="answerDraft"
                  rows="4"
                  placeholder="답변을 입력하세요..."
                />
                <div class="cbtns">
                  <button
                    class="cbtn-save"
                    @click="saveAnswer(q.id)"
                    :disabled="!answerDraft.trim()"
                  >
                    저장
                  </button>
                  <button class="cbtn-cancel" @click="cancelAnswerEdit">취소</button>
                </div>
              </div>
            </div>

            <!-- 관리자: 답변 작성 -->
            <div class="answer-form-wrap" v-else-if="isAdmin">
              <div class="answer-head write">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
                답변 작성
              </div>
              <div class="answer-form">
                <textarea
                  class="cta"
                  v-model="answerDraft"
                  rows="4"
                  placeholder="질문에 대한 답변을 작성하세요..."
                />
                <div class="cbtns">
                  <button
                    class="cbtn-save"
                    @click="saveAnswer(q.id)"
                    :disabled="!answerDraft.trim()"
                  >
                    답변 등록
                  </button>
                </div>
              </div>
            </div>

            <!-- 일반 사용자: 답변 대기 -->
            <div class="waiting" v-else>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <span>관리자 답변을 기다리고 있습니다.</span>
            </div>
          </div>
        </template>
      </template>
      <div v-else class="empty">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <span>검색 결과가 없습니다.</span>
      </div>
    </div>

    <!-- 관리자 배지 -->
    <div class="admin-badge" v-if="isAdmin">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="10"
        height="10"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      </svg>
      관리자 모드 활성화 — 답변 작성/수정 가능
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAuth } from "../composables/useAuth";

const { isAdmin } = useAuth();

const query = ref("");
const expandedId = ref(null);
const answerDraft = ref("");
const editingAnswerId = ref(null);

const answersStore = ref(JSON.parse(localStorage.getItem("tas_qna_answers") || "{}"));

function persist() {
  localStorage.setItem("tas_qna_answers", JSON.stringify(answersStore.value));
}

function getAnswer(itemId) {
  return answersStore.value[itemId] || null;
}

function getStatus(item) {
  return answersStore.value[item.id] ? "답변완료" : item.status;
}

function getStatusCls(item) {
  return answersStore.value[item.id] ? "done" : item.cls;
}

function toggle(itemId) {
  if (expandedId.value === itemId) {
    expandedId.value = null;
  } else {
    expandedId.value = itemId;
    cancelAnswerEdit();
    if (!getAnswer(itemId)) answerDraft.value = "";
  }
}

function startAnswerEdit(itemId) {
  editingAnswerId.value = itemId;
  answerDraft.value = getAnswer(itemId)?.text || "";
}

function cancelAnswerEdit() {
  editingAnswerId.value = null;
  answerDraft.value = "";
}

function saveAnswer(itemId) {
  const text = answerDraft.value.trim();
  if (!text || !isAdmin.value) return;
  const now = new Date();
  const time = `${String(now.getMonth() + 1).padStart(2, "0")}.${String(
    now.getDate()
  ).padStart(2, "0")} ${String(now.getHours()).padStart(2, "0")}:${String(
    now.getMinutes()
  ).padStart(2, "0")}`;
  answersStore.value[itemId] = { text, time };
  persist();
  cancelAnswerEdit();
}

const items = [
  {
    id: 1,
    title: "WebSocket 연결이 자꾸 끊기는 문제",
    body:
      "WebSocket 연결이 일정 시간이 지나면 자동으로 끊깁니다. 서버 설정 문제인지, 클라이언트 설정 문제인지 알고 싶습니다.",
    author: "user06",
    status: "답변완료",
    cls: "done",
    isNew: false,
  },
  {
    id: 2,
    title: "카메라 RTSP 주소 형식이 어떻게 되나요?",
    body:
      "NVR에 연결된 카메라의 RTSP 스트림 주소를 TrafficAS에 등록하려고 하는데, 정확한 주소 형식이 궁금합니다.",
    author: "user07",
    status: "답변완료",
    cls: "done",
    isNew: false,
  },
  {
    id: 3,
    title: "번호판 인식률이 70%대에 머물러요",
    body:
      "야간에 번호판 인식률이 70~75% 수준입니다. 카메라 해상도는 1080p이고 조명 조건은 가로등 수준입니다. 개선 방법이 있을까요?",
    author: "user08",
    status: "답변중",
    cls: "ing",
    isNew: true,
  },
  {
    id: 4,
    title: "Docker 환경에서 GPU 설정 방법",
    body:
      "Docker Compose로 배포 시 NVIDIA GPU를 YOLOv8에서 사용하려면 어떤 설정이 필요한지 알려주세요.",
    author: "user09",
    status: "대기중",
    cls: "wait",
    isNew: true,
  },
  {
    id: 5,
    title: "Spring Boot 토큰 만료 시간 설정",
    body:
      "JWT 토큰 만료 시간을 변경하고 싶습니다. application.yml에서 수정하면 되는지, 다른 곳도 변경해야 하는지 알고 싶습니다.",
    author: "user10",
    status: "답변완료",
    cls: "done",
    isNew: false,
  },
];

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return items;
  return items.filter(
    (i) => i.title.toLowerCase().includes(q) || i.author.toLowerCase().includes(q)
  );
});

const highlight = (text) => {
  const q = query.value.trim();
  if (!q) return text;
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  return text.replace(re, "<mark>$1</mark>");
};
</script>

<style scoped>
.top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.info {
  font-size: 13px;
  color: var(--t2);
  font-weight: 300;
}
.wbtn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--a);
  color: var(--bg);
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}
.wbtn:hover {
  opacity: 0.87;
}

/* ── 검색바 ── */
.search-bar {
  display: flex;
  align-items: center;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 6px;
  margin-bottom: 10px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-bar:focus-within {
  border-color: var(--a);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}
.s-ico {
  padding: 0 10px;
  display: flex;
  align-items: center;
  color: var(--t3);
  flex-shrink: 0;
}
.s-input {
  flex: 1;
  padding: 9px 0;
  background: none;
  border: none;
  font-size: 12px;
  color: var(--t);
  outline: none;
  font-family: "Noto Sans KR", sans-serif;
}
.s-input::placeholder {
  color: var(--t3);
}
.s-clear {
  padding: 0 10px;
  display: flex;
  align-items: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--t3);
  transition: color 0.2s;
  flex-shrink: 0;
}
.s-clear:hover {
  color: var(--t);
}
.s-count {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--a);
  padding: 0 10px 0 0;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ── 테이블 ── */
.tbl {
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 7px;
  overflow: hidden;
}
.th {
  padding: 10px 16px;
  border-bottom: 1px solid var(--b);
  background: rgba(255, 255, 255, 0.025);
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--t3);
}
.tr {
  padding: 11px 16px;
  border-bottom: 1px solid var(--b);
  font-size: 12px;
  align-items: center;
  transition: background 0.15s;
  cursor: pointer;
}
.tr:hover {
  background: rgba(255, 255, 255, 0.03);
}
.tr.active {
  background: rgba(96, 165, 250, 0.05);
  border-bottom-color: transparent;
}
.grid3 {
  display: grid;
  grid-template-columns: 1fr 80px 80px;
  gap: 8px;
  align-items: center;
}
.ttl {
  display: flex;
  align-items: center;
  gap: 5px;
  overflow: hidden;
}
.ttl-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--t);
}
.chv {
  flex-shrink: 0;
  color: var(--t3);
  transition: transform 0.2s;
}
.chv.open {
  transform: rotate(90deg);
  color: var(--a);
}
.sub {
  font-size: 11px;
  color: var(--t3);
}
.nb {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--a);
  padding: 1px 5px;
  border-radius: 100px;
  flex-shrink: 0;
}
.sts {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 3px;
}
.done {
  background: rgba(52, 211, 153, 0.1);
  color: #34d399;
}
.ing {
  background: rgba(251, 146, 60, 0.1);
  color: #fb923c;
}
.wait {
  background: rgba(255, 255, 255, 0.05);
  color: var(--t3);
}

/* ── 답변 패널 ── */
.apanel {
  border-bottom: 1px solid var(--b);
  background: rgba(0, 0, 0, 0.12);
}

/* 질문 본문 */
.qbody {
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.qbody-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  margin-bottom: 8px;
  letter-spacing: 0.08em;
}
.qbody-text {
  font-size: 12px;
  color: var(--t2);
  line-height: 1.7;
  margin: 0 0 6px 0;
  white-space: pre-wrap;
}
.qmeta {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--t3);
}

/* 답변 박스 */
.answer-box {
  padding: 14px 16px;
  border-left: 3px solid var(--a);
  margin: 12px 16px;
  background: rgba(96, 165, 250, 0.04);
  border-radius: 0 6px 6px 0;
}
.answer-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--a);
  margin-bottom: 8px;
  letter-spacing: 0.08em;
}
.answer-head.write {
  color: var(--t3);
}
.answer-time {
  font-size: 9px;
  color: var(--t3);
  margin-left: 4px;
  flex: 1;
}
.answer-text {
  font-size: 12px;
  color: var(--t2);
  line-height: 1.7;
  white-space: pre-wrap;
}

/* 답변 작성 폼 */
.answer-form-wrap {
  padding: 14px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.answer-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cta {
  width: 100%;
  box-sizing: border-box;
  background: var(--bg);
  border: 1px solid var(--b);
  border-radius: 5px;
  padding: 8px 10px;
  font-size: 12px;
  color: var(--t);
  font-family: "Noto Sans KR", sans-serif;
  outline: none;
  resize: vertical;
  line-height: 1.6;
  transition: border-color 0.2s;
}
.cta:focus {
  border-color: var(--ba);
}
.cta::placeholder {
  color: var(--t3);
}

.cbtns {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}
.cact {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  padding: 2px 8px;
  border-radius: 3px;
  border: 1px solid var(--b);
  background: none;
  color: var(--t3);
  cursor: pointer;
  transition: all 0.15s;
}
.cact:hover {
  border-color: var(--ba);
  color: var(--a);
}
.cbtn-save {
  padding: 5px 14px;
  background: var(--a);
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 11px;
  font-family: "IBM Plex Mono", monospace;
  cursor: pointer;
  transition: opacity 0.2s;
}
.cbtn-save:hover:not(:disabled) {
  opacity: 0.85;
}
.cbtn-save:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.cbtn-cancel {
  padding: 5px 12px;
  background: none;
  border: 1px solid var(--b);
  border-radius: 4px;
  font-size: 11px;
  font-family: "IBM Plex Mono", monospace;
  color: var(--t3);
  cursor: pointer;
  transition: all 0.15s;
}
.cbtn-cancel:hover {
  border-color: var(--ba);
  color: var(--t);
}

/* 답변 대기 */
.waiting {
  padding: 18px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--t3);
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
}

/* 관리자 배지 */
.admin-badge {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(96, 165, 250, 0.06);
  border: 1px solid rgba(96, 165, 250, 0.2);
  border-radius: 5px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  color: var(--a);
}

/* 검색어 하이라이트 */
:deep(mark) {
  background: rgba(96, 165, 250, 0.22);
  color: var(--a);
  border-radius: 2px;
  padding: 0 1px;
}

.empty {
  padding: 28px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: var(--t3);
}
</style>
