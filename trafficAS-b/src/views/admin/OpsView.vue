<template>
  <div class="ops-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen">
          Traffic <em>AS</em>
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
        <h1><a class="t-sub t-main" @click="goHome">시설운영팀</a></h1>
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
          <DeptSwitcher />
          <div class="t-user">
            <i class="bi bi-person-circle"></i> 시설운영팀 매니저
            <i class="bi bi-chevron-down"></i>
          </div>
        </div>
      </header>

      <template v-if="tab === 'status'">
        <!-- ============ 메인 그리드 (좌 2x2 + 우 풀세로 장애상세) ============ -->
        <section class="main-grid">
          <!-- 네트워크 지연 (top-left, 위치 변경) -->
          <div class="card net-card">
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

          <!-- 서버 상태 (3 cards with CPU/메모리/디스크/서비스 bars) -->
          <div class="card srv-card">
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
                <i class="bi bi-arrows-fullscreen"></i>
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
              <a class="ch-link" @click="tab = 'fault'">전체 보기 ›</a>
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
              <table class="cam-tbl">
                <thead>
                  <tr>
                    <th>카메라명</th>
                    <th>상태</th>
                    <th>지연(ms)</th>
                    <th>최근 응답</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="(c, i) in cams.slice(0, 3)"
                    :key="i"
                    :class="{ bad: c.st === '장애' }"
                    @click="openCam(c)"
                    style="cursor: pointer"
                  >
                    <td><i class="bi bi-camera-video"></i> {{ c.name }}</td>
                    <td>
                      <span class="stat" :class="c.stTone">{{ c.st }}</span>
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

        <!-- 상단 KPI 7박스 -->
        <div class="pnl-summary nd-kpi nd-kpi-7">
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
        </div>

        <!-- 위치별 분포 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>위치별 분포</h4>
            <span class="nd-h-cnt">6개 구역</span>
          </div>
          <div class="cd-zones">
            <div class="cdz" v-for="z in camZones" :key="z.name">
              <div class="cdz-h">
                <span class="cdz-n">{{ z.name }}</span>
                <span class="cdz-c"
                  ><strong>{{ z.ok + z.warn + z.bad }}</strong
                  ><em>대</em></span
                >
              </div>
              <div class="cdz-bar">
                <span class="gr" :style="{ flex: z.ok }"></span>
                <span class="yl" :style="{ flex: z.warn }"></span>
                <span class="rd" :style="{ flex: z.bad }"></span>
              </div>
              <div class="cdz-leg">
                <span><span class="ns-d gr"></span>{{ z.ok }}</span>
                <span><span class="ns-d yl"></span>{{ z.warn }}</span>
                <span><span class="ns-d rd"></span>{{ z.bad }}</span>
              </div>
            </div>
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
                <td><i class="bi bi-camera-video"></i> {{ c.name }}</td>
                <td>{{ c.loc }}</td>
                <td class="mono">10.20.{{ 10 + i }}.{{ 100 + i }}</td>
                <td>
                  <span class="stat" :class="c.stTone">{{ c.st }}</span>
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
                <td colspan="12" class="pnl-empty">검색 결과 없음</td>
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

        <!-- 최근 카메라 이벤트 -->
        <div class="nd-block">
          <div class="nd-h"><h4>최근 카메라 이벤트</h4></div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>발생 시각</th>
                <th>장비 ID</th>
                <th>이벤트</th>
                <th>심각도</th>
                <th>지속 시간</th>
                <th>담당자</th>
                <th>조치</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="mono">14:24:17</td>
                <td class="mono">CAM-M-002</td>
                <td>오프라인 (RTSP timeout)</td>
                <td><span class="stat no">CRIT</span></td>
                <td class="mono rd-txt">8분 1초</td>
                <td>김기사</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">14:11:42</td>
                <td class="mono">CAM-J-007</td>
                <td>지연 286ms 임계 초과</td>
                <td><span class="stat wn">HIGH</span></td>
                <td class="mono yl-txt">20분 36초</td>
                <td>자동</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">13:55:18</td>
                <td class="mono">CAM-IC-0011</td>
                <td>연결 복구 완료 (재기동)</td>
                <td><span class="stat ok">INFO</span></td>
                <td class="mono">—</td>
                <td>이대리</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
              <tr>
                <td class="mono">12:48:22</td>
                <td class="mono">GBN-S-0032</td>
                <td>이미지 노이즈 임계 초과</td>
                <td><span class="stat wn">MED</span></td>
                <td class="mono">1시간 44분</td>
                <td>자동</td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
            </tbody>
          </table>
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

      <section v-if="tab === 'fault'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>장애 관리 <span class="ch-kpi rd">진행 1 · 처리중 2 · 완료 5</span></h3>
          <div class="pnl-tools">
            <button class="pnl-act">
              <i class="bi bi-plus-circle"></i> 장애 신규 등록
            </button>
            <button class="pnl-act"><i class="bi bi-download"></i> CSV</button>
          </div>
        </div>

        <!-- KPI 8박스 (MTTR/MTBF 포함) -->
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
          <div class="ps-box">
            <div class="ps-l">MTTR</div>
            <div class="ps-v">18<span>분</span></div>
            <div class="ps-sub">평균 복구</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">최장 지연</div>
            <div class="ps-v">2<span>h 14m</span></div>
            <div class="ps-sub">CAM-M-002</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">MTBF</div>
            <div class="ps-v">7.2<span>일</span></div>
            <div class="ps-sub">장애 간 평균</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">자동 복구율</div>
            <div class="ps-v">73<span>%</span></div>
            <div class="ps-sub">최근 7일</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">미해결 SLA</div>
            <div class="ps-v">1</div>
            <div class="ps-sub">15분 초과</div>
          </div>
        </div>

        <!-- 현재 진행 중인 장애 (큰 강조 카드) -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>현재 진행 중 장애</h4>
            <span class="nd-h-cnt rd-txt">우선 대응 필요</span>
          </div>
          <div class="fl-cur">
            <div class="flc-h">
              <div class="flc-id">
                <span class="stat no">CRIT</span>
                <strong>FLT-2025-0517-014</strong>
                <span class="flc-dev">CAM-M-002 (마포대로)</span>
              </div>
              <div class="flc-time">
                <span class="flc-l">경과</span>
                <strong class="rd-txt">8분 1초</strong>
              </div>
            </div>
            <div class="flc-body">
              <div class="flc-row"><span>발생 시각</span><strong>14:24:17</strong></div>
              <div class="flc-row">
                <span>증상</span><strong>RTSP 스트림 응답 없음 (timeout 30s)</strong>
              </div>
              <div class="flc-row">
                <span>예상 원인</span><strong>광케이블 단선 (NSN-N-0023 연동)</strong>
              </div>
              <div class="flc-row">
                <span>영향 범위</span><strong>마포대교 2개 차로 영상 수집 중단</strong>
              </div>
              <div class="flc-row">
                <span>담당자</span><strong>김기사 (현장 출동 중, 도착 예정 14:45)</strong>
              </div>
              <div class="flc-row">
                <span>SLA 마감</span><strong class="rd-txt">14:39 (5분 후 초과)</strong>
              </div>
            </div>
            <div class="flc-progress">
              <div class="flc-step done"><span>1</span>알람 발생</div>
              <div class="flc-step done"><span>2</span>담당자 배정</div>
              <div class="flc-step on"><span>3</span>현장 출동</div>
              <div class="flc-step"><span>4</span>원인 식별</div>
              <div class="flc-step"><span>5</span>복구 작업</div>
              <div class="flc-step"><span>6</span>완료 확인</div>
            </div>
            <div class="flc-acts">
              <button class="pnl-act"><i class="bi bi-share"></i> 담당자 변경</button>
              <button class="pnl-act">
                <i class="bi bi-arrow-clockwise"></i> 재시도
              </button>
              <button class="pnl-act">
                <i class="bi bi-clipboard-data"></i> 작업 로그
              </button>
              <button class="pnl-act">
                <i class="bi bi-check2-circle"></i> 복구 완료
              </button>
            </div>
          </div>
        </div>

        <!-- 장애 유형 분포 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>장애 유형 분포 (최근 7일)</h4>
            <span class="nd-h-cnt">총 21건</span>
          </div>
          <div class="cd-zones">
            <div class="cdz" v-for="t in faultTypes" :key="t.name">
              <div class="cdz-h">
                <span class="cdz-n">{{ t.name }}</span>
                <span class="cdz-c"
                  ><strong>{{ t.count }}</strong
                  ><em>건</em></span
                >
              </div>
              <div class="cdz-bar">
                <span class="rd" :style="{ flex: t.ongoing }"></span>
                <span class="gr" :style="{ flex: t.count - t.ongoing }"></span>
              </div>
              <div class="cdz-leg">
                <span><span class="ns-d rd"></span>{{ t.ongoing }}</span>
                <span><span class="ns-d gr"></span>{{ t.count - t.ongoing }} 복구</span>
                <span style="color: #6b7a92">{{ t.mttr }}분</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 전체 장애 목록 -->
        <div class="nd-block">
          <div class="nd-h">
            <h4>전체 장애 목록</h4>
            <span class="nd-h-cnt">{{ faults.length }}건</span>
          </div>
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>장애 ID</th>
                <th>발생 시각</th>
                <th>장비</th>
                <th>증상</th>
                <th>심각도</th>
                <th>담당자</th>
                <th>경과</th>
                <th>상태</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="f in faults" :key="f.id">
                <td class="mono">{{ f.id }}</td>
                <td class="mono">{{ f.time }}</td>
                <td class="mono">{{ f.dev }}</td>
                <td>{{ f.symp }}</td>
                <td>
                  <span class="stat" :class="f.tone">{{ f.sev }}</span>
                </td>
                <td>{{ f.who }}</td>
                <td
                  class="mono"
                  :class="
                    f.stTone === 'no' ? 'rd-txt' : f.stTone === 'wn' ? 'yl-txt' : ''
                  "
                >
                  {{ f.elapsed }}
                </td>
                <td>
                  <span class="stat" :class="f.stTone">{{ f.st }}</span>
                </td>
                <td><button class="pnl-act sm">상세</button></td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
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
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import SideWeather from "@/components/dashboard/SideWeather.vue";
import { INITIAL_DISTRICTS_WEATHER, DISTRICT_LIST } from "@/data/weather";

const tab = ref("status");
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
const camQuery = ref("");
const camSt = ref("all");
const filteredCams = computed(() => {
  const q = camQuery.value.trim().toLowerCase();
  return cams.filter((c) => {
    if (camSt.value !== "all" && c.st !== camSt.value) return false;
    if (!q) return true;
    return (
      c.name.toLowerCase().includes(q) ||
      c.id.toLowerCase().includes(q) ||
      c.loc.toLowerCase().includes(q)
    );
  });
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
  },
]);

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
onMounted(() => {
  nowTimer = setInterval(() => {
    nowSec.value += 1;
  }, 1000);
});
onBeforeUnmount(() => {
  if (nowTimer) clearInterval(nowTimer);
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
  { id: "alarm", icon: "bi bi-bell", label: "알람/이벤트", bdg: 3 },
  { id: "fault", icon: "bi bi-exclamation-triangle", label: "장애 관리", bdg: 3 },
];

const cams = Object.freeze([
  {
    name: "한남대교_남단_A4",
    loc: "강변북로 09K+200",
    st: "정상",
    stTone: "ok",
    lat: 94,
    ts: "10:32:18",
    id: "GBN-S-0032",
  },
  {
    name: "가양IC_본선_C2",
    loc: "올림픽대로 14K+800",
    st: "정상",
    stTone: "ok",
    lat: 96,
    ts: "10:32:17",
    id: "OLP-W-0041",
  },
  {
    name: "정릉터널_입구_B1",
    loc: "내부순환로 03K+150",
    st: "장애",
    stTone: "no",
    lat: "—",
    ts: "10:24:17",
    id: "NSN-N-0023",
  },
]);

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
