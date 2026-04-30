<template>
  <div class="theme-navy" :class="{light:!isDark}">
    <AppNav design="navy" @goChat="page='support'; tab='chat'" />
    <AppFab />

    <main class="content">

      <!-- ① 사용법 -->
      <template v-if="page==='usage'">
        <div class="ph">
          <div class="ph-ey">GUIDE</div>
          <h1>📖 <em>사용법</em></h1>
          <p class="ph-sub">단계별 설치 및 실행 안내입니다.</p>
        </div>
        <div class="pb">
          <div class="steps">
            <div class="step" v-for="(s,i) in usageSteps" :key="i">
              <div class="step-n">0{{ i+1 }}</div>
              <div>
                <div class="step-t">{{ s.title }}</div>
                <div class="step-d">{{ s.desc }}</div>
                <pre class="code" v-if="s.code">{{ s.code }}</pre>
              </div>
            </div>
          </div>
          <div class="divider"></div>
          <h3 class="sh">자주 묻는 질문</h3>
          <div class="cg">
            <div class="card" v-for="f in faq" :key="f.q">
              <div class="ctag">FAQ</div>
              <div class="ctitle">{{ f.q }}</div>
              <div class="cdesc">{{ f.a }}</div>
            </div>
          </div>
        </div>
      </template>

      <!-- ② 시스템 소개 -->
      <template v-if="page==='intro'">
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
      <template v-if="page==='support'">
        <div class="ph">
          <div class="ph-ey">SUPPORT</div>
          <h1>🎧 고객 <em>지원</em></h1>
          <p class="ph-sub">게시판, Q&A, 실시간 채팅으로 도움을 드립니다.</p>
        </div>
        <div class="tabs">
          <div class="tab" :class="{on:tab==='board'}" @click="tab='board'">
            📋 게시판 <span class="tc">6</span>
          </div>
          <div class="tab" :class="{on:tab==='qna'}" @click="tab='qna'">
            ❓ Q&amp;A <span class="tc">5</span>
          </div>
          <div class="tab" :class="{on:tab==='chat'}" @click="tab='chat'">
            💬 실시간 채팅 <span class="tc live">Live</span>
          </div>
        </div>
        <div class="tab-body">
          <BoardTab v-if="tab==='board'" />
          <QnaTab   v-if="tab==='qna'"   />
          <ChatTab  v-if="tab==='chat'"  />
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
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppNav   from '@/components/AppNav.vue'
import AppFab   from '@/components/AppFab.vue'
import BoardTab from '@/components/BoardTab.vue'
import QnaTab   from '@/components/QnaTab.vue'
import ChatTab  from '@/components/ChatTab.vue'
import { useTheme } from '@/composables/useTheme'

const { isDark } = useTheme()
const route = useRoute()

const page = ref('usage')
const tab  = ref('board')

const applyHash = () => {
  const hash = route.hash.replace('#', '')
  if (['usage','intro','support'].includes(hash)) page.value = hash
  if (route.query.tab) tab.value = route.query.tab
}

onMounted(applyHash)
watch(() => route.hash, applyHash)

const usageSteps = [
  {
    title: '저장소 클론 및 환경 설정',
    desc: 'Python 3.10+, Node.js 18+, PostgreSQL 15+ 필요.',
    code: 'git clone https://github.com/team/traffic-as.git\ncd traffic-as && cp .env.example .env',
  },
  {
    title: 'FastAPI AI 서버 실행',
    desc: 'YOLO 모델과 EasyOCR 엔진이 포함된 AI 서버를 실행합니다.',
    code: 'cd ai-server\npip install -r requirements.txt\nuvicorn main:app --reload --port 8000',
  },
  {
    title: 'Spring Boot API 서버 실행',
    desc: 'REST API, JWT 인증, PostgreSQL 연동 서버를 실행합니다.',
    code: 'cd api-server && ./mvnw spring-boot:run',
  },
  {
    title: 'Vue.js 프론트엔드 실행',
    desc: '대시보드를 실행하고 http://localhost:5173 에서 접속합니다.',
    code: 'cd frontend && npm install && npm run dev',
  },
]

const faq = [
  { q: '카메라가 인식되지 않아요',   a: 'RTSP URL 형식 확인: rtsp://ip:port/stream' },
  { q: '번호판 인식률이 낮아요',      a: '카메라 해상도를 1080p 이상으로 설정하세요.' },
  { q: 'WebSocket 연결이 끊겨요',     a: '방화벽에서 8000번 포트를 열어주세요.' },
  { q: 'DB 마이그레이션 방법은?',     a: './mvnw flyway:migrate 명령어로 실행하세요.' },
]

const archCards = [
  { tag: 'FRONTEND',    title: 'Vue.js 3',    desc: 'Composition API, Pinia, Chart.js 기반 반응형 대시보드.' },
  { tag: 'BACKEND API', title: 'Spring Boot', desc: 'REST API, JWT 인증, JPA/Hibernate, PostgreSQL 연동.' },
  { tag: 'AI SERVER',   title: 'FastAPI',     desc: 'YOLOv8 추론, WebSocket 스트리밍, EasyOCR 번호판 인식.' },
  { tag: 'DATABASE',    title: 'PostgreSQL',  desc: '6개 테이블 논리 구조, 인덱스 최적화, 집계 캐시.' },
]

const dbTables = [
  { tbl: 'zones',                name: '구역 관리',      desc: '입구·출구·내부통로·주차라인 논리 구역 정의.',   cols: ['zone_id','name','direction_type'] },
  { tbl: 'cameras',              name: '카메라 관리',    desc: '카메라와 Zone 연결. IN/OUT 판정 보조.',         cols: ['camera_id','zone_id','direction_type','status'] },
  { tbl: 'vehicles',             name: '차량 마스터',    desc: '번호판 기준 엔티티. 최초 생성·반복 업데이트.',   cols: ['vehicle_id','plate_number','vehicle_type','last_seen'] },
  { tbl: 'detection_logs',       name: '원본 감지 로그', desc: 'AI 감지 데이터 원본 보관.',                     cols: ['log_id','vehicle_id','camera_id','confidence','created_at'] },
  { tbl: 'vehicle_flow_events',  name: '이동 이벤트',   desc: '정제된 IN/OUT 이벤트. 분석용 핵심 테이블.',      cols: ['event_id','vehicle_id','zone_id','event_type','event_time'] },
  { tbl: 'hourly_traffic_stats', name: '시간별 집계',   desc: '대시보드 빠른 조회용 집계 캐시.',               cols: ['stat_id','zone_id','stat_hour','in_count','out_count'] },
]
</script>

<style scoped>
/* LAYOUT */
.content { padding-top: 62px; min-height: 100vh; }

/* PAGE HEADER */
.ph { padding: 44px 48px 32px; border-bottom: 1px solid var(--b); background: var(--bg2); }
.ph-ey {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: .2em; color: var(--a); opacity: .62;
  margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
}
.ph-ey::before { content: ''; width: 12px; height: 1px; background: var(--a); opacity: .5; }
h1 { font-family: 'Syne', sans-serif; font-size: clamp(22px, 3vw, 38px); font-weight: 800; letter-spacing: -1.5px; color: var(--t); }
h1 em { color: var(--a); font-style: normal; }
.ph-sub { font-size: 13px; color: var(--t2); font-weight: 300; line-height: 1.8; margin-top: 7px; }

/* PAGE BODY */
.pb { padding: 36px 48px; }
.sh { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: -.4px; color: var(--t); margin-bottom: 16px; }
.divider { height: 1px; background: var(--b); margin: 28px 0; }

/* CARDS */
.cg  { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; margin-bottom: 28px; }
.card { background: var(--card); border: 1px solid var(--b); border-radius: 7px; padding: 20px 18px; transition: all .22s; }
.card:hover { border-color: var(--ba); transform: translateY(-2px); }
.ctag   { font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: .12em; color: var(--a); opacity: .55; margin-bottom: 7px; }
.ctitle { font-size: 14px; font-weight: 600; margin-bottom: 6px; color: var(--t); }
.cdesc  { font-size: 12px; color: var(--t2); line-height: 1.7; font-weight: 300; }

/* STEPS */
.steps { display: flex; flex-direction: column; margin-bottom: 28px; }
.step  { display: flex; gap: 20px; padding: 22px 0; border-bottom: 1px solid var(--b); }
.step:last-child { border-bottom: none; }
.step-n { font-family: 'Syne', sans-serif; font-size: 36px; font-weight: 800; letter-spacing: -2px; color: rgba(96,165,250,.1); line-height: 1; flex-shrink: 0; width: 50px; }
.step-t { font-size: 15px; font-weight: 600; margin-bottom: 6px; color: var(--t); }
.step-d { font-size: 13px; color: var(--t2); line-height: 1.75; font-weight: 300; }
.code   { background: var(--bg2); border: 1px solid var(--b); border-radius: 5px; padding: 12px 14px; margin-top: 10px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--a); line-height: 1.8; overflow-x: auto; white-space: pre; }

/* DB */
.dbg { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 28px; }
.dbc { background: var(--card); border: 1px solid var(--b); border-radius: 7px; padding: 18px 20px; transition: border-color .22s; }
.dbc:hover { border-color: var(--ba); }
.db-badge { font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: .1em; color: var(--a); background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.18); border-radius: 3px; padding: 2px 8px; display: inline-block; margin-bottom: 8px; }
.db-name  { font-size: 13px; font-weight: 700; margin-bottom: 4px; color: var(--t); }
.db-desc  { font-size: 11px; color: var(--t2); line-height: 1.65; font-weight: 300; margin-bottom: 9px; }
.db-cols  { display: flex; flex-wrap: wrap; gap: 3px; }
.col      { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--t3); background: rgba(255,255,255,.03); border: 1px solid var(--b); border-radius: 3px; padding: 2px 6px; }

/* SUPPORT TABS */
.tabs { display: flex; border-bottom: 1px solid var(--b); background: var(--bg2); padding: 0 48px; }
.tab  { display: flex; align-items: center; gap: 7px; padding: 14px 16px; font-size: 13px; color: var(--t3); cursor: pointer; border-bottom: 2px solid transparent; transition: all .2s; white-space: nowrap; }
.tab:hover { color: var(--t); }
.tab.on    { color: var(--a); border-bottom-color: var(--a); }
.tc  { font-family: 'IBM Plex Mono', monospace; font-size: 9px; background: rgba(96,165,250,.12); color: var(--a); padding: 1px 6px; border-radius: 100px; }
.tc.live { background: rgba(52,211,153,.15); color: var(--in); }
.tab-body { padding: 36px 48px; }

footer { border-top: 1px solid var(--b); padding: 26px 60px; background: var(--bg2); display: flex; align-items: center; justify-content: space-between; }
.fl { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; letter-spacing: -.3px; color: var(--t); }
.fl em { color: var(--a); font-style: normal; }
.fr { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--t3); }

@media (max-width: 768px) {
  .ph, .pb, .tab-body { padding-left: 20px; padding-right: 20px; }
  .tabs { padding: 0 20px; }
  .dbg { grid-template-columns: 1fr; }
}
</style>
