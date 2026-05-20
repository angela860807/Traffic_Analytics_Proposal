<template>
  <div class="rev-shell">
    <header class="top">
      <RouterLink to="/" class="brand" title="홈으로">
        Traffic <em>AS</em>
      </RouterLink>
      <h1><a class="t-main" @click="goHome">단속관리팀</a></h1>
      <div class="hdr-kpi">
        <span class="kpi-chip bl" title="검토 대기"><i class="bi bi-hourglass-split"></i> 대기 <strong>{{ waitCount }}</strong></span>
        <span class="kpi-chip gr" title="승인"><i class="bi bi-check-circle-fill"></i> 승인 <strong>{{ approveCount }}</strong></span>
        <span class="kpi-chip rd" title="반려"><i class="bi bi-x-circle-fill"></i> 반려 <strong>{{ rejectCount }}</strong></span>
        <span class="kpi-chip pl" title="OCR 평균 신뢰도"><span class="kc-ocr">OCR</span> <strong>{{ avgConf }}%</strong></span>
      </div>
      <div class="t-right">
        <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>14:32:18</strong></span>
        <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
          <span class="km-dot"></span>
          <span class="km-lab">자동 새로고침</span>
          <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
        </button>
        <div class="rev-dl">
          <input type="date" class="rev-dl-date" v-model="reportDate" />
          <button class="rev-dl-btn" @click="downloadDeptReport('review', 'daily', { date: reportDate })" title="일일 단속 보고서"><i class="bi bi-download"></i> 일일</button>
          <button class="rev-dl-btn" @click="downloadDeptReport('review', 'weekly', { date: weekStart, endDate: reportDate })" title="주간 단속 통계 (선택 날짜 기준 직전 7일)"><i class="bi bi-download"></i> 주간</button>
        </div>
        <DeptSwitcher />
        <div class="t-user"><i class="bi bi-person-circle"></i> 단속관리팀 매니저 <i class="bi bi-chevron-down"></i></div>
      </div>
    </header>

    <section class="grid">
      <div class="card list-card">
        <div class="lh">
          <h3>이벤트 목록</h3>
          <div class="lh-r">
            <select class="lh-sel" v-model="filterType">
              <option value="all">전체 ({{ countAll }})</option>
              <option value="속도 위반">과속 ({{ countSpeed }})</option>
              <option value="OCR 인식">OCR 인식 ({{ countOcr }})</option>
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
            <template v-for="grp in groupedEvents" :key="grp.date">
              <tr class="date-row">
                <td colspan="4">
                  <i class="bi bi-calendar3"></i>
                  <span class="date-t">{{ grp.date }}</span>
                  <span class="date-c">{{ grp.items.length }}건</span>
                </td>
              </tr>
              <tr v-for="e in grp.items" :key="e.id"
                :class="{ sel: selected && selected.id === e.id }"
                @click="selectEvent(e)">
                <td class="mono">{{ e.time }}</td>
                <td class="ttl">{{ e.place }}<div class="row-sub">{{ e.type === '속도 위반' ? '드론 구간' : '단속 임시' }}</div></td>
                <td class="mono">{{ e.plate }}</td>
                <td><span class="stat" :class="stTone(e.st)">{{ e.st }}</span></td>
              </tr>
            </template>
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
          <div class="vi-lab">
            <i :class="evtViewMode === 'image' && selected.image ? 'bi bi-image-fill' : 'bi bi-camera-video'"></i>
            {{ evtViewMode === 'image' && selected.image ? '관제센터 전송 이미지' : '실시간 영상' }}
            <span v-if="evtViewMode !== 'image'" class="vi-live"><span class="dot-live"></span></span>
            <span v-else class="vi-fromctrl">CTRL</span>
          </div>

          <!-- 모드 토글 — 이미지 이벤트일 때만 노출 -->
          <div v-if="selected.image" class="vi-tabs">
            <button class="vi-tab" :class="{ on: evtViewMode === 'image' }" @click="evtViewMode = 'image'"><i class="bi bi-image"></i> 캡처</button>
            <button class="vi-tab" :class="{ on: evtViewMode === 'live' }" @click="evtViewMode = 'live'"><i class="bi bi-broadcast"></i> 실시간</button>
          </div>

          <!-- 캡처 이미지 -->
          <div v-if="evtViewMode === 'image' && selected.image" class="vi-still">
            <img :src="selected.image" alt="관제센터 전송 이미지" />
            <div class="vi-ts">{{ selected.date || '' }} {{ selected.time }}</div>
          </div>

          <!-- 실시간 영상 (또는 시드 비디오) -->
          <div v-else class="vi-video">
            <video
              ref="evtVideoEl"
              :src="selected.clip || '/0513.mp4'"
              :key="(selected.clip || '/0513.mp4') + '-' + selected.id"
              autoplay muted loop playsinline
              preload="auto"
            ></video>
            <div class="vi-ts">{{ nowTime }}</div>
          </div>

          <div class="vi-controls" v-if="evtViewMode !== 'image'">
            <button class="vi-ctl" @click="toggleVideo"><i :class="videoPlaying ? 'bi bi-pause-fill' : 'bi bi-play-fill'"></i></button>
            <button class="vi-ctl" @click="restartVideo"><i class="bi bi-arrow-counterclockwise"></i></button>
            <button class="vi-ctl" @click="toggleMute"><i :class="videoMuted ? 'bi bi-volume-mute' : 'bi bi-volume-up'"></i></button>
            <button class="vi-zoom" @click="enterEvtFullscreen"><i class="bi bi-arrows-fullscreen"></i></button>
          </div>
        </div>
        <div class="thumb-row">
          <div class="th-cnt"><i class="bi bi-collection"></i> 최근 단속<br><span class="th-num">{{ recentPlates.length }}건</span></div>
          <div class="th-imgs">
            <div v-for="(p, i) in recentPlates" :key="p.evtId" class="th" :class="{ on: thumbIdx === i }" @click="thumbIdx = i">
              <div class="th-plate">{{ p.plate }}</div>
              <div class="th-time">{{ p.time }}</div>
            </div>
          </div>
        </div>
        <div class="ocr-section">
          <div class="ocr-h">
            <i class="bi bi-camera"></i> 차량 정보 (OCR)
            <div class="ocr-tools">
              <button class="ocr-cap-sm" @click="stepFrame(-0.1)" title="이전 프레임" :disabled="autoBusy"><i class="bi bi-skip-backward-fill"></i></button>
              <button class="ocr-cap-sm" @click="stepFrame(0.1)" title="다음 프레임" :disabled="autoBusy"><i class="bi bi-skip-forward-fill"></i></button>
              <button class="ocr-cap ocr-auto" @click="autoCapture" :disabled="autoBusy" title="선명한 프레임 자동 선택">
                <i :class="autoBusy ? 'bi bi-arrow-repeat spin' : 'bi bi-magic'"></i>
                {{ autoBusy ? '분석중…' : '자동' }}
              </button>
              <button class="ocr-cap" @click="captureSnapshot(true)" title="순간 캡처 (정지)" :disabled="autoBusy"><i class="bi bi-camera2"></i> 순간</button>
              <button v-if="snapFrozen" class="ocr-cap ocr-resume" @click="resumeAfterSnap" title="재생 재개"><i class="bi bi-play-fill"></i> 재생</button>
            </div>
          </div>
          <div class="ocr-grid">
            <div class="plate-snap">
              <img v-if="ocrSnapUrl" :src="ocrSnapUrl" alt="OCR 캡처" />
              <div v-else class="plate-snap-ph"><i class="bi bi-image"></i> 캡처 대기…</div>
              <div class="snap-plate">{{ selected.plate }}</div>
            </div>
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
        <h3><i class="bi bi-shield-check"></i> 2차 검증 · 최종 승인</h3>
        <div class="src-row">
          <i class="bi bi-broadcast"></i>
          <div>
            <div class="src-t">관제센터 캡처 이미지 수신</div>
            <div class="src-s">{{ selected.camera }} · 자동 캡처 시각 {{ selected.time }}</div>
          </div>
        </div>

        <div class="vq-h">
          <span class="vq-step">STEP 1</span>
          <strong>실제 과속 위반인가요?</strong>
        </div>
        <div class="ver-grid">
          <button class="vb" :class="{ on: verification === 'valid' }" @click="verification = 'valid'">
            <i class="bi bi-check2-circle"></i>
            <div>
              <span class="vbt">실제 과속</span>
              <span class="vbs">영상·OCR 모두 일치, 단속 확정</span>
            </div>
          </button>
          <button class="vb" :class="{ on: verification === 'error' }" @click="verification = 'error'">
            <i class="bi bi-exclamation-octagon"></i>
            <div>
              <span class="vbt">시스템 오류</span>
              <span class="vbs">오탐·환경요인, 단속 무효</span>
            </div>
          </button>
        </div>

        <div class="vq-h" :class="{ dim: !verification }">
          <span class="vq-step">STEP 2</span>
          <strong>사유 선택 · 메모</strong>
        </div>
        <div class="memo" :class="{ dim: !verification }">
          <select class="reason-sel" v-model="reason" :disabled="!verification">
            <option value="">사유 선택</option>
            <template v-if="verification === 'valid'">
              <option>명확한 위반 — 영상·OCR 모두 일치</option>
              <option>제한속도 초과 + 차량번호 명확</option>
              <option>기타 (메모 입력)</option>
            </template>
            <template v-else-if="verification === 'error'">
              <option>차량번호 식별 불가</option>
              <option>긴급차량 등 예외 상황</option>
              <option>장비 오류로 인한 오탐</option>
              <option>드론·환경 노이즈</option>
              <option>기타 (메모 입력)</option>
            </template>
          </select>
          <textarea v-model="memo" placeholder="2차 검증 메모 (선택 사항)" maxlength="200" :disabled="!verification"></textarea>
          <div class="memo-c">{{ memo.length }} / 200</div>
        </div>

        <div class="vq-h" :class="{ dim: !verification }">
          <span class="vq-step">STEP 3</span>
          <strong>최종 결정</strong>
        </div>
        <div class="final-act">
          <button class="fa-btn gr" @click="judge('승인')">
            <i class="bi bi-check-circle-fill"></i> 단속 확정 (승인)
          </button>
          <button class="fa-btn rd" @click="judge('반려')">
            <i class="bi bi-x-circle-fill"></i> 단속 무효 (반려)
          </button>
        </div>

        <div class="hist">
          <h4>검토 히스토리</h4>
          <div class="hist-row"><i class="bi bi-person-circle"></i>
            <div><div class="hr-t">단속관리팀 <span class="auth-tag bl mini">{{ selected.st }}</span></div><div class="hr-s">2024-05-16 14:32:25</div></div>
          </div>
          <div class="hist-row"><i class="bi bi-broadcast"></i>
            <div><div class="hr-t">관제센터 <span class="hr-act">캡처 이미지 전달</span></div><div class="hr-s">2024-05-16 {{ selected.time }}</div></div>
          </div>
          <div class="hist-row"><i class="bi bi-cpu"></i>
            <div><div class="hr-t">시스템 <span class="hr-act">속도 위반 자동 감지</span></div><div class="hr-s">2024-05-16 {{ selected.time }}</div></div>
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import { useReportDownload } from "@/composables/useReportDownload";
import { useViolationQueue } from "@/composables/useViolationQueue";
import { fmtDateTime, enterFullscreen, captureFrameDataURL, seekVideo } from "@/composables/useVideoUtils";
const { downloadDeptReport } = useReportDownload();
const { queue: violationQueue } = useViolationQueue();

// 보고서 다운로드 날짜
const todayISO = () => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};
const reportDate = ref(todayISO());
const weekStart = computed(() => {
  const d = new Date(reportDate.value);
  d.setDate(d.getDate() - 6);
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
});

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

// 시드 이벤트에 가상 날짜 부여 (최근 3일에 걸쳐 분산)
function seedDate(i) {
  const d = new Date();
  d.setDate(d.getDate() - Math.floor(i / 4)); // 4건마다 하루씩 과거
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}
const baseEvents = ref(seed.map((e, i) => {
  const date = seedDate(i);
  return {
    ...e,
    id: i + 1,
    date,
    evtId: `EVT-${date.replace(/-/g, "")}-${e.time.replace(/:/g, "")}`,
    clip: i % 2 === 0 ? "/0513.mp4" : "/1.mp4",
    source: "seed",
  };
}));

// 관제센터 전송 큐 + 시드 이벤트 병합 (전송 항목이 위로) — 참조 직결로 mutate 반영
const allEvents = computed(() => [
  ...violationQueue.value,
  ...baseEvents.value,
]);

const filterType = ref("all");
const query = ref("");
const page = ref(1);
const perPage = 8;
const selected = ref(null);
const memo = ref("");

// 이벤트 상세 뷰 모드: 'image' (캡처) / 'live' (실시간 영상)
const evtViewMode = ref("image");

// 단속 영상 컨트롤 — 한 번에 1개만 재생
const evtVideoEl = ref(null);
const videoPlaying = ref(true);
const videoMuted = ref(true);
function toggleVideo() {
  if (!evtVideoEl.value) return;
  if (evtVideoEl.value.paused) { evtVideoEl.value.play().catch(() => {}); videoPlaying.value = true; }
  else { evtVideoEl.value.pause(); videoPlaying.value = false; }
}
function restartVideo() {
  if (!evtVideoEl.value) return;
  evtVideoEl.value.currentTime = 0;
  evtVideoEl.value.play().catch(() => {});
  videoPlaying.value = true;
}
function toggleMute() {
  if (!evtVideoEl.value) return;
  evtVideoEl.value.muted = !evtVideoEl.value.muted;
  videoMuted.value = evtVideoEl.value.muted;
}
function enterEvtFullscreen() {
  enterFullscreen(evtVideoEl);
}

// 최근 단속 3개 (선택 제외)
const recentPlates = computed(() => {
  if (!selected.value) return [];
  return allEvents.value
    .filter((e) => e.id !== selected.value.id)
    .slice(0, 3)
    .map((e) => ({ evtId: e.evtId, plate: e.plate, time: e.time }));
});

// OCR 순간 캡처 — 프레임 정지 + 확대 크롭
const ocrSnapUrl = ref("");
const snapFrozen = ref(false);
function captureSnapshot(freeze = true) {
  const v = evtVideoEl.value;
  if (!v || !v.videoWidth) return;
  if (freeze && !v.paused) {
    v.pause();
    videoPlaying.value = false;
    snapFrozen.value = true;
  }
  // 번호판 추정 영역: 가로 중앙 60%, 세로 30~80%
  const url = captureFrameDataURL(v, {
    outWidth: 480,
    quality: 0.92,
    crop: {
      x: v.videoWidth * 0.20,
      y: v.videoHeight * 0.35,
      w: v.videoWidth * 0.60,
      h: v.videoHeight * 0.45,
    },
  });
  if (url) ocrSnapUrl.value = url;
}
function resumeAfterSnap() {
  const v = evtVideoEl.value;
  if (!v) return;
  v.play().catch(() => {});
  videoPlaying.value = true;
  snapFrozen.value = false;
}
function stepFrame(deltaSec) {
  const v = evtVideoEl.value;
  if (!v) return;
  if (!v.paused) { v.pause(); videoPlaying.value = false; }
  v.currentTime = Math.max(0, Math.min(v.duration || 0, v.currentTime + deltaSec));
  snapFrozen.value = true;
  // 짧은 지연 후 재캡처
  setTimeout(() => captureSnapshot(false), 100);
}

// 자동 캡처 — 선명도(엣지 강도) 기준으로 가장 또렷한 프레임 선택
const autoBusy = ref(false);
async function autoCapture() {
  const v = evtVideoEl.value;
  if (!v || !v.duration || autoBusy.value) return;
  autoBusy.value = true;
  try {
    if (!v.paused) { v.pause(); videoPlaying.value = false; }
    snapFrozen.value = true;

    const startT = v.currentTime;
    const samples = 8;
    const windowSec = 1.6;
    const step = windowSec / samples;

    const aw = 240, ah = 135;
    const aCanvas = document.createElement("canvas");
    aCanvas.width = aw; aCanvas.height = ah;
    const aCtx = aCanvas.getContext("2d", { willReadFrequently: true });

    let best = { score: -1, time: startT };

    for (let i = 0; i < samples; i++) {
      const t = startT + i * step;
      if (v.duration && t > v.duration - 0.05) break;
      await seekVideo(v,t);

      // 번호판 추정 영역만 분석
      const vw = v.videoWidth, vh = v.videoHeight;
      const cx = vw * 0.20, cy = vh * 0.35, cw = vw * 0.60, ch = vh * 0.45;
      aCtx.drawImage(v, cx, cy, cw, ch, 0, 0, aw, ah);
      const data = aCtx.getImageData(0, 0, aw, ah).data;

      // 엣지 강도 합 (가벼운 |dx|+|dy| on luminance)
      let score = 0;
      const stride = aw * 4;
      for (let y = 1; y < ah - 1; y += 2) {
        for (let x = 1; x < aw - 1; x += 2) {
          const idx = y * stride + x * 4;
          const lum = data[idx] * 299 + data[idx + 1] * 587 + data[idx + 2] * 114;
          const lumR = data[idx + 4] * 299 + data[idx + 5] * 587 + data[idx + 6] * 114;
          const lumB = data[idx + stride] * 299 + data[idx + stride + 1] * 587 + data[idx + stride + 2] * 114;
          score += Math.abs(lum - lumR) + Math.abs(lum - lumB);
        }
      }
      if (score > best.score) best = { score, time: t };
    }

    // 최상의 프레임으로 점프 후 캡처
    await seekVideo(v,best.time);
    captureSnapshot(false);
  } finally {
    autoBusy.value = false;
  }
}
// 이벤트 선택 후 1.2초 뒤 자동 캡처 (영상 프레임 로드 대기)
// 관제센터 전송 이미지의 경우 그대로 OCR 슬롯에 채움
watch(() => selected.value?.id, (id) => {
  ocrSnapUrl.value = "";
  // 이미지 이벤트면 캡처 모드로, 아니면 실시간 모드로 기본 설정
  evtViewMode.value = selected.value?.image ? "image" : "live";
  if (!id) return;
  if (selected.value?.image) {
    ocrSnapUrl.value = selected.value.image;
    return;
  }
  setTimeout(captureSnapshot, 1200);
});

// 실시간 시계
const nowTime = ref("");
let timeTimer = null;
onMounted(() => {
  nowTime.value = fmtDateTime();
  timeTimer = setInterval(() => { nowTime.value = fmtDateTime(); }, 1000);
});
onBeforeUnmount(() => {
  if (timeTimer) clearInterval(timeTimer);
});
const reason = ref("");
const thumbIdx = ref(0);
const history = ref([]);
const auditLog = ref([
  { at: "2024-05-16 14:32:25", user: "단속관리팀", role: "단속관리팀", action: "검토 대기 등록", result: "-", resultTone: "wait", note: "이벤트 검토 대기 상태로 등록" },
  { at: "2024-05-16 14:32:18", user: "시스템",       role: "시스템",     action: "이벤트 생성",     result: "성공", resultTone: "ok",   note: "이벤트 발생 및 OCR 처리 완료" },
]);

const approveCount = computed(() => 42 + history.value.filter(h => h.verdict === "승인").length);
const rejectCount  = computed(() => 3  + history.value.filter(h => h.verdict === "반려").length);

// 2차 검증 상태: 'valid' (실제 과속) | 'error' (시스템 오류) | ''
const verification = ref("");

// 필터 칩 카운트
const countAll = computed(() => allEvents.value.length);
const countSpeed = computed(() => allEvents.value.filter((e) => e.type === "속도 위반").length);
const countOcr = computed(() => allEvents.value.filter((e) => e.type === "OCR 인식").length);

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

// 페이지 이벤트를 일자별로 그룹화 (최신 날짜 위)
const groupedEvents = computed(() => {
  const map = new Map();
  pagedEvents.value.forEach((e) => {
    const d = e.date || "—";
    if (!map.has(d)) map.set(d, []);
    map.get(d).push(e);
  });
  return Array.from(map.entries())
    .map(([date, items]) => ({ date, items }))
    .sort((a, b) => (a.date < b.date ? 1 : -1));
});

const waitCount = computed(() => {
  const dynamic = allEvents.value.filter(e => e.st === "검토 대기").length;
  const initial = 18;
  return Math.max(initial + (dynamic - 6), 0);
});
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
  verification.value = "";
  reason.value = "";
}

const nowStr = () => fmtDateTime();

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
  verification.value = "";
}


function copyId() {
  if (!selected.value) return;
  try { navigator.clipboard?.writeText(selected.value.evtId); } catch (_) {}
}
</script>

<style scoped>
.rev-shell { min-height: 100vh; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.top { display: flex; align-items: center; gap: 12px; }
.top h1 { display: flex; align-items: center; gap: 8px; margin: 0; flex: 1; }
.brand-link { display: inline-flex; align-items: center; gap: 8px; color: inherit; text-decoration: none; cursor: pointer; }
.brand-link:hover { opacity: 0.85; }
.top .dot { width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; box-shadow: 0 0 8px #60a5fa; }
.t-sub { font-weight: 500; opacity: .8; }
.t-right { display: flex; align-items: center; gap: 10px; }
.hdr-kpi {
  display: inline-flex; align-items: center; gap: 6px;
  margin-left: 14px; flex-wrap: wrap;
}
.kpi-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 100px;
  padding: 4px 11px;
  font-size: 12.5px; font-weight: 600;
  color: #e4eeff; white-space: nowrap;
}
.kpi-chip strong {
  font-family: "JetBrains Mono", monospace;
  font-weight: 800; font-size: 13.5px;
  margin-left: 1px;
}
.kpi-chip i { font-size: 12px; }
.kpi-chip.bl { color: #60a5fa; border-color: rgba(96,165,250,0.35); background: rgba(96,165,250,0.08); }
.kpi-chip.gr { color: #34d399; border-color: rgba(52,211,153,0.35); background: rgba(52,211,153,0.08); }
.kpi-chip.rd { color: #f87171; border-color: rgba(248,113,113,0.35); background: rgba(248,113,113,0.08); }
.kpi-chip.pl { color: #a78bfa; border-color: rgba(167,139,250,0.35); background: rgba(167,139,250,0.08); }
.kpi-chip .kc-ocr {
  background: rgba(255,255,255,0.12); padding: 1px 6px; border-radius: 3px;
  font-size: 10px; font-weight: 800; letter-spacing: 0.04em;
}
.rev-dl { display: inline-flex; gap: 4px; }
.rev-dl-date {
  background: #06101e;
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 5px 8px;
  border-radius: 4px;
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  margin-right: 2px;
}
.rev-dl-date::-webkit-calendar-picker-indicator {
  filter: invert(0.7);
  cursor: pointer;
}
.rev-dl-btn {
  background: #059669; color: #fff; border: 0;
  padding: 6px 12px; border-radius: 4px;
  font-size: 12.5px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; gap: 4px;
}
.rev-dl-btn:hover { background: #047857; }
.t-logout { width: 32px; height: 32px; background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.7); border-radius: 6px; cursor: pointer; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.st-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 18px 22px; display: flex; align-items: center; gap: 12px; }
.st-card > i { font-size: 22px; }
.ocr-cir { width: 30px; height: 30px; border-radius: 50%; background: rgba(96,165,250,.18); color: #60a5fa; font-size: 11px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }
.st-lab { font-size: 14px; opacity: .8; flex: 1; }
.st-val { font-size: 22px; font-weight: 800; }
.st-u { font-size: 13px; font-weight: 500; opacity: .65; margin-left: 2px; }
.grid { display: grid; grid-template-columns: 0.85fr 1.6fr 1fr; gap: 14px; }
.card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; }
.card h3 { font-size: 14px; font-weight: 700; margin: 0; }
.lh { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; gap: 10px; }
.lh-r { display: flex; gap: 8px; align-items: center; }
.lh-pills { display: inline-flex; gap: 4px; }
.lh-pill {
  background: rgba(255,255,255,0.04); border: 1px solid #1f3055;
  color: rgba(228,238,255,0.75);
  padding: 5px 11px; border-radius: 100px;
  font-size: 12.5px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; gap: 5px;
}
.lh-pill .lh-c {
  background: rgba(255,255,255,0.1); color: inherit;
  font-family: "JetBrains Mono", monospace;
  font-size: 11.5px; padding: 1px 7px; border-radius: 100px;
  font-weight: 800;
}
.lh-pill:hover { background: rgba(255,255,255,0.08); color: #fff; }
.lh-pill.on { background: #2563eb; border-color: #2563eb; color: #fff; }
.lh-pill.on .lh-c { background: rgba(255,255,255,0.25); }
.lh-pill.rd.on { background: #dc2626; border-color: #dc2626; }
.lh-pill.bl.on { background: #2563eb; border-color: #2563eb; }
.lh-sel { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; font-size: 12px; padding: 5px 10px; border-radius: 5px; }

/* 과속 차량 TOP strip */
.speeders-strip {
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 14px;
}
.ss-h {
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 10px;
}
.ss-h > i { color: #f87171; font-size: 18px; }
.ss-h strong { font-size: 14px; color: #e4eeff; }
.ss-sub { font-size: 11.5px; opacity: 0.6; margin-left: 4px; }
.ss-all {
  margin-left: auto; background: none; border: 0;
  color: #60a5fa; font-size: 12px; font-weight: 700; cursor: pointer;
}
.ss-all:hover { color: #93c5fd; }
.ss-list {
  display: grid; grid-auto-flow: column; grid-auto-columns: minmax(180px, 1fr);
  gap: 8px; overflow-x: auto; padding-bottom: 2px;
}
.ss-card {
  background: #06101e;
  border: 1px solid #1f3055;
  border-left: 3px solid #ef4444;
  border-radius: 6px;
  padding: 10px 12px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  display: flex; flex-direction: column; gap: 4px;
  min-width: 0;
}
.ss-card:hover { background: rgba(239,68,68,0.06); border-color: #ef4444; }
.ss-card.on { background: rgba(96,165,250,0.1); border-color: #60a5fa; border-left-color: #60a5fa; }
.ss-over {
  font-family: "JetBrains Mono", monospace;
  font-size: 22px; font-weight: 800; color: #f87171;
  line-height: 1.1;
}
.ss-over small { font-size: 11px; font-weight: 600; opacity: 0.75; margin-left: 3px; }
.ss-plate {
  display: inline-block; background: #fff; color: #0c1f40;
  font-family: "JetBrains Mono", monospace; font-weight: 800;
  font-size: 13px; padding: 2px 8px; border-radius: 2px;
  border: 1.5px solid #1a1a1a;
  align-self: flex-start;
}
.ss-meta {
  display: flex; justify-content: space-between;
  font-family: "JetBrains Mono", monospace;
  font-size: 11px; opacity: 0.7; margin-top: 2px;
}
.ss-spd { color: #fca5a5; font-weight: 700; }
.ss-place {
  font-size: 11.5px; color: rgba(228,238,255,0.75);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lh-search { position: relative; }
.lh-search i { position: absolute; left: 8px; top: 50%; transform: translateY(-50%); opacity: .55; font-size: 12px; }
.lh-search input { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 5px 8px 5px 26px; border-radius: 5px; font-size: 12px; width: 170px; }
.tbl-rev { width: 100%; border-collapse: collapse; font-size: 14px; }
.tbl-rev th, .tbl-rev td { padding: 10px 10px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-rev th { font-weight: 700; opacity: .65; font-size: 13px; }
.tbl-rev tr.sel { background: rgba(96,165,250,.08); }
.tbl-rev .date-row { background: rgba(96,165,250,0.06); }
.tbl-rev .date-row td {
  padding: 6px 12px !important;
  border-bottom: 1px solid rgba(96,165,250,0.25) !important;
  cursor: default;
}
.tbl-rev .date-row i {
  color: #60a5fa; margin-right: 6px; font-size: 12px;
}
.tbl-rev .date-row .date-t {
  font-family: "JetBrains Mono", monospace;
  font-size: 12.5px; font-weight: 800; color: #93c5fd;
  letter-spacing: 0.02em;
}
.tbl-rev .date-row .date-c {
  margin-left: 8px; font-size: 11px; opacity: 0.65;
  font-family: "JetBrains Mono", monospace;
}
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
.vimg { position: relative; background: #0a1424; border-radius: 8px; aspect-ratio: 16/9; width: 100%; margin-bottom: 10px; overflow: hidden; }
.vi-lab { position: absolute; top: 8px; left: 10px; font-size: 12px; font-weight: 800; color: #ffffff; background: rgba(0,0,0,.7); padding: 4px 10px; border-radius: 3px; z-index: 2; display: inline-flex; align-items: center; gap: 6px; }
.vi-lab i { color: #93c5fd; }
.vi-live { display: inline-flex; align-items: center; }
.vi-live .dot-live { width: 9px; height: 9px; border-radius: 50%; background: #ef4444; box-shadow: 0 0 0 2px rgba(239,68,68,0.35); animation: nsPulse 1.2s ease-in-out infinite; }
.vi-video { width: 100%; height: 100%; position: relative; }
.vi-video video { width: 100%; height: 100%; object-fit: cover; display: block; background: #000; }
.vi-still { width: 100%; height: 100%; position: relative; }
.vi-still img { width: 100%; height: 100%; object-fit: contain; display: block; background: #000; }
.vi-fromctrl {
  background: #2563eb; color: #fff;
  font-size: 10px; font-weight: 800; letter-spacing: 0.06em;
  padding: 2px 7px; border-radius: 3px; margin-left: 4px;
}
.vi-tabs {
  position: absolute; top: 8px; left: 50%; transform: translateX(-50%);
  display: inline-flex; gap: 2px; z-index: 3;
  background: rgba(0,0,0,0.75); padding: 3px;
  border: 1px solid rgba(255,255,255,0.35);
  border-radius: 5px;
}
.vi-tab {
  background: transparent; border: 0; color: rgba(255,255,255,0.7);
  padding: 4px 10px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  border-radius: 3px;
  display: inline-flex; align-items: center; gap: 4px;
}
.vi-tab.on { background: #2563eb; color: #fff; }
.vi-tab:hover:not(.on) { color: #fff; background: rgba(255,255,255,0.08); }
.vi-ts { position: absolute; top: 8px; right: 10px; font-size: 12px; font-weight: 700; color: #ffffff; background: rgba(0,0,0,.7); padding: 4px 10px; border-radius: 3px; font-family: "JetBrains Mono", monospace; z-index: 2; letter-spacing: 0.02em; }
.vi-controls {
  position: absolute; bottom: 6px; right: 6px;
  display: inline-flex; gap: 3px; z-index: 3;
  padding: 3px;
  background: rgba(0, 0, 0, 0.78);
  border: 1px solid rgba(255,255,255,0.45);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.vi-ctl, .vi-zoom {
  width: 22px; height: 22px;
  background: #2563eb;
  border: 1px solid rgba(255,255,255,0.5);
  color: #ffffff;
  border-radius: 3px; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11px;
  transition: background 0.15s, transform 0.1s;
  position: static;
}
.vi-ctl i, .vi-zoom i {
  color: #ffffff !important;
  font-size: 11px;
  line-height: 1;
}
.vi-ctl:hover, .vi-zoom:hover {
  background: #1d4ed8;
  box-shadow: 0 0 0 2px rgba(37,99,235,0.5);
}
.vi-ctl:active, .vi-zoom:active { transform: scale(0.92); }
@keyframes nsPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
.thumb-row { display: flex; align-items: stretch; gap: 8px; margin-bottom: 12px; }
.th-cnt { font-size: 11.5px; opacity: .8; padding: 0 8px; display: flex; flex-direction: column; justify-content: center; min-width: 70px; }
.th-cnt i { color: #60a5fa; margin-right: 4px; }
.th-imgs { display: flex; gap: 6px; flex: 1; }
.th {
  flex: 1; padding: 6px 8px; border-radius: 4px;
  background: linear-gradient(180deg, #1a2a45 0%, #0f1d34 100%);
  border: 1px solid #1f3055;
  cursor: pointer;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 3px;
  transition: border-color 0.15s;
}
.th:hover { border-color: #3b82f6; }
.th.on { border-color: #3b82f6; background: linear-gradient(180deg, #1d4ed8 0%, #1e3a8a 100%); }
.th-plate {
  background: #ffffff; color: #0c1f40; font-family: "JetBrains Mono", monospace;
  font-weight: 800; font-size: 12.5px; padding: 3px 8px; border-radius: 2px;
  border: 1.5px solid #1a1a1a;
  white-space: nowrap;
}
.th-time { font-size: 10px; opacity: 0.75; font-family: "JetBrains Mono", monospace; }
.th.on { outline: 2px solid #60a5fa; }
.ocr-section { background: #06101e; border: 1px solid #1f3055; border-radius: 8px; padding: 12px; }
.ocr-h {
  font-size: 12.5px; font-weight: 700; color: #ffffff; margin-bottom: 10px;
  display: flex; align-items: center; gap: 6px;
}
.ocr-h i { color: #60a5fa; }
.ocr-tools { margin-left: auto; display: inline-flex; gap: 4px; align-items: center; }
.ocr-cap, .ocr-cap-sm {
  background: #2563eb; color: #fff; border: 0;
  padding: 4px 10px; font-size: 11px; font-weight: 700;
  border-radius: 3px; cursor: pointer;
  display: inline-flex; align-items: center; gap: 4px;
}
.ocr-cap-sm { padding: 4px 7px; background: rgba(96,165,250,0.18); color: #93c5fd; }
.ocr-cap-sm:hover { background: rgba(96,165,250,0.32); color: #fff; }
.ocr-cap:hover { background: #1d4ed8; }
.ocr-cap.ocr-resume { background: #059669; }
.ocr-cap.ocr-resume:hover { background: #047857; }
.ocr-cap.ocr-auto { background: #7c3aed; }
.ocr-cap.ocr-auto:hover { background: #6d28d9; }
.ocr-cap:disabled, .ocr-cap-sm:disabled { opacity: 0.55; cursor: not-allowed; }
.spin { animation: ocrSpin 0.8s linear infinite; }
@keyframes ocrSpin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
.ocr-grid { display: grid; grid-template-columns: 200px 1fr; gap: 16px; align-items: center; }
.plate-snap {
  position: relative; background: #000; border-radius: 5px;
  aspect-ratio: 2/1; overflow: hidden;
  border: 2px solid #1a1a1a;
}
.plate-snap img { width: 100%; height: 100%; object-fit: cover; display: block; }
.plate-snap-ph {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  gap: 6px; color: rgba(255,255,255,0.5); font-size: 11px;
}
.snap-plate {
  position: absolute; bottom: 6px; left: 50%; transform: translateX(-50%);
  background: #fff; color: #000;
  font-family: "JetBrains Mono", monospace; font-weight: 800; font-size: 13px;
  padding: 2px 8px; border-radius: 2px;
  border: 1.5px solid #1a1a1a;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}
.ocr-lab { font-size: 11px; opacity: .65; }
.ocr-val { font-size: 22px; font-weight: 800; margin: 2px 0 6px; }
.ocr-conf { font-size: 11.5px; opacity: .8; }
.ocr-conf strong { color: #60a5fa; font-size: 13px; }
.verify-card h3 { margin-bottom: 10px; display: flex; align-items: center; gap: 6px; color: #0c1f40; }
.verify-card h3 i { color: #2563eb; }

/* 관제센터 출처 표시 */
.src-row {
  display: flex; align-items: center; gap: 10px;
  background: rgba(37,99,235,0.08);
  border: 1px solid rgba(37,99,235,0.25);
  border-radius: 5px; padding: 10px 14px; margin-bottom: 14px;
}
.src-row > i { color: #2563eb; font-size: 18px; }
.src-t { font-size: 13px; font-weight: 700; color: #0c1f40; }
.src-s { font-size: 11.5px; color: #4a5b78; font-family: "JetBrains Mono", monospace; margin-top: 2px; }

/* STEP 헤더 */
.vq-h {
  display: flex; align-items: center; gap: 8px;
  margin: 16px 0 8px;
  font-size: 13.5px; font-weight: 700; color: #0c1f40;
}
.vq-h.dim { opacity: 0.4; }
.vq-step {
  background: #2563eb; color: #fff;
  font-size: 11px; font-weight: 800; letter-spacing: 0.04em;
  padding: 3px 9px; border-radius: 3px;
}

/* 2차 검증 선택 (실제 과속 / 시스템 오류) */
.ver-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.vb {
  display: flex; align-items: center; gap: 10px;
  background: #ffffff;
  border: 2px solid #c9d4e3;
  border-radius: 6px; padding: 12px 14px;
  cursor: pointer; text-align: left;
  transition: border-color 0.15s, background 0.15s;
  color: #0c1f40;
}
.vb i { font-size: 22px; flex-shrink: 0; color: #6b7a92; }
.vb > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.vbt { font-size: 14px; font-weight: 800; color: #0c1f40; }
.vbs { font-size: 11.5px; color: #4a5b78; }
.vb:hover { border-color: #2563eb; }
.vb.on:nth-child(1) {
  background: rgba(16,185,129,0.10);
  border-color: #10b981;
}
.vb.on:nth-child(1) i { color: #059669; }
.vb.on:nth-child(2) {
  background: rgba(239,68,68,0.10);
  border-color: #ef4444;
}
.vb.on:nth-child(2) i { color: #dc2626; }

/* 최종 결정 */
.final-act { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.fa-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  padding: 12px; border-radius: 5px; border: 0; cursor: pointer;
  font-size: 13.5px; font-weight: 800;
}
.fa-btn:disabled {
  background: rgba(255,255,255,0.04) !important;
  color: rgba(228,238,255,0.3) !important;
  cursor: not-allowed;
}
.fa-btn i { font-size: 16px; }
.fa-btn.gr { background: #10b981; color: #fff; }
.fa-btn.gr:hover:not(:disabled) { background: #059669; }
.fa-btn.rd { background: #ef4444; color: #fff; }
.fa-btn.rd:hover:not(:disabled) { background: #dc2626; }

.memo.dim { opacity: 0.45; pointer-events: none; }
.memo .reason-sel:disabled, .memo textarea:disabled { cursor: not-allowed; }
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
