<template>
  <div class="theme-navy" :class="{light:!isDark}">
    <AppNav />
    <AppFab />

    <main class="content">

      <!-- 히어로 -->
      <div class="ph">
        <div class="ph-ey">INSTALLATION GUIDE</div>
        <h1>설치 <em>가이드</em></h1>
        <p class="ph-sub">4단계만 따라하면 TrafficAS 전체 스택이 로컬에서 동작합니다.</p>
        <div class="ph-badges">
          <span class="badge">Python 3.10+</span>
          <span class="badge">Node.js 18+</span>
          <span class="badge">PostgreSQL 15+</span>
          <span class="badge">Java 17+</span>
        </div>
      </div>

      <!-- 콘텐츠 -->
      <div class="body-wrap">
        <div class="main-col">

          <!-- 설치 단계 -->
          <section
            class="step-section"
            v-for="(s,i) in steps" :key="i"
          >
            <div class="step-aside">
              <div class="step-big-n">{{ String(i+1).padStart(2,'0') }}</div>
              <div class="step-vline"></div>
            </div>
            <div class="step-body">
              <div class="step-meta">
                <span class="step-tag">{{ s.tag }}</span>
                <span class="step-idx">STEP {{ String(i+1).padStart(2,'0') }} / 04</span>
              </div>
              <h2 class="step-title">{{ s.title }}</h2>
              <p class="step-desc">{{ s.desc }}</p>
              <div class="terminal">
                <div class="term-bar">
                  <div class="tdots"><i></i><i></i><i></i></div>
                  <span class="tlang">{{ s.lang }}</span>
                  <button class="tcopy" @click="copy(s.code, i)" :class="{ok: copiedIdx===i}">
                    {{ copiedIdx===i ? '✓ 복사됨' : '복사' }}
                  </button>
                </div>
                <pre class="tcode"><span
                  v-for="(line,li) in s.code.split('\n')" :key="li"
                  class="tline"
                ><span class="tprompt">$</span>{{ line }}</span></pre>
              </div>
            </div>
          </section>

          <!-- 기술 스택 -->
          <section class="ref-section">
            <div class="ref-label">TECH STACK</div>
            <h2 class="ref-title">개발 및 운영 환경</h2>
            <div class="arch-grid">
              <div class="arch-card" v-for="n in arch" :key="n.name" :style="{'--nc': n.color}">
                <div class="arch-top">
                  <div class="arch-stack">
                    <span class="arch-tech" v-for="t in n.tech" :key="t">{{ t }}</span>
                  </div>
                  <div class="arch-dot" :style="{background: n.color}"></div>
                </div>
                <div class="arch-name">{{ n.name }}</div>
                <div class="arch-role">{{ n.role }}</div>
              </div>
            </div>
          </section>

          <!-- FAQ -->
          <section class="ref-section" id="faq">
            <div class="ref-label">TROUBLESHOOTING</div>
            <h2 class="ref-title">자주 묻는 질문</h2>
            <div class="faq-list">
              <div
                class="faq-item"
                v-for="(f,i) in faq" :key="i"
                :class="{open: openFaq===i}"
                @click="openFaq = openFaq===i ? null : i"
              >
                <div class="faq-q">
                  <span class="faq-n">{{ String(i+1).padStart(2,'0') }}</span>
                  <span class="faq-text">{{ f.q }}</span>
                  <span class="faq-ic">{{ openFaq===i ? '−' : '+' }}</span>
                </div>
                <Transition name="slide">
                  <div class="faq-a" v-if="openFaq===i">{{ f.a }}</div>
                </Transition>
              </div>
            </div>
          </section>

        </div>
      </div>

    </main>

    <footer>
      <span class="fl">Traffic<em>AS</em></span>
      <span class="fr">© 2025 네바퀴 1조 · 스마트 모빌리티 DX Academy</span>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppNav from '@/components/AppNav.vue'
import AppFab from '@/components/AppFab.vue'
import { useTheme } from '@/composables/useTheme'

const { isDark }  = useTheme()
const copiedIdx   = ref(null)
const openFaq     = ref(null)

const copy = (text, idx) => {
  navigator.clipboard.writeText(text)
  copiedIdx.value = idx
  setTimeout(() => { copiedIdx.value = null }, 2000)
}

const steps = [
  {
    tag: 'CLONE & ENV', lang: 'bash', shortTitle: '환경 설정',
    title: '저장소 클론 및 환경 설정',
    desc: 'Python 3.10+, Node.js 18+, PostgreSQL 15+ 환경이 필요합니다. 저장소를 클론한 뒤 .env 파일을 복사해 데이터베이스 접속 정보를 입력하세요.',
    code: 'git clone https://github.com/team/traffic-as.git\ncd traffic-as && cp .env.example .env',
  },
  {
    tag: 'AI SERVER', lang: 'bash', shortTitle: 'AI 서버',
    title: 'FastAPI AI 서버 실행',
    desc: 'YOLOv8n 모델과 EasyOCR 엔진이 포함된 AI 추론 서버입니다. 첫 실행 시 모델 가중치 파일 다운로드로 수 분이 소요될 수 있습니다.',
    code: 'cd ai-server\npip install -r requirements.txt\nuvicorn main:app --reload --port 8000',
  },
  {
    tag: 'API SERVER', lang: 'bash', shortTitle: 'API 서버',
    title: 'Spring Boot API 서버 실행',
    desc: 'JWT 인증, 데이터 처리, 흐름 분석, REST API를 제공하는 백엔드 서버입니다. 첫 실행 시 Flyway로 DB 마이그레이션이 자동 수행됩니다.',
    code: 'cd api-server && ./mvnw spring-boot:run',
  },
  {
    tag: 'FRONTEND', lang: 'bash', shortTitle: '프론트엔드',
    title: 'Vue.js 프론트엔드 실행',
    desc: '실시간 모니터링 대시보드입니다. 의존성 설치 후 개발 서버를 실행하면 http://localhost:5173 에서 확인할 수 있습니다.',
    code: 'cd frontend && npm install && npm run dev',
  },
]

const arch = [
  { name: 'AI 서버',     tech: ['Python','FastAPI'],   role: 'YOLO 차량 탐지 + OCR 번호판 인식', color: '#34d399' },
  { name: '백엔드 서버', tech: ['Java','Spring Boot'], role: '데이터 처리, 흐름 분석, REST API',  color: '#60a5fa' },
  { name: '데이터베이스', tech: ['PostgreSQL'],         role: '감지 로그, 흐름 데이터, 통계 저장', color: '#fb923c' },
  { name: '프론트엔드',  tech: ['Vue.js','Nginx'],     role: '실시간 대시보드 및 관리 UI',         color: '#a78bfa' },
]

const faq = [
  { q: '카메라가 인식되지 않아요',  a: 'RTSP URL 형식을 확인하세요. 올바른 형식: rtsp://ip:port/stream' },
  { q: '번호판 인식률이 낮아요',    a: '카메라 해상도를 1080p 이상으로 설정하고 충분한 조도를 확보하세요.' },
  { q: 'WebSocket 연결이 끊겨요',   a: '방화벽에서 8000번 포트를 허용하고 CORS 설정을 확인하세요.' },
  { q: 'DB 마이그레이션 방법은?',   a: 'api-server 디렉터리에서 ./mvnw flyway:migrate 명령어를 실행하세요.' },
  { q: 'YOLO 모델 교체 방법은?',   a: 'ai-server/models 디렉터리에 .pt 파일을 교체한 뒤 서버를 재시작하세요.' },
]
</script>

<style scoped>
.content { padding-top: 62px; min-height: 100vh; }

/* ── 히어로 ── */
.ph {
  padding: 64px 60px 52px;
  border-bottom: 1px solid var(--b);
  background: var(--bg2);
}
.ph-ey {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px; letter-spacing: .22em;
  color: var(--a); opacity: .6;
  margin-bottom: 10px;
  display: flex; align-items: center; gap: 8px;
}
.ph-ey::before {
  content: ''; width: 14px; height: 1px;
  background: var(--a); opacity: .5;
}
h1 {
  font-family: 'Syne', sans-serif;
  font-size: clamp(36px, 5vw, 68px); font-weight: 800;
  letter-spacing: -3px; color: var(--t); line-height: .95; margin-bottom: 16px;
}
h1 em { color: var(--a); font-style: normal; }
.ph-sub {
  font-size: 13px; color: var(--t2); font-weight: 300;
  line-height: 1.85; max-width: 600px; margin-bottom: 20px; margin-top: 16px;
}
.ph-badges { display: flex; gap: 6px; flex-wrap: wrap; }
.badge {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--t3); border: 1px solid var(--b); border-radius: 100px;
  padding: 4px 12px; letter-spacing: .04em;
}

/* ── 바디 레이아웃 ── */
.body-wrap { max-width: 1400px; margin: 0 auto; }
.main-col { padding: 0; }

/* ── 스텝 섹션 ── */
.step-section {
  display: flex; gap: 0;
  padding: 56px 60px; border-bottom: 1px solid var(--b);
  scroll-margin-top: 80px;
}
.step-aside {
  display: flex; flex-direction: column; align-items: center;
  flex-shrink: 0; padding-right: 32px; padding-top: 4px;
}
.step-big-n {
  font-family: 'Syne', sans-serif; font-size: 52px; font-weight: 800;
  letter-spacing: -3px; color: var(--a); opacity: .12; line-height: 1;
  user-select: none; writing-mode: horizontal-tb;
}
.step-vline {
  flex: 1; width: 1px; background: linear-gradient(to bottom, var(--a), transparent);
  opacity: .12; margin-top: 8px;
}
.step-body { flex: 1; min-width: 0; }
.step-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }
.step-tag {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px; letter-spacing: .12em;
  color: var(--a); background: rgba(96,165,250,.08);
  border: 1px solid rgba(96,165,250,.2); border-radius: 4px; padding: 3px 10px;
}
.step-idx {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: .1em; color: var(--t3);
}
.step-title {
  font-family: 'Syne', sans-serif; font-size: clamp(18px, 2vw, 26px);
  font-weight: 800; letter-spacing: -.6px; color: var(--t); margin-bottom: 12px;
}
.step-desc {
  font-size: 13px; color: var(--t2); line-height: 1.85;
  font-weight: 300; margin-bottom: 20px; max-width: 580px;
}

/* ── 터미널 ── */
.terminal { border: 1px solid var(--b); border-radius: 8px; overflow: hidden; max-width: 600px; }
.term-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 9px 14px; background: rgba(255,255,255,.03); border-bottom: 1px solid var(--b);
}
.tdots { display: flex; gap: 5px; }
.tdots i { display: block; width: 10px; height: 10px; border-radius: 50%; }
.tdots i:nth-child(1) { background: #ff5f57; }
.tdots i:nth-child(2) { background: #febc2e; }
.tdots i:nth-child(3) { background: #28c840; }
.tlang { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--t3); letter-spacing: .08em; flex: 1; }
.tcopy {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--t3);
  background: none; border: 1px solid var(--b); border-radius: 4px;
  padding: 3px 10px; cursor: pointer; transition: all .18s;
}
.tcopy:hover { border-color: var(--ba); color: var(--a); }
.tcopy.ok { border-color: #34d399; color: #34d399; }
.tcode {
  padding: 16px 18px; font-family: 'IBM Plex Mono', monospace;
  font-size: 12px; line-height: 2; background: var(--bg);
  display: flex; flex-direction: column;
}
.tline { display: block; color: var(--t2); }
.tprompt { color: var(--a); opacity: .4; margin-right: 10px; user-select: none; }

/* ── 레퍼런스 섹션 (기술스택, FAQ) ── */
.ref-section {
  padding: 56px 60px; border-bottom: 1px solid var(--b);
  scroll-margin-top: 80px;
}
.ref-label {
  font-family: 'IBM Plex Mono', monospace; font-size: 9px;
  letter-spacing: .2em; color: var(--a); opacity: .55;
  margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
}
.ref-label::before { content: ''; width: 12px; height: 1px; background: var(--a); opacity: .5; }
.ref-title {
  font-family: 'Syne', sans-serif; font-size: 22px;
  font-weight: 800; letter-spacing: -.5px; color: var(--t); margin-bottom: 28px;
}

/* 기술 스택 카드 */
.arch-grid {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
}
.arch-card {
  border: 1px solid var(--b); border-radius: 10px;
  padding: 22px 20px; background: var(--card);
  position: relative; overflow: hidden; transition: all .22s;
}
.arch-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: var(--nc);
}
.arch-card:hover { border-color: var(--nc); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,.12); }
.arch-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 12px; }
.arch-stack { display: flex; gap: 4px; flex-wrap: wrap; }
.arch-tech {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px; letter-spacing: .04em;
  color: var(--nc); background: rgba(255,255,255,.04);
  border: 1px solid rgba(255,255,255,.06); border-radius: 3px; padding: 2px 8px;
}
.arch-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 3px;
  box-shadow: 0 0 8px currentColor;
}
.arch-name { font-size: 14px; font-weight: 700; color: var(--t); margin-bottom: 6px; }
.arch-role { font-size: 12px; color: var(--t2); line-height: 1.6; font-weight: 300; }

/* FAQ */
.faq-list { border: 1px solid var(--b); border-radius: 8px; overflow: hidden; }
.faq-item { border-bottom: 1px solid var(--b); cursor: pointer; transition: background .15s; }
.faq-item:last-child { border-bottom: none; }
.faq-item:hover { background: rgba(96,165,250,.025); }
.faq-item.open { background: rgba(96,165,250,.04); }
.faq-q { display: flex; align-items: center; gap: 16px; padding: 18px 20px; user-select: none; }
.faq-n {
  font-family: 'IBM Plex Mono', monospace; font-size: 10px;
  color: var(--a); opacity: .4; flex-shrink: 0;
}
.faq-text { flex: 1; font-size: 13px; font-weight: 500; color: var(--t); }
.faq-item.open .faq-text { color: var(--a); }
.faq-ic { font-size: 16px; color: var(--t3); line-height: 1; flex-shrink: 0; }
.faq-item.open .faq-ic { color: var(--a); }
.faq-a { padding: 0 20px 18px 52px; font-size: 13px; color: var(--t2); line-height: 1.8; font-weight: 300; }
.slide-enter-active, .slide-leave-active { transition: opacity .15s, transform .15s; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-5px); }

/* ── 푸터 ── */
footer {
  border-top: 1px solid var(--b); padding: 26px 60px;
  background: var(--bg2); display: flex; align-items: center; justify-content: space-between;
}
.fl { font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 800; letter-spacing: -.3px; color: var(--t); }
.fl em { color: var(--a); font-style: normal; }
.fr { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--t3); }

@media (max-width: 900px) {
  .hero { flex-direction: column; align-items: flex-start; }
  .hero-stat-col { border-left: none; border-top: 1px solid var(--b); padding-left: 0; padding-top: 20px; flex-direction: row; flex-wrap: wrap; gap: 24px; }
  .arch-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .hero, .step-section, .ref-section { padding-left: 20px; padding-right: 20px; }
  .arch-grid { grid-template-columns: 1fr; }
  footer { padding-left: 20px; padding-right: 20px; }
}
</style>
