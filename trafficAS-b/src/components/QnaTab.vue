<template>
  <div class="qna">
    <div class="top-row">
      <p class="info">궁금한 점을 질문하고 전문가 답변을 받으세요.</p>
      <button class="wbtn" @click="openQuestionForm">질문하기</button>
    </div>

    <div v-if="message" class="notice" :class="messageType">{{ message }}</div>

    <div class="question-form-wrap" v-if="showQuestionForm">
      <input
        v-model="questionTitle"
        class="q-input"
        type="text"
        placeholder="질문 제목을 입력하세요"
      />
      <textarea
        v-model="questionContent"
        class="cta"
        rows="4"
        placeholder="질문 내용을 입력하세요"
      />
      <div class="cbtns">
        <button class="cbtn-cancel" @click="closeQuestionForm">취소</button>
        <button
          class="cbtn-save"
          :disabled="savingQuestion || !questionTitle.trim() || !questionContent.trim()"
          @click="createQuestion"
        >
          질문 등록
        </button>
      </div>
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
              </div>
              <div class="answer-text">
                {{ getAnswer(q.id).text }}
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
                    :disabled="savingAnswer || !answerDraft.trim()"
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
        <span>{{ loading ? "Q&A 목록을 불러오는 중입니다." : "검색 결과가 없습니다." }}</span>
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
      관리자 모드 활성화 — 답변 작성 가능
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { apiClient, apiGet } from "@/api/client";
import { useAuth } from "../composables/useAuth";

const { isAdmin, isLoggedIn, openLogin } = useAuth();

const query = ref("");
const expandedId = ref(null);
const answerDraft = ref("");
const loading = ref(false);
const savingQuestion = ref(false);
const savingAnswer = ref(false);
const showQuestionForm = ref(false);
const questionTitle = ref("");
const questionContent = ref("");
const message = ref("");
const messageType = ref("info");
const items = ref([]);
const answersStore = ref({});

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
  window.setTimeout(() => {
    if (message.value === text) message.value = "";
  }, 3000);
}

function getAnswer(itemId) {
  return answersStore.value[itemId] || null;
}

function getStatus(item) {
  return answersStore.value[item.id] || item.rawStatus === "ANSWERED" ? "답변완료" : "대기중";
}

function getStatusCls(item) {
  return answersStore.value[item.id] || item.rawStatus === "ANSWERED" ? "done" : "wait";
}

async function toggle(itemId) {
  if (expandedId.value === itemId) {
    expandedId.value = null;
  } else {
    expandedId.value = itemId;
    cancelAnswerEdit();
    if (!getAnswer(itemId)) answerDraft.value = "";
    await loadQuestionDetail(itemId);
  }
}

function cancelAnswerEdit() {
  answerDraft.value = "";
}

function openQuestionForm() {
  if (!isLoggedIn.value) {
    openLogin();
    showMessage("로그인 후 질문을 등록할 수 있습니다.", "warn");
    return;
  }
  showQuestionForm.value = true;
}

function closeQuestionForm() {
  showQuestionForm.value = false;
  questionTitle.value = "";
  questionContent.value = "";
}

function normalizeQuestion(q) {
  return {
    id: q.questionId,
    title: q.title,
    body: q.content,
    author: q.authorName || "-",
    rawStatus: q.status,
    status: q.status === "ANSWERED" ? "답변완료" : "대기중",
    cls: q.status === "ANSWERED" ? "done" : "wait",
    isNew: false,
  };
}

function normalizeAnswer(answer) {
  if (!answer) return null;
  const createdAt = answer.createdAt ? new Date(answer.createdAt) : null;
  const time = createdAt && !Number.isNaN(createdAt.getTime())
    ? `${String(createdAt.getMonth() + 1).padStart(2, "0")}.${String(createdAt.getDate()).padStart(2, "0")} ${String(createdAt.getHours()).padStart(2, "0")}:${String(createdAt.getMinutes()).padStart(2, "0")}`
    : "";
  return {
    id: answer.answerId,
    text: answer.content,
    author: answer.authorName || "관리자",
    time,
  };
}

async function loadQuestions() {
  loading.value = true;
  try {
    const body = await apiGet("/api/qna/questions");
    items.value = Array.isArray(body.data) ? body.data.map(normalizeQuestion) : [];
  } catch (error) {
    console.warn("Failed to load QNA questions", error);
    showMessage("Q&A 목록을 불러오지 못했습니다.", "error");
  } finally {
    loading.value = false;
  }
}

async function loadQuestionDetail(itemId) {
  try {
    const body = await apiGet(`/api/qna/questions/${itemId}`);
    const answer = normalizeAnswer(body.data?.answer);
    if (answer) {
      answersStore.value = { ...answersStore.value, [itemId]: answer };
    }
  } catch (error) {
    console.warn("Failed to load QNA detail", error);
    showMessage("질문 상세 정보를 불러오지 못했습니다.", "error");
  }
}

async function createQuestion() {
  if (!questionTitle.value.trim() || !questionContent.value.trim()) return;
  savingQuestion.value = true;
  try {
    await apiClient.post("/api/qna/questions", {
      title: questionTitle.value.trim(),
      content: questionContent.value.trim(),
    });
    closeQuestionForm();
    await loadQuestions();
    showMessage("질문이 등록되었습니다.", "success");
  } catch (error) {
    console.warn("Failed to create QNA question", error);
    showMessage("질문 등록에 실패했습니다.", "error");
  } finally {
    savingQuestion.value = false;
  }
}

async function saveAnswer(itemId) {
  const text = answerDraft.value.trim();
  if (!text || !isAdmin.value) return;
  savingAnswer.value = true;
  try {
    await apiClient.post(`/api/qna/questions/${itemId}/answers`, { content: text });
    answerDraft.value = "";
    await loadQuestionDetail(itemId);
    await loadQuestions();
    showMessage("답변이 등록되었습니다.", "success");
  } catch (error) {
    console.warn("Failed to save QNA answer", error);
    showMessage("답변 등록에 실패했습니다.", "error");
  } finally {
    savingAnswer.value = false;
  }
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return items.value;
  return items.value.filter(
    (i) => i.title.toLowerCase().includes(q) || i.author.toLowerCase().includes(q)
  );
});

const highlight = (text) => {
  const q = query.value.trim();
  if (!q) return text;
  const re = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
  return text.replace(re, "<mark>$1</mark>");
};

onMounted(loadQuestions);
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
  font-family: "JetBrains Mono", monospace;
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

.notice {
  margin-bottom: 10px;
  padding: 9px 12px;
  border-radius: 5px;
  border: 1px solid var(--b);
  font-size: 12px;
  color: var(--t2);
  background: var(--bg2);
}
.notice.success {
  color: #34d399;
  border-color: rgba(52, 211, 153, 0.25);
  background: rgba(52, 211, 153, 0.06);
}
.notice.warn {
  color: #fb923c;
  border-color: rgba(251, 146, 60, 0.25);
  background: rgba(251, 146, 60, 0.06);
}
.notice.error {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.25);
  background: rgba(248, 113, 113, 0.06);
}

.question-form-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
  padding: 12px;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 7px;
}
.q-input {
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
}
.q-input:focus {
  border-color: var(--ba);
}
.q-input::placeholder {
  color: var(--t3);
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
  font-size: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--a);
  padding: 1px 5px;
  border-radius: 100px;
  flex-shrink: 0;
}
.sts {
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
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
