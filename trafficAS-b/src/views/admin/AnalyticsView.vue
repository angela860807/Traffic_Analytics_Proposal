<template>
  <div class="an-shell">
    <div class="body">
      <aside class="filter">
        <RouterLink to="/" class="brand">
          Traffic <em>AS</em>
        </RouterLink>
        <nav class="snav">
          <button v-for="m in analysisMenu" :key="m.id" class="snav-i" :class="{ on: anaTab === m.id }" @click="anaTab = m.id">
            <i :class="m.icon"></i>{{ m.label }}
          </button>
        </nav>



        <div class="data-up">
          <div class="du-l">데이터 업데이트</div>
          <div class="du-r">{{ dataUpdated }} <i class="bi bi-arrow-clockwise"></i></div>
        </div>
      </aside>

      <div class="content">
        <header class="top">
          <h1><a class="t-main" @click="goHome">교통분석팀</a></h1>
          <div class="t-right">
            <span class="hdr-time"><i class="bi bi-clock"></i> 마지막 업데이트 <strong>{{ dataUpdated }}</strong></span>
            <button class="km-toggle" :class="{ on: autoRefresh }" @click="autoRefresh = !autoRefresh" :aria-pressed="autoRefresh">
              <span class="km-dot"></span>
              <span class="km-lab">자동 새로고침</span>
              <span class="km-state">{{ autoRefresh ? 'ON' : 'OFF' }}</span>
            </button>
            <DeptSwitcher />
            <div class="t-user"><i class="bi bi-person-circle"></i> 교통분석팀 매니저 <i class="bi bi-chevron-down"></i></div>
          </div>
        </header>

        <section class="ctx-bar" v-if="anaTab === 'dashboard'">
          <div class="ctx-grp">
            <span class="ctx-lab"><i class="bi bi-arrow-left-right"></i> 비교 기준</span>
            <select class="ctx-sel" v-model="compareBase">
              <option value="prev">전일</option>
              <option value="prevWeek">전주 동일 요일</option>
              <option value="avg7">최근 7일 평균</option>
            </select>
          </div>
          <div class="ctx-grp">
            <span class="ctx-lab"><i class="bi bi-calendar3"></i> 기간</span>
            <div class="ctx-seg">
              <button v-for="p in periods" :key="p.id"
                class="ctx-seg-b" :class="{ on: period === p.id }"
                @click="period = p.id">{{ p.label }}</button>
            </div>
            <span class="ctx-date">{{ dateRange }}</span>
          </div>
          <div class="ctx-grp">
            <span class="ctx-lab"><i class="bi bi-clock"></i> 시간대</span>
            <select class="ctx-sel" v-model="timeSlot">
              <option value="all">전체 시간</option>
              <option value="am">오전 (06~12시)</option>
              <option value="pm">오후 (12~18시)</option>
              <option value="rush">출퇴근 (07~09, 17~19)</option>
              <option value="night">야간 (22~05시)</option>
            </select>
          </div>
          <div class="ctx-acts">
            <button class="ctx-act bl" @click="opMsg = '통계 조회 실행'" title="통계 조회"><i class="bi bi-bar-chart"></i> 통계</button>
            <button class="ctx-act bl" @click="opMsg = '기간 비교 실행'" title="기간 비교"><i class="bi bi-calendar3"></i> 비교</button>
            <button class="ctx-act gr" @click="opMsg = '리포트 생성 시작'" title="리포트 생성"><i class="bi bi-file-earmark-text"></i> 리포트</button>
            <button class="ctx-act pl" @click="opMsg = 'CSV 내보내기 완료'" title="CSV 내보내기"><i class="bi bi-download"></i> CSV</button>
          </div>
        </section>
        <div v-if="opMsg && anaTab === 'dashboard'" class="ctx-msg">{{ opMsg }}</div>

        <section class="insight-strip" v-if="anaTab === 'dashboard'">
          <div class="is-h"><i class="bi bi-clipboard-data"></i> 분석 인사이트</div>
          <div class="is-list">
            <div class="is-card" v-for="(ins, i) in aiInsights" :key="i">
              <i :class="ins.icon" :style="{ color: ins.color }"></i>
              <div>
                <div class="is-t">{{ ins.title }}</div>
                <div class="is-d">{{ ins.detail }}</div>
              </div>
            </div>
          </div>
          <button class="is-more" @click="anaTab = 'insight'">상세 <i class="bi bi-arrow-right"></i></button>
        </section>

        <section class="row-cmp" v-if="anaTab === 'dashboard'">
          <div class="cmp-area">
            <div class="cmp-h">
              <h3>구간 성능 비교 <i class="bi bi-info-circle"></i></h3>
            </div>
            <div class="cmp-grid">
              <div class="cm-chart">
                <div class="cm-head">
                  <h4>구간별 속도 비교 <span class="cm-u">(km/h)</span></h4>
                  <div class="cm-legend-ext">
                    <span><span class="lg-dot bl"></span>금일</span>
                    <span><span class="lg-dot gy"></span>전일</span>
                    <span><span class="lg-dot gr"></span>최근 7일 평균</span>
                  </div>
                </div>
                <div ref="cmpChartEl" class="cm-echart"></div>
              </div>

              <div class="cm-chart">
                <div class="cm-head">
                  <h4>시간대별 속도 추이 <span class="cm-u">(km/h)</span></h4>
                  <div class="cm-legend-ext">
                    <span><span class="lg-dot bl"></span>금일</span>
                    <span><span class="lg-dot gy"></span>전일</span>
                    <span><span class="lg-dot gr"></span>최근 7일 평균</span>
                  </div>
                </div>
                <div ref="hourChartEl" class="cm-echart"></div>
              </div>
            </div>
          </div>

        </section>

        <!-- 분석 인사이트 상세 탭 -->
        <section v-if="anaTab === 'insight'" class="tab-panel">
          <div class="tp-h">
            <h2><i class="bi bi-clipboard-data"></i> 분석 인사이트 상세</h2>
            <span class="tp-sub">AI 분석 · 최근 24시간 · {{ aiInsights.length }}건</span>
          </div>
          <div class="ins-grid">
            <div class="ins-detail" v-for="(ins, i) in insightDetails" :key="i">
              <div class="id-h">
                <i :class="ins.icon" :style="{ color: ins.color }"></i>
                <div class="id-title">
                  <div class="id-t">{{ ins.title }}</div>
                  <div class="id-sub">{{ ins.detail }}</div>
                </div>
                <span class="id-impact" :class="ins.tone">영향도 {{ ins.impact }}</span>
              </div>
              <div class="id-metrics">
                <div class="id-m"><span>대상 구간</span><strong>{{ ins.target }}</strong></div>
                <div class="id-m"><span>변동률</span><strong :class="ins.dTone">{{ ins.change }}</strong></div>
                <div class="id-m"><span>발생 빈도</span><strong>{{ ins.freq }}</strong></div>
                <div class="id-m"><span>지속 시간</span><strong>{{ ins.duration }}</strong></div>
              </div>
              <div class="id-actions">
                <div class="id-act-h"><i class="bi bi-lightbulb"></i> 권장 조치</div>
                <ul>
                  <li v-for="(a, j) in ins.actions" :key="j">{{ a }}</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        <!-- 구간 분석 탭 -->
        <section v-if="anaTab === 'section'" class="tab-panel">
          <div class="tp-h">
            <h2><i class="bi bi-bezier2"></i> 구간 분석</h2>
            <span class="tp-sub">{{ segKpis.length }}개 구간 · {{ activeRoadLabel }}</span>
          </div>
          <div class="tp-stat-row">
            <div class="tp-st"><span>평균 속도</span><strong>{{ metrics.avgSpeed }}<small>km/h</small></strong></div>
            <div class="tp-st"><span>혼잡 구간</span><strong class="rd">{{ metrics.congSections }}<small>개</small></strong></div>
            <div class="tp-st"><span>전일 대비</span><strong class="up">▲ {{ metrics.changeDelta }}%</strong></div>
            <div class="tp-st"><span>상시 혼잡</span><strong>{{ metrics.recurringJam }}<small>개</small></strong></div>
          </div>
          <table class="tp-tbl">
            <thead>
              <tr><th>구간</th><th>평균 속도</th><th>전일 대비</th><th>피크 시간</th><th>통행량</th><th>혼잡도</th></tr>
            </thead>
            <tbody>
              <tr v-for="r in segKpis" :key="r.name">
                <td><strong>{{ r.name }}</strong></td>
                <td class="mono"><strong>{{ r.speed }}</strong> km/h</td>
                <td><span :class="r.dTone" class="mono">{{ r.delta }}</span></td>
                <td class="mono">{{ r.peak }}</td>
                <td class="mono">{{ (r.speed * 80).toLocaleString() }}대/h</td>
                <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- 교차로 분석 탭 -->
        <section v-if="anaTab === 'cross'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-diagram-3"></i> 교차로 분석</h2><span class="tp-sub">3개 주요 교차로 · 신호 효율 평균 71%</span></div>
          <div class="tp-grid">
            <div class="tp-card" v-for="x in crossroads" :key="x.name">
              <div class="tpc-name"><i class="bi bi-stoplights" :style="{ color: x.tone === 'rd' ? '#dc2626' : x.tone === 'or' ? '#b45309' : '#059669' }"></i> {{ x.name }}</div>
              <div class="tpc-row"><span>평균 대기</span><strong class="mono">{{ x.wait }}초</strong></div>
              <div class="tpc-row"><span>혼잡도</span><span class="cg-tag" :class="x.tone">{{ x.level }}</span></div>
              <div class="tpc-row"><span>통행량 (시간)</span><strong class="mono">{{ x.vol.toLocaleString() }}대</strong></div>
              <div class="tpc-row"><span>신호 효율</span><strong class="mono" :class="x.effTone">{{ x.eff }}%</strong></div>
              <div class="tpc-row"><span>좌회전 비율</span><strong class="mono">{{ x.leftPct }}%</strong></div>
              <div class="tpc-row"><span>보행 통과</span><strong class="mono">{{ x.pedPass }}건/h</strong></div>
            </div>
          </div>
        </section>

        <!-- 시간대 분석 탭 -->
        <section v-if="anaTab === 'time'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-clock"></i> 시간대 분석</h2><span class="tp-sub">24시간 평균 · 전일 대비 변동</span></div>
          <table class="tp-tbl">
            <thead><tr><th>시간대</th><th>평균 속도</th><th>전일 대비</th><th>혼잡 구간</th><th>통행량</th><th>특징</th></tr></thead>
            <tbody>
              <tr v-for="t in timeSlots" :key="t.slot">
                <td><strong>{{ t.slot }}</strong></td>
                <td class="mono"><strong>{{ t.speed }}</strong> km/h</td>
                <td><span :class="t.dTone" class="mono">{{ t.delta }}</span></td>
                <td><span class="cg-tag" :class="t.tone">{{ t.level }}</span> {{ t.cong }}</td>
                <td class="mono">{{ t.vol.toLocaleString() }}대/h</td>
                <td>{{ t.note }}</td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- 교통통계 탭 (교통정보센터에서 이관) -->
        <section v-if="anaTab === 'stats'" class="tab-panel">
          <div class="tp-h">
            <h2><i class="bi bi-bar-chart"></i> 교통통계</h2>
            <span class="tp-sub">시간대별 평균 속도 추이</span>
          </div>
          <div class="stats-card">
            <div class="stats-head">
              <div class="stats-meta">
                <span class="stats-lab">구간</span>
                <strong>강변북로 (구리 → 한남)</strong>
              </div>
              <div class="stats-tabs">
                <button v-for="t in statsChartTabs" :key="t.id"
                  class="stats-t" :class="{ on: statsChartTab === t.id }"
                  @click="statsChartTab = t.id">{{ t.label }}</button>
              </div>
            </div>
            <div class="stats-kpi-row">
              <div class="stats-kpi"><span>평균 속도</span><strong>{{ statsAvg }}<small>km/h</small></strong></div>
              <div class="stats-kpi"><span>최저</span><strong class="rd">32<small>km/h</small></strong></div>
              <div class="stats-kpi"><span>최고</span><strong class="up">82<small>km/h</small></strong></div>
              <div class="stats-kpi"><span>표본 구간</span><strong>{{ statsX.length }}<small>지점</small></strong></div>
            </div>
            <svg class="stats-line" viewBox="0 0 400 160" preserveAspectRatio="none">
              <defs>
                <linearGradient id="sg-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#2563eb" stop-opacity="0.35"/>
                  <stop offset="100%" stop-color="#2563eb" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <line v-for="y in [32, 64, 96, 128]" :key="y" :x1="0" :y1="y" :x2="400" :y2="y" stroke="#e7edf6" stroke-dasharray="3 5"/>
              <path :d="`${statsLine} L400,160 L0,160 Z`" fill="url(#sg-fill)"/>
              <path :d="statsLine" fill="none" stroke="#2563eb" stroke-width="2.5"/>
            </svg>
            <div class="stats-x">
              <span v-for="x in statsX" :key="x">{{ x }}</span>
            </div>
          </div>
        </section>

        <!-- 사고·이벤트 분석 탭 -->
        <section v-if="anaTab === 'incident'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-exclamation-triangle"></i> 사고·이벤트 분석</h2><span class="tp-sub">최근 24시간 · 진행 1건 / 복구 2건</span></div>
          <div class="tp-stat-row">
            <div class="tp-st"><span>총 발생</span><strong>3<small>건</small></strong></div>
            <div class="tp-st"><span>진행 중</span><strong class="rd">1<small>건</small></strong></div>
            <div class="tp-st"><span>평균 복구</span><strong class="mono">31<small>분</small></strong></div>
            <div class="tp-st"><span>영향 거리</span><strong class="mono">4.2<small>km</small></strong></div>
          </div>
          <table class="tp-tbl">
            <thead><tr><th>발생 시각</th><th>구간</th><th>유형</th><th>지속</th><th>영향 거리</th><th>영향</th><th>상태</th></tr></thead>
            <tbody>
              <tr v-for="ev in incidents" :key="ev.id">
                <td class="mono">{{ ev.time }}</td>
                <td>{{ ev.place }}</td>
                <td>{{ ev.type }}</td>
                <td class="mono">{{ ev.dur }}</td>
                <td class="mono">{{ ev.dist }}km</td>
                <td><span class="cg-tag" :class="ev.impTone">{{ ev.impact }}</span></td>
                <td><span class="cg-tag" :class="ev.stTone">{{ ev.st }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- 보고서 관리 탭 -->
        <section v-if="anaTab === 'report'" class="tab-panel">
          <div class="tp-h">
            <h2><i class="bi bi-file-earmark-text"></i> 보고서 관리</h2>
            <span class="tp-sub">예약 {{ reservations.length }}건 · 저장 {{ savedAnalyses.length }}건 · 최근 발행 {{ recentReports.length }}건</span>
            <label class="tp-auto"><input type="checkbox" v-model="autoPublish" /> 자동 발행</label>
          </div>
          <div class="tp-dl-row">
            <button class="tp-dl" @click="downloadDeptReport('analytics', 'daily')"><i class="bi bi-download"></i> 일일 교통흐름 리포트 (CSV)</button>
            <button class="tp-dl" @click="downloadDeptReport('analytics', 'weekly')"><i class="bi bi-download"></i> 주간 구간 성능 분석 (CSV)</button>
          </div>

          <div class="tp-sec-h">
            <h3 class="tp-sec">최근 발행</h3>
          </div>
          <table class="tp-tbl">
            <thead><tr><th>보고서명</th><th>발행일</th><th>발행자</th><th>크기</th><th>조회</th><th>상태</th><th></th></tr></thead>
            <tbody>
              <tr v-for="r in recentReports" :key="r.t">
                <td><strong>{{ r.t }}</strong></td>
                <td class="mono">{{ r.date }}</td>
                <td>{{ r.by }}</td>
                <td class="mono">{{ r.size }}</td>
                <td class="mono"><i class="bi bi-eye"></i> {{ r.views }}</td>
                <td><span class="cg-tag" :class="r.tone === 'ok' ? 'gr' : 'bl'">{{ r.st }}</span></td>
                <td><button class="tp-dl-sm" @click="downloadDeptReport('analytics', r.t.includes('주간') || r.t.includes('월간') ? 'weekly' : 'daily')"><i class="bi bi-download"></i></button></td>
              </tr>
            </tbody>
          </table>
          <div class="tp-2col">
            <div>
              <div class="tp-sec-h">
                <h3 class="tp-sec">보고서 예약 현황</h3>
                <button class="tp-add"><i class="bi bi-plus-lg"></i> 예약 추가</button>
              </div>
              <table class="tp-tbl">
                <thead><tr><th>보고서명</th><th>주기</th><th>다음 실행</th><th>수신자</th><th>상태</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="r in reservations" :key="r.id">
                    <td><strong>{{ r.name }}</strong></td><td>{{ r.cycle }}</td><td class="mono">{{ r.next }}</td>
                    <td class="mono">{{ r.to }}</td>
                    <td><span class="cg-tag" :class="r.tone === 'ok' ? 'gr' : 'or'">{{ r.st }}</span></td>
                    <td><button class="tp-dl-sm" @click="downloadDeptReport('analytics', r.cycle.includes('주') ? 'weekly' : 'daily')"><i class="bi bi-download"></i></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div>
              <div class="tp-sec-h">
                <h3 class="tp-sec">저장된 분석 목록</h3>
                <button class="tp-add"><i class="bi bi-plus-lg"></i> 분석 생성</button>
              </div>
              <table class="tp-tbl">
                <thead><tr><th>분석명</th><th>유형</th><th>기간</th><th>생성자</th><th>생성</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="s in savedAnalyses" :key="s.id">
                    <td><strong>{{ s.name }}</strong></td><td>{{ s.type }}</td>
                    <td class="mono">{{ s.range }}</td><td>{{ s.by }}</td><td class="mono">{{ s.created }}</td>
                    <td><button class="tp-dl-sm" @click="downloadDeptReport('analytics', s.type.includes('시간') ? 'weekly' : 'daily')"><i class="bi bi-download"></i></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- 설정 탭 -->
        <section v-if="anaTab === 'settings'" class="tab-panel">
          <div class="tp-h"><h2><i class="bi bi-gear"></i> 설정</h2><span class="tp-sub">대시보드 · 알람 · 데이터</span></div>
          <div class="tp-set-grid">
            <div class="tp-set-blk">
              <h3 class="tp-sec">분석 기본값</h3>
              <div class="tps-row"><label>기본 비교 기준</label>
                <select v-model="compareBase">
                  <option value="prev">전일</option><option value="prevWeek">전주 동일 요일</option><option value="avg7">최근 7일 평균</option>
                </select>
              </div>
              <div class="tps-row"><label>기본 시간대</label>
                <select v-model="timeSlot">
                  <option value="all">전체</option><option value="am">오전</option><option value="pm">오후</option><option value="rush">출퇴근</option><option value="night">야간</option>
                </select>
              </div>
              <div class="tps-row"><label>자동 새로고침</label><input type="checkbox" v-model="autoRefresh" /></div>
              <div class="tps-row"><label>리포트 자동 발행</label><input type="checkbox" /></div>
            </div>
            <div class="tp-set-blk">
              <h3 class="tp-sec">알람 임계값</h3>
              <div class="tps-row"><label>혼잡 경보 (속도 ≤)</label><input type="number" value="30" /> km/h</div>
              <div class="tps-row"><label>주의 경보 (속도 ≤)</label><input type="number" value="40" /> km/h</div>
              <div class="tps-row"><label>이벤트 알림</label><input type="checkbox" checked /></div>
              <div class="tps-row"><label>주말 알림 제외</label><input type="checkbox" /></div>
            </div>
            <div class="tp-set-blk">
              <h3 class="tp-sec">데이터·보관</h3>
              <div class="tps-row"><label>원본 로그 보관</label>
                <select><option>30일</option><option>60일</option><option>90일</option></select>
              </div>
              <div class="tps-row"><label>집계 보관</label>
                <select><option>1년</option><option>2년</option><option>영구</option></select>
              </div>
              <div class="tps-row"><label>익명화 처리</label><input type="checkbox" checked /></div>
            </div>
          </div>
        </section>

        <section class="row-mid" v-if="anaTab === 'dashboard'">
          <div class="card jam-map-card">
            <h3>도로 구간 혼잡 현황 <i class="bi bi-info-circle"></i></h3>
            <div ref="jamMapEl" class="jam-leaflet"></div>
            <div class="jm-legend">
              <span class="jl-label">평균 속도 (km/h)</span>
              <div class="jl-bar"></div>
              <div class="jl-ticks"><span>20</span><span>40</span><span>60</span><span>80</span></div>
            </div>
          </div>

          <div class="card kpi-tbl-card">
            <div class="kpi-head">
              <h3><i class="bi bi-bar-chart-line"></i> 구간 주요 지표</h3>
              <a class="ch-link" @click="anaTab = 'section'">전체 보기 ›</a>
            </div>
            <div class="kpi-mini-row">
              <div class="kpi-mini bl">
                <span class="km-l"><i class="bi bi-speedometer2"></i> 평균속도</span>
                <span class="km-v">{{ metrics.avgSpeed }}<small>km/h</small></span>
                <span class="km-d dn">▼ {{ metrics.speedDelta }}%</span>
              </div>
              <div class="kpi-mini rd">
                <span class="km-l"><i class="bi bi-exclamation-triangle"></i> 혼잡 구간</span>
                <span class="km-v">{{ metrics.congSections }}<small>개</small></span>
                <span class="km-d up-r">▲ {{ metrics.congDelta }}</span>
              </div>
              <div class="kpi-mini or">
                <span class="km-l"><i class="bi bi-graph-up-arrow"></i> 피크 악화</span>
                <span class="km-v">{{ metrics.recurringJam }}<small>구간</small></span>
                <span class="km-d up-r">▲ 1</span>
              </div>
              <div class="kpi-mini gr">
                <span class="km-l"><i class="bi bi-file-earmark-text"></i> 보고서</span>
                <span class="km-v">{{ metrics.changeDelta }}<small>건</small></span>
                <span class="km-d">예약</span>
              </div>
            </div>
            <table class="tbl-kpi">
              <thead><tr>
                <th><i class="bi bi-geo-alt"></i> 구간</th>
                <th><i class="bi bi-speedometer2"></i> 평균(km/h)</th>
                <th><i class="bi bi-arrow-down-up"></i> 전일 대비</th>
                <th><i class="bi bi-clock"></i> 피크</th>
                <th><i class="bi bi-traffic-light"></i> 혼잡도</th>
              </tr></thead>
              <tbody>
                <tr v-for="r in segKpis" :key="r.name">
                  <td><i class="bi bi-pin-map kpi-i"></i> {{ r.name }}</td>
                  <td class="mono">{{ r.speed }}</td>
                  <td><span :class="r.dTone" class="mono">{{ r.delta }}</span></td>
                  <td class="mono">{{ r.peak }}</td>
                  <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import { RouterLink } from "vue-router";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import echarts from "@/composables/echartsSetup";
import { loadOSMRoads, renderOSMRoads } from "@/composables/useOSMRoads";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import { useReportDownload } from "@/composables/useReportDownload";
const { downloadDeptReport } = useReportDownload();

const roads = [
  { id: "gangbyeon", label: "강변복로 (구리 → 한남)",     subs: ["구리IC", "토평IC", "강일IC", "미사IC", "암사IC", "천호대교", "한남IC"] },
  { id: "olympic",   label: "올림픽대로 (가양 → 여의도)", subs: ["가양IC", "성산IC", "양화대교", "여의도"] },
  { id: "naebu",     label: "내부순환로 (월계 → 성수)",   subs: ["월계IC", "정릉", "홍지문", "성수JC"] },
];

const sectQuery = ref("");
const activeRoad = ref("gangbyeon");
const period = ref("7d");
const timeSlot = ref("all");
const cmpTab = ref("speed");

const periods = [
  { id: "today", label: "오늘" },
  { id: "yest",  label: "어제" },
  { id: "7d",    label: "최근 7일" },
  { id: "30d",   label: "최근 30일" },
];

const filteredRoads = computed(() => {
  const q = sectQuery.value.trim().toLowerCase();
  if (!q) return roads;
  return roads.filter(r => r.label.toLowerCase().includes(q));
});

const activeRoadObj = computed(() => roads.find(r => r.id === activeRoad.value) || roads[0]);
const activeRoadLabel = computed(() => activeRoadObj.value.label);
const activeSubs = computed(() => activeRoadObj.value.subs);

const periodLabel = computed(() => periods.find(p => p.id === period.value)?.label || "");

const dateRange = computed(() => {
  const map = {
    today: "2026-05-17 ~ 2026-05-17",
    yest:  "2026-05-16 ~ 2026-05-16",
    "7d":  "2026-05-11 ~ 2026-05-17",
    "30d": "2026-04-18 ~ 2026-05-17",
  };
  return map[period.value];
});

const baseMetrics = {
  gangbyeon: { avgSpeed: 42, speedDelta: 6,  congSections: 12, congDelta: 2, changeDelta: 8, recurringJam: 4 },
  olympic:   { avgSpeed: 56, speedDelta: 3,  congSections:  6, congDelta: 1, changeDelta: 4, recurringJam: 2 },
  naebu:     { avgSpeed: 38, speedDelta: 9,  congSections: 14, congDelta: 3, changeDelta: 11,recurringJam: 5 },
};
const periodMult = { today: 1, yest: 1.05, "7d": 0.95, "30d": 0.9 };
const slotMult = { all: 1, am: 1.1, pm: 0.9, rush: 0.7, night: 1.25 };

const metrics = computed(() => {
  const b = baseMetrics[activeRoad.value];
  const k = periodMult[period.value] * slotMult[timeSlot.value];
  return {
    avgSpeed:     Math.round(b.avgSpeed * k),
    speedDelta:   b.speedDelta,
    congSections: Math.max(1, Math.round(b.congSections / k)),
    congDelta:    b.congDelta,
    changeDelta:  b.changeDelta,
    recurringJam: b.recurringJam,
  };
});

const cmpVariants = {
  "gangbyeon-speed": { today: "20,60 80,45 140,60 200,90 260,130 320,110 340,95", prev: "20,75 80,70 140,75 200,80 260,85 320,90 340,90", avg: "20,80 80,75 140,80 200,85 260,90 320,95 340,95" },
  "gangbyeon-time":  { today: "20,120 80,135 140,120 200,90 260,50 320,75 340,90", prev: "20,105 80,110 140,105 200,100 260,95 320,90 340,90", avg: "20,100 80,105 140,100 200,95 260,90 320,85 340,85" },
  "olympic-speed":   { today: "20,40 80,38 140,42 200,55 260,70 320,60 340,50", prev: "20,55 80,50 140,55 200,60 260,65 320,60 340,55", avg: "20,60 80,55 140,60 200,65 260,70 320,65 340,60" },
  "olympic-time":    { today: "20,130 80,135 140,128 200,100 260,75 320,90 340,110", prev: "20,115 80,120 140,115 200,110 260,105 320,110 340,115", avg: "20,110 80,115 140,110 200,105 260,100 320,105 340,110" },
  "naebu-speed":     { today: "20,80 80,70 140,90 200,115 260,140 320,130 340,120", prev: "20,90 80,85 140,95 200,100 260,105 320,100 340,95", avg: "20,95 80,90 140,100 200,105 260,110 320,105 340,100" },
  "naebu-time":      { today: "20,100 80,110 140,90 200,60 260,30 320,55 340,75", prev: "20,90 80,95 140,90 200,85 260,80 320,85 340,90", avg: "20,85 80,90 140,85 200,80 260,75 320,80 340,85" },
};

const cmpLines = computed(() => cmpVariants[`${activeRoad.value}-${cmpTab.value}`]);

const cmpDots = computed(() =>
  cmpLines.value.today.split(" ").map(p => {
    const [x, y] = p.split(",");
    return { x: Number(x), y: Number(y) };
  })
);

const aiInsights = [
  { icon: "bi bi-exclamation-circle-fill", color: "#dc2626", title: "피크시간 악화 구간 증가", detail: "출근 시간대 혼잡 악화 구간이 전일 대비 1개 증가했습니다." },
  { icon: "bi bi-exclamation-triangle-fill", color: "#b45309", title: "특정 구간 속도 저하", detail: "일산IC → 원효대교 구간 속도가 전일 대비 12% 감소했습니다." },
  { icon: "bi bi-check-circle-fill", color: "#059669", title: "전반적 흐름 개선", detail: "전체 평균 속도는 전일 대비 6% 개선되었습니다." },
  { icon: "bi bi-info-circle-fill", color: "#2563eb", title: "사고 영향 감소", detail: "사고 다발 구간의 영향이 전일 대비 18% 감소했습니다." },
];

const analysisMenu = [
  { id: "dashboard", icon: "bi bi-grid-1x2",            label: "대시보드" },
  { id: "insight",   icon: "bi bi-clipboard-data",      label: "분석 인사이트" },
  { id: "section",   icon: "bi bi-bezier2",             label: "구간 분석" },
  { id: "cross",     icon: "bi bi-diagram-3",           label: "교차로 분석" },
  { id: "time",      icon: "bi bi-clock",               label: "시간대 분석" },
  { id: "stats",     icon: "bi bi-bar-chart",           label: "교통통계" },
  { id: "incident",  icon: "bi bi-exclamation-triangle",label: "사고·이벤트 분석" },
  { id: "report",    icon: "bi bi-file-earmark-text",   label: "보고서 관리" },
  { id: "settings",  icon: "bi bi-gear",                label: "설정" },
];

// 교통통계 — 시간대별 평균 속도 (ControlView에서 이관)
const statsChartTabs = [
  { id: "1h", label: "1시간" },
  { id: "3h", label: "3시간" },
  { id: "6h", label: "6시간" },
  { id: "24h", label: "24시간" },
];
const statsChartTab = ref("3h");
const statsChartData = {
  "1h":  { line: "M0,46 L40,42 L80,50 L120,52 L160,58 L200,68 L240,78 L280,88 L320,108 L360,118 L400,128", x: ["13:30","13:45","14:00","14:15","14:30"], avg: 62 },
  "3h":  { line: "M0,30 L50,38 L100,35 L150,48 L200,55 L250,72 L300,90 L350,108 L400,128", x: ["11:30","12:15","13:00","13:45","14:30"], avg: 54 },
  "6h":  { line: "M0,28 L60,40 L120,52 L180,58 L240,70 L300,86 L360,110 L400,128", x: ["08:30","10:00","11:30","13:00","14:30"], avg: 48 },
  "24h": { line: "M0,90 L40,70 L80,40 L120,32 L160,55 L200,75 L240,55 L280,40 L320,60 L360,95 L400,110", x: ["00시","04시","08시","12시","16시","20시","24시"], avg: 56 },
};
const statsLine = computed(() => statsChartData[statsChartTab.value].line);
const statsX = computed(() => statsChartData[statsChartTab.value].x);
const statsAvg = computed(() => statsChartData[statsChartTab.value].avg);

const insightDetails = [
  { icon: "bi bi-exclamation-circle-fill", color: "#dc2626", tone: "rd",
    title: "피크시간 악화 구간 증가", detail: "출근 시간대 혼잡 악화 구간이 전일 대비 1개 증가",
    target: "강변북로 일산IC, 내부순환로 정릉", change: "+12%", dTone: "dn",
    freq: "5일 연속", duration: "07:00 ~ 09:30",
    actions: ["일산IC 우회 경로 안내 강화", "08:00 전 신호 사이클 단축 검토"] },
  { icon: "bi bi-exclamation-triangle-fill", color: "#b45309", tone: "or",
    title: "특정 구간 속도 저하", detail: "일산IC → 원효대교 구간 속도 전일 대비 12% 감소",
    target: "강변북로 일산IC ~ 원효대교", change: "-12%", dTone: "dn",
    freq: "당일 4회", duration: "누적 2시간 18분",
    actions: ["원효대교 진입 차로 분배 점검", "사고 다발 패턴 매칭 확인"] },
  { icon: "bi bi-check-circle-fill", color: "#059669", tone: "gr",
    title: "전반적 흐름 개선", detail: "전체 평균 속도 전일 대비 6% 개선",
    target: "전 구간", change: "+6%", dTone: "up",
    freq: "지속", duration: "당일 종일",
    actions: ["개선 요인 분석 리포트 자동 생성", "주간 보고서 반영"] },
  { icon: "bi bi-info-circle-fill", color: "#2563eb", tone: "bl",
    title: "사고 영향 감소", detail: "사고 다발 구간의 영향이 전일 대비 18% 감소",
    target: "강변북로 한남TG·올림픽 가양", change: "-18%", dTone: "up",
    freq: "주간 추세", duration: "최근 7일",
    actions: ["영향 감소 요인 추적", "유사 패턴 사전 경보 적용 검토"] },
];

const crossroads = [
  { name: "강남대로 × 테헤란로", wait: 87, level: "혼잡", tone: "rd", vol: 4820, eff: 58, effTone: "dn", leftPct: 22, pedPass: 312 },
  { name: "한남대교 북단",      wait: 62, level: "주의", tone: "or", vol: 3940, eff: 74, effTone: "yl", leftPct: 18, pedPass: 188 },
  { name: "여의도 환승센터",   wait: 38, level: "원활", tone: "gr", vol: 2110, eff: 86, effTone: "up", leftPct: 14, pedPass: 274 },
];

const timeSlots = [
  { slot: "출근 (07~09)", speed: 34, delta: "▼ 6",  dTone: "dn", level: "혼잡", tone: "rd", cong: 12, vol: 6800, note: "강변·올림픽 정체" },
  { slot: "오전 (09~12)", speed: 56, delta: "▲ 2",  dTone: "up", level: "주의", tone: "or", cong: 4,  vol: 5200, note: "점진적 해소" },
  { slot: "오후 (12~17)", speed: 58, delta: "▲ 1",  dTone: "up", level: "보통", tone: "yl", cong: 2,  vol: 4800, note: "안정" },
  { slot: "퇴근 (17~20)", speed: 28, delta: "▼ 9",  dTone: "dn", level: "혼잡", tone: "rd", cong: 15, vol: 7200, note: "전 구간 정체" },
  { slot: "야간 (22~05)", speed: 72, delta: "▲ 3",  dTone: "up", level: "원활", tone: "gr", cong: 0,  vol: 1400, note: "최저 통행량" },
];

const incidents = [
  { id: 1, time: "14:24", place: "강변북로 한남TG", type: "차량 정체 (사고)", dur: "8분",       dist: 1.2, impact: "혼잡 +12", impTone: "rd", st: "진행", stTone: "rd" },
  { id: 2, time: "11:08", place: "올림픽대로 가양", type: "차량 고장",         dur: "22분",     dist: 0.8, impact: "평균 -18%", impTone: "or", st: "복구", stTone: "gr" },
  { id: 3, time: "08:42", place: "내부순환 정릉",   type: "출근 정체",         dur: "1시간 14분", dist: 2.2, impact: "평균 -32%", impTone: "rd", st: "복구", stTone: "gr" },
];
const anaTab = ref("dashboard");
const autoRefresh = ref(true);
function goHome() {
  anaTab.value = "dashboard";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const compareBase = ref("prev");
const opMsg = ref("");
const dataUpdated = ref("2025-05-15  08:00");

const jamPoints = [
  { name: "구리IC",   x:  60, y: 124, ly: -12, speed: "48km/h", color: "#fbbf24" },
  { name: "독립IC",   x: 150, y: 124, ly: -12, speed: "52km/h", color: "#fbbf24" },
  { name: "강변IC",   x: 240, y: 130, ly: -12, speed: "61km/h", color: "#34d399" },
  { name: "마사IC",   x: 340, y: 138, ly: 18,  speed: "42km/h", color: "#fbbf24" },
  { name: "일산IC",   x: 430, y: 148, ly: -12, speed: "23km/h", color: "#ef4444" },
  { name: "원효대교", x: 510, y: 162, ly: 18,  speed: "27km/h", color: "#ef4444" },
  { name: "한남IC",   x: 565, y: 178, ly: 18,  speed: "55km/h", color: "#fbbf24" },
];

const segKpis = [
  { name: "강변IC",   speed: 61, delta: "▲ 4",  dTone: "up",   peak: "09시", cg: "원활", cgTone: "gr" },
  { name: "일산IC",   speed: 23, delta: "▼ 9",  dTone: "dn",   peak: "08시", cg: "혼잡", cgTone: "rd" },
  { name: "원효대교", speed: 27, delta: "▼ 11", dTone: "dn",   peak: "18시", cg: "혼잡", cgTone: "rd" },
];

const reservations = [
  { id: 1, name: "일일 교통흐름 리포트",   cycle: "매일 08:00",   next: "2025-05-16 08:00", to: "admin@trafficas.com", st: "예약", tone: "ok" },
  { id: 2, name: "주간 구간 성능 리포트", cycle: "매주 월 09:00", next: "2025-05-19 09:00", to: "team@trafficas.com",  st: "예약", tone: "ok" },
];

const savedAnalyses = [
  { id: 1, name: "일산IC 혼잡 원인 분석",       type: "구간 분석",  range: "2025-05-09 ~ 2025-05-15", created: "2025-05-15 07:45", by: "김분석" },
  { id: 2, name: "출근시간 속도 저하 구간 분석", type: "시간대 분석", range: "2025-05-09 ~ 2025-05-15", created: "2025-05-14 18:30", by: "김분석" },
];

// 최근 발행 보고서 (운영기획팀에서 흡수)
const autoPublish = ref(true);
const recentReports = [
  { t: "일일 운영 보고서",     date: "2026-05-19", by: "교통분석팀 김분석",  size: "2.4MB", views: 12, st: "발행", tone: "ok" },
  { t: "주간 성과 보고서",     date: "2026-05-12", by: "교통분석팀 정민혁",  size: "5.1MB", views: 38, st: "발행", tone: "ok" },
  { t: "5월 1주 이슈 리포트", date: "2026-05-08", by: "교통분석팀 이수진",  size: "1.8MB", views: 24, st: "발행", tone: "ok" },
  { t: "4월 월간 종합",       date: "2026-05-02", by: "교통분석팀 김분석",  size: "8.6MB", views: 56, st: "승인", tone: "appr" },
];

function resetFilters() {
  sectQuery.value = "";
  activeRoad.value = "gangbyeon";
  period.value = "7d";
  timeSlot.value = "all";
  cmpTab.value = "speed";
}

// === Leaflet 혼잡도 지도 ===
const jamMapEl = ref(null);
let jamMap = null;

const ICs = [
  { name: "구리IC",   lat: 37.5996, lng: 127.1387, speed: 48, color: "#fbbf24" },
  { name: "독립IC",   lat: 37.5751, lng: 127.1080, speed: 52, color: "#fbbf24" },
  { name: "강변IC",   lat: 37.5566, lng: 127.0890, speed: 61, color: "#34d399" },
  { name: "마사IC",   lat: 37.5470, lng: 127.0700, speed: 42, color: "#fbbf24" },
  { name: "일산IC",   lat: 37.5378, lng: 127.0460, speed: 23, color: "#ef4444" },
  { name: "원효대교", lat: 37.5318, lng: 127.0210, speed: 27, color: "#ef4444" },
  { name: "한남IC",   lat: 37.5258, lng: 126.9967, speed: 55, color: "#fbbf24" },
];

function speedToColor(s) {
  if (s < 30) return "#ef4444";
  if (s < 40) return "#fb923c";
  if (s < 60) return "#fbbf24";
  return "#34d399";
}

// === ECharts: 구간별 속도 비교 + 시간대별 속도 추이 ===
const cmpChartEl = ref(null);
const hourChartEl = ref(null);
let cmpChart = null;
let hourChart = null;

const cmpData = {
  cats: ["구리IC", "독립IC", "강변IC", "마사IC", "일산IC", "원효대교", "한남IC"],
  today: [48, 52, 61, 42, 23, 27, 55],
  prev:  [52, 54, 60, 45, 32, 35, 58],
  avg:   [54, 56, 62, 48, 38, 42, 60],
};
const hourData = {
  cats: ["00시", "04시", "08시", "12시", "16시", "20시", "24시"],
  today: [80, 78, 32, 58, 70, 88, 92],
  prev:  [78, 76, 40, 62, 68, 82, 88],
  avg:   [75, 74, 45, 60, 65, 80, 85],
};

function lineSeries(name, data, color, dashed = false) {
  return {
    name,
    type: "line",
    data,
    smooth: 0.35,
    symbol: "circle",
    symbolSize: 7,
    lineStyle: {
      width: dashed ? 2 : 3,
      color,
      type: dashed ? "dashed" : "solid",
      shadowBlur: dashed ? 0 : 10,
      shadowColor: color + "55",
    },
    itemStyle: { color, borderColor: "#fff", borderWidth: 1.5 },
    emphasis: { focus: "series", scale: 1.4 },
    areaStyle: dashed
      ? undefined
      : {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + "55" },
            { offset: 1, color: color + "00" },
          ]),
        },
    animationDuration: 1100,
    animationEasing: "cubicOut",
  };
}

function buildOption(d, redBandRange) {
  return {
    grid: { left: 50, right: 18, top: 14, bottom: 38 },
    legend: { show: false },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(12,31,64,0.95)",
      borderWidth: 0,
      padding: [8, 12],
      textStyle: {
        color: "#fff",
        fontSize: 12.5,
        fontFamily: "Inter, Pretendard, sans-serif",
      },
      axisPointer: {
        type: "line",
        lineStyle: { color: "#94a3b8", type: "dashed", width: 1 },
      },
    },
    xAxis: {
      type: "category",
      data: d.cats,
      boundaryGap: false,
      axisLine: { lineStyle: { color: "#c9d4e3" } },
      axisTick: { show: false },
      axisLabel: {
        color: "#4a5b78",
        fontSize: 12,
        fontWeight: 600,
        fontFamily: "Inter, Pretendard, sans-serif",
        margin: 10,
      },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: "#6b7a92",
        fontSize: 11.5,
        fontFamily: "IBM Plex Mono, monospace",
        formatter: "{value}",
      },
      splitLine: { lineStyle: { color: "#e7edf6", type: "dashed" } },
    },
    series: [
      lineSeries("최근 7일 평균", d.avg, "#10b981", false),
      lineSeries("전일", d.prev, "#94a3b8", true),
      {
        ...lineSeries("금일", d.today, "#2563eb", false),
        markArea: redBandRange
          ? {
              silent: true,
              itemStyle: { color: "rgba(239,68,68,0.10)" },
              label: {
                show: true,
                position: "insideTop",
                distance: 8,
                color: "#b91c1c",
                fontSize: 12,
                fontWeight: 800,
                fontFamily: "Inter, Pretendard, sans-serif",
                backgroundColor: "rgba(255,255,255,0.85)",
                padding: [3, 8],
                borderRadius: 4,
                overflow: "none",
              },
              data: [redBandRange],
            }
          : undefined,
        markPoint: {
          symbol: "pin",
          symbolSize: 38,
          data: [{ type: "min", name: "최저", itemStyle: { color: "#dc2626" } }],
          label: {
            color: "#fff",
            fontSize: 11,
            fontWeight: 700,
            formatter: "{c}",
          },
        },
      },
    ],
  };
}

function initCmpCharts() {
  if (cmpChartEl.value && !cmpChart) {
    cmpChart = echarts.init(cmpChartEl.value, null, { renderer: "canvas" });
    cmpChart.setOption(
      buildOption(cmpData, [{ name: "혼잡 구간", xAxis: "마사IC" }, { xAxis: "한남IC" }])
    );
    new ResizeObserver(() => cmpChart && cmpChart.resize()).observe(cmpChartEl.value);
  }
  if (hourChartEl.value && !hourChart) {
    hourChart = echarts.init(hourChartEl.value, null, { renderer: "canvas" });
    hourChart.setOption(
      buildOption(hourData, [{ name: "피크 시간대", xAxis: "08시" }, { xAxis: "12시" }])
    );
    new ResizeObserver(() => hourChart && hourChart.resize()).observe(hourChartEl.value);
  }
}

watch(anaTab, (v) => {
  if (v === "dashboard") nextTick(() => initCmpCharts());
});
window.addEventListener("resize", () => {
  cmpChart && cmpChart.resize();
  hourChart && hourChart.resize();
});

onMounted(async () => {
  nextTick(() => initCmpCharts());
  if (!jamMapEl.value) return;
  await new Promise(r => setTimeout(r, 50));
  try {
    jamMap = L.map(jamMapEl.value, {
      center: [37.5566, 127.0700],
      zoom: 11,
      minZoom: 9,
      maxZoom: 18,
      zoomControl: true,
      attributionControl: false,
    });
    const vworld = L.tileLayer(
      "https://xdworld.vworld.kr/2d/midnight/202002/{z}/{x}/{y}.png",
      { maxZoom: 19, maxNativeZoom: 18 }
    );
    const cartoDark = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
      { maxZoom: 19, maxNativeZoom: 19, subdomains: "abcd" }
    );
    vworld.on("tileerror", () => {
      jamMap.removeLayer(vworld);
      cartoDark.addTo(jamMap);
    });
    vworld.addTo(jamMap);

    // OSM Overpass에서 강변북로 일대 motorway/trunk만 → 가벼움
    const ways = await loadOSMRoads(
      "osm-roads-analytics-gangbyeon-v2",
      "37.51,126.97,37.60,127.14",
      ["motorway", "trunk"]
    );
    if (ways && ways.length > 0) {
      renderOSMRoads(jamMap, ways);
    }

    setTimeout(() => jamMap?.invalidateSize(), 200);
  } catch (e) {
    console.warn("[Analytics jam map]", e.message);
  }
});

onBeforeUnmount(() => {
  if (jamMap) { jamMap.remove(); jamMap = null; }
  if (cmpChart) { cmpChart.dispose(); cmpChart = null; }
  if (hourChart) { hourChart.dispose(); hourChart = null; }
});
</script>

<style scoped>
.an-shell { height: 100vh; overflow: hidden; display: flex; flex-direction: column; }
.an-shell .body { flex: 1; min-height: 0; overflow: hidden; }
.an-shell .content {
  flex: 1; min-height: 0; overflow: hidden;
  display: flex !important; flex-direction: column !important; gap: 10px !important;
  padding: 12px 16px !important;
}
.an-shell .row-cmp { flex: 1;    min-height: 0; gap: 12px !important; order: 2; }
.an-shell .row-mid { flex: 1.2;  min-height: 0; gap: 12px !important; order: 1; }
/* row-cmp 단일 컬럼 (인사이트 분리됨) */
.an-shell .row-cmp { grid-template-columns: 1fr !important; }

/* 카드 패딩/여백 조절 */
.an-shell .cmp-area,
.an-shell .jam-map-card,
.an-shell .kpi-tbl-card {
  padding: 10px 14px !important;
  min-height: 0;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden;
}
.an-shell .cmp-h,
.an-shell .jam-map-card h3,
.an-shell .kpi-tbl-card h3 {
  flex-shrink: 0;
  margin-bottom: 6px !important;
}
.an-shell .cmp-grid {
  flex: 1; min-height: 0;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 20px;
}
.an-shell .cm-chart {
  display: flex; flex-direction: column; min-height: 0;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  padding: 12px 14px;
  border-radius: 2px;
}
.an-shell .cm-chart h4 { flex-shrink: 0; margin: 0; }
.an-shell .cm-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px; margin-bottom: 8px; flex-shrink: 0; flex-wrap: wrap;
}
.an-shell .cm-legend-ext {
  display: inline-flex; gap: 14px; align-items: center;
  font-size: 12.5px; font-weight: 600; color: #0c1f40;
  font-family: "Inter, Pretendard", sans-serif;
}
.an-shell .cm-legend-ext span { display: inline-flex; align-items: center; gap: 5px; }
.an-shell .cm-legend-ext .lg-dot {
  display: inline-block; width: 10px; height: 10px; border-radius: 50%;
}
.an-shell .cm-legend-ext .lg-dot.bl { background: #2563eb; }
.an-shell .cm-legend-ext .lg-dot.gy { background: #94a3b8; }
.an-shell .cm-legend-ext .lg-dot.gr { background: #10b981; }
.an-shell .cm-echart {
  flex: 1; width: 100%; min-height: 220px; min-width: 0;
}

.an-shell .jam-leaflet { flex: 1; height: auto !important; min-height: 100px; }
.an-shell .jm-legend { flex-shrink: 0; }

.an-shell .tbl-kpi { width: 100%; border-collapse: collapse; table-layout: fixed; }
.an-shell .tbl-kpi th, .an-shell .tbl-kpi td {
  padding: 7px 8px !important;
  font-size: 13.5px !important;
  text-align: center !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.an-shell .tbl-kpi th { font-size: 12.5px !important; }
.an-shell .kpi-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 6px !important;
  flex-shrink: 0;
}
.an-shell .kpi-head h3 { margin: 0 !important; }
.an-shell .kpi-tbl-card .ch-link {
  color: #2563eb; font-size: 13px; font-weight: 700; cursor: pointer;
  text-decoration: none;
}
.an-shell .kpi-tbl-card .ch-link:hover { text-decoration: underline; }
.an-shell .kpi-head h3 i { color: #2563eb; margin-right: 5px; }
.an-shell .kpi-mini-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
  margin-bottom: 10px;
}
.an-shell .kpi-mini {
  background: #f1f5fb; border: 1px solid #c9d4e3; border-left: 3px solid #c9d4e3;
  border-radius: 4px; padding: 8px 10px;
  display: flex; flex-direction: column; gap: 2px;
  min-width: 0;
}
.an-shell .kpi-mini.bl { border-left-color: #2563eb; }
.an-shell .kpi-mini.rd { border-left-color: #dc2626; }
.an-shell .kpi-mini.or { border-left-color: #b45309; }
.an-shell .kpi-mini.gr { border-left-color: #059669; }
.an-shell .kpi-mini .km-l {
  font-size: 11.5px; font-weight: 600; color: #4a5b78;
  display: inline-flex; align-items: center; gap: 4px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.an-shell .kpi-mini .km-l i { color: inherit; opacity: 0.85; }
.an-shell .kpi-mini.bl .km-l i { color: #2563eb; }
.an-shell .kpi-mini.rd .km-l i { color: #dc2626; }
.an-shell .kpi-mini.or .km-l i { color: #b45309; }
.an-shell .kpi-mini.gr .km-l i { color: #059669; }
.an-shell .kpi-mini .km-v {
  font-family: "IBM Plex Mono", monospace;
  font-size: 18px; font-weight: 800; color: #0c1f40; line-height: 1.1;
}
.an-shell .kpi-mini .km-v small {
  font-size: 11px; font-weight: 600; color: #4a5b78; margin-left: 2px;
}
.an-shell .kpi-mini .km-d {
  font-family: "IBM Plex Mono", monospace;
  font-size: 11px; font-weight: 700;
}
.an-shell .kpi-mini .km-d.dn { color: #b91c1c; }
.an-shell .kpi-mini .km-d.up-r { color: #b45309; }
.an-shell .tbl-kpi th i { color: #2563eb; opacity: 0.85; margin-right: 4px; font-size: 12px; }
.an-shell .tbl-kpi .kpi-i { color: #2563eb; opacity: 0.7; margin-right: 4px; font-size: 12px; }

.an-shell .top { padding: 10px 16px !important; flex-shrink: 0; }
.an-shell .top h1 { font-size: 20px !important; }
.an-shell .top .t-main { font-size: 24px !important; }

/* ★ 탭 패널 (구간/교차로/시간대/사고/보고서/설정) - 빔프로젝트 시연용 */
.an-shell .tab-panel {
  flex: 1; min-height: 0; overflow: hidden;
  display: flex; flex-direction: column;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 20px 24px;
}
.an-shell .tp-h {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 2px solid #0c1f40;
  flex-shrink: 0;
}
.an-shell .tp-h h2 {
  font-size: 24px; font-weight: 800; color: #0c1f40;
  margin: 0; display: flex; align-items: center; gap: 10px;
  letter-spacing: -0.02em;
}
.an-shell .tp-h h2 i { color: #2563eb; font-size: 22px; }
.an-shell .tp-sub { font-size: 15px; color: #4a5b78; font-weight: 600; }

.an-shell .tp-tbl {
  width: 100%; border-collapse: collapse;
  font-size: 17px;
}
.an-shell .tp-tbl th {
  background: #e3e9f2;
  padding: 14px 14px;
  text-align: left;
  font-size: 15px;
  font-weight: 700;
  color: #4a5b78;
  border-bottom: 2px solid #c9d4e3;
  letter-spacing: -0.01em;
}
.an-shell .tp-tbl td {
  padding: 14px 14px;
  border-bottom: 1px solid #d8dfe9;
  color: #0c1f40;
}
.an-shell .tp-tbl tbody tr:hover { background: #f1f5fb; }

/* === 추가 디테일 === */
.an-shell .tp-stat-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
  margin-bottom: 14px;
}
.an-shell .tp-st {
  background: #f1f5fb; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 10px 14px; display: flex; flex-direction: column; gap: 4px;
}
.an-shell .tp-st span { font-size: 12px; color: #4a5b78; font-weight: 600; }
.an-shell .tp-st strong { font-size: 22px; font-weight: 800; color: #0c1f40; font-family: "IBM Plex Mono", monospace; }
.an-shell .tp-st strong small { font-size: 12px; color: #4a5b78; font-weight: 600; margin-left: 4px; }
.an-shell .tp-st .rd { color: #b91c1c !important; }
.an-shell .tp-st .up { color: #059669 !important; }

.an-shell .tp-sec-h {
  display: flex; align-items: center; justify-content: space-between;
  margin: 6px 0 8px;
}
.an-shell .tp-add {
  background: #2563eb; color: #fff; border: 0; padding: 6px 12px;
  border-radius: 4px; font-size: 13px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; gap: 4px;
}
.an-shell .tp-add:hover { background: #1d4ed8; }
.an-shell .tp-auto {
  margin-left: auto; display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; color: #4a5b78; cursor: pointer;
}
.an-shell .tp-auto input { accent-color: #2563eb; }
.an-shell .tp-dl-row { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.an-shell .tp-dl {
  background: #059669; color: #fff; border: 0; padding: 8px 14px;
  border-radius: 4px; font-size: 13px; font-weight: 700; cursor: pointer;
  display: inline-flex; align-items: center; gap: 6px;
}
.an-shell .tp-dl:hover { background: #047857; }
.an-shell .tp-dl-sm {
  background: rgba(5,150,105,0.12); color: #047857;
  border: 1px solid rgba(5,150,105,0.3);
  padding: 3px 8px; border-radius: 3px; cursor: pointer; font-size: 12px;
}
.an-shell .tp-dl-sm:hover { background: #059669; color: #fff; }

.an-shell .tp-set-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
}
.an-shell .tp-set-blk {
  background: #f1f5fb; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 14px 16px;
}
.an-shell .tp-set-blk .tp-sec {
  font-size: 14.5px; font-weight: 700; color: #0c1f40; margin: 0 0 10px;
  padding-bottom: 6px; border-bottom: 1px solid #c9d4e3;
}
.an-shell .tp-set-blk .tps-row {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
  font-size: 13.5px; color: #0c1f40;
}
.an-shell .tp-set-blk .tps-row label { flex: 1; font-weight: 600; }
.an-shell .tp-set-blk input[type="number"] {
  width: 64px; padding: 4px 6px; border: 1px solid #c9d4e3;
  border-radius: 3px; font-family: "IBM Plex Mono", monospace;
}
.an-shell .tp-set-blk select {
  padding: 4px 8px; border: 1px solid #c9d4e3; border-radius: 3px;
  background: #fff; font-size: 13px;
}

/* 인사이트 상세 */
.an-shell .ins-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  grid-auto-rows: 1fr;
  gap: 14px;
  flex: 1; min-height: 0; overflow: auto;
  align-items: stretch;
}
.an-shell .ins-detail {
  background: #ffffff; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 14px 16px; display: flex; flex-direction: column; gap: 10px;
  min-height: 0; min-width: 0;
}
.an-shell .ins-detail .id-actions { margin-top: auto; }
.an-shell .id-h {
  display: flex; align-items: flex-start; gap: 10px;
  padding-bottom: 10px; border-bottom: 1px solid #e7edf6;
}
.an-shell .id-h > i { font-size: 22px; flex-shrink: 0; margin-top: 2px; }
.an-shell .id-title { flex: 1; min-width: 0; }
.an-shell .id-t { font-size: 15px; font-weight: 800; color: #0c1f40; margin-bottom: 4px; }
.an-shell .id-sub { font-size: 12.5px; color: #4a5b78; line-height: 1.4; }
.an-shell .id-impact {
  padding: 3px 10px; border-radius: 100px; font-size: 11.5px; font-weight: 700;
  flex-shrink: 0; align-self: flex-start;
}
.an-shell .id-impact.rd { background: rgba(220,38,38,.12); color: #b91c1c; }
.an-shell .id-impact.or { background: rgba(180,83,9,.12); color: #b45309; }
.an-shell .id-impact.gr { background: rgba(5,150,105,.12); color: #047857; }
.an-shell .id-impact.bl { background: rgba(37,99,235,.12); color: #1d4ed8; }
.an-shell .id-metrics {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
}
.an-shell .id-m {
  background: #f1f5fb; border-radius: 3px; padding: 6px 8px;
  display: flex; flex-direction: column; gap: 2px;
}
.an-shell .id-m span { font-size: 11px; color: #4a5b78; font-weight: 600; }
.an-shell .id-m strong { font-size: 13.5px; font-weight: 800; color: #0c1f40; font-family: "IBM Plex Mono", monospace; }
.an-shell .id-m strong.dn { color: #b91c1c; }
.an-shell .id-m strong.up { color: #047857; }
.an-shell .id-actions { background: #fff8e6; border: 1px solid #f5d989; border-radius: 4px; padding: 10px 12px; }
.an-shell .id-act-h { font-size: 13px; font-weight: 700; color: #92400e; margin-bottom: 6px; display: inline-flex; align-items: center; gap: 5px; }
.an-shell .id-actions ul { margin: 0; padding-left: 20px; }
.an-shell .id-actions li { font-size: 13px; color: #0c1f40; line-height: 1.5; }

/* 교차로 카드 — 행 추가에 맞춰 살짝 컴팩트 */
.an-shell .tp-card .tpc-name { display: inline-flex; align-items: center; gap: 6px; }
.an-shell .tp-card .tpc-row .mono.dn { color: #b91c1c; }
.an-shell .tp-card .tpc-row .mono.up { color: #047857; }
.an-shell .tp-card .tpc-row .mono.yl { color: #b45309; }
.an-shell .tp-tbl strong { font-weight: 700; }
.an-shell .tp-tbl .mono { font-family: "IBM Plex Mono", monospace; }

.an-shell .cg-tag {
  display: inline-block; padding: 4px 10px; border-radius: 100px;
  font-size: 13.5px; font-weight: 800;
}
.an-shell .cg-tag.gr { background: rgba(4,120,87,.14); color: #047857; }
.an-shell .cg-tag.yl { background: rgba(180,83,9,.14); color: #b45309; }
.an-shell .cg-tag.or { background: rgba(180,83,9,.14); color: #b45309; }
.an-shell .cg-tag.rd { background: rgba(220,38,38,.14); color: #b91c1c; }
.an-shell .tp-tbl .up { color: #047857; font-weight: 700; }
.an-shell .tp-tbl .dn { color: #b91c1c; font-weight: 700; }

/* 교차로 분석 그리드 */
.an-shell .tp-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;
  flex: 1; min-height: 0;
}
.an-shell .tp-card {
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  border-left: 4px solid #2563eb;
  padding: 18px 20px;
  display: flex; flex-direction: column; gap: 10px;
}
.an-shell .tpc-name {
  font-size: 18px; font-weight: 800; color: #0c1f40;
  letter-spacing: -0.01em; padding-bottom: 10px;
  border-bottom: 1px solid #c9d4e3;
}
.an-shell .tpc-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 15.5px; color: #4a5b78;
}
.an-shell .tpc-row strong {
  font-size: 17px; color: #0c1f40; font-weight: 800;
}

/* 보고서 관리 2-column */
.an-shell .tp-2col {
  display: grid; grid-template-columns: 1fr 1fr; gap: 24px;
  flex: 1; min-height: 0; overflow: hidden;
}
.an-shell .tp-2col > div { display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.an-shell .tp-sec {
  font-size: 17px; font-weight: 800; color: #0c1f40;
  margin: 0 0 12px; padding-bottom: 8px;
  border-bottom: 1px solid #c9d4e3;
}

/* 설정 */
.an-shell .tp-set { display: flex; flex-direction: column; gap: 14px; max-width: 520px; }
.an-shell .tps-row {
  display: grid; grid-template-columns: 200px 1fr; align-items: center; gap: 14px;
  padding: 12px 14px;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
}
.an-shell .tps-row label {
  font-size: 16px; font-weight: 700; color: #0c1f40;
}
.an-shell .tps-row select {
  font-size: 15px; padding: 8px 10px;
  background: #ffffff; border: 1px solid #c9d4e3;
  font-family: inherit; color: #0c1f40;
}
.an-shell .tps-row input[type="checkbox"] {
  width: 22px; height: 22px; accent-color: #2563eb;
}

.an-shell .insight-strip { padding: 12px 16px !important; }

/* 비교 설정 컨텍스트 바 */
.an-shell .ctx-bar {
  display: flex; align-items: center; gap: 22px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 10px 16px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.an-shell .ctx-grp { display: inline-flex; align-items: center; gap: 8px; }
.an-shell .ctx-lab {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12.5px; font-weight: 700; color: #4a5b78;
}
.an-shell .ctx-lab i { color: #2563eb; font-size: 13px; }
.an-shell .ctx-sel {
  background: #f1f5fb; border: 1px solid #c9d4e3;
  color: #0c1f40; font-size: 13px; font-weight: 600;
  padding: 5px 10px; border-radius: 3px; cursor: pointer;
}
.an-shell .ctx-seg {
  display: inline-flex; background: #f1f5fb; border: 1px solid #c9d4e3;
  border-radius: 3px; overflow: hidden;
}
.an-shell .ctx-seg-b {
  background: none; border: 0; color: #4a5b78;
  font-size: 12.5px; font-weight: 600; padding: 5px 11px; cursor: pointer;
  border-right: 1px solid #c9d4e3;
}
.an-shell .ctx-seg-b:last-child { border-right: 0; }
.an-shell .ctx-seg-b.on { background: #2563eb; color: #fff; }
.an-shell .ctx-seg-b:hover:not(.on) { background: #e3e9f2; color: #0c1f40; }
.an-shell .ctx-date {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px; color: #6b7a92; margin-left: 4px;
}
.an-shell .ctx-acts {
  margin-left: auto;
  display: inline-flex; gap: 5px;
}
.an-shell .ctx-act {
  display: inline-flex; align-items: center; gap: 4px;
  background: #2563eb; color: #fff; border: 0;
  font-size: 12.5px; font-weight: 700;
  padding: 6px 12px; border-radius: 3px; cursor: pointer;
}
.an-shell .ctx-act i { font-size: 12.5px; }
.an-shell .ctx-act:hover { background: #1d4ed8; }
.an-shell .ctx-act.bl { background: #2563eb; }
.an-shell .ctx-act.bl:hover { background: #1d4ed8; }
.an-shell .ctx-act.gr { background: #059669; }
.an-shell .ctx-act.gr:hover { background: #047857; }
.an-shell .ctx-act.pl { background: #7c3aed; }
.an-shell .ctx-act.pl:hover { background: #6d28d9; }
/* 교통통계 카드 (이관) */
.an-shell .stats-card {
  background: #ffffff; border: 1px solid #c9d4e3; border-radius: 4px;
  padding: 16px 18px;
  display: flex; flex-direction: column; gap: 12px;
}
.an-shell .stats-head {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
}
.an-shell .stats-meta { display: inline-flex; align-items: baseline; gap: 8px; }
.an-shell .stats-lab { font-size: 12px; color: #4a5b78; font-weight: 600; }
.an-shell .stats-meta strong { font-size: 14.5px; color: #0c1f40; font-weight: 800; }
.an-shell .stats-tabs { display: inline-flex; background: #f1f5fb; border: 1px solid #c9d4e3; border-radius: 4px; overflow: hidden; }
.an-shell .stats-t {
  background: none; border: 0; padding: 6px 14px; cursor: pointer;
  font-size: 12.5px; font-weight: 600; color: #4a5b78;
  border-right: 1px solid #c9d4e3;
}
.an-shell .stats-t:last-child { border-right: 0; }
.an-shell .stats-t.on { background: #2563eb; color: #fff; }
.an-shell .stats-kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
}
.an-shell .stats-kpi {
  background: #f1f5fb; border: 1px solid #c9d4e3; border-radius: 3px;
  padding: 8px 12px;
  display: flex; flex-direction: column; gap: 2px;
}
.an-shell .stats-kpi span { font-size: 11.5px; color: #4a5b78; font-weight: 600; }
.an-shell .stats-kpi strong {
  font-family: "IBM Plex Mono", monospace;
  font-size: 18px; font-weight: 800; color: #0c1f40;
}
.an-shell .stats-kpi strong small { font-size: 11px; font-weight: 600; color: #4a5b78; margin-left: 3px; }
.an-shell .stats-kpi strong.rd { color: #b91c1c; }
.an-shell .stats-kpi strong.up { color: #047857; }
.an-shell .stats-line { width: 100%; height: 220px; }
.an-shell .stats-x {
  display: flex; justify-content: space-between;
  font-family: "IBM Plex Mono", monospace;
  font-size: 11.5px; color: #6b7a92; padding: 0 4px;
}

.an-shell .ctx-msg {
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #047857;
  padding: 6px 12px; border-radius: 3px;
  font-size: 12.5px; font-weight: 600;
  margin-bottom: 10px;
}
.an-shell .is-card { padding: 10px 14px !important; }
.an-shell .is-h { font-size: 19px !important; }
.an-shell .is-t { font-size: 16.5px !important; }
.an-shell .is-d { font-size: 14.5px !important; -webkit-line-clamp: 1 !important; }
.an-shell .is-more { font-size: 16px !important; padding: 12px 18px !important; }
.an-shell .cm-chart h4 { font-size: 18px !important; }
.an-shell .cm-legend { font-size: 14.5px !important; }
.an-shell .cmp-h h3 { font-size: 20px !important; }
.an-shell .jam-map-card h3,
.an-shell .kpi-tbl-card h3 { font-size: 20px !important; }
.an-shell .tbl-kpi { font-size: 17px; }
.an-shell .tbl-kpi th { font-size: 16px !important; padding: 12px 12px !important; }
.an-shell .tbl-kpi td { padding: 12px 12px !important; }
.an-shell .y-axis span,
.an-shell .cm-x span { font-size: 13px !important; }

/* 인사이트 가로 스트립 */
.an-shell .insight-strip {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  flex-shrink: 0;
}
.an-shell .is-h {
  font-size: 14.5px;
  font-weight: 800;
  color: #0c1f40;
  white-space: nowrap;
  letter-spacing: -0.01em;
}
.an-shell .is-h i { color: #2563eb; margin-right: 4px; }
.an-shell .is-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.an-shell .is-card {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  border-left: 3px solid #c9d4e3;
  padding: 7px 10px;
  min-width: 0;
}
.an-shell .is-card:nth-child(1) { border-left-color: #dc2626; }
.an-shell .is-card:nth-child(2) { border-left-color: #b45309; }
.an-shell .is-card:nth-child(3) { border-left-color: #047857; }
.an-shell .is-card:nth-child(4) { border-left-color: #2563eb; }
.an-shell .is-card i { font-size: 16.5px; padding-top: 2px; flex-shrink: 0; }
.an-shell .is-card > div { min-width: 0; }
.an-shell .is-t {
  font-size: 15.5px;
  font-weight: 800;
  color: #0c1f40;
  letter-spacing: -0.01em;
}
.an-shell .is-d {
  font-size: 14.5px;
  color: #4a5b78;
  font-weight: 500;
  line-height: 1.35;
  margin-top: 1px;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.an-shell .is-more {
  background: #ffffff;
  border: 1px solid #c9d4e3;
  color: #2563eb;
  padding: 8px 14px;
  font-size: 15.5px;
  font-weight: 700;
  cursor: pointer;
  border-radius: 2px;
  font-family: inherit;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.an-shell .is-more:hover { background: #2563eb; color: #ffffff; border-color: #2563eb; }
.an-shell .row-cmp > .cmp-area,
.an-shell .row-cmp > .insight,
.an-shell .row-mid > .card,
.an-shell .row-bot > .card {
  min-height: 0;
  display: flex; flex-direction: column;
  overflow: hidden;
}
/* 차트 높이 제한 */
.an-shell .cmp-grid { flex: 1; min-height: 0; }
.an-shell .cm-chart { display: flex; flex-direction: column; min-height: 0; }
.an-shell .chart-frame { flex: 1; min-height: 0; }
.an-shell .line-svg { height: 100% !important; }
.an-shell .jam-leaflet { flex: 1; height: auto !important; min-height: 120px; }
/* 표는 카드 안에서 fit */
.an-shell .tbl-kpi,
.an-shell .tbl-resv,
.an-shell .tbl-saved { flex: 0 0 auto; }
/* 인사이트 카드 컴팩트 */
.an-shell .insight { overflow-y: auto; }
.an-shell .ins-card { padding: 6px 0 !important; }
.top { padding: 16px 24px; border-bottom: 1px solid #1a2a45; }
.top h1 { display: flex; align-items: center; gap: 8px; }
.brand-link { display: inline-flex; align-items: center; gap: 8px; color: inherit; text-decoration: none; cursor: pointer; }
.brand-link:hover { opacity: 0.85; }
.top .dot { width: 7px; height: 7px; border-radius: 50%; background: #60a5fa; box-shadow: 0 0 8px #60a5fa; }
.t-sub { font-weight: 500; opacity: .8; }
.t-right { display: flex; align-items: center; gap: 10px; }
.btn-pri { background: #3b82f6; color: #fff; border: 0; border-radius: 6px; padding: 8px 14px; font-size: 14.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }

.body { display: flex; min-height: calc(100vh - 60px); }
.filter { width: 220px; background: #06101e; border-right: 1px solid #1a2a45; padding: 20px 16px; flex-shrink: 0; display: flex; flex-direction: column; gap: 20px; }
.filter h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 6px; }
.f-lab { font-size: 16.5px; font-weight: 600; opacity: .85; margin-bottom: 8px; }
.f-search { position: relative; margin-bottom: 8px; }
.f-search i { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); opacity: .55; font-size: 16.5px; }
.f-search input { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 26px 6px 10px; border-radius: 5px; font-size: 16.5px; }
.ck-list { display: flex; flex-direction: column; gap: 6px; }
.ck { display: flex; align-items: center; gap: 6px; font-size: 15.5px; cursor: pointer; }
.ck input { accent-color: #60a5fa; }
.sub-list { display: flex; flex-direction: column; gap: 4px; padding: 4px 0 4px 24px; border-left: 1px dashed #1f3055; margin-left: 8px; }
.empty-q { font-size: 15.5px; opacity: .5; padding: 6px 4px; }

.filter { width: 240px; }
.f-block { margin-bottom: 20px; padding-bottom: 18px; border-bottom: 1px solid #1a2a45; }
.f-block:last-of-type { border-bottom: 0; }
.anav { display: flex; flex-direction: column; gap: 2px; }
.anav-i { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 6px; color: rgba(228,238,255,.55); font-size: 15.5px; border: 0; background: none; cursor: pointer; font-family: inherit; text-align: left; }
.anav-i:hover { background: rgba(96,165,250,.06); color: #e4eeff; }
.anav-i.on { background: rgba(96,165,250,.15); color: #60a5fa; font-weight: 600; }
.anav-i i { width: 16px; }
.auth-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.auth-btn { display: flex; align-items: center; justify-content: center; gap: 5px; padding: 9px 6px; border: 0; border-radius: 6px; font-size: 15.5px; font-weight: 700; cursor: pointer; font-family: inherit; color: #fff; }
.auth-btn.bl { background: #3b82f6; }
.auth-btn:nth-child(2).bl { background: rgba(59,130,246,.18); color: #60a5fa; border: 1px solid rgba(59,130,246,.35); }
.auth-btn.gr { background: #10b981; }
.auth-btn.pl { background: #8b5cf6; }
.auth-btn i { font-size: 16.5px; }
.op-msg { margin-top: 8px; font-size: 15.5px; color: #34d399; text-align: center; }
.data-up { margin-top: auto; padding-top: 12px; font-size: 16.5px; opacity: .6; }
.du-l { margin-bottom: 2px; }
.du-r { font-family: "JetBrains Mono", monospace; display: flex; justify-content: space-between; align-items: center; }
.t-avatar { width: 30px; height: 30px; border-radius: 50%; background: #3b82f6; color: #fff; font-size: 15.5px; font-weight: 800; display: inline-flex; align-items: center; justify-content: center; }

.row-mid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 14px; }
.jam-map-card, .kpi-tbl-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.jam-map-card h3, .kpi-tbl-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.jam-map-card { position: relative; }
.jam-leaflet { width: 100%; height: 280px; border-radius: 8px; overflow: hidden; background: #06101e; }
.jam-leaflet :deep(.leaflet-container) { background: #06101e; }
.jam-leaflet :deep(.leaflet-control-zoom a) { background: rgba(8,16,32,.85); color: #e4eeff; border-color: #1f3055; }
.jam-leaflet :deep(.ic-tip), .jam-leaflet :deep(.osm-road-tip) { background: rgba(8,16,32,.92); border: 1px solid #1f3055; color: #e4eeff; font-size: 15.5px; padding: 4px 8px; line-height: 1.55; }
.jm-legend { display: flex; align-items: center; gap: 8px; margin-top: 10px; font-size: 16.5px; opacity: .8; }
.jl-label { white-space: nowrap; }
.jl-bar { flex: 1; height: 8px; max-width: 200px; border-radius: 2px;
  background: linear-gradient(90deg, #ef4444 0%, #fb923c 33%, #fbbf24 66%, #34d399 100%); }
.jl-ticks { display: flex; justify-content: space-between; max-width: 200px; flex: 1; font-family: "JetBrains Mono", monospace; }
.tbl-kpi { width: 100%; border-collapse: collapse; font-size: 16.5px; }
.tbl-kpi th, .tbl-kpi td { padding: 8px 6px; text-align: center; border-bottom: 1px solid #1a2a45; }
.tbl-kpi th { font-weight: 600; opacity: .55; font-size: 15.5px; }
.tbl-kpi .mono { font-family: "JetBrains Mono", monospace; }
.tbl-kpi .up { color: #34d399; }
.tbl-kpi .dn { color: #f87171; }
.cg-tag { padding: 2px 8px; border-radius: 100px; font-size: 16.5px; font-weight: 700; }
.cg-tag.yl { background: rgba(245,158,11,.18); color: #fbbf24; }
.cg-tag.or { background: rgba(251,146,60,.2); color: #fb923c; }
.cg-tag.rd { background: rgba(239,68,68,.18); color: #f87171; }

.row-bot { display: grid; grid-template-columns: 1fr 1.5fr; gap: 14px; }
.resv-card, .saved-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.resv-card h3, .saved-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.tbl-resv, .tbl-saved { width: 100%; border-collapse: collapse; font-size: 14.5px; }
.tbl-resv th, .tbl-resv td, .tbl-saved th, .tbl-saved td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #1a2a45; }
.tbl-resv th, .tbl-saved th { font-weight: 600; opacity: .55; font-size: 16.5px; }
.tbl-resv .mono, .tbl-saved .mono { font-family: "JetBrains Mono", monospace; opacity: .85; }
.resv-st { padding: 2px 8px; border-radius: 100px; font-size: 14.5px; font-weight: 700; }
.resv-st.ok { background: rgba(96,165,250,.18); color: #60a5fa; }
.resv-st.wait { background: rgba(245,158,11,.18); color: #fbbf24; }
.more-btn { width: 100%; margin-top: 10px; background: rgba(96,165,250,.06); border: 1px solid rgba(96,165,250,.2); color: #60a5fa; padding: 7px; border-radius: 5px; font-size: 14.5px; cursor: pointer; }
.sb { font-size: 14.5px; opacity: .7; padding-left: 10px; position: relative; }
.sb::before { content: ""; position: absolute; left: 0; top: 50%; width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; transform: translateY(-50%); }
.seg-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 4px; margin-bottom: 8px; }
.seg { background: #0a1424; border: 1px solid #1f3055; color: rgba(228,238,255,.7); padding: 5px; font-size: 15.5px; border-radius: 4px; cursor: pointer; }
.seg.on { background: #3b82f6; border-color: #3b82f6; color: #fff; }
.date-r { font-size: 15.5px; opacity: .7; display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: #0a1424; border: 1px solid #1f3055; border-radius: 4px; }
.f-sel { width: 100%; background: #0a1424; border: 1px solid #1f3055; color: #e4eeff; padding: 6px 10px; border-radius: 5px; font-size: 15.5px; }
.reset { margin-top: auto; background: rgba(96,165,250,.08); border: 1px solid rgba(96,165,250,.25); color: #60a5fa; padding: 8px; border-radius: 5px; cursor: pointer; font-size: 16.5px; }

.content { flex: 1; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; min-width: 0; }
.metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
.mt-time .mt-time-v { font-size: 15.5px; font-weight: 700; padding: 4px 0; }
.mt-time .mt-time-v i { opacity: .55; margin-left: 4px; }
.mt-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; display: grid; grid-template-columns: 1fr auto; grid-template-rows: auto auto auto; gap: 4px 12px; }
.mt-lab { grid-column: 1; font-size: 16.5px; opacity: .75; }
.mt-val { grid-column: 1; font-size: 30px; font-weight: 800; }
.mt-val.gr { color: #34d399; }
.mt-val.or { color: #fbbf24; }
.mt-u { font-size: 14.5px; font-weight: 500; opacity: .65; margin-left: 2px; }
.mt-spark { grid-column: 2; grid-row: 1 / 3; align-self: center; width: 80px; }
.sp { width: 100%; height: 24px; }
.mt-d { grid-column: 1 / -1; font-size: 15.5px; opacity: .65; padding-top: 4px; border-top: 1px solid #1a2a45; margin-top: 4px; }
.mt-d .up-r { color: #f87171; }
.mt-d .dn { color: #f87171; }

.row-cmp { display: grid; grid-template-columns: 1fr 260px; gap: 14px; }
.cmp-area { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.cmp-h { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.cmp-h h3 { font-size: 15.5px; font-weight: 700; margin: 0; }
.seg-sub { font-size: 16.5px; opacity: .55; font-weight: 400; margin-left: 4px; }
.cmp-tabs { display: flex; gap: 4px; background: #06101e; border: 1px solid #1f3055; border-radius: 6px; padding: 2px; }
.ct { background: none; border: 0; color: rgba(228,238,255,.6); font-size: 14.5px; padding: 5px 12px; border-radius: 4px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; }
.ct.on { background: rgba(96,165,250,.15); color: #60a5fa; }
.cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.cm-chart h4 { font-size: 16.5px; font-weight: 600; margin: 0 0 8px; }
.cm-legend { display: flex; flex-wrap: wrap; gap: 10px; font-size: 16.5px; opacity: .8; margin-bottom: 8px; }
.lg-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; }
.lg-dot.bl { background: #60a5fa; }
.lg-dot.gy { background: #9ca3af; }
.lg-dot.gr { background: #10b981; }
.lg-dot.bl-d { background: #3b82f6; opacity: .5; }
.lg-dot.gr-d { background: #10b981; opacity: .5; }
.line-svg { width: 100%; height: 180px; }
.chart-frame { display: flex; gap: 6px; align-items: stretch; }
.y-axis { display: flex; flex-direction: column; justify-content: space-between; font-size: 15.5px; opacity: .5; padding: 2px 0; width: 22px; text-align: right; }
.chart-frame .line-svg { flex: 1; }
.cm-u { font-size: 16.5px; opacity: .55; font-weight: 400; }
.cm-chart h4 { display: flex; align-items: baseline; gap: 4px; }
.cm-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; padding: 4px 0 0; }

.insight { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 14px; }
.insight h3 { font-size: 14.5px; font-weight: 700; margin: 0 0 8px; display: flex; align-items: center; gap: 6px; }
.ins-card { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #1a2a45; }
.ins-card:last-of-type { border-bottom: 0; }
.ins-card > i { font-size: 17.5px; padding-top: 1px; flex-shrink: 0; }
.ic-t { font-size: 15.5px; font-weight: 700; margin-bottom: 3px; }
.ic-d { font-size: 15.5px; opacity: .7; line-height: 1.5; }
.ai-detail-btn { width: 100%; margin-top: 12px; background: rgba(96,165,250,.1); border: 1px solid rgba(96,165,250,.3); color: #60a5fa; padding: 9px; border-radius: 6px; font-size: 16.5px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.insight h3.mt { margin-top: 14px; }
.insight h4 { font-size: 16.5px; opacity: .75; margin: 0 0 8px; font-weight: 500; }
.ins { display: flex; gap: 8px; padding: 8px 0; font-size: 14.5px; line-height: 1.55; border-bottom: 1px solid #1a2a45; }
.ins:last-of-type { border-bottom: 0; }
.ins-ic { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 4px; }
.rec { font-size: 14.5px; padding: 6px 0; display: flex; align-items: flex-start; gap: 6px; line-height: 1.5; }
.rec i { color: #60a5fa; padding-top: 2px; }
.rep-d { display: flex; align-items: center; gap: 8px; padding: 8px; background: rgba(96,165,250,.06); border-radius: 6px; }
.rep-d > i { font-size: 25px; color: #60a5fa; }
.rep-d > div { flex: 1; min-width: 0; }
.rep-t { font-size: 16.5px; font-weight: 700; }
.rep-s { font-size: 16.5px; opacity: .65; }
.rep-dl { background: rgba(96,165,250,.15); border: 0; color: #60a5fa; width: 26px; height: 26px; border-radius: 4px; cursor: pointer; }

.row-bot { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.flow-card, .deep-card { background: #0f1d34; border: 1px solid #1f3055; border-radius: 10px; padding: 16px; }
.flow-card h3, .deep-card h3 { font-size: 15.5px; font-weight: 700; margin: 0 0 12px; }
.flow-grid { display: grid; grid-template-columns: 1fr 100px 1fr; gap: 10px; align-items: center; }
.fc { padding: 6px; }
.fc-h { font-size: 16.5px; margin-bottom: 6px; }
.fc-lg { font-size: 16.5px; opacity: .75; margin-bottom: 6px; display: flex; gap: 8px; }
.flow-svg { width: 100%; height: 120px; }
.fc-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; padding-top: 4px; }
.fc-mid { display: flex; flex-direction: column; gap: 6px; font-size: 15.5px; padding: 0 8px; }
.m-row { display: flex; align-items: center; gap: 6px; opacity: .8; }
.m-row .d { width: 6px; height: 6px; border-radius: 50%; border: 1px solid #60a5fa; }

.b-red { background: rgba(239,68,68,.18); color: #f87171; font-size: 16.5px; font-weight: 700; padding: 1px 8px; border-radius: 4px; margin-left: 4px; }
.deep-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 14px; }
.dl-h { font-size: 16.5px; font-weight: 700; margin-bottom: 10px; }
.dl-i { display: flex; gap: 10px; padding: 8px 0; align-items: flex-start; }
.dl-i i { font-size: 17.5px; padding-top: 2px; }
.dl-i > div { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.dl-i strong { font-size: 15.5px; }
.dl-i span { font-size: 15.5px; opacity: .7; line-height: 1.45; }
.deep-right { display: flex; flex-direction: column; gap: 10px; }
.dr-c h4 { font-size: 15.5px; font-weight: 600; margin: 0 0 4px; opacity: .85; }
.dr-u { font-size: 14.5px; opacity: .55; font-weight: 400; margin-left: 2px; }
.sp-c { width: 100%; height: 80px; }
.dr-x { display: flex; justify-content: space-between; font-size: 15.5px; opacity: .55; }
</style>
