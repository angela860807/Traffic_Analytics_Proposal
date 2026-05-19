<template>
  <div class="rev-shell">
    <header class="top">
      <h1><a class="t-main" @click="goHome">단속관리팀</a></h1>
      <div class="t-right">
        <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>14:32:18</strong></span>
        <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
          <span class="km-dot"></span>
          <span class="km-lab">자동 새로고침</span>
          <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
        </button>
        <DeptSwitcher />
        <div class="t-user"><i class="bi bi-person-circle"></i> 단속관리팀 매니저 <i class="bi bi-chevron-down"></i></div>
      </div>
    </header>

    <section class="stats">
      <div class="st-card">
        <i class="bi bi-hourglass-split" style="color:#60a5fa"></i>
        <span class="st-lab">검토 대기</span>
        <span class="st-val">{{ waitCount }} <span class="st-u">건</span></span>
      </div>
      <div class="st-card">
        <i class="bi bi-check-circle-fill" style="color:#34d399"></i>
        <span class="st-lab">승인</span>
        <span class="st-val">{{ approveCount }} <span class="st-u">건</span></span>
      </div>
      <div class="st-card">
        <i class="bi bi-x-circle-fill" style="color:#f87171"></i>
        <span class="st-lab">반려</span>
        <span class="st-val">{{ rejectCount }} <span class="st-u">건</span></span>
      </div>
      <div class="st-card">
        <span class="ocr-cir">OCR</span>
        <span class="st-lab">OCR 평균 신뢰도</span>
        <span class="st-val">{{ avgConf }}<span class="st-u">%</span></span>
      </div>
    </section>

    <section class="grid">
      <div class="card list-card">
        <div class="lh">
          <h3>이벤트 목록</h3>
          <div class="lh-r">
            <select class="lh-sel" v-model="filterType">
              <option value="all">전체</option>
              <option value="속도 위반">속도 위반</option>
              <option value="OCR 인식">OCR 인식</option>
            </select>
            <div class="lh-search">
              <i class="bi bi-search"></i>
              <input v-model="query" placeholder="위치, 차량번호 검색" />
            </div>
          </div>
        </div>
        <table class="tbl-rev">
          <thead><tr><th>시간</th><th>위치</th><th>차량번호</th><th>상태</th></tr></thead>
          <tbody>
            <tr v-for="e in pagedEvents" :key="e.id"
              :class="{ sel: selected && selected.id === e.id }"
              @click="selectEvent(e)">
              <td class="mono">{{ e.time }}<div class="row-sub">2024-05-16</div></td>
              <td class="ttl">{{ e.place }}<div class="row-sub">{{ e.type === '속도 위반' ? '드론 구간' : '단속 임시' }}</div></td>
              <td class="mono">{{ e.plate }}</td>
              <td><span class="stat" :class="stTone(e.st)">{{ e.st }}</span></td>
            </tr>
            <tr v-if="!pagedEvents.length"><td colspan="4" class="empty">검색 결과가 없습니다.</td></tr>
          </tbody>
        </table>
        <div class="pager">
          <button @click="page > 1 && page--" :disabled="page === 1"><i class="bi bi-chevron-left"></i></button>
          <button v-for="(p, i) in pageNumbers" :key="i"
            class="pg" :class="{ on: page === p, dots: p === '...' }"
            :disabled="p === '...'"
            @click="typeof p === 'number' && (page = p)">{{ p }}</button>
          <button @click="page < pageTotal && page++" :disabled="page === pageTotal"><i class="bi bi-chevron-right"></i></button>
        </div>
      </div>

      <div class="card detail-card" v-if="selected">
        <div class="dh">
          <h3>선택 이벤트 상세 <span class="b-red" v-if="selected.type === '속도 위반'">속도 위반</span><span class="b-bl" v-else>OCR 인식</span></h3>
          <div class="evt-id">이벤트 ID  {{ selected.evtId }} <i class="bi bi-copy" @click="copyId"></i></div>
        </div>
        <div class="vimg">
          <div class="vi-lab">차량 이미지 (단속 사진)</div>
          <div class="vi-img"><div class="plate-on-car">{{ selected.plate }}</div></div>
          <button class="vi-zoom"><i class="bi bi-arrows-fullscreen"></i></button>
        </div>
        <div class="thumb-row">
          <div class="th-cnt">관련 이미지<br><span class="th-num">{{ thumbIdx + 1 }} / 3</span></div>
          <div class="th-imgs"><div v-for="i in 3" :key="i" class="th" :class="{ on: thumbIdx === i - 1 }" @click="thumbIdx = i - 1"></div></div>
          <button class="th-next" @click="thumbIdx < 2 && thumbIdx++"><i class="bi bi-chevron-right"></i></button>
        </div>
        <div class="ocr-section">
          <div class="ocr-h">차량 정보 (OCR)</div>
          <div class="ocr-grid">
            <div class="plate-img">{{ selected.plate }}</div>
            <div>
              <div class="ocr-lab">인식 결과</div>
              <div class="ocr-val">{{ selected.plate }}</div>
              <div class="ocr-conf">OCR 신뢰도 <strong class="bl">{{ selected.conf }}%</strong></div>
            </div>
          </div>
        </div>

        <div class="evt-info">
          <div class="ei-h">이벤트 정보</div>
          <div class="ei-grid">
            <div class="ei-row"><span>발생 시간</span><strong>2024-05-16 {{ selected.time }}</strong></div>
            <div class="ei-row"><span>위치</span><strong>{{ selected.place }}</strong></div>
            <div class="ei-row"><span>위반 내용</span><strong>{{ selected.type }}</strong></div>
            <div class="ei-row"><span>검지 구간</span><strong>드론 구간</strong></div>
            <div class="ei-row"><span>감지 속도</span><strong class="rd">{{ selected.detectSpeed }} km/h</strong></div>
            <div class="ei-row"><span>단속 임시</span><strong>2024-05-16 {{ selected.time }}</strong></div>
            <div class="ei-row"><span>제한 속도</span><strong>{{ selected.limitSpeed }} km/h</strong></div>
            <div class="ei-row"><span>장비/카메라</span><strong>KBR-123 ({{ selected.camera }})</strong></div>
            <div class="ei-row"><span>초과 속도</span><strong class="rd">+{{ selected.detectSpeed - selected.limitSpeed }} km/h</strong></div>
            <div class="ei-row"><span>OCR 신뢰도</span><strong class="bl">{{ selected.conf }}%</strong></div>
          </div>
        </div>

        <div class="mini-map">
          <svg viewBox="0 0 400 90" class="mm-svg">
            <rect width="400" height="90" fill="#1a2a45"/>
            <path d="M0,55 Q80,45 160,50 T320,40 T400,45" stroke="#3b82f6" stroke-width="3" fill="none"/>
            <path d="M0,60 Q140,68 280,62 T400,58" stroke="#1f3055" stroke-width="2" fill="none"/>
          </svg>
          <div class="mm-pin"><i class="bi bi-geo-alt-fill"></i><span>{{ selected.place }}</span></div>
        </div>
      </div>
      <div v-else class="card detail-card empty-card">
        <i class="bi bi-arrow-left"></i>
        <p>좌측 이벤트 목록에서 항목을 선택해 주세요.</p>
      </div>

      <div class="card verify-card" v-if="selected">
        <h3>이벤트 검토</h3>
        <p class="vq">검토 결과를 선택하고 필요한 경우 사유를 입력하세요.</p>
        <div class="auth-row">
          <span class="auth-lab">검토 권한</span>
          <span class="auth-tag bl">단속관리팀</span>
          <span class="auth-tag pl">최종 결정 가능</span>
        </div>

        <div class="judge">
          <div class="j-grid">
            <button class="jb gr" @click="judge('승인')"><i class="bi bi-check-circle"></i><span class="jt">승인</span><span class="js">위반으로 최종 확정</span></button>
            <button class="jb rd" @click="judge('반려')"><i class="bi bi-x-circle"></i><span class="jt">반려</span><span class="js">위반 아님</span></button>
            <button class="jb or" @click="judge('오탐')"><i class="bi bi-exclamation-triangle"></i><span class="jt">오탐 처리</span><span class="js">시스템 오탐으로 분류</span></button>
            <button class="jb bl" @click="openEvidence"><i class="bi bi-search"></i><span class="jt">증빙 조회</span><span class="js">관련 증빙 자료 확인</span></button>
          </div>
          <div class="memo">
            <div class="memo-lab">사유</div>
            <select class="reason-sel" v-model="reason">
              <option value="">사유 선택 (선택 사항)</option>
              <option>명확한 위반 — 영상·OCR 모두 일치</option>
              <option>차량번호 식별 불가</option>
              <option>긴급 차량 등 예외 상황</option>
              <option>장비 오류로 인한 오탐</option>
              <option>기타</option>
            </select>
            <textarea v-model="memo" placeholder="상세 사유를 입력하세요. (선택 사항)" maxlength="200"></textarea>
            <div class="memo-c">{{ memo.length }} / 200</div>
          </div>
        </div>

        <div class="hist">
          <h4>검토 히스토리</h4>
          <div class="hist-row"><i class="bi bi-person-circle"></i>
            <div><div class="hr-t">단속관리팀 <span class="auth-tag bl mini">{{ selected.st }}</span></div><div class="hr-s">2024-05-16 14:32:25</div></div>
          </div>
          <div class="hist-row"><i class="bi bi-cpu"></i>
            <div><div class="hr-t">시스템 <span class="hr-act">이벤트 생성</span></div><div class="hr-s">2024-05-16 {{ selected.time }}</div></div>
          </div>
        </div>
      </div>
    </section>

    <section class="card log-card">
      <div class="lh"><h3>감사 로그 (Audit Trail)</h3></div>
      <table class="tbl-audit">
        <thead><tr><th>순번</th><th>시간</th><th>사용자</th><th>역할</th><th>작업</th><th>결과</th><th>비고</th></tr></thead>
        <tbody>
          <tr v-for="(h, i) in auditLog" :key="i">
            <td class="mono">{{ auditLog.length - i }}</td>
            <td class="mono">{{ h.at }}</td>
            <td>{{ h.user }}</td>
            <td>{{ h.role }}</td>
            <td>{{ h.action }}</td>
            <td><span class="stat" :class="h.resultTone">{{ h.result }}</span></td>
            <td>{{ h.note }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";

const seed = [
  { time: "14:32:18", place: "강변복로 (구리 → 한남)", type: "속도 위반", typeTone: "tg-rd", plate: "12가 4567", conf: 96, st: "검토 대기", detectSpeed: 112, limitSpeed: 80, camera: "CAM-K-014", lane: 2 },
  { time: "14:31:54", place: "용산구 한강대로",         type: "OCR 인식",  typeTone: "tg-bl", plate: "12서 3456", conf: 93, st: "검토 대기", detectSpeed: 64,  limitSpeed: 60, camera: "CAM-H-022", lane: 1 },
  { time: "14:31:22", place: "내부순환로 (정릉 → 성수)", type: "속도 위반", typeTone: "tg-rd", plate: "34더 5678", conf: 95, st: "검토 대기", detectSpeed: 108, limitSpeed: 80, camera: "CAM-J-007", lane: 3 },
  { time: "14:30:49", place: "올림픽대로 (가양 → 마포)", type: "OCR 인식",  typeTone: "tg-bl", plate: "56루 7890", conf: 92, st: "검토 대기", detectSpeed: 78,  limitSpeed: 80, camera: "CAM-O-011", lane: 2 },
  { time: "14:30:11", place: "강변복로 (한남 TG 부근)",   type: "속도 위반", typeTone: "tg-rd", plate: "11가 2233", conf: 97, st: "검토 대기", detectSpeed: 121, limitSpeed: 80, camera: "CAM-K-015", lane: 1 },
  { time: "14:29:33", place: "동부간선로 (수락 → 성수)", type: "속도 위반", typeTone: "tg-rd", plate: "28오 3344", conf: 94, st: "검토 대기", detectSpeed: 104, limitSpeed: 80, camera: "CAM-D-031", lane: 2 },
  { time: "14:28:52", place: "강변복로 (마포 → 구리)",   type: "OCR 인식",  typeTone: "tg-bl", plate: "45주 6677", conf: 96, st: "승인",       detectSpeed: 72,  limitSpeed: 80, camera: "CAM-K-008", lane: 3 },
  { time: "14:28:10", place: "마포구 마포대로",          type: "OCR 인식",  typeTone: "tg-bl", plate: "33바 8899", conf: 91, st: "승인",       detectSpeed: 58,  limitSpeed: 60, camera: "CAM-M-002", lane: 1 },
  { time: "14:27:31", place: "올림픽대로 (여의도 → 가양)", type: "속도 위반", typeTone: "tg-rd", plate: "71너 9900", conf: 93, st: "반려",       detectSpeed: 95,  limitSpeed: 80, camera: "CAM-O-019", lane: 2 },
  { time: "14:26:44", place: "강남구 테헤란로",          type: "OCR 인식",  typeTone: "tg-bl", plate: "65도 1122", conf: 95, st: "승인",       detectSpeed: 55,  limitSpeed: 60, camera: "CAM-G-004", lane: 1 },
];

const allEvents = ref(seed.map((e, i) => ({
  ...e,
  id: i + 1,
  evtId: `EVT-2024-05-16-${e.time.replace(/:/g, "")}`,
})));

const filterType = ref("all");
const query = ref("");
const page = ref(1);
const perPage = 8;
const selected = ref(null);
const memo = ref("");
const reason = ref("");
const thumbIdx = ref(0);
const history = ref([]);
const auditLog = ref([
  { at: "2024-05-16 14:32:25", user: "단속관리팀", role: "단속관리팀", action: "검토 대기 등록", result: "-", resultTone: "wait", note: "이벤트 검토 대기 상태로 등록" },
  { at: "2024-05-16 14:32:18", user: "시스템",       role: "시스템",     action: "이벤트 생성",     result: "성공", resultTone: "ok",   note: "이벤트 발생 및 OCR 처리 완료" },
]);

const approveCount = computed(() => 42 + history.value.filter(h => h.verdict === "승인").length);
const rejectCount  = computed(() => 3  + history.value.filter(h => h.verdict === "반려").length);

function openEvidence() {
  if (!selected.value) return;
  auditLog.value.unshift({
    at: new Date().toLocaleString("sv-SE").replace(",", ""),
    user: "단속관리팀", role: "단속관리팀",
    action: "증빙 조회", result: "성공", resultTone: "ok",
    note: `이벤트 ${selected.value.evtId} 증빙 조회`,
  });
}

const stTone = (s) => s === "검토 대기" ? "wait" : (s === "승인" ? "ok" : (s === "반려" || s === "오탐" ? "no" : "wait"));

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return allEvents.value.filter(e => {
    if (filterType.value !== "all" && e.type !== filterType.value) return false;
    if (!q) return true;
    return e.place.toLowerCase().includes(q) || e.plate.toLowerCase().includes(q);
  });
});

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage)));
const pageTotal = computed(() => Math.max(totalPages.value, 20));
const pageNumbers = computed(() => {
  const last = pageTotal.value;
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1);
  const cur = Math.min(Math.max(page.value, 1), last);
  const pages = [];
  if (cur <= 4) pages.push(1, 2, 3, 4, 5, "...", last);
  else if (cur >= last - 3) pages.push(1, "...", last - 4, last - 3, last - 2, last - 1, last);
  else pages.push(1, "...", cur - 1, cur, cur + 1, "...", last);
  return pages;
});
const pagedEvents = computed(() => {
  const p = Math.min(page.value, totalPages.value);
  const start = (p - 1) * perPage;
  return filtered.value.slice(start, start + perPage);
});

const waitCount = computed(() => {
  const dynamic = allEvents.value.filter(e => e.st === "검토 대기").length;
  const initial = 18;
  return Math.max(initial + (dynamic - 6), 0);
});
const doneCount = computed(() => allEvents.value.filter(e => e.st !== "검토 대기").length);
const avgConf = computed(() => {
  if (!allEvents.value.length) return 94;
  const sum = allEvents.value.reduce((s, e) => s + e.conf, 0);
  return Math.round((sum / allEvents.value.length + 94) / 2);
});

const autoRefresh = ref(true);
function goHome() {
  selected.value = null;
  page.value = 1;
  query.value = "";
  filterType.value = "all";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function selectEvent(e) {
  selected.value = e;
  thumbIdx.value = 0;
  memo.value = "";
}

function pad(n) { return String(n).padStart(2, "0"); }
function nowStr() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function judge(verdict) {
  if (!selected.value) return;
  const target = allEvents.value.find(x => x.id === selected.value.id);
  if (!target) return;
  target.st = verdict;
  history.value.unshift({
    at: nowStr(), evtId: target.evtId, type: target.type, typeTone: target.typeTone,
    plate: target.plate, verdict,
    verdictTone: verdict === "승인" ? "ok" : "no",
    by: "단속관리팀", note: memo.value || reason.value || "-",
  });
  auditLog.value.unshift({
    at: nowStr(), user: "단속관리팀", role: "단속관리팀",
    action: `검토 ${verdict}`, result: "성공", resultTone: "ok",
    note: `${target.evtId} → ${verdict}${reason.value ? ` (${reason.value})` : ""}`,
  });
  memo.value = "";
  reason.value = "";
}

function judgeAndNext() {
  if (!selected.value) return;
  if (selected.value.st === "검토 대기") judge("승인");
  const waiting = allEvents.value.filter(e => e.st === "검토 대기");
  selected.value = waiting[0] || null;
  thumbIdx.value = 0;
}

function copyId() {
  if (!selected.value) return;
  try { navigator.clipboard?.writeText(selected.value.evtId); } catch (_) {}
}
</script>

<style scoped>
.rev-shell { min-height: 100vh; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.top h1 { display: flex; align-items: center; gap: 8px; }
.brand-link { display: inline-flex; align-items: center; gap: 8px; color: inherit; text-decoration: none; cursor: pointer; }
.brand-link:hover { opacity: 0.85; }
.top .dot { width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; box-shadow: 0 0 8px #60a5fa; }
.t-sub { font-weight: 500; opacity: .8; }
.t-right { display: flex; align-items: center; gap: 10px; }
.t-logout { width: 32px; height: 32px; background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.7); border-radius: 6px; cursor: pointer; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.st-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 18px 22px; display: flex; align-items: center; gap: 12px; }
.st-card > i { font-size: 22px; }
.ocr-cir { width: 30px; height: 30px; border-radius: 50%; background: rgba(96,165,250,.18); color: #60a5fa; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }
.st-lab { font-size: 14px; opacity: .8; flex: 1; }
.st-val { font-size: 22px; font-weight: 800; }
.st-u { font-size: 13px; font-weight: 500; opacity: .65; margin-left: 2px; }
.grid { display: grid; grid-template-columns: 1.1fr 1.3fr 1fr; gap: 14px; }
.card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; }
.card h3 { font-size: 14px; font-weight: 700; margin: 0; }
.lh { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; gap: 10px; }
.lh-r { display: flex; gap: 8px; align-items: center; }
.lh-sel { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; font-size: 12px; padding: 5px 10px; border-radius: 5px; }
.lh-search { position: relative; }
.lh-search i { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); opacity: .55; font-size: 12px; }
.lh-search input { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 5px 8px 5px 26px; border-radius: 5px; font-size: 12px; width: 170px; }
.tbl-rev { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl-rev th, .tbl-rev td { padding: 10px 10px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-rev th { font-weight: 700; opacity: .65; font-size: 13px; }
.tbl-rev tr.sel { background: rgba(96,165,250,.08); }
.tbl-rev .mono { font-family: "JetBrains Mono", monospace; }
.tbl-rev .ttl { font-weight: 600; max-width: 220px; }
.tbl-rev .row-sub { font-size: 12px; opacity: .55; font-weight: 400; margin-top: 2px; font-family: "JetBrains Mono", monospace; }
.tbl-rev .sp-rd { color: #f87171; }
.tag { padding: 2px 8px; border-radius: 100px; font-size: 10.5px; font-weight: 700; }
.tag.tg-rd { background: rgba(239,68,68,.18); color: #f87171; }
.tag.tg-bl { background: rgba(96,165,250,.18); color: #60a5fa; }
.stat { padding: 3px 11px; border-radius: 100px; font-size: 12.5px; font-weight: 700; }
.stat.wait { background: rgba(96,165,250,.1); color: #60a5fa; border: 1px solid rgba(96,165,250,.3); }
.stat.ok { background: rgba(16,185,129,.15); color: #34d399; }
.stat.no { background: rgba(239,68,68,.15); color: #f87171; }
.pager { display: flex; gap: 4px; justify-content: center; align-items: center; padding-top: 12px; }
.pager button { background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.7); width: 28px; height: 28px; border-radius: 4px; font-size: 11.5px; cursor: pointer; }
.pager .pg.on { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.pager .pg.dots { border: 0; cursor: default; opacity: .5; background: none; }
.pg-dots { color: rgba(228,238,255,.5); font-size: 11px; padding: 0 4px; }
.dh { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; gap: 10px; }
.dh h3 { display: flex; align-items: center; gap: 6px; }
.b-red { background: rgba(239,68,68,.18); color: #f87171; font-size: 10.5px; font-weight: 700; padding: 1px 8px; border-radius: 4px; }
.evt-id { font-size: 11px; opacity: .65; font-family: "JetBrains Mono", monospace; display: inline-flex; align-items: center; gap: 4px; }
.vimg { position: relative; background: linear-gradient(180deg, #4a5575 0%, #2a3550 100%); border-radius: 8px; height: 220px; margin-bottom: 10px; overflow: hidden; }
.vi-lab { position: absolute; top: 8px; left: 10px; font-size: 11px; opacity: .85; background: rgba(0,0,0,.4); padding: 2px 8px; border-radius: 3px; z-index: 1; }
.vi-img { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; position: relative; }
.plate-on-car { position: absolute; bottom: 40%; background: #fff; color: #000; padding: 4px 10px; border-radius: 3px; font-weight: 800; font-family: "JetBrains Mono", monospace; font-size: 14px; border: 2px solid #1a1a1a; }
.vi-zoom { position: absolute; bottom: 8px; right: 8px; width: 26px; height: 26px; background: rgba(0,0,0,.5); border: 0; color: #fff; border-radius: 3px; cursor: pointer; }
.thumb-row { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.thumb-row button { background: rgba(255,255,255,.04); border: 1px solid #1f3055; color: rgba(228,238,255,.6); width: 26px; height: 38px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.th-cnt { font-size: 11.5px; opacity: .65; padding: 0 6px; }
.th-imgs { display: flex; gap: 6px; flex: 1; }
.th { flex: 1; height: 38px; background: linear-gradient(180deg, #4a5575 0%, #2a3550 100%); border-radius: 4px; }
.th.on { outline: 2px solid #60a5fa; }
.ocr-section { background: #06101e; border: 1px solid #1f3055; border-radius: 8px; padding: 12px; }
.ocr-h { font-size: 12px; font-weight: 600; opacity: .85; margin-bottom: 10px; }
.ocr-grid { display: grid; grid-template-columns: 180px 1fr; gap: 16px; align-items: center; }
.plate-img { background: #fff; color: #000; font-family: "JetBrains Mono", monospace; font-weight: 800; font-size: 22px; padding: 14px 18px; border-radius: 5px; text-align: center; border: 2px solid #1a1a1a; }
.ocr-lab { font-size: 11px; opacity: .65; }
.ocr-val { font-size: 22px; font-weight: 800; margin: 2px 0 6px; }
.ocr-conf { font-size: 11.5px; opacity: .8; }
.ocr-conf strong { color: #60a5fa; font-size: 13px; }
.verify-card h3 { margin-bottom: 4px; }
.vq { font-size: 14px; font-weight: 700; margin: 4px 0 14px; }
.v-row { display: grid; grid-template-columns: 18px 1fr auto; gap: 8px; padding: 8px 0; border-bottom: 1px dashed rgba(255,255,255,.05); font-size: 12.5px; align-items: center; }
.v-row > i { opacity: .55; }
.v-row > span:nth-child(2) { opacity: .65; }
.v-row > span:nth-child(3) { font-weight: 700; }
.v-row .vr { color: #ef4444; }
.ocr-bar { display: flex; align-items: center; gap: 8px; font-size: 11.5px; font-weight: 700; }
.ocr-bar > span:first-child { display: inline-block; width: 120px; height: 6px; background: rgba(255,255,255,.06); border-radius: 4px; overflow: hidden; }
.ocr-bar > span:first-child span { display: block; height: 100%; background: linear-gradient(90deg, #60a5fa, #3b82f6); }
.judge { margin-top: 14px; }
.jh { font-size: 12px; font-weight: 600; opacity: .85; margin-bottom: 8px; }
.j-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.jb { padding: 12px 8px; border-radius: 8px; cursor: pointer; display: flex; flex-direction: column; align-items: center; gap: 4px; border: 1px solid; background: none; }
.jb i { font-size: 18px; }
.jt { font-size: 13px; font-weight: 700; }
.js { font-size: 10.5px; opacity: .65; }
.jb.gr { background: rgba(16,185,129,.1); border-color: rgba(16,185,129,.35); color: #34d399; }
.jb.rd { background: rgba(239,68,68,.1); border-color: rgba(239,68,68,.35); color: #f87171; }
.jb.or { background: rgba(245,158,11,.1); border-color: rgba(245,158,11,.35); color: #fbbf24; }
.jb.bl { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.jb.bl .js { color: rgba(255,255,255,.8); }
.memo { margin-top: 12px; }
.memo-lab { font-size: 11.5px; opacity: .75; margin-bottom: 6px; }
.memo textarea { width: 100%; min-height: 60px; background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 8px; border-radius: 5px; font-size: 12px; resize: vertical; outline: none; font-family: inherit; }
.memo-c { font-size: 10px; opacity: .55; text-align: right; margin-top: 2px; }
.log-card { padding: 14px; }
.tbl-log { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
.tbl-log th, .tbl-log td { padding: 8px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-log th { font-weight: 600; opacity: .55; font-size: 11px; }
.tbl-log .mono { font-family: "JetBrains Mono", monospace; }
.t-view { background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.65); font-size: 11.5px; padding: 4px 10px; border-radius: 5px; cursor: pointer; }

.th-num { font-weight: 700; color: #e4eeff; opacity: .85; }
.evt-info { background: #06101e; border: 1px solid #1f3055; border-radius: 8px; padding: 12px; margin-top: 10px; }
.ei-h { font-size: 12px; font-weight: 700; opacity: .85; margin-bottom: 10px; }
.ei-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 14px; }
.ei-row { display: flex; justify-content: space-between; font-size: 11.5px; padding: 3px 0; }
.ei-row > span { opacity: .65; }
.ei-row > strong { font-weight: 700; }
.ei-row .rd { color: #f87171; }
.ei-row .bl { color: #60a5fa; }
.mini-map { position: relative; margin-top: 10px; border-radius: 6px; overflow: hidden; background: #06101e; border: 1px solid #1f3055; }
.mm-svg { width: 100%; height: 90px; display: block; }
.mm-pin { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(8,16,32,.85); border: 1px solid #ef4444; padding: 5px 10px; border-radius: 4px; font-size: 11px; display: inline-flex; align-items: center; gap: 4px; font-weight: 700; white-space: nowrap; }
.mm-pin i { color: #ef4444; }

.vq { font-size: 11.5px; opacity: .65; line-height: 1.5; margin: 4px 0 12px; }
.auth-row { display: flex; align-items: center; gap: 6px; padding: 8px 10px; background: #06101e; border: 1px solid #1f3055; border-radius: 6px; margin-bottom: 12px; flex-wrap: wrap; }
.auth-lab { font-size: 11.5px; opacity: .7; margin-right: 4px; }
.auth-tag { font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 100px; }
.auth-tag.bl { background: rgba(96,165,250,.18); color: #60a5fa; }
.auth-tag.pl { background: rgba(139,92,246,.18); color: #a78bfa; }
.auth-tag.mini { font-size: 9.5px; padding: 1px 6px; margin-left: 4px; }

.reason-sel { width: 100%; background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 7px 10px; border-radius: 5px; font-size: 12px; margin-bottom: 6px; }
.hist { margin-top: 16px; padding-top: 12px; border-top: 1px solid #1a2a45; }
.hist h4 { font-size: 13px; font-weight: 700; margin: 0 0 10px; }
.hist-row { display: flex; gap: 10px; padding: 8px 0; align-items: center; }
.hist-row > i { font-size: 18px; color: #60a5fa; }
.hr-t { font-size: 12px; font-weight: 700; }
.hr-s { font-size: 10.5px; opacity: .55; font-family: "JetBrains Mono", monospace; margin-top: 2px; }
.hr-act { font-size: 10.5px; opacity: .7; font-weight: 400; margin-left: 4px; }

.tbl-audit { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 8px; }
.tbl-audit th, .tbl-audit td { padding: 8px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-audit th { font-weight: 600; opacity: .55; font-size: 11px; }
.tbl-audit .mono { font-family: "JetBrains Mono", monospace; }
</style>
