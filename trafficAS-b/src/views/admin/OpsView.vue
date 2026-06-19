<template>
  <div class="ops-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen">
          <img src="/TAS.png" alt="TAS" class="brand-img" />
        </RouterLink>
        <button
          class="side-toggle"
          @click="sideOpen = !sideOpen"
          :aria-label="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
          :title="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
        >
          <i :class="sideOpen ? 'bi bi-arrow-left-short' : 'bi bi-arrow-right-short'"></i>
        </button>
      </div>
      <nav class="snav">
        <button
          v-for="n in nav"
          :key="n.id"
          class="snav-i"
          :class="{ on: tab === n.id }"
          @click="tab = n.id"
          :title="!sideOpen ? n.label + (n.bdg ? ` (${n.bdg})` : '') : ''"
        >
          <span class="snav-ic">
            <i :class="n.icon"></i>
            <span v-if="n.bdg && !sideOpen" class="snav-bdg-dot"></span>
          </span>
          <span class="snav-lab">{{ n.label }}</span>
          <span v-if="n.bdg && sideOpen" class="snav-bdg">{{ n.bdg }}</span>
        </button>
      </nav>
      <div class="side-foot" v-if="sideOpen">시설운영팀 v2.1.0<br />© 2026</div>
    </aside>

    <div class="main">
      <header class="top">
        <h1><a class="t-main" @click="goHome">시설운영팀</a></h1>
        <div class="t-right">
          <span class="hdr-time"
            ><i class="bi bi-clock"></i> 마지막 업데이트 <strong>10:32:18</strong></span
          >
          <div class="hdr-weather">
            <button class="hwx-chip" @click="showWeather = !showWeather" :class="{ on: showWeather }">
              <i :class="weatherSummary.icon" :style="{ color: weatherSummary.color }"></i>
              <span class="hwx-temp">{{ weatherSummary.temp }}°</span>
              <span class="hwx-cond">{{ weatherSummary.condition }}</span>
              <i class="bi" :class="showWeather ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
            </button>
            <div v-if="showWeather" class="hwx-pop" @click.stop>
              <SideWeather />
            </div>
          </div>
          <button
            class="km-toggle"
            :class="{ on: autoRefresh }"
            @click="autoRefresh = !autoRefresh"
            :aria-pressed="autoRefresh"
          >
            <span class="km-dot"></span>
            <span class="km-lab">자동 새로고침</span>
            <span class="km-state">{{ autoRefresh ? "ON" : "OFF" }}</span>
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
          <div class="t-user">
            <i class="bi bi-person-circle"></i> 시설운영팀 매니저
            <i class="bi bi-chevron-down"></i>
          </div>
        </div>
      </header>

      <GuideOverlay
        v-model="guideOpen"
        :steps="guideSteps"
        :on-step-enter="onGuideStep"
      />

      <template v-if="tab === 'status'">
        <!-- ============ 데이터 소스 필터 ============ -->
        <div class="pm-ds-row">
          <label class="pm-ds-lab">
            <i class="bi bi-database"></i> 데이터 소스
          </label>
          <select v-model="pmDataSource" class="pm-ds-sel">
            <option value="REAL">실데이터</option>
            <option value="OPEN_DATA">공개데이터</option>
            <option value="SIMULATED">시뮬레이션</option>
            <option value="FAULT_INJECTED">장애 주입</option>
            <option value="MOCK">목업</option>
          </select>
          <span v-if="pmDataSource !== 'REAL'" class="pm-ds-bdg" :class="pmDataSourceTone(pmDataSource)">
            <i class="bi bi-exclamation-triangle-fill"></i>
            {{ pmDataSourceLabel(pmDataSource) }} 모드 — 실제 운영 데이터 아님
          </span>
        </div>

        <!-- ============ 예지보전 인사이트 스트립 ============ -->
        <section class="pm-strip">
          <div class="pm-kpi" :class="{ ok: pmSloOk, bad: !pmSloOk }">
            <i class="bi bi-heart-pulse"></i>
            <div class="pm-kpi-b">
              <div class="pm-kpi-v">{{ pmHealthAvg }}<small>/100</small></div>
              <div class="pm-kpi-l">평균 Health Score <span class="pm-sub">{{ pmSloOk ? '운영 양호' : '하향 추세' }}</span></div>
            </div>
          </div>
          <div class="pm-kpi" :class="{ alert: pmPredictedCount > 0 }">
            <i class="bi bi-graph-up-arrow"></i>
            <div class="pm-kpi-b">
              <div class="pm-kpi-v">{{ pmPredictedCount }}<small>건</small></div>
              <div class="pm-kpi-l">악화 예측 <span class="pm-sub">10분 내 임계 도달</span></div>
            </div>
          </div>
          <div class="pm-kpi" :class="{ alert: pmCriticalCount > 0 }">
            <i class="bi bi-exclamation-octagon-fill"></i>
            <div class="pm-kpi-b">
              <div class="pm-kpi-v">{{ pmCriticalCount }}<small>대</small></div>
              <div class="pm-kpi-l">위험 카메라 <span class="pm-sub">Health &lt; 50</span></div>
            </div>
          </div>
          <div class="pm-kpi" :class="{ alert: pmOverdueTickets > 0 }">
            <i class="bi bi-stopwatch"></i>
            <div class="pm-kpi-b">
              <div class="pm-kpi-v">{{ pmOverdueTickets }}<small>건</small></div>
              <div class="pm-kpi-l">SLA 초과 <span class="pm-sub">조치 지연 티켓</span></div>
            </div>
          </div>
          <div class="pm-kpi bl">
            <i class="bi bi-cpu"></i>
            <div class="pm-kpi-b">
              <div class="pm-kpi-v">{{ pmBaselineLearning }}<small>대</small></div>
              <div class="pm-kpi-l">기준선 학습 중 <span class="pm-sub">14일 표본 수집</span></div>
            </div>
          </div>
        </section>

        <!-- ============ 메인 그리드 (좌 2x2 + 우 풀세로 장애상세) ============ -->
        <section class="main-grid">
          <!-- 네트워크 지연 카드 — net 탭에 동일 기능 있어 제거 -->
          <div class="card net-card" v-if="false">
            <div class="ch">
              <h3>네트워크 지연 <span class="ch-kpi">평균 128ms · 최대 286ms</span></h3>
              <a class="ch-link" @click="tab = 'net'">전체 보기 ›</a>
            </div>
            <div class="net-summary">
              <div class="ns-head">
                <div class="ns-status">
                  <span class="ns-dot yl"></span>
                  <span class="ns-st-label">주의</span>
                </div>
                <div class="ns-avg">
                  <strong>128<small>ms</small></strong>
                  <span>평균</span>
                </div>
              </div>

              <div ref="netChartEl" class="net-echart"></div>

            </div>
          </div>

          <!-- 서버 상태 카드 — srv 탭에 동일 기능 있어 제거 -->
          <div class="card srv-card" v-if="false">
            <div class="ch">
              <h3>서버 상태 <span class="ch-kpi gr">대표 · ocr-srv-01</span></h3>
              <a class="ch-link" @click="tab = 'srv'">전체 보기 ›</a>
            </div>
            <div v-for="(s, i) in servers.slice(0, 1)" :key="i" class="srv">
              <div class="srv-h">
                <div class="srv-name">
                  <svg viewBox="0 0 32 32" class="srv-icon" aria-hidden="true">
                    <!-- 3D 서버 랙: 윗면 + 정면 + 측면 -->
                    <polygon points="6,10 16,4 28,8 18,14" fill="#7ea4d8" />
                    <polygon points="6,10 18,14 18,28 6,24" fill="#2563eb" />
                    <polygon points="18,14 28,8 28,22 18,28" fill="#1d4ed8" />
                    <!-- LED 점 (정면) -->
                    <circle cx="9" cy="14" r="1" fill="#34d399" />
                    <circle cx="9" cy="18" r="1" fill="#fbbf24" />
                    <circle cx="9" cy="22" r="1" fill="#34d399" />
                    <!-- 디스크 슬롯 라인 -->
                    <line
                      x1="11"
                      y1="14"
                      x2="16"
                      y2="15"
                      stroke="#fff"
                      stroke-opacity=".25"
                      stroke-width="0.5"
                    />
                    <line
                      x1="11"
                      y1="18"
                      x2="16"
                      y2="19"
                      stroke="#fff"
                      stroke-opacity=".25"
                      stroke-width="0.5"
                    />
                    <line
                      x1="11"
                      y1="22"
                      x2="16"
                      y2="23"
                      stroke="#fff"
                      stroke-opacity=".25"
                      stroke-width="0.5"
                    />
                  </svg>
                  <div>
                    <div class="sn-t">
                      {{ s.name }} <span class="sn-tag" v-if="s.tag">{{ s.tag }}</span>
                    </div>
                    <div class="sn-ip">{{ s.ip }}</div>
                  </div>
                </div>
                <span class="stat" :class="s.stTone">{{ s.st }}</span>
              </div>
              <div class="srv-gauges">
                <div v-for="b in s.bars" :key="b.l" class="srv-g" :class="b.tone">
                  <div class="srv-g-wrap" :ref="(el) => setSrvChart(el, b)"></div>
                  <div class="srv-g-lab">{{ b.l }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- ▶ 우측 컬럼 스택: 알람타임라인(작게) + 장애상세(크게) ◀ -->
          <div class="col3-stack">
            <!-- 알람 타임라인 (위, 작게) -->
            <div class="card timeline-card">
              <div class="ch">
                <h3>알람 타임라인</h3>
                <div class="tl-filter">
                  <button
                    v-for="f in ['ALL', 'CRIT', 'HIGH', 'MED', 'INFO']"
                    :key="f"
                    class="tl-f"
                    :class="{ on: tlFilter === f }"
                    @click="tlFilter = f"
                  >
                    {{ f }}
                  </button>
                </div>
              </div>
              <div class="tl-list">
                <div class="tl-th">
                  <span>시간</span>
                  <span>내용</span>
                  <span>담당자</span>
                  <span></span>
                </div>
                <div
                  v-for="a in filteredAlarms.slice(0, 3)"
                  :key="a.id"
                  class="tl-row"
                  :class="a.kind"
                  @click="openAlarm(a)"
                  style="cursor: pointer"
                >
                  <span class="tl-t">{{ a.time }}</span>
                  <span class="tl-msg">{{ a.msg }}</span>
                  <span class="tl-who">{{ a.who }}</span>
                  <i class="bi bi-chevron-right tl-arrow"></i>
                </div>
                <div v-if="!filteredAlarms.length" class="tl-empty">해당 분류 없음</div>
              </div>
              <div class="tl-foot" style="justify-content: flex-end;">
                <a class="ch-link" @click="tab = 'alarm'">전체 알람 보기 ›</a>
              </div>
            </div>

            <!-- 장애 상세 (아래, 크게) -->
            <div class="card fail-card">
              <div class="ch">
                <h3>
                  장애 상세 <span class="b-rd">진행 중</span>
                  <span class="ch-kpi rd">1건 장애 · 2건 처리 대기</span>
                </h3>
                <a class="ch-link" @click="tab = 'fault'">전체 보기 ›</a>
              </div>
              <div class="fl-head">
                <div class="fl-title">
                  정릉터널_입구_B1 <span class="fl-tag">장애</span>
                </div>
              </div>
              <div class="fl-rows">
                <div class="fl-row"><span><i class="bi bi-hdd-network"></i> 장비 ID</span><strong>NSN-N-0023</strong></div>
                <div class="fl-row">
                  <span><i class="bi bi-geo-alt"></i> 위치</span><strong>내부순환로 03K+150</strong>
                </div>
                <div class="fl-row">
                  <span><i class="bi bi-clock-history"></i> 최초 감지</span><strong>10:24:17 <em>(8분 전)</em></strong>
                </div>
                <div class="fl-row">
                  <span><i class="bi bi-exclamation-triangle"></i> 증상</span><strong>RTSP 스트림 타임아웃</strong>
                </div>
              </div>
              <h4><i class="bi bi-list-check"></i> 조치 이력</h4>
              <div class="hst">
                <div><i class="bi bi-circle-fill hst-i"></i><span class="hst-t">10:24:17</span> 장애 자동 감지</div>
                <div>
                  <i class="bi bi-circle-fill hst-i"></i><span class="hst-t">10:28:11</span> 김기사(IT) 상황 확인 — 현장 출동 예정
                </div>
              </div>
              <div class="act-row">
                <button class="ab bl"><i class="bi bi-arrow-repeat"></i> 재연결</button>
                <button class="ab rd"><i class="bi bi-exclamation-octagon"></i> 장애 등록</button>
                <button class="ab gy"><i class="bi bi-tools"></i> 점검 요청</button>
                <button class="ab gr"><i class="bi bi-check2-circle"></i> 복구 완료</button>
              </div>
              <div class="resp-row">
                <span><i class="bi bi-person-badge"></i> 담당자</span><strong>김기사 (IT)</strong
                ><button class="ab-sm">변경</button>
              </div>
              <div class="memo-row">
                <span><i class="bi bi-pencil-square"></i> 메모</span
                ><input v-model="failMemo" placeholder="메모를 입력하세요..." /><button
                  class="ab-sm"
                >
                  저장
                </button>
              </div>
            </div>
          </div>

          <div class="bot-row">
            <!-- 카메라 상태 (왼쪽, 위치 변경) -->
            <div class="card cam-card">
              <div class="ch">
                <h3>
                  카메라 상태 <span class="ch-kpi gr">24/25 <em>96.0%</em></span>
                </h3>
                <a class="ch-link" @click="tab = 'cams'">전체 보기 ›</a>
              </div>
              <div class="cam-filter">
                <span class="cf on">전체 25</span>
                <span class="cf gr">정상 23</span>
                <span class="cf yl">지연 1</span>
                <span class="cf rd">장애 2</span>
                <div class="cf-r">
                  <input placeholder="카메라명 검색" /><select>
                    <option>전체 위치</option>
                  </select>
                </div>
              </div>
              <table class="cam-tbl pm-cam-tbl">
                <thead>
                  <tr>
                    <th>카메라명</th>
                    <th>상태</th>
                    <th class="num">Health</th>
                    <th>지연(ms)</th>
                    <th>최근 응답</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(c, i) in cams.slice(0, 4)"
                    :key="i"
                    :class="{ bad: c.st === '장애' }"
                    @click="openCam(c)"
                    style="cursor: pointer"
                  >
                    <td>
                      <i class="bi bi-camera-video"></i> {{ c.name }}
                      <span
                        v-if="c.predictedRisk > 0"
                        class="pm-pred-bdg"
                        :title="`${c.predictedType} · ${c.predictedAt} 임계 도달 예상`"
                      >
                        <i class="bi bi-graph-up-arrow"></i> 악화 예측
                      </span>
                    </td>
                    <td>
                      <span class="stat" :class="c.stTone">{{ c.st }}</span>
                    </td>
                    <td class="num mono">
                      <span v-if="c.healthStatus === 'BASELINE_LEARNING'" class="pm-baseline" title="기준선 학습 중">
                        <i class="bi bi-cpu"></i> {{ c.baselineSamples }}/{{ c.baselineRequired }}
                      </span>
                      <span v-else-if="c.healthScore != null" class="pm-hs" :class="pmScoreTone(c.healthScore)">{{ c.healthScore.toFixed(1) }}</span>
                      <span v-else class="pm-hs gy">—</span>
                    </td>
                    <td class="mono">{{ c.lat }}</td>
                    <td class="mono">{{ c.ts }}</td>
                  </tr>
                </tbody>
              </table>
              <div class="cam-foot">
                <span>총 25개</span>
                <div class="pg-row">
                  <button><i class="bi bi-chevron-double-left"></i></button>
                  <button><i class="bi bi-chevron-left"></i></button>
                  <button class="on">1</button>
                  <button><i class="bi bi-chevron-right"></i></button>
                  <button><i class="bi bi-chevron-double-right"></i></button>
                </div>
              </div>
            </div>

          </div>
          <!-- /.bot-row -->
        </section>
      </template>

      <section v-if="tab === 'cams'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>
            카메라 운영 현황
            <span class="ch-kpi">전체 25대 모니터링</span>
          </h3>
          <div class="pnl-tools">
            <select v-model="camSort" class="pnl-sort" :title="'정렬 (현재: ' + camSortLabel + ')'">
              <option value="healthScore,asc">위험 카메라 우선</option>
              <option value="healthScore,desc">정상 카메라 우선</option>
              <option value="cameraName,asc">이름 가나다순</option>
              <option value="latestSampledAt,desc">최근 응답순</option>
            </select>
            <input
              v-model="camQuery"
              placeholder="카메라명 / ID / 위치 검색"
              class="pnl-search-i"
            />
            <select v-model="camSt">
              <option value="all">전체 상태</option>
              <option>정상</option>
              <option>지연</option>
              <option>장애</option>
            </select>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV 내보내기</button>
          </div>
        </div>

        <!-- 상단 KPI 9박스 (운영 7 + 예지 2) -->
        <div class="pnl-summary nd-kpi nd-kpi-9">
          <div class="ps-box">
            <div class="ps-l">전체</div>
            <div class="ps-v">25</div>
            <div class="ps-sub">운영 카메라</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">23</div>
            <div class="ps-sub">92.0%</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">지연</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">4.0%</div>
          </div>
          <div class="ps-box rd">
            <div class="ps-l">장애</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">4.0%</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 지연</div>
            <div class="ps-v">94<span>ms</span></div>
            <div class="ps-sub">전일 -3ms</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 가동률</div>
            <div class="ps-v">96.2<span>%</span></div>
            <div class="ps-sub">최근 30일</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 OCR 신뢰도</div>
            <div class="ps-v">94.8<span>%</span></div>
            <div class="ps-sub">최근 24h</div>
          </div>
          <div class="ps-box pm">
            <div class="ps-l"><i class="bi bi-heart-pulse"></i> 평균 Health</div>
            <div class="ps-v">{{ pmHealthAvg }}<span>/100</span></div>
            <div class="ps-sub">예지 운영 점수</div>
          </div>
          <div class="ps-box pm-alert" :class="{ alert: pmPredictedCount > 0 }">
            <div class="ps-l"><i class="bi bi-graph-up-arrow"></i> 악화 예측</div>
            <div class="ps-v">{{ pmPredictedCount }}<span>건</span></div>
            <div class="ps-sub">10분 내 임계 도달</div>
          </div>
        </div>

        <!-- 카메라 전체 목록 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>카메라 전체 목록</h4>
            <span class="nd-h-cnt">{{ filteredCams.length }} / {{ cams.length }}대</span>
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>장비 ID</th>
                <th>카메라명</th>
                <th>위치</th>
                <th>IP</th>
                <th>상태</th>
                <th class="num">Health</th>
                <th>지연</th>
                <th>가동률</th>
                <th>OCR 신뢰도</th>
                <th>펌웨어</th>
                <th>마지막 점검</th>
                <th>최근 응답</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(c, i) in filteredCams"
                :key="i"
                @click="openCam(c)"
                style="cursor: pointer"
                :class="{ bad: c.st === '장애' }"
              >
                <td class="mono">{{ c.id }}</td>
                <td>
                  <i class="bi bi-camera-video"></i> {{ c.name }}
                  <span
                    v-if="c.predictedRisk > 0"
                    class="pm-pred-bdg"
                    :title="`${c.predictedType} · ${c.predictedAt} 임계 도달 예상`"
                  >
                    <i class="bi bi-graph-up-arrow"></i> 악화 예측
                  </span>
                </td>
                <td>{{ c.loc }}</td>
                <td class="mono">10.20.{{ 10 + i }}.{{ 100 + i }}</td>
                <td>
                  <span class="stat" :class="c.stTone">{{ c.st }}</span>
                </td>
                <td class="num mono">
                  <span v-if="c.healthStatus === 'BASELINE_LEARNING'" class="pm-baseline" title="기준선 학습 중">
                    <i class="bi bi-cpu"></i> {{ c.baselineSamples }}/{{ c.baselineRequired }}
                  </span>
                  <span v-else-if="c.healthScore != null" class="pm-hs" :class="pmScoreTone(c.healthScore)">{{ c.healthScore.toFixed(1) }}</span>
                  <span v-else class="pm-hs gy">—</span>
                </td>
                <td class="mono">{{ c.lat }}<span v-if="c.lat !== '—'">ms</span></td>
                <td
                  class="mono"
                  :class="c.st === '장애' ? 'rd-txt' : c.st === '지연' ? 'yl-txt' : ''"
                >
                  {{ c.st === "장애" ? "0.0" : (95 + (i % 5)).toFixed(1) }}%
                </td>
                <td class="mono">{{ c.st === "장애" ? "—" : 88 + (i % 11) + "%" }}</td>
                <td class="mono">
                  v{{
                    [
                      "3.2.1",
                      "3.2.1",
                      "3.1.8",
                      "3.2.0",
                      "3.2.1",
                      "3.0.5",
                      "3.2.1",
                      "2.9.4",
                    ][i]
                  }}
                </td>
                <td class="mono">
                  {{
                    [
                      "2025-04-12",
                      "2025-03-28",
                      "2025-04-22",
                      "2024-12-15",
                      "2025-04-30",
                      "2025-02-17",
                      "2025-04-04",
                      "2025-05-10",
                    ][i]
                  }}
                </td>
                <td class="mono">{{ c.ts }}</td>
                <td><i class="bi bi-chevron-right" style="opacity: 0.5"></i></td>
              </tr>
              <tr v-if="!filteredCams.length">
                <td colspan="13" class="pnl-empty">검색 결과 없음</td>
              </tr>
            </tbody>
          </table>
          <div class="pnl-foot">
            <span>표시 {{ filteredCams.length }} / {{ cams.length }} (전체 25)</span>
            <div class="pg-row">
              <button>‹</button>
              <button class="on">1</button><button>2</button><button>3</button>
              <button>›</button>
            </div>
          </div>
        </div>

      </section>

      <section v-if="tab === 'srv'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>
            서버 / OCR 엔진 상태 <span class="ch-kpi">{{ servers.length }}대 운영</span>
          </h3>
          <div class="pnl-tools">
            <select v-model="srvRange">
              <option value="1h">최근 1시간</option>
              <option value="24h">최근 24시간</option>
              <option value="7d">최근 7일</option>
            </select>
            <button class="pnl-act">
              <i class="bi bi-arrow-clockwise"></i> 새로고침
            </button>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV</button>
          </div>
        </div>
        <div class="pnl-summary nd-kpi nd-kpi-7">
          <div class="ps-box">
            <div class="ps-l">전체 서버</div>
            <div class="ps-v">2</div>
            <div class="ps-sub">운영 중</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">50.0%</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">경고</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">50.0%</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 CPU</div>
            <div class="ps-v">42<span>%</span></div>
            <div class="ps-sub">최근 1시간</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 메모리</div>
            <div class="ps-v">55<span>%</span></div>
            <div class="ps-sub">최근 1시간</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">서비스 가동</div>
            <div class="ps-v">14<span>/15</span></div>
            <div class="ps-sub">93.3%</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 응답시간</div>
            <div class="ps-v">48<span>ms</span></div>
            <div class="ps-sub">OCR 처리</div>
          </div>
        </div>

        <div v-for="(s, i) in servers" :key="i" class="srv srv-detail">
          <div class="srv-h">
            <div class="srv-name">
              <svg viewBox="0 0 32 32" class="srv-icon" aria-hidden="true">
                <polygon points="6,10 16,4 28,8 18,14" fill="#7ea4d8" />
                <polygon points="6,10 18,14 18,28 6,24" fill="#2563eb" />
                <polygon points="18,14 28,8 28,22 18,28" fill="#1d4ed8" />
                <circle cx="9" cy="14" r="1" fill="#34d399" />
                <circle
                  cx="9"
                  cy="18"
                  r="1"
                  :fill="s.stTone === 'wn' ? '#fbbf24' : '#34d399'"
                />
                <circle cx="9" cy="22" r="1" fill="#34d399" />
              </svg>
              <div>
                <div class="sn-t">
                  {{ s.name }} <span class="sn-tag" v-if="s.tag">{{ s.tag }}</span>
                </div>
                <div class="sn-ip">
                  {{ s.ip }} ·
                  {{
                    [
                      "Ubuntu 22.04 / CPU 16C 32G",
                      "Ubuntu 22.04 / CPU 16C 32G",
                      "Rocky 9 / CPU 8C 16G",
                    ][i]
                  }}
                </div>
              </div>
            </div>
            <div class="srv-h-r">
              <span class="srv-uptime">가동 {{ [37, 37, 12][i] }}일</span>
              <span class="stat" :class="s.stTone">{{ s.st }}</span>
            </div>
          </div>
          <div class="srv-bars">
            <div v-for="b in s.bars" :key="b.l" class="srv-b">
              <div class="srv-lab">{{ b.l }}</div>
              <div class="srv-val" :class="b.tone">{{ b.v }}</div>
              <div class="bar">
                <span :style="{ width: b.bar + '%', background: b.color }"></span>
              </div>
            </div>
          </div>
          <div class="srv-meta">
            <span
              ><i class="bi bi-globe2"></i>
              {{ ["처리량 1.2k req/s", "대기", "검색 32 qps"][i] }}</span
            >
            <span
              ><i class="bi bi-thermometer-half"></i>
              {{ ["58°C", "52°C", "64°C"][i] }}</span
            >
            <span
              ><i class="bi bi-arrow-down"></i> {{ ["142", "128", "310"][i] }} Mbps</span
            >
            <span><i class="bi bi-arrow-up"></i> {{ ["98", "12", "215"][i] }} Mbps</span>
            <span><i class="bi bi-people"></i> 접속 {{ [42, 0, 18][i] }}</span>
          </div>
        </div>

        <!-- 서비스 / 프로세스 상태 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>서비스 / 프로세스 상태</h4>
            <span class="nd-h-cnt">{{ srvServices.length }}개 서비스</span>
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>서비스명</th>
                <th>호스트</th>
                <th>포트</th>
                <th>PID</th>
                <th>버전</th>
                <th>응답시간</th>
                <th>업타임</th>
                <th>마지막 재시작</th>
                <th>상태</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in srvServices" :key="s.name">
                <td class="mono"><i class="bi bi-hdd-fill"></i> {{ s.name }}</td>
                <td>{{ s.host }}</td>
                <td class="mono">{{ s.port }}</td>
                <td class="mono">{{ s.pid }}</td>
                <td class="mono">{{ s.ver }}</td>
                <td
                  class="mono"
                  :class="s.tone === 'rd' ? 'rd-txt' : s.tone === 'yl' ? 'yl-txt' : ''"
                >
                  {{ s.rt }}
                </td>
                <td class="mono">{{ s.uptime }}</td>
                <td class="mono">{{ s.lastRestart }}</td>
                <td>
                  <span class="stat" :class="s.statTone">{{ s.stat }}</span>
                </td>
                <td><button class="pnl-act sm">재시작</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 최근 서버 이벤트 -->
        <div class="nd-block">
          <div class="nd-h"><h4>최근 서버 이벤트</h4></div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>발생 시각</th>
                <th>호스트</th>
                <th>이벤트</th>
                <th>심각도</th>
                <th>지속</th>
                <th>처리</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="mono">14:18:42</td>
                <td class="mono">ocr-srv-02</td>
                <td>디스크 사용량 78% 임계 초과</td>
                <td><span class="stat wn">HIGH</span></td>
                <td class="mono yl-txt">14분</td>
                <td>박과장</td>
              </tr>
              <tr>
                <td class="mono">10:32:15</td>
                <td class="mono">ocr-srv-02</td>
                <td>메모리 88% 일시 spike</td>
                <td><span class="stat wn">MED</span></td>
                <td class="mono">3분 22초</td>
                <td>자동 GC</td>
              </tr>
              <tr>
                <td class="mono">08:00:00</td>
                <td class="mono">ocr-srv-01</td>
                <td>주간 정기 백업 완료 (4.2GB)</td>
                <td><span class="stat ok">INFO</span></td>
                <td class="mono">—</td>
                <td>자동</td>
              </tr>
              <tr>
                <td class="mono">02:15:03</td>
                <td class="mono">ocr-srv-03</td>
                <td>로그 로테이트 완료</td>
                <td><span class="stat ok">INFO</span></td>
                <td class="mono">—</td>
                <td>자동</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="tab === 'net'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>
            네트워크 지연 현황
            <span class="ch-kpi">{{ netPaths.length }}개 경로 모니터링</span>
          </h3>
          <div class="pnl-tools">
            <select v-model="netZone">
              <option value="all">전체 구역</option>
              <option>강변북로</option>
              <option>올림픽대로</option>
              <option>내부순환</option>
              <option>경부고속</option>
            </select>
            <select v-model="netRange">
              <option value="1h">최근 1시간</option>
              <option value="6h">최근 6시간</option>
              <option value="24h">최근 24시간</option>
              <option value="7d">최근 7일</option>
            </select>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV 내보내기</button>
          </div>
        </div>

        <!-- 상단 KPI 6개 -->
        <div class="pnl-summary nd-kpi">
          <div class="ps-box">
            <div class="ps-l">평균 지연</div>
            <div class="ps-v">128<span>ms</span></div>
            <div class="ps-sub">전일 대비 +4ms</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">최대 지연</div>
            <div class="ps-v">286<span>ms</span></div>
            <div class="ps-sub">14:24 NSN-N-0023</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">P95 지연</div>
            <div class="ps-v">142<span>ms</span></div>
            <div class="ps-sub">상위 5% 기준</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">23<span>/25</span></div>
            <div class="ps-sub">92.0%</div>
          </div>
          <div class="ps-box rd">
            <div class="ps-l">장애</div>
            <div class="ps-v">1<span>/25</span></div>
            <div class="ps-sub">4.0%</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">패킷 손실</div>
            <div class="ps-v">0.4<span>%</span></div>
            <div class="ps-sub">최근 1시간</div>
          </div>
        </div>

        <!-- 24h 라인 차트 + 임계선 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>24시간 지연 추이</h4>
            <div class="nd-h-r">
              <span><span class="lg-l bl"></span> 평균 지연</span>
              <span><span class="lg-l gr"></span> 정상 ≤100ms</span>
              <span><span class="lg-l rd"></span> 임계 200ms</span>
              <span><span class="lg-l sp"></span> 이상</span>
            </div>
          </div>
          <div class="nd-chart">
            <div class="nc-y">
              <span>300</span><span>200</span><span>100</span><span>0</span>
            </div>
            <div class="nc-svgwrap">
              <svg viewBox="0 0 480 140" preserveAspectRatio="none" class="nc-svg">
                <rect x="0" y="0" width="480" height="46.67" fill="rgba(220,38,38,.06)" />
                <rect
                  x="0"
                  y="46.67"
                  width="480"
                  height="46.67"
                  fill="rgba(180,83,9,.05)"
                />
                <line
                  x1="0"
                  y1="46.67"
                  x2="480"
                  y2="46.67"
                  stroke="#b91c1c"
                  stroke-dasharray="4 4"
                  stroke-width="0.6"
                />
                <line
                  x1="0"
                  y1="93.33"
                  x2="480"
                  y2="93.33"
                  stroke="#047857"
                  stroke-dasharray="4 4"
                  stroke-width="0.6"
                />
                <polyline
                  points="0,100 40,105 80,98 120,89 160,96 200,79 240,91 280,7 320,86 360,96 400,99 440,92 480,97"
                  fill="none"
                  stroke="#2563eb"
                  stroke-width="1.8"
                  vector-effect="non-scaling-stroke"
                />
                <circle
                  cx="280"
                  cy="7"
                  r="4"
                  fill="#dc2626"
                  stroke="#fff"
                  stroke-width="1.2"
                />
              </svg>
              <div class="nc-spike" style="left: 58%">
                <strong>NSN-N-0023</strong>
                <span>286ms · 14:24</span>
              </div>
            </div>
            <div class="nc-x">
              <span>00</span><span>04</span><span>08</span><span>12</span><span>16</span
              ><span>20</span><span>24</span>
            </div>
          </div>
        </div>

        <!-- 구간별 상세 표 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>경로별 상세</h4>
            <span class="nd-h-cnt">{{ netPaths.length }}개 경로</span>
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>경로 ID</th>
                <th>출발</th>
                <th>도착</th>
                <th>현재 RTT</th>
                <th>24h 평균</th>
                <th>최대</th>
                <th>패킷 손실</th>
                <th>업타임</th>
                <th>마지막 응답</th>
                <th>상태</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in netPaths" :key="i">
                <td class="mono">PATH-{{ String(i + 1).padStart(3, "0") }}</td>
                <td>{{ p.from }}</td>
                <td>{{ p.to }}</td>
                <td class="mono">
                  <strong>{{ p.lat }}</strong
                  >{{ typeof p.lat === "number" ? "ms" : "" }}
                </td>
                <td class="mono">{{ p.avg }}ms</td>
                <td class="mono">{{ Math.round(p.avg * 1.6) }}ms</td>
                <td
                  class="mono"
                  :class="p.loss > 0 ? (p.loss >= 50 ? 'rd-txt' : 'yl-txt') : ''"
                >
                  {{ p.loss }}%
                </td>
                <td class="mono">
                  {{ p.tone === "bad" ? "0.0%" : p.tone === "warn" ? "98.4%" : "99.97%" }}
                </td>
                <td class="mono">
                  {{
                    p.tone === "bad"
                      ? "12분 전"
                      : p.tone === "warn"
                      ? "8초 전"
                      : "< 1초 전"
                  }}
                </td>
                <td>
                  <span class="stat" :class="p.tone">{{ p.st }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 최근 이상 이벤트 -->
        <div class="nd-block">
          <div class="nd-h"><h4>최근 네트워크 이상 이벤트</h4></div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>발생 시각</th>
                <th>장비</th>
                <th>구간</th>
                <th>유형</th>
                <th>심각도</th>
                <th>지속 시간</th>
                <th>조치</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="mono">14:24:17</td>
                <td>NSN-N-0023</td>
                <td>EDGE-W → 한남TG</td>
                <td>RTSP 응답 없음</td>
                <td><span class="stat no">CRIT</span></td>
                <td class="mono rd-txt">8분 1초</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">14:18:05</td>
                <td>GBG-S-0077</td>
                <td>EDGE-S → 강변북로</td>
                <td>지연 286ms 임계 초과</td>
                <td><span class="stat wn">HIGH</span></td>
                <td class="mono yl-txt">14분 13초</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">13:55:18</td>
                <td>CAM-IC-0011</td>
                <td>EDGE-N → 정릉</td>
                <td>연결 복구 완료</td>
                <td><span class="stat ok">INFO</span></td>
                <td class="mono">—</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">11:15:09</td>
                <td>OLP-W-0041</td>
                <td>EDGE-S → 올림픽대로</td>
                <td>전원 차단 후 복구</td>
                <td><span class="stat ok">INFO</span></td>
                <td class="mono">—</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="tab === 'alarm'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>
            알람 / 이벤트 <span class="ch-kpi">{{ alarmsExt.length }}건</span>
          </h3>
          <div class="pnl-tools">
            <select v-model="alarmSev">
              <option value="all">전체 심각도</option>
              <option>CRIT</option>
              <option>HIGH</option>
              <option>MED</option>
              <option>INFO</option>
            </select>
            <button class="pnl-act"><i class="bi bi-bell-slash"></i> 음소거</button>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV</button>
          </div>
        </div>

        <!-- 심각도별 KPI 7박스 -->
        <div class="pnl-summary nd-kpi nd-kpi-7">
          <div class="ps-box rd">
            <div class="ps-l">CRIT</div>
            <div class="ps-v">3</div>
            <div class="ps-sub">즉시 대응 필요</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">HIGH</div>
            <div class="ps-v">5</div>
            <div class="ps-sub">SLA 위반 2</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">MED</div>
            <div class="ps-v">8</div>
            <div class="ps-sub">정상 범위</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">INFO</div>
            <div class="ps-v">12</div>
            <div class="ps-sub">자동 처리</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">해결됨 24h</div>
            <div class="ps-v">17</div>
            <div class="ps-sub">자동 73%</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 응답</div>
            <div class="ps-v">4.2<span>분</span></div>
            <div class="ps-sub">전일 -1.1분</div>
          </div>
          <div class="ps-box rd">
            <div class="ps-l">SLA 위반</div>
            <div class="ps-v">2</div>
            <div class="ps-sub">15분 초과</div>
          </div>
        </div>

        <!-- 카테고리별 분포 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>카테고리별 분포 (24h)</h4>
            <span class="nd-h-cnt">총 {{ alarmsExt.length }}건</span>
          </div>
          <div class="cd-zones">
            <div class="cdz" v-for="c in alarmCats" :key="c.name">
              <div class="cdz-h">
                <span class="cdz-n">{{ c.name }}</span>
                <span class="cdz-c"
                  ><strong>{{ c.crit + c.high + c.med + c.info }}</strong
                  ><em>건</em></span
                >
              </div>
              <div class="cdz-bar">
                <span class="rd" :style="{ flex: c.crit }"></span>
                <span class="yl" :style="{ flex: c.high }"></span>
                <span class="yl" :style="{ flex: c.med, opacity: 0.6 }"></span>
                <span style="flex: 1; background: #c9d4e3" v-if="c.info"></span>
              </div>
              <div class="cdz-leg">
                <span><span class="ns-d rd"></span>{{ c.crit }}</span>
                <span><span class="ns-d yl"></span>{{ c.high + c.med }}</span>
                <span style="color: #6b7a92">{{ c.info }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- SLA 위반 진행 중 알람 (강조) -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>SLA 위반 / 진행 중 알람</h4>
            <span class="nd-h-cnt rd-txt">즉시 대응 필요</span>
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>발생</th>
                <th>심각도</th>
                <th>장비</th>
                <th>메시지</th>
                <th>경과</th>
                <th>SLA</th>
                <th>담당자</th>
                <th>조치</th>
              </tr>
            </thead>
            <tbody>
              <tr class="bad">
                <td class="mono">14:24:17</td>
                <td><span class="stat no">CRIT</span></td>
                <td class="mono">NSN-N-0023</td>
                <td>RTSP 스트림 응답 없음 (timeout 30s)</td>
                <td class="mono rd-txt"><strong>8분 1초</strong></td>
                <td class="mono rd-txt">초과 0:08</td>
                <td>김기사</td>
                <td><button class="pnl-act sm">처리</button></td>
              </tr>
              <tr class="bad">
                <td class="mono">14:11:42</td>
                <td><span class="stat wn">HIGH</span></td>
                <td class="mono">ocr-srv-02</td>
                <td>디스크 사용량 78% 경고</td>
                <td class="mono rd-txt"><strong>20분 36초</strong></td>
                <td class="mono rd-txt">초과 5:36</td>
                <td>—</td>
                <td><button class="pnl-act sm">배정</button></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 전체 알람 표 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>전체 알람 목록</h4>
            <span class="nd-h-cnt"
              >{{ filteredAlarmExt.length }} / {{ alarmsExt.length }}건</span
            >
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>발생</th>
                <th>심각도</th>
                <th>구분</th>
                <th>장비</th>
                <th>메시지</th>
                <th>담당자</th>
                <th>상태</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in filteredAlarmExt" :key="a.id">
                <td class="mono">{{ a.time }}</td>
                <td>
                  <span class="stat" :class="a.tone">{{ a.sev }}</span>
                </td>
                <td>{{ a.cat }}</td>
                <td class="mono">{{ a.dev }}</td>
                <td>{{ a.msg }}</td>
                <td>{{ a.who }}</td>
                <td>
                  <span class="stat" :class="a.handled ? 'ok' : 'wn'">{{
                    a.handled ? "처리됨" : "진행중"
                  }}</span>
                </td>
                <td><i class="bi bi-chevron-right" style="opacity: 0.5"></i></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="tab === 'fault'" class="card pnl net-detail pm-fault-scroll">
        <div class="pnl-head">
          <h3>
            장애·이상 관리
            <span class="ch-kpi rd">장애 3 · 이상 {{ pmAnomalyCount }} · SLA 초과 {{ pmSlaOverdueCount }}</span>
          </h3>
          <div class="pnl-tools">
            <button
              class="pnl-act"
              :disabled="!canCreateTicket"
              :title="canCreateTicket ? '' : '수동 티켓 생성 권한 없음 (OPERATOR/ADMIN)'"
            >
              <i class="bi bi-plus-circle"></i> 장애 신규 등록
            </button>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV</button>
          </div>
        </div>

        <!-- KPI 8박스 (예지 통합: 악화 예측 / SLA 초과 강조) -->
        <div class="pnl-summary nd-kpi nd-kpi-8">
          <div class="ps-box rd">
            <div class="ps-l">진행 중</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">CAM-M-002</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">처리 중</div>
            <div class="ps-v">2</div>
            <div class="ps-sub">담당자 배정</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">금일 복구</div>
            <div class="ps-v">5</div>
            <div class="ps-sub">자동 3, 수동 2</div>
          </div>
          <div class="ps-box pm-alert" :class="{ alert: pmPredictedCount2 > 0 }">
            <div class="ps-l"><i class="bi bi-graph-up-arrow"></i> 악화 예측</div>
            <div class="ps-v">{{ pmPredictedCount2 }}<span>건</span></div>
            <div class="ps-sub">임계 도달 예상</div>
          </div>
          <div class="ps-box pm">
            <div class="ps-l"><i class="bi bi-bullseye"></i> 활성 이상</div>
            <div class="ps-v">{{ pmAnomalyCount }}<span>건</span></div>
            <div class="ps-sub">예지 탐지</div>
          </div>
          <div class="ps-box pm">
            <div class="ps-l"><i class="bi bi-hourglass-split"></i> MTTA</div>
            <div class="ps-v">{{ pmMtta }}<span>분</span></div>
            <div class="ps-sub">평균 응답</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">MTTR</div>
            <div class="ps-v">{{ pmMttr }}<span>분</span></div>
            <div class="ps-sub">평균 복구</div>
          </div>
          <div class="ps-box pm-alert" :class="{ alert: pmSlaOverdueCount > 0 }">
            <div class="ps-l"><i class="bi bi-stopwatch"></i> SLA 초과</div>
            <div class="ps-v">{{ pmSlaOverdueCount }}<span>건</span></div>
            <div class="ps-sub">조치 지연 티켓</div>
          </div>
        </div>

        <!-- ===== 활성 이상 이벤트 (예지 탐지) — 진행 중 장애 위에 배치 ===== -->
        <div class="nd-block" v-if="activeAnomaly">
          <div class="nd-h">
            <h4>
              <i class="bi bi-bullseye"></i> 활성 이상 이벤트
              <span class="pm-pred-bdg" v-if="activeAnomaly.detectionMethod === 'TREND_PROJECTION'">
                <i class="bi bi-graph-up-arrow"></i> 악화 예측
              </span>
            </h4>
            <span class="nd-h-cnt">{{ activeAnomaly.id }} · {{ activeAnomaly.dev }}</span>
          </div>

          <div class="pm-anom-card">
            <!-- 헤더: 유형 / 심각도 / 탐지 방식 / SLA -->
            <div class="pm-anom-head">
              <div class="pm-anom-titles">
                <span class="sev-bdg" :class="activeAnomaly.tone">{{ activeAnomaly.sev }}</span>
                <strong>{{ anomalyTypeLabelKo(activeAnomaly.anomalyType) }}</strong>
                <span class="dm-bdg">{{ detectionMethodLabelKo(activeAnomaly.detectionMethod) }}</span>
                <span class="pri-bdg" :class="pmPriorityTone(activeAnomaly.priority)">{{ activeAnomaly.priority }}</span>
              </div>
              <div class="pm-anom-time" v-if="activeAnomaly.projectedAt">
                <i class="bi bi-clock-history"></i>
                <strong class="rd-txt">{{ activeAnomaly.projectedAt }} 임계 도달 예상</strong>
              </div>
            </div>

            <!-- 통계 지표 + detector 정보 -->
            <div class="pm-stats-row" v-if="activeAnomaly.trend || activeAnomaly.detector">
              <div v-if="activeAnomaly.trend?.robustZScore != null" class="pm-stat">
                <div class="pm-stat-l">Robust Z-score</div>
                <div class="pm-stat-v" :class="zScoreTone(activeAnomaly.trend.robustZScore)">
                  {{ activeAnomaly.trend.robustZScore.toFixed(2) }}
                </div>
                <div class="pm-stat-s">기준선 대비 편차</div>
              </div>
              <div v-if="activeAnomaly.trend?.slope != null" class="pm-stat">
                <div class="pm-stat-l">추세 기울기</div>
                <div class="pm-stat-v" :class="slopeTone(activeAnomaly.trend.slope)">
                  {{ activeAnomaly.trend.slope > 0 ? '+' : '' }}{{ activeAnomaly.trend.slope.toFixed(2) }}<small>/분</small>
                </div>
                <div class="pm-stat-s">{{ activeAnomaly.trend.slope < 0 ? '하향' : '상승' }} 추세</div>
              </div>
              <div v-if="activeAnomaly.trend?.confidence != null" class="pm-stat">
                <div class="pm-stat-l">추세 신뢰도</div>
                <div class="pm-stat-v" :class="confTone(activeAnomaly.trend.confidence)">
                  {{ (activeAnomaly.trend.confidence * 100).toFixed(0) }}<small>%</small>
                </div>
                <div class="pm-stat-s">{{ activeAnomaly.trend.confidence >= 0.7 ? '높음' : '보통' }}</div>
              </div>
              <div v-if="activeAnomaly.detector" class="pm-stat pm-stat-det">
                <div class="pm-stat-l">탐지기</div>
                <div class="pm-stat-v pm-stat-det-name">{{ activeAnomaly.detector.name }}</div>
                <div class="pm-stat-s">
                  v{{ activeAnomaly.detector.version }} · {{ activeAnomaly.detector.policyCode }}
                </div>
              </div>
            </div>

            <!-- 관측값 / 기준값 / 임계값 비교 표 -->
            <table class="pm-evidence-tbl">
              <thead>
                <tr>
                  <th>지표</th>
                  <th class="num">관측값</th>
                  <th class="num">기준선 (median)</th>
                  <th class="num">임계값</th>
                  <th>판정</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="e in activeAnomaly.evidence" :key="e.metric">
                  <td>{{ e.metric }}</td>
                  <td class="num mono"><strong :class="evTone(e)">{{ e.observed }}{{ e.unit }}</strong></td>
                  <td class="num mono">{{ e.baseline }}{{ e.unit }}</td>
                  <td class="num mono rd-txt">{{ e.threshold }}{{ e.unit }}</td>
                  <td><span class="ev-jd" :class="evTone(e)">{{ evJudge(e) }}</span></td>
                </tr>
              </tbody>
            </table>

            <!-- 교통 맥락 교차검증 -->
            <div class="pm-traffic" v-if="activeAnomaly.trafficContext">
              <div class="pm-traffic-h">
                <i class="bi bi-car-front-fill"></i>
                <strong>교통 맥락 교차검증</strong>
                <span class="pm-traffic-jd" :class="trafficJdTone(activeAnomaly.trafficContext.crossValidation)">
                  {{ trafficJdLabel(activeAnomaly.trafficContext.crossValidation) }}
                </span>
              </div>
              <div class="pm-traffic-body">
                <div class="pm-traffic-self">
                  <div class="pm-traffic-l">본 카메라</div>
                  <div class="pm-traffic-v">
                    <strong>{{ activeAnomaly.trafficContext.currentVehicleCount }}</strong>대
                    <span class="pm-traffic-sub">· {{ activeAnomaly.trafficContext.currentAvgSpeed }}km/h</span>
                  </div>
                </div>
                <i class="bi bi-arrow-left-right pm-traffic-arr"></i>
                <div class="pm-traffic-adj">
                  <div class="pm-traffic-l">인접 카메라 평균</div>
                  <div class="pm-traffic-v">
                    <strong>{{ adjacentAvg(activeAnomaly.trafficContext) }}</strong>대
                    <span class="pm-traffic-sub">· {{ adjacentSpeedAvg(activeAnomaly.trafficContext) }}km/h</span>
                  </div>
                </div>
              </div>
              <div class="pm-traffic-note">{{ activeAnomaly.trafficContext.crossValidationLabel }}</div>
            </div>

            <!-- 원인 후보 / 운영자 확정 원인 -->
            <div class="pm-causes">
              <div class="pm-cause-blk">
                <div class="pm-cause-h">원인 후보 <em>(탐지 시스템 추정)</em></div>
                <ul class="pm-cause-list">
                  <li v-for="(c, i) in activeAnomaly.suspectedCauses" :key="i">{{ c }}</li>
                </ul>
              </div>
              <div class="pm-cause-blk confirmed">
                <div class="pm-cause-h">확정 원인 <em>(운영자 입력)</em></div>
                <div v-if="activeAnomaly.confirmedCause" class="pm-confirmed">
                  ✓ {{ activeAnomaly.confirmedCause }}
                </div>
                <div v-else class="pm-confirmed-empty">
                  <i class="bi bi-pencil-square"></i> 미확정 — 해결(resolve) 시 입력 필요
                </div>
              </div>
            </div>

            <!-- SHADOW (LSTM AutoEncoder) — 비교 모델, 운영 판정에 사용 X -->
            <div class="pm-shadow" v-if="activeAnomaly.shadowModel">
              <div class="pm-shadow-h">
                <i class="bi bi-cpu"></i>
                <strong>비교 모델</strong>
                <span class="shadow-bdg">SHADOW · {{ activeAnomaly.shadowModel.name }} v{{ activeAnomaly.shadowModel.version }}</span>
                <span class="pm-shadow-note">운영 이벤트 생성에 사용되지 않음 (비교·평가용)</span>
              </div>
              <div class="pm-shadow-body">
                <div class="pm-shadow-score">
                  <div class="pm-ss-l">재구성 오차</div>
                  <div class="pm-ss-v" :class="shadowScoreTone(activeAnomaly.shadowModel)">
                    {{ activeAnomaly.shadowModel.score.toFixed(2) }}
                  </div>
                  <div class="pm-ss-thr">
                    임계 W {{ activeAnomaly.shadowModel.warningThreshold }} · C {{ activeAnomaly.shadowModel.criticalThreshold }}
                  </div>
                  <div class="pm-ss-pred">
                    예측 심각도: <strong :class="shadowPredTone(activeAnomaly.shadowModel)">{{ activeAnomaly.shadowModel.predictedSeverity }}</strong>
                  </div>
                </div>
                <div class="pm-shadow-feats">
                  <div class="pm-sf-l">기여 feature <em>(재구성 오차 평균 상위 — 원인 확정값 아님)</em></div>
                  <div class="pm-sf-rows">
                    <div v-for="f in activeAnomaly.shadowModel.topFeatures" :key="f.name" class="pm-sf-row">
                      <span class="pm-sf-n">{{ f.name }}</span>
                      <div class="pm-sf-bar">
                        <div class="pm-sf-fill" :style="{ width: (f.value * 100) + '%' }"></div>
                      </div>
                      <span class="pm-sf-v mono">{{ f.value.toFixed(2) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 연결된 정비 티켓 -->
            <div class="pm-linked-ticket" v-if="linkedTicket(activeAnomaly)">
              <i class="bi bi-link-45deg"></i>
              <span class="pm-linked-l">연결된 정비 티켓</span>
              <strong>{{ linkedTicket(activeAnomaly).id }}</strong>
              <span class="pri-bdg" :class="pmPriorityTone(linkedTicket(activeAnomaly).priority)">{{ linkedTicket(activeAnomaly).priority }}</span>
              <span class="stat" :class="linkedTicket(activeAnomaly).stTone">{{ ticketStatusLabel(linkedTicket(activeAnomaly).ticketStatus) }}</span>
              <span class="pm-linked-sla mono">SLA {{ formatSlaRemaining(linkedTicket(activeAnomaly).slaRemainingMin) }}</span>
            </div>
            <div class="pm-linked-ticket none" v-else>
              <i class="bi bi-info-circle"></i>
              연결된 정비 티켓 없음 — 해결 시 자동 생성됩니다
            </div>

            <!-- 액션: 권한 매트릭스 기반 노출 -->
            <div class="pm-anom-acts" role="group" aria-label="이상 이벤트 처리">
              <button
                class="pnl-act"
                :disabled="!canResolveAnomaly"
                :aria-disabled="!canResolveAnomaly"
                :title="canResolveAnomaly ? '' : 'OPERATOR/ADMIN만 해결 처리 가능'"
                @click="openAnomalyResolve(activeAnomaly)"
              >
                <i class="bi bi-check2-circle" aria-hidden="true"></i> 해결(resolve)
              </button>
              <button
                class="pnl-act"
                :disabled="!canResolveAnomaly"
                :aria-disabled="!canResolveAnomaly"
                :title="canResolveAnomaly ? '' : 'OPERATOR/ADMIN만 오탐 종료 가능'"
                @click="openAnomalyDismiss(activeAnomaly)"
              >
                <i class="bi bi-x-circle" aria-hidden="true"></i> 오탐 종료(dismiss)
              </button>
              <button
                class="pnl-act"
                :disabled="!canAssignTicket"
                :aria-disabled="!canAssignTicket"
                :title="canAssignTicket ? '' : 'OPERATOR/ADMIN만 담당자 배정 가능'"
                @click="openAssignModal(activeAnomaly)"
              >
                <i class="bi bi-person-plus" aria-hidden="true"></i> 담당자 배정
              </button>
            </div>
          </div>
        </div>


        <!-- 전체 장애·이상 목록 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>전체 장애·이상 목록</h4>
            <span class="nd-h-cnt">{{ filteredFaults.length }} / {{ faults.length }}건 ({{ pmAnomalyCount }} 예지 탐지 포함)</span>
          </div>

          <!-- 필터 -->
          <div class="pm-fault-filter">
            <select v-model="faultFilter.kind">
              <option value="">전체</option>
              <option value="fault">장애만</option>
              <option value="anomaly">이상 이벤트만</option>
            </select>
            <select v-model="faultFilter.priority">
              <option value="">우선순위 전체</option>
              <option value="P1">P1</option>
              <option value="P2">P2</option>
              <option value="P3">P3</option>
            </select>
            <select v-model="faultFilter.detectionMethod">
              <option value="">탐지 방식 전체</option>
              <option value="RULE">룰</option>
              <option value="TREND_PROJECTION">추세 예측</option>
              <option value="ROBUST_Z_SCORE">z-score</option>
              <option value="CROSS_VALIDATION">교차 검증</option>
            </select>
            <select v-model="faultFilter.status">
              <option value="">상태 전체</option>
              <option value="OPEN">대기</option>
              <option value="ASSIGNED">배정</option>
              <option value="IN_PROGRESS">진행 중</option>
              <option value="RESOLVED">해결</option>
              <option value="CLOSED">종결</option>
            </select>
            <label class="pm-fault-flag">
              <input type="checkbox" v-model="faultFilter.slaOverdueOnly" />
              SLA 초과만
            </label>
            <button class="pnl-act sm" @click="resetFaultFilter">
              <i class="bi bi-arrow-counterclockwise"></i> 초기화
            </button>
          </div>

          <table class="pnl-tbl nd-tbl pm-fault-tbl">
            <thead>
              <tr>
                <th>ID</th>
                <th class="num">P</th>
                <th>발생 시각</th>
                <th>장비</th>
                <th>증상</th>
                <th>심각도</th>
                <th>탐지</th>
                <th>담당자</th>
                <th>SLA 잔여</th>
                <th>상태</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in filteredFaults" :key="f.id">
                <td class="mono">
                  {{ f.id }}
                  <span v-if="f.kind === 'anomaly'" class="pm-kind-bdg" title="예지보전 탐지">PM</span>
                </td>
                <td class="num">
                  <span class="pri-bdg" :class="pmPriorityTone(f.priority)">{{ f.priority }}</span>
                </td>
                <td class="mono">{{ f.time }}</td>
                <td class="mono">{{ f.dev }}</td>
                <td>
                  {{ f.symp }}
                  <span
                    v-if="f.detectionMethod === 'TREND_PROJECTION'"
                    class="pm-pred-bdg sm"
                  >
                    <i class="bi bi-graph-up-arrow"></i> 악화 예측
                  </span>
                </td>
                <td>
                  <span class="stat" :class="f.tone">{{ f.sev }}</span>
                </td>
                <td>
                  <span class="dm-bdg sm" v-if="f.detectionMethod">
                    {{ detectionMethodLabelKo(f.detectionMethod) }}
                  </span>
                </td>
                <td>{{ f.who }}</td>
                <td class="mono" :class="f.slaOverdue ? 'rd-txt' : f.slaRemainingMin < 30 ? 'yl-txt' : ''">
                  <template v-if="f.slaOverdue">
                    <i class="bi bi-exclamation-octagon-fill"></i> {{ formatSlaRemaining(f.slaRemainingMin) }}
                  </template>
                  <template v-else>
                    {{ formatSlaRemaining(f.slaRemainingMin) }}
                  </template>
                </td>
                <td>
                  <span class="stat" :class="f.stTone">{{ f.st }}</span>
                </td>
                <td class="pm-fault-acts">
                  <button
                    v-if="canTransitionTicket(f.ticketStatus, 'IN_PROGRESS')"
                    class="pnl-act sm"
                    @click="openTicketTransition(f, 'IN_PROGRESS')"
                  >작업 시작</button>
                  <button
                    v-if="canTransitionTicket(f.ticketStatus, 'RESOLVED')"
                    class="pnl-act sm gr"
                    @click="openTicketTransition(f, 'RESOLVED')"
                  >해결</button>
                  <button
                    v-if="canTransitionTicket(f.ticketStatus, 'CLOSED')"
                    class="pnl-act sm"
                    @click="openTicketTransition(f, 'CLOSED')"
                    title="OPERATOR/ADMIN만 처리 가능"
                  >최종 종결</button>
                  <button class="pnl-act sm">상세</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>

      <!-- ============ 담당자 배정 모달 ============ -->
      <div
        v-if="assignModal"
        class="cam-modal-bg"
        @click="closeAssignModal"
        role="dialog"
        aria-modal="true"
        aria-label="담당자 배정"
      >
        <div class="cam-modal pm-ticket-modal" @click.stop>
          <div class="cm-h">
            <div class="cm-title">
              <i class="bi bi-person-plus" aria-hidden="true"></i>
              <span>담당자 배정</span>
            </div>
            <button class="cm-x" @click="closeAssignModal" aria-label="닫기"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
          </div>
          <div class="pm-ticket-body">
            <div class="cm-row">
              <span>대상 ID</span><strong>{{ assignModal.target.id }}</strong>
            </div>
            <div class="cm-row">
              <span>장비</span><strong>{{ assignModal.target.dev }}</strong>
            </div>
            <div class="pm-ticket-note">
              <label>담당자 선택 <span class="req">* 필수</span></label>
              <select v-model="assignModal.assigneeId">
                <option value="">선택…</option>
                <option v-for="a in assignees" :key="a.id" :value="a.id">
                  {{ a.name }} ({{ a.role }})
                </option>
              </select>
            </div>
            <div class="pm-ticket-note">
              <label>전달 메모 (선택)</label>
              <textarea
                v-model="assignModal.note"
                placeholder="담당자에게 전달할 내용 (예: 현장 점검 / 원격 진단 / 부품 교체 등)"
                rows="3"
              ></textarea>
            </div>
            <div v-if="assignModal.error" class="pm-ticket-err">
              <i class="bi bi-exclamation-circle"></i> {{ assignModal.error }}
            </div>
            <div class="pm-ticket-acts">
              <button class="pnl-act" @click="closeAssignModal">취소</button>
              <button class="pnl-act gr" @click="submitAssignModal">
                <i class="bi bi-check2"></i> 배정
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ 이상 이벤트 resolve / dismiss 모달 ============ -->
      <div
        v-if="anomalyModal"
        class="cam-modal-bg"
        @click="closeAnomalyModal"
        role="dialog"
        aria-modal="true"
        :aria-label="anomalyModal.mode === 'resolve' ? '이상 이벤트 해결' : '이상 이벤트 오탐 종료'"
      >
        <div class="cam-modal pm-ticket-modal" @click.stop>
          <div class="cm-h">
            <div class="cm-title">
              <i :class="anomalyModal.mode === 'resolve' ? 'bi bi-check2-circle' : 'bi bi-x-circle'" aria-hidden="true"></i>
              <span>{{ anomalyModal.mode === 'resolve' ? '이상 이벤트 해결' : '이상 이벤트 오탐 종료' }}</span>
            </div>
            <button class="cm-x" @click="closeAnomalyModal" aria-label="닫기"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
          </div>
          <div class="pm-ticket-body">
            <div class="cm-row">
              <span>이벤트 ID</span><strong>{{ anomalyModal.anom.id }}</strong>
            </div>
            <div class="cm-row">
              <span>유형</span><strong>{{ anomalyTypeLabelKo(anomalyModal.anom.anomalyType) }}</strong>
            </div>
            <div class="cm-row">
              <span>장비</span><strong>{{ anomalyModal.anom.dev }}</strong>
            </div>

            <!-- resolve 모드: confirmedCause + resolutionNote -->
            <template v-if="anomalyModal.mode === 'resolve'">
              <div class="pm-ticket-note">
                <label>확정 원인 <span class="req">* 필수</span></label>
                <select v-model="anomalyModal.confirmedCause">
                  <option value="">선택…</option>
                  <option
                    v-for="c in anomalyModal.anom.suspectedCauses || []"
                    :key="c"
                    :value="c"
                  >{{ c }}</option>
                  <option value="기타">기타 (입력 필요)</option>
                </select>
              </div>
              <div class="pm-ticket-note">
                <label>조치 내용 <span class="req">* 필수</span></label>
                <textarea
                  v-model="anomalyModal.resolutionNote"
                  placeholder="수행한 조치를 구체적으로 기록해주세요"
                  rows="3"
                ></textarea>
              </div>
            </template>

            <!-- dismiss 모드: reason -->
            <template v-else>
              <div class="pm-ticket-note">
                <label>오탐 종료 사유 <span class="req">* 필수</span></label>
                <textarea
                  v-model="anomalyModal.reason"
                  placeholder="왜 오탐(정상 상황을 이상으로 판단)으로 판정했는지 기록"
                  rows="4"
                ></textarea>
              </div>
            </template>

            <div v-if="anomalyModal.error" class="pm-ticket-err">
              <i class="bi bi-exclamation-circle"></i> {{ anomalyModal.error }}
            </div>

            <div class="pm-ticket-acts">
              <button class="pnl-act" @click="closeAnomalyModal">취소</button>
              <button class="pnl-act gr" @click="submitAnomalyModal">
                <i class="bi bi-check2"></i> {{ anomalyModal.mode === 'resolve' ? '해결 확정' : '오탐 종료' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ 티켓 상태 전이 모달 (RESOLVED 시 메모 필수) ============ -->
      <div
        v-if="ticketModal"
        class="cam-modal-bg"
        @click="closeTicketModal"
        role="dialog"
        aria-modal="true"
        aria-label="티켓 상태 변경"
      >
        <div class="cam-modal pm-ticket-modal pm-ticket-modal-wide" @click.stop>
          <div class="cm-h">
            <div class="cm-title">
              <i class="bi bi-clipboard-check" aria-hidden="true"></i>
              <span>티켓 상태 변경</span>
              <span class="stat" :class="ticketModal.fault.tone">{{ ticketModal.fault.sev }}</span>
            </div>
            <button class="cm-x" @click="closeTicketModal" aria-label="닫기"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
          </div>
          <div class="pm-ticket-body">
            <div class="cm-row">
              <span>티켓 ID</span><strong>{{ ticketModal.fault.id }}</strong>
            </div>
            <div class="cm-row">
              <span>현재 상태</span><strong>{{ ticketStatusLabel(ticketModal.fault.ticketStatus) }}</strong>
            </div>
            <div class="cm-row">
              <span>전환 상태</span>
              <strong class="rd-txt">→ {{ ticketStatusLabel(ticketModal.toStatus) }}</strong>
            </div>

            <!-- 변경 이력 timeline -->
            <div class="pm-ticket-timeline">
              <div class="pm-tl-h">
                <i class="bi bi-clock-history"></i> 변경 이력
                <span class="pm-tl-cnt">{{ ticketHistory(ticketModal.fault).length }}건</span>
              </div>
              <div class="pm-tl-list">
                <div v-for="(h, i) in ticketHistory(ticketModal.fault)" :key="i" class="pm-tl-row">
                  <div class="pm-tl-dot" :class="h.kind"></div>
                  <div class="pm-tl-body">
                    <div class="pm-tl-line">
                      <strong>{{ h.action }}</strong>
                      <span class="pm-tl-from-to" v-if="h.from && h.to">
                        {{ ticketStatusLabel(h.from) }} → {{ ticketStatusLabel(h.to) }}
                      </span>
                    </div>
                    <div class="pm-tl-meta">
                      <span class="mono">{{ h.at }}</span>
                      <span v-if="h.by"> · {{ h.by }}</span>
                    </div>
                    <div v-if="h.note" class="pm-tl-note">{{ h.note }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="pm-ticket-note">
              <label>
                조치 메모
                <span v-if="ticketModal.toStatus === 'RESOLVED'" class="req">* 필수</span>
              </label>
              <textarea
                v-model="ticketModal.note"
                :placeholder="ticketModal.toStatus === 'RESOLVED' ? '수행한 조치 내용을 기록해주세요 (필수)' : '메모 (선택)'"
                rows="4"
              ></textarea>
              <div v-if="ticketModal.error" class="pm-ticket-err">
                <i class="bi bi-exclamation-circle"></i> {{ ticketModal.error }}
              </div>
            </div>
            <div class="pm-ticket-acts">
              <button class="pnl-act" @click="closeTicketModal">취소</button>
              <button class="pnl-act gr" @click="submitTicketTransition">
                <i class="bi bi-check2"></i> 적용
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ============ 설정 탭 ============ -->
      <section v-if="tab === 'settings'" class="card pnl pm-settings-scroll">
        <h3><i class="bi bi-gear"></i> 시설운영 환경 설정</h3>
        <div class="ops-set-grid">
          <div class="ops-set-blk">
            <h4>자동 새로고침 · 알림</h4>
            <div class="set-row"><label>자동 새로고침</label><input type="checkbox" v-model="autoRefresh" /></div>
            <div class="set-row"><label>갱신 주기 (초)</label><input type="number" v-model.number="setRefreshSec" min="10" max="600" /></div>
            <div class="set-row"><label>알림 사운드</label><input type="checkbox" v-model="setSound" /></div>
            <div class="set-row"><label>심각도 critical만 팝업</label><input type="checkbox" /></div>
          </div>
          <div class="ops-set-blk">
            <h4>장애 임계값</h4>
            <div class="set-row"><label>네트워크 지연 경보 (ms ≥)</label><input type="number" value="200" /></div>
            <div class="set-row"><label>CPU 사용률 경보 (% ≥)</label><input type="number" value="85" /></div>
            <div class="set-row"><label>디스크 경보 (% ≥)</label><input type="number" value="90" /></div>
            <div class="set-row"><label>RTSP 타임아웃 (분 ≥)</label><input type="number" value="5" /></div>
          </div>
          <div class="ops-set-blk">
            <h4>점검 · 로그</h4>
            <div class="set-row"><label>장비 점검 주기</label>
              <select><option>매일</option><option>주 1회</option><option>월 1회</option></select>
            </div>
            <div class="set-row"><label>장애 로그 보관</label>
              <select><option>30일</option><option>60일</option><option>90일</option><option>1년</option></select>
            </div>
            <div class="set-row"><label>정기 점검 알림</label><input type="checkbox" checked /></div>
          </div>
        </div>
        <div class="ops-set-foot">
          <button class="ops-set-save" @click="saveSettings"><i class="bi bi-check2"></i> 저장</button>
          <span v-if="setMsg" class="ops-set-msg">{{ setMsg }}</span>
        </div>

        <!-- ============ 탐지 정책 (예지보전) ============ -->
        <div class="pm-policy-block">
          <div class="pm-policy-head">
            <h4>
              <i class="bi bi-sliders"></i> 탐지 정책
              <span class="pm-policy-cnt">{{ pmPolicies.length }}개</span>
            </h4>
            <div class="pm-policy-meta">
              <span v-if="!isPmAdmin" class="pm-readonly-bdg" title="ADMIN만 수정 가능">
                <i class="bi bi-lock-fill"></i> READ ONLY · ADMIN 전용
              </span>
              <span v-else class="pm-admin-bdg">
                <i class="bi bi-pencil-fill"></i> 편집 가능
              </span>
            </div>
          </div>
          <p class="pm-policy-note">
            예지보전 탐지 시스템이 사용하는 정책 임계값입니다. 변경 시 적용된 정책이 활성 상태인 카메라 전체에 즉시 반영됩니다.
          </p>

          <div class="pm-policy-grid">
            <div
              v-for="p in pmPolicies"
              :key="p.policyCode"
              class="pm-policy-card"
              :class="{ disabled: !p.enabled }"
            >
              <div class="pm-policy-card-head">
                <div class="pm-policy-titles">
                  <span class="dm-bdg sm">{{ detectionMethodLabelKo(p.detectionMethod) }}</span>
                  <strong>{{ anomalyTypeLabelKo(p.anomalyType) }}</strong>
                </div>
                <label class="pm-policy-toggle" :class="{ disabled: !canEditPolicy }">
                  <input
                    type="checkbox"
                    v-model="p.enabled"
                    :disabled="!canEditPolicy"
                  />
                  <span>{{ p.enabled ? '활성' : '비활성' }}</span>
                </label>
              </div>

              <div class="pm-policy-code">{{ p.policyCode }}</div>

              <div class="pm-policy-fields">
                <div class="pm-field" :class="{ err: policyFieldErrors[p.policyCode]?.warningThreshold }">
                  <label>경고 임계</label>
                  <input
                    type="number"
                    v-model.number="p.warningThreshold"
                    :disabled="!canEditPolicy"
                    :step="p.step || 1"
                    :min="p.min"
                    :max="p.max"
                    @input="validatePolicy(p)"
                  />
                  <span class="pm-field-unit">{{ p.unit }}</span>
                </div>
                <div class="pm-field" :class="{ err: policyFieldErrors[p.policyCode]?.criticalThreshold }">
                  <label>위험 임계</label>
                  <input
                    type="number"
                    v-model.number="p.criticalThreshold"
                    :disabled="!canEditPolicy"
                    :step="p.step || 1"
                    :min="p.min"
                    :max="p.max"
                    @input="validatePolicy(p)"
                  />
                  <span class="pm-field-unit">{{ p.unit }}</span>
                </div>
                <div class="pm-field" :class="{ err: policyFieldErrors[p.policyCode]?.warningConsecutiveWindows }">
                  <label>경고 연속 윈도</label>
                  <input
                    type="number"
                    v-model.number="p.warningConsecutiveWindows"
                    :disabled="!canEditPolicy"
                    min="1" max="10"
                    @input="validatePolicy(p)"
                  />
                  <span class="pm-field-unit">회</span>
                </div>
                <div class="pm-field" :class="{ err: policyFieldErrors[p.policyCode]?.criticalConsecutiveWindows }">
                  <label>위험 연속 윈도</label>
                  <input
                    type="number"
                    v-model.number="p.criticalConsecutiveWindows"
                    :disabled="!canEditPolicy"
                    min="1" max="10"
                    @input="validatePolicy(p)"
                  />
                  <span class="pm-field-unit">회</span>
                </div>
              </div>

              <!-- 정책 방식별 추가 입력 (Rule / z-score / 추세) -->
              <div v-if="p.detectionMethod === 'ROBUST_Z_SCORE'" class="pm-policy-extra">
                <div class="pm-field">
                  <label>z-score 윈도(분)</label>
                  <input type="number" v-model.number="p.zScoreWindowMinutes" :disabled="!canEditPolicy" min="5" max="120" />
                  <span class="pm-field-unit">분</span>
                </div>
                <div class="pm-field">
                  <label>최소 표본 수</label>
                  <input type="number" v-model.number="p.minimumSampleCount" :disabled="!canEditPolicy" min="10" max="200" />
                  <span class="pm-field-unit">개</span>
                </div>
              </div>
              <div v-else-if="p.detectionMethod === 'TREND_PROJECTION'" class="pm-policy-extra">
                <div class="pm-field">
                  <label>예측 horizon</label>
                  <input type="number" v-model.number="p.predictionHorizonMinutes" :disabled="!canEditPolicy" min="5" max="60" />
                  <span class="pm-field-unit">분</span>
                </div>
                <div class="pm-field">
                  <label>EWMA α</label>
                  <input type="number" v-model.number="p.ewmaAlpha" :disabled="!canEditPolicy" min="0.1" max="0.9" step="0.05" />
                  <span class="pm-field-unit"></span>
                </div>
                <div class="pm-field">
                  <label>최소 신뢰도</label>
                  <input type="number" v-model.number="p.minimumTrendConfidence" :disabled="!canEditPolicy" min="0.3" max="0.95" step="0.05" />
                  <span class="pm-field-unit"></span>
                </div>
              </div>

              <!-- validation 에러 메시지 -->
              <div v-if="hasPolicyError(p)" class="pm-policy-err">
                <i class="bi bi-exclamation-circle"></i>
                <span>{{ policyErrorMessage(p) }}</span>
              </div>

              <div v-if="p.warningConsecutiveWindows !== p.criticalConsecutiveWindows" class="pm-policy-warn">
                <i class="bi bi-info-circle"></i>
                경고/위험 연속 윈도가 다릅니다 (자원 포화 등 비대칭 정책)
              </div>

              <div class="pm-policy-actions" v-if="canEditPolicy">
                <button
                  class="pnl-act sm"
                  :disabled="hasPolicyError(p)"
                  @click="openPolicyConfirm(p)"
                >
                  <i class="bi bi-check2"></i> 변경 저장
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ============ 정책 수정 확인 modal ============ -->
      <div
        v-if="policyConfirm"
        class="cam-modal-bg"
        @click="policyConfirm = null"
        role="dialog"
        aria-modal="true"
        aria-label="정책 변경 확인"
      >
        <div class="cam-modal pm-policy-modal" @click.stop>
          <div class="cm-h">
            <div class="cm-title">
              <i class="bi bi-shield-exclamation" aria-hidden="true"></i>
              <span>정책 변경 확인</span>
            </div>
            <button class="cm-x" @click="policyConfirm = null" aria-label="닫기"><i class="bi bi-x-lg" aria-hidden="true"></i></button>
          </div>
          <div class="pm-policy-confirm-body">
            <div class="cm-row">
              <span>정책 코드</span><strong>{{ policyConfirm.policyCode }}</strong>
            </div>
            <div class="cm-row">
              <span>탐지 대상</span><strong>{{ anomalyTypeLabelKo(policyConfirm.anomalyType) }}</strong>
            </div>
            <div class="cm-row">
              <span>경고 임계</span><strong>{{ policyConfirm.warningThreshold }}{{ policyConfirm.unit }}</strong>
            </div>
            <div class="cm-row">
              <span>위험 임계</span><strong>{{ policyConfirm.criticalThreshold }}{{ policyConfirm.unit }}</strong>
            </div>
            <div class="cm-row">
              <span>연속 윈도</span><strong>경고 {{ policyConfirm.warningConsecutiveWindows }}회 · 위험 {{ policyConfirm.criticalConsecutiveWindows }}회</strong>
            </div>
            <div class="cm-row">
              <span>활성 상태</span><strong>{{ policyConfirm.enabled ? '활성' : '비활성' }}</strong>
            </div>
            <p class="pm-policy-confirm-note">
              저장 시 활성 카메라 전체에 즉시 반영됩니다. 진행할까요?
            </p>
            <div class="pm-ticket-acts">
              <button class="pnl-act" @click="policyConfirm = null">취소</button>
              <button class="pnl-act gr" @click="submitPolicyUpdate">
                <i class="bi bi-check2"></i> 저장
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- ============ 카메라 상세 모달 ============ -->
    <div v-if="camModal" class="cam-modal-bg" @click="camModal = null">
      <div class="cam-modal" @click.stop>
        <div class="cm-h">
          <div class="cm-title">
            <i class="bi bi-camera-video-fill"></i>
            <span>{{ camModal.name }}</span>
            <span class="stat" :class="camModal.stTone">{{ camModal.st }}</span>
          </div>
          <button class="cm-x" @click="camModal = null" aria-label="닫기">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="cm-body">
          <!-- 좌: 영상 영역 (mock) -->
          <div class="cm-stream">
            <div class="cm-stream-inner">
              <i class="bi bi-camera-video"></i>
              <div class="cm-stream-lab">실시간 스트림</div>
              <div class="cm-stream-id">{{ camModal.id }}</div>
              <div class="cm-stream-time">2026-05-18 {{ camModal.ts }}</div>
            </div>
            <span class="cm-live" v-if="camModal.st === '정상'"><i></i> LIVE</span>
            <span class="cm-offline" v-else>● 신호 없음</span>
          </div>
          <!-- 우: 정보 + 컨트롤 -->
          <div class="cm-info">
            <div class="cm-row">
              <span>장비 ID</span><strong>{{ camModal.id }}</strong>
            </div>
            <div class="cm-row">
              <span>이름</span><strong>{{ camModal.name }}</strong>
            </div>
            <div class="cm-row">
              <span>위치</span><strong>{{ camModal.loc }}</strong>
            </div>
            <div class="cm-row">
              <span>상태</span
              ><strong :class="'cm-' + camModal.stTone">{{ camModal.st }}</strong>
            </div>
            <div class="cm-row">
              <span>지연(ms)</span><strong>{{ camModal.lat }}</strong>
            </div>
            <div class="cm-row">
              <span>최근 응답</span><strong>{{ camModal.ts }}</strong>
            </div>
            <div class="cm-actions">
              <button class="ab bl"><i class="bi bi-arrow-clockwise"></i> 재연결</button>
              <button class="ab gy">
                <i class="bi bi-arrows-fullscreen"></i> 풀스크린
              </button>
              <button class="ab gy"><i class="bi bi-download"></i> 스냅샷</button>
              <button class="ab rd" v-if="camModal.st === '정상'">
                <i class="bi bi-x-circle"></i> 일시 정지
              </button>
            </div>
          </div>
        </div>

        <!-- ====== 예지보전 헬스 패널 (하단) ====== -->
        <div class="cm-pm">
          <div class="cm-pm-head">
            <h4>
              <i class="bi bi-heart-pulse"></i> 헬스 분석
              <span v-if="camModal.healthStatus === 'BASELINE_LEARNING'" class="cm-pm-baseline-bdg">
                <i class="bi bi-cpu"></i> 기준선 학습 중
              </span>
              <span v-else-if="camModal.healthScore != null" class="cm-pm-score" :class="pmScoreTone(camModal.healthScore)">
                Health {{ camModal.healthScore.toFixed(1) }}
              </span>
              <span v-else class="cm-pm-score gy">Health —</span>
            </h4>
            <div v-if="camModal.predictedRisk > 0" class="cm-pm-pred">
              <i class="bi bi-graph-up-arrow"></i>
              <span><strong>{{ camModal.predictedType }}</strong> 추세 — {{ camModal.predictedAt }} 임계 도달 예상</span>
            </div>
          </div>

          <!-- BASELINE_LEARNING — 차트/지표 대신 진행률 표시 -->
          <div v-if="camModal.healthStatus === 'BASELINE_LEARNING'" class="cm-pm-baseline-card">
            <div class="cm-pm-baseline-l">신규 카메라의 기준선(baseline) 학습이 진행 중입니다.</div>
            <div class="cm-pm-baseline-bar">
              <div class="cm-pm-baseline-fill"
                :style="{ width: ((camModal.baselineSamples || 0) / (camModal.baselineRequired || 30) * 100) + '%' }"
              ></div>
            </div>
            <div class="cm-pm-baseline-stat">
              표본 수집: <strong>{{ camModal.baselineSamples || 0 }}</strong> / {{ camModal.baselineRequired || 30 }}
              <span class="cm-pm-baseline-sub">(완료 시 정상 모니터링으로 자동 전환)</span>
            </div>
          </div>

          <template v-else>

          <!-- Health Score 30분 추세 sparkline -->
          <div class="cm-pm-chart">
            <div class="cm-pm-chart-lab">
              <span>Health Score · 최근 30분</span>
              <span class="cm-pm-chart-leg">
                <i class="ln-base"></i> 기준선
                <i class="ln-thr"></i> 임계
                <i class="ln-pred"></i> 예측
              </span>
            </div>
            <svg
              viewBox="0 0 400 100"
              class="cm-pm-svg"
              preserveAspectRatio="none"
              role="img"
              :aria-label="`Health Score 30분 추세 차트. 현재 ${camModal && camModal.healthScore != null ? camModal.healthScore.toFixed(1) : '값 없음'}, 기준선 75, 위험 임계 50`"
            >
              <!-- 임계선 (50) -->
              <line x1="0" y1="50" x2="400" y2="50" stroke="#dc2626" stroke-width="1" stroke-dasharray="4 4" opacity="0.5"/>
              <!-- 기준선 (75) -->
              <line x1="0" y1="25" x2="400" y2="25" stroke="#9aa6b8" stroke-width="1" stroke-dasharray="2 4" opacity="0.6"/>
              <!-- 실측 (실선) -->
              <polyline
                :points="pmSparklinePoints(camModal)"
                fill="none"
                stroke="#2563eb"
                stroke-width="2"
              />
              <!-- 예측 (점선) -->
              <polyline
                v-if="camModal.predictedRisk > 0"
                :points="pmPredictedPoints(camModal)"
                fill="none"
                stroke="#ea580c"
                stroke-width="2"
                stroke-dasharray="5 3"
              />
              <!-- 현재 시점 마커 -->
              <line x1="280" y1="0" x2="280" y2="100" stroke="#0c1f40" stroke-width="0.5" opacity="0.3"/>
              <text x="282" y="12" font-size="9" fill="#4a5b78">지금</text>
            </svg>
          </div>

          <!-- 핵심 지표 4종 (현재 / 기준선 / 임계 + 미니 시계열) -->
          <div class="cm-pm-mtx">
            <div v-for="m in pmCameraMetrics(camModal)" :key="m.label" class="cm-pm-mtx-row" :class="m.tone">
              <div class="cm-pm-mtx-head">
                <div class="cm-pm-mtx-l">{{ m.label }}</div>
                <div class="cm-pm-mtx-vals">
                  <span class="cm-pm-mtx-cur" :class="m.tone">{{ m.cur }}{{ m.unit }}</span>
                  <span class="cm-pm-mtx-sep">vs</span>
                  <span class="cm-pm-mtx-base">{{ m.base }}{{ m.unit }} <em>기준</em></span>
                  <span class="cm-pm-mtx-thr">임계 {{ m.thr }}{{ m.unit }}</span>
                </div>
              </div>
              <!-- 미니 시계열 sparkline (30분, 외부 lib 0) -->
              <svg viewBox="0 0 200 36" class="cm-pm-mtx-svg" preserveAspectRatio="none" :aria-label="`${m.label} 30분 추세`">
                <!-- 임계선 -->
                <line x1="0" :y1="thresholdY(m)" x2="200" :y2="thresholdY(m)" stroke="#dc2626" stroke-width="0.6" stroke-dasharray="3 3" opacity="0.4"/>
                <!-- 기준선 -->
                <line x1="0" :y1="baselineY(m)" x2="200" :y2="baselineY(m)" stroke="#9aa6b8" stroke-width="0.6" stroke-dasharray="2 3" opacity="0.5"/>
                <!-- 실측 폴리라인 -->
                <polyline
                  :points="metricSparkline(m)"
                  fill="none"
                  :stroke="metricStrokeColor(m.tone)"
                  stroke-width="1.5"
                />
              </svg>
            </div>
          </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ============ 알람 상세 모달 (간결) ============ -->
    <div v-if="alarmModal" class="cam-modal-bg" @click="alarmModal = null">
      <div class="cam-modal alarm-modal" @click.stop>
        <div class="cm-h">
          <div class="cm-title">
            <i
              :class="
                alarmModal.kind === 'recovered'
                  ? 'bi bi-check-circle-fill'
                  : alarmModal.kind === 'info'
                  ? 'bi bi-info-circle-fill'
                  : 'bi bi-exclamation-triangle-fill'
              "
              :style="{
                color:
                  alarmModal.kind === 'recovered'
                    ? '#059669'
                    : alarmModal.kind === 'info'
                    ? '#2563eb'
                    : '#dc2626',
              }"
            ></i>
            <span>알람 상세</span>
            <span
              class="stat"
              :class="
                alarmModal.sev.toLowerCase() === 'crit'
                  ? 'no'
                  : alarmModal.sev.toLowerCase() === 'high' ||
                    alarmModal.sev.toLowerCase() === 'med'
                  ? 'wn'
                  : 'ok'
              "
              >{{ alarmModal.sev }}</span
            >
          </div>
          <button class="cm-x" @click="alarmModal = null" aria-label="닫기">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="am-body">
          <div class="am-msg">{{ alarmModal.msg }}</div>
          <div class="cm-row">
            <span>발생 시각</span><strong>{{ alarmModal.time }}</strong>
          </div>
          <div class="cm-row">
            <span>경과 시간 (SLA)</span>
            <strong class="am-sla" :class="slaClass(alarmModal)">
              <i class="bi bi-stopwatch"></i> {{ slaText(alarmModal) }}
            </strong>
          </div>
          <div class="cm-row">
            <span>장비</span><strong>{{ alarmModal.dev }}</strong>
          </div>
          <div class="cm-row">
            <span>심각도</span><strong>{{ alarmModal.sev }}</strong>
          </div>
          <div class="cm-row">
            <span>담당자</span><strong>{{ alarmModal.who }}</strong>
          </div>
          <div class="cm-row">
            <span>유형</span
            ><strong>{{
              alarmModal.kind === "recovered"
                ? "복구"
                : alarmModal.kind === "info"
                ? "정보"
                : "이벤트"
            }}</strong>
          </div>
          <div class="cm-actions">
            <button class="ab bl">
              <i class="bi bi-arrow-right-circle"></i> 처리 시작
            </button>
            <button class="ab gy"><i class="bi bi-share"></i> 담당자 변경</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ 네트워크 장비 상세 모달 ═══ -->
    <div v-if="netModal" class="cam-modal-bg" @click="netModal = null">
      <div class="cam-modal alarm-modal" @click.stop>
        <div class="cm-h">
          <div class="cm-title">
            <i
              class="bi bi-hdd-network-fill"
              :style="{
                color:
                  netModal.tone === 'gr'
                    ? '#047857'
                    : netModal.tone === 'yl'
                    ? '#b45309'
                    : netModal.tone === 'or'
                    ? '#c2410c'
                    : '#dc2626',
              }"
            ></i>
            <span>네트워크 장비 상세</span>
            <span class="stat" :class="netStatTone(netModal.tone)">{{
              netLabel(netModal.tone)
            }}</span>
          </div>
          <button class="cm-x" @click="netModal = null" aria-label="닫기">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="am-body">
          <div class="am-msg">{{ netModal.id }}</div>
          <div class="cm-row">
            <span>장비 ID</span><strong>{{ netModal.id }}</strong>
          </div>
          <div class="cm-row">
            <span>현재 RTT</span><strong>{{ netModal.ms }} ms</strong>
          </div>
          <div class="cm-row">
            <span>상태</span>
            <strong
              >{{ netLabel(netModal.tone)
              }}{{ netModal.ms > 200 ? " (임계 200ms 초과)" : "" }}</strong
            >
          </div>
          <div class="cm-row">
            <span>패킷 손실</span>
            <strong>{{
              netModal.tone === "rd" ? "100%" : netModal.tone === "or" ? "12%" : "0%"
            }}</strong>
          </div>
          <div class="cm-row">
            <span>업타임</span>
            <strong>{{
              netModal.tone === "rd"
                ? "0% (오프라인)"
                : netModal.tone === "or"
                ? "98.4%"
                : "99.97%"
            }}</strong>
          </div>
          <div class="cm-row">
            <span>마지막 응답</span>
            <strong>{{
              netModal.tone === "rd"
                ? "12분 전"
                : netModal.tone === "or"
                ? "8초 전"
                : "< 1초 전"
            }}</strong>
          </div>
          <div class="cm-row">
            <span>구역</span>
            <strong>{{
              netModal.id.startsWith("CAM-K")
                ? "강변북로"
                : netModal.id.startsWith("CAM-O")
                ? "올림픽대로"
                : netModal.id.startsWith("CAM-J")
                ? "내부순환"
                : netModal.id.startsWith("CAM-D")
                ? "동부간선"
                : netModal.id.startsWith("CAM-G")
                ? "강남대로"
                : netModal.id.startsWith("CAM-M")
                ? "마포대교"
                : netModal.id.startsWith("CAM-N")
                ? "내부순환"
                : netModal.id.startsWith("EDGE")
                ? "Edge 라우터"
                : netModal.id.startsWith("CORE")
                ? "Core 백본"
                : netModal.id.startsWith("ocr")
                ? "OCR 서버 팜"
                : netModal.id.startsWith("NSN")
                ? "한남TG 광케이블"
                : "—"
            }}</strong>
          </div>
          <div class="cm-actions">
            <button class="ab bl"><i class="bi bi-arrow-clockwise"></i> 재연결</button>
            <button class="ab gy"><i class="bi bi-graph-up"></i> 24h 그래프</button>
            <button
              class="ab gy"
              @click="
                tab = 'net';
                netModal = null;
              "
            >
              <i class="bi bi-arrow-right-circle"></i> 전체 보기
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from "vue";
import echarts from "@/composables/echartsSetup";
import { RouterLink, useRoute, useRouter } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import SideWeather from "@/components/dashboard/SideWeather.vue";
import { INITIAL_DISTRICTS_WEATHER, DISTRICT_LIST } from "@/data/weather";
import GuideOverlay from "@/components/GuideOverlay.vue";
import guideSteps from "@/data/guides/ops.js";
import { usePredictivePerm } from "@/composables/usePredictivePerm";

// 예지보전 권한 헬퍼 (요구사항 정의서 2-4/7-2 + DB 협의 2026-06-12 반영)
const {
  isAdmin: isPmAdmin,
  isMaintainer,
  canCreateTicket,
  canCloseTicket,
  canAssignTicket,
  canResolveAnomaly,
  canChangeTicketStatus,
  canTransitionTicket,
} = usePredictivePerm();

const guideOpen = ref(false);

// ─── URL query 동기화 (tab + 필터 상태) ───
// /admin/ops?tab=fault&kind=anomaly&priority=P1&overdue=1 식으로 보존
const route = useRoute();
const router = useRouter();

const ALLOWED_TABS = ["status", "cams", "srv", "net", "fault", "settings"];
const initialTab = ALLOWED_TABS.includes(route.query.tab) ? route.query.tab : "status";
const tab = ref(initialTab);

// 라우터 query를 안전하게 갱신 (history 누적 X)
let suppressSync = false;
function syncToQuery(partial) {
  if (suppressSync) return;
  const next = { ...route.query, ...partial };
  // 빈 값은 query에서 제거
  Object.keys(next).forEach((k) => {
    if (next[k] === "" || next[k] === null || next[k] === undefined || next[k] === false) {
      delete next[k];
    }
  });
  router.replace({ path: route.path, query: next });
}

// tab 변경 → URL (flush:sync로 suppressSync flag와 동기화)
watch(tab, (v) => syncToQuery({ tab: v === "status" ? "" : v }), { flush: "sync" });

// URL → state (back/forward 버튼 대응)
watch(() => route.query, (q) => {
  suppressSync = true
  try {
    const nextTab = ALLOWED_TABS.includes(q.tab) ? q.tab : "status"
    if (tab.value !== nextTab) tab.value = nextTab
    // fault 필터
    if (faultFilter.value.kind !== (q.kind || "")) faultFilter.value.kind = pick(ALLOWED_KIND, q.kind)
    if (faultFilter.value.priority !== (q.priority || "")) faultFilter.value.priority = pick(ALLOWED_PRI, q.priority)
    if (faultFilter.value.detectionMethod !== (q.dm || "")) faultFilter.value.detectionMethod = pick(ALLOWED_DM, q.dm)
    if (faultFilter.value.status !== (q.ts || "")) faultFilter.value.status = pick(ALLOWED_TS, q.ts)
    const overdueFlag = q.overdue === "1"
    if (faultFilter.value.slaOverdueOnly !== overdueFlag) faultFilter.value.slaOverdueOnly = overdueFlag
    // cams 필터
    const qStr = typeof q.q === "string" ? q.q : ""
    if (camQuery.value !== qStr) camQuery.value = qStr
    const stStr = ALLOWED_CAM_ST.includes(q.st) ? q.st : "all"
    if (camSt.value !== stStr) camSt.value = stStr
  } finally {
    suppressSync = false
  }
})
async function onGuideStep(step) {
  if (step?.tab && step.tab !== tab.value) {
    tab.value = step.tab;
  }
}
const autoRefresh = ref(true);

// 헤더 날씨 칩 + 팝오버
const showWeather = ref(false);
const weatherSummary = computed(() => {
  const d = INITIAL_DISTRICTS_WEATHER[DISTRICT_LIST[0]];
  return { temp: d.temp, condition: d.condition, icon: d.icon, color: d.color };
});
const failMemo = ref("PoE 차단기 OFF/ON 1회 시도 — 미복구. 17:00 김기사 현장 출동 예정.");

// 헤더 「시설운영팀」 클릭 → 메인(status) 탭으로 + 스크롤 최상단
function goHome() {
  tab.value = "status";
  if (typeof window !== "undefined") window.scrollTo({ top: 0, behavior: "smooth" });
}

// 카메라 상세 모달 + 카메라 탭 필터
const camModal = ref(null);
function openCam(c) {
  camModal.value = c;
}

// 알람 상세 모달
const alarmModal = ref(null);
function openAlarm(a) {
  alarmModal.value = a;
}
// cams 탭 필터 — URL 동기화
const ALLOWED_CAM_ST = ["all", "정상", "지연", "장애"]
const camQuery = ref(typeof route.query.q === "string" ? route.query.q : "");
const camSt = ref(ALLOWED_CAM_ST.includes(route.query.st) ? route.query.st : "all");
watch([camQuery, camSt], ([q, st]) => {
  syncToQuery({
    q: q || "",
    st: st === "all" ? "" : st,
  })
}, { flush: "sync" })
// 카메라 정렬 — Health Score 오름차순(위험 우선) 기본. 운영자가 즉시 우선순위 식별
// 백엔드 계약 §3-2 sort=healthScore,asc 와 동일
const camSort = ref("healthScore,asc");
const ALLOWED_CAM_SORT = ["healthScore,asc", "healthScore,desc", "cameraName,asc", "latestSampledAt,desc"];
const camSortLabel = computed(() => ({
  "healthScore,asc":  "위험 우선",
  "healthScore,desc": "정상 우선",
  "cameraName,asc":   "이름순",
  "latestSampledAt,desc": "최근 응답순",
}[camSort.value] || ""));

function compareCams(a, b, key) {
  if (key === "healthScore,asc") {
    // BASELINE_LEARNING (healthScore null) / OFFLINE(0) 정렬 안정화
    const av = a.healthScore == null ? 100 : a.healthScore;  // 학습 중은 끝으로
    const bv = b.healthScore == null ? 100 : b.healthScore;
    return av - bv;  // 낮을수록 위험 → 위로
  }
  if (key === "healthScore,desc") {
    const av = a.healthScore == null ? -1 : a.healthScore;
    const bv = b.healthScore == null ? -1 : b.healthScore;
    return bv - av;
  }
  if (key === "cameraName,asc") return a.name.localeCompare(b.name);
  if (key === "latestSampledAt,desc") return (b.ts || "").localeCompare(a.ts || "");
  return 0;
}

const filteredCams = computed(() => {
  const q = camQuery.value.trim().toLowerCase();
  const filtered = cams.filter((c) => {
    if (camSt.value !== "all" && c.st !== camSt.value) return false;
    if (!q) return true;
    return (
      c.name.toLowerCase().includes(q) ||
      c.id.toLowerCase().includes(q) ||
      c.loc.toLowerCase().includes(q)
    );
  });
  // 정렬 적용 (기본: 위험 카메라 우선)
  return [...filtered].sort((a, b) => compareCams(a, b, camSort.value));
});
if (typeof window !== "undefined") {
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      camModal.value = null;
      alarmModal.value = null;
    }
  });
}

const tlFilter = ref("ALL");
const netZone = ref("all");
const netRange = ref("1h");
const sideOpen = ref(true);
const srvRange = ref("1h");
const srvServices = Object.freeze([
  {
    name: "nginx",
    host: "ocr-srv-01",
    port: 443,
    pid: 1234,
    ver: "1.24.0",
    rt: "12ms",
    uptime: "37일 2h",
    lastRestart: "2025-04-12 03:00",
    stat: "RUNNING",
    statTone: "ok",
    tone: "gr",
  },
  {
    name: "ocr-engine",
    host: "ocr-srv-01",
    port: 8080,
    pid: 1842,
    ver: "v3.2.1",
    rt: "48ms",
    uptime: "37일 2h",
    lastRestart: "2025-04-12 03:05",
    stat: "RUNNING",
    statTone: "ok",
    tone: "gr",
  },
  {
    name: "redis",
    host: "ocr-srv-01",
    port: 6379,
    pid: 1956,
    ver: "7.2.4",
    rt: "2ms",
    uptime: "37일 2h",
    lastRestart: "2025-04-12 03:00",
    stat: "RUNNING",
    statTone: "ok",
    tone: "gr",
  },
]);
const netModal = ref(null);

// ─── ECharts (서버 게이지 + 네트워크 막대) ───
const netChartEl = ref(null);
let netChart = null;
const srvCharts = new Map();

function srvGaugeOption(b) {
  const val = parseFloat(String(b.v).replace(/[^\d.]/g, "")) || b.bar || 0;
  const tone = b.tone || "gr";
  const gradMap = {
    gr: ["#6ee7b7", "#047857"],
    yl: ["#fde68a", "#b45309"],
    rd: ["#fca5a5", "#b91c1c"],
  };
  const [c1, c2] = gradMap[tone] || gradMap.gr;
  const isSlash = String(b.v).includes("/");
  return {
    series: [
      {
        type: "gauge",
        startAngle: 90,
        endAngle: -270,
        radius: "92%",
        pointer: { show: false },
        progress: {
          show: true,
          overlap: false,
          roundCap: true,
          clip: false,
          width: 12,
          itemStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 1,
              y2: 1,
              colorStops: [
                { offset: 0, color: c1 },
                { offset: 1, color: c2 },
              ],
            },
            shadowColor: c2 + "66",
            shadowBlur: 12,
            shadowOffsetY: 0,
          },
        },
        axisLine: {
          lineStyle: {
            width: 12,
            color: [[1, "#eff3f8"]],
            shadowColor: "rgba(12,31,64,0.08)",
            shadowBlur: 4,
            shadowOffsetY: 2,
          },
        },
        splitLine: { show: false },
        axisTick: { show: false },
        axisLabel: { show: false },
        anchor: { show: false },
        data: [{ value: val }],
        title: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, "0%"],
          fontSize: 26,
          fontWeight: 800,
          fontFamily: "IBM Plex Mono, monospace",
          color: "#0c1f40",
          formatter: () => (isSlash ? b.v : val.toFixed(val % 1 ? 1 : 0) + "%"),
        },
        animationDuration: 1400,
        animationEasing: "cubicOut",
      },
    ],
  };
}

function setSrvChart(el, b) {
  if (!el) return;
  // 컨테이너 사이즈가 0이면 다음 프레임에 재시도
  const tryInit = () => {
    const w = el.clientWidth;
    const h = el.clientHeight;
    if (w === 0 || h === 0) {
      requestAnimationFrame(tryInit);
      return;
    }
    if (!srvCharts.has(el)) {
      const ch = echarts.init(el, null, { renderer: "canvas" });
      ch.setOption(srvGaugeOption(b));
      srvCharts.set(el, ch);
      // 컨테이너 사이즈 변경 감지
      const ro = new ResizeObserver(() => {
        ch.resize();
      });
      ro.observe(el);
    } else {
      srvCharts.get(el).setOption(srvGaugeOption(b));
      srvCharts.get(el).resize();
    }
  };
  nextTick(tryInit);
}

function initNetChart() {
  if (!netChartEl.value) return;
  const el = netChartEl.value;
  if (el.clientWidth === 0 || el.clientHeight === 0) {
    requestAnimationFrame(initNetChart);
    return;
  }
  if (!netChart) {
    netChart = echarts.init(el, null, { renderer: "canvas" });
    const ro = new ResizeObserver(() => netChart && netChart.resize());
    ro.observe(el);
    // 막대 클릭 → 구역 상세 모달
    netChart.on("click", "series", (params) => {
      const z = netZones.find((n) => n.name === params.name);
      if (z) netModal.value = { id: z.name, ms: z.ms, tone: z.tone };
    });
    // 막대 위 hover 시 cursor pointer
    netChart.getZr().on("mousemove", (ev) => {
      const target = ev.target;
      el.style.cursor = target ? "pointer" : "default";
    });
  }
  const zones = netZones || [];
  const toneGrad = {
    gr: ["#34d399", "#047857"],
    yl: ["#fbbf24", "#b45309"],
    or: ["#fb923c", "#c2410c"],
    rd: ["#f87171", "#b91c1c"],
  };
  netChart.setOption({
    grid: { left: 44, right: 14, top: 32, bottom: 44 },
    tooltip: {
      trigger: "axis",
      backgroundColor: "rgba(12,31,64,0.95)",
      borderWidth: 0,
      padding: [8, 12],
      textStyle: {
        color: "#ffffff",
        fontSize: 13,
        fontFamily: "Inter, Pretendard, sans-serif",
      },
      axisPointer: {
        type: "shadow",
        shadowStyle: { color: "rgba(37,99,235,0.08)" },
      },
      formatter: (p) => {
        const d = p[0];
        const t = (zones.find((z) => z.name === d.name) || {}).tone || "gr";
        const label =
          t === "rd" ? "장애" : t === "or" ? "경고" : t === "yl" ? "지연" : "정상";
        return `<div style="font-weight:800;font-size:13px;margin-bottom:4px">${d.name}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:800">${d.value}<span style="font-size:11px;opacity:.7;margin-left:2px">ms</span></div>
                <div style="font-size:11px;opacity:.85;margin-top:2px">상태 · ${label}</div>`;
      },
    },
    xAxis: {
      type: "category",
      data: zones.map((z) => z.name),
      axisLine: { lineStyle: { color: "#c9d4e3" } },
      axisLabel: {
        color: "#0c1f40",
        fontSize: 13.5,
        fontWeight: 700,
        fontFamily: "Inter, Pretendard, sans-serif",
        interval: 0,
        margin: 10,
      },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value",
      max: 300,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: "#6b7a92",
        fontSize: 12.5,
        fontFamily: "IBM Plex Mono, monospace",
        formatter: "{value}",
      },
      splitLine: { lineStyle: { color: "#e7edf6", type: "dashed" } },
    },
    series: [
      {
        type: "bar",
        z: 1,
        data: zones.map((z) => ({
          value: z.ms,
          itemStyle: {
            color: {
              type: "linear",
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: (toneGrad[z.tone] || toneGrad.gr)[0] },
                { offset: 1, color: (toneGrad[z.tone] || toneGrad.gr)[1] },
              ],
            },
            borderRadius: [6, 6, 0, 0],
            shadowColor: (toneGrad[z.tone] || toneGrad.gr)[1] + "55",
            shadowBlur: 10,
            shadowOffsetY: 2,
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 18,
              shadowOffsetY: 0,
            },
          },
        })),
        barWidth: "60%",
        markLine: {
          silent: true,
          symbol: "none",
          lineStyle: { type: "dashed", color: "#b91c1c", width: 1.4, opacity: 0.75 },
          data: [
            {
              yAxis: 200,
              label: {
                show: true,
                color: "#b91c1c",
                fontSize: 11.5,
                fontWeight: 700,
                formatter: "임계 200ms",
                position: "insideStartTop",
              },
            },
          ],
        },
        label: {
          show: true,
          position: "top",
          color: "#0c1f40",
          fontSize: 13.5,
          fontWeight: 800,
          fontFamily: "IBM Plex Mono, monospace",
          formatter: "{c}",
        },
        animationDuration: 1200,
        animationEasing: "cubicOut",
        animationDelay: (i) => i * 80,
      },
    ],
  });
}

function resizeAllCharts() {
  if (netChart) netChart.resize();
  srvCharts.forEach((c) => c.resize());
}

onMounted(() => {
  nextTick(() => {
    initNetChart();
    window.addEventListener("resize", resizeAllCharts);
  });
});

// tab이 status로 돌아올 때 차트 재초기화 (v-if로 DOM이 새로 마운트되므로)
watch(tab, (v) => {
  if (v === "status") {
    if (netChart) { netChart.dispose(); netChart = null; }
    srvCharts.forEach((c) => c.dispose());
    srvCharts.clear();
    nextTick(() => initNetChart());
  }
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeAllCharts);
  if (netChart) {
    netChart.dispose();
    netChart = null;
  }
  srvCharts.forEach((c) => c.dispose());
  srvCharts.clear();
});
watch(
  () => netModal.value,
  () => nextTick(resizeAllCharts)
);

function netLabel(t) {
  return t === "gr" ? "정상" : t === "yl" ? "지연" : t === "or" ? "경고" : "장애";
}
function netStatTone(t) {
  return t === "gr" ? "ok" : t === "yl" || t === "or" ? "wn" : "no";
}
// 알람 카테고리별 분포 (24h)
const alarmCats = Object.freeze([
  { name: "네트워크", crit: 1, high: 2, med: 1, info: 3 },
  { name: "카메라", crit: 1, high: 2, med: 2, info: 4 },
  { name: "서버", crit: 0, high: 1, med: 3, info: 2 },
]);

// 장애 유형 분포 (최근 7일)
const faultTypes = Object.freeze([
  { name: "네트워크 단선", count: 6, ongoing: 1, mttr: 24 },
  { name: "카메라 오프라인", count: 5, ongoing: 0, mttr: 12 },
  { name: "서버 리소스", count: 4, ongoing: 0, mttr: 8 },
]);

// 카메라 위치별 분포 (cams 탭용)
const camZones = Object.freeze([
  { name: "강변북로", ok: 5, warn: 0, bad: 0 },
  { name: "올림픽대로", ok: 4, warn: 0, bad: 0 },
  { name: "내부순환", ok: 3, warn: 1, bad: 0 },
]);

// 구역별 평균 지연 (대시보드 요약 막대용)
const netZones = Object.freeze([
  { name: "강변북로", ms: 86, tone: "gr" },
  { name: "올림픽", ms: 92, tone: "gr" },
  { name: "내부순환", ms: 124, tone: "yl" },
]);

// 25개 노드 헬스 그리드 (대시보드 요약용)
const netPaths = Object.freeze([
  {
    from: "GBN-S-0032",
    to: "ocr-srv-01",
    lat: 28.6,
    avg: 27.8,
    loss: 0.0,
    st: "정상",
    tone: "ok",
  },
  {
    from: "OLP-W-0041",
    to: "ocr-srv-01",
    lat: 22.1,
    avg: 24.5,
    loss: 0.0,
    st: "정상",
    tone: "ok",
  },
  {
    from: "NSN-N-0023",
    to: "ocr-srv-01",
    lat: "—",
    avg: 18.2,
    loss: 100,
    st: "장애",
    tone: "no",
  },
]);

const alarmSev = ref("all");
const alarmsExt = Object.freeze([
  {
    id: 1,
    time: "14:24:17",
    sev: "CRIT",
    tone: "no",
    cat: "네트워크",
    dev: "NSN-N-0023",
    msg: "RTSP 스트림 응답 없음 (timeout 30s)",
    who: "김기사",
    handled: false,
  },
  {
    id: 2,
    time: "14:18:05",
    sev: "HIGH",
    tone: "wn",
    cat: "네트워크",
    dev: "GBG-S-0077",
    msg: "네트워크 지연 286ms 임계 초과",
    who: "자동",
    handled: false,
  },
  {
    id: 3,
    time: "14:11:42",
    sev: "MED",
    tone: "wn",
    cat: "서버",
    dev: "search-srv",
    msg: "디스크 사용량 78% 경고",
    who: "—",
    handled: false,
  },
]);
const filteredAlarmExt = computed(() =>
  alarmSev.value === "all" ? alarmsExt : alarmsExt.filter((a) => a.sev === alarmSev.value)
);

// 장애·이상 통합 목록 — 기존 운영 필드 + 예지보전 필드(priority/방식/SLA/원인 등)
// kind: 'fault' (전통적 장애) | 'anomaly' (예지보전 탐지)
const faults = Object.freeze([
  {
    id: "FLT-2026-00342",
    time: "10:24:17",
    dev: "NSN-N-0023",
    symp: "RTSP 스트림 응답 없음",
    sev: "CRIT",
    tone: "no",
    who: "김기사",
    elapsed: "00:08:15",
    st: "진행 중",
    stTone: "no",
    ticketStatus: "IN_PROGRESS",
    kind: "fault",
    priority: "P1",
    detectionMethod: "RULE",
    anomalyType: "CAMERA_OFFLINE",
    slaDeadline: "14:39",
    slaOverdue: false,
    slaRemainingMin: 5,
  },
  {
    id: "ANM-2026-00118",
    time: "10:32:00",
    dev: "OLP-W-0041",
    symp: "FPS 11.2 → 10분 후 임계 도달 예상",
    sev: "WARN",
    tone: "yl",
    who: "—",
    elapsed: "00:00:32",
    st: "탐지",
    stTone: "wn",
    ticketStatus: "OPEN",
    kind: "anomaly",
    priority: "P2",
    detectionMethod: "TREND_PROJECTION",
    anomalyType: "FPS_DEGRADATION",
    projectedAt: "10:44",
    slaDeadline: "10:42",
    slaOverdue: false,
    slaRemainingMin: 10,
    evidence: [
      { metric: "FPS",        observed: 11.2,  baseline: 24.1, threshold: 10.0, unit: "fps" },
      { metric: "CPU 사용률", observed: 91.3,  baseline: 45.0, threshold: 85.0, unit: "%"   },
      { metric: "지연 P95",   observed: 1600,  baseline: 540,  threshold: 2000, unit: "ms"  },
    ],
    suspectedCauses: ["분석 프로세스 과부하 (CPU 91.3%)", "RTSP 입력 일시 jitter"],
    confirmedCause: null,
    // 운영 detector 정보 (계약 §3-6)
    detector: {
      name: "camera-trend-projection",
      version: "1.0.0",
      policyCode: "CAMERA_TREND_PROJECTION_V1",
    },
    // 통계 지표 (계약 §3-6 trend)
    trend: {
      slope: -0.73,            // 분당 -0.73 fps (하향)
      confidence: 0.81,         // 추세 신뢰도
      robustZScore: -4.2,       // robust z-score (관측-기준선) / mad
      predictionHorizonMinutes: 10,
    },
    // 교통 맥락 교차검증 — 인접 카메라는 정상이면 이 카메라 자체 문제일 가능성 ↑
    trafficContext: {
      currentVehicleCount: 8,
      currentAvgSpeed: 42.3,
      adjacentCameras: [
        { id: "OLP-W-0040", name: "잠실대교 남단", vehicleCount: 43, avgSpeed: 41.8, qualityStatus: "COMPLETE" },
        { id: "OLP-W-0042", name: "올림픽대로 잠실", vehicleCount: 39, avgSpeed: 39.5, qualityStatus: "COMPLETE" },
      ],
      crossValidation: "ABNORMAL_LOCAL",  // 인접 정상 / 본 카메라만 비정상
      crossValidationLabel: "본 카메라 단독 이상 — 인접 카메라는 정상 트래픽 유지",
    },
    shadowModel: {
      name: "camera-lstm-autoencoder",
      version: "1.0.0",
      score: 0.91,
      warningThreshold: 0.72,
      criticalThreshold: 0.82,
      predictedSeverity: "CRITICAL",
      topFeatures: [
        { name: "fpsAvg",      value: 0.38 },
        { name: "cpuUsagePct", value: 0.24 },
        { name: "latencyP95",  value: 0.17 },
      ],
    },
  },
  {
    id: "FLT-2026-00341",
    time: "09:42:05",
    dev: "GBG-S-0077",
    symp: "지연 286ms 초과 지속",
    sev: "HIGH",
    tone: "wn",
    who: "자동",
    elapsed: "00:50:27",
    st: "처리 중",
    stTone: "wn",
    ticketStatus: "IN_PROGRESS",
    kind: "fault",
    priority: "P2",
    detectionMethod: "RULE",
    anomalyType: "LATENCY_DEGRADATION",
    slaDeadline: "10:12",
    slaOverdue: false,
    slaRemainingMin: 30,
  },
  {
    id: "ANM-2026-00117",
    time: "09:21:48",
    dev: "GBN-W-0019",
    symp: "OCR 실패율 추세 상승 (5.2% → 18.5%)",
    sev: "WARN",
    tone: "yl",
    who: "박엔지",
    elapsed: "01:10:30",
    st: "확인",
    stTone: "wn",
    ticketStatus: "ASSIGNED",
    kind: "anomaly",
    priority: "P3",
    detectionMethod: "TREND_PROJECTION",
    anomalyType: "OCR_QUALITY_DEGRADATION",
    projectedAt: "10:51",
    slaDeadline: "11:21",
    slaOverdue: false,
    slaRemainingMin: 49,
  },
  {
    id: "FLT-2026-00340",
    time: "08:11:33",
    dev: "search-srv",
    symp: "디스크 78% 초과",
    sev: "MED",
    tone: "wn",
    who: "이대리",
    elapsed: "02:14:00",
    st: "처리 중",
    stTone: "wn",
    ticketStatus: "IN_PROGRESS",
    kind: "fault",
    priority: "P3",
    detectionMethod: "RULE",
    anomalyType: "RESOURCE_SATURATION",
    slaDeadline: "09:11",
    slaOverdue: true,
    slaRemainingMin: -180,
  },
]);

// 집계 (헤더/KPI용)
const pmAnomalyCount   = computed(() => faults.filter((f) => f.kind === "anomaly").length)
const pmPredictedCount2 = computed(() => faults.filter((f) => f.detectionMethod === "TREND_PROJECTION").length)
const pmSlaOverdueCount = computed(() => faults.filter((f) => f.slaOverdue).length)

// MTTA (Mean Time To Acknowledge) — 데모 더미값
const pmMtta = ref(7.4)
const pmMttr = ref(18)

// ─── fault 필터 (URL query 동기화) ───
const ALLOWED_KIND = ["", "fault", "anomaly"]
const ALLOWED_PRI = ["", "P1", "P2", "P3"]
const ALLOWED_DM = ["", "RULE", "TREND_PROJECTION", "ROBUST_Z_SCORE", "CROSS_VALIDATION", "LSTM_AUTOENCODER"]
const ALLOWED_TS = ["", "OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
function pick(arr, v, def = "") { return arr.includes(v) ? v : def }

const faultFilter = ref({
  kind:           pick(ALLOWED_KIND, route.query.kind),
  priority:       pick(ALLOWED_PRI,  route.query.priority),
  detectionMethod: pick(ALLOWED_DM,  route.query.dm),
  status:         pick(ALLOWED_TS,   route.query.ts),
  slaOverdueOnly: route.query.overdue === "1",
})

function resetFaultFilter() {
  faultFilter.value = { kind: "", priority: "", detectionMethod: "", status: "", slaOverdueOnly: false }
}

// fault 필터 변경 → URL
watch(faultFilter, (v) => {
  syncToQuery({
    kind:     v.kind,
    priority: v.priority,
    dm:       v.detectionMethod,
    ts:       v.status,
    overdue:  v.slaOverdueOnly ? "1" : "",
  })
}, { deep: true, flush: "sync" })
const filteredFaults = computed(() => {
  const f = faultFilter.value
  return faults.filter((it) => {
    if (f.kind && it.kind !== f.kind) return false
    if (f.priority && it.priority !== f.priority) return false
    if (f.detectionMethod && it.detectionMethod !== f.detectionMethod) return false
    if (f.status && it.ticketStatus !== f.status) return false
    if (f.slaOverdueOnly && !it.slaOverdue) return false
    return true
  })
})

// 우선순위 색상
const pmPriorityTone = (p) => p === "P1" ? "rd" : p === "P2" ? "yl" : "gy"
const pmPriorityLabel = (p) => p || "—"

// 가장 우선 처리해야 할 활성 이상 (TREND_PROJECTION 우선, 그 다음 CRITICAL)
const activeAnomaly = computed(() => {
  const list = faults.filter((f) => f.kind === "anomaly")
  return list.find((f) => f.detectionMethod === "TREND_PROJECTION") || list[0] || null
})

// 이상 이벤트에 연결된 정비 티켓 (현재 mock: 같은 장비의 fault kind 항목)
function linkedTicket(anom) {
  if (!anom) return null
  return faults.find((f) => f.kind === "fault" && f.dev === anom.dev) || null
}

// 교통 맥락 헬퍼
function trafficJdLabel(code) {
  const m = {
    ABNORMAL_LOCAL:  "본 카메라 단독 이상",
    ABNORMAL_GLOBAL: "광역 교통 영향",
    NORMAL_TRAFFIC:  "정상 교통",
    INSUFFICIENT:    "데이터 부족",
  }
  return m[code] || code || "—"
}
function trafficJdTone(code) {
  if (code === "ABNORMAL_LOCAL")  return "rd"
  if (code === "ABNORMAL_GLOBAL") return "yl"
  if (code === "NORMAL_TRAFFIC")  return "gr"
  return "gy"
}
function adjacentAvg(ctx) {
  const arr = ctx?.adjacentCameras || []
  if (!arr.length) return "—"
  return Math.round(arr.reduce((s, c) => s + (c.vehicleCount || 0), 0) / arr.length)
}
function adjacentSpeedAvg(ctx) {
  const arr = ctx?.adjacentCameras || []
  if (!arr.length) return "—"
  return (arr.reduce((s, c) => s + (c.avgSpeed || 0), 0) / arr.length).toFixed(1)
}

// 통계 지표 톤 분기
function zScoreTone(z) {
  const abs = Math.abs(z)
  if (abs >= 4) return "rd"
  if (abs >= 2.5) return "yl"
  return "gr"
}
function slopeTone(s) {
  if (s == null) return "gy"
  return s < 0 ? "rd" : "gr"
}
function confTone(c) {
  if (c == null) return "gy"
  if (c >= 0.7) return "gr"
  if (c >= 0.5) return "yl"
  return "rd"
}

// 티켓 변경 이력 (현재 상태에 맞춰 발생한 단계까지의 history 생성)
// 실제 백엔드 연동 시 GET /tickets/{id}/history 로 교체
function ticketHistory(fault) {
  if (!fault) return []
  const events = []
  const STAGES = ["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]
  const currentIdx = STAGES.indexOf(fault.ticketStatus)
  const baseTime = fault.time || "10:00:00"

  // 발생 (항상)
  events.push({
    action: "티켓 생성",
    kind: "create",
    at: `${baseTime}`,
    by: fault.detectionMethod === "TREND_PROJECTION" ? "예지 시스템" : "장애 자동 감지",
    from: null, to: "OPEN",
    note: fault.symp,
  })
  // 배정
  if (currentIdx >= 1) {
    events.push({
      action: "담당자 배정",
      kind: "assign",
      at: addMin(baseTime, 4),
      by: "운영자",
      from: "OPEN", to: "ASSIGNED",
      note: `${fault.who || "담당자"}에게 배정`,
    })
  }
  // 진행 중
  if (currentIdx >= 2) {
    events.push({
      action: "작업 시작",
      kind: "progress",
      at: addMin(baseTime, 12),
      by: fault.who || "담당자",
      from: "ASSIGNED", to: "IN_PROGRESS",
      note: "현장 점검 시작",
    })
  }
  // 해결
  if (currentIdx >= 3) {
    events.push({
      action: "작업 완료",
      kind: "resolve",
      at: addMin(baseTime, 38),
      by: fault.who || "담당자",
      from: "IN_PROGRESS", to: "RESOLVED",
      note: "장비 재기동 후 정상 동작 확인",
    })
  }
  // 종결
  if (currentIdx >= 4) {
    events.push({
      action: "최종 종결",
      kind: "close",
      at: addMin(baseTime, 52),
      by: "운영자",
      from: "RESOLVED", to: "CLOSED",
      note: "복구 확인 후 종결",
    })
  }
  return events
}

function addMin(hms, mins) {
  const [h, m, s] = (hms || "00:00:00").split(":").map((n) => parseInt(n, 10))
  const total = h * 60 + m + mins
  const nh = Math.floor(total / 60)
  const nm = total % 60
  const pad = (n) => String(n).padStart(2, "0")
  return `${pad(nh)}:${pad(nm)}:${pad(s || 0)}`
}

// 라벨 헬퍼 (Enum → 한글)
function anomalyTypeLabelKo(t) {
  const m = {
    CAMERA_OFFLINE: "카메라 오프라인",
    FPS_DEGRADATION: "FPS 저하",
    FRAME_DROP_DEGRADATION: "프레임 손실 증가",
    LATENCY_DEGRADATION: "지연시간 증가",
    BLUR_DEGRADATION: "흐림 증가",
    OCR_QUALITY_DEGRADATION: "OCR 품질 저하",
    RESOURCE_SATURATION: "리소스 과부하",
    NETWORK_INSTABILITY: "네트워크 불안정",
  }
  return m[t] || t || "—"
}
function detectionMethodLabelKo(m) {
  const map = {
    RULE: "룰",
    ROBUST_Z_SCORE: "z-score",
    TREND_PROJECTION: "추세 예측",
    CROSS_VALIDATION: "교차 검증",
    LSTM_AUTOENCODER: "LSTM",
  }
  return map[m] || m || "—"
}
function ticketStatusLabel(s) {
  const map = {
    OPEN: "대기",
    ASSIGNED: "배정",
    IN_PROGRESS: "진행 중",
    RESOLVED: "해결",
    CLOSED: "종결",
  }
  return map[s] || s || "—"
}

// 관측값 판정 — 관측이 임계를 넘었는가 (방향은 metric별로 다르지만 여기선 단순 비교)
function evJudge(e) {
  if (e.metric === "FPS") return e.observed < e.threshold ? "임계 초과" : "정상"
  return e.observed > e.threshold ? "임계 초과" : "정상"
}
function evTone(e) {
  return evJudge(e) === "임계 초과" ? "rd" : "gr"
}

// SHADOW 점수 색상 (위험 ≥ critical, 경고 ≥ warning, 그 외 정상)
function shadowScoreTone(s) {
  if (!s) return "gy"
  if (s.score >= s.criticalThreshold) return "rd"
  if (s.score >= s.warningThreshold) return "yl"
  return "gr"
}
function shadowPredTone(s) {
  if (!s) return ""
  return s.predictedSeverity === "CRITICAL" ? "rd-txt" : "yl-txt"
}

// SLA 잔여 시간 표시
function formatSlaRemaining(min) {
  if (min == null) return "—"
  if (min < 0) {
    const abs = Math.abs(min)
    return abs >= 60 ? `${(abs / 60).toFixed(1)}시간 초과` : `${abs}분 초과`
  }
  if (min < 60) return `${min}분 남음`
  return `${(min / 60).toFixed(1)}시간 남음`
}

// ─── 티켓 상태 전이 modal ───
const ticketModal = ref(null)
function openTicketTransition(fault, toStatus) {
  ticketModal.value = { fault, toStatus, note: "", error: "" }
}
function closeTicketModal() { ticketModal.value = null }
function submitTicketTransition() {
  if (!ticketModal.value) return
  const { toStatus, note } = ticketModal.value
  if (toStatus === "RESOLVED" && !note.trim()) {
    ticketModal.value.error = "RESOLVED 전환 시 조치 메모는 필수입니다."
    return
  }
  // 실제 호출은 백엔드 연동 후: changeTicketStatus(ticketId, { toStatus, note })
  console.info("[ticket transition]", ticketModal.value.fault.id, "→", toStatus, note)
  closeTicketModal()
}

// ─── 이상 이벤트 resolve / dismiss 모달 ───
// 백엔드 계약: resolve = confirmedCause + resolutionNote 필수
//              dismiss = reason 필수
const anomalyModal = ref(null)

// ─── 담당자 배정 모달 ───
const assignees = [
  { id: 7,  name: "김기사",  role: "MAINTAINER" },
  { id: 8,  name: "이엔지",  role: "MAINTAINER" },
  { id: 9,  name: "박엔지",  role: "MAINTAINER" },
  { id: 12, name: "정매니저", role: "OPERATOR" },
]
const assignModal = ref(null)
function openAssignModal(target) {
  assignModal.value = { target, assigneeId: "", note: "", error: "" }
}
function closeAssignModal() { assignModal.value = null }
function submitAssignModal() {
  if (!assignModal.value) return
  if (!assignModal.value.assigneeId) {
    assignModal.value.error = "담당자를 선택해주세요."
    return
  }
  // 실제 호출: assignMaintenanceTicket(ticketId, { assigneeId, note })
  console.info("[assign]", assignModal.value.target.id,
    "→", assignModal.value.assigneeId, assignModal.value.note)
  closeAssignModal()
}

function openAnomalyResolve(anom) {
  anomalyModal.value = {
    mode: "resolve",
    anom,
    confirmedCause: "",
    resolutionNote: "",
    reason: "",
    error: "",
  }
}
function openAnomalyDismiss(anom) {
  anomalyModal.value = {
    mode: "dismiss",
    anom,
    confirmedCause: "",
    resolutionNote: "",
    reason: "",
    error: "",
  }
}
function closeAnomalyModal() { anomalyModal.value = null }

function submitAnomalyModal() {
  if (!anomalyModal.value) return
  const m = anomalyModal.value
  if (m.mode === "resolve") {
    if (!m.confirmedCause.trim()) {
      m.error = "확정 원인은 필수입니다."
      return
    }
    if (!m.resolutionNote.trim()) {
      m.error = "조치 내용은 필수입니다."
      return
    }
    // 실제 호출: resolveAnomaly(eventId, { confirmedCause, resolutionNote })
    console.info("[anomaly resolve]", m.anom.id, {
      confirmedCause: m.confirmedCause,
      resolutionNote: m.resolutionNote,
    })
  } else if (m.mode === "dismiss") {
    if (!m.reason.trim()) {
      m.error = "오탐 종료 사유는 필수입니다."
      return
    }
    // 실제 호출: dismissAnomaly(eventId, { reason })
    console.info("[anomaly dismiss]", m.anom.id, { reason: m.reason })
  }
  closeAnomalyModal()
}

// ─── 탐지 정책 (settings 탭) ───
// 백엔드 계약 §3-14 응답 구조 매핑.
// thresholdDirection은 B방안(미표시) — DB·백엔드 내부에서만 사용, 프론트는 숫자만.
// consecutiveWindows는 warning/critical 2필드로 분리 (DB 협의 2026-06-12)
const pmPolicies = ref([
  {
    policyCode: "FPS_DEGRADATION_RULE_V1",
    anomalyType: "FPS_DEGRADATION",
    detectionMethod: "RULE",
    warningThreshold: 10.0,
    criticalThreshold: 5.0,
    warningConsecutiveWindows: 3,
    criticalConsecutiveWindows: 3,
    enabled: true,
    unit: "fps",
    step: 0.5,
  },
  {
    policyCode: "LATENCY_DEGRADATION_RULE_V1",
    anomalyType: "LATENCY_DEGRADATION",
    detectionMethod: "RULE",
    warningThreshold: 2000,
    criticalThreshold: 5000,
    warningConsecutiveWindows: 3,
    criticalConsecutiveWindows: 3,
    enabled: true,
    unit: "ms",
    step: 100,
  },
  {
    policyCode: "RESOURCE_SATURATION_RULE_V1",
    anomalyType: "RESOURCE_SATURATION",
    detectionMethod: "RULE",
    warningThreshold: 85,
    criticalThreshold: 95,
    warningConsecutiveWindows: 5,  // 경고 5분 (비대칭)
    criticalConsecutiveWindows: 3, // 위험 3분
    enabled: true,
    unit: "%",
    step: 1,
  },
  {
    policyCode: "OCR_QUALITY_DEGRADATION_RULE_V1",
    anomalyType: "OCR_QUALITY_DEGRADATION",
    detectionMethod: "RULE",
    warningThreshold: 0.70,
    criticalThreshold: 0.90,
    warningConsecutiveWindows: 3,
    criticalConsecutiveWindows: 3,
    enabled: true,
    unit: "",
    step: 0.05,
  },
  {
    policyCode: "NETWORK_INSTABILITY_RULE_V1",
    anomalyType: "NETWORK_INSTABILITY",
    detectionMethod: "RULE",
    warningThreshold: 500,
    criticalThreshold: 1000,
    warningConsecutiveWindows: 3,
    criticalConsecutiveWindows: 3,
    enabled: true,
    unit: "ms",
    step: 50,
  },
  {
    policyCode: "BLUR_DEGRADATION_RULE_V1",
    anomalyType: "BLUR_DEGRADATION",
    detectionMethod: "RULE",
    warningThreshold: 0.75,
    criticalThreshold: 0.90,
    warningConsecutiveWindows: 3,
    criticalConsecutiveWindows: 3,
    enabled: true,
    unit: "",
    step: 0.05,
  },
  {
    policyCode: "CAMERA_TREND_PROJECTION_V1",
    anomalyType: "FPS_DEGRADATION",
    detectionMethod: "TREND_PROJECTION",
    warningThreshold: 10.0,
    criticalThreshold: 5.0,
    warningConsecutiveWindows: 1,
    criticalConsecutiveWindows: 1,
    enabled: true,
    unit: "fps",
    step: 0.5,
    min: 0, max: 60,
    // TREND_PROJECTION 전용
    predictionHorizonMinutes: 10,
    ewmaAlpha: 0.3,
    minimumTrendConfidence: 0.6,
  },
  {
    policyCode: "CAMERA_ROBUST_ZSCORE_V1",
    anomalyType: "LATENCY_DEGRADATION",
    detectionMethod: "ROBUST_Z_SCORE",
    warningThreshold: 3.0,
    criticalThreshold: 5.0,
    warningConsecutiveWindows: 2,
    criticalConsecutiveWindows: 2,
    enabled: true,
    unit: "σ",
    step: 0.1,
    min: 1, max: 10,
    // ROBUST_Z_SCORE 전용
    zScoreWindowMinutes: 30,
    minimumSampleCount: 30,
  },
])

// 정책 입력 범위 설정 (min/max 미설정 시 사용)
;(function setPolicyRanges() {
  pmPolicies.value.forEach((p) => {
    if (p.min == null) p.min = 0
    if (p.max == null) {
      p.max = p.unit === "%" ? 100 : p.unit === "ms" ? 10000 : 1000
    }
  })
})()

// 정책 validation
const policyFieldErrors = ref({})
function validatePolicy(p) {
  const errs = {}
  // 1. 경고가 위험보다 더 위험한 값이면 안 됨 (방향에 따라 다르지만 단순화)
  // FPS_DEGRADATION (LOWER_IS_WORSE): warning(10) > critical(5)
  // LATENCY (HIGHER_IS_WORSE):       warning(2000) < critical(5000)
  const isLowerWorse = ["FPS_DEGRADATION"].includes(p.anomalyType)
  if (isLowerWorse) {
    if (p.warningThreshold <= p.criticalThreshold) {
      errs.warningThreshold = true; errs.criticalThreshold = true
    }
  } else {
    if (p.warningThreshold >= p.criticalThreshold) {
      errs.warningThreshold = true; errs.criticalThreshold = true
    }
  }
  // 2. 연속 윈도 1~10
  if (p.warningConsecutiveWindows < 1 || p.warningConsecutiveWindows > 10) errs.warningConsecutiveWindows = true
  if (p.criticalConsecutiveWindows < 1 || p.criticalConsecutiveWindows > 10) errs.criticalConsecutiveWindows = true
  // 3. 범위 검증
  if (p.warningThreshold < p.min || p.warningThreshold > p.max) errs.warningThreshold = true
  if (p.criticalThreshold < p.min || p.criticalThreshold > p.max) errs.criticalThreshold = true

  policyFieldErrors.value = { ...policyFieldErrors.value, [p.policyCode]: errs }
}
function hasPolicyError(p) {
  const e = policyFieldErrors.value[p.policyCode] || {}
  return Object.values(e).some(Boolean)
}
function policyErrorMessage(p) {
  const e = policyFieldErrors.value[p.policyCode] || {}
  const msgs = []
  const isLowerWorse = ["FPS_DEGRADATION"].includes(p.anomalyType)
  if (e.warningThreshold && e.criticalThreshold) {
    msgs.push(isLowerWorse
      ? "경고 임계는 위험 임계보다 커야 합니다 (낮을수록 위험)"
      : "위험 임계는 경고 임계보다 커야 합니다")
  }
  if (e.warningConsecutiveWindows || e.criticalConsecutiveWindows) msgs.push("연속 윈도는 1~10회 사이여야 합니다")
  if (e.warningThreshold && !e.criticalThreshold) msgs.push(`경고 임계는 ${p.min}~${p.max}${p.unit} 범위여야 합니다`)
  return msgs.join(" / ")
}

const policyConfirm = ref(null)
function openPolicyConfirm(p) {
  policyConfirm.value = { ...p }
}
// 정책 저장 (백엔드 PATCH + 성공 후 서버 데이터 재조회 — TODO 5-6)
async function submitPolicyUpdate() {
  if (!policyConfirm.value) return
  const code = policyConfirm.value.policyCode
  // payload: thresholdDirection 보내지 않음 (B방안), consecutiveWindows는 2필드
  const payload = {
    warningThreshold:           policyConfirm.value.warningThreshold,
    criticalThreshold:          policyConfirm.value.criticalThreshold,
    warningConsecutiveWindows:  policyConfirm.value.warningConsecutiveWindows,
    criticalConsecutiveWindows: policyConfirm.value.criticalConsecutiveWindows,
    enabled:                    policyConfirm.value.enabled,
  }
  try {
    const { updatePolicy, listPolicies } = await import("@/api/predictiveApi")
    await updatePolicy(code, payload)
    // 성공 후 서버 데이터 재조회 — 다른 사용자의 변경분도 함께 반영
    const result = await listPolicies()
    if (Array.isArray(result?.content)) {
      pmPolicies.value = result.content
    }
  } catch (err) {
    // 백엔드 미연동 상태 (현재 데모) — console 출력 + 로컬 상태만 갱신
    console.info("[policy update] (오프라인 데모 모드)", code, payload,
      err?.normalized?.message || err?.message)
  }
  policyConfirm.value = null
}

const alarmsTimeline = Object.freeze([
  {
    id: 1,
    time: "14:24:17",
    kind: "event",
    sev: "CRIT",
    dev: "NSN-N-0023",
    msg: "RTSP 스트림 응답 없음 (timeout 30s)",
    who: "김기사",
  },
  {
    id: 2,
    time: "14:18:05",
    kind: "event",
    sev: "HIGH",
    dev: "GBG-S-0077",
    msg: "네트워크 지연 286ms 임계 초과",
    who: "자동",
  },
  {
    id: 3,
    time: "14:11:42",
    kind: "event",
    sev: "MED",
    dev: "ocr-srv-02",
    msg: "디스크 사용량 78% 경고",
    who: "—",
  },
]);
// 시연용 현재 시각 (헤더 14:32:18 기준) — 1초마다 tick
const nowSec = ref(14 * 3600 + 32 * 60 + 18);
let nowTimer = null;
// ESC 키로 열려있는 모달 닫기 (접근성)
function onGlobalKeydown(e) {
  if (e.key !== "Escape") return
  // 우선순위: 가장 최근에 연 모달부터
  if (anomalyModal.value) { closeAnomalyModal(); return }
  if (ticketModal.value) { closeTicketModal(); return }
  if (policyConfirm.value) { policyConfirm.value = null; return }
  if (camModal.value) { camModal.value = null; return }
  if (alarmModal.value) { alarmModal.value = null; return }
}

onMounted(() => {
  nowTimer = setInterval(() => {
    nowSec.value += 1;
  }, 1000);
  document.addEventListener("keydown", onGlobalKeydown)
});
onBeforeUnmount(() => {
  if (nowTimer) clearInterval(nowTimer);
  document.removeEventListener("keydown", onGlobalKeydown)
});

function alarmSec(t) {
  const [h, m, s] = t.split(":").map(Number);
  return h * 3600 + m * 60 + s;
}
function formatElapsed(sec) {
  if (sec < 60) return `${sec}초`;
  if (sec < 3600) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return s === 0 ? `${m}분` : `${m}분 ${s}초`;
  }
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  return `${h}시간 ${m}분`;
}
function slaTone(sec) {
  if (sec < 5 * 60) return "warn";
  if (sec < 15 * 60) return "high";
  return "crit";
}
function slaText(a) {
  const elapsed = nowSec.value - alarmSec(a.time);
  if (elapsed < 0) return "—";
  return formatElapsed(elapsed);
}
function slaClass(a) {
  if (a.kind !== "event") return "resolved";
  const elapsed = nowSec.value - alarmSec(a.time);
  if (elapsed < 0) return "";
  return slaTone(elapsed);
}

const filteredAlarms = computed(() => {
  if (tlFilter.value === "ALL") return alarmsTimeline;
  if (tlFilter.value === "INFO")
    return alarmsTimeline.filter((a) => a.kind === "info" || a.kind === "recovered");
  return alarmsTimeline.filter((a) => a.sev === tlFilter.value);
});
const nav = [
  { id: "status", icon: "bi bi-grid-3x3", label: "장비 현황" },
  { id: "cams", icon: "bi bi-camera-video", label: "카메라" },
  { id: "srv", icon: "bi bi-hdd-stack", label: "서버" },
  { id: "net", icon: "bi bi-diagram-3", label: "네트워크" },
  { id: "fault", icon: "bi bi-exclamation-triangle", label: "장애·이상 관리", bdg: 3 },
  { id: "settings", icon: "bi bi-gear", label: "설정" },
];

/* ── 헤더 실시간 알림 ── */
const showAlerts = ref(false);
const liveAlerts = ref([
  { id: 1, sev: "critical", icon: "bi bi-camera-video-off", title: "카메라 RTSP 타임아웃", detail: "NSN-N-0023 — 12분간 무신호. 현장 점검 필요", place: "내부순환로 03K+150", time: "14:18" },
  { id: 2, sev: "serious",  icon: "bi bi-hdd-network",      title: "엣지 서버 디스크 90% 도달", detail: "EDGE-02 디스크 용량 임계치 초과", place: "정릉터널",         time: "13:50" },
  { id: 3, sev: "caution",  icon: "bi bi-wifi-off",         title: "네트워크 지연 상승",      detail: "강남 권역 평균 지연 286ms (정상 100ms 대비)", place: "강남 권역", time: "13:32" },
  { id: 4, sev: "info",     icon: "bi bi-check-circle-fill",title: "정기 점검 완료",          detail: "OCR 서버 4대 정상 재가동 확인",        place: "OCR 클러스터",      time: "10:00" },
]);
const hasCritical = computed(() => liveAlerts.value.some(a => a.sev === "critical"));

/* ── 설정 ── */
const setSound = ref(true);
const setRefreshSec = ref(30);
const setMsg = ref("");
function saveSettings() {
  setMsg.value = "설정 저장 완료";
  setTimeout(() => { setMsg.value = ""; }, 1800);
}

function closeAlertsOnOutside(e) {
  if (showAlerts.value && !e.target.closest(".hdr-bell-wrap")) showAlerts.value = false;
}
if (typeof document !== "undefined") {
  document.addEventListener("click", closeAlertsOnOutside);
}

// 카메라 데이터 — 기존 운영 필드(st/lat/ts) + 예지보전 필드(healthScore/predictedRisk) 통합
// 3건: 정상 / 지연+악화예측 / 장애 (각 상태 대표 1건씩)
const cams = Object.freeze([
  {
    name: "한남대교_남단_A4",
    loc: "강변북로 09K+200",
    st: "정상", stTone: "ok",
    lat: 94, ts: "10:32:18",
    id: "GBN-S-0032",
    healthScore: 88.4, healthStatus: "NORMAL",
    predictedRisk: 0,
  },
  {
    name: "가양IC_본선_C2",
    loc: "올림픽대로 14K+800",
    st: "지연", stTone: "wn",
    lat: 142, ts: "10:32:17",
    id: "OLP-W-0041",
    // 추세 예측 — 12분 후 임계 초과
    healthScore: 67.2, healthStatus: "DEGRADED",
    predictedRisk: 1,
    predictedType: "FPS 저하",
    predictedAt: "10:44",
  },
  {
    name: "정릉터널_입구_B1",
    loc: "내부순환로 03K+150",
    st: "장애", stTone: "no",
    lat: "—", ts: "10:24:17",
    id: "NSN-N-0023",
    healthScore: 0, healthStatus: "OFFLINE",
    predictedRisk: 0,
  },
  {
    // 신규 설치 카메라 — 기준선 학습 중 (예지보전 케이스 다양성)
    name: "마곡대로_C7",
    loc: "마곡대로 04K+700",
    st: "수집 중", stTone: "wn",
    lat: 102, ts: "10:32:11",
    id: "MGK-W-0102",
    healthScore: null, healthStatus: "BASELINE_LEARNING",
    baselineSamples: 14,
    baselineRequired: 30,
    predictedRisk: 0,
  },
]);

/* ── 예지보전 KPI (cams 기반 집계) ── */
const pmHealthAvg = computed(() => {
  const live = cams.filter((c) => c.healthStatus !== "OFFLINE")
  if (!live.length) return 0
  return (live.reduce((s, c) => s + c.healthScore, 0) / live.length).toFixed(1)
})
const pmPredictedCount = computed(() => cams.filter((c) => c.predictedRisk > 0).length)
const pmCriticalCount = computed(() => cams.filter((c) => c.healthStatus === "CRITICAL").length)
const pmBaselineLearning = computed(() => cams.filter((c) => c.healthStatus === "BASELINE_LEARNING").length)
const pmOverdueTickets = ref(1) // SLA 초과 티켓 — 추후 백엔드 연동 시 교체

// dataSource 필터 (status 탭) — 백엔드 호출 시 query parameter로 전달
const pmDataSource = ref("REAL")
function pmDataSourceLabel(v) {
  return { REAL: "실데이터", OPEN_DATA: "공개데이터", SIMULATED: "시뮬레이션", FAULT_INJECTED: "장애 주입", MOCK: "목업" }[v] || v
}
function pmDataSourceTone(v) {
  return v === "FAULT_INJECTED" ? "rd" : v === "MOCK" ? "gy" : "yl"
}
const pmSloOk = computed(() => pmHealthAvg.value >= 75)
function pmScoreTone(score) {
  if (score == null) return "gy"
  if (score < 50) return "rd"
  if (score < 70) return "yl"
  return "gr"
}

// Health Score 30분 sparkline 좌표 (확정적 더미)
// viewBox 400x100 — y는 0=Health 100, 100=Health 0 (역방향)
function pmSparklinePoints(cam) {
  if (!cam) return ""
  const cur = cam.healthScore || 50
  const pts = []
  // 14 표본 — 30분 / 14 ≈ 2분 간격
  // 시작값은 현재의 +5~+10 (이전엔 더 좋았다가 점차 떨어진 경향), 마지막은 cur
  const start = Math.min(100, cur + (cam.predictedRisk > 0 ? 12 : 3))
  for (let i = 0; i < 14; i++) {
    const t = i / 13
    const noise = Math.sin(i * 1.7 + cam.healthScore) * 2
    const v = start + (cur - start) * t + noise
    const x = (280 / 13) * i
    const y = 100 - v // y 반전
    pts.push(`${x.toFixed(1)},${Math.max(0, Math.min(100, y)).toFixed(1)}`)
  }
  return pts.join(" ")
}

// 예측선 — 현재 시점부터 우측까지, 추세 기울기로 외삽
function pmPredictedPoints(cam) {
  if (!cam || !cam.predictedRisk) return ""
  const cur = cam.healthScore || 50
  const pts = []
  // 10분 예측 — viewBox의 280~400 영역
  // 추세 기울기: predictedRisk 있으면 -1.5 ~ -2 (악화)
  const slope = -1.8
  for (let i = 0; i <= 5; i++) {
    const t = i / 5
    const v = cur + slope * (i + 1)
    const x = 280 + (120 / 5) * i
    const y = 100 - Math.max(0, v)
    pts.push(`${x.toFixed(1)},${Math.max(0, Math.min(100, y)).toFixed(1)}`)
  }
  return pts.join(" ")
}

// 메트릭별 sparkline (viewBox 200x36)
function metricSparkline(m) {
  if (!m) return ""
  const cur = parseFloat(m.cur) || 0
  const base = parseFloat(m.base) || 0
  // 12 표본 — 시작은 base 근처, 끝은 cur
  const pts = []
  for (let i = 0; i < 12; i++) {
    const t = i / 11
    const noise = Math.sin(i * 1.3 + cur * 0.1) * (Math.abs(cur - base) * 0.08)
    const v = base + (cur - base) * t + noise
    const x = (200 / 11) * i
    const y = metricYCoord(v, m)
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`)
  }
  return pts.join(" ")
}
function metricYCoord(v, m) {
  // y: 0(상) ~ 36(하), 값이 작을수록 정상인 경우(FPS만)
  const base = parseFloat(m.base) || 0
  const thr = parseFloat(m.thr) || 0
  const range = Math.max(Math.abs(base - thr) * 2, 1)
  const center = (base + thr) / 2
  const norm = (v - center) / range  // -0.5 ~ 0.5
  return Math.max(2, Math.min(34, 18 - norm * 24))
}
function baselineY(m) { return metricYCoord(parseFloat(m.base), m) }
function thresholdY(m) { return metricYCoord(parseFloat(m.thr), m) }
function metricStrokeColor(tone) {
  return tone === "rd" ? "#dc2626" : tone === "yl" ? "#d97706" : tone === "gr" ? "#059669" : "#9aa6b8"
}

// 카메라 헬스 핵심 지표 4종 — 현재 / 기준선 / 임계
function pmCameraMetrics(cam) {
  if (!cam) return []
  const offline = cam.healthStatus === "OFFLINE"
  const isFps = cam.predictedType?.includes("FPS")
  const isOcr = cam.predictedType?.includes("OCR")
  // 카메라 별 가상 메트릭 — 현재 상태에 따라 조정
  const fpsCur = offline ? 0 : isFps ? 11.2 : 23.4
  const latCur = typeof cam.lat === "number" ? cam.lat : 0
  const cpuCur = offline ? 0 : (cam.healthScore < 70 ? 91.3 : 42.5)
  const ocrFailCur = offline ? 100 : isOcr ? 31.0 : 5.2
  return [
    {
      label: "FPS",
      cur: fpsCur.toFixed(1), base: "24.1", thr: "10.0", unit: "",
      tone: fpsCur < 10 ? "rd" : fpsCur < 16 ? "yl" : "gr",
    },
    {
      label: "지연(P95)",
      cur: latCur || "—", base: "540", thr: "2000", unit: "ms",
      tone: latCur > 2000 ? "rd" : latCur > 1000 ? "yl" : latCur ? "gr" : "gy",
    },
    {
      label: "CPU 사용률",
      cur: cpuCur.toFixed(1), base: "45.0", thr: "85.0", unit: "%",
      tone: cpuCur > 85 ? "rd" : cpuCur > 70 ? "yl" : "gr",
    },
    {
      label: "OCR 실패율",
      cur: ocrFailCur.toFixed(1), base: "5.0", thr: "20.0", unit: "%",
      tone: ocrFailCur > 20 ? "rd" : ocrFailCur > 10 ? "yl" : "gr",
    },
  ]
}

const servers = Object.freeze([
  {
    name: "ocr-srv-01",
    tag: "Primary",
    ip: "10.20.10.11",
    st: "정상",
    stTone: "ok",
    bars: [
      { l: "CPU", v: "34.2%", bar: 34, color: "#6fa581", tone: "" },
      { l: "메모리", v: "43.7%", bar: 44, color: "#6fa581", tone: "" },
      { l: "디스크", v: "38.1%", bar: 38, color: "#6fa581", tone: "" },
      { l: "서비스", v: "5/5", bar: 100, color: "#6fa581", tone: "" },
    ],
  },
  {
    name: "search-srv",
    tag: "",
    ip: "10.20.10.21",
    st: "경고",
    stTone: "wn",
    bars: [
      { l: "CPU", v: "73.4%", bar: 73, color: "#d4a652", tone: "yl" },
      { l: "메모리", v: "78.2%", bar: 78, color: "#d4a652", tone: "yl" },
      { l: "디스크", v: "62.0%", bar: 62, color: "#d4a652", tone: "yl" },
      { l: "서비스", v: "4/5", bar: 80, color: "#d4a652", tone: "yl" },
    ],
  },
]);

</script>

<style scoped src="./OpsView.css"></style>
<style scoped>
/* ── 예지보전 KPI 스트립 (status 탭 상단) — 세련된 미니멀 ── */
.ops-shell .pm-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-bottom: 12px;
  flex-shrink: 0;
}
.ops-shell .pm-kpi {
  background: #ffffff;
  border: 1px solid #eaeef5;
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
  transition: all .2s ease;
  box-shadow: 0 1px 2px rgba(12, 31, 64, 0.04);
}
.ops-shell .pm-kpi:hover {
  border-color: #d8e0ec;
  box-shadow: 0 4px 12px rgba(12, 31, 64, 0.06);
  transform: translateY(-1px);
}
.ops-shell .pm-kpi > i {
  font-size: 18px;
  color: #94a3b8;
  flex-shrink: 0;
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  background: #f4f7fb;
  border-radius: 8px;
}
.ops-shell .pm-kpi-b { flex: 1; min-width: 0; }
.ops-shell .pm-kpi-v {
  font-family: 'Inter', 'Pretendard Variable', sans-serif;
  font-weight: 700;
  font-size: 24px;
  color: #0c1f40;
  line-height: 1.1;
  letter-spacing: -0.02em;
}
.ops-shell .pm-kpi-v > small { font-size: 11.5px; font-weight: 500; color: #94a3b8; margin-left: 3px; }
.ops-shell .pm-kpi-l {
  font-size: 11.5px;
  color: #64748b;
  font-weight: 500;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ops-shell .pm-sub {
  font-size: 10.5px;
  font-weight: 400;
  color: #94a3b8;
}
.ops-shell .pm-kpi.ok > i { color: #059669; background: #ecfdf5; }
.ops-shell .pm-kpi.bad > i { color: #d97706; background: #fffbeb; }
.ops-shell .pm-kpi.alert > i { color: #dc2626; background: #fef2f2; }
.ops-shell .pm-kpi.alert .pm-kpi-v { color: #dc2626; }
.ops-shell .pm-kpi.bl > i { color: #7c3aed; background: #f5f3ff; }

/* ── 카메라 표 — Health 컬럼 + 악화 예측 배지 ── */
.ops-shell .pm-cam-tbl .num { text-align: right; }
.ops-shell .pm-hs {
  font-weight: 800;
  padding: 1px 8px;
  border-radius: 100px;
  font-size: 12px;
}
.ops-shell .pm-hs.gr { background: rgba(5,150,105,0.12); color: #059669; }
.ops-shell .pm-hs.yl { background: rgba(217,119,6,0.12); color: #d97706; }
.ops-shell .pm-hs.rd { background: rgba(220,38,38,0.12); color: #dc2626; }
.ops-shell .pm-hs.gy { background: rgba(107,114,128,0.15); color: #6b7280; }
.ops-shell .pm-pred-bdg {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 6px;
  padding: 1px 7px;
  border-radius: 100px;
  background: rgba(234,88,12,0.12);
  color: #ea580c;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
.ops-shell .pm-pred-bdg > i { font-size: 9px; }

@media (max-width: 1400px) {
  .ops-shell .pm-strip { grid-template-columns: repeat(3, 1fr); }
  .ops-shell .pm-kpi > i { font-size: 18px; }
  .ops-shell .pm-kpi-v { font-size: 20px; }
}
@media (max-width: 1100px) {
  .ops-shell .pm-strip { grid-template-columns: repeat(2, 1fr); gap: 6px; }
  .ops-shell .pm-kpi { padding: 8px 10px; gap: 8px; }
  .ops-shell .pm-kpi-l { font-size: 10.5px; }
  .ops-shell .pm-sub { display: none; }
}

/* ── cams 탭 KPI 9박스 ── */
.ops-shell .net-detail .pnl-summary.nd-kpi-9 {
  grid-template-columns: repeat(9, 1fr);
}
.ops-shell .ps-box.pm {
  border-top: 3px solid #2563eb;
  background: #f6faff;
}
.ops-shell .ps-box.pm .ps-l > i { color: #2563eb; margin-right: 4px; font-size: 11px; }
.ops-shell .ps-box.pm-alert {
  border-top: 3px solid #ea580c;
}
.ops-shell .ps-box.pm-alert .ps-l > i { color: #ea580c; margin-right: 4px; font-size: 11px; }
.ops-shell .ps-box.pm-alert.alert { background: #fff7ed; }
@media (max-width: 1600px) {
  .ops-shell .net-detail .pnl-summary.nd-kpi-9 { grid-template-columns: repeat(5, 1fr); }
}

/* ── 카메라 모달 예지 헬스 패널 ── */
.ops-shell .cm-pm {
  border-top: 1px solid #e3e9f1;
  padding: 16px 20px;
  background: #fafbfd;
}
.ops-shell .cm-pm-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.ops-shell .cm-pm-head h4 {
  font-size: 14px;
  font-weight: 800;
  color: #0c1f40;
  margin: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.ops-shell .cm-pm-head h4 > i { color: #2563eb; }
.ops-shell .cm-pm-score {
  margin-left: 6px;
  padding: 2px 10px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 800;
  font-family: 'JetBrains Mono', monospace;
}
.ops-shell .cm-pm-score.gr { background: rgba(5,150,105,0.12); color: #059669; }
.ops-shell .cm-pm-score.yl { background: rgba(217,119,6,0.12); color: #d97706; }
.ops-shell .cm-pm-score.rd { background: rgba(220,38,38,0.12); color: #dc2626; }
.ops-shell .cm-pm-score.gy { background: rgba(107,114,128,0.15); color: #6b7280; }
.ops-shell .cm-pm-pred {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(234,88,12,0.1);
  border: 1px solid rgba(234,88,12,0.3);
  border-radius: 6px;
  font-size: 12px;
  color: #ea580c;
  font-weight: 600;
}
.ops-shell .cm-pm-pred > i { font-size: 13px; }

.ops-shell .cm-pm-chart {
  background: #ffffff;
  border: 1px solid #e3e9f1;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
.ops-shell .cm-pm-chart-lab {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11.5px;
  color: #4a5b78;
  font-weight: 600;
  margin-bottom: 6px;
}
.ops-shell .cm-pm-chart-leg {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 10.5px;
  color: #4a5b78;
  font-weight: 500;
}
.ops-shell .cm-pm-chart-leg > i {
  display: inline-block;
  width: 14px;
  height: 0;
  border-top: 2px solid;
  margin-right: 3px;
  vertical-align: middle;
}
.ops-shell .ln-base { border-top-style: dashed !important; border-color: #9aa6b8; }
.ops-shell .ln-thr  { border-top-style: dashed !important; border-color: #dc2626; }
.ops-shell .ln-pred { border-top-style: dashed !important; border-color: #ea580c; }
.ops-shell .cm-pm-svg {
  width: 100%;
  height: 100px;
  display: block;
}

.ops-shell .cm-pm-mtx {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.ops-shell .cm-pm-mtx-row {
  background: #ffffff;
  border: 1px solid #e3e9f1;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.ops-shell .cm-pm-mtx-row.rd { border-left: 3px solid #dc2626; }
.ops-shell .cm-pm-mtx-row.yl { border-left: 3px solid #d97706; }
.ops-shell .cm-pm-mtx-row.gr { border-left: 3px solid #059669; }
.ops-shell .cm-pm-mtx-row.gy { border-left: 3px solid #9aa6b8; }
.ops-shell .cm-pm-mtx-l {
  font-size: 11px;
  font-weight: 700;
  color: #4a5b78;
  letter-spacing: 0.02em;
}
.ops-shell .cm-pm-mtx-vals {
  display: flex;
  align-items: baseline;
  gap: 6px;
  font-size: 12px;
  flex-wrap: wrap;
}
.ops-shell .cm-pm-mtx-cur {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 800;
  font-size: 18px;
  color: #0c1f40;
}
.ops-shell .cm-pm-mtx-cur.rd { color: #dc2626; }
.ops-shell .cm-pm-mtx-cur.yl { color: #d97706; }
.ops-shell .cm-pm-mtx-cur.gr { color: #059669; }
.ops-shell .cm-pm-mtx-cur.gy { color: #9aa6b8; }
.ops-shell .cm-pm-mtx-sep { font-size: 10.5px; color: #9aa6b8; }
.ops-shell .cm-pm-mtx-base {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11.5px;
  color: #4a5b78;
}
.ops-shell .cm-pm-mtx-base > em { font-style: normal; font-size: 10px; opacity: 0.65; margin-left: 1px; }
.ops-shell .cm-pm-mtx-thr {
  margin-left: auto;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: #dc2626;
  background: rgba(220,38,38,0.08);
  padding: 1px 6px;
  border-radius: 100px;
}

/* ============ fault 탭 — 활성 이상 카드 (세련된 톤) ============ */
.ops-shell .pm-anom-card {
  background: #ffffff;
  border: 1px solid #eaeef5;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(12, 31, 64, 0.04);
  position: relative;
}
.ops-shell .pm-anom-card::before {
  content: "";
  position: absolute;
  top: 0; left: 24px; right: 24px;
  height: 2px;
  background: linear-gradient(90deg, #ea580c, transparent);
  border-radius: 2px 2px 0 0;
}
.ops-shell .pm-anom-head {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 12px;
  margin-bottom: 20px;
}
.ops-shell .pm-anom-titles {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  font-size: 14px;
}
.ops-shell .pm-anom-titles > strong {
  font-size: 16px; color: #0c1f40;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.ops-shell .sev-bdg {
  padding: 3px 10px; border-radius: 6px;
  font-size: 10.5px; font-weight: 700; letter-spacing: 0.02em;
  text-transform: uppercase;
}
.ops-shell .sev-bdg.no, .ops-shell .sev-bdg.rd { background: #fef2f2; color: #dc2626; }
.ops-shell .sev-bdg.wn, .ops-shell .sev-bdg.yl { background: #fffbeb; color: #d97706; }
.ops-shell .dm-bdg {
  padding: 3px 10px; border-radius: 6px;
  background: #eff6ff;
  color: #2563eb; font-size: 11px; font-weight: 600;
  border: 1px solid #dbeafe;
}
.ops-shell .dm-bdg.sm { font-size: 10px; padding: 2px 7px; }
.ops-shell .pri-bdg {
  display: inline-block;
  padding: 3px 8px; border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10.5px; font-weight: 700;
  letter-spacing: 0.02em;
}
.ops-shell .pri-bdg.rd { background: #fef2f2; color: #dc2626; }
.ops-shell .pri-bdg.yl { background: #fffbeb; color: #d97706; }
.ops-shell .pri-bdg.gy { background: #f1f5f9; color: #64748b; }
.ops-shell .pm-anom-time {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 13px; color: #64748b;
}
.ops-shell .pm-anom-time > i { color: #ea580c; }
.ops-shell .pm-anom-time > strong { color: #ea580c; font-weight: 600; }

/* 관측값 테이블 — 미니멀 */
.ops-shell .pm-evidence-tbl {
  width: 100%; border-collapse: collapse;
  background: #fafbfd;
  border: 1px solid #eaeef5;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 20px;
}
.ops-shell .pm-evidence-tbl th {
  font-size: 11px; font-weight: 600; color: #64748b;
  padding: 10px 14px; text-align: left;
  border-bottom: 1px solid #eaeef5;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  background: #f4f7fb;
}
.ops-shell .pm-evidence-tbl .num { text-align: right; }
.ops-shell .pm-evidence-tbl td {
  padding: 10px 14px; font-size: 13px; color: #0c1f40;
  border-bottom: 1px solid #eaeef5;
}
.ops-shell .pm-evidence-tbl tr:last-child td { border-bottom: 0; }
.ops-shell .pm-evidence-tbl tr:hover td { background: #ffffff; }
.ops-shell .pm-evidence-tbl .mono { font-family: 'JetBrains Mono', monospace; font-size: 12.5px; }
.ops-shell .ev-jd {
  padding: 3px 10px; border-radius: 6px;
  font-size: 10.5px; font-weight: 700;
  letter-spacing: 0.02em;
}
.ops-shell .ev-jd.rd { background: #fef2f2; color: #dc2626; }
.ops-shell .ev-jd.gr { background: #ecfdf5; color: #059669; }
.ops-shell strong.rd { color: #dc2626; }
.ops-shell strong.gr { color: #059669; }
.ops-shell .rd-txt { color: #dc2626; }
.ops-shell .yl-txt { color: #d97706; }

/* 원인 후보 — 미니멀 카드 */
.ops-shell .pm-causes {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
  margin-bottom: 20px;
}
.ops-shell .pm-cause-blk {
  background: #fafbfd;
  border: 1px solid #eaeef5;
  border-radius: 10px;
  padding: 14px 18px;
}
.ops-shell .pm-cause-blk.confirmed {
  background: #ecfdf5;
  border-color: #d1fae5;
}
.ops-shell .pm-cause-h {
  font-size: 11px; font-weight: 600; color: #64748b;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.ops-shell .pm-cause-h em { font-style: normal; color: #94a3b8; font-weight: 400; margin-left: 4px; text-transform: none; letter-spacing: 0; }
.ops-shell .pm-cause-list {
  margin: 0; padding-left: 18px;
  font-size: 13px; color: #0c1f40; line-height: 1.7;
}
.ops-shell .pm-confirmed { font-size: 13.5px; color: #059669; font-weight: 600; }
.ops-shell .pm-confirmed-empty {
  font-size: 12.5px; color: #94a3b8;
  display: inline-flex; align-items: center; gap: 6px;
}

/* SHADOW 비교 모델 — 부드러운 톤 */
.ops-shell .pm-shadow {
  background: #faf8ff;
  border: 1px solid #ede9fe;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}
.ops-shell .pm-shadow-h {
  display: flex; align-items: center; gap: 10px;
  font-size: 13px; color: #5b21b6;
  margin-bottom: 14px; flex-wrap: wrap;
}
.ops-shell .pm-shadow-h > i { color: #7c3aed; font-size: 15px; }
.ops-shell .pm-shadow-h > strong { color: #4c1d95; font-size: 14px; font-weight: 600; letter-spacing: -0.01em; }
.ops-shell .shadow-bdg {
  padding: 3px 10px; border-radius: 6px;
  background: #ede9fe;
  color: #6d28d9; font-size: 10.5px; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase;
}
.ops-shell .pm-shadow-note {
  font-size: 11px; color: #7c6f9c;
  margin-left: auto;
  background: #ffffff;
  padding: 3px 10px;
  border-radius: 6px;
  border: 1px solid #ede9fe;
}
.ops-shell .pm-shadow-body {
  display: grid; grid-template-columns: 200px 1fr; gap: 14px;
}
.ops-shell .pm-shadow-score {
  background: #ffffff;
  border-radius: 6px; padding: 10px 12px;
  display: flex; flex-direction: column; gap: 4px;
}
.ops-shell .pm-ss-l { font-size: 11px; font-weight: 700; color: #4a5b78; }
.ops-shell .pm-ss-v {
  font-family: 'JetBrains Mono', monospace; font-weight: 800;
  font-size: 24px;
}
.ops-shell .pm-ss-v.gr { color: #059669; }
.ops-shell .pm-ss-v.yl { color: #d97706; }
.ops-shell .pm-ss-v.rd { color: #dc2626; }
.ops-shell .pm-ss-v.gy { color: #9aa6b8; }
.ops-shell .pm-ss-thr { font-size: 10.5px; color: #6b7280; font-family: 'JetBrains Mono', monospace; }
.ops-shell .pm-ss-pred { font-size: 11.5px; color: #4a5b78; margin-top: 2px; }

.ops-shell .pm-shadow-feats {
  background: #ffffff;
  border-radius: 6px; padding: 10px 12px;
}
.ops-shell .pm-sf-l {
  font-size: 11px; font-weight: 700; color: #4a5b78; margin-bottom: 8px;
}
.ops-shell .pm-sf-l em { font-style: normal; opacity: 0.65; font-weight: 500; margin-left: 4px; }
.ops-shell .pm-sf-rows { display: flex; flex-direction: column; gap: 5px; }
.ops-shell .pm-sf-row {
  display: grid; grid-template-columns: 100px 1fr 40px;
  align-items: center; gap: 8px;
  font-size: 12px;
}
.ops-shell .pm-sf-n { color: #4a5b78; font-family: 'JetBrains Mono', monospace; font-size: 11px; }
.ops-shell .pm-sf-bar {
  height: 6px; background: rgba(124,58,237,0.1); border-radius: 100px;
  overflow: hidden;
}
.ops-shell .pm-sf-fill {
  height: 100%; background: linear-gradient(90deg, #7c3aed, #ea580c);
  border-radius: 100px;
}
.ops-shell .pm-sf-v { text-align: right; color: #4c1d95; font-weight: 700; }

/* 액션 */
.ops-shell .pm-anom-acts {
  display: flex; gap: 6px; flex-wrap: wrap;
}

/* fault 목록 표 확장 */
.ops-shell .pm-fault-tbl .num { text-align: right; }
.ops-shell .pm-fault-tbl .pm-kind-bdg {
  display: inline-block;
  font-size: 9px; font-weight: 800;
  padding: 1px 5px; border-radius: 3px;
  background: #2563eb; color: #fff;
  margin-left: 4px; letter-spacing: 0.04em;
}
.ops-shell .pm-fault-acts { display: flex; gap: 4px; flex-wrap: wrap; }
.ops-shell .pnl-act.sm.gr { background: #059669; color: #fff; }
.ops-shell .pnl-act.sm.gr:hover { background: #047857; }

/* ============ 티켓 상태 전이 모달 ============ */
.ops-shell .pm-ticket-modal { max-width: 480px; }
.ops-shell .pm-ticket-body { padding: 16px 20px; }
.ops-shell .pm-ticket-note { margin-top: 12px; }
.ops-shell .pm-ticket-note > label {
  display: block; font-size: 12px; font-weight: 700; color: #4a5b78;
  margin-bottom: 6px;
}
.ops-shell .pm-ticket-note .req { color: #dc2626; margin-left: 4px; }
.ops-shell .pm-ticket-note textarea {
  width: 100%; padding: 10px;
  border: 1px solid #c9d4e3; border-radius: 6px;
  font-family: inherit; font-size: 13px;
  resize: vertical;
}
.ops-shell .pm-ticket-err {
  margin-top: 8px;
  color: #dc2626; font-size: 12px;
  display: flex; align-items: center; gap: 6px;
}
.ops-shell .pm-ticket-acts {
  margin-top: 16px;
  display: flex; gap: 8px; justify-content: flex-end;
}
.ops-shell .pnl-act.gr { background: #059669; color: #fff; border-color: #047857; }
.ops-shell .pnl-act.gr:hover { background: #047857; }

@media (max-width: 1200px) {
  .ops-shell .pm-shadow-body { grid-template-columns: 1fr; }
  .ops-shell .pm-causes { grid-template-columns: 1fr; }
  .ops-shell .pm-traffic-body { grid-template-columns: 1fr; gap: 8px; }
  .ops-shell .pm-traffic-arr { display: none; }
}
@media (max-width: 1100px) {
  /* fault 필터: 줄바꿈 + select 폭 적당히 */
  .ops-shell .pm-fault-filter { gap: 6px; }
  .ops-shell .pm-fault-filter select { font-size: 11.5px; padding: 4px 8px; }
  /* fault 표: 가로 스크롤 허용 — 컬럼 13개 초과 폭 시 */
  .ops-shell .pm-fault-tbl { font-size: 11.5px; }
  .ops-shell .pm-fault-tbl .pm-fault-acts .pnl-act.sm {
    font-size: 10.5px; padding: 3px 6px;
  }
}
@media (max-width: 900px) {
  .ops-shell .pm-policy-fields { grid-template-columns: 1fr; }
  .ops-shell .pm-field { grid-template-columns: 90px 1fr 28px; gap: 4px; }
}

/* ===== status 탭 카드 잘림 수정 =====
   pm-strip(KPI 5칩)가 .main-grid 위에 들어가서 가용 높이가 줄어
   카드 내부 표/리스트/장애 상세가 overflow:hidden에 잘림.
   해결: 카드 자체는 overflow:auto, 단 fail-card는 일부 자식만 스크롤. */
.ops-shell .main-grid > .card,
.ops-shell .main-grid > .bot-row > .card,
.ops-shell .main-grid > .col3-stack > .card {
  overflow: auto !important;
}
.ops-shell .main-grid .fl-cur,
.ops-shell .main-grid .tl-list,
.ops-shell .main-grid .cam-tbl tbody {
  overflow-y: auto;
  min-height: 0;
}

/* status 탭 — 네트워크/서버 카드 제거 후 그리드 단순화
   카메라 상태 위 + 알람타임라인/장애상세 아래로 swap */
.ops-shell .main-grid {
  grid-template-columns: 1fr !important;
  grid-template-rows: 1fr 1fr !important;
}
/* bot-row: 원래 display:contents → 박스로 부활시키고 row 1로 배치 */
.ops-shell .main-grid .bot-row {
  display: block !important;
  grid-column: 1 / -1 !important;
  grid-row: 1 !important;
}
/* bot-row 안의 cam-card는 원래 grid-row:2 강제 → 해제 */
.ops-shell .main-grid .bot-row .cam-card {
  grid-column: auto !important;
  grid-row: auto !important;
  width: 100%;
}
.ops-shell .main-grid .col3-stack {
  grid-column: 1 / -1 !important;
  grid-row: 2 !important;
  display: grid !important;
  grid-template-columns: 1fr 1fr !important;
  gap: 10px;
  overflow: visible !important;
  min-height: 0;
}
/* 좌측: 장애 상세, 우측: 알람 타임라인 */
.ops-shell .main-grid .col3-stack > .fail-card    { order: 1; min-height: 0; max-height: none !important; }
.ops-shell .main-grid .col3-stack > .timeline-card { order: 2; min-height: 0; max-height: none !important; }

/* fail-card 내부 hst가 flex:1로 squash되어 act-row와 겹치는 문제 수정.
   hst를 natural height + 자체 스크롤로 변경 — 항상 act-row와 명확히 분리. */
.ops-shell .main-grid .fail-card .hst {
  flex: 0 0 auto !important;
  max-height: 90px;
  overflow-y: auto;
  padding-bottom: 4px;
}
.ops-shell .main-grid .fail-card .act-row {
  margin-top: 6px !important;
  flex-shrink: 0;
}
.ops-shell .main-grid .fail-card h4 {
  margin-top: 8px !important;
  margin-bottom: 4px !important;
}

/* ===== 사이드바 푸터 가림 수정 ===== */
/* .snav가 가용 공간 차지하며 내부 스크롤 → .side-foot 항상 하단 노출 */
.ops-shell .side {
  height: 100vh;
  overflow: hidden;
}
.ops-shell .snav {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
.ops-shell .side-foot {
  flex-shrink: 0;
  padding-top: 8px;
  margin-top: 4px;
  border-top: 1px solid rgba(31, 48, 85, 0.4);
}

/* 모든 탭 섹션 내부 스크롤 — viewport 초과 시 하단 잘림 방지 */
.ops-shell .main > section.pnl,
.ops-shell .main > section.net-detail,
.ops-shell .pm-fault-scroll,
.ops-shell .pm-settings-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
.ops-shell .main > section.pnl > .pnl-head,
.ops-shell .pm-fault-scroll > .pnl-head {
  flex-shrink: 0;
}

/* ============ 탐지 정책 블록 ============ */
.ops-shell .pm-policy-block {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1px solid #eaeef5;
}
.ops-shell .pm-policy-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px; flex-wrap: wrap; gap: 8px;
}
.ops-shell .pm-policy-head h4 {
  font-size: 15px; font-weight: 800; color: #0c1f40;
  margin: 0; display: inline-flex; align-items: center; gap: 6px;
}
.ops-shell .pm-policy-head h4 > i { color: #7c3aed; }
.ops-shell .pm-policy-cnt {
  font-size: 11.5px; font-weight: 600; color: #4a5b78;
  background: rgba(124,58,237,0.08); color: #7c3aed;
  padding: 2px 8px; border-radius: 100px;
  margin-left: 6px;
}
.ops-shell .pm-readonly-bdg {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(107,114,128,0.12);
  color: #6b7280;
  padding: 4px 10px; border-radius: 6px;
  font-size: 11.5px; font-weight: 700;
}
.ops-shell .pm-admin-bdg {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(5,150,105,0.12);
  color: #059669;
  padding: 4px 10px; border-radius: 6px;
  font-size: 11.5px; font-weight: 700;
}
.ops-shell .pm-policy-note {
  font-size: 12px; color: #4a5b78;
  margin: 0 0 14px;
  background: #f4f7fb;
  padding: 8px 12px;
  border-left: 3px solid #2563eb;
  border-radius: 0 6px 6px 0;
}

.ops-shell .pm-policy-grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px;
}
.ops-shell .pm-policy-card {
  background: #ffffff;
  border: 1px solid #eaeef5;
  border-radius: 12px;
  padding: 18px 20px;
  display: flex; flex-direction: column; gap: 12px;
  transition: all .2s ease;
  box-shadow: 0 1px 2px rgba(12, 31, 64, 0.04);
}
.ops-shell .pm-policy-card:hover {
  border-color: #d8e0ec;
  box-shadow: 0 4px 12px rgba(12, 31, 64, 0.06);
}
.ops-shell .pm-policy-card.disabled { opacity: 0.55; }
.ops-shell .pm-policy-card-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
}
.ops-shell .pm-policy-titles {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 14px;
}
.ops-shell .pm-policy-titles > strong { font-size: 14px; color: #0c1f40; }
.ops-shell .pm-policy-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px; color: #6b7280;
  letter-spacing: 0.02em;
}
.ops-shell .pm-policy-toggle {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700;
  cursor: pointer; flex-shrink: 0;
}
.ops-shell .pm-policy-toggle.disabled { cursor: not-allowed; opacity: 0.6; }
.ops-shell .pm-policy-toggle input[type="checkbox"] {
  width: 16px; height: 16px;
  cursor: inherit;
}

.ops-shell .pm-policy-fields {
  display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
}
.ops-shell .pm-field {
  display: grid; grid-template-columns: 100px 1fr 32px;
  align-items: center; gap: 6px;
  font-size: 12px;
}
.ops-shell .pm-field > label {
  font-size: 11.5px; font-weight: 600; color: #4a5b78;
}
.ops-shell .pm-field > input[type="number"] {
  padding: 5px 8px;
  border: 1px solid #c9d4e3; border-radius: 5px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12.5px; color: #0c1f40;
  background: #ffffff;
}
.ops-shell .pm-field > input[disabled] {
  background: #f4f7fb; color: #6b7280; cursor: not-allowed;
}
.ops-shell .pm-field-unit {
  font-size: 11px; color: #6b7280; font-weight: 600;
}

.ops-shell .pm-policy-warn {
  background: rgba(217,119,6,0.08);
  color: #b45309;
  padding: 6px 10px;
  border-radius: 5px;
  font-size: 11.5px;
  display: flex; align-items: center; gap: 6px;
}
.ops-shell .pm-policy-actions {
  display: flex; justify-content: flex-end;
}

/* 정책 수정 확인 모달 */
.ops-shell .pm-policy-modal { max-width: 500px; }
.ops-shell .pm-policy-confirm-body { padding: 16px 20px; }
.ops-shell .pm-policy-confirm-body .cm-row {
  padding: 8px 0; border-bottom: 1px solid #f1f4f8;
  display: flex; justify-content: space-between; align-items: center;
}
.ops-shell .pm-policy-confirm-body .cm-row:last-of-type { border-bottom: 0; }
.ops-shell .pm-policy-confirm-note {
  margin: 12px 0;
  padding: 10px 12px;
  background: rgba(217,119,6,0.08);
  border-left: 3px solid #d97706;
  color: #92400e;
  font-size: 12.5px;
  border-radius: 0 6px 6px 0;
}

@media (max-width: 1200px) {
  .ops-shell .pm-policy-grid { grid-template-columns: 1fr; }
  .ops-shell .pm-policy-fields { grid-template-columns: 1fr; }
}

/* ====== fault 목록 필터 ====== */
.ops-shell .pm-fault-filter {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  padding: 10px 0; margin-bottom: 8px;
  border-bottom: 1px solid #e3e9f1;
}
.ops-shell .pm-fault-filter select {
  padding: 5px 10px;
  border: 1px solid #c9d4e3; border-radius: 5px;
  background: #ffffff; color: #0c1f40;
  font-family: inherit; font-size: 12px;
}
.ops-shell .pm-fault-flag {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px; color: #4a5b78; font-weight: 600;
  background: #f4f7fb; padding: 5px 10px; border-radius: 5px;
  border: 1px solid #c9d4e3; cursor: pointer;
}
.ops-shell .pm-fault-flag input { cursor: pointer; }

/* cams 탭 정렬 셀렉트 */
.ops-shell .pnl-sort {
  padding: 6px 10px;
  border: 1px solid #c9d4e3; border-radius: 6px;
  background: #ffffff; color: #0c1f40;
  font-family: inherit; font-size: 12px;
  cursor: pointer;
}

/* dataSource 행 (status 탭 상단) */
.ops-shell .pm-ds-row {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 10px; flex-shrink: 0;
  flex-wrap: wrap;
}
.ops-shell .pm-ds-lab {
  font-size: 12px; font-weight: 600; color: #64748b;
  display: inline-flex; align-items: center; gap: 6px;
}
.ops-shell .pm-ds-lab > i { color: #2563eb; }
.ops-shell .pm-ds-sel {
  padding: 6px 12px;
  border: 1px solid #c9d4e3; border-radius: 6px;
  background: #ffffff; color: #0c1f40;
  font-family: inherit; font-size: 12.5px;
}
.ops-shell .pm-ds-bdg {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 6px;
  font-size: 11.5px; font-weight: 600;
}
.ops-shell .pm-ds-bdg.yl { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
.ops-shell .pm-ds-bdg.rd { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.ops-shell .pm-ds-bdg.gy { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

/* 활성 이상 통계 지표 4박스 (z-score / slope / confidence / detector) */
.ops-shell .pm-stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
  margin-bottom: 20px;
}
.ops-shell .pm-stat {
  background: #fafbfd;
  border: 1px solid #eaeef5;
  border-radius: 10px;
  padding: 12px 14px;
}
.ops-shell .pm-stat-l {
  font-size: 10.5px; font-weight: 600; color: #64748b;
  letter-spacing: 0.04em; text-transform: uppercase;
}
.ops-shell .pm-stat-v {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700; font-size: 22px;
  color: #0c1f40;
  margin: 4px 0 2px;
  line-height: 1.1;
}
.ops-shell .pm-stat-v > small { font-size: 11.5px; font-weight: 500; color: #94a3b8; margin-left: 2px; }
.ops-shell .pm-stat-v.rd { color: #dc2626; }
.ops-shell .pm-stat-v.yl { color: #d97706; }
.ops-shell .pm-stat-v.gr { color: #059669; }
.ops-shell .pm-stat-v.gy { color: #94a3b8; }
.ops-shell .pm-stat-s {
  font-size: 11px; color: #64748b;
}
.ops-shell .pm-stat-det .pm-stat-det-name {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px; font-weight: 600; color: #0c1f40;
  word-break: break-word; line-height: 1.3;
}
@media (max-width: 1200px) {
  .ops-shell .pm-stats-row { grid-template-columns: repeat(2, 1fr); }
}

/* 메트릭 미니 sparkline */
.ops-shell .cm-pm-mtx-row {
  display: flex; flex-direction: column; gap: 4px;
}
.ops-shell .cm-pm-mtx-head {
  display: flex; flex-direction: column; gap: 2px;
}
.ops-shell .cm-pm-mtx-svg {
  width: 100%; height: 32px;
  display: block;
  margin-top: 4px;
}

/* 정책 입력 에러 표시 */
.ops-shell .pm-field.err > input { border-color: #dc2626 !important; background: #fef2f2; }
.ops-shell .pm-policy-err {
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 8px 12px;
  color: #dc2626; font-size: 12px;
  display: flex; align-items: center; gap: 6px;
}
.ops-shell .pm-policy-extra {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 10px;
  background: #f4f7fb;
  border-radius: 8px;
  border-left: 3px solid #7c3aed;
}
.ops-shell .pm-policy-extra .pm-field { font-size: 11.5px; }
@media (max-width: 900px) {
  .ops-shell .pm-policy-extra { grid-template-columns: 1fr; }
}

/* ====== 연결된 정비 티켓 ====== */
.ops-shell .pm-linked-ticket {
  display: flex; align-items: center; gap: 8px;
  background: #eef4ff;
  border: 1px solid #c9dcff;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 12.5px;
}
.ops-shell .pm-linked-ticket > i { color: #2563eb; font-size: 14px; }
.ops-shell .pm-linked-l { color: #4a5b78; font-weight: 600; }
.ops-shell .pm-linked-ticket > strong {
  font-family: 'JetBrains Mono', monospace;
  color: #0c1f40; font-size: 12px;
}
.ops-shell .pm-linked-sla {
  margin-left: auto; font-size: 11px; color: #4a5b78;
}
.ops-shell .pm-linked-ticket.none {
  background: #f4f7fb; border-color: #e3e9f1;
  color: #6b7280; font-size: 12px;
}
.ops-shell .pm-linked-ticket.none > i { color: #9aa6b8; }

/* BASELINE_LEARNING 표시 (Health 컬럼) */
.ops-shell .pm-baseline {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(124,58,237,0.12);
  color: #7c3aed;
  padding: 2px 8px; border-radius: 100px;
  font-size: 11px; font-weight: 700;
}
.ops-shell .pm-baseline > i { font-size: 10px; }
.ops-shell .cm-pm-baseline-bdg {
  margin-left: 6px;
  padding: 2px 10px; border-radius: 100px;
  background: rgba(124,58,237,0.12);
  color: #7c3aed;
  font-size: 11px; font-weight: 800;
  display: inline-flex; align-items: center; gap: 4px;
}
.ops-shell .cm-pm-baseline-bdg > i { font-size: 10px; }
.ops-shell .cm-pm-baseline-card {
  background: #ffffff;
  border: 1px solid rgba(124,58,237,0.25);
  border-left: 3px solid #7c3aed;
  border-radius: 8px;
  padding: 14px 16px;
}
.ops-shell .cm-pm-baseline-l {
  font-size: 13px; color: #4a5b78; margin-bottom: 10px;
}
.ops-shell .cm-pm-baseline-bar {
  height: 10px;
  background: rgba(124,58,237,0.1);
  border-radius: 100px;
  overflow: hidden;
  margin-bottom: 8px;
}
.ops-shell .cm-pm-baseline-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #2563eb);
  border-radius: 100px;
  transition: width .3s;
}
.ops-shell .cm-pm-baseline-stat {
  font-size: 13px; color: #0c1f40;
  font-family: 'JetBrains Mono', monospace;
}
.ops-shell .cm-pm-baseline-stat > strong { color: #7c3aed; font-size: 16px; }
.ops-shell .cm-pm-baseline-sub {
  margin-left: 6px;
  font-family: 'Inter', sans-serif;
  font-size: 11.5px; color: #6b7280; font-weight: 500;
}

/* 교통 맥락 교차검증 — 부드러운 카드 */
.ops-shell .pm-traffic {
  background: #fafbfd;
  border: 1px solid #eaeef5;
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 20px;
}
.ops-shell .pm-traffic-h {
  display: flex; align-items: center; gap: 10px;
  font-size: 13px; color: #64748b;
  margin-bottom: 14px;
}
.ops-shell .pm-traffic-h > i { color: #2563eb; font-size: 15px; }
.ops-shell .pm-traffic-h > strong { color: #0c1f40; font-size: 14px; font-weight: 600; letter-spacing: -0.01em; }
.ops-shell .pm-traffic-jd {
  margin-left: auto;
  padding: 3px 10px; border-radius: 6px;
  font-size: 10.5px; font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.ops-shell .pm-traffic-jd.rd { background: #fef2f2; color: #dc2626; }
.ops-shell .pm-traffic-jd.yl { background: #fffbeb; color: #d97706; }
.ops-shell .pm-traffic-jd.gr { background: #ecfdf5; color: #059669; }
.ops-shell .pm-traffic-jd.gy { background: #f1f5f9; color: #64748b; }

.ops-shell .pm-traffic-body {
  display: grid; grid-template-columns: 1fr 24px 1fr; gap: 12px;
  align-items: center; margin-bottom: 8px;
}
.ops-shell .pm-traffic-self,
.ops-shell .pm-traffic-adj {
  background: #ffffff;
  border-radius: 6px;
  padding: 8px 12px;
}
.ops-shell .pm-traffic-l {
  font-size: 10.5px; color: #4a5b78; font-weight: 700;
  letter-spacing: 0.04em; margin-bottom: 2px;
}
.ops-shell .pm-traffic-v {
  font-family: 'JetBrains Mono', monospace;
  display: flex; align-items: baseline; gap: 4px;
}
.ops-shell .pm-traffic-v > strong { font-size: 20px; color: #0c1f40; font-weight: 800; }
.ops-shell .pm-traffic-sub { font-size: 11.5px; color: #4a5b78; }
.ops-shell .pm-traffic-arr {
  color: #9aa6b8; font-size: 16px; text-align: center;
}
.ops-shell .pm-traffic-note {
  font-size: 11.5px; color: #4a5b78;
  background: rgba(37,99,235,0.06);
  padding: 6px 10px; border-radius: 5px;
  border-left: 2px solid #2563eb;
}

/* 티켓 변경 이력 timeline (모달 내부) */
.ops-shell .pm-ticket-modal-wide { max-width: 580px; }
/* 티켓·이상 모달 본문이 viewport보다 길어지면 내부 스크롤 */
.ops-shell .pm-ticket-modal .pm-ticket-body {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}
.ops-shell .pm-ticket-modal .pm-ticket-acts {
  position: sticky;
  bottom: 0;
  background: #ffffff;
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #f1f4f8;
  z-index: 1;
}
.ops-shell .pm-policy-modal .pm-policy-confirm-body {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
}
.ops-shell .pm-ticket-timeline {
  margin-top: 14px;
  background: #f4f7fb;
  border-radius: 8px;
  padding: 12px 14px;
}
.ops-shell .pm-tl-h {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; font-weight: 700; color: #4a5b78;
  margin-bottom: 10px;
}
.ops-shell .pm-tl-h > i { color: #2563eb; }
.ops-shell .pm-tl-cnt {
  margin-left: auto;
  font-size: 10.5px; color: #6b7280;
  background: #ffffff;
  padding: 1px 8px; border-radius: 100px;
  font-weight: 600;
}
.ops-shell .pm-tl-list {
  position: relative;
  padding-left: 4px;
}
.ops-shell .pm-tl-list::before {
  content: "";
  position: absolute;
  left: 9px; top: 6px; bottom: 6px;
  width: 1px;
  background: #c9d4e3;
}
.ops-shell .pm-tl-row {
  position: relative;
  display: flex; gap: 12px;
  padding: 6px 0;
}
.ops-shell .pm-tl-dot {
  width: 12px; height: 12px;
  border-radius: 50%;
  background: #c9d4e3;
  border: 2px solid #ffffff;
  z-index: 1;
  margin-top: 4px;
  flex-shrink: 0;
}
.ops-shell .pm-tl-dot.create   { background: #6b7280; }
.ops-shell .pm-tl-dot.assign   { background: #2563eb; }
.ops-shell .pm-tl-dot.progress { background: #d97706; }
.ops-shell .pm-tl-dot.resolve  { background: #059669; }
.ops-shell .pm-tl-dot.close    { background: #0c1f40; }
.ops-shell .pm-tl-body { flex: 1; min-width: 0; }
.ops-shell .pm-tl-line {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: #0c1f40;
}
.ops-shell .pm-tl-line > strong { font-weight: 700; }
.ops-shell .pm-tl-from-to {
  font-size: 11px; color: #6b7280;
  background: #ffffff;
  padding: 1px 7px; border-radius: 100px;
  font-family: 'JetBrains Mono', monospace;
}
.ops-shell .pm-tl-meta {
  font-size: 11px; color: #6b7280;
  margin-top: 2px;
}
.ops-shell .pm-tl-meta .mono { font-family: 'JetBrains Mono', monospace; }
.ops-shell .pm-tl-note {
  font-size: 11.5px; color: #4a5b78;
  background: #ffffff;
  padding: 5px 10px;
  border-radius: 5px;
  margin-top: 4px;
  border-left: 2px solid #c9d4e3;
}

/* anomaly modal select */
.ops-shell .pm-ticket-note select {
  width: 100%; padding: 8px 10px;
  border: 1px solid #c9d4e3; border-radius: 6px;
  background: #ffffff; color: #0c1f40;
  font-family: inherit; font-size: 13px;
}
</style>
