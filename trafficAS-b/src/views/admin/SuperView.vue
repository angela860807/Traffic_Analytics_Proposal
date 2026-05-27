<template>
  <div class="sa-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen"><img src="/TAS.png" alt="TAS" class="brand-img" /></RouterLink>
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
      <div class="side-foot">TAS<br />경영전략본부 v2.0.0</div>
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
          <div class="t-user"><i class="bi bi-person-circle"></i> SUPER ADMIN <i class="bi bi-chevron-down"></i></div>
        </div>
      </header>

      <GuideOverlay
        v-model="guideOpen"
        :steps="guideSteps"
        :on-step-enter="onGuideStep"
      />

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

      <!-- ── 운영현황 (ops) ── -->
      <template v-if="tab === 'ops'">
        <section class="seg">
          <div class="seg-h">
            <h2>전사 운영현황 <span class="seg-sub">시설운영팀 통합</span></h2>
          </div>
          <div class="kpis">
            <div v-for="k in opsKpis" :key="k.label" class="kpi" :class="k.tone">
              <i :class="k.icon"></i>
              <div class="kpi-body">
                <div class="kpi-lab">{{ k.label }}</div>
                <div class="kpi-val">{{ k.value }}</div>
                <div class="kpi-sub">전일 대비 {{ k.delta }}</div>
              </div>
            </div>
          </div>
        </section>
        <section class="card pnl">
          <h3>대표 서버 상태</h3>
          <table class="pnl-tbl">
            <thead><tr><th>서버</th><th>역할</th><th>CPU</th><th>메모리</th><th>디스크</th><th>상태</th></tr></thead>
            <tbody>
              <tr v-for="s in opsServers" :key="s.name">
                <td class="dn mono">{{ s.name }}</td>
                <td>{{ s.role }}</td>
                <td class="mono">{{ s.cpu }}%</td>
                <td class="mono">{{ s.mem }}%</td>
                <td class="mono">{{ s.disk }}%</td>
                <td><span class="stat" :class="s.tone">{{ s.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>

      <!-- ── 지도 (map) ── -->
      <template v-if="tab === 'map'">
        <section class="card pnl">
          <h3>실시간 교통 흐름 <span class="seg-sub">교통정보센터 요약</span></h3>
          <div class="map-overview">
            <div class="map-stub-card">
              <i class="bi bi-map-fill"></i>
              <div class="ms-t">서울 주요 간선 실시간 흐름</div>
              <div class="ms-sub">상세 지도는 교통정보센터 대시보드에서 확인하세요</div>
            </div>
            <table class="pnl-tbl">
              <thead><tr><th>도로</th><th>평균 속도</th><th>혼잡도</th><th>활성 이벤트</th></tr></thead>
              <tbody>
                <tr v-for="r in mapRoadStats" :key="r.road">
                  <td class="dn">{{ r.road }}</td>
                  <td class="mono">{{ r.speed }} km/h</td>
                  <td><span class="stat" :class="r.tone">{{ r.level }}</span></td>
                  <td class="mono">{{ r.events }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- ── 이벤트 (events) ── -->
      <template v-if="tab === 'events'">
        <section class="card pnl">
          <h3>전사 이벤트 통합 <span class="seg-sub">최근 24시간 · {{ allEvents.length }}건</span></h3>
          <table class="pnl-tbl">
            <thead><tr><th>시각</th><th>부서</th><th>유형</th><th>상세</th></tr></thead>
            <tbody>
              <tr v-for="(e, i) in allEvents" :key="i">
                <td class="mono">{{ e.time }}</td>
                <td class="dn">{{ e.dept }}</td>
                <td><span class="stat" :class="e.tone">{{ e.type }}</span></td>
                <td>{{ e.detail }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>

      <!-- ── 카메라 (cams) ── -->
      <template v-if="tab === 'cams'">
        <section class="seg">
          <div class="seg-h">
            <h2>전체 카메라 현황 <span class="seg-sub">총 {{ allCamStats.total }}대 운영</span></h2>
          </div>
          <div class="kpis">
            <div class="kpi gr">
              <i class="bi bi-camera-video-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">정상 운영</div>
                <div class="kpi-val">{{ allCamStats.online }}<span class="kpi-u">대</span></div>
                <div class="kpi-sub">{{ ((allCamStats.online / allCamStats.total) * 100).toFixed(1) }}%</div>
              </div>
            </div>
            <div class="kpi rd">
              <i class="bi bi-camera-video-off-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">오프라인</div>
                <div class="kpi-val">{{ allCamStats.offline }}<span class="kpi-u">대</span></div>
                <div class="kpi-sub">즉시 점검 필요</div>
              </div>
            </div>
            <div class="kpi yl">
              <i class="bi bi-exclamation-triangle-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">오류</div>
                <div class="kpi-val">{{ allCamStats.error }}<span class="kpi-u">대</span></div>
                <div class="kpi-sub">신호 이상</div>
              </div>
            </div>
            <div class="kpi bl">
              <i class="bi bi-grid-3x3-gap-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">전체 카메라</div>
                <div class="kpi-val">{{ allCamStats.total }}<span class="kpi-u">대</span></div>
                <div class="kpi-sub">5개 권역</div>
              </div>
            </div>
          </div>
        </section>
        <section class="card pnl">
          <h3>부서별 카메라 배분</h3>
          <table class="pnl-tbl">
            <thead><tr><th>부서</th><th>전체</th><th>정상</th><th>오프라인</th><th>오류</th><th>가동률</th></tr></thead>
            <tbody>
              <tr v-for="(c, i) in camsByDept" :key="i">
                <td class="dn">{{ c.dept }}</td>
                <td class="mono">{{ c.total }}</td>
                <td class="mono">{{ c.online }}</td>
                <td class="mono">{{ c.offline }}</td>
                <td class="mono">{{ c.error }}</td>
                <td class="mono">{{ ((c.online / c.total) * 100).toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
        </section>
        <section class="card pnl">
          <h3>최근 이슈 카메라</h3>
          <table class="pnl-tbl">
            <thead><tr><th>장비 ID</th><th>위치</th><th>상태</th><th>경과 시간</th></tr></thead>
            <tbody>
              <tr v-for="c in recentCamIssues" :key="c.id">
                <td class="mono dn">{{ c.id }}</td>
                <td>{{ c.name }}</td>
                <td><span class="stat" :class="c.tone">{{ c.status }}</span></td>
                <td class="mono">{{ c.since }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>

      <!-- ── OCR (ocr) ── -->
      <template v-if="tab === 'ocr'">
        <section class="seg">
          <div class="seg-h">
            <h2>OCR 인식 현황 <span class="seg-sub">단속관리팀 통합 · 오늘</span></h2>
          </div>
          <div class="kpis">
            <div class="kpi bl">
              <i class="bi bi-card-text"></i>
              <div class="kpi-body">
                <div class="kpi-lab">오늘 처리</div>
                <div class="kpi-val">{{ ocrSummary.todayTotal.toLocaleString() }}<span class="kpi-u">건</span></div>
              </div>
            </div>
            <div class="kpi gr">
              <i class="bi bi-check-circle-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">인식 성공률</div>
                <div class="kpi-val">{{ ocrSummary.successRate }}<span class="kpi-u">%</span></div>
                <div class="kpi-sub">{{ ocrSummary.success.toLocaleString() }}건 성공</div>
              </div>
            </div>
            <div class="kpi yl">
              <i class="bi bi-speedometer"></i>
              <div class="kpi-body">
                <div class="kpi-lab">평균 신뢰도</div>
                <div class="kpi-val">{{ ocrSummary.avgConf }}<span class="kpi-u">%</span></div>
              </div>
            </div>
            <div class="kpi rd">
              <i class="bi bi-x-circle-fill"></i>
              <div class="kpi-body">
                <div class="kpi-lab">인식 실패</div>
                <div class="kpi-val">{{ ocrSummary.failed }}<span class="kpi-u">건</span></div>
                <div class="kpi-sub">중복 제거 {{ ocrSummary.duplicates }}건</div>
              </div>
            </div>
          </div>
        </section>
        <section class="card pnl">
          <h3>최근 OCR 인식 로그</h3>
          <table class="pnl-tbl">
            <thead><tr><th>시각</th><th>차량 번호</th><th>카메라</th><th>방향</th><th>신뢰도</th><th>상태</th></tr></thead>
            <tbody>
              <tr v-for="(o, i) in recentOcr" :key="i">
                <td class="mono">{{ o.time }}</td>
                <td class="mono dn">{{ o.plate }}</td>
                <td>{{ o.cam }}</td>
                <td class="mono">{{ o.dir === 'in' ? '진입' : o.dir === 'out' ? '이탈' : '-' }}</td>
                <td class="mono">{{ o.conf > 0 ? o.conf + '%' : '-' }}</td>
                <td><span class="stat" :class="o.status === 'FLOW_EVENT_CREATED' ? 'gr' : 'rd'">{{ o.status === 'FLOW_EVENT_CREATED' ? '정상' : '실패' }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>

      <!-- ── 통계 (stats) ── -->
      <template v-if="tab === 'stats'">
        <section class="seg">
          <div class="seg-h">
            <h2>교통 통계 요약 <span class="seg-sub">교통분석팀 통합 · 오늘</span></h2>
          </div>
          <div class="kpis">
            <div v-for="s in statsKpis" :key="s.label" class="kpi" :class="s.up ? 'gr' : 'rd'">
              <i :class="s.icon"></i>
              <div class="kpi-body">
                <div class="kpi-lab">{{ s.label }}</div>
                <div class="kpi-val">{{ s.value }}<span class="kpi-u">{{ s.unit }}</span></div>
                <div class="kpi-sub">전일 대비 {{ s.diff }}</div>
              </div>
            </div>
          </div>
        </section>
        <section class="card pnl">
          <h3>시간대별 통행량 분포</h3>
          <table class="pnl-tbl">
            <thead><tr><th>시간대</th><th>통행량</th><th>혼잡도</th><th>분포</th></tr></thead>
            <tbody>
              <tr v-for="h in statsByHour" :key="h.hour">
                <td class="dn">{{ h.hour }}</td>
                <td class="mono">{{ h.traffic.toLocaleString() }}대</td>
                <td><span class="stat" :class="h.level === '정체' ? 'rd' : h.level === '혼잡' ? 'or' : h.level === '보통' ? 'yl' : 'gr'">{{ h.level }}</span></td>
                <td><div class="stat-bar"><div class="stat-bar-fill" :style="{ width: (h.traffic / 1840 * 100) + '%' }"></div></div></td>
              </tr>
            </tbody>
          </table>
        </section>
      </template>

      <!-- ── 설정 (settings) ── -->
      <template v-if="tab === 'settings'">
        <section class="card pnl">
          <h3>전사 시스템 설정 <span class="seg-sub">경영전략본부 권한 필요</span></h3>
          <div class="su-set-grid">
            <div class="su-set-blk">
              <h4>알림 · 백업</h4>
              <div class="set-row"><label>알림 사운드</label><input type="checkbox" v-model="setAlertSound" /></div>
              <div class="set-row"><label>자동 백업</label><input type="checkbox" v-model="setAutoBackup" /></div>
              <div class="set-row"><label>유지보수 시간대</label><input type="text" v-model="setMaintWindow" /></div>
            </div>
            <div class="su-set-blk">
              <h4>로그 · API</h4>
              <div class="set-row"><label>로그 보관 (일)</label><input type="number" v-model.number="setLogRetention" min="30" max="365" /></div>
              <div class="set-row"><label>API 타임아웃 (초)</label><input type="number" v-model.number="setApiTimeout" min="3" max="60" /></div>
              <div class="set-row"><label>데이터 보존 (일)</label><input type="number" v-model.number="setRetention" min="30" max="365" /></div>
            </div>
            <div class="su-set-blk">
              <h4>보안</h4>
              <div class="set-row"><label>이중 인증 (MFA)</label><input type="checkbox" v-model="setMfa" /></div>
              <div class="set-row"><label>유지보수 모드</label><input type="checkbox" v-model="setMaint" /></div>
              <div class="set-row"><label>IP 허용 목록 사용</label><input type="checkbox" checked /></div>
            </div>
          </div>
          <button class="btn-save" @click="saveSys"><i class="bi bi-check2"></i> 전체 저장</button>
          <div v-if="msg" class="set-msg">{{ msg }}</div>
        </section>
      </template>

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
import GuideOverlay from "@/components/GuideOverlay.vue";
import guideSteps from "@/data/guides/super.js";
const { downloadDeptReport } = useReportDownload();

const guideOpen = ref(false);
const tab = ref("dashboard");

/* ── 헤더 실시간 알림 ── */
const showAlerts = ref(false);
const liveAlerts = ref([
  { id: 1, sev: "critical", icon: "bi bi-shield-exclamation",     title: "권한 승격 요청 대기",       detail: "교통분석팀장 — 부장급 권한 승격 요청 (대기 4시간)",   place: "권한 관리 큐",       time: "11:24" },
  { id: 2, sev: "serious",  icon: "bi bi-file-earmark-text",      title: "월간 종합 보고서 결재",     detail: "4월 월간 운영 보고서 — 최종 승인 필요 (마감 D-2)",   place: "경영전략본부 결재함", time: "10:45" },
  { id: 3, sev: "caution",  icon: "bi bi-cash-stack",             title: "분기 예산 집행률 알림",     detail: "Q2 IT 인프라 예산 78% 집행 — 목표치 초과",            place: "예산 모니터",         time: "10:12" },
  { id: 4, sev: "info",     icon: "bi bi-check-circle-fill",      title: "전 부서 SLA 달성",          detail: "이번 주 전 부서 SLA 98% 이상 달성",                   place: "전사 SLA 모니터",     time: "09:30" },
]);
const hasCritical = computed(() => liveAlerts.value.some(a => a.sev === "critical"));
function closeAlertsOnOutside(e) {
  if (showAlerts.value && !e.target.closest(".hdr-bell-wrap")) showAlerts.value = false;
}
if (typeof document !== "undefined") {
  document.addEventListener("click", closeAlertsOnOutside);
}
async function onGuideStep(step) {
  if (step?.tab && step.tab !== tab.value) {
    tab.value = step.tab;
  }
}
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
  { label: "전체 시스템",     value: "정상", unit: "",   icon: "bi bi-shield-check",             tone: "gr" },
  { label: "활성 이벤트",     value: 18,     unit: "건", icon: "bi bi-bell-fill",                tone: "rd" },
  { label: "처리 중 이벤트",  value: 36,     unit: "건", icon: "bi bi-hourglass-split",          tone: "or" },
  { label: "카메라 온라인",   value: 98,     unit: "%",  icon: "bi bi-camera-video-fill",        tone: "bl", sub: "2,450 / 2,500" },
  { label: "OCR 정상률",      value: 96,     unit: "%",  icon: "bi bi-card-text",                tone: "pl" },
  { label: "속도 이상 처리율", value: 97,    unit: "%",  icon: "bi bi-speedometer2",             tone: "gr" },
  { label: "데이터 수집률",   value: 98,     unit: "%",  icon: "bi bi-cloud-arrow-down-fill",    tone: "cy" },
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

/* ── topNav 탭별 통합 데이터 ── */

/* 운영현황 (ops) — 시설운영팀 요약 */
const opsKpis = [
  { label: "전체 가동률",     value: "99.6%",  delta: "+0.2",  tone: "gr", icon: "bi bi-activity" },
  { label: "온라인 카메라",   value: "243/247", delta: "-2",   tone: "yl", icon: "bi bi-camera-video-fill" },
  { label: "평균 네트워크 지연", value: "128ms",  delta: "+18", tone: "yl", icon: "bi bi-wifi" },
  { label: "활성 장애",       value: "3건",     delta: "-2",   tone: "rd", icon: "bi bi-exclamation-triangle-fill" },
];
const opsServers = [
  { name: "ocr-srv-01",   role: "OCR 처리",   cpu: 42, mem: 58, disk: 72, status: "정상", tone: "gr" },
  { name: "stream-srv-02", role: "스트림",    cpu: 68, mem: 71, disk: 45, status: "주의", tone: "yl" },
  { name: "edge-04",      role: "엣지 분석",  cpu: 35, mem: 48, disk: 88, status: "정상", tone: "gr" },
  { name: "db-master",    role: "DB 마스터",  cpu: 28, mem: 65, disk: 52, status: "정상", tone: "gr" },
];

/* 지도 (map) — 교통정보센터 요약 */
const mapRoadStats = [
  { road: "강변북로",   speed: 42, level: "혼잡", tone: "or", events: 3 },
  { road: "올림픽대로", speed: 56, level: "보통", tone: "yl", events: 1 },
  { road: "내부순환로", speed: 38, level: "정체", tone: "rd", events: 2 },
  { road: "동부간선",   speed: 64, level: "원활", tone: "gr", events: 0 },
  { road: "경부고속",   speed: 71, level: "원활", tone: "gr", events: 1 },
];

/* 이벤트 (events) — 전 부서 이벤트 누적 */
const allEvents = [
  { time: "14:32", dept: "교통정보센터", type: "교통사고",  detail: "강변북로 한남TG 2개 차로 통제", tone: "rd" },
  { time: "14:24", dept: "단속관리팀",   type: "과속 단속", detail: "신규 후보 5건 검토 대기 큐 추가",  tone: "or" },
  { time: "14:18", dept: "시설운영팀",   type: "장비 장애", detail: "NSN-N-0023 RTSP 타임아웃",        tone: "rd" },
  { time: "13:50", dept: "교통분석팀",   type: "AI 인사이트", detail: "피크시간 악화 구간 1개 증가",   tone: "yl" },
  { time: "13:32", dept: "시설운영팀",   type: "네트워크",  detail: "강남 권역 평균 지연 286ms",        tone: "yl" },
  { time: "11:08", dept: "교통정보센터", type: "차량 고장", detail: "올림픽대로 가양 갓길 정차",        tone: "yl" },
  { time: "10:00", dept: "시설운영팀",   type: "점검 완료", detail: "OCR 서버 4대 재가동 확인",         tone: "gr" },
];

/* 카메라 (cams) — 전 부서 카메라 통합 */
const allCamStats = { online: 243, offline: 2, error: 2, total: 247 };
const camsByDept = [
  { dept: "교통정보센터", total: 95,  online: 94, offline: 1, error: 0 },
  { dept: "시설운영팀",   total: 152, online: 149, offline: 1, error: 2 },
];
const recentCamIssues = [
  { id: "NSN-N-0023", name: "내부순환로 03K+150", status: "장애", since: "12분", tone: "rd" },
  { id: "CAM-O-019",  name: "올림픽대로 가양IC", status: "오프라인", since: "1시간 8분", tone: "rd" },
  { id: "CAM-K-008",  name: "강변북로 한남",     status: "오류",     since: "32분", tone: "or" },
];

/* OCR (ocr) — 단속관리팀 OCR 결과 요약 */
const ocrSummary = {
  todayTotal: 1842,
  success: 1763,
  failed: 79,
  successRate: 95.7,
  avgConf: 94.2,
  duplicates: 286,
};
const recentOcr = [
  { time: "14:32:18", plate: "12가 4567", cam: "강변북로", conf: 97, dir: "in",  status: "FLOW_EVENT_CREATED" },
  { time: "14:31:22", plate: "34더 5678", cam: "내부순환", conf: 92, dir: "out", status: "FLOW_EVENT_CREATED" },
  { time: "14:30:11", plate: "11가 2233", cam: "강변북로", conf: 98, dir: "in",  status: "FLOW_EVENT_CREATED" },
  { time: "14:29:47", plate: "미인식",     cam: "올림픽",  conf: 0,  dir: "-",   status: "OCR_FAILED" },
  { time: "14:29:33", plate: "78사 4321", cam: "동부간선", conf: 89, dir: "out", status: "FLOW_EVENT_CREATED" },
];

/* 통계 (stats) — 교통분석팀 요약 */
const statsKpis = [
  { label: "총 감지 차량",   value: "2,418",  unit: "대",  diff: "+8.2%", up: true,  icon: "bi bi-car-front-fill" },
  { label: "진입 (IN)",       value: "1,247",  unit: "대",  diff: "+5.4%", up: true,  icon: "bi bi-box-arrow-in-down-right" },
  { label: "이탈 (OUT)",     value: "1,171",  unit: "대",  diff: "+4.1%", up: true,  icon: "bi bi-box-arrow-up-right" },
  { label: "평균 통과 속도", value: "47",     unit: "km/h", diff: "-2.3%", up: false, icon: "bi bi-speedometer2" },
];
const statsByHour = [
  { hour: "00~06", traffic: 320,  level: "원활" },
  { hour: "06~09", traffic: 1840, level: "혼잡" },
  { hour: "09~12", traffic: 980,  level: "보통" },
  { hour: "12~15", traffic: 1120, level: "보통" },
  { hour: "15~18", traffic: 1450, level: "혼잡" },
  { hour: "18~21", traffic: 1680, level: "정체" },
  { hour: "21~24", traffic: 720,  level: "원활" },
];

/* 설정 (settings) — 전사 시스템 설정 */
const setAlertSound = ref(true);
const setAutoBackup = ref(true);
const setLogRetention = ref(90);
const setApiTimeout = ref(10);
const setMaintWindow = ref("03:00 ~ 04:00");
</script>

<style scoped>
/* shell/brand/snav/top/bell/bdg/user/seg-sub는 admin-shared.css */
.side { width: 200px; padding: 20px 12px; display: flex; flex-direction: column; overflow-y: auto; }
.snav-sep { display: flex; align-items: center; gap: 8px; padding: 16px 12px 8px; font-size: 12px; color: #34d399; font-weight: 700; border-top: 1px solid #1a2a45; margin-top: 12px; }
.snav-sep i { color: #34d399; }
.side-foot { font-size: 10.5px; opacity: .4; padding: 12px 6px 0; line-height: 1.6; }
.main { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.top h1 { font-size: 18px; font-weight: 600; color: #0c1f40; display: flex; align-items: center; gap: 10px; }
.top h1 .t-main { font-size: 22px; font-weight: 700; color: #0c1f40; }
.t-tag { background: linear-gradient(90deg, #8b5cf6, #3b82f6); color: #fff; font-size: 10px; font-weight: 800; padding: 3px 10px; border-radius: 4px; letter-spacing: 0.05em; }
.t-right { gap: 14px; }
.t-ic { font-size: 18px; opacity: .7; cursor: pointer; }
.seg-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.seg-h h2 { font-size: 15px; font-weight: 700; margin: 0; }
.seg-ts { font-size: 12px; opacity: .55; }

.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
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

.row-top { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }
.row-bot { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 12px; }
.row-top2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 12px; }
.row-bot2 { display: grid; grid-template-columns: 1fr; gap: 12px; }
.org-tiles.wide { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
.perm-grid.wide { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
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
.pnl h3 { font-size: 14px; font-weight: 700; margin: 0 0 14px; color: #0c1f40; }
.pnl-search { width: 100%; background: #ffffff; border: 1px solid #d8dfeb; color: #0c1f40; padding: 8px 12px; border-radius: 6px; font-size: 12.5px; margin-bottom: 12px; }
.pnl-search::placeholder { color: #94a3b8; }
.pnl-tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; color: #0c1f40; }
.pnl-tbl th, .pnl-tbl td { padding: 9px 10px; text-align: left; border-bottom: 1px solid #e3eaf4; }
.pnl-tbl th { font-weight: 700; color: #4a5b78; font-size: 11.5px; background: #f5f8fd; }
.pnl-tbl .mono { font-family: "JetBrains Mono", monospace; color: #1e293b; }
.pnl-tbl .dn { font-weight: 700; color: #0c1f40; }
.pnl-empty { text-align: center; color: #94a3b8; padding: 24px 0; }
.stat { padding: 3px 10px; border-radius: 100px; font-size: 11px; font-weight: 700; }
.stat.ok, .stat.gr { background: #d1fae5; color: #047857; }
.stat.wn, .stat.yl { background: #fef3c7; color: #b45309; }
.stat.or { background: #fed7aa; color: #9a3412; }
.stat.no, .stat.rd { background: #fee2e2; color: #b91c1c; }
.stat.bl { background: #dbeafe; color: #1e40af; }
.btn-mini { background: #eff6ff; border: 1px solid #bfdbfe; color: #2563eb; padding: 4px 10px; border-radius: 4px; font-size: 11.5px; cursor: pointer; font-weight: 600; }
.btn-mini:hover { background: #dbeafe; }
.ms-sub { font-size: 11px; color: #5b6b85; max-width: 360px; line-height: 1.6; }
.set-row { display: grid; grid-template-columns: 220px 1fr; gap: 12px; align-items: center; padding: 10px 0; border-bottom: 1px solid #e3eaf4; font-size: 13px; color: #2c3a52; }
.set-row label { font-weight: 600; color: #0c1f40; }
.set-row input[type="number"], .set-row input[type="text"], .set-row select {
  background: #ffffff; border: 1px solid #d8dfeb; color: #0c1f40;
  padding: 6px 10px; border-radius: 5px; font-size: 12.5px; max-width: 200px;
}
.set-row input[type="checkbox"] { accent-color: #2563eb; width: 16px; height: 16px; cursor: pointer; }
.btn-save { margin-top: 14px; background: #2563eb; color: #fff; border: 0; padding: 9px 18px; border-radius: 6px; font-size: 13px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.btn-save:hover { background: #1d4ed8; }
.set-msg { margin-top: 10px; font-size: 12px; color: #059669; font-weight: 600; display: inline-block; margin-left: 12px; }

.su-rep-grid { display: grid; grid-template-columns: 1fr; gap: 10px; }
.su-rep {
  display: flex; align-items: center; gap: 14px;
  background: #f5f8fd;
  border: 1px solid #e3eaf4;
  border-radius: 8px; padding: 16px 18px;
  transition: background 0.15s, border-color 0.15s;
}
.su-rep:hover { background: #eff6ff; border-color: #bfdbfe; }
.su-rep > i { font-size: 26px; color: #2563eb; flex-shrink: 0; }
.sr-body { flex: 1; min-width: 0; }
.sr-t { font-size: 14.5px; font-weight: 700; color: #0c1f40; margin-bottom: 4px; }
.sr-d { font-size: 12.5px; color: #5b6b85; }
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

/* ── topNav 탭별 통합 뷰 ── */
.map-overview {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 16px;
  align-items: start;
}
.map-stub-card {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
  min-height: 220px;
  background: #f5f8fd;
  border: 1px dashed #c9d4e3;
  border-radius: 8px;
  text-align: center;
  padding: 24px;
}
.map-stub-card > i { font-size: 48px; color: #2563eb; }
.map-stub-card .ms-t { font-size: 14.5px; font-weight: 700; color: #0c1f40; }
.map-stub-card .ms-sub { font-size: 12.5px; color: #5b6b85; }

.stat-bar {
  width: 100%; height: 8px;
  background: #e3eaf4;
  border-radius: 4px;
  overflow: hidden;
}
.stat-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  border-radius: 4px;
  transition: width 0.3s;
}

/* 설정 그리드 */
.su-set-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
  margin-bottom: 14px;
}
.su-set-blk {
  background: #f5f8fd;
  border: 1px solid #e3eaf4;
  border-radius: 8px;
  padding: 14px 16px;
}
.su-set-blk h4 {
  font-size: 14px; font-weight: 700; color: #0c1f40;
  margin: 0 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e3eaf4;
}
.su-set-blk .set-row { padding: 8px 0; border-bottom: 1px solid #eef2f9; }
.su-set-blk .set-row:last-child { border-bottom: 0; }

@media (max-width: 1100px) {
  .map-overview { grid-template-columns: 1fr; }
}
</style>
