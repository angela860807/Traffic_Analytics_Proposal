<template>
  <div class="sa-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen">Traffic <em>AS</em></RouterLink>
        <button class="side-toggle" @click="sideOpen = !sideOpen"
          :aria-label="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
          :title="sideOpen ? '사이드바 접기' : '사이드바 펼치기'">
          <i :class="sideOpen ? 'bi bi-arrow-left-short' : 'bi bi-arrow-right-short'"></i>
        </button>
      </div>
      <nav class="snav">
        <button v-for="n in topNav" :key="n.id" class="snav-i"
          :class="{ on: tab === n.id }" @click="tab = n.id">
          <i :class="n.icon"></i>{{ n.label }}
        </button>
        <div class="snav-sep">
          <i class="bi bi-shield-lock-fill"></i>
          <span>경영전략본부</span>
        </div>
        <button v-for="n in saNav" :key="n.id" class="snav-i"
          :class="{ on: tab === n.id }" @click="tab = n.id">
          <i :class="n.icon"></i>{{ n.label }}
        </button>
      </nav>
      <div class="side-foot">Traffic AS<br />경영전략본부 v2.0.0</div>
    </aside>

    <div class="main">
      <header class="top">
        <h1><a class="t-main" @click="goHome">경영전략본부</a></h1>
        <div class="t-right">
          <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>10:30:00</strong></span>
          <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
            <span class="km-dot"></span>
            <span class="km-lab">자동 새로고침</span>
            <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
          </button>
          <DeptSwitcher />
          <div class="t-user"><i class="bi bi-person-circle"></i> SUPER ADMIN <i class="bi bi-chevron-down"></i></div>
        </div>
      </header>

      <template v-if="tab === 'dashboard'">
      <section class="seg">
        <div class="seg-h">
          <h2>글로벌 상태 요약</h2>
          <span class="seg-ts">최종 업데이트 10:30:00 <i class="bi bi-arrow-clockwise"></i></span>
        </div>
        <div class="kpis">
          <div v-for="k in kpis" :key="k.label" class="kpi" :class="k.tone">
            <i :class="k.icon"></i>
            <div class="kpi-body">
              <div class="kpi-lab">{{ k.label }}</div>
              <div class="kpi-val">{{ k.value }}<span class="kpi-u">{{ k.unit }}</span></div>
              <div v-if="k.sub" class="kpi-sub">{{ k.sub }}</div>
            </div>
          </div>
        </div>
      </section>

      <section class="row-top2">
        <div class="card">
          <div class="card-h">
            <h3>부서별 성과 요약 <span class="seg-sub">(오늘 기준)</span></h3>
          </div>
          <div class="legend">
            <span><i class="lg gr"></i>정상</span>
            <span><i class="lg yl"></i>경고</span>
            <span><i class="lg rd"></i>위험</span>
            <span><i class="lg bl"></i>정보</span>
          </div>
          <table class="tbl-dept">
            <thead><tr><th>부서</th><th>상태</th><th>이벤트</th><th>SLA 준수율</th><th>핵심 지표</th></tr></thead>
            <tbody>
              <tr v-for="d in depts" :key="d.name">
                <td class="dn">{{ d.name }}</td>
                <td><span class="st-ic" :class="d.tone"><i :class="d.icon"></i></span></td>
                <td :class="d.evTone">{{ d.events }}</td>
                <td>{{ d.sla }}</td>
                <td>{{ d.kpi }} <span :class="d.kpiTone">{{ d.kpiDelta }}</span></td>
              </tr>
              <tr class="tot">
                <td class="dn">전체 평균</td><td></td><td>18</td><td>98.3%</td><td>94%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card">
          <div class="card-h"><h3>승인 대기 목록 <span class="cnt-bdg">7</span></h3></div>
          <table class="tbl-app">
            <thead><tr><th>구분</th><th>요청 내용</th><th>요청자</th><th>요청 시간</th><th>우선순위</th></tr></thead>
            <tbody>
              <tr v-for="(a, i) in approvals" :key="i">
                <td>{{ a.type }}</td>
                <td class="ttl">{{ a.title }}</td>
                <td>{{ a.user }}</td>
                <td class="mono">{{ a.time }}</td>
                <td><span class="pr" :class="a.prTone"><i class="dot-pr"></i>{{ a.pr }}</span></td>
              </tr>
            </tbody>
          </table>
          <button class="t-view full">전체 승인 요청 보기 <i class="bi bi-chevron-right"></i></button>
        </div>
      </section>

      <section class="row-bot2">
        <div class="card">
          <h3>최근 활동 로그</h3>
          <table class="tbl-log">
            <thead><tr><th>시간</th><th>사용자</th><th>작업</th><th>대상</th></tr></thead>
            <tbody>
              <tr v-for="(l, i) in logs" :key="i">
                <td class="mono">{{ l.time }}</td>
                <td class="su">{{ l.user }}</td>
                <td>{{ l.action }}</td>
                <td>{{ l.target }}</td>
              </tr>
            </tbody>
          </table>
          <button class="t-view full" @click="tab = 'audit'">전체 감사 로그 보기 <i class="bi bi-chevron-right"></i></button>
        </div>
      </section>

      </template>

      <section v-if="tab === 'perms'" class="card pnl">
        <h3>권한 관리 <span class="seg-sub">계층 · 사용자별 부여 권한</span></h3>
        <table class="pnl-tbl">
          <thead><tr><th>계층</th><th>권한 범위</th><th>인원</th><th>작업</th></tr></thead>
          <tbody>
            <tr v-for="r in roleRows" :key="r.role">
              <td class="dn">
                <span class="role-badge" :class="r.badge">{{ r.tier }}</span>
                {{ r.role }}
              </td>
              <td>{{ r.scope }}</td>
              <td class="mono">{{ r.count }}명</td>
              <td><button class="btn-mini" @click="flash(`${r.role} 권한 편집`)">편집</button></td>
            </tr>
          </tbody>
        </table>

        <h3 style="margin-top: 18px;">권한 매트릭스 <span class="seg-sub">예시 사용자별 접근 권한</span></h3>
        <table class="pnl-tbl perm-matrix">
          <thead>
            <tr>
              <th>기능</th>
              <th>김사원<br><em>사원급</em></th>
              <th>김대리<br><em>대리급</em></th>
              <th>김과장<br><em>과장급</em></th>
              <th>김부장<br><em>부장급</em></th>
              <th>이실장<br><em>경영전략실</em></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in permMatrix" :key="p.feat">
              <td class="dn">{{ p.feat }}</td>
              <td class="pm-cell" :class="{ on: p.rd === '🟢' }">{{ p.rd === '🟢' ? '✓' : '—' }}</td>
              <td class="pm-cell" :class="{ on: p.lj === '🟢' }">{{ p.lj === '🟢' ? '✓' : '—' }}</td>
              <td class="pm-cell" :class="{ on: p.pa === '🟢' }">{{ p.pa === '🟢' ? '✓' : '—' }}</td>
              <td class="pm-cell" :class="{ on: p.gh === '🟢' }">{{ p.gh === '🟢' ? '✓' : '—' }}</td>
              <td class="pm-cell" :class="{ on: p.sa === '🟢' }">{{ p.sa === '🟢' ? '✓' : '—' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="msg" class="set-msg">{{ msg }}</div>
      </section>

      <section v-if="tab === 'users'" class="card pnl">
        <h3>사용자 및 역할 현황</h3>
        <div class="users-grid">
          <div class="donut-w">
            <svg viewBox="0 0 120 120" class="donut">
              <circle cx="60" cy="60" r="42" fill="none" stroke="#1d2c44" stroke-width="20"/>
              <circle cx="60" cy="60" r="42" fill="none" stroke="#8b5cf6" stroke-width="20"
                stroke-dasharray="2.6 260" stroke-dashoffset="0" transform="rotate(-90 60 60)"/>
              <circle cx="60" cy="60" r="42" fill="none" stroke="#3b82f6" stroke-width="20"
                stroke-dasharray="21 260" stroke-dashoffset="-2.6" transform="rotate(-90 60 60)"/>
              <circle cx="60" cy="60" r="42" fill="none" stroke="#fbbf24" stroke-width="20"
                stroke-dasharray="50.2 260" stroke-dashoffset="-23.6" transform="rotate(-90 60 60)"/>
              <circle cx="60" cy="60" r="42" fill="none" stroke="#34d399" stroke-width="20"
                stroke-dasharray="166.4 260" stroke-dashoffset="-73.8" transform="rotate(-90 60 60)"/>
              <circle cx="60" cy="60" r="42" fill="none" stroke="#94a3b8" stroke-width="20"
                stroke-dasharray="23.8 260" stroke-dashoffset="-240.2" transform="rotate(-90 60 60)"/>
            </svg>
            <div class="donut-c">
              <div class="dc-lab">총 사용자</div>
              <div class="dc-val">236<span class="dc-u">명</span></div>
            </div>
          </div>
          <div class="user-legend">
            <div v-for="u in users" :key="u.role"><span class="lg" :style="{ background: u.color }"></span>{{ u.role }} <strong>{{ u.count }}</strong> <span class="pct">({{ u.pct }}%)</span></div>
          </div>
        </div>

        <h3 style="margin-top: 22px;">사용자 목록 — 총 {{ userList.length }}명</h3>
        <input class="pnl-search" v-model="userQuery" placeholder="이름·이메일·부서 검색" />
        <table class="pnl-tbl">
          <thead><tr><th>이름</th><th>이메일</th><th>역할</th><th>계층</th><th>부여 권한</th><th>부서</th><th>상태</th><th>작업</th></tr></thead>
          <tbody>
            <tr v-for="u in filteredUserList" :key="u.id">
              <td class="dn">{{ u.name }}</td>
              <td class="mono">{{ u.email }}</td>
              <td>{{ u.role }}</td>
              <td><span class="role-badge" :class="u.role === '슈퍼어드민' ? 'super' : (u.role === '관리자' ? 'admin' : (u.role === '게스트' ? 'guest' : 'user'))">{{ u.tier }}</span></td>
              <td>{{ u.perms }}</td>
              <td>{{ u.dept }}</td>
              <td><span class="stat" :class="u.tone">{{ u.st }}</span></td>
              <td><button class="btn-mini" @click="flash(`${u.name} 권한 편집`)">권한 편집</button></td>
            </tr>
            <tr v-if="!filteredUserList.length"><td colspan="8" class="pnl-empty">검색 결과 없음</td></tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'org'" class="card pnl">
        <h3>조직 관리 <span class="seg-sub">전체 조직 개요</span></h3>
        <div class="org-stat">
          <div class="os-num"><strong>5</strong><span>부서</span></div>
          <div class="os-num"><strong>79</strong><span>팀</span></div>
          <div class="os-num"><strong>81</strong><span>시스템</span></div>
        </div>
        <div class="org-tiles wide">
          <div v-for="o in orgs" :key="o.name" class="ot" :class="o.tone">
            <div class="ot-dot"></div>
            <div class="ot-n">{{ o.name }}</div>
            <div class="ot-c">{{ o.count }} <span class="ot-s">· {{ o.status }}</span></div>
          </div>
        </div>

        <h3 style="margin-top: 22px;">권한 및 역할 <span class="seg-sub">경영전략본부</span></h3>
        <div class="auth-hero">
          <i class="bi bi-shield-shaded"></i>
          <div class="ah-t">최고 권한</div>
          <div class="ah-s">전체 시스템 · 전체 데이터</div>
        </div>
        <div class="perm-grid wide">
          <div v-for="p in perms" :key="p.t" class="pg">
            <i :class="p.icon"></i>
            <span>{{ p.t }}</span>
          </div>
        </div>
      </section>

      <section v-if="tab === 'sys'" class="card pnl">
        <h3>시스템 설정</h3>
        <div class="set-row"><label>데이터 보존 기간 (일)</label><input type="number" v-model.number="setRetention" min="30" max="365" /></div>
        <div class="set-row"><label>이중 인증 (MFA)</label><input type="checkbox" v-model="setMfa" /></div>
        <div class="set-row"><label>유지보수 모드</label><input type="checkbox" v-model="setMaint" /></div>
        <button class="btn-save" @click="saveSys"><i class="bi bi-check2"></i> 저장</button>
        <div v-if="msg" class="set-msg">{{ msg }}</div>
      </section>

      <section v-if="tab === 'audit'" class="card pnl">
        <h3>감사 로그 <button class="su-dl" @click="downloadDeptReport('super', 'audit')"><i class="bi bi-download"></i> CSV 다운로드</button></h3>
        <table class="pnl-tbl">
          <thead><tr><th>시간</th><th>사용자</th><th>작업</th><th>대상</th></tr></thead>
          <tbody>
            <tr v-for="(l, i) in logs" :key="i">
              <td class="mono">{{ l.time }}</td><td class="su">{{ l.user }}</td>
              <td>{{ l.action }}</td><td>{{ l.target }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'reports'" class="card pnl">
        <h3>경영전략 보고서 <span class="seg-sub">전사 종합 · 감사용</span></h3>
        <div class="su-rep-grid">
          <div class="su-rep">
            <i class="bi bi-graph-up-arrow"></i>
            <div class="sr-body">
              <div class="sr-t">월간 종합 운영 보고서</div>
              <div class="sr-d">전 부서 KPI 종합 · 매월 1일 자동 생성</div>
            </div>
            <button class="su-dl" @click="downloadDeptReport('super', 'monthly')"><i class="bi bi-download"></i> 다운로드</button>
          </div>
          <div class="su-rep">
            <i class="bi bi-shield-lock"></i>
            <div class="sr-body">
              <div class="sr-t">보안·감사 로그 보고서</div>
              <div class="sr-d">사용자 활동 + 권한 변경 이력</div>
            </div>
            <button class="su-dl" @click="downloadDeptReport('super', 'audit')"><i class="bi bi-download"></i> 다운로드</button>
          </div>
          <div class="su-rep">
            <i class="bi bi-bar-chart-steps"></i>
            <div class="sr-body">
              <div class="sr-t">분기 KPI 종합 보고서</div>
              <div class="sr-d">분기별 부서 성과 비교</div>
            </div>
            <button class="su-dl" @click="downloadDeptReport('reports', 'quarterly')"><i class="bi bi-download"></i> 다운로드</button>
          </div>
        </div>
      </section>

      <section v-if="topNavTabs.includes(tab) && tab !== 'reports'" class="card pnl">
        <h3>{{ topNavLabel }} <span class="seg-sub">전사 통합 뷰</span></h3>
        <div class="map-stub">
          <i class="bi bi-globe2"></i>
          <div>{{ topNavLabel }} — 모든 부서의 데이터 통합 표시</div>
          <div class="ms-sub">상세 권한이 있는 부서 대시보드에서 더 풍부한 정보를 확인할 수 있습니다.</div>
        </div>
      </section>

      <footer v-if="tab === 'dashboard'" class="bot-bar">
        <div class="bb"><i class="bi bi-clock"></i><span>시스템 시간</span><strong>2025-05-16 (금) 10:30:00</strong></div>
        <div class="bb"><i class="bi bi-circle-fill" style="color:#34d399; font-size:9px"></i><span>서비스 상태</span><strong>모든 서비스 정상 운영 중</strong></div>
        <div class="bb"><span>데이터 보존 정책</span><strong>90일 (자동 삭제: 2025-08-14)</strong></div>
        <button class="bb-set">설정</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import { useReportDownload } from "@/composables/useReportDownload";
const { downloadDeptReport } = useReportDownload();

const tab = ref("dashboard");
const autoRefresh = ref(true);
const sideOpen = ref(true);
function goHome() {
  tab.value = "dashboard";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const topNav = [
  { id: "ops",     icon: "bi bi-speedometer2",      label: "운영현황" },
  { id: "map",     icon: "bi bi-map",               label: "지도" },
  { id: "events",  icon: "bi bi-bell",              label: "이벤트" },
  { id: "cams",    icon: "bi bi-camera-video",      label: "카메라" },
  { id: "ocr",     icon: "bi bi-card-text",         label: "OCR" },
  { id: "stats",   icon: "bi bi-bar-chart",         label: "통계" },
  { id: "reports", icon: "bi bi-file-earmark-text", label: "보고서" },
  { id: "settings",icon: "bi bi-gear",              label: "설정" },
];
const saNav = [
  { id: "dashboard", icon: "bi bi-grid-1x2",        label: "대시보드" },
  { id: "perms",     icon: "bi bi-shield-check",    label: "권한 관리" },
  { id: "users",     icon: "bi bi-people",          label: "사용자 관리" },
  { id: "org",       icon: "bi bi-diagram-3",       label: "조직 관리" },
  { id: "sys",       icon: "bi bi-sliders",         label: "시스템 설정" },
  { id: "audit",     icon: "bi bi-file-earmark-text", label: "감사 로그" },
];

const kpis = [
  { label: "전체 시스템",   value: "정상", unit: "", icon: "bi bi-check-circle-fill",          tone: "gr" },
  { label: "활성 이벤트",   value: 18,     unit: "건", icon: "bi bi-exclamation-triangle-fill", tone: "rd" },
  { label: "처리 중 이벤트", value: 36,     unit: "건", icon: "bi bi-exclamation-triangle-fill", tone: "or" },
  { label: "카메라 온라인", value: 98,     unit: "%",  icon: "bi bi-camera-video-fill",         tone: "bl", sub: "2,450 / 2,500" },
  { label: "OCR 정상률",   value: 96,     unit: "%",  icon: "bi bi-bullseye",                  tone: "pl" },
  { label: "속도 이상 처리율", value: 97,  unit: "%",  icon: "bi bi-speedometer",              tone: "gr" },
  { label: "데이터 수집률", value: 98,     unit: "%",  icon: "bi bi-database-fill",            tone: "cy" },
];

const topNavTabs = computed(() => topNav.map(n => n.id));
const topNavLabel = computed(() => topNav.find(n => n.id === tab.value)?.label || "");

const roleRows = [
  { role: "총괄 관리자 (슈퍼어드민)", tier: "경영전략실", scope: "시스템 전체 · 경영전략실 정책 수정", count: 2,  badge: "super" },
  { role: "관리자 (부장급)",           tier: "관리자",     scope: "모든 권한 · 반려/승인 · 보고서 발행", count: 18, badge: "admin" },
  { role: "관리자 (과장급)",           tier: "관리자",     scope: "속도 추이 · 이벤트 상세 · 분석 도구",  count: 24, badge: "admin" },
  { role: "일반 사용자 (대리급)",      tier: "일반",       scope: "카메라 + 지도 조회",                  count: 64, badge: "user" },
  { role: "일반 사용자 (사원급)",      tier: "일반",       scope: "카메라 조회만",                       count: 106, badge: "user" },
  { role: "게스트",                    tier: "게스트",     scope: "읽기 전용 (제한 영역)",               count: 22, badge: "guest" },
];

const permMatrix = [
  { feat: "카메라 조회",        rd: "🟢", lj: "🟢", pa: "🟢", gh: "🟢", sa: "🟢" },
  { feat: "지도 조회",           rd: "—", lj: "🟢", pa: "🟢", gh: "🟢", sa: "🟢" },
  { feat: "속도 추이 분석",     rd: "—", lj: "—", pa: "🟢", gh: "🟢", sa: "🟢" },
  { feat: "이벤트 상세 / OCR",  rd: "—", lj: "—", pa: "🟢", gh: "🟢", sa: "🟢" },
  { feat: "반려 / 승인",         rd: "—", lj: "—", pa: "—", gh: "🟢", sa: "🟢" },
  { feat: "사용자 / 권한 관리", rd: "—", lj: "—", pa: "—", gh: "—",  sa: "🟢" },
  { feat: "경영전략실 정책 수정",rd: "—", lj: "—", pa: "—", gh: "—",  sa: "🟢" },
];

const userQuery = ref("");
const userList = [
  { id: 1, name: "김사원", email: "kim.sw@traffic.kr",  role: "일반 사용자", tier: "사원급",  perms: "카메라",                          dept: "교통정보센터", st: "정상", tone: "ok" },
  { id: 2, name: "김대리", email: "kim.dl@traffic.kr",  role: "일반 사용자", tier: "대리급",  perms: "카메라, 지도",                    dept: "교통정보센터", st: "정상", tone: "ok" },
  { id: 3, name: "김과장", email: "kim.kj@traffic.kr",  role: "관리자",      tier: "과장급",  perms: "속도 추이, 이벤트 상세",          dept: "교통분석팀",   st: "정상", tone: "ok" },
  { id: 4, name: "김부장", email: "kim.bj@traffic.kr",  role: "관리자",      tier: "부장급",  perms: "모든 권한 · 반려/승인",            dept: "단속관리팀",   st: "정상", tone: "ok" },
  { id: 5, name: "이실장", email: "lee.sj@traffic.kr",  role: "슈퍼어드민",  tier: "경영전략실", perms: "시스템 전체 · 정책 수정",       dept: "경영전략본부", st: "정상", tone: "ok" },
  { id: 6, name: "박과장", email: "park.kj@traffic.kr", role: "관리자",      tier: "과장급",  perms: "속도 추이, 이벤트 상세",          dept: "교통분석팀",   st: "휴직", tone: "wn" },
  { id: 7, name: "한도윤", email: "han.dy@traffic.kr",  role: "게스트",      tier: "외부",    perms: "읽기 전용",                       dept: "외부",         st: "비활성", tone: "no" },
];
const filteredUserList = computed(() => {
  const q = userQuery.value.trim().toLowerCase();
  if (!q) return userList;
  return userList.filter(u => u.name.includes(q) || u.email.toLowerCase().includes(q) || u.dept.includes(q));
});

const setRetention = ref(90);
const setMfa = ref(true);
const setMaint = ref(false);
const msg = ref("");
function flash(t) { msg.value = t; setTimeout(() => { msg.value = ""; }, 1800); }
function saveSys() { flash("시스템 설정 저장 완료"); }

const orgs = [
  { name: "교통정보센터",  status: "정상", tone: "gr",   count: "24 / 24" },
  { name: "단속관리팀",    status: "정상", tone: "gr",   count: "18 / 18" },
  { name: "교통분석팀",    status: "정상", tone: "gr",   count: "15 / 15" },
  { name: "시설운영팀",    status: "경고", tone: "warn", count: "12 / 14" },
  { name: "운영기획팀",    status: "정상", tone: "gr",   count: "10 / 10" },
];

const depts = [
  { name: "교통정보센터", tone: "gr", icon: "bi bi-check", events: 2,  sla: "99.2%", kpi: "94%", kpiTone: "up", kpiDelta: "↑", evTone: "" },
  { name: "단속관리팀",   tone: "gr", icon: "bi bi-check", events: 3,  sla: "98.7%", kpi: "97%", kpiTone: "up", kpiDelta: "↑", evTone: "" },
  { name: "교통분석팀",   tone: "gr", icon: "bi bi-check", events: 1,  sla: "98.9%", kpi: "93%", kpiTone: "up", kpiDelta: "↑", evTone: "" },
  { name: "시설운영팀",   tone: "wn", icon: "bi bi-exclamation", events: 12, sla: "95.1%", kpi: "89%", kpiTone: "dn", kpiDelta: "↓", evTone: "rd" },
  { name: "운영기획팀",   tone: "gr", icon: "bi bi-check", events: 0,  sla: "99.7%", kpi: "98%", kpiTone: "up", kpiDelta: "↑", evTone: "" },
];

const perms = [
  { t: "전체 조회", icon: "bi bi-eye-fill" },
  { t: "전체 편집", icon: "bi bi-pencil-fill" },
  { t: "사용자 관리", icon: "bi bi-people-fill" },
  { t: "권한 설정", icon: "bi bi-key-fill" },
  { t: "보고서 승인", icon: "bi bi-check2-square" },
];

const approvals = [
  { type: "보고서 승인", title: "5월 운영성과 보고서",       user: "운영기획팀 김지면",   time: "10:25", pr: "높음", prTone: "high" },
  { type: "사용자 생성", title: "신규 사용자 3명",          user: "교통정보센터 박현우", time: "09:58", pr: "보통", prTone: "med" },
  { type: "권한 변경",   title: "역할 권한 수정 요청",       user: "시설운영팀 이수진",   time: "09:42", pr: "보통", prTone: "med" },
  { type: "시스템 설정", title: "카메라 그룹 설정 변경",     user: "시설운영팀 이수진",   time: "09:30", pr: "낮음", prTone: "low" },
  { type: "보고서 승인", title: "주간 교통흐름 분석 보고",   user: "교통분석팀 정민혁",   time: "09:15", pr: "낮음", prTone: "low" },
];

const users = [
  { role: "경영전략본부",  count: 2,   pct: 1,  color: "#8b5cf6" },
  { role: "관리자",        count: 18,  pct: 8,  color: "#3b82f6" },
  { role: "팀장",          count: 46,  pct: 19, color: "#fbbf24" },
  { role: "일반 사용자",   count: 148, pct: 63, color: "#34d399" },
  { role: "게스트",        count: 22,  pct: 9,  color: "#94a3b8" },
];

const logs = [
  { time: "10:29", user: "SUPER ADMIN", action: "사용자 권한 수정", target: "교통정보센터" },
  { time: "10:24", user: "SUPER ADMIN", action: "보고서 승인",      target: "5월 운영보고서" },
  { time: "10:18", user: "SUPER ADMIN", action: "역할 정책 수정",   target: "단속관리팀" },
  { time: "10:12", user: "SUPER ADMIN", action: "카메라 설정 변경", target: "강남대로 구간" },
  { time: "10:05", user: "SUPER ADMIN", action: "사용자 생성",      target: "신규 사용자 2명" },
];
</script>

<style scoped>
/* shell/brand/snav/top/bell/bdg/user/seg-sub는 admin-shared.css */
.side { width: 200px; padding: 20px 12px; display: flex; flex-direction: column; overflow-y: auto; }
.snav-sep { display: flex; align-items: center; gap: 8px; padding: 16px 12px 8px; font-size: 12px; color: #34d399; font-weight: 700; border-top: 1px solid #1a2a45; margin-top: 12px; }
.snav-sep i { color: #34d399; }
.side-foot { font-size: 10.5px; opacity: .4; padding: 12px 6px 0; line-height: 1.6; }
.main { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.top h1 { font-size: 19px; display: flex; align-items: center; gap: 10px; }
.t-tag { background: linear-gradient(90deg, #8b5cf6, #3b82f6); color: #fff; font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 4px; letter-spacing: 0.05em; }
.t-right { gap: 14px; }
.t-ic { font-size: 18px; opacity: .7; cursor: pointer; }
.seg-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.seg-h h2 { font-size: 15px; font-weight: 700; margin: 0; }
.seg-ts { font-size: 12px; opacity: .55; }

.kpis { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
.kpi { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 12px 14px; display: flex; gap: 10px; align-items: flex-start; }
.kpi > i { font-size: 18px; padding-top: 2px; }
.kpi.gr > i { color: #34d399; }
.kpi.rd > i { color: #ef4444; }
.kpi.or > i { color: #fbbf24; }
.kpi.bl > i { color: #60a5fa; }
.kpi.pl > i { color: #a78bfa; }
.kpi.cy > i { color: #22d3ee; }
.kpi-body { flex: 1; min-width: 0; }
.kpi-lab { font-size: 11px; opacity: .7; margin-bottom: 2px; }
.kpi-val { font-size: 20px; font-weight: 800; }
.kpi.rd .kpi-val { color: #f87171; }
.kpi.or .kpi-val { color: #fbbf24; }
.kpi-u { font-size: 11px; font-weight: 500; opacity: .65; margin-left: 1px; }
.kpi-sub { font-size: 10.5px; opacity: .55; margin-top: 2px; }

.row-top { display: grid; grid-template-columns: 1.1fr 1.4fr 1.1fr; gap: 12px; }
.row-bot { display: grid; grid-template-columns: 1.3fr 1fr 1.2fr; gap: 12px; }
.row-top2 { display: grid; grid-template-columns: 1.1fr 1fr; gap: 12px; }
.row-bot2 { display: grid; grid-template-columns: 1fr; gap: 12px; }
.org-tiles.wide { grid-template-columns: repeat(3, 1fr); }
.perm-grid.wide { grid-template-columns: repeat(3, 1fr); }
.card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.card h3 { font-size: 14px; font-weight: 700; margin: 0 0 12px; }
.card-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.card-h h3 { margin: 0; }

.org-card { display: flex; flex-direction: column; }
.org-stat { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
.os-num { background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.18); border-radius: 8px; padding: 12px 8px; text-align: center; }
.os-num strong { display: block; font-size: 22px; font-weight: 800; color: #60a5fa; line-height: 1; }
.os-num span { display: block; font-size: 11px; opacity: .65; margin-top: 4px; }
.org-tiles { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; flex: 1; }
.ot { background: rgba(255,255,255,.02); border: 1px solid #1f3055; border-left: 3px solid #34d399; border-radius: 6px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; position: relative; }
.ot.warn { border-left-color: #fbbf24; }
.ot-dot { position: absolute; top: 10px; right: 10px; width: 6px; height: 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 8px rgba(52,211,153,.6); }
.ot.warn .ot-dot { background: #fbbf24; box-shadow: 0 0 8px rgba(251,191,36,.6); }
.ot-n { font-size: 12.5px; font-weight: 700; }
.ot-c { font-size: 11px; opacity: .6; font-family: "JetBrains Mono", monospace; }
.org-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.org-list li { display: grid; grid-template-columns: 16px 1fr auto auto; gap: 8px; align-items: center; font-size: 12.5px; }
.org-list .ol-n { font-weight: 600; }
.ol-s { font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 100px; }
.ol-s.gr { background: rgba(16,185,129,.15); color: #34d399; }
.ol-s.warn { background: rgba(245,158,11,.18); color: #fbbf24; }
.ol-c { font-size: 11px; opacity: .65; font-family: "JetBrains Mono", monospace; }
.org-foot { padding-top: 12px; margin-top: 12px; border-top: 1px solid #1a2a45; font-size: 12px; }

.t-view { background: none; border: 1px solid #1f3055; color: rgba(228,238,255,.7); font-size: 11.5px; padding: 5px 12px; border-radius: 5px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; }
.t-view.full { width: 100%; justify-content: center; margin-top: 10px; padding: 8px; background: rgba(96,165,250,.06); border-color: rgba(96,165,250,.2); color: #60a5fa; font-weight: 600; }

.legend { display: flex; gap: 12px; font-size: 11px; opacity: .85; margin-bottom: 8px; }
.legend .lg { display: inline-block; width: 8px; height: 8px; border-radius: 2px; margin-right: 4px; }
.legend .gr { background: #34d399; }
.legend .yl { background: #fbbf24; }
.legend .rd { background: #ef4444; }
.legend .bl { background: #60a5fa; }

.tbl-dept, .tbl-app, .tbl-log { width: 100%; border-collapse: collapse; font-size: 12px; }
.tbl-dept th, .tbl-dept td, .tbl-app th, .tbl-app td, .tbl-log th, .tbl-log td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-dept th, .tbl-app th, .tbl-log th { font-weight: 600; opacity: .55; font-size: 11px; }
.tbl-dept .dn { font-weight: 700; }
.tbl-dept .tot { background: rgba(96,165,250,.04); font-weight: 700; }
.tbl-dept .up { color: #34d399; }
.tbl-dept .dn { color: #f87171; }
.tbl-dept .rd { color: #f87171; }
.st-ic { display: inline-flex; align-items: center; justify-content: center; width: 22px; height: 22px; border-radius: 50%; }
.st-ic.gr { background: rgba(16,185,129,.15); color: #34d399; }
.st-ic.wn { background: rgba(245,158,11,.18); color: #fbbf24; }

.auth-card { padding: 14px; display: flex; flex-direction: column; }
.auth-hero { text-align: center; padding: 16px 12px; background: linear-gradient(135deg, rgba(139,92,246,.14), rgba(59,130,246,.1)); border: 1px solid rgba(139,92,246,.28); border-radius: 10px; margin-bottom: 12px; }
.auth-hero i { font-size: 28px; color: #a78bfa; display: block; margin-bottom: 6px; }
.ah-t { font-size: 16px; font-weight: 800; color: #e4eeff; letter-spacing: .02em; }
.ah-s { font-size: 11px; opacity: .65; margin-top: 2px; }
.perm-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; flex: 1; }
.pg { display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: rgba(52,211,153,.06); border: 1px solid rgba(52,211,153,.2); border-radius: 6px; font-size: 12px; font-weight: 600; }
.pg i { color: #34d399; font-size: 13px; }
.pg:nth-child(5) { grid-column: 1 / -1; }
.auth-go { width: 100%; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 9px; border-radius: 6px; margin-top: 12px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }

.cnt-bdg { background: rgba(245,158,11,.18); color: #fbbf24; font-size: 11px; font-weight: 700; padding: 1px 8px; border-radius: 999px; margin-left: 4px; }
.tbl-app .ttl { font-weight: 600; }
.tbl-app .mono { font-family: "JetBrains Mono", monospace; opacity: .8; }
.pr { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; }
.pr .dot-pr { width: 8px; height: 8px; border-radius: 50%; }
.pr.high .dot-pr { background: #ef4444; }
.pr.med .dot-pr { background: #fbbf24; }
.pr.low .dot-pr { background: #60a5fa; }
.pr.high { color: #f87171; }
.pr.med { color: #fbbf24; }
.pr.low { color: #60a5fa; }

.users-grid { display: grid; grid-template-columns: 130px 1fr; gap: 14px; align-items: center; margin-bottom: 14px; }
.donut-w { position: relative; width: 130px; height: 130px; }
.donut { width: 100%; height: 100%; }
.donut-c { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.dc-lab { font-size: 10.5px; opacity: .6; }
.dc-val { font-size: 18px; font-weight: 800; }
.dc-u { font-size: 11px; opacity: .65; margin-left: 1px; }
.user-legend { display: flex; flex-direction: column; gap: 5px; font-size: 12px; }
.user-legend > div { display: flex; align-items: center; gap: 6px; }
.user-legend .lg { display: inline-block; width: 9px; height: 9px; border-radius: 2px; }
.user-legend strong { font-weight: 700; margin-left: auto; }
.user-legend .pct { opacity: .55; font-size: 11px; }
.user-acts { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }

.tbl-log .mono { font-family: "JetBrains Mono", monospace; opacity: .8; font-size: 11px; }
.tbl-log .su { color: #a78bfa; font-weight: 600; font-size: 11px; }

.bot-bar { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 12px 18px; display: flex; align-items: center; gap: 28px; font-size: 12px; }
.bb { display: flex; align-items: center; gap: 8px; }
.bb i { opacity: .55; }
.bb > span { opacity: .65; }
.bb strong { font-weight: 700; }
.bb-set { margin-left: auto; background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 6px 18px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; }
.pnl { padding: 18px; }
.pnl h3 { font-size: 14px; font-weight: 700; margin: 0 0 14px; }
.pnl-search { width: 100%; background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 8px 12px; border-radius: 6px; font-size: 12.5px; margin-bottom: 12px; }
.pnl-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.pnl-tbl th, .pnl-tbl td { padding: 9px 10px; text-align: left; border-bottom: 1px solid #1a2a45; }
.pnl-tbl th { font-weight: 600; opacity: .6; font-size: 11.5px; }
.pnl-tbl .mono { font-family: "JetBrains Mono", monospace; opacity: .8; }
.pnl-tbl .dn { font-weight: 700; }
.pnl-empty { text-align: center; opacity: .55; padding: 24px 0; }
.stat { padding: 2px 8px; border-radius: 100px; font-size: 10.5px; font-weight: 700; }
.stat.ok { background: rgba(16,185,129,.15); color: #34d399; }
.stat.wn { background: rgba(245,158,11,.18); color: #fbbf24; }
.stat.no { background: rgba(239,68,68,.18); color: #f87171; }
.btn-mini { background: rgba(96,165,250,.12); border: 0; color: #60a5fa; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; }
.map-stub { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; height: 280px; background: #06101e; border: 1px dashed #1f3055; border-radius: 8px; opacity: .85; text-align: center; }
.map-stub > i { font-size: 36px; color: #60a5fa; }
.ms-sub { font-size: 11px; opacity: .55; max-width: 360px; line-height: 1.6; }
.set-row { display: grid; grid-template-columns: 220px 1fr; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid #1a2a45; font-size: 13px; }
.set-row input[type="number"], .set-row select { background: #06101e; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 12.5px; max-width: 200px; }
.set-row input[type="checkbox"] { accent-color: #60a5fa; }
.btn-save { margin-top: 14px; background: #3b82f6; color: #fff; border: 0; padding: 9px 16px; border-radius: 6px; font-size: 12.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.set-msg { margin-top: 10px; font-size: 12px; color: #34d399; }

.su-rep-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
.su-rep {
  display: flex; align-items: center; gap: 14px;
  background: rgba(96,165,250,0.05);
  border: 1px solid rgba(96,165,250,0.18);
  border-radius: 6px; padding: 14px 16px;
}
.su-rep > i { font-size: 22px; color: #60a5fa; flex-shrink: 0; }
.sr-body { flex: 1; min-width: 0; }
.sr-t { font-size: 14px; font-weight: 700; color: #e4eeff; margin-bottom: 3px; }
.sr-d { font-size: 12px; opacity: 0.65; }
.su-dl {
  background: #059669; color: #fff; border: 0;
  padding: 7px 14px; border-radius: 4px;
  font-size: 12.5px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; gap: 5px;
  flex-shrink: 0;
}
.su-dl:hover { background: #047857; }
.pnl h3 .su-dl { margin-left: auto; }
.pnl h3 { display: flex; align-items: center; gap: 10px; }
</style>
