<template>
  <div class="board">
    <div class="top-row">
      <p class="info">사용 후기, 활용 사례, 공지사항을 공유하세요.</p>
      <button class="wbtn">글쓰기</button>
    </div>

    <div class="search-bar">
      <span class="s-ico">
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      </span>
      <input v-model="query" type="text" placeholder="제목 또는 작성자 검색..." class="s-input" />
      <button v-if="query" class="s-clear" @click="query = ''">
        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
      <span class="s-count" v-if="query">{{ filtered.length }}건</span>
    </div>

    <div class="tbl">
      <div class="th grid4"><span>제목</span><span>작성자</span><span>날짜</span><span>조회</span></div>
      <template v-if="filtered.length">
        <template v-for="p in filtered" :key="p.id">
          <div class="tr grid4" @click="toggle(p.id)" :class="{ active: expandedId === p.id }">
            <span class="ttl">
              <svg class="chv" :class="{ open: expandedId === p.id }" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              <span class="ttl-text">
                <template v-if="query"><span v-html="highlight(p.title)"></span></template>
                <template v-else>{{ p.title }}</template>
              </span>
              <span class="nb" v-if="p.isNew">NEW</span>
              <span class="cc" v-if="getComments(p.id).length">💬 {{ getComments(p.id).length }}</span>
            </span>
            <span class="sub">{{ p.author }}</span>
            <span class="sub mono">{{ p.date }}</span>
            <span class="sub mono">{{ p.views }}</span>
          </div>

          <!-- 댓글 패널 -->
          <div class="cpanel" v-if="expandedId === p.id" @click.stop>
            <div class="cphead">
              <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              댓글 <strong>{{ getComments(p.id).length }}</strong>
            </div>

            <div class="clist">
              <template v-if="getComments(p.id).length">
                <div class="citem" v-for="c in getComments(p.id)" :key="c.id">
                  <div class="chead-row">
                    <span class="caut">{{ c.author }}</span>
                    <span class="ctm">{{ c.time }}{{ c.edited ? ' (수정됨)' : '' }}</span>
                    <div class="cacts" v-if="canEdit(c)">
                      <button class="cact" @click="startEdit(c)">수정</button>
                      <button class="cact del" @click="removeComment(p.id, c.id)">삭제</button>
                    </div>
                  </div>
                  <div class="ctxt" v-if="editingId !== c.id">{{ c.text }}</div>
                  <div class="cedit" v-else>
                    <textarea class="cta" v-model="editText" rows="2" @keydown.esc="cancelEdit" />
                    <div class="cbtns">
                      <button class="cbtn-save" @click="saveEdit(p.id, c.id)" :disabled="!editText.trim()">저장</button>
                      <button class="cbtn-cancel" @click="cancelEdit">취소</button>
                    </div>
                  </div>
                </div>
              </template>
              <div class="cempty" v-else>아직 댓글이 없습니다. 첫 댓글을 남겨보세요.</div>
            </div>

            <div class="cwrite" v-if="isLoggedIn">
              <div class="cav">{{ currentUser.name[0] }}</div>
              <div class="cright">
                <textarea class="cta" v-model="newComment" placeholder="댓글을 입력하세요... (Ctrl+Enter 등록)" rows="2"
                  @keydown.ctrl.enter.prevent="addComment(p.id)" />
                <div class="cbtns">
                  <span class="chint">Ctrl+Enter</span>
                  <button class="cbtn-save" @click="addComment(p.id)" :disabled="!newComment.trim()">등록</button>
                </div>
              </div>
            </div>
            <div class="clogin" v-else>
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              댓글을 작성하려면 <button class="clink" @click="openLogin">로그인</button>이 필요합니다.
            </div>
          </div>
        </template>
      </template>
      <div v-else class="empty">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <span>검색 결과가 없습니다.</span>
      </div>
    </div>

    <div class="pagi" v-if="!query">
      <button class="pg on">1</button>
      <button class="pg" v-for="n in 4" :key="n">{{ n + 1 }}</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAuth } from "../composables/useAuth";

const { isLoggedIn, currentUser, openLogin } = useAuth();

const query = ref("");
const expandedId = ref(null);
const newComment = ref("");
const editingId = ref(null);
const editText = ref("");

const commentsStore = ref(JSON.parse(localStorage.getItem("tas_board_comments") || "{}"));

function persist() {
  localStorage.setItem("tas_board_comments", JSON.stringify(commentsStore.value));
}

function getComments(postId) {
  return commentsStore.value[postId] || [];
}

function toggle(postId) {
  if (expandedId.value === postId) {
    expandedId.value = null;
  } else {
    expandedId.value = postId;
    newComment.value = "";
    cancelEdit();
  }
}

function canEdit(c) {
  return isLoggedIn.value && currentUser.value?.email === c.authorEmail;
}

function addComment(postId) {
  const text = newComment.value.trim();
  if (!text || !isLoggedIn.value) return;
  if (!commentsStore.value[postId]) commentsStore.value[postId] = [];
  commentsStore.value[postId].push({
    id: Date.now(),
    author: currentUser.value.name,
    authorEmail: currentUser.value.email,
    text,
    time: now(),
    edited: false,
  });
  persist();
  newComment.value = "";
}

function startEdit(c) {
  editingId.value = c.id;
  editText.value = c.text;
}

function cancelEdit() {
  editingId.value = null;
  editText.value = "";
}

function saveEdit(postId, commentId) {
  const text = editText.value.trim();
  if (!text) return;
  const c = (commentsStore.value[postId] || []).find((x) => x.id === commentId);
  if (c) { c.text = text; c.edited = true; }
  persist();
  cancelEdit();
}

function removeComment(postId, commentId) {
  const list = commentsStore.value[postId];
  if (!list) return;
  commentsStore.value[postId] = list.filter((c) => c.id !== commentId);
  persist();
}

function now() {
  const d = new Date();
  return `${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

const posts = [
  { id: 1, title: "[공지] 시스템 v1.2 업데이트 안내",       author: "관리자", date: "04.29", views: 128, isNew: true  },
  { id: 2, title: "야간 번호판 인식률 개선 후기",             author: "user01", date: "04.28", views: 87,  isNew: true  },
  { id: 3, title: "다중 카메라 동시 운영 팁",                author: "user02", date: "04.27", views: 64,  isNew: false },
  { id: 4, title: "Docker Compose 설정 파일 공유",           author: "user03", date: "04.26", views: 52,  isNew: false },
  { id: 5, title: "Spring Boot + FastAPI 연동 주의사항",     author: "user04", date: "04.25", views: 41,  isNew: false },
  { id: 6, title: "PostgreSQL 인덱스 최적화 경험담",         author: "user05", date: "04.24", views: 38,  isNew: false },
];

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return posts;
  return posts.filter((p) => p.title.toLowerCase().includes(q) || p.author.toLowerCase().includes(q));
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
.info { font-size: 13px; color: var(--t2); font-weight: 300; }
.wbtn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: var(--a); color: var(--bg);
  font-family: "IBM Plex Mono", monospace; font-size: 11px;
  font-weight: 700; letter-spacing: 0.08em; border-radius: 4px;
  cursor: pointer; border: none;
}
.wbtn:hover { opacity: 0.87; }

/* ── 검색바 ── */
.search-bar {
  display: flex; align-items: center;
  background: var(--bg2); border: 1px solid var(--b);
  border-radius: 6px; margin-bottom: 10px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-bar:focus-within {
  border-color: var(--a);
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}
.s-ico { padding: 0 10px; display: flex; align-items: center; color: var(--t3); flex-shrink: 0; }
.s-input {
  flex: 1; padding: 9px 0; background: none; border: none;
  font-size: 12px; color: var(--t); outline: none;
  font-family: "Noto Sans KR", sans-serif;
}
.s-input::placeholder { color: var(--t3); }
.s-clear {
  padding: 0 10px; display: flex; align-items: center;
  background: none; border: none; cursor: pointer;
  color: var(--t3); transition: color 0.2s; flex-shrink: 0;
}
.s-clear:hover { color: var(--t); }
.s-count {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  color: var(--a); padding: 0 10px 0 0; white-space: nowrap; flex-shrink: 0;
}

/* ── 테이블 ── */
.tbl {
  background: var(--bg2); border: 1px solid var(--b);
  border-radius: 7px; overflow: hidden; margin-bottom: 14px;
}
.th {
  padding: 10px 16px; border-bottom: 1px solid var(--b);
  background: rgba(255, 255, 255, 0.025);
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px; letter-spacing: 0.1em; color: var(--t3);
}
.tr {
  padding: 11px 16px; border-bottom: 1px solid var(--b);
  font-size: 12px; align-items: center;
  transition: background 0.15s; cursor: pointer;
}
.tr:hover { background: rgba(255, 255, 255, 0.03); }
.tr.active { background: rgba(96, 165, 250, 0.05); border-bottom-color: transparent; }
.grid4 { display: grid; grid-template-columns: 1fr 80px 70px 50px; gap: 8px; align-items: center; }
.ttl {
  display: flex; align-items: center; gap: 5px;
  overflow: hidden;
}
.ttl-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--t); }
.chv { flex-shrink: 0; color: var(--t3); transition: transform 0.2s; }
.chv.open { transform: rotate(90deg); color: var(--a); }
.sub { font-size: 11px; color: var(--t3); }
.mono { font-family: "IBM Plex Mono", monospace; font-size: 10px; }
.nb {
  font-family: "IBM Plex Mono", monospace; font-size: 8px;
  background: rgba(255, 255, 255, 0.1); color: var(--a);
  padding: 1px 5px; border-radius: 100px; flex-shrink: 0;
}
.cc {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  color: var(--t3); flex-shrink: 0;
}

/* ── 댓글 패널 ── */
.cpanel {
  border-bottom: 1px solid var(--b);
  background: rgba(0, 0, 0, 0.12);
  padding: 0;
}
.cphead {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 16px;
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  color: var(--t3); border-bottom: 1px solid var(--b);
}
.cphead strong { color: var(--a); }

.clist { padding: 0; }
.citem {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.citem:last-child { border-bottom: none; }
.chead-row {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 5px;
}
.caut {
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  color: var(--a); font-weight: 500;
}
.ctm {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  color: var(--t3); flex: 1;
}
.cacts { display: flex; gap: 4px; }
.cact {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  padding: 2px 8px; border-radius: 3px;
  border: 1px solid var(--b); background: none;
  color: var(--t3); cursor: pointer; transition: all 0.15s;
}
.cact:hover { border-color: var(--ba); color: var(--a); }
.cact.del:hover { border-color: rgba(248, 113, 113, 0.4); color: #f87171; }
.ctxt { font-size: 12px; color: var(--t2); line-height: 1.6; white-space: pre-wrap; }

.cempty {
  padding: 20px 16px; font-size: 11px; color: var(--t3); text-align: center;
}

/* 수정 폼 */
.cedit { display: flex; flex-direction: column; gap: 6px; }

/* 댓글 작성 */
.cwrite {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 12px 16px;
  border-top: 1px solid var(--b);
  background: rgba(255, 255, 255, 0.02);
}
.cav {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--a); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
  margin-top: 2px;
}
.cright { flex: 1; display: flex; flex-direction: column; gap: 6px; }

.cta {
  width: 100%; box-sizing: border-box;
  background: var(--bg); border: 1px solid var(--b);
  border-radius: 5px; padding: 8px 10px;
  font-size: 12px; color: var(--t);
  font-family: "Noto Sans KR", sans-serif;
  outline: none; resize: none; line-height: 1.6;
  transition: border-color 0.2s;
}
.cta:focus { border-color: var(--ba); }
.cta::placeholder { color: var(--t3); }

.cbtns { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.chint {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  color: var(--t3); margin-right: auto;
}
.cbtn-save {
  padding: 5px 14px; background: var(--a); color: #fff;
  border: none; border-radius: 4px; font-size: 11px;
  font-family: "IBM Plex Mono", monospace;
  cursor: pointer; transition: opacity 0.2s;
}
.cbtn-save:hover:not(:disabled) { opacity: 0.85; }
.cbtn-save:disabled { opacity: 0.4; cursor: not-allowed; }
.cbtn-cancel {
  padding: 5px 12px; background: none;
  border: 1px solid var(--b); border-radius: 4px; font-size: 11px;
  font-family: "IBM Plex Mono", monospace;
  color: var(--t3); cursor: pointer; transition: all 0.15s;
}
.cbtn-cancel:hover { border-color: var(--ba); color: var(--t); }

.clogin {
  padding: 14px 16px;
  border-top: 1px solid var(--b);
  font-size: 12px; color: var(--t3);
  display: flex; align-items: center; gap: 5px;
}
.clink {
  background: none; border: none; color: var(--a);
  font-size: 12px; cursor: pointer; text-decoration: underline;
  font-family: "Noto Sans KR", sans-serif; padding: 0;
}

/* 검색어 하이라이트 */
:deep(mark) {
  background: rgba(96, 165, 250, 0.22); color: var(--a);
  border-radius: 2px; padding: 0 1px;
}

.empty {
  padding: 28px 16px; display: flex; align-items: center;
  justify-content: center; gap: 8px; font-size: 12px; color: var(--t3);
}

/* ── 페이지네이션 ── */
.pagi { display: flex; gap: 5px; justify-content: center; }
.pg {
  width: 30px; height: 30px; border-radius: 4px;
  border: 1px solid var(--b); background: transparent;
  color: var(--t3); font-family: "IBM Plex Mono", monospace;
  font-size: 11px; cursor: pointer; transition: all 0.2s;
}
.pg:hover, .pg.on {
  border-color: var(--ba); color: var(--a);
  background: rgba(255, 255, 255, 0.04);
}
</style>
