<template>
  <div class="admin-shell">
    <aside class="side">
      <RouterLink to="/" class="brand">
        <span class="dot"></span> Traffic <em>AS</em>
      </RouterLink>
      <nav class="snav">
        <button v-for="n in nav" :key="n.id" class="snav-i"
          :class="{ on: tab === n.id }" @click="tab = n.id">
          <i :class="n.icon"></i>{{ n.label }}
        </button>
      </nav>
      <div class="side-kpi">
        <div class="sk-h">상태 요약 <em>(오늘)</em></div>
        <div v-for="k in sideKpis" :key="k.label" class="sk-i" :class="k.tone">
          <div class="sk-top">
            <span class="sk-l">{{ k.label }}</span>
            <span class="sk-d" :class="k.deltaTone">{{ k.delta }}</span>
          </div>
          <div class="sk-v">{{ k.value }}<small>{{ k.unit }}</small></div>
          <div class="sk-bar"><span :style="{ width: k.bar + '%' }" :class="k.tone"></span></div>
        </div>
        <div class="sk-foot"><i class="bi bi-arrow-clockwise"></i> 10:30 갱신</div>
      </div>
    </aside>

    <div class="main">
      <header class="top">
        <h1><a class="t-main" @click="goHome">운영기획팀</a></h1>
        <div class="t-right">
          <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>10:30:00</strong></span>
          <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
            <span class="km-dot"></span>
            <span class="km-lab">자동 새로고침</span>
            <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
          </button>
          <DeptSwitcher />
          <div class="t-user"><i class="bi bi-person-circle"></i> 운영기획팀 매니저 <i class="bi bi-chevron-down"></i></div>
        </div>
      </header>

      <template v-if="tab === 'ops'">
      <section class="row2">
        <div class="card big">
          <div class="card-h">
            <h3>성과 개요 <span class="seg-sub">(최근 7일)</span></h3>
            <span class="hdr-ts">업데이트 10:30 <i class="bi bi-arrow-clockwise"></i></span>
          </div>
          <div class="ctrl-row">
            <div class="tabs">
              <button class="tab" :class="{ on: perfTab === 'congest' }" @click="perfTab = 'congest'">혼잡 관리 성과</button>
              <button class="tab" :class="{ on: perfTab === 'speed' }" @click="perfTab = 'speed'">속도 이상 처리율</button>
              <button class="tab" :class="{ on: perfTab === 'event' }" @click="perfTab = 'event'">이벤트 처리 현황</button>
            </div>
            <div class="period-sel">
              <button v-for="p in periods" :key="p.id" class="ps" :class="{ on: period === p.id }" @click="period = p.id">{{ p.label }}</button>
            </div>
          </div>
          <div class="legend"><span class="lg-dot bl"></span> 성과(%) <span class="lg-dot gr"></span> 목표(90%) <span class="lg-dot or"></span> 미달</div>
          <div class="bars" @mouseleave="hoverBar = -1">
            <div v-for="(d, i) in trendData" :key="d.day" class="bcol"
              @mouseenter="hoverBar = i" tabindex="0"
              :aria-label="`${d.day} 성과 ${d.value}%, 목표 ${d.target}%`">
              <div class="bnum">{{ d.value }}%</div>
              <div class="bwrap" :class="{ on: hoverBar === i, miss: d.value < d.target }">
                <div class="bbar" :style="{ height: d.value + '%' }"></div>
                <div class="bline" :style="{ bottom: d.target + '%' }"></div>
                <div v-if="hoverBar === i" class="b-tip" role="tooltip">
                  <strong>{{ d.value }}%</strong>
                  <span>목표 {{ d.target }}%</span>
                  <span class="b-delta" :class="d.value >= d.target ? 'up' : 'dn'">
                    {{ d.value >= d.target ? '▲' : '▼' }} {{ Math.abs(d.value - d.target) }}%p
                  </span>
                </div>
              </div>
              <div class="bday">{{ d.day }}</div>
            </div>
          </div>
          <div class="perf-stats">
            <div class="ps-i"><span class="ps-l">평균</span><strong class="ps-v">93.4%</strong></div>
            <div class="ps-i"><span class="ps-l">최고</span><strong class="ps-v gr">96%</strong><em class="ps-e">5/13 (화)</em></div>
            <div class="ps-i"><span class="ps-l">최저</span><strong class="ps-v or">90%</strong><em class="ps-e">5/11 (일)</em></div>
            <div class="ps-i"><span class="ps-l">목표 달성</span><strong class="ps-v">6 / 7일</strong><em class="ps-e gr">85.7%</em></div>
            <div class="ps-i"><span class="ps-l">전주 대비</span><strong class="ps-v gr">▲ 2.1%p</strong></div>
          </div>
        </div>

        <div class="card mid">
          <div class="card-h">
            <h3>이벤트 처리 현황 <span class="seg-sub">(오늘)</span></h3>
          </div>
          <div class="evt-body">
            <div class="donut-wrap">
              <svg viewBox="0 0 120 120" class="donut">
                <circle cx="60" cy="60" r="48" fill="none" stroke="#1d2c44" stroke-width="18"/>
                <circle cx="60" cy="60" r="48" fill="none" stroke="#3b82f6" stroke-width="18"
                  stroke-dasharray="243.5 301.6" stroke-dashoffset="0" transform="rotate(-90 60 60)"/>
                <circle cx="60" cy="60" r="48" fill="none" stroke="#f59e0b" stroke-width="18"
                  stroke-dasharray="15 301.6" stroke-dashoffset="-243.5" transform="rotate(-90 60 60)"/>
                <circle cx="60" cy="60" r="48" fill="none" stroke="#ef4444" stroke-width="18"
                  stroke-dasharray="42 301.6" stroke-dashoffset="-258.5" transform="rotate(-90 60 60)"/>
              </svg>
              <div class="donut-c">
                <div class="dc-lab">전체</div>
                <div class="dc-val">128<span class="dc-u">건</span></div>
              </div>
            </div>
            <div class="donut-legend compact">
              <div><span class="lg-dot bl"></span> 정상 <strong>103</strong><em>81%</em></div>
              <div><span class="lg-dot yl"></span> 지연 <strong>7</strong><em>5%</em></div>
              <div><span class="lg-dot rd"></span> 미처리 <strong>18</strong><em>14%</em></div>
            </div>
          </div>
          <div class="evt-meta-row">
            <span><i class="bi bi-clock"></i> 평균 <strong>8:32</strong></span>
            <span><i class="bi bi-exclamation-circle"></i> 최장 <strong class="rd">24분</strong></span>
            <span><i class="bi bi-check2-circle"></i> SLA <strong class="gr">86%</strong></span>
          </div>
          <div class="evt-types">
            <div class="et-i"><span class="et-tag bl">사고</span><span class="et-bar"><span style="width:42%;background:#2563eb"></span></span><strong>54</strong></div>
            <div class="et-i"><span class="et-tag or">혼잡</span><span class="et-bar"><span style="width:30%;background:#b45309"></span></span><strong>38</strong></div>
            <div class="et-i"><span class="et-tag rd">속도</span><span class="et-bar"><span style="width:18%;background:#dc2626"></span></span><strong>23</strong></div>
            <div class="et-i"><span class="et-tag pl">OCR</span><span class="et-bar"><span style="width:10%;background:#7c3aed"></span></span><strong>13</strong></div>
          </div>
        </div>

        <div class="card mid risk">
          <div class="card-h">
            <h3>리스크 요약 <span class="seg-sub">(오늘)</span></h3>
            <div class="rsk-cnts">
              <span class="rsk-c high">높음 1</span>
              <span class="rsk-c med">보통 1</span>
              <span class="rsk-c low">낮음 1</span>
            </div>
          </div>
          <div v-for="r in risks" :key="r.title" class="rk" :class="r.sev">
            <span class="rk-bar" :class="r.sev"></span>
            <div class="rk-body">
              <div class="rk-top">
                <span class="rk-sev-tag" :class="r.sev">{{ r.sevLabel }}</span>
                <span class="rk-t">{{ r.title }}</span>
                <span class="rk-cnt">{{ r.count }}</span>
              </div>
              <div class="rk-d">{{ r.detail }} · <em>{{ r.owner }} · {{ r.due }}</em></div>
              <div class="rk-bot">
                <span class="rk-sb"><span :style="{ width: r.score + '%' }" :class="r.sev"></span></span>
                <strong class="rk-num">{{ r.score }}</strong>
                <span class="rk-act">{{ r.action }}</span>
              </div>
            </div>
          </div>
          <button class="rk-more">전체 리스크 보기 <i class="bi bi-chevron-right"></i></button>
        </div>
      </section>

      </template>

      <template v-if="tab === 'reports' || tab === 'ops'">
      <section class="row3">
        <div class="card">
          <div class="card-h">
            <h3>부서별 성과 비교 <span class="seg-sub">(오늘)</span></h3>
          </div>
          <table class="tbl-dept">
            <thead>
              <tr>
                <th>부서</th><th>혼잡 관리 성과</th><th>속도 이상 처리율</th>
                <th>OCR 인식 성공률</th><th>카메라 정상 가동률</th><th>미처리 이벤트</th><th>등급</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="d in depts" :key="d.name">
                <td class="dn">{{ d.name }}</td>
                <td>{{ d.v1 }} <span :class="d.t1">{{ d.d1 }}</span></td>
                <td>{{ d.v2 }} <span :class="d.t2">{{ d.d2 }}</span></td>
                <td>{{ d.v3 }} <span :class="d.t3">{{ d.d3 }}</span></td>
                <td>{{ d.v4 }} <span :class="d.t4">{{ d.d4 }}</span></td>
                <td>{{ d.v5 }} <span :class="d.t5">{{ d.d5 }}</span></td>
                <td><span class="grade" :class="d.gradeTone">{{ d.grade }}</span></td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td class="dn">평균</td>
                <td>93.8%</td><td>96.5%</td><td>95.5%</td><td>98.0%</td><td>9건</td>
                <td><span class="grade A">A</span></td>
              </tr>
            </tfoot>
          </table>

          <div class="steps inline compact">
            <span class="steps-h">운영 절차</span>
            <div class="steps-row">
              <template v-for="(s, i) in steps" :key="i">
                <span class="step"><b>{{ i + 1 }}.</b> {{ s.t }}</span>
                <i v-if="i < 3" class="bi bi-chevron-right step-arrow"></i>
              </template>
            </div>
          </div>
        </div>

        <div class="card report-card">
          <div class="card-h">
            <h3>보고서 생성</h3>
            <label class="auto-pub"><input type="checkbox" v-model="autoPublish" /> 자동 발행</label>
          </div>
          <div class="rep-grid">
            <div v-for="r in reportTypes" :key="r.t" class="rep">
              <div class="rep-h"><i class="bi bi-calendar3"></i> {{ r.t }}</div>
              <div class="rep-d">{{ r.desc }}</div>
              <div class="rep-date">{{ r.date }}</div>
              <button class="rep-btn">생성</button>
            </div>
          </div>
          <div class="rep-actions">
            <button class="btn-pri"><i class="bi bi-download"></i> 보고서 다운로드</button>
            <button class="btn-sec"><i class="bi bi-bar-chart"></i> 주간 요약</button>
            <button class="btn-sec"><i class="bi bi-list-ul"></i> 이슈 보기</button>
          </div>
          <div class="recent-rep">
            <div class="rr-h">
              <span>최근 발행 <em class="rr-cnt">{{ recentReports.length }}</em></span>
              <a class="rr-all" href="#">전체 보기 <i class="bi bi-chevron-right"></i></a>
            </div>
            <div class="rr-list">
              <div v-for="r in recentReports.slice(0, 2)" :key="r.t" class="rr-i">
                <div class="rr-i-l">
                  <span class="rr-t">{{ r.t }}</span>
                  <span class="rr-meta">{{ r.date }} · {{ r.by }} · {{ r.size }}</span>
                </div>
                <span class="rr-views"><i class="bi bi-eye"></i> {{ r.views }}</span>
                <span class="rr-st" :class="r.tone">{{ r.st }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      </template>

      <section v-if="tab === 'events'" class="card panel">
        <h3>이벤트 <span class="seg-sub">최근 이벤트 목록</span></h3>
        <table class="tbl-dept">
          <thead><tr><th>시간</th><th>구간</th><th>유형</th><th>상태</th></tr></thead>
          <tbody>
            <tr v-for="e in eventsList" :key="e.id">
              <td class="dn">{{ e.time }}</td><td>{{ e.line }}</td><td>{{ e.type }}</td>
              <td><span :class="e.tone">{{ e.st }}</span></td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'stats'" class="card panel">
        <h3>통계 <span class="seg-sub">7일간 추이</span></h3>
        <div class="legend"><span class="lg-dot bl"></span> 처리 건수</div>
        <div class="bars">
          <div v-for="d in statsBars" :key="d.day" class="bcol">
            <div class="bnum">{{ d.value }}</div>
            <div class="bwrap"><div class="bbar" :style="{ height: (d.value / 200 * 100) + '%' }"></div></div>
            <div class="bday">{{ d.day }}</div>
          </div>
        </div>
      </section>

      <section v-if="tab === 'settings'" class="card panel">
        <h3>설정 <span class="seg-sub">대시보드 환경</span></h3>
        <div class="set-row"><label>알림 수신</label><input type="checkbox" v-model="setAlert" /></div>
        <div class="set-row"><label>자동 새로고침 (초)</label><input type="number" v-model.number="setRefresh" min="5" max="300" /></div>
        <div class="set-row"><label>기본 부서</label>
          <select v-model="setDept"><option>전체</option><option>교통정보센터</option><option>단속관리팀</option><option>교통분석팀</option><option>시설운영팀</option></select>
        </div>
        <button class="btn-pri" @click="saveSettings"><i class="bi bi-check2"></i> 저장</button>
        <div v-if="setMsg" class="set-msg">{{ setMsg }}</div>
      </section>


      <footer class="foot">Traffic AS · 운영성과 보고 v2.0.0</footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";

const tab = ref("ops");
const autoRefresh = ref(true);
function goHome() {
  tab.value = "ops";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const hoverBar = ref(-1);

const eventsList = [
  { id: 1, time: "14:32:18", line: "강변북로 (구리 → 한남)", type: "교통사고", st: "처리중", tone: "up" },
  { id: 2, time: "14:30:12", line: "올림픽대로 (가양 → 여의도)", type: "정체", st: "완료", tone: "up" },
  { id: 3, time: "14:28:55", line: "내부순환로 (월계 → 성수)", type: "속도 급감", st: "대기", tone: "dn" },
  { id: 4, time: "14:25:40", line: "강남구 테헤란로", type: "OCR 인식", st: "완료", tone: "up" },
  { id: 5, time: "14:22:11", line: "동부간선로 (수락 → 성수)", type: "서행", st: "처리중", tone: "up" },
];
const statsBars = [
  { day: "5/11", value: 142 }, { day: "5/12", value: 168 }, { day: "5/13", value: 155 },
  { day: "5/14", value: 178 }, { day: "5/15", value: 162 }, { day: "5/16", value: 184 }, { day: "5/17", value: 128 },
];
const sideKpis = [
  { label: "혼잡 관리 성과",   value: 94, unit: "%",  bar: 94, tone: "bl", delta: "▲ 4%p",  deltaTone: "up" },
  { label: "속도 이상 처리율", value: 97, unit: "%",  bar: 97, tone: "gr", delta: "▲ 2%p",  deltaTone: "up" },
  { label: "미처리 이벤트",    value: 18, unit: "건", bar: 60, tone: "or", delta: "▼ -6",  deltaTone: "up" },
  { label: "OCR 인식 성공률",  value: 96, unit: "%",  bar: 96, tone: "pl", delta: "▲ 1%p",  deltaTone: "up" },
  { label: "카메라 정상 가동", value: 98, unit: "%",  bar: 98, tone: "cy", delta: "0%p",    deltaTone: "flat" },
];

const autoPublish = ref(true);
const setAlert = ref(true);
const setRefresh = ref(30);
const setDept = ref("전체");
const setMsg = ref("");
function saveSettings() {
  setMsg.value = "설정이 저장되었습니다.";
  setTimeout(() => { setMsg.value = ""; }, 2000);
}
const nav = [
  { id: "ops",      icon: "bi bi-speedometer2",      label: "운영현황" },
  { id: "events",   icon: "bi bi-bell",              label: "이벤트" },
  { id: "stats",    icon: "bi bi-bar-chart",         label: "통계" },
  { id: "reports",  icon: "bi bi-file-earmark-text", label: "보고서" },
  { id: "settings", icon: "bi bi-gear",              label: "설정" },
];

const trendData = [
  { day: "5/10 (토)", value: 92, target: 90 },
  { day: "5/11 (일)", value: 90, target: 90 },
  { day: "5/12 (월)", value: 95, target: 90 },
  { day: "5/13 (화)", value: 96, target: 90 },
  { day: "5/14 (수)", value: 94, target: 90 },
  { day: "5/15 (목)", value: 93, target: 90 },
  { day: "5/16 (금)", value: 94, target: 90 },
];

const risks = [
  { title: "미처리 이벤트 증가",  count: "18건", detail: "전일 대비 +6건 증가",   action: "이벤트 빠른 처리 필요",  sev: "high", sevLabel: "높음", owner: "교통정보센터", due: "10:30 마감", score: 78 },
  { title: "속도 이상 검지 지연", count: "3건",  detail: "40km/h 초과 구간 2건",  action: "현장 확인 권장",        sev: "med",  sevLabel: "보통", owner: "교통분석팀",   due: "오늘 18:00",  score: 52 },
  { title: "카메라 연결 불안정",  count: "1건",  detail: "마포대로 CAM-M-002",   action: "네트워크 상태 점검",     sev: "low",  sevLabel: "낮음", owner: "시설운영팀",   due: "내일 09:00",  score: 34 },
];

const perfTab = ref("congest");
const period = ref("7d");
const periods = [
  { id: "today", label: "오늘" },
  { id: "7d",    label: "7일" },
  { id: "30d",   label: "30일" },
  { id: "qtr",   label: "분기" },
];

const recentReports = [
  { t: "일일 운영 보고서",  date: "2025-05-15", by: "운영기획팀 김지면", size: "2.4MB", views: 12, st: "발행", tone: "ok" },
  { t: "주간 성과 보고서",  date: "2025-05-12", by: "운영기획팀 김지면", size: "5.1MB", views: 38, st: "발행", tone: "ok" },
  { t: "5월 1주 이슈 리포트", date: "2025-05-08", by: "운영기획팀 이수진", size: "1.8MB", views: 24, st: "발행", tone: "ok" },
  { t: "4월 월간 종합",     date: "2025-05-02", by: "운영기획팀 김지면", size: "8.6MB", views: 56, st: "승인", tone: "appr" },
];

const depts = [
  { name: "전체",         v1: "94%", d1: "",       t1: "",     v2: "97%", d2: "",       t2: "",     v3: "96%", d3: "",       t3: "",     v4: "98%", d4: "",       t4: "",     v5: "18건", d5: "",       t5: "",     grade: "—", gradeTone: "" },
  { name: "교통정보센터", v1: "96%", d1: "▲ 2%p", t1: "up",   v2: "98%", d2: "▲ 1%p", t2: "up",   v3: "97%", d3: "▲ 1%p", t3: "up",   v4: "99%", d4: "▲ 1%p", t4: "up",   v5: "5건",  d5: "▼ -2건",t5: "up",   grade: "A+",gradeTone: "A" },
  { name: "단속관리팀",   v1: "93%", d1: "▼ -1%p",t1: "dn",   v2: "96%", d2: "▼ -1%p",t2: "dn",   v3: "95%", d3: "▼ -1%p",t3: "dn",   v4: "98%", d4: "0%p",   t4: "flat", v5: "7건",  d5: "▼ -1건",t5: "up",   grade: "A", gradeTone: "A" },
  { name: "교통분석팀",   v1: "92%", d1: "▼ -2%p",t1: "dn",   v2: "95%", d2: "▼ -2%p",t2: "dn",   v3: "94%", d3: "▼ -2%p",t3: "dn",   v4: "97%", d4: "▼ -1%p",t4: "dn",   v5: "6건",  d5: "▼ -3건",t5: "up",   grade: "B+",gradeTone: "B" },
];

const reportTypes = [
  { t: "일일 보고서", desc: "오늘의 운영 성과와 이벤트 현황 요약", date: "2025-05-16" },
  { t: "주간 보고서", desc: "주간 성과 추이 및 주요 이슈 분석",     date: "2025-05-10 ~ 2025-05-16" },
  { t: "월간 보고서", desc: "월간 성과 종합 및 개선 사항 제안",     date: "2025-05" },
];

const steps = [
  { t: "상태 요약", d: "전체 운영 상태를 한눈에 확인" },
  { t: "리스크 확인", d: "주의/경고 리스크를 점검" },
  { t: "성과 비교", d: "부서별 성과를 비교 분석" },
  { t: "보고서 생성", d: "보고서를 생성하고 공유" },
];
</script>

<style scoped>
.admin-shell { display: flex; min-height: 100vh; }
.side { width: 200px; padding: 20px 12px; }
.main { flex: 1; padding: 24px 28px; display: flex; flex-direction: column; gap: 18px; min-width: 0; }
.t-pick { background: #0f1d34; border: 1px solid #1f3055; border-radius: 6px; padding: 7px 12px; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; cursor: pointer; }

.seg-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.seg-h h2 { font-size: 15px; font-weight: 700; margin: 0; }
.seg-ts { font-size: 12px; opacity: .55; }

.kpis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
.kpi { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; display: flex; gap: 12px; }
.kpi.or { background: #1d1814; border-color: #5a3e1d; }
.kpi-ic { width: 38px; height: 38px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; flex-shrink: 0; }
.kpi.bl .kpi-ic { background: rgba(59,130,246,.15); color: #60a5fa; }
.kpi.gr .kpi-ic { background: rgba(16,185,129,.15); color: #34d399; }
.kpi.or .kpi-ic { background: rgba(245,158,11,.18); color: #fbbf24; }
.kpi.pl .kpi-ic { background: rgba(139,92,246,.15); color: #a78bfa; }
.kpi.cy .kpi-ic { background: rgba(6,182,212,.15); color: #22d3ee; }
.kpi-body { flex: 1; min-width: 0; }
.kpi-lab { font-size: 12px; opacity: .7; }
.kpi-val { font-size: 24px; font-weight: 800; margin: 2px 0 8px; }
.kpi.or .kpi-val { color: #fbbf24; }
.kpi-u { font-size: 12px; font-weight: 500; opacity: .65; margin-left: 2px; }
.kpi-bar { height: 4px; background: rgba(255,255,255,.06); border-radius: 4px; overflow: hidden; margin-bottom: 6px; }
.kpi-bar span { display: block; height: 100%; border-radius: 4px; }
.kpi-foot { display: flex; justify-content: space-between; font-size: 11px; opacity: .65; }
.kpi-foot .up { color: #34d399; }
.kpi-foot .dn { color: #f87171; }
.kpi-foot .flat { color: #94a3b8; }

.row2 { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 12px; }
.row3 { display: grid; grid-template-columns: 1.4fr 1.6fr; gap: 12px; }
.card { padding: 16px; }
.card-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.card-h h3 { margin: 0; }
.rb { background: rgba(239,68,68,.18); color: #f87171; padding: 3px 10px; border-radius: 100px; font-size: 11.5px; font-weight: 700; }

.tabs { display: flex; gap: 6px; margin-bottom: 10px; }
.tab { background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.55); font-size: 12px; padding: 6px 12px; border-radius: 6px; cursor: pointer; }
.tab.on { background: rgba(96,165,250,.12); color: #60a5fa; border-color: rgba(96,165,250,.35); }
.legend { font-size: 11.5px; opacity: .65; margin-bottom: 8px; display: flex; gap: 12px; }
.lg-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.lg-dot.bl { background: #3b82f6; }
.lg-dot.gr { background: #34d399; }
.lg-dot.yl { background: #f59e0b; }
.lg-dot.rd { background: #ef4444; }

.bars { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; height: 180px; padding: 0 4px; }
.bcol { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.bnum { font-size: 11px; font-weight: 700; color: #60a5fa; }
.bwrap { position: relative; flex: 1; width: 100%; max-width: 32px; background: rgba(255,255,255,.04); border-radius: 3px; display: flex; align-items: flex-end; transition: filter .15s; }
.bwrap.on { filter: brightness(1.25); }
.b-tip { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); margin-bottom: 6px; background: rgba(8,16,32,.95); border: 1px solid #1f3055; border-radius: 5px; padding: 5px 8px; font-size: 10.5px; white-space: nowrap; display: flex; flex-direction: column; align-items: center; gap: 2px; pointer-events: none; box-shadow: 0 4px 12px rgba(0,0,0,.4); z-index: 5; }
.b-tip strong { color: #60a5fa; font-weight: 800; font-size: 12px; }
.b-tip .b-delta.up { color: #34d399; }
.b-tip .b-delta.dn { color: #f87171; }
.bcol { cursor: pointer; outline: none; }
.bbar { width: 100%; background: linear-gradient(180deg, #60a5fa, #3b82f6); border-radius: 3px; }
.bline { position: absolute; left: -4px; right: -4px; height: 2px; background: #34d399; box-shadow: 0 0 4px #34d399; }
.bday { font-size: 10.5px; opacity: .55; }

.donut-wrap { position: relative; width: 160px; height: 160px; margin: 8px auto; }
.donut { width: 100%; height: 100%; }
.donut-c { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.dc-lab { font-size: 11px; opacity: .6; }
.dc-val { font-size: 24px; font-weight: 800; }
.dc-u { font-size: 12px; opacity: .65; margin-left: 2px; }
.donut-legend { display: flex; flex-direction: column; gap: 6px; font-size: 12px; opacity: .85; }
.donut-legend strong { font-weight: 700; margin-left: 2px; }

.risk .rk { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #1a2a45; cursor: pointer; align-items: center; }
.risk .rk:last-of-type { border-bottom: 0; }
.risk .rk > i.bi-exclamation-triangle { color: #fbbf24; font-size: 14px; padding-top: 2px; }
.rk-body { flex: 1; min-width: 0; }
.rk-t { font-size: 13px; font-weight: 600; display: flex; justify-content: space-between; }
.rk-cnt { color: #fbbf24; font-weight: 700; }
.rk-d { font-size: 11.5px; opacity: .65; margin-top: 2px; }
.rk-a { font-size: 11.5px; opacity: .55; }
.risk .rk > i.bi-chevron-right { opacity: .4; font-size: 12px; }
.rk-more { width: 100%; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 9px; border-radius: 6px; margin-top: 10px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }

.tbl-dept { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.tbl-dept th, .tbl-dept td { padding: 9px 10px; text-align: center; border-bottom: 1px solid #1a2a45; }
.tbl-dept th { font-weight: 600; opacity: .65; font-size: 11.5px; background: rgba(255,255,255,.02); }
.tbl-dept .dn { font-weight: 700; text-align: left; }
.tbl-dept .up { color: #34d399; font-size: 11px; }
.tbl-dept .dn { color: #f87171; font-size: 11px; }
.tbl-dept .flat { color: #94a3b8; font-size: 11px; }

.rep-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }
.rep { background: #122140; border: 1px solid #1f3055; border-radius: 8px; padding: 12px; }
.rep-h { font-size: 13px; font-weight: 700; display: inline-flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.rep-d { font-size: 11.5px; opacity: .7; line-height: 1.5; min-height: 32px; }
.rep-date { font-size: 11px; opacity: .55; margin: 6px 0 10px; }
.rep-btn { width: 100%; background: rgba(96,165,250,.1); border: 1px solid rgba(96,165,250,.25); color: #60a5fa; padding: 7px; border-radius: 5px; font-size: 12px; font-weight: 600; cursor: pointer; }
.rep-actions { display: grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 8px; }
.btn-pri, .btn-sec { padding: 10px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-pri { background: #3b82f6; color: #fff; border: 0; }
.btn-sec { background: rgba(255,255,255,.04); border: 1px solid #1f3055; color: rgba(228,238,255,.75); }

.steps { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 12px 16px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; align-items: center; }
.step { display: flex; align-items: center; gap: 10px; position: relative; }
.sn { width: 24px; height: 24px; border-radius: 50%; background: rgba(96,165,250,.15); color: #60a5fa; font-size: 11.5px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.st { font-size: 13px; font-weight: 700; }
.sd { font-size: 11px; opacity: .6; margin-top: 1px; }
.step-arrow { position: absolute; right: -6px; opacity: .3; }


.panel { min-height: 320px; }
.map-stub { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; height: 280px; background: #06101e; border: 1px dashed #1f3055; border-radius: 8px; opacity: .85; }
.map-stub > i { font-size: 36px; color: #60a5fa; }
.ms-legend { display: flex; gap: 14px; font-size: 11.5px; }
.ms-legend i.d { display: inline-block; width: 14px; height: 4px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }
.ms-legend i.gr { background: #34d399; }
.ms-legend i.yl { background: #f59e0b; }
.ms-legend i.or { background: #fb923c; }
.ms-legend i.rd { background: #ef4444; }
.cam-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.cam-cell { background: #06101e; border: 1px solid #1f3055; border-radius: 8px; padding: 14px; position: relative; }
.cam-cell > i { font-size: 22px; color: #60a5fa; }
.cc-id { font-size: 12px; font-weight: 700; margin-top: 6px; }
.cc-loc { font-size: 11px; opacity: .65; margin-top: 2px; }
.cc-st { position: absolute; top: 10px; right: 10px; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 100px; }
.cam-cell.ok .cc-st { background: rgba(16,185,129,.18); color: #34d399; }
.cam-cell.warn .cc-st { background: rgba(245,158,11,.18); color: #fbbf24; }
.cam-cell.bad .cc-st { background: rgba(239,68,68,.18); color: #f87171; }
.set-row { display: grid; grid-template-columns: 200px 1fr; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a2a45; font-size: 13px; }
.set-row input[type="number"], .set-row select { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 12.5px; max-width: 200px; }
.set-row input[type="checkbox"] { accent-color: #60a5fa; }
.set-msg { margin-top: 10px; font-size: 12px; color: #34d399; }
</style>
