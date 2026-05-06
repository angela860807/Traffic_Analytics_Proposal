<template>
  <div class="theme-navy" :class="{ light: !isDark }">
    <AppNav
      design="navy"
      @goChat="
        page = 'support';
        tab = 'chat';
      "
    />
    <AppFab />

    <main class="content">
      <!-- ① 사용법 -->
      <template v-if="page === 'usage'">
        <div class="ph">
          <div class="ph-ey">GUIDE</div>
          <h1>📖 <em>사용법</em></h1>
          <p class="ph-sub">TrafficAS 주요 기능의 단계별 사용 안내입니다.</p>
        </div>
        <div class="pb">
          <div class="steps">
            <div class="step" v-for="(s, i) in usageSteps" :key="i">
              <div class="step-n">0{{ i + 1 }}</div>
              <div>
                <div class="step-t">{{ s.title }}</div>
                <div class="step-d">{{ s.desc }}</div>
                <pre class="code" v-if="s.code">{{ s.code }}</pre>
              </div>
            </div>
          </div>
          <div class="divider"></div>
          <h3 class="sh">자주 묻는 질문</h3>
          <div class="faq-list">
            <div
              class="faq-item"
              v-for="(f, i) in faq"
              :key="f.q"
              @click="openFaq = openFaq === i ? null : i"
            >
              <div class="faq-q">
                <span class="faq-tag">FAQ</span>
                <span class="faq-text">{{ f.q }}</span>
                <svg
                  class="faq-arr"
                  :class="{ open: openFaq === i }"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </div>
              <div class="faq-a" :class="{ open: openFaq === i }">
                <div class="faq-a-inner">{{ f.a }}</div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ② 시스템 소개 -->
      <template v-if="page === 'intro'">
        <div class="ph">
          <div class="ph-ey">SYSTEM</div>
          <h1>🖥️ 시스템 <em>소개</em></h1>
          <p class="ph-sub">기술 아키텍처 및 DB 구조를 설명합니다.</p>
        </div>
        <div class="pb">
          <h3 class="sh">시스템 아키텍처</h3>
          <div class="cg">
            <div class="card" v-for="c in archCards" :key="c.tag">
              <div class="ctag">{{ c.tag }}</div>
              <div class="ctitle">{{ c.title }}</div>
              <div class="cdesc">{{ c.desc }}</div>
            </div>
          </div>
          <div class="divider"></div>
          <h3 class="sh">DB 테이블 구조</h3>
          <div class="dbg">
            <div class="dbc" v-for="d in dbTables" :key="d.tbl">
              <div class="db-badge">{{ d.tbl }}</div>
              <div class="db-name">{{ d.name }}</div>
              <div class="db-desc">{{ d.desc }}</div>
              <div class="db-cols">
                <span class="col" v-for="c in d.cols" :key="c">{{ c }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ③ 고객 지원 -->
      <template v-if="page === 'support'">
        <div class="ph">
          <div class="ph-ey">SUPPORT</div>
          <h1>고객 <em>지원</em></h1>
          <p class="ph-sub">게시판, Q&A, 실시간 채팅으로 도움을 드립니다.</p>
        </div>
        <div class="tabs">
          <div class="tab" :class="{ on: tab === 'board' }" @click="tab = 'board'">
            게시판 <span class="tc">6</span>
          </div>
          <div class="tab" :class="{ on: tab === 'qna' }" @click="tab = 'qna'">
            Q&amp;A <span class="tc">5</span>
          </div>
          <div class="tab" :class="{ on: tab === 'chat' }" @click="tab = 'chat'">
            실시간 채팅 <span class="tc live">Live</span>
          </div>
        </div>
        <div class="tab-body">
          <BoardTab v-if="tab === 'board'" />
          <QnaTab v-if="tab === 'qna'" />
          <ChatTab v-if="tab === 'chat'" />
        </div>
      </template>
    </main>

    <footer>
      <span class="fl">Traffic<em>AS</em></span>
      <span class="fr">© 2025 네바퀴 1조 · 스마트 모빌리티 DX Academy</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute } from "vue-router";
import AppNav from "@/components/AppNav.vue";
import AppFab from "@/components/AppFab.vue";
import BoardTab from "@/components/BoardTab.vue";
import QnaTab from "@/components/QnaTab.vue";
import ChatTab from "@/components/ChatTab.vue";
import { useTheme } from "@/composables/useTheme";

const { isDark } = useTheme();
const route = useRoute();

const page = ref("usage");
const tab = ref("board");
const openFaq = ref(null);

const applyHash = () => {
  const hash = route.hash.replace("#", "");
  if (["usage", "intro", "support"].includes(hash)) page.value = hash;
  if (route.query.tab) tab.value = route.query.tab;
};

onMounted(applyHash);
watch(() => route.hash, applyHash);

const usageSteps = [
  {
    title: "로그인 및 계정 설정",
    desc: "관리자 계정으로 로그인한 뒤 프로필 설정과 알림 수신 여부를 구성합니다.",
    code: null,
  },
  {
    title: "카메라 등록 및 구역 설정",
    desc:
      "설정 > 카메라 관리에서 RTSP 주소를 입력해 카메라를 추가하고, 구역(Zone)과 IN/OUT 방향을 지정합니다.",
    code: "RTSP 예시: rtsp://192.168.0.100:554/stream1",
  },
  {
    title: "실시간 모니터링",
    desc:
      "메인 대시보드에서 등록된 카메라의 실시간 차량 감지 현황과 번호판 인식 결과를 확인합니다.",
    code: null,
  },
  {
    title: "통계 및 리포트 조회",
    desc:
      "통계 탭에서 구역별 유입·유출 집계와 시간대별 교통 흐름 분석 리포트를 조회합니다.",
    code: null,
  },
];

const faq = [
  {
    q: "대시보드 메인 화면은 어디서 볼 수 있나요?",
    a:
      "로그인 후 상단 내비게이션의 '대시보드' 메뉴를 클릭하면 실시간 감지 현황 화면으로 이동합니다.",
  },
  {
    q: "번호판 인식 결과는 어디서 확인하나요?",
    a:
      "대시보드 하단 감지 로그 패널에서 인식된 번호판, 신뢰도, 감지 시각을 실시간으로 확인할 수 있습니다.",
  },
  {
    q: "구역별 통계는 어떻게 조회하나요?",
    a:
      "통계 탭 > 구역별 현황에서 날짜와 구역을 선택하면 유입·유출 집계와 시간대별 차트를 볼 수 있습니다.",
  },
  {
    q: "카메라를 추가로 등록하려면?",
    a:
      "설정 > 카메라 관리에서 '카메라 추가' 버튼을 클릭하고 RTSP 주소와 연결할 구역을 입력하면 됩니다.",
  },
  {
    q: "번호판 인식률이 낮게 나와요.",
    a:
      "카메라 해상도를 1080p 이상으로 설정하고, 야간에는 적외선 조명 보조 장치를 사용하면 인식률이 향상됩니다.",
  },
];

const archCards = [
  {
    tag: "FRONTEND",
    title: "Vue.js 3",
    desc: "Composition API, Pinia, Chart.js 기반 반응형 대시보드.",
  },
  {
    tag: "BACKEND API",
    title: "Spring Boot",
    desc: "REST API, JWT 인증, JPA/Hibernate, PostgreSQL 연동.",
  },
  {
    tag: "AI SERVER",
    title: "FastAPI",
    desc: "YOLOv8 추론, WebSocket 스트리밍, EasyOCR 번호판 인식.",
  },
  {
    tag: "DATABASE",
    title: "PostgreSQL",
    desc: "6개 테이블 논리 구조, 인덱스 최적화, 집계 캐시.",
  },
];

const dbTables = [
  {
    tbl: "zones",
    name: "구역 관리",
    desc: "입구·출구·내부통로·주차라인 논리 구역 정의.",
    cols: ["zone_id", "name", "direction_type"],
  },
  {
    tbl: "cameras",
    name: "카메라 관리",
    desc: "카메라와 Zone 연결. IN/OUT 판정 보조.",
    cols: ["camera_id", "zone_id", "direction_type", "status"],
  },
  {
    tbl: "vehicles",
    name: "차량 마스터",
    desc: "번호판 기준 엔티티. 최초 생성·반복 업데이트.",
    cols: ["vehicle_id", "plate_number", "vehicle_type", "last_seen"],
  },
  {
    tbl: "detection_logs",
    name: "원본 감지 로그",
    desc: "AI 감지 데이터 원본 보관.",
    cols: ["log_id", "vehicle_id", "camera_id", "confidence", "created_at"],
  },
  {
    tbl: "vehicle_flow_events",
    name: "이동 이벤트",
    desc: "정제된 IN/OUT 이벤트. 분석용 핵심 테이블.",
    cols: ["event_id", "vehicle_id", "zone_id", "event_type", "event_time"],
  },
  {
    tbl: "hourly_traffic_stats",
    name: "시간별 집계",
    desc: "대시보드 빠른 조회용 집계 캐시.",
    cols: ["stat_id", "zone_id", "stat_hour", "in_count", "out_count"],
  },
];
</script>

<style scoped>
/* LAYOUT */
.content {
  padding-top: 62px;
  min-height: 100vh;
}

/* PAGE HEADER */
.ph {
  padding: 44px 48px 32px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
}
.ph-ey {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.2em;
  color: var(--a);
  opacity: 0.62;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ph-ey::before {
  content: "";
  width: 12px;
  height: 1px;
  background: var(--a);
  opacity: 0.5;
}
h1 {
  font-family: "Syne", sans-serif;
  font-size: clamp(22px, 3vw, 38px);
  font-weight: 800;
  letter-spacing: -1.5px;
  color: var(--t);
}
h1 em {
  color: var(--a);
  font-style: normal;
}
.ph-sub {
  font-size: 13px;
  color: var(--t2);
  font-weight: 300;
  line-height: 1.8;
  margin-top: 7px;
}

/* PAGE BODY */
.pb {
  padding: 36px 48px;
}
.sh {
  font-family: "Syne", sans-serif;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.4px;
  color: var(--t);
  margin-bottom: 16px;
}
.divider {
  height: 1px;
  background: var(--b);
  margin: 28px 0;
}

/* CARDS */
.cg {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 12px;
  margin-bottom: 28px;
}
.card {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 7px;
  padding: 20px 18px;
  transition: all 0.22s;
}
.card:hover {
  border-color: var(--ba);
  transform: translateY(-2px);
}
.ctag {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--a);
  opacity: 0.55;
  margin-bottom: 7px;
}
.ctitle {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--t);
}
.cdesc {
  font-size: 12px;
  color: var(--t2);
  line-height: 1.7;
  font-weight: 300;
}

/* STEPS */
.steps {
  display: flex;
  flex-direction: column;
  margin-bottom: 28px;
}
.step {
  display: flex;
  gap: 20px;
  padding: 22px 0;
  border-bottom: 1px solid var(--b);
}
.step:last-child {
  border-bottom: none;
}
.step-n {
  font-family: "Syne", sans-serif;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -2px;
  color: rgba(96, 165, 250, 0.1);
  line-height: 1;
  flex-shrink: 0;
  width: 50px;
}
.step-t {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--t);
}
.step-d {
  font-size: 13px;
  color: var(--t2);
  line-height: 1.75;
  font-weight: 300;
}
.code {
  background: var(--bg2);
  border: 1px solid var(--b);
  border-radius: 5px;
  padding: 12px 14px;
  margin-top: 10px;
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px;
  color: var(--a);
  line-height: 1.8;
  overflow-x: auto;
  white-space: pre;
}

/* DB */
.dbg {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}
.dbc {
  background: var(--card);
  border: 1px solid var(--b);
  border-radius: 7px;
  padding: 18px 20px;
  transition: border-color 0.22s;
}
.dbc:hover {
  border-color: var(--ba);
}
.db-badge {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  letter-spacing: 0.1em;
  color: var(--a);
  background: rgba(96, 165, 250, 0.08);
  border: 1px solid rgba(96, 165, 250, 0.18);
  border-radius: 3px;
  padding: 2px 8px;
  display: inline-block;
  margin-bottom: 8px;
}
.db-name {
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 4px;
  color: var(--t);
}
.db-desc {
  font-size: 11px;
  color: var(--t2);
  line-height: 1.65;
  font-weight: 300;
  margin-bottom: 9px;
}
.db-cols {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
}
.col {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  color: var(--t3);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--b);
  border-radius: 3px;
  padding: 2px 6px;
}

/* FAQ ACCORDION */
.faq-list {
  border: 1px solid var(--b);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 28px;
}
.faq-item {
  border-bottom: 1px solid var(--b);
  cursor: pointer;
  user-select: none;
}
.faq-item:last-child {
  border-bottom: none;
}
.faq-item:hover {
  background: rgba(255, 255, 255, 0.02);
}
.faq-q {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
}
.faq-tag {
  font-family: "IBM Plex Mono", monospace;
  font-size: 8px;
  letter-spacing: 0.1em;
  color: var(--a);
  background: rgba(96, 165, 250, 0.1);
  border: 1px solid rgba(96, 165, 250, 0.2);
  border-radius: 3px;
  padding: 2px 6px;
  flex-shrink: 0;
}
.faq-text {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: var(--t);
}
.faq-arr {
  flex-shrink: 0;
  color: var(--t3);
  transition: transform 0.25s ease;
}
.faq-arr.open {
  transform: rotate(180deg);
}
.faq-a {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
}
.faq-a.open {
  max-height: 120px;
}
.faq-a-inner {
  padding: 0 18px 14px 56px;
  font-size: 12px;
  color: var(--t2);
  line-height: 1.75;
  font-weight: 300;
}

/* SUPPORT TABS */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
  padding: 0 48px;
}
.tab {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 14px 16px;
  font-size: 13px;
  color: var(--t3);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}
.tab:hover {
  color: var(--t);
}
.tab.on {
  color: var(--a);
  border-bottom-color: var(--a);
}
.tc {
  font-family: "IBM Plex Mono", monospace;
  font-size: 9px;
  background: rgba(96, 165, 250, 0.12);
  color: var(--a);
  padding: 1px 6px;
  border-radius: 100px;
}
.tc.live {
  background: rgba(52, 211, 153, 0.15);
  color: var(--in);
}
.tab-body {
  padding: 36px 48px;
}

footer {
  border-top: 1px solid var(--b);
  padding: 26px 60px;
  background: var(--bg2);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.fl {
  font-family: "Syne", sans-serif;
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.3px;
  color: var(--t);
}
.fl em {
  color: var(--a);
  font-style: normal;
}
.fr {
  font-family: "IBM Plex Mono", monospace;
  font-size: 10px;
  color: var(--t3);
}

@media (max-width: 768px) {
  .ph,
  .pb,
  .tab-body {
    padding-left: 20px;
    padding-right: 20px;
  }
  .tabs {
    padding: 0 20px;
  }
  .dbg {
    grid-template-columns: 1fr;
  }
}
</style>
