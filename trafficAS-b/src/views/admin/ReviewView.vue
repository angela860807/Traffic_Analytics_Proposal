<template>
  <div class="rev-shell">
    <header class="top">
      <RouterLink to="/" class="brand" title="홈으로">
        <img src="/TAS.png" alt="TAS" class="brand-img" />
      </RouterLink>
      <h1><a class="t-main" @click="goHome">단속관리팀</a></h1>
      <div class="t-right">
        <span class="hdr-time"><i class="bi bi-clock"></i> <strong>{{ lastUpdated || nowTime }}</strong></span>
        <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
          <span class="km-dot"></span>
          <span class="km-lab">자동 새로고침</span>
          <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
        </button>
        <div class="hdr-bell-wrap" @click.stop>
          <button class="hdr-bell" :class="{ critical: hasCritical, on: showAlerts }" @click="showAlerts = !showAlerts">
            <i class="bi bi-bell-fill"></i>
            <span v-if="liveAlerts.length" class="hdr-bell-c">{{ liveAlerts.length }}</span>
          </button>
          <div v-if="showAlerts" class="hdr-bell-pop" @click.stop>
            <div class="hbp-h">
              <i class="bi bi-exclamation-octagon-fill"></i>
              <strong>실시간 알림</strong>
              <span class="hbp-c">{{ liveAlerts.length }}건</span>
              <button class="hbp-x" @click="showAlerts = false"><i class="bi bi-x-lg"></i></button>
            </div>
            <div class="hbp-list">
              <div v-for="a in liveAlerts" :key="a.id" class="ac-row" :class="a.sev" @click="showAlerts = false">
                <div class="ac-sev"><i :class="a.icon"></i></div>
                <div class="ac-body">
                  <div class="ac-t">{{ a.title }}</div>
                  <div class="ac-d">{{ a.detail }}</div>
                  <div class="ac-meta">
                    <span class="ac-loc"><i class="bi bi-geo-alt"></i> {{ a.place }}</span>
                    <span class="ac-time">{{ a.time }}</span>
                  </div>
                </div>
              </div>
              <div v-if="!liveAlerts.length" class="ac-empty">활성 알림이 없습니다.</div>
            </div>
          </div>
        </div>
        <button class="km-toggle guide-btn-trigger" @click="guideOpen = true" title="사용자 가이드">
          <i class="bi bi-question-circle"></i>
          <span class="km-lab">가이드</span>
        </button>
        <DeptSwitcher />
        <div class="t-user"><i class="bi bi-person-circle"></i> 단속관리팀 매니저 <i class="bi bi-chevron-down"></i></div>
      </div>
    </header>

    <GuideOverlay v-model="guideOpen" :steps="guideSteps" />

    <!-- 본문 상단 툴바: KPI + 보고서 다운로드 -->
    <div class="rev-toolbar">
      <div class="hdr-kpi">
        <span class="kpi-chip bl" title="아직 최종 판정 전인 과속 후보"><i class="bi bi-hourglass-split"></i> 검토 대기 <strong>{{ waitCount }}</strong></span>
        <span class="kpi-chip gr" title="과속으로 최종 확정된 건"><i class="bi bi-check-circle-fill"></i> 과속 확정 <strong>{{ approveCount }}</strong></span>
        <span class="kpi-chip rd" title="검증 후 미과속으로 처리된 건"><i class="bi bi-x-circle-fill"></i> 미과속 <strong>{{ rejectCount }}</strong></span>
        <span class="kpi-chip bl" title="종결/보관 처리된 건"><i class="bi bi-archive-fill"></i> 종결 <strong>{{ closedCount }}</strong></span>
        <span class="kpi-chip pl" title="목록 내 OCR 평균 신뢰도"><span class="kc-ocr">OCR</span> <strong>{{ avgConfLabel }}</strong></span>
      </div>
      <div class="rev-dl">
        <button class="rev-dl-btn" @click="downloadDeptReport('review', 'daily', { date: reportDate })" title="오늘자 일일 단속 보고서"><i class="bi bi-download"></i> 일일</button>
        <button class="rev-dl-btn" @click="downloadDeptReport('review', 'weekly', { date: weekStart, endDate: reportDate })" title="오늘 기준 직전 7일 주간 단속 통계"><i class="bi bi-download"></i> 주간</button>
        <div class="rev-dl-range" v-if="rangeOpen" @click.stop>
          <span class="rev-dl-range-lab">기간 :</span>
          <input type="date" class="rev-dl-date" v-model="rangeStart" :max="rangeEnd" />
          <span class="rev-dl-range-sep">~</span>
          <input type="date" class="rev-dl-date" v-model="rangeEnd" :min="rangeStart" />
          <button class="rev-dl-btn ok" @click="downloadRangeReport" :disabled="!rangeStart || !rangeEnd" title="기간 보고서 다운로드">
            <i class="bi bi-download"></i> 받기
          </button>
        </div>
        <button class="rev-dl-btn alt" @click="rangeOpen = !rangeOpen" :class="{ on: rangeOpen }" title="기간 지정 다운로드">
          <i class="bi" :class="rangeOpen ? 'bi-x-lg' : 'bi-calendar-range'"></i>
          {{ rangeOpen ? '닫기' : '기간' }}
        </button>
      </div>
    </div>

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
            <tr v-if="isLoading">
              <td colspan="4" class="empty">과속 이벤트를 불러오는 중입니다.</td>
            </tr>
            <tr v-else-if="loadError">
              <td colspan="4" class="empty error">{{ loadError }}</td>
            </tr>
            <template v-else v-for="grp in groupedEvents" :key="grp.date">
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
                <td><span class="stat" :class="stTone(e)">{{ e.st }}</span></td>
              </tr>
            </template>
            <tr v-if="!isLoading && !loadError && !pagedEvents.length"><td colspan="4" class="empty">검색 결과가 없습니다.</td></tr>
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
            <i :class="selected.image ? 'bi bi-image-fill' : 'bi bi-image'"></i>
            {{ selected.image ? selected.imageName : '캡처 이미지 없음' }}
            <span v-if="selected.image" class="vi-fromctrl">CAPTURE</span>
          </div>

          <!-- 캡처 이미지 -->
          <div v-if="selected.image" class="vi-still">
            <img :src="selected.image" alt="관제센터 전송 이미지" @error="handleEvidenceImageError" />
            <div class="vi-ts">{{ selected.date || '' }} {{ selected.time }}</div>
          </div>
          <div v-else class="vi-empty">
            <i class="bi bi-image"></i>
            <span>저장된 캡처 이미지가 없습니다.</span>
          </div>
        </div>
        <div class="ocr-evt-row">
          <div class="ocr-section">
            <div class="ocr-h">
              <i class="bi bi-camera"></i> 차량 정보 (OCR)
            </div>
            <div class="ocr-grid">
              <div class="plate-snap">
                <img v-if="ocrSnapUrl" :src="ocrSnapUrl" alt="OCR 캡처" @error="handlePlateCropError" />
                <div v-else class="plate-snap-ph"><i class="bi bi-image"></i> Crop 이미지 없음</div>
              </div>
              <div>
                <div class="ocr-lab">인식 결과</div>
                <div class="ocr-val">{{ selected.plate }}</div>
                <div class="ocr-conf">OCR 신뢰도 <strong class="bl">{{ formatPercent(selected.conf) }}</strong></div>
              </div>
            </div>
          </div>

          <div class="evt-info">
            <div class="ei-h">이벤트 정보</div>
            <div class="ei-grid">
              <div class="ei-row"><span>발생 시간</span><strong>{{ selected.date }} {{ selected.time }}</strong></div>
              <div class="ei-row"><span>위반 내용</span><strong>{{ selected.type }}</strong></div>
              <div class="ei-row"><span>감지 속도</span><strong class="rd">{{ formatSpeed(selected.detectSpeed) }}</strong></div>
              <div class="ei-row"><span>제한 속도</span><strong>{{ formatSpeed(selected.limitSpeed) }}</strong></div>
              <div class="ei-row"><span>초과 속도</span><strong class="rd">{{ overSpeedText(selected) }}</strong></div>
            </div>
          </div>
        </div>

        <div class="mini-map">
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
          <button class="vb" :class="{ on: verification === 'valid' }" :disabled="isStep1Disabled" @click="setVerification('valid')">
            <i class="bi bi-check2-circle"></i>
            <div>
              <span class="vbt">실제 과속</span>
              <span class="vbs">영상·OCR 모두 일치, 단속 확정</span>
            </div>
          </button>
          <button class="vb" :class="{ on: verification === 'error' }" :disabled="isStep1Disabled" @click="setVerification('error')">
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
          <select class="reason-sel" v-model="reason" :disabled="isStep2Disabled">
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
          <textarea v-model="memo" placeholder="2차 검증 메모 (선택 사항)" maxlength="200" :disabled="isStep2Disabled"></textarea>
          <div class="memo-c">{{ memo.length }} / 200</div>
        </div>

        <div class="vq-h" :class="{ dim: !isStep3Ready }">
          <span class="vq-step">STEP 3</span>
          <strong>최종 결정</strong>
        </div>
        <div class="final-act final-act-4" :class="{ dim: !isStep3Ready }">
          <button class="fa-btn wn" :disabled="!canJudgeStatus('UNPROCESSED')" @click="judge('보류', 'UNPROCESSED')">
            <i class="bi bi-pause-circle-fill"></i> 보류 <span class="fa-code">UNPROCESSED</span>
          </button>
          <button class="fa-btn gr" :disabled="!canJudgeStatus('NOTIFIED')" @click="judge('과속 확정', 'NOTIFIED')">
            <i class="bi bi-check-circle-fill"></i> 과속 확정 <span class="fa-code">NOTIFIED</span>
          </button>
          <button class="fa-btn rd" :disabled="!canJudgeStatus('REJECTED')" @click="judge('미과속', 'REJECTED')">
            <i class="bi bi-x-circle-fill"></i> 미과속 <span class="fa-code">REJECTED</span>
          </button>
          <button class="fa-btn bl" :disabled="!canJudgeStatus('CLOSED')" @click="judge('종결/보관', 'CLOSED')">
            <i class="bi bi-archive-fill"></i> 종결/보관 <span class="fa-code">CLOSED</span>
          </button>
        </div>
        <div class="step-help" :class="{ warn: !isStep3Ready }">{{ finalDecisionHint }}</div>
        <div v-if="statusError" class="status-error">{{ statusError }}</div>

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
import GuideOverlay from "@/components/GuideOverlay.vue";
import guideSteps from "@/data/guides/review.js";

const guideOpen = ref(false);

/* ── 헤더 실시간 알림 ── */
const showAlerts = ref(false);
const liveAlerts = ref([
  { id: 1, sev: "critical", icon: "bi bi-speedometer2",          title: "신규 과속 후보 5건",         detail: "교통정보센터에서 일괄 전송됨 — 검토 대기 큐 추가",  place: "단속관리팀 큐",      time: "14:32" },
  { id: 2, sev: "serious",  icon: "bi bi-exclamation-octagon-fill", title: "OCR 신뢰도 임계 미만",       detail: "최근 3건의 OCR 신뢰도가 85% 미만 — 수동 확인 필요", place: "내부순환로 정릉",       time: "14:24" },
  { id: 3, sev: "caution",  icon: "bi bi-clock-history",          title: "처리 마감 임박",            detail: "검토 대기 7건 중 2건이 오늘 마감 시한 도래",         place: "단속관리팀 큐",         time: "13:50" },
  { id: 4, sev: "info",     icon: "bi bi-file-earmark-text",      title: "일일 보고서 자동 발행",      detail: "16:00 일일 단속 보고서가 자동 발행될 예정입니다",    place: "교통분석팀 · 경영본부", time: "13:00" },
]);
const hasCritical = computed(() => liveAlerts.value.some(a => a.sev === "critical"));
function closeAlertsOnOutside(e) {
  if (showAlerts.value && !e.target.closest(".hdr-bell-wrap")) showAlerts.value = false;
}
if (typeof document !== "undefined") {
  document.addEventListener("click", closeAlertsOnOutside);
}
import { listSpeedViolations, updateSpeedViolationStatus } from "@/api/speedViolations";
import { useReportDownload } from "@/composables/useReportDownload";
import { fmtDateTime } from "@/composables/useVideoUtils";
const { downloadDeptReport } = useReportDownload();

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

/* ── 기간 지정 다운로드 ── */
const rangeOpen = ref(false);
const rangeStart = ref(weekStart.value);
const rangeEnd = ref(reportDate.value);
function downloadRangeReport() {
  if (!rangeStart.value || !rangeEnd.value) return;
  const start = rangeStart.value <= rangeEnd.value ? rangeStart.value : rangeEnd.value;
  const end = rangeStart.value <= rangeEnd.value ? rangeEnd.value : rangeStart.value;
  /* 기간이 7일 초과면 weekly 템플릿, 이내면 daily 템플릿 사용 */
  const diff = (new Date(end) - new Date(start)) / 86400000;
  const reportKey = diff >= 6 ? "weekly" : "daily";
  downloadDeptReport("review", reportKey, { date: start, endDate: end });
  rangeOpen.value = false;
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/+$/, "");
const FASTAPI_BASE_URL = (import.meta.env.VITE_FASTAPI_BASE_URL || "").replace(/\/+$/, "");
const REVIEW_SPEED_LIMIT_KMH = 70;
const STATUS_LABELS = {
  UNPROCESSED: "보류",
  NOTIFIED: "과속 확정",
  REJECTED: "미과속",
  CLOSED: "종결/보관",
};

const speedEvents = ref([]);
const isLoading = ref(false);
const isUpdatingStatus = ref(false);
const loadError = ref("");
const statusError = ref("");
const lastUpdated = ref("");

const allEvents = computed(() => speedEvents.value);

function asNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function splitDateTime(value) {
  if (!value) return { date: "—", time: "—" };
  const raw = String(value);
  const [date, rest = ""] = raw.split("T");
  return {
    date: date || "—",
    time: rest.slice(0, 8) || "—",
  };
}

function buildImageSrc(path) {
  if (!path) return "";
  const value = String(path);
  if (/^(https?:|data:|blob:)/.test(value)) return value;
  if (value.startsWith("/")) return API_BASE_URL ? `${API_BASE_URL}${value}` : value;
  return API_BASE_URL ? `${API_BASE_URL}/${value}` : `/${value}`;
}

function toDatePath(date) {
  if (!date || date === "—") return "";
  return date.replaceAll("-", "/");
}

function basename(path) {
  return String(path || "").replaceAll("\\", "/").split("/").pop() || "";
}

function normalizeDetectionPath(path, date) {
  if (!path) return "";
  const value = String(path).trim().replaceAll("\\", "/");
  if (/^(https?:|data:|blob:)/.test(value)) return value;

  const withoutLeadingSlash = value.replace(/^\/+/, "");
  if (withoutLeadingSlash.startsWith("static/detections/")) {
    return `/${withoutLeadingSlash}`;
  }
  if (withoutLeadingSlash.startsWith("storage/detections/")) {
    return `/${withoutLeadingSlash.replace(/^storage\/detections/, "static/detections")}`;
  }
  if (withoutLeadingSlash.startsWith("detections/")) {
    return `/static/${withoutLeadingSlash}`;
  }
  if (!withoutLeadingSlash.includes("/")) {
    const datePath = toDatePath(date);
    return datePath ? `/static/detections/${datePath}/${withoutLeadingSlash}` : `/${withoutLeadingSlash}`;
  }
  return value.startsWith("/") ? value : `/${value}`;
}

function buildDetectionImageSrc(path, date) {
  const normalized = normalizeDetectionPath(path, date);
  if (!normalized) return "";
  if (/^(https?:|data:|blob:)/.test(normalized)) return normalized;
  if (normalized.startsWith("/static/detections")) {
    return FASTAPI_BASE_URL ? `${FASTAPI_BASE_URL}${normalized}` : normalized;
  }
  return buildImageSrc(normalized);
}

function derivePlateCropPath(path) {
  if (!path) return "";
  const value = String(path).trim();
  if (/_plate_crop\./i.test(value)) return value;
  if (/_frame\./i.test(value)) return value.replace(/_frame(\.[^.]+)$/i, "_plate_crop$1");
  const dotIndex = value.lastIndexOf(".");
  if (dotIndex < 0) return "";
  return `${value.slice(0, dotIndex)}_plate_crop${value.slice(dotIndex)}`;
}

function imageNameFromPath(path) {
  return basename(path) || "N/A";
}

function isOverSpeed(measuredSpeed, speedLimit) {
  const measured = asNumber(measuredSpeed);
  const limit = asNumber(speedLimit);
  return measured !== null && limit !== null && measured > limit;
}

function displayViolationStatus(row, measuredSpeed, speedLimit) {
  if (row.violationStatus === "UNPROCESSED" && row.reviewedManually && row.latestReviewStatus === "UNPROCESSED") {
    return STATUS_LABELS.UNPROCESSED;
  }
  if (row.violationStatus === "UNPROCESSED") {
    if (isOverSpeed(measuredSpeed, speedLimit)) return "과속";
    const measured = asNumber(measuredSpeed);
    const limit = asNumber(speedLimit);
    if (measured !== null && limit !== null) return "미과속";
  }
  return STATUS_LABELS[row.violationStatus] || row.violationStatus || "보류";
}

function mapSpeedViolation(row) {
  const occurred = splitDateTime(row.violatedAt || row.createdAt);
  const measuredSpeed = asNumber(row.measuredSpeed);
  const speedLimit = REVIEW_SPEED_LIMIT_KMH;
  const imagePath = row.violationImageUrl || row.violationImagePath || "";
  const plateCropPath = row.plateCropImageUrl || row.plateCropImagePath || derivePlateCropPath(imagePath);
  return {
    id: row.violationId,
    violationId: row.violationId,
    flowEventId: row.flowEventId,
    evtId: row.flowEventId ? `FLOW-${row.flowEventId}` : `SV-${row.violationId}`,
    time: occurred.time,
    date: occurred.date,
    place: row.cameraName || "카메라 미지정",
    type: "속도 위반",
    typeTone: "tg-rd",
    plate: row.plateNumber || "미인식",
    conf: row.confidenceScore ?? null,
    st: displayViolationStatus(row, measuredSpeed, speedLimit),
    stCode: row.violationStatus || "UNPROCESSED",
    reviewedManually: Boolean(row.reviewedManually),
    latestReviewStatus: row.latestReviewStatus || "",
    latestReviewReason: row.latestReviewReason || "",
    latestReviewMemo: row.latestReviewMemo || "",
    latestReviewedBy: row.latestReviewedBy || "",
    latestReviewedAt: row.latestReviewedAt || "",
    detectSpeed: measuredSpeed,
    limitSpeed: speedLimit,
    camera: row.cameraName || (row.cameraId ? `CAM-${row.cameraId}` : "미지정"),
    cameraId: row.cameraId,
    vehicleId: row.vehicleId,
    lane: null,
    image: buildDetectionImageSrc(imagePath, occurred.date),
    imagePath: row.violationImagePath || "",
    imageName: imageNameFromPath(imagePath),
    plateCropImage: buildDetectionImageSrc(plateCropPath, occurred.date),
    plateCropPath,
    plateCropName: imageNameFromPath(plateCropPath),
    source: "spring",
    raw: row,
  };
}

function selectedDateRange() {
  return {
    start: `${reportDate.value}T00:00:00`,
    end: `${reportDate.value}T23:59:59`,
  };
}

function getErrorMessage(error) {
  return error?.response?.data?.message || error?.message || "요청 처리 중 오류가 발생했습니다.";
}

async function loadSpeedViolationEvents({ silent = false } = {}) {
  if (!silent) isLoading.value = true;
  loadError.value = "";
  try {
    const rows = await listSpeedViolations(selectedDateRange());
    speedEvents.value = rows.map(mapSpeedViolation);
    lastUpdated.value = fmtDateTime();
    if (selected.value) {
      selected.value = speedEvents.value.find((e) => e.id === selected.value.id) || null;
    }
  } catch (error) {
    console.warn("[ReviewView] failed to load speed violations", error);
    speedEvents.value = [];
    lastUpdated.value = fmtDateTime();
  } finally {
    if (!silent) isLoading.value = false;
  }
}

function formatSpeed(value) {
  const n = asNumber(value);
  return n === null ? "—" : `${n.toFixed(1)} km/h`;
}

function formatPercent(value) {
  const n = asNumber(value);
  return n === null ? "N/A" : `${(n * 100).toFixed(1)}%`;
}

function overSpeedText(event) {
  const measured = asNumber(event?.detectSpeed);
  const limit = asNumber(event?.limitSpeed);
  if (measured === null || limit === null) return "—";
  const diff = measured - limit;
  return `${diff >= 0 ? "+" : ""}${diff.toFixed(1)} km/h`;
}

const filterType = ref("all");
const query = ref("");
const page = ref(1);
const perPage = 8;
const selected = ref(null);
const memo = ref("");

const ocrSnapUrl = ref("");

watch(() => selected.value?.id, (id) => {
  ocrSnapUrl.value = "";
  if (!id) return;
  if (selected.value?.plateCropImage) {
    ocrSnapUrl.value = selected.value.plateCropImage;
    return;
  }
});

function handleEvidenceImageError() {
  if (!selected.value) return;
  selected.value.image = "";
}

function handlePlateCropError() {
  if (!selected.value) return;
  ocrSnapUrl.value = "";
  selected.value.plateCropImage = "";
  selected.value.plateCropName = "";
}

// 실시간 시계
const nowTime = ref("");
let timeTimer = null;
let refreshTimer = null;
onMounted(() => {
  nowTime.value = fmtDateTime();
  timeTimer = setInterval(() => { nowTime.value = fmtDateTime(); }, 1000);
  loadSpeedViolationEvents();
  refreshTimer = setInterval(() => {
    if (autoRefresh.value) loadSpeedViolationEvents({ silent: true });
  }, 30000);
});
onBeforeUnmount(() => {
  if (timeTimer) clearInterval(timeTimer);
  if (refreshTimer) clearInterval(refreshTimer);
});
const reason = ref("");
const history = ref([]);
const auditLog = ref([
  { at: "2024-05-16 14:32:25", user: "단속관리팀", role: "단속관리팀", action: "검토 대기 등록", result: "-", resultTone: "wait", note: "이벤트 검토 대기 상태로 등록" },
  { at: "2024-05-16 14:32:18", user: "시스템",       role: "시스템",     action: "이벤트 생성",     result: "성공", resultTone: "ok",   note: "이벤트 발생 및 OCR 처리 완료" },
]);

const approveCount = computed(() => allEvents.value.filter((e) => e.stCode === "NOTIFIED").length);
const rejectCount  = computed(() => allEvents.value.filter((e) => e.stCode === "REJECTED").length);
const closedCount  = computed(() => allEvents.value.filter((e) => e.stCode === "CLOSED").length);

// 2차 검증 상태: 'valid' (실제 과속) | 'error' (시스템 오류) | ''
const verification = ref("");
const selectedStatus = computed(() => selected.value?.stCode || "");
const hasReason = computed(() => reason.value.trim().length > 0);
const isStep1Disabled = computed(() => isUpdatingStatus.value || selectedStatus.value === "CLOSED");
const isStep2Disabled = computed(() => isStep1Disabled.value || !verification.value);
const isStep3Ready = computed(() => !isStep2Disabled.value && hasReason.value);

const finalDecisionHint = computed(() => {
  if (selectedStatus.value === "CLOSED") return "이미 종결/보관된 건입니다.";
  if (!verification.value) return "STEP 1에서 검증 결과를 먼저 선택해 주세요.";
  if (!hasReason.value) return "STEP 2에서 사유를 선택해야 최종 결정이 가능합니다.";
  if (verification.value === "valid") return "실제 과속 검증에서는 과속 확정만 활성화됩니다.";
  if (verification.value === "error") return "시스템 오류 검증에서는 보류, 미과속, 종결/보관을 선택할 수 있습니다.";
  return "";
});

function setVerification(next) {
  if (isStep1Disabled.value) return;
  if (verification.value !== next) {
    reason.value = "";
    memo.value = "";
  }
  verification.value = next;
  statusError.value = "";
}

function canJudgeStatus(code) {
  if (!selected.value || isUpdatingStatus.value || selectedStatus.value === "CLOSED") return false;
  if (code === "CLOSED" && selectedStatus.value === "NOTIFIED") return true;
  if (!isStep3Ready.value) return false;
  if (verification.value === "error") return ["UNPROCESSED", "REJECTED", "CLOSED"].includes(code);
  if (code === selectedStatus.value) return false;
  if (code === "NOTIFIED") return verification.value === "valid";
  return false;
}

// 필터 칩 카운트
const countAll = computed(() => allEvents.value.length);
const countSpeed = computed(() => allEvents.value.filter((e) => e.type === "속도 위반").length);
const countOcr = computed(() => allEvents.value.filter((e) => e.type === "OCR 인식").length);

const stTone = (eventOrStatus) => {
  const event = typeof eventOrStatus === "object" ? eventOrStatus : null;
  const status = event?.stCode || eventOrStatus;
  if (status === "NOTIFIED" || status === "과속 확정" || status === "승인") return "ok";
  if (status === "REJECTED" || status === "미과속" || status === "반려" || status === "오탐") return "no";
  if (status === "CLOSED" || status === "종결/보관") return "closed";
  if (event?.st === STATUS_LABELS.UNPROCESSED) return "wait";
  if (event && isOverSpeed(event.detectSpeed, event.limitSpeed)) return "no";
  return "wait";
};

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase();
  return allEvents.value.filter(e => {
    if (filterType.value !== "all" && e.type !== filterType.value) return false;
    if (!q) return true;
    return e.place.toLowerCase().includes(q) || e.plate.toLowerCase().includes(q);
  });
});

watch([filterType, query], () => {
  page.value = 1;
});

watch(reportDate, () => {
  page.value = 1;
  selected.value = null;
  loadSpeedViolationEvents();
});

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage)));
const pageTotal = computed(() => totalPages.value);
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
  return allEvents.value.filter(e => e.stCode === "UNPROCESSED").length;
});
const avgConfLabel = computed(() => {
  const values = allEvents.value
    .map((e) => asNumber(e.conf))
    .filter((value) => value !== null);
  if (!values.length) return "N/A";
  const sum = values.reduce((s, value) => s + value, 0);
  return `${Math.round((sum / values.length) * 100)}%`;
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
  memo.value = "";
  verification.value = "";
  reason.value = "";
  statusError.value = "";
}

const nowStr = () => fmtDateTime();

const VERDICT_TONE = {
  "보류": "wait",
  "과속 확정": "ok",
  "미과속": "no",
  "종결/보관": "wait",
};
async function judge(verdict, code) {
  if (!canJudgeStatus(code)) return;
  const target = allEvents.value.find(x => x.id === selected.value.id);
  if (!target?.violationId) return;
  isUpdatingStatus.value = true;
  statusError.value = "";
  let updatedTarget = target;
  try {
    const updated = await updateSpeedViolationStatus(target.violationId, code, {
      reason: reason.value,
      memo: memo.value,
      reviewer: "단속관리팀",
    });
    updatedTarget = mapSpeedViolation(updated);
    const index = speedEvents.value.findIndex((e) => e.id === updatedTarget.id);
    if (index >= 0) speedEvents.value.splice(index, 1, updatedTarget);
    selected.value = updatedTarget;
    lastUpdated.value = fmtDateTime();
  } catch (error) {
    statusError.value = getErrorMessage(error);
    auditLog.value.unshift({
      at: nowStr(), user: "단속관리팀", role: "단속관리팀",
      action: `검토 ${verdict} (${code})`, result: "실패", resultTone: "no",
      note: `${target.evtId} → ${statusError.value}`,
    });
    return;
  } finally {
    isUpdatingStatus.value = false;
  }
  history.value.unshift({
    at: nowStr(), evtId: updatedTarget.evtId, type: updatedTarget.type, typeTone: updatedTarget.typeTone,
    plate: updatedTarget.plate, verdict,
    verdictTone: VERDICT_TONE[verdict] || "wait",
    by: "단속관리팀", note: memo.value || reason.value || "-",
  });
  auditLog.value.unshift({
    at: nowStr(), user: "단속관리팀", role: "단속관리팀",
    action: `검토 ${verdict} (${code})`, result: "성공", resultTone: "ok",
    note: `${updatedTarget.evtId} → ${code}${reason.value ? ` (${reason.value})` : ""}`,
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
