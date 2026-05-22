<template>
  <div class="board">
    <div v-if="detailPost" class="detail-view">
      <div class="dv-top">
        <button class="dv-back" @click="closeDetail">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          목록으로
        </button>
        <div class="dv-top-actions" v-if="canEditPost(detailPost)">
          <button class="pact del" @click="removePost(detailPost.id)">삭제</button>
        </div>
      </div>

      <h2 class="dv-title">
        {{ detailPost.title }}
        <span class="nb" v-if="detailPost.isNew">NEW</span>
      </h2>
      <div class="dv-meta">
        <span class="pb-author">{{ detailPost.author }}</span>
        <span class="pb-sep">·</span>
        <span class="pb-date">{{ detailPost.date }}</span>
        <span class="pb-sep">·</span>
        <span class="pb-views">조회 {{ detailPost.views }}</span>
        <span class="pb-sep">·</span>
        <span class="pb-views">댓글 {{ getComments(detailPost.id).length }}</span>
      </div>
      <div class="dv-body">{{ detailPost.body || '본문 내용이 없습니다.' }}</div>

      <div class="dv-comments">
        <div class="cphead">
          <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          댓글 <strong>{{ getComments(detailPost.id).length }}</strong>
        </div>

        <div class="clist">
          <template v-if="getComments(detailPost.id).length">
            <div class="citem" v-for="c in getComments(detailPost.id)" :key="c.id">
              <div class="chead-row">
                <span class="caut">{{ c.author }}</span>
                <span class="ctm">{{ c.time }}{{ c.edited ? ' (수정됨)' : '' }}</span>
                <div class="cacts" v-if="canEdit(c)">
                  <button class="cact" @click="startEdit(c)">수정</button>
                  <button class="cact del" @click="removeComment(detailPost.id, c.id)">삭제</button>
                </div>
              </div>
              <div class="ctxt" v-if="editingId !== c.id">{{ c.text }}</div>
              <div class="cedit" v-else>
                <textarea class="cta" v-model="editText" rows="2" @keydown.esc="cancelEdit" />
                <div class="cbtns">
                  <button class="cbtn-save" @click="saveEdit(detailPost.id, c.id)" :disabled="!editText.trim()">저장</button>
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
              @keydown.ctrl.enter.prevent="addComment(detailPost.id)" />
            <div class="cbtns">
              <span class="chint">Ctrl+Enter</span>
              <button class="cbtn-save" @click="addComment(detailPost.id)" :disabled="!newComment.trim()">등록</button>
            </div>
          </div>
        </div>
        <div class="clogin" v-else>
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          댓글을 작성하려면 <button class="clink" @click="openLogin">로그인</button>이 필요합니다.
        </div>
      </div>
    </div>

    <template v-else>
    <div class="top-row">
      <p class="info">사용 후기, 활용 사례, 공지사항을 공유하세요.</p>
      <button v-if="isAdmin" class="wbtn" @click="onWrite" title="새 글 작성">
        <i class="bi bi-pencil-square"></i> 글쓰기
      </button>
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
        <div class="tr grid4" v-for="p in filtered" :key="p.id" @click="openDetail(p)">
          <span class="ttl">
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
    </template>

    <div v-if="showWrite" class="wmodal" @click.self="closeWrite">
      <div class="wbox">
        <div class="wb-head">
          <span>새 글 작성</span>
          <button class="wb-close" @click="closeWrite">×</button>
        </div>
        <input v-model="wTitle" class="wb-title" type="text" placeholder="제목을 입력하세요" maxlength="100" />
        <textarea v-model="wBody" class="wb-body" placeholder="내용을 입력하세요" rows="10"></textarea>
        <div class="wb-foot">
          <button class="cbtn-cancel" @click="closeWrite">취소</button>
          <button class="cbtn-save" :disabled="!wTitle.trim() || !wBody.trim()" @click="submitPost">등록</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useAuth } from "../composables/useAuth";

const { isLoggedIn, isAdmin, currentUser, openLogin } = useAuth();

const showWrite = ref(false);
const wTitle = ref("");
const wBody = ref("");

function onWrite() {
  if (!isAdmin.value) return;
  showWrite.value = true;
}
function closeWrite() {
  showWrite.value = false;
  wTitle.value = "";
  wBody.value = "";
}

const query = ref("");
const detailPost = ref(null);
const newComment = ref("");
const editingId = ref(null);
const editText = ref("");

function openDetail(p) {
  // 시드 글은 조회수 증가 안 함, 사용자 글만 (단순 데모)
  detailPost.value = p;
  newComment.value = "";
  cancelEdit();
}
function closeDetail() {
  detailPost.value = null;
  newComment.value = "";
  cancelEdit();
}

const commentsStore = ref(JSON.parse(localStorage.getItem("tas_board_comments") || "{}"));

function persist() {
  localStorage.setItem("tas_board_comments", JSON.stringify(commentsStore.value));
}

function getComments(postId) {
  return commentsStore.value[postId] || [];
}

function canEdit(c) {
  if (!isLoggedIn.value) return false;
  if (isAdmin.value) return true;                    // 관리자: 모든 댓글 수정/삭제
  return currentUser.value?.email === c.authorEmail; // 일반 회원: 본인 댓글만
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

const seedPosts = [
  { id: 1, title: "[공지] 시스템 v1.2 업데이트 안내", author: "관리자", date: "04.29", views: 128, isNew: true,
    body: "TAS v1.2 업데이트가 4/29 새벽 2시에 진행됩니다.\n\n주요 변경 사항\n- 야간 번호판 인식률 개선 (저조도 보정 알고리즘 적용)\n- 카메라 동시 운영 안정성 강화\n- 검색 필터 7종 추가\n\n점검 예상 시간 약 1시간. 양해 부탁드립니다." },
  { id: 2, title: "야간 번호판 인식률 개선 후기", author: "user01", date: "04.28", views: 87, isNew: true,
    body: "야간 모드 적용 후 인식률이 약 18% 향상되었습니다. 카메라별 노출 보정 + OCR 후처리 단계의 임계값 튜닝이 핵심이었어요." },
  { id: 3, title: "다중 카메라 동시 운영 팁", author: "user02", date: "04.27", views: 64, isNew: false,
    body: "동시에 6대 이상 운영할 땐 GPU 메모리가 빠르게 소진됩니다. 배치 단위 추론과 frame skip 옵션을 활용하면 부하가 크게 줄어요." },
  { id: 4, title: "Docker Compose 설정 파일 공유", author: "user03", date: "04.26", views: 52, isNew: false,
    body: "PostgreSQL + Redis + FastAPI + Nginx 통합 compose 파일 공유합니다. 환경 변수 파일 별도 분리 권장." },
  { id: 5, title: "Spring Boot + Vue.js 연동 주의사항", author: "user04", date: "04.25", views: 41, isNew: false,
    body: "CORS 설정, JWT refresh 토큰 갱신 시 race condition 주의. axios interceptor에서 401 핸들링을 잘 잡아야 합니다." },
  { id: 6, title: "PostgreSQL 인덱스 최적화 경험담", author: "user05", date: "04.24", views: 38, isNew: false,
    body: "차량 로그 테이블이 5천만 건 넘어가니까 쿼리가 느려져서, 시간 + 카메라 ID 복합 인덱스 추가로 평균 응답 200ms → 12ms로 개선됐습니다." },
];

const customPosts = ref(JSON.parse(localStorage.getItem("tas_board_posts") || "[]"));
function persistPosts() {
  localStorage.setItem("tas_board_posts", JSON.stringify(customPosts.value));
}

const posts = computed(() => [...customPosts.value, ...seedPosts]);

function submitPost() {
  if (!isAdmin.value) return;
  const title = wTitle.value.trim();
  const body = wBody.value.trim();
  if (!title || !body) return;
  const d = new Date();
  const date = `${String(d.getMonth() + 1).padStart(2, "0")}.${String(d.getDate()).padStart(2, "0")}`;
  customPosts.value.unshift({
    id: Date.now(),
    title,
    body,
    author: currentUser.value?.name || "관리자",
    date,
    views: 0,
    isNew: true,
  });
  persistPosts();
  closeWrite();
}

function canEditPost(p) {
  if (!isAdmin.value) return false;
  return customPosts.value.some((cp) => cp.id === p.id);
}

function removePost(postId) {
  if (!isAdmin.value) return;
  if (!confirm("이 글을 삭제하시겠습니까?")) return;
  customPosts.value = customPosts.value.filter((p) => p.id !== postId);
  persistPosts();
  if (detailPost.value && detailPost.value.id === postId) detailPost.value = null;
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return posts.value;
  return posts.value.filter((p) => p.title.toLowerCase().includes(q) || p.author.toLowerCase().includes(q));
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
.info { font-size: 16px; color: var(--t); opacity: 0.72; font-weight: 500; }
.wbtn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 11px 22px; background: var(--a); color: var(--bg);
  font-family: "JetBrains Mono", monospace; font-size: 14px;
  font-weight: 700; letter-spacing: 0.08em; border-radius: 4px;
  cursor: pointer; border: none;
}
.wbtn:hover:not(:disabled) { opacity: 0.87; }
.wbtn:disabled { opacity: 0.45; cursor: not-allowed; }
.wbtn i { margin-right: 4px; }

/* search */
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
  flex: 1; padding: 12px 0; background: none; border: none;
  font-size: 15px; color: var(--t); outline: none;
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
  font-family: "JetBrains Mono", monospace; font-size: 12.5px;
  color: var(--a); padding: 0 10px 0 0; white-space: nowrap; flex-shrink: 0;
}

/* table */
.tbl {
  background: var(--bg2); border: 1px solid var(--b);
  border-radius: 7px; overflow: hidden; margin-bottom: 14px;
}
.th {
  padding: 14px 20px; border-bottom: 1px solid var(--b);
  background: rgba(255, 255, 255, 0.025);
  font-family: "JetBrains Mono", monospace;
  font-size: 12.5px; letter-spacing: 0.1em; color: var(--t2);
}
.tr {
  padding: 15px 20px; border-bottom: 1px solid var(--b);
  font-size: 15.5px; align-items: center;
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
.sub { font-size: 14px; color: var(--t2); }
.mono { font-family: "JetBrains Mono", monospace; font-size: 13.5px; }
.nb {
  font-family: "JetBrains Mono", monospace; font-size: 11.5px;
  background: rgba(255, 255, 255, 0.1); color: var(--a);
  padding: 3px 8px; border-radius: 100px; flex-shrink: 0;
}
.cc {
  font-family: "JetBrains Mono", monospace; font-size: 12.5px;
  color: var(--t3); flex-shrink: 0;
}

/* comments */
.cphead {
  display: flex; align-items: center; gap: 6px;
  padding: 14px 20px;
  font-family: "JetBrains Mono", monospace; font-size: 13.5px;
  color: var(--t2); border-bottom: 1px solid var(--b);
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
  font-family: "JetBrains Mono", monospace; font-size: 13.5px;
  color: var(--a); font-weight: 600;
}
.ctm {
  font-family: "JetBrains Mono", monospace; font-size: 12.5px;
  color: var(--t3); flex: 1;
}
.cacts { display: flex; gap: 4px; }
.cact {
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  padding: 3px 9px; border-radius: 3px;
  border: 1px solid var(--b); background: none;
  color: var(--t3); cursor: pointer; transition: all 0.15s;
}
.cact:hover { border-color: var(--ba); color: var(--a); }
.cact.del:hover { border-color: rgba(248, 113, 113, 0.4); color: #f87171; }
.ctxt { font-size: 15px; color: var(--t); opacity: 0.85; line-height: 1.7; white-space: pre-wrap; }

.cempty {
  padding: 22px 18px; font-size: 13px; color: var(--t3); text-align: center;
}

/* edit form */
.cedit { display: flex; flex-direction: column; gap: 6px; }

/* compose */
.cwrite {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 12px 16px;
  border-top: 1px solid var(--b);
  background: rgba(255, 255, 255, 0.02);
}
.cav {
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--a); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 13.5px; font-weight: 700; flex-shrink: 0;
  margin-top: 2px;
}
.cright { flex: 1; display: flex; flex-direction: column; gap: 6px; }

.cta {
  width: 100%; box-sizing: border-box;
  background: var(--bg); border: 1px solid var(--b);
  border-radius: 5px; padding: 10px 12px;
  font-size: 14px; color: var(--t);
  font-family: "Noto Sans KR", sans-serif;
  outline: none; resize: none; line-height: 1.6;
  transition: border-color 0.2s;
}
.cta:focus { border-color: var(--ba); }
.cta::placeholder { color: var(--t3); }

.cbtns { display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
.chint {
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  color: var(--t3); margin-right: auto;
}
.cbtn-save {
  padding: 6px 16px; background: var(--a); color: #fff;
  border: none; border-radius: 4px; font-size: 12.5px;
  font-family: "JetBrains Mono", monospace;
  cursor: pointer; transition: opacity 0.2s;
}
.cbtn-save:hover:not(:disabled) { opacity: 0.85; }
.cbtn-save:disabled { opacity: 0.4; cursor: not-allowed; }
.cbtn-cancel {
  padding: 6px 14px; background: none;
  border: 1px solid var(--b); border-radius: 4px; font-size: 12.5px;
  font-family: "JetBrains Mono", monospace;
  color: var(--t3); cursor: pointer; transition: all 0.15s;
}
.cbtn-cancel:hover { border-color: var(--ba); color: var(--t); }

.clogin {
  padding: 16px 18px;
  border-top: 1px solid var(--b);
  font-size: 14.5px; color: var(--t2);
  display: flex; align-items: center; gap: 5px;
}
.clink {
  background: none; border: none; color: var(--a);
  font-size: 14.5px; cursor: pointer; text-decoration: underline;
  font-family: "Noto Sans KR", sans-serif; padding: 0;
}

/* search highlight */
:deep(mark) {
  background: rgba(96, 165, 250, 0.22); color: var(--a);
  border-radius: 2px; padding: 0 1px;
}

.empty {
  padding: 32px 18px; display: flex; align-items: center;
  justify-content: center; gap: 8px; font-size: 14.5px; color: var(--t2);
}

/* pagination */
.pagi { display: flex; gap: 5px; justify-content: center; }
.pg {
  width: 36px; height: 36px; border-radius: 4px;
  border: 1px solid var(--b); background: transparent;
  color: var(--t2); font-family: "JetBrains Mono", monospace;
  font-size: 14px; cursor: pointer; transition: all 0.2s;
}
.pg:hover, .pg.on {
  border-color: var(--ba); color: var(--a);
  background: rgba(255, 255, 255, 0.04);
}

/* detail view */
.detail-view {
  display: flex; flex-direction: column;
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 7px;
  padding: 20px 24px 24px;
}
.dv-top {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--b);
  margin-bottom: 18px;
}
.dv-back {
  display: inline-flex; align-items: center; gap: 6px;
  background: none; border: 1px solid var(--b);
  border-radius: 5px; padding: 7px 14px;
  color: var(--t); font-size: 13.5px; cursor: pointer;
  transition: all 0.18s;
}
.dv-back:hover { border-color: var(--ba); color: var(--a); }
.dv-top-actions { display: flex; gap: 6px; }
.dv-title {
  font-size: 19px; font-weight: 700; color: var(--t);
  letter-spacing: -0.3px; margin: 0 0 10px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.dv-meta {
  display: flex; align-items: center; gap: 8px;
  font-family: "JetBrains Mono", monospace;
  font-size: 12.5px; color: var(--t2);
  padding-bottom: 18px; border-bottom: 1px dashed var(--b);
  margin-bottom: 18px;
}
.dv-body {
  font-size: 15px; color: var(--t);
  line-height: 1.85; white-space: pre-wrap;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--b);
}
.dv-comments { padding-top: 18px; }
.dv-comments .cphead { padding: 0 0 12px; }
.dv-comments .clist { padding: 0; }
.dv-comments .citem { padding: 12px 0; }
.dv-comments .cwrite,
.dv-comments .clogin { padding: 14px 0 0; border-top: 1px solid var(--b); margin-top: 4px; }

/* detail view meta + actions */
.pb-author { color: var(--a); font-weight: 600; }
.pb-sep { opacity: 0.4; }
.pact {
  font-size: 12px; padding: 3px 10px; border-radius: 3px;
  border: 1px solid var(--b); background: none;
  color: var(--t3); cursor: pointer;
}
.pact.del:hover { border-color: #f87171; color: #f87171; }

/* write modal */
.wmodal {
  position: fixed; inset: 0; z-index: 500;
  background: rgba(0, 0, 0, 0.5);
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.wbox {
  width: 100%; max-width: 640px;
  background: var(--card); border: 1px solid var(--b);
  border-radius: 12px; padding: 24px;
  display: flex; flex-direction: column; gap: 12px;
}
.theme-navy.light .wbox { background: #fff; box-shadow: 0 24px 60px rgba(15, 40, 90, 0.2); }
.wb-head {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 16px; font-weight: 700; color: var(--t);
}
.wb-close {
  background: none; border: none; cursor: pointer;
  font-size: 24px; line-height: 1; color: var(--t3); padding: 0 4px;
}
.wb-close:hover { color: var(--t); }
.wb-title, .wb-body {
  background: var(--bg2); border: 1px solid var(--b);
  border-radius: 6px; padding: 11px 14px;
  font-family: "Noto Sans KR", sans-serif;
  font-size: 14.5px; color: var(--t); outline: none;
  transition: border-color 0.18s;
}
.wb-title:focus, .wb-body:focus { border-color: var(--a); }
.wb-body { resize: vertical; line-height: 1.6; min-height: 200px; }
.wb-foot {
  display: flex; justify-content: flex-end; gap: 8px;
  margin-top: 4px;
}
</style>
