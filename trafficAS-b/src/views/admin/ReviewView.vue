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

<style scoped src="./ReviewView.css"></style>
