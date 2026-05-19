<template>
  <div class="ops-shell" :class="{ 'side-collapsed': !sideOpen }">
    <aside class="side">
      <div class="side-top">
        <RouterLink to="/" class="brand" v-if="sideOpen">
          <span class="dot"></span> Traffic <em>AS</em>
        </RouterLink>
        <button
          class="side-toggle"
          @click="sideOpen = !sideOpen"
          :aria-label="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
          :title="sideOpen ? '접기' : '펼치기'"
        >
          <i
            :class="sideOpen ? 'bi bi-chevron-double-left' : 'bi bi-chevron-double-right'"
          ></i>
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

      <section v-if="tab === 'check'" class="card pnl">
        <div class="pnl-head">
          <h3>점검 관리 <span class="ch-kpi">예정 4 · 완료 12 · 지연 1</span></h3>
        </div>
        <div class="pnl-summary">
          <div class="ps-box">
            <div class="ps-l">예정 (이번 주)</div>
            <div class="ps-v">4</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">완료 (이번 달)</div>
            <div class="ps-v">12</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">지연</div>
            <div class="ps-v">1</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 소요</div>
            <div class="ps-v">38<span>분</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">담당자</div>
            <div class="ps-v">5<span>명</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">다음 점검</div>
            <div class="ps-v" style="font-size: 17px">05-19 02:00</div>
          </div>
        </div>
        <table class="pnl-tbl">
          <thead>
            <tr>
              <th>예정일시</th>
              <th>점검 유형</th>
              <th>대상 장비</th>
              <th>담당자</th>
              <th>예상 소요</th>
              <th>영향 범위</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in checksExt" :key="c.id">
              <td class="mono">{{ c.date }}</td>
              <td>{{ c.type }}</td>
              <td class="mono">{{ c.dev }}</td>
              <td>{{ c.who }}</td>
              <td class="mono">{{ c.dur }}</td>
              <td>{{ c.scope }}</td>
              <td>
                <span class="stat" :class="c.tone">{{ c.st }}</span>
              </td>
            </tr>
          </tbody>
        </table>
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

        <div v-if="faultMsg" class="set-msg">{{ faultMsg }}</div>
      </section>

      <section v-if="tab === 'reports'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>
            장비 보고서 <span class="ch-kpi">{{ reportRows.length }}개 보고서</span>
          </h3>
        </div>
        <div class="nd-block">
          <table class="pnl-tbl nd-tbl">
            <thead>
              <tr>
                <th>보고서명</th>
                <th>설명</th>
                <th>기간</th>
                <th>크기</th>
                <th>형식</th>
                <th>다운로드</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in reportRows" :key="r.id">
                <td>
                  <i class="bi bi-file-earmark-text" style="color: #2563eb"></i>
                  <strong>{{ r.t }}</strong>
                </td>
                <td>{{ r.d }}</td>
                <td class="mono">{{ r.period }}</td>
                <td class="mono">{{ r.size }}</td>
                <td class="mono">{{ r.fmt }}</td>
                <td>
                  <button class="pnl-act sm" @click="downloadReport(r)">
                    <i class="bi bi-download"></i> 다운로드
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="faultMsg" class="set-msg">{{ faultMsg }}</div>
      </section>

      <section v-if="tab === 'settings'" class="card pnl net-detail">
        <div class="pnl-head">
          <h3>설정</h3>
          <div class="pnl-tools">
            <button class="pnl-act" @click="resetSet">
              <i class="bi bi-arrow-counterclockwise"></i> 기본값 복원
            </button>
            <button class="pnl-act"><i class="bi bi-download"></i> 설정 내보내기</button>
          </div>
        </div>

        <!-- 1. 모니터링 / 알림 임계값 -->
        <div class="nd-block">
          <div class="nd-h"><h4>모니터링 / 알림 임계값</h4></div>
          <div class="set-grid">
            <div class="set-it">
              <label>지연 경고 임계 (ms)</label>
              <input type="number" v-model.number="setLatThreshold" min="50" max="1000" />
              <span class="set-h">200 이상 시 HIGH 알람</span>
            </div>
            <div class="set-it">
              <label>지연 위험 임계 (ms)</label>
              <input type="number" v-model.number="setLatCritical" min="100" max="2000" />
              <span class="set-h">초과 시 CRIT 알람</span>
            </div>
            <div class="set-it">
              <label>패킷 손실 임계 (%)</label>
              <input
                type="number"
                v-model.number="setLossThreshold"
                min="0"
                max="100"
                step="0.1"
              />
              <span class="set-h">초과 시 HIGH 알람</span>
            </div>
            <div class="set-it">
              <label>CPU 임계 (%)</label>
              <input type="number" v-model.number="setCpuThreshold" min="50" max="100" />
              <span class="set-h">초과 시 서버 경고</span>
            </div>
            <div class="set-it">
              <label>메모리 임계 (%)</label>
              <input type="number" v-model.number="setMemThreshold" min="50" max="100" />
              <span class="set-h">초과 시 서버 경고</span>
            </div>
            <div class="set-it">
              <label>디스크 임계 (%)</label>
              <input type="number" v-model.number="setDiskThreshold" min="60" max="100" />
              <span class="set-h">초과 시 서버 경고</span>
            </div>
          </div>
        </div>

        <!-- 2. 알림 / 통보 -->
        <div class="nd-block">
          <div class="nd-h"><h4>알림 / 통보</h4></div>
          <div class="set-grid">
            <div class="set-it">
              <label>주 알림 채널</label>
              <select v-model="setChannel">
                <option>이메일</option>
                <option>SMS</option>
                <option>슬랙</option>
                <option>카카오워크</option>
              </select>
              <span class="set-h">{{ setChannelTarget }}</span>
            </div>
            <div class="set-it">
              <label>중복 알림 억제 (분)</label>
              <input type="number" v-model.number="setDedup" min="1" max="60" />
              <span class="set-h">동일 알람 재발송 차단</span>
            </div>
            <div class="set-it set-toggle">
              <label>야간 모드 (22:00~07:00)</label>
              <input type="checkbox" v-model="setNightMode" />
              <span class="set-h">CRIT만 알림, 나머지 보류</span>
            </div>
            <div class="set-it set-toggle">
              <label>이메일 일일 요약</label>
              <input type="checkbox" v-model="setDailyDigest" />
              <span class="set-h">매일 08:00 발송</span>
            </div>
            <div class="set-it set-toggle">
              <label>SMS 긴급 통보 (CRIT)</label>
              <input type="checkbox" v-model="setSmsCrit" />
              <span class="set-h">담당자 + 백업 담당자</span>
            </div>
            <div class="set-it set-toggle">
              <label>슬랙 자동 전달</label>
              <input type="checkbox" v-model="setSlackForward" />
              <span class="set-h">#ops-alarm 채널</span>
            </div>
          </div>
        </div>

        <!-- 3. 자동 처리 -->
        <div class="nd-block">
          <div class="nd-h"><h4>자동 처리</h4></div>
          <div class="set-grid">
            <div class="set-it set-toggle">
              <label>자동 재연결 시도</label>
              <input type="checkbox" v-model="setAutoReconnect" />
              <span class="set-h">RTSP timeout 시 자동 재접속</span>
            </div>
            <div class="set-it">
              <label>재연결 재시도 (회)</label>
              <input type="number" v-model.number="setRetryCount" min="1" max="10" />
              <span class="set-h">실패 시 알람 발생</span>
            </div>
            <div class="set-it">
              <label>재연결 간격 (초)</label>
              <input type="number" v-model.number="setRetryInterval" min="5" max="300" />
              <span class="set-h">재시도 사이 대기</span>
            </div>
            <div class="set-it set-toggle">
              <label>장애 자동 등록</label>
              <input type="checkbox" v-model="setAutoFault" />
              <span class="set-h">CRIT 알람 → 장애 티켓</span>
            </div>
            <div class="set-it set-toggle">
              <label>로그 자동 로테이트</label>
              <input type="checkbox" v-model="setAutoRotate" />
              <span class="set-h">매일 02:00, 30일 보존</span>
            </div>
            <div class="set-it set-toggle">
              <label>이상 시 자동 격리</label>
              <input type="checkbox" v-model="setQuarantine" />
              <span class="set-h">패킷 손실 50% 초과 시</span>
            </div>
          </div>
        </div>

        <!-- 4. 점검 / 백업 -->
        <div class="nd-block">
          <div class="nd-h"><h4>점검 / 백업</h4></div>
          <div class="set-grid">
            <div class="set-it">
              <label>정기 점검 주기</label>
              <select v-model="setCheckCycle">
                <option>매주</option>
                <option>격주</option>
                <option>매월</option>
              </select>
              <span class="set-h">자동 일정 생성</span>
            </div>
            <div class="set-it">
              <label>점검 시간대</label>
              <select v-model="setCheckTime">
                <option>02:00 ~ 04:00</option>
                <option>03:00 ~ 05:00</option>
                <option>04:00 ~ 06:00</option>
              </select>
              <span class="set-h">새벽 트래픽 최저 시간</span>
            </div>
            <div class="set-it">
              <label>백업 보존 기간 (일)</label>
              <input type="number" v-model.number="setBackupDays" min="7" max="365" />
              <span class="set-h">초과분 자동 삭제</span>
            </div>
            <div class="set-it set-toggle">
              <label>자동 백업</label>
              <input type="checkbox" v-model="setAutoBackup" />
              <span class="set-h">매일 03:00 풀백업</span>
            </div>
          </div>
        </div>

        <!-- 5. 보안 / 권한 -->
        <div class="nd-block">
          <div class="nd-h"><h4>보안 / 권한</h4></div>
          <div class="set-grid">
            <div class="set-it set-toggle">
              <label>2단계 인증 (MFA)</label>
              <input type="checkbox" v-model="setMfa" />
              <span class="set-h">관리자 계정 강제</span>
            </div>
            <div class="set-it">
              <label>세션 만료 (분)</label>
              <input
                type="number"
                v-model.number="setSessionTimeout"
                min="10"
                max="480"
              />
              <span class="set-h">미사용 자동 로그아웃</span>
            </div>
            <div class="set-it">
              <label>로그인 시도 제한</label>
              <input type="number" v-model.number="setLoginAttempts" min="3" max="10" />
              <span class="set-h">초과 시 계정 잠금</span>
            </div>
            <div class="set-it set-toggle">
              <label>감사 로그 기록</label>
              <input type="checkbox" v-model="setAuditLog" />
              <span class="set-h">모든 관리자 액션 기록</span>
            </div>
          </div>
        </div>

        <!-- 저장 액션 -->
        <div class="set-actions">
          <button class="btn-save" @click="saveSet">
            <i class="bi bi-check2"></i> 변경 사항 저장
          </button>
          <span v-if="setMsg" class="set-msg" style="margin: 0 0 0 12px">{{
            setMsg
          }}</span>
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

const tab = ref("status");
const autoRefresh = ref(true);
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
const netGrid = Object.freeze([
  { id: "CAM-K-014", ms: 78, tone: "gr" },
  { id: "CAM-K-015", ms: 82, tone: "gr" },
  { id: "CAM-O-011", ms: 91, tone: "gr" },
]);

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

const checksExt = Object.freeze([
  {
    id: 1,
    date: "2026-05-19 02:00",
    type: "정기",
    dev: "ocr-srv-01",
    who: "김기사",
    dur: "30분",
    scope: "OCR 서비스 일시 중단",
    st: "예정",
    tone: "wait",
  },
  {
    id: 2,
    date: "2026-05-20 01:00",
    type: "정기",
    dev: "DB-PRIMARY",
    who: "이대리",
    dur: "60분",
    scope: "전체 서비스 영향 없음",
    st: "예정",
    tone: "wait",
  },
  {
    id: 3,
    date: "2026-05-22 03:00",
    type: "정기",
    dev: "NET-CORE-1",
    who: "박과장",
    dur: "45분",
    scope: "네트워크 30초 단절",
    st: "예정",
    tone: "wait",
  },
]);

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
  { id: "check", icon: "bi bi-clipboard-check", label: "점검 관리" },
  { id: "fault", icon: "bi bi-exclamation-triangle", label: "장애 관리", bdg: 3 },
  { id: "reports", icon: "bi bi-file-earmark", label: "보고서" },
  { id: "settings", icon: "bi bi-gear", label: "설정" },
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

const alarms = Object.freeze([
  {
    id: 1,
    time: "10:24:17",
    dev: "CAM-IC-0032",
    sev: "장애",
    tone: "no",
    msg: "스트림 응답 없음",
  },
  {
    id: 2,
    time: "10:18:55",
    dev: "OCR-SRV-2",
    sev: "경고",
    tone: "wn",
    msg: "디스크 사용량 78%",
  },
  {
    id: 3,
    time: "09:55:12",
    dev: "CAM-IC-0077",
    sev: "경고",
    tone: "wn",
    msg: "지연 286ms 초과",
  },
]);
const checks = Object.freeze([
  {
    id: 1,
    date: "2026-05-18",
    dev: "CAM-IC-0032",
    type: "정기",
    who: "장비운영팀",
    st: "예정",
    tone: "wn",
  },
  {
    id: 2,
    date: "2026-05-20",
    dev: "OCR-SRV-1",
    type: "정기",
    who: "서버팀",
    st: "예정",
    tone: "wn",
  },
  {
    id: 3,
    date: "2026-05-15",
    dev: "검색 서버",
    type: "임시",
    who: "서버팀",
    st: "완료",
    tone: "ok",
  },
]);
const reportRows = Object.freeze([
  {
    id: "cams",
    t: "장비 가동률 보고서",
    d: "카메라 25대 24시간 가동률·OCR 신뢰도",
    period: "2026-05-17",
    size: "1.8MB",
    fmt: "CSV",
  },
  {
    id: "faults",
    t: "장애 발생 이력",
    d: "최근 30일 장애 21건 · MTTR·MTBF 분석",
    period: "2026-04-17 ~ 2026-05-17",
    size: "3.2MB",
    fmt: "CSV",
  },
  {
    id: "net",
    t: "네트워크 지연 분석",
    d: "경로 25개 RTT·패킷손실·업타임 주간 추이",
    period: "2026-05-11 ~ 2026-05-17",
    size: "2.4MB",
    fmt: "CSV",
  },
]);

// CSV 생성 + 다운로드 트리거
function buildCsv(rows) {
  return rows
    .map((r) =>
      r
        .map((v) => {
          const s = String(v ?? "");
          return /[,"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
        })
        .join(",")
    )
    .join("\n");
}

function downloadCsv(filename, rows) {
  const csv = "﻿" + buildCsv(rows); // UTF-8 BOM (한글 Excel 호환)
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 500);
}

function downloadReport(r) {
  const today = new Date().toISOString().slice(0, 10);
  let rows = [];
  let filename = `${r.id}_${today}.csv`;

  if (r.id === "cams") {
    rows = [
      [
        "장비ID",
        "카메라명",
        "위치",
        "상태",
        "지연(ms)",
        "가동률(%)",
        "OCR 신뢰도(%)",
        "마지막 응답",
      ],
    ];
    cams.forEach((c, i) => {
      rows.push([
        c.id,
        c.name,
        c.loc,
        c.st,
        c.lat,
        c.st === "장애" ? 0 : (95 + (i % 5)).toFixed(1),
        c.st === "장애" ? "-" : 88 + (i % 11),
        c.ts,
      ]);
    });
  } else if (r.id === "faults") {
    rows = [["장애ID", "발생시각", "장비", "증상", "심각도", "담당자", "경과", "상태"]];
    faults.forEach((f) =>
      rows.push([f.id, f.time, f.dev, f.symp, f.sev, f.who, f.elapsed, f.st])
    );
  } else if (r.id === "net") {
    rows = [
      [
        "경로ID",
        "출발",
        "도착",
        "현재RTT",
        "24h평균(ms)",
        "최대(ms)",
        "패킷손실(%)",
        "업타임(%)",
        "마지막응답",
        "상태",
      ],
    ];
    netPaths.forEach((p, i) => {
      rows.push([
        `PATH-${String(i + 1).padStart(3, "0")}`,
        p.from,
        p.to,
        p.lat,
        p.avg,
        Math.round(p.avg * 1.6),
        p.loss,
        p.tone === "bad" ? "0.0" : p.tone === "warn" ? "98.4" : "99.97",
        p.tone === "bad" ? "12분 전" : p.tone === "warn" ? "8초 전" : "< 1초 전",
        p.st,
      ]);
    });
  } else if (r.id === "alarms") {
    rows = [["발생시각", "심각도", "구분", "장비", "메시지", "담당자", "상태"]];
    alarmsExt.forEach((a) =>
      rows.push([
        a.time,
        a.sev,
        a.cat,
        a.dev,
        a.msg,
        a.who,
        a.handled ? "처리됨" : "진행중",
      ])
    );
  } else if (r.id === "srv") {
    rows = [
      [
        "서버명",
        "IP",
        "상태",
        "가동일수",
        "CPU(%)",
        "메모리(%)",
        "디스크(%)",
        "온도(°C)",
      ],
    ];
    servers.forEach((s, i) => {
      const cpu = s.bars.find((b) => b.l === "CPU")?.bar ?? "-";
      const mem = s.bars.find((b) => b.l === "메모리")?.bar ?? "-";
      const disk = s.bars.find((b) => b.l === "디스크")?.bar ?? "-";
      rows.push([
        s.name,
        s.ip,
        s.st,
        [37, 37, 12][i],
        cpu,
        mem,
        disk,
        ["58", "52", "64"][i],
      ]);
    });
  }

  downloadCsv(filename, rows);
  faultMsg.value = `${r.t} 다운로드 완료 — ${filename}`;
  setTimeout(() => {
    faultMsg.value = "";
  }, 2500);
}
const faultMsg = ref("");
// 모니터링 / 알림 임계값
const setLatThreshold = ref(200);
const setLatCritical = ref(500);
const setLossThreshold = ref(5);
const setCpuThreshold = ref(85);
const setMemThreshold = ref(85);
const setDiskThreshold = ref(80);

// 알림 / 통보
const setChannel = ref("이메일");
const setDedup = ref(10);
const setNightMode = ref(true);
const setDailyDigest = ref(true);
const setSmsCrit = ref(true);
const setSlackForward = ref(true);

const channelTargets = {
  이메일: "ops@trafficas.kr",
  SMS: "010-****-1234 외 3명",
  슬랙: "#ops-alarm",
  카카오워크: "운영팀 그룹",
};
const setChannelTarget = computed(() => channelTargets[setChannel.value] || "");

// 자동 처리
const setAutoReconnect = ref(true);
const setRetryCount = ref(3);
const setRetryInterval = ref(30);
const setAutoFault = ref(true);
const setAutoRotate = ref(true);
const setQuarantine = ref(false);

// 점검 / 백업
const setCheckCycle = ref("매주");
const setCheckTime = ref("02:00 ~ 04:00");
const setBackupDays = ref(30);
const setAutoBackup = ref(true);

// 보안 / 권한
const setMfa = ref(true);
const setSessionTimeout = ref(60);
const setLoginAttempts = ref(5);
const setAuditLog = ref(true);

const setMsg = ref("");

function resetSet() {
  setLatThreshold.value = 200;
  setLatCritical.value = 500;
  setLossThreshold.value = 5;
  setCpuThreshold.value = 85;
  setMemThreshold.value = 85;
  setDiskThreshold.value = 80;
  setChannel.value = "이메일";
  setDedup.value = 10;
  setNightMode.value = true;
  setDailyDigest.value = true;
  setSmsCrit.value = true;
  setSlackForward.value = true;
  setAutoReconnect.value = true;
  setRetryCount.value = 3;
  setRetryInterval.value = 30;
  setAutoFault.value = true;
  setAutoRotate.value = true;
  setQuarantine.value = false;
  setCheckCycle.value = "매주";
  setCheckTime.value = "02:00 ~ 04:00";
  setBackupDays.value = 30;
  setAutoBackup.value = true;
  setMfa.value = true;
  setSessionTimeout.value = 60;
  setLoginAttempts.value = 5;
  setAuditLog.value = true;
  setMsg.value = "기본값으로 복원 완료";
  setTimeout(() => {
    setMsg.value = "";
  }, 2000);
}

function saveSet() {
  setMsg.value = "설정 저장 완료";
  setTimeout(() => {
    setMsg.value = "";
  }, 1800);
}
</script>

<style scoped>
/* shell/brand/snav/top/bell/bdg/user는 admin-shared.css */
.side {
  width: 180px;
  padding: 20px 12px;
  display: flex;
  flex-direction: column;
}
.snav-lab {
  flex: 1;
}
.snav-bdg {
  background: #ef4444;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 100px;
  min-width: 16px;
  text-align: center;
}
.side-foot {
  font-size: 13px;
  opacity: 0.35;
  padding: 6px;
  line-height: 1.5;
}
.main {
  flex: 1;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.card {
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 10px;
  padding: 14px;
}
.card h3 {
  font-size: 13.5px;
  font-weight: 700;
  margin: 0;
}
.ch {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.ch-link {
  color: rgba(228, 238, 255, 0.55);
  font-size: 13px;
  cursor: pointer;
}

.cam-filter {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.cf {
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 13.5px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid #1f3055;
}
.cf.on {
  background: rgba(255, 255, 255, 0.08);
}
.cf.gr {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.3);
}
.cf.yl {
  color: #fbbf24;
  border-color: rgba(251, 191, 36, 0.3);
}
.cf.rd {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.3);
}
.cf-r {
  margin-left: auto;
  display: flex;
  gap: 4px;
}
.cf-r input,
.cf-r select {
  background: #06101e;
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13.5px;
}

.cam-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.cam-tbl th,
.cam-tbl td {
  padding: 7px 8px;
  text-align: left;
  border-bottom: 1px solid #1a2a45;
}
.cam-tbl th {
  font-weight: 600;
  opacity: 0.55;
  font-size: 13px;
}
.cam-tbl tr.bad {
  background: rgba(239, 68, 68, 0.05);
}
.cam-tbl tr.bad td {
  color: #fca5a5;
}
.cam-tbl .mono {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.cf {
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 13.5px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.03);
}
.cf.on {
  background: rgba(96, 165, 250, 0.18);
  color: #60a5fa;
}
.cam-card {
  display: flex;
  flex-direction: column;
}
.cam-card .cam-tbl {
  flex: 1;
}
.cam-card .cam-foot {
  margin-top: auto;
  padding-top: 12px;
}
.stat {
  padding: 1px 8px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 700;
}
.stat.ok {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
}
.stat.wn {
  background: rgba(251, 191, 36, 0.18);
  color: #fbbf24;
}
.stat.no {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
}

.cam-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  font-size: 13.5px;
  opacity: 0.65;
}
.pg-row {
  display: flex;
  gap: 3px;
}
.pg-row button {
  background: none;
  border: 1px solid #1f3055;
  color: rgba(228, 238, 255, 0.7);
  width: 24px;
  height: 24px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}
.pg-row button.on {
  background: #3b82f6;
  border-color: #3b82f6;
  color: #fff;
}

.srv-card {
  display: flex;
  flex-direction: column;
}
.srv-card .ch {
  flex-shrink: 0;
}
.srv {
  padding: 16px 0;
  border-bottom: 1px solid #c9d4e3;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 0;
  gap: 12px;
}
.srv + .srv {
  margin-top: 8px;
}
.srv:last-of-type {
  border-bottom: 0;
}
.srv-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  gap: 10px;
  min-width: 0;
  flex-wrap: nowrap;
}
.srv-h .srv-name {
  min-width: 0;
  flex: 1;
  overflow: hidden;
}
.srv-h .sn-t {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.srv-h .sn-ip {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.srv-h .stat {
  flex-shrink: 0;
  white-space: nowrap;
}
.srv-name {
  display: flex;
  gap: 8px;
  align-items: center;
}
.srv-name > i {
  font-size: 13.5px;
  color: #60a5fa;
}
.sn-t {
  font-size: 13.5px;
  font-weight: 700;
}
.sn-tag {
  font-size: 13px;
  opacity: 0.55;
  font-weight: 400;
  margin-left: 4px;
}
.sn-ip {
  font-size: 13px;
  opacity: 0.55;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.srv-bars {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 8px;
}
.srv-b {
  font-size: 13px;
}
.srv-lab {
  opacity: 0.65;
}
.srv-val {
  font-weight: 700;
  font-size: 13px;
  margin: 2px 0 4px;
}
.srv-val.yl {
  color: #fbbf24;
}

/* 서버 게이지 - 원형 progress */
/* 서버 게이지 (ECharts) */
.srv-gauges {
  display: grid;
  grid-template-columns: repeat(2, minmax(80px, 1fr));
  gap: 8px 12px;
  align-items: center;
  justify-items: center;
  padding: 8px 4px;
  min-width: 0;
}
.srv-g {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  width: 100%;
  min-width: 0;
}
.srv-g-wrap {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  position: relative;
  filter: drop-shadow(0 4px 12px rgba(12, 31, 64, 0.08));
}
.srv-g-lab {
  font-size: 13px;
  color: #0c1f40;
  font-weight: 800;
  letter-spacing: -0.01em;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 100%;
}

/* 네트워크 ECharts */
.net-echart {
  flex: 1;
  width: 100%;
  min-height: 120px;
  min-width: 0;
}

/* ★ 반응형 - 창 최소화 시 폰트/레이아웃 깨짐 방지 */
.main-grid > .card,
.main-grid > .bot-row > .card,
.main-grid > .col3-stack > .card {
  min-width: 0;
}
.ch h3 {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ch {
  gap: 8px;
  flex-wrap: nowrap;
  min-width: 0;
}
.ch-kpi {
  white-space: nowrap;
  flex-shrink: 0;
}
.cam-filter {
  flex-wrap: wrap;
  gap: 6px 4px;
  min-width: 0;
}
.cam-filter .cf {
  flex-shrink: 0;
}
.cf-r {
  flex-basis: 100%;
  display: flex;
  gap: 6px;
  min-width: 0;
}
.cf-r input {
  flex: 1; min-width: 0;
}
.srv-h, .ch {
  min-width: 0;
}
.srv-name {
  min-width: 0; overflow: hidden;
}
.sn-t, .sn-ip {
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 100%;
}

/* ── 노트북 / 작은 화면 / 최소화 시 자연스러운 페이지 스크롤 허용 ── */
@media (max-width: 1600px) {
  .srv-gauges { gap: 8px 10px; }
  .srv-g-wrap { width: 100px; height: 100px; }
  .main-grid .ch h3 { font-size: 14.5px !important; }
}

@media (max-width: 1440px) {
  /* 노트북 일반 — 강제 1뷰포트 락 풀고 자연 스크롤 */
  .ops-shell, .ops-shell :deep(.main) {
    height: auto !important;
    min-height: 100vh;
    max-height: none !important;
    overflow: visible !important;
  }
  .main-grid {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
    grid-template-rows: auto auto !important;
  }
  .main-grid > .card,
  .main-grid > .bot-row > .card,
  .main-grid > .col3-stack > .card {
    overflow: visible !important;
    min-height: 240px;
  }
  .col3-stack { overflow: visible !important; }
  .col3-stack .timeline-card { max-height: none !important; }
  .srv-g-wrap { width: 96px; height: 96px; }
  .srv-gauges { padding: 6px 4px; }
  .net-echart { min-height: 160px; }
}

@media (max-width: 1200px) {
  /* 사이드바 좁아진 환경 — 메인 그리드 2컬럼 + 장애 가로배치 */
  .main-grid {
    grid-template-columns: 1fr 1fr !important;
  }
  .srv-card { grid-column: 1 !important; grid-row: 1 !important; }
  .cam-card { grid-column: 2 !important; grid-row: 1 !important; }
  .fail-card { grid-column: 1 / -1 !important; grid-row: 2 !important; }
  .bot-row {
    grid-column: 1 / -1 !important; grid-row: 3 !important;
    grid-template-columns: 1fr 1fr !important;
  }
  .ch h3 { font-size: 14px !important; }
  .srv-g-wrap { width: 90px; height: 90px; }
}

@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr !important;
  }
  .srv-card,
  .cam-card,
  .fail-card,
  .bot-row {
    grid-column: 1 !important;
  }
  .bot-row {
    grid-template-columns: 1fr !important;
  }
  .srv-gauges {
    grid-template-columns: repeat(2, 1fr);
  }
}
.bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
}
.bar span {
  display: block;
  height: 100%;
  border-radius: 4px;
}

.b-rd {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  font-size: 13px;
  font-weight: 700;
  padding: 1px 8px;
  border-radius: 4px;
  margin-left: 4px;
}
.fl-head {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 10px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
.fl-title {
  font-size: 13px;
  font-weight: 700;
  color: #fca5a5;
}
.fl-tag {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  font-size: 13px;
  padding: 1px 6px;
  border-radius: 3px;
  margin-left: 6px;
}
.fl-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  margin-bottom: 12px;
}
.fl-row {
  display: flex;
  justify-content: space-between;
}
.fl-row span {
  opacity: 0.65;
}
.card h4 {
  font-size: 13px;
  font-weight: 700;
  margin: 10px 0 6px;
}
.hst {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13.5px;
  padding-left: 4px;
  margin-bottom: 4px;
}
.hst-t {
  color: #60a5fa;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  margin-right: 6px;
}
.rec-p {
  font-size: 13.5px;
  opacity: 0.75;
  line-height: 1.5;
  margin: 0 0 10px;
}
.act-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-bottom: 8px;
}
.ab {
  padding: 8px;
  border-radius: 5px;
  font-size: 13px;
  font-weight: 700;
  border: 0;
  cursor: pointer;
}
.ab.bl {
  background: #3b82f6;
  color: #fff;
}
.ab.rd {
  background: #ef4444;
  color: #fff;
}
.ab.gy {
  background: rgba(255, 255, 255, 0.06);
  color: #e4eeff;
  border: 1px solid #1f3055;
}
.ab.gr {
  background: #10b981;
  color: #fff;
}
.resp-row,
.memo-row {
  display: grid;
  grid-template-columns: 50px 1fr auto;
  gap: 6px;
  align-items: center;
  font-size: 13px;
  margin-top: 6px;
}
.resp-row span,
.memo-row span {
  opacity: 0.65;
}
.memo-row input {
  background: #06101e;
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13.5px;
}
.ab-sm {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
}

/* ============================================================
   ★ 산업/실무 톤 오버라이드 — AI 느낌 제거
   - 모서리 사각형에 가깝게, 폰트/아이콘 작게, 채도 다운
   - 숫자는 모노스페이스, 그라데이션·글로우 제거
   ============================================================ */
/* ============================================================
   ★ 인덱스 페이지 라이트 톤 매칭
   - 배경 #f1f5fb / 카드 흰색 / 텍스트 #0c1f40 / 액센트 #2563eb
   ============================================================ */
.ops-shell {
  font-size: 13px;
  line-height: 1.55;
  background: #d6deeb !important;
  color: #0c1f40 !important;
  height: 100vh;
  overflow: hidden;
  font-family: "Inter", "Pretendard Variable", Pretendard, -apple-system,
    BlinkMacSystemFont, "Segoe UI", sans-serif !important;
  font-feature-settings: "tnum" 1, "cv11" 1, "ss01" 1;
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.ops-shell *,
.ops-shell :deep(*) {
  font-family: inherit;
}
/* 숫자/ID — 깔끔한 IBM Plex Mono */
.ops-shell [class*="mono"],
.ops-shell .mono,
.ops-shell :deep(.mono),
.ops-shell :deep([class*="mono"]) {
  font-family: "IBM Plex Mono", "JetBrains Mono", ui-monospace, monospace !important;
}
.ops-shell :deep(.main) {
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 사이드바 접기/펼치기 */
.ops-shell .side-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.ops-shell .side-toggle {
  width: 28px;
  height: 28px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  color: #4a5b78;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  font-size: 13.5px;
  flex-shrink: 0;
}
.ops-shell .side-toggle:hover {
  background: #2563eb;
  border-color: #2563eb;
  color: #ffffff;
}

.ops-shell.side-collapsed :deep(.side) {
  width: 56px !important;
  padding: 18px 8px !important;
}
.ops-shell.side-collapsed :deep(.side-top) {
  justify-content: center;
}
.ops-shell.side-collapsed :deep(.snav-i) {
  justify-content: center;
  padding: 12px 4px !important;
}
.ops-shell.side-collapsed :deep(.snav-i .snav-lab) {
  display: none;
}
.ops-shell.side-collapsed :deep(.snav-i i) {
  font-size: 22px !important;
}
.ops-shell.side-collapsed :deep(.snav-ic) {
  width: 28px !important;
}

/* 아이콘 + 알람 뱃지 */
.ops-shell :deep(.snav-ic) {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  flex-shrink: 0;
}

/* 펼친 모드 - 뱃지는 행 우측에 숫자 표시 */
.ops-shell :deep(.snav-i .snav-bdg) {
  margin-left: auto !important;
  min-width: 18px !important;
  height: 18px !important;
  padding: 0 6px !important;
  background: #dc2626 !important;
  color: #fff !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  border-radius: 100px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1;
}

/* 접힌 모드 - 아이콘 우상단 작은 빨간 점 (깜빡임) */
.ops-shell.side-collapsed :deep(.snav-bdg-dot) {
  position: absolute !important;
  top: -2px !important;
  right: -3px !important;
  width: 8px !important;
  height: 8px !important;
  background: #dc2626 !important;
  border: 1.5px solid #e3e9f2 !important;
  border-radius: 50% !important;
  animation: nsPulse 1.4s ease-in-out infinite;
}
.ops-shell :deep(.side) {
  background: #e3e9f2 !important; /* 톤 다운 */
  border-right: 1px solid #b8c5d8 !important;
  color: #0c1f40 !important;
}
.ops-shell :deep(.brand) {
  color: #0c1f40 !important;
}
.ops-shell :deep(.brand em) {
  color: #2563eb !important;
}
.ops-shell :deep(.brand .dot) {
  background: #2563eb !important;
}
.ops-shell :deep(.snav-i) {
  color: rgba(12, 31, 64, 0.92) !important;
}
.ops-shell :deep(.snav-i:hover) {
  background: rgba(37, 99, 235, 0.06) !important;
  color: #0c1f40 !important;
}
.ops-shell :deep(.snav-i.on) {
  background: rgba(37, 99, 235, 0.1) !important;
  color: #2563eb !important;
  border-left-color: #2563eb !important;
}
.ops-shell :deep(.snav-bdg),
.snav-bdg {
  background: #dc2626 !important;
  color: #fff !important;
}
.ops-shell :deep(.side-foot) {
  color: rgba(12, 31, 64, 0.9);
}

.ops-shell :deep(.top h1) {
  color: #0c1f40 !important;
  margin: 0;
  font-size: 13.5px !important;
  font-weight: 700 !important;
}
.ops-shell :deep(.t-sub) {
  color: #0c1f40 !important;
}
.ops-shell :deep(.t-main) {
  color: #0c1f40 !important;
  text-decoration: none !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
  letter-spacing: -0.01em;
  cursor: pointer;
  padding: 2px 0;
  border-bottom: 2px solid transparent;
  display: inline-block;
}
.ops-shell :deep(.t-main:hover) {
  color: #0c1f40 !important;
  border-bottom-color: transparent !important;
}
.ops-shell :deep(.t-bell),
.ops-shell :deep(.t-user) {
  background: #ffffff !important;
  border: 1px solid #dde8f4 !important;
  color: #0c1f40 !important;
}
.ops-shell :deep(.bdg) {
  background: #dc2626 !important;
  color: #fff !important;
}

/* DeptSwitcher — 라이트 톤 매칭 */
.ops-shell :deep(.ds-btn) {
  background: #ffffff !important;
  border: 1px solid #c9d4e3 !important;
  color: #0c1f40 !important;
}
.ops-shell :deep(.ds-btn:hover) {
  background: #f1f5fb !important;
  border-color: #2563eb !important;
}
.ops-shell :deep(.ds-btn > i:first-child) {
  color: #2563eb !important;
}
.ops-shell :deep(.ds-chev) {
  color: rgba(12, 31, 64, 0.9) !important;
}
.ops-shell :deep(.ds-pop) {
  background: #ffffff !important;
  border: 1px solid #c9d4e3 !important;
  box-shadow: 0 8px 24px rgba(12, 31, 64, 0.12) !important;
}
.ops-shell :deep(.ds-h) {
  color: #0c1f40 !important;
  font-weight: 700 !important;
  font-size: 13px !important;
}
.ops-shell :deep(.ds-i) {
  color: #0c1f40 !important;
  padding: 10px 12px !important;
}
.ops-shell :deep(.ds-i:hover) {
  background: #e3e9f2 !important;
}
.ops-shell :deep(.ds-i.cur) {
  background: rgba(37, 99, 235, 0.1) !important;
}
.ops-shell :deep(.ds-i > i:first-child) {
  color: #2563eb !important;
  font-size: 13px !important;
}
.ops-shell :deep(.ds-t) {
  color: #0c1f40 !important;
  font-weight: 700 !important;
  font-size: 13px !important;
}
.ops-shell :deep(.ds-s) {
  color: #0c1f40 !important;
  opacity: 0.8 !important;
  font-size: 13.5px !important;
}
.ops-shell :deep(.ds-arr) {
  color: #0c1f40 !important;
  opacity: 0.55 !important;
  font-size: 13px !important;
}
.ops-shell :deep(.ds-cur) {
  font-size: 13.5px !important;
  padding: 3px 8px !important;
}
.ops-shell :deep(.ds-cur) {
  background: rgba(5, 150, 105, 0.12) !important;
  color: #059669 !important;
}
.ops-shell :deep(.ds-sep) {
  background: #e3e9f2 !important;
}

/* 카드 — 톤 다운 */
.ops-shell :deep(.card) {
  background: #f1f5fb !important;
  border: 1px solid #b8c5d8 !important;
  border-radius: 4px;
  padding: 12px 14px;
  box-shadow: 0 1px 2px rgba(12, 31, 64, 0.08) !important;
}
.ops-shell :deep(.card h3) {
  font-size: 13px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #0c1f40;
  padding-bottom: 0;
  border-bottom: 0;
}
.ops-shell :deep(.ch) {
  padding-bottom: 0;
  border-bottom: 0;
  margin-bottom: 10px;
}
.ops-shell :deep(.ch h3) {
  padding-bottom: 0;
  border-bottom: 0;
  margin-bottom: 0;
}
.ops-shell :deep(*) {
  transition: none !important;
}
.ops-shell :deep(*) {
  font-feature-settings: "tnum" 1;
} /* 실무: 표 안 숫자 너비 균일 */
.ops-shell :deep(.brand) {
  font-size: 13px;
}
.ops-shell :deep(.brand .dot) {
  box-shadow: none;
  width: 8px;
  height: 8px;
}
.ops-shell :deep(.brand em) {
  color: #7ea4d8;
}
.ops-shell :deep(.snav-i) {
  font-size: 16px !important;
  padding: 11px 12px !important;
  border-radius: 2px;
  transition: none;
}
.ops-shell :deep(.snav-i i) {
  font-size: 17px !important;
}
.ops-shell :deep(.snav-i .snav-lab) {
  font-size: 16px !important;
}
.ops-shell :deep(.snav-i.on) {
  background: rgba(120, 160, 210, 0.14);
  color: #c4d8f5;
  border-left: 3px solid #7ea4d8;
  padding-left: 8px;
  font-weight: 600;
}
.ops-shell :deep(.snav-bdg),
.snav-bdg {
  background: #b94545;
  font-weight: 600;
  padding: 1px 6px;
  font-size: 13px;
  border-radius: 2px;
  min-width: 18px;
}
.ops-shell :deep(.top h1) {
  font-size: 13.5px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.ops-shell :deep(.t-sub) {
  font-size: 13.5px;
  margin-left: 8px;
  opacity: 0.75;
}
.ops-shell :deep(.t-bell),
.ops-shell :deep(.t-user) {
  height: 32px;
  border-radius: 2px;
  font-size: 13.5px;
  padding: 0 14px;
}
.ops-shell :deep(.t-bell) {
  width: 32px;
  padding: 0;
}
.ops-shell :deep(.t-bell i) {
  font-size: 13.5px;
}
.ops-shell :deep(.bdg) {
  background: #b94545;
  min-width: 15px;
  height: 15px;
  font-size: 13px;
  border-radius: 2px;
  top: -3px;
  right: -3px;
}

/* 카드 — 컴팩트, 평면 */
.ops-shell :deep(.card) {
  border-radius: 3px;
  padding: 11px 12px;
  box-shadow: none !important;
}
.ops-shell :deep(.card h3) {
  font-size: 13.5px;
  font-weight: 600;
  margin: 0 0 8px;
  letter-spacing: 0;
}
.ops-shell :deep(*) {
  transition: none !important;
} /* AI 부드러움 제거 */

/* ch-link */
.ch-link {
  font-size: 13.5px !important;
  color: #7ea4d8 !important;
}
.ch h3 {
  letter-spacing: -0.01em;
}
.seg-sub {
  font-size: 13.5px !important;
  opacity: 0.55;
}

/* ============================================================
   ★ KPI 카드 (5개 + 자동 새로고침 토글)
   ============================================================ */
/* ★ 헤더 우측 — 시각 + 자동 새로고침 */
.hdr-time {
  font-size: 13px;
  color: #0c1f40;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 6px;
  white-space: nowrap;
}
.hdr-time > i {
  font-size: 13px;
  opacity: 0.8;
}
.hdr-time strong {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-weight: 700;
  color: #0c1f40;
  margin-left: 2px;
}

/* ★ 카드 헤더 분산 KPI — 칩 형태 X, 텍스트만 (AI 티 제거) */
.ops-shell :deep(.ch-kpi) {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  font-weight: 700;
  margin-left: 10px;
  letter-spacing: 0;
  color: #0c1f40;
}
.ops-shell :deep(.ch-kpi em) {
  font-style: normal;
  opacity: 0.8;
  font-weight: 600;
  margin-left: 4px;
}
.ops-shell :deep(.ch-kpi.gr) {
  color: #047857;
}
.ops-shell :deep(.ch-kpi.yl) {
  color: #b45309;
}
.ops-shell :deep(.ch-kpi.rd) {
  color: #b91c1c;
}
.ops-shell :deep(.ch-kpi.bl) {
  color: #1d4ed8;
}

/* ★ 알람 타임라인 — 텍스트 위주, 빡빡 */
.timeline-card {
  display: flex;
  flex-direction: column;
}
.timeline-card .ch {
  justify-content: space-between;
}
.tl-filter {
  display: flex;
  gap: 2px;
}
.tl-f {
  background: transparent;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  padding: 2px 8px;
  font-size: 13.5px;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  cursor: pointer;
  border-radius: 2px;
  letter-spacing: 0.05em;
}
.tl-f.on {
  background: #0c1f40;
  color: #fff;
  border-color: #0c1f40;
}
.tl-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.tl-th {
  display: grid;
  grid-template-columns: 76px 1fr 80px 14px;
  gap: 10px;
  align-items: center;
  padding: 6px 6px;
  border-bottom: 2px solid #0c1f40;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  font-weight: 700;
  color: #4a5b78;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  background: #e3e9f2;
}
.tl-th > span {
  text-align: center;
}
.tl-row {
  display: grid;
  grid-template-columns: 76px 1fr 80px 14px;
  gap: 10px;
  align-items: center;
  padding: 7px 6px;
  border-bottom: 1px solid #c9d4e3;
  font-size: 13.5px;
  color: #0c1f40;
  cursor: pointer;
}
.tl-row .tl-t,
.tl-row .tl-msg,
.tl-row .tl-who {
  text-align: center;
}

/* 알람 모달 SLA 표시 */
.am-sla {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace !important;
  padding: 3px 9px !important;
  border-radius: 3px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 4px !important;
  font-size: 13px !important;
}
.am-sla i {
  font-size: 13px;
}
.am-sla.warn {
  background: rgba(180, 83, 9, 0.14);
  color: #b45309;
}
.am-sla.high {
  background: rgba(220, 38, 38, 0.14);
  color: #b91c1c;
}
.am-sla.crit {
  background: #dc2626;
  color: #fff;
}
.am-sla.resolved {
  background: rgba(5, 150, 105, 0.14);
  color: #059669;
}

@keyframes slaPulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.75;
  }
}
.tl-row:hover {
  background: #ecf0f6;
}
.tl-row.recovered,
.tl-row.info {
  opacity: 0.65;
}
.tl-t {
  color: #0c1f40;
  font-size: 13px;
}
.tl-msg {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13.5px;
  color: #0c1f40;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tl-who {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 13.5px;
  color: #0c1f40;
  text-align: right;
}
.tl-arrow {
  color: rgba(12, 31, 64, 0.55);
  font-size: 13px;
}
.tl-empty {
  padding: 24px;
  text-align: center;
  color: rgba(12, 31, 64, 0.7);
  font-size: 13px;
}
.tl-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  font-size: 13.5px;
  color: #0c1f40;
}
.km-toggle {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #f1f5fb;
  border: 1px solid #dde8f4;
  color: #0c1f40;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 13.5px;
  font-family: inherit;
  cursor: pointer;
}
.km-toggle.on {
  background: rgba(5, 150, 105, 0.08);
  border-color: rgba(5, 150, 105, 0.4);
  color: #0c1f40;
}
.km-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
}
.km-toggle.on .km-dot {
  background: #059669;
}
.km-lab {
  flex: 1;
  text-align: left;
}
.km-state {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  padding: 2px 6px;
  border-radius: 3px;
  background: #e8eff8;
  color: #0c1f40;
}
.km-toggle.on .km-state {
  background: rgba(5, 150, 105, 0.15);
  color: #059669;
}

/* ============================================================
   ★ 장애 상세 (fail-card)
   ============================================================ */
.b-rd {
  background: rgba(217, 112, 112, 0.18);
  color: #d97070;
  font-size: 13px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 2px;
  margin-left: 4px;
}
.fail-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-color: rgba(217, 112, 112, 0.45); /* 단색 빨간 보더만 */
}
.fail-card .ch {
  margin-bottom: 0;
}
.fail-card .fl-head {
  margin-bottom: 0;
}
.fail-card .fl-rows {
  margin-bottom: 0;
  gap: 7px;
}
.fail-card .hst {
  gap: 6px;
  padding: 6px 4px;
  flex: 1;
  min-height: 0;
}
.fail-card .rec-p {
  margin: 0;
  padding: 4px 0;
}
.fail-card h4 {
  margin: 2px 0;
}
.fail-card .act-row {
  margin: 0;
  gap: 6px;
}
.fail-card .ab {
  padding: 10px;
}
.fail-card .resp-row,
.fail-card .memo-row {
  padding: 6px 0;
  margin: 0;
}
.fail-card .ch i.bi-arrows-fullscreen {
  font-size: 13.5px;
  opacity: 0.5;
  cursor: pointer;
}
.fl-head {
  background: rgba(217, 112, 112, 0.08);
  border: 1px solid rgba(217, 112, 112, 0.3);
  padding: 9px 11px;
  border-radius: 2px;
  margin-bottom: 10px;
}
.fl-title {
  font-size: 13.5px;
  font-weight: 700;
  color: #fca5a5;
}
.fl-tag {
  background: rgba(217, 112, 112, 0.22);
  color: #d97070;
  font-size: 13px;
  padding: 1px 6px;
  border-radius: 2px;
  margin-left: 6px;
}
.fl-rows {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 13px;
  margin-bottom: 10px;
}
.fl-row {
  display: flex;
  justify-content: space-between;
}
.fl-row span {
  opacity: 0.6;
}
.fl-row strong {
  font-weight: 600;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
}
.fail-card h4 {
  font-size: 13px;
  font-weight: 600;
  margin: 8px 0 5px;
  opacity: 0.85;
}
.hst {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 13.5px;
  padding-left: 2px;
  margin-bottom: 3px;
}
.hst-t {
  color: #7ea4d8;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  margin-right: 5px;
}
.rec-p {
  font-size: 13.5px;
  opacity: 0.75;
  line-height: 1.5;
  margin: 0 0 8px;
}
.act-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px;
  margin-bottom: 8px;
}
.ab {
  padding: 7px;
  border-radius: 2px;
  font-size: 13px;
  font-weight: 600;
  border: 0;
  cursor: pointer;
  font-family: inherit;
}
.ab.bl {
  background: #2a4a78;
  color: #fff;
}
.ab.rd {
  background: #b94545;
  color: #fff;
}
.ab.gy {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(228, 238, 255, 0.7);
  border: 1px solid #1f3055;
}
.ab.gr {
  background: #4a7a5a;
  color: #fff;
}
.resp-row,
.memo-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 0;
  font-size: 13.5px;
}
.resp-row span,
.memo-row span {
  opacity: 0.6;
  flex-shrink: 0;
}
.resp-row strong {
  font-weight: 600;
  flex: 1;
}
.memo-row input {
  flex: 1;
  background: #06101e;
  border: 1px solid #1f3055;
  color: #d4dbe7;
  padding: 4px 8px;
  border-radius: 2px;
  font-size: 13.5px;
  font-family: inherit;
}
.ab-sm {
  padding: 3px 8px;
  background: rgba(120, 160, 210, 0.12);
  border: 1px solid rgba(120, 160, 210, 0.3);
  color: #7ea4d8;
  border-radius: 2px;
  font-size: 13px;
  cursor: pointer;
}

/* ============================================================
   ★ 메인 그리드 — 좌측 2x2 + 우측 풀세로 장애상세
   ============================================================ */
.main-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr;
  grid-template-rows: 1.25fr 0.75fr;
  gap: 8px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.main-grid > .card,
.main-grid > .bot-row > .card,
.main-grid > .col3-stack > .card {
  display: flex;
  flex-direction: column;
  padding: 10px 12px !important;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}
/* 카드 내부 표/리스트는 카드 안에서만 차지하고 오버플로 시 카드 안에 머무름 */
.main-grid .cam-tbl,
.main-grid .tl-list,
.main-grid .srv,
.main-grid .net-summary,
.main-grid .nz-chart {
  min-height: 0;
}
.main-grid .cam-tbl tbody,
.main-grid .tl-list {
  overflow: hidden;
}
.main-grid .ch h3 {
  font-size: 15.5px !important;
}
.main-grid .ch {
  margin-bottom: 6px !important;
}

/* ── 알람 타임라인 컴팩트 (3행 더미에 딱 맞게) ── */
.main-grid .timeline-card .tl-list { flex: 1; min-height: 0; overflow: hidden; margin-top: 0 !important; border-top: 0 !important; }
.main-grid .timeline-card .tl-th,
.main-grid .timeline-card .tl-row {
  grid-template-columns: 64px 1fr 72px 12px !important;
  gap: 6px !important;
}
.main-grid .timeline-card .tl-th {
  margin-top: 0 !important;
  border-top: 0 !important;
}
.main-grid .timeline-card .tl-th {
  padding: 5px 8px !important;
  font-size: 13px !important;
  line-height: 1.3 !important;
}
.main-grid .timeline-card .tl-row {
  padding: 7px 8px !important;
  font-size: 14.5px !important;
  line-height: 1.35 !important;
}
.main-grid .timeline-card .tl-row .tl-t,
.main-grid .timeline-card .tl-row .tl-msg,
.main-grid .timeline-card .tl-row .tl-who {
  font-size: 14.5px !important;
  line-height: 1.35 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}
.main-grid .timeline-card .tl-foot {
  font-size: 13px !important;
  padding: 5px 8px !important;
}
.main-grid .timeline-card .tl-filter button {
  font-size: 13px !important;
  padding: 2px 6px !important;
}

/* ── 카메라 카드 컴팩트 (가로 2칸 span이라 폭 여유) ── */
.main-grid .cam-card .cam-tbl th,
.main-grid .cam-card .cam-tbl td {
  padding: 5px 8px !important;
  font-size: 13.5px !important;
  line-height: 1.3 !important;
}
.main-grid .cam-card .cam-filter {
  margin-bottom: 4px !important;
  gap: 4px !important;
}
.main-grid .cam-card .cf {
  padding: 2px 8px !important;
  font-size: 12px !important;
}
.main-grid .cam-card .cf-r input,
.main-grid .cam-card .cf-r select {
  padding: 2px 6px !important;
  font-size: 12px !important;
}
.main-grid .cam-card .cam-foot {
  font-size: 12px !important;
  padding: 4px 6px !important;
}
.main-grid .cam-card .cam-foot button {
  padding: 2px 6px !important;
  font-size: 12px !important;
}

/* ── 장애상세 (row2 + 1.22fr 으로 공간 여유 있음) ── */
.main-grid .fail-card .fl-head { padding: 8px 12px !important; margin-bottom: 8px !important; }
.main-grid .fail-card .fl-rows { gap: 5px !important; margin-bottom: 10px !important; }
.main-grid .fail-card .fl-row { font-size: 14.5px !important; padding: 2px 0 !important; line-height: 1.45 !important; }
.main-grid .fail-card .fl-row span,
.main-grid .fail-card .fl-row strong { font-size: 14.5px !important; line-height: 1.45 !important; }
.main-grid .fail-card .fl-row span i { margin-right: 5px; color: #2563eb; opacity: 0.85; }
.main-grid .fail-card h4 i { margin-right: 6px; color: #2563eb; }
.main-grid .fail-card .hst > div { display: flex; align-items: center; gap: 6px; }
.main-grid .fail-card .hst .hst-i { font-size: 7px; color: #dc2626; flex-shrink: 0; }
.main-grid .fail-card .ab i { margin-right: 4px; font-size: 12px; }
.main-grid .fail-card .resp-row span i,
.main-grid .fail-card .memo-row span i { margin-right: 5px; color: #2563eb; opacity: 0.85; }
.main-grid .fail-card h4 { font-size: 14.5px !important; margin: 8px 0 6px !important; }
.main-grid .fail-card .hst { font-size: 14px !important; gap: 4px !important; line-height: 1.45 !important; }
.main-grid .fail-card .hst > div { font-size: 14px !important; line-height: 1.45 !important; }
.main-grid .fail-card .ab { padding: 8px 11px !important; font-size: 14px !important; line-height: 1.2 !important; }
.main-grid .fail-card .act-row { gap: 5px !important; flex-wrap: wrap; }
.main-grid .fail-card .resp-row,
.main-grid .fail-card .memo-row { font-size: 14px !important; }
.main-grid .fail-card .memo-row input { font-size: 14px !important; min-width: 0; }

/* 카드 내부 — 폰트 크게 유지, 행 적당히 */
.main-grid .cam-tbl th {
  padding: 8px 8px !important;
  font-size: 14.5px !important;
}
.main-grid .cam-tbl td {
  padding: 8px 8px !important;
  font-size: 14.5px !important;
}
.main-grid .tl-row {
  padding: 8px 6px !important;
  font-size: 14.5px !important;
}
.main-grid .tl-th {
  padding: 6px 8px !important;
  font-size: 14.5px !important;
}

/* 서버 카드 — 게이지 큼직하게 */
.main-grid .srv-card .srv {
  padding: 8px 0 !important;
  gap: 10px !important;
}
.main-grid .srv-card .srv-gauges {
  gap: 14px 20px !important;
  padding: 14px 8px !important;
}
.main-grid .srv-card .srv-g-wrap {
  width: 140px !important;
  height: 140px !important;
}
.main-grid .srv-card .srv-g-lab {
  font-size: 14px !important;
}
.main-grid .net-echart {
  min-height: 210px !important;
}
.main-grid .srv-card .srv-bars {
  gap: 8px !important;
}
.main-grid .srv-card .srv-b {
  padding: 4px 0 !important;
}
.main-grid .srv-card .srv-icon {
  width: 34px !important;
  height: 34px !important;
}
.main-grid .srv-card .sn-t {
  font-size: 14.5px !important;
}
.main-grid .srv-card .sn-ip {
  font-size: 14px !important;
}
.main-grid .srv-card .srv-lab {
  font-size: 14.5px !important;
}
.main-grid .srv-card .srv-val {
  font-size: 14.5px !important;
}

/* 네트워크 요약 */
.main-grid .net-summary {
  gap: 10px !important;
  padding: 4px !important;
}
.main-grid .ns-head {
  padding: 4px 6px 8px !important;
}
.main-grid .ns-avg strong {
  font-size: 14.5px !important;
}
.main-grid .ns-foot {
  padding: 8px 4px 4px !important;
  font-size: 14.5px !important;
}

/* 장애 상세 카드 */
.main-grid .fail-card {
  padding: 14px 16px !important;
}
.main-grid .fl-meta {
  gap: 6px !important;
}
.main-grid .fl-meta-item {
  padding: 6px 10px !important;
  font-size: 13px !important;
}

/* ── 메인 그리드 배치 ──
   [서버상태]   [네트워크지연]   [알람타임라인]
   [카메라 (가로 2칸 span)]      [장애상세]
*/
.srv-card {
  grid-column: 1;
  grid-row: 1;
}
.net-card {
  grid-column: 2;
  grid-row: 1;
  display: flex;
  flex-direction: column;
}
.bot-row {
  display: contents;
}
.bot-row .cam-card {
  grid-column: 1 / span 2;
  grid-row: 2;
}
/* 우측 컬럼 스택 — 알람타임라인(작게) + 장애상세(크게) */
.col3-stack {
  grid-column: 3;
  grid-row: 1 / span 2;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow: hidden;
}
.col3-stack .timeline-card {
  flex: 0 0 auto;
  max-height: 32%;
}
.col3-stack .fail-card {
  flex: 1 1 auto;
  min-height: 0;
}

/* ★ 네트워크 지연 — heartbeat 라인 차트 (상세 탭에서만 사용) */
.net-chart {
  display: grid;
  grid-template-columns: 30px 1fr;
  grid-template-rows: 1fr auto auto;
  gap: 4px 8px;
  min-height: 0;
  flex: 1;
}
.nc-y {
  grid-column: 1;
  grid-row: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding: 2px 0;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 600;
}
.nc-svgwrap {
  grid-column: 2;
  grid-row: 1;
  position: relative;
  background: #ffffff;
  border: 1px solid #c9d4e3;
  min-height: 140px;
}
.nc-svg {
  width: 100%;
  height: 100%;
  display: block;
}
.nc-spike {
  position: absolute;
  top: 4px;
  transform: translateX(-50%);
  background: #dc2626;
  color: #fff;
  padding: 3px 8px;
  border-radius: 2px;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  line-height: 1.3;
}
.nc-spike::after {
  content: "";
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #dc2626;
  border-bottom: 0;
}
.nc-spike strong {
  display: block;
  font-weight: 800;
}
.nc-spike span {
  display: block;
  font-weight: 600;
  opacity: 0.9;
  font-size: 13px;
  margin-top: 1px;
}

.nc-x {
  grid-column: 2;
  grid-row: 2;
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 600;
}
.nc-legend {
  grid-column: 1 / -1;
  grid-row: 3;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  padding: 6px 2px 0;
  border-top: 1px solid #c9d4e3;
  margin-top: 2px;
  font-size: 13.5px;
  color: #0c1f40;
  font-weight: 600;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.nc-legend .lg-l {
  display: inline-block;
  width: 14px;
  height: 2px;
  vertical-align: middle;
  margin-right: 4px;
}
.nc-legend .lg-l.bl {
  background: #2563eb;
  height: 2px;
}
.nc-legend .lg-l.gr {
  background: transparent;
  border-top: 2px dashed #047857;
  height: 0;
  margin-top: 5px;
}
.nc-legend .lg-l.rd {
  background: transparent;
  border-top: 2px dashed #b91c1c;
  height: 0;
  margin-top: 5px;
}
.nc-legend .lg-l.sp {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dc2626;
  border: 1.5px solid #fff;
  box-shadow: 0 0 0 1px #dc2626;
  vertical-align: middle;
}

/* ★ 네트워크 요약 - 25셀 헬스 그리드 (산업 NOC 톤) */
.net-summary {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  padding: 4px 4px 0;
}
.ns-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 4px 4px 10px;
  border-bottom: 1px solid #c9d4e3;
}
.ns-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.ns-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.ns-dot.gr {
  background: #047857;
}
.ns-dot.yl {
  background: #b45309;
  animation: nsPulse 2s ease-in-out infinite;
}
.ns-dot.rd {
  background: #b91c1c;
  animation: nsPulse 1.4s ease-in-out infinite;
}
@keyframes nsPulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.55;
  }
}
.ns-st-label {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  font-weight: 800;
  color: #0c1f40;
  letter-spacing: 0.04em;
}
.ns-avg {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
}
.ns-avg strong {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  font-weight: 800;
  color: #0c1f40;
  line-height: 1;
}
.ns-avg strong small {
  font-size: 13px;
  font-weight: 600;
  color: #4a5b78;
  margin-left: 2px;
}
.ns-avg span {
  font-size: 13.5px;
  color: #4a5b78;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}

/* 구역별 평균 지연 세로 막대 (박스 fit) */
.nz-chart {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
  padding: 10px 8px 6px;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  flex: 1;
  min-height: 140px;
  align-items: stretch;
}
.nz-bar {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  cursor: pointer;
  transition: transform 0.1s;
}
.nz-bar:hover {
  transform: translateY(-2px);
}
.nz-v {
  font-size: 13px;
  font-weight: 800;
  color: #0c1f40;
  text-align: center;
  margin-bottom: 4px;
  letter-spacing: -0.02em;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  flex-shrink: 0;
}
.nz-v small {
  font-size: 13px;
  font-weight: 600;
  color: #4a5b78;
  margin-left: 1px;
}
.nz-bar.gr .nz-v {
  color: #047857;
}
.nz-bar.yl .nz-v {
  color: #b45309;
}
.nz-bar.rd .nz-v {
  color: #b91c1c;
}
.nz-fill {
  width: 100%;
  background: #047857;
  margin-top: auto;
  min-height: 6px;
  border-top: 2px solid transparent;
}
.nz-bar.yl .nz-fill {
  background: #b45309;
}
.nz-bar.or .nz-fill {
  background: #c2410c;
}
.nz-bar.rd .nz-fill {
  background: #b91c1c;
  animation: nsPulse 1.4s ease-in-out infinite;
}
.nz-name {
  margin-top: 5px;
  font-size: 13.5px;
  font-weight: 700;
  color: #0c1f40;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
  letter-spacing: -0.01em;
}

.ns-foot {
  display: flex;
  justify-content: space-between;
  padding: 8px 4px 4px;
  border-top: 1px solid #c9d4e3;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 600;
}
.ns-foot strong {
  color: #0c1f40;
  font-weight: 800;
  margin-left: 4px;
}
.ns-d {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 4px;
  vertical-align: middle;
}
.ns-d.gr {
  background: #047857;
}
.ns-d.yl {
  background: #b45309;
}
.ns-d.rd {
  background: #b91c1c;
}

/* ★ 네트워크 상세 탭 (전체 보기) */
.net-detail .pnl-summary.nd-kpi {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  margin-bottom: 18px;
}
.net-detail .ps-box {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 14px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
}
.net-detail .ps-box.gr {
  border-top: 3px solid #047857;
}
.net-detail .ps-box.yl {
  border-top: 3px solid #b45309;
}
.net-detail .ps-box.rd {
  border-top: 3px solid #b91c1c;
}
.net-detail .ps-l {
  font-size: 13px;
  color: #4a5b78;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.net-detail .ps-v {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 26px;
  font-weight: 800;
  color: #0c1f40;
  line-height: 1.1;
}
.net-detail .ps-v span {
  font-size: 13px;
  font-weight: 600;
  color: #4a5b78;
  margin-left: 2px;
}
.net-detail .ps-sub {
  font-size: 13px;
  color: #6b7a92;
  font-weight: 500;
  letter-spacing: -0.01em;
  margin-top: 2px;
}

.nd-block {
  margin-bottom: 22px;
}
.nd-block:last-child {
  margin-bottom: 0;
}
.nd-h {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0 10px;
  border-bottom: 2px solid #0c1f40;
  margin-bottom: 12px;
}
.nd-h h4 {
  margin: 0;
  font-size: 13.5px;
  font-weight: 800;
  color: #0c1f40;
  letter-spacing: -0.01em;
}
.nd-h-r {
  display: flex;
  gap: 14px;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.nd-h-cnt {
  font-size: 13px;
  color: #4a5b78;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.nd-chart {
  display: grid;
  grid-template-columns: 30px 1fr;
  grid-template-rows: 1fr auto;
  gap: 4px 8px;
  min-height: 220px;
}
.nd-chart .nc-y {
  grid-column: 1;
  grid-row: 1;
}
.nd-chart .nc-svgwrap {
  grid-column: 2;
  grid-row: 1;
  min-height: 220px;
}
.nd-chart .nc-x {
  grid-column: 2;
  grid-row: 2;
}

.nd-tbl th,
.nd-tbl td {
  padding: 8px 10px !important;
  border-bottom: 1px solid #c9d4e3 !important;
  font-size: 13.5px;
  color: #0c1f40;
}
.nd-tbl th {
  background: #e3e9f2;
  font-size: 13px;
  font-weight: 700;
  color: #4a5b78;
  letter-spacing: -0.01em;
  text-align: left;
}
.nd-tbl tbody tr:hover {
  background: #f1f5fb;
}
.nd-tbl .rd-txt {
  color: #b91c1c;
  font-weight: 800;
}
.nd-tbl .yl-txt {
  color: #b45309;
  font-weight: 700;
}

.pnl-act {
  background: #ffffff;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 2px;
  cursor: pointer;
  letter-spacing: -0.01em;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.pnl-act:hover {
  background: #f1f5fb;
  border-color: #2563eb;
  color: #2563eb;
}
.pnl-act.sm {
  padding: 3px 8px;
  font-size: 13.5px;
}

/* ★ 카메라 페이지 - 위치별 분포 */
.net-detail .pnl-summary.nd-kpi-7 {
  grid-template-columns: repeat(7, 1fr);
}
.cd-zones {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
}
.cdz {
  background: #ffffff;
  border: 1px solid #c9d4e3;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.cdz-h {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.cdz-n {
  font-size: 13px;
  color: #0c1f40;
  font-weight: 800;
  letter-spacing: -0.01em;
}
.cdz-c strong {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  font-weight: 800;
  color: #0c1f40;
}
.cdz-c em {
  font-style: normal;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 600;
  margin-left: 2px;
}
.cdz-bar {
  display: flex;
  height: 6px;
  background: #e3e9f2;
  border: 1px solid #c9d4e3;
  overflow: hidden;
}
.cdz-bar > span {
  display: block;
  height: 100%;
}
.cdz-bar > span.gr {
  background: #047857;
}
.cdz-bar > span.yl {
  background: #b45309;
}
.cdz-bar > span.rd {
  background: #b91c1c;
}
.cdz-leg {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #4a5b78;
  font-weight: 700;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.cdz-leg span {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

/* KPI 7/8박스 그리드 */
.net-detail .pnl-summary.nd-kpi-8 {
  grid-template-columns: repeat(8, 1fr);
}

/* 진행 중 장애 큰 강조 카드 */
.fl-cur {
  background: #ffffff;
  border: 1px solid #b91c1c;
  border-left: 4px solid #b91c1c;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.flc-h {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1d1d1;
}
.flc-id {
  display: flex;
  align-items: center;
  gap: 10px;
}
.flc-id strong {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  font-weight: 800;
  color: #0c1f40;
}
.flc-dev {
  font-size: 13px;
  color: #4a5b78;
  font-weight: 700;
}
.flc-time {
  display: flex;
  align-items: baseline;
  gap: 6px;
}
.flc-l {
  font-size: 13.5px;
  color: #4a5b78;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.flc-time strong {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  font-weight: 800;
}
.flc-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 24px;
}
.flc-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 5px 0;
  border-bottom: 1px dashed #eef2f7;
  font-size: 13.5px;
  gap: 8px;
}
.flc-row span {
  color: #4a5b78;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
  letter-spacing: -0.01em;
}
.flc-row strong {
  color: #0c1f40;
  font-weight: 700;
  text-align: right;
  font-size: 13px;
  letter-spacing: -0.01em;
}

/* 작업 진행 단계 */
.flc-progress {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0;
  padding: 10px 0;
  border-top: 1px solid #c9d4e3;
  border-bottom: 1px solid #c9d4e3;
}
.flc-step {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 8px;
  position: relative;
  font-size: 13.5px;
  font-weight: 700;
  color: #6b7a92;
  letter-spacing: -0.01em;
}
.flc-step span {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e3e9f2;
  color: #6b7a92;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 13.5px;
  font-weight: 800;
  border: 1px solid #c9d4e3;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.flc-step::after {
  content: "→";
  position: absolute;
  right: -4px;
  color: #c9d4e3;
  font-weight: 800;
}
.flc-step:last-child::after {
  content: "";
}
.flc-step.done {
  color: #047857;
}
.flc-step.done span {
  background: #047857;
  color: #fff;
  border-color: #047857;
}
.flc-step.on {
  color: #b91c1c;
}
.flc-step.on span {
  background: #b91c1c;
  color: #fff;
  border-color: #b91c1c;
  animation: nsPulse 1.5s ease-in-out infinite;
}

.flc-acts {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

/* ★ 설정 페이지 - 그리드 입력 (한글 가독성 Pretendard) */
.set-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.set-it {
  display: grid;
  grid-template-columns: 1fr 100px;
  grid-template-rows: auto auto;
  gap: 4px 10px;
  padding: 12px 14px;
  background: #ffffff;
  border: 1px solid #c9d4e3;
}
.set-it label {
  grid-column: 1;
  grid-row: 1;
  font-size: 13px;
  font-weight: 700;
  color: #0c1f40;
  align-self: center;
  letter-spacing: -0.01em;
}
.set-it input[type="number"],
.set-it select {
  grid-column: 2;
  grid-row: 1;
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  padding: 6px 10px;
  font-size: 13px;
  border-radius: 2px;
  width: 100%;
  font-weight: 700;
}
.set-it input[type="number"] {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.set-it input[type="number"]:focus,
.set-it select:focus {
  outline: 1px solid #2563eb;
  border-color: #2563eb;
}
.set-it .set-h {
  grid-column: 1 / -1;
  grid-row: 2;
  font-size: 13px;
  color: #6b7a92;
  font-weight: 500;
  letter-spacing: -0.01em;
  line-height: 1.4;
}

.set-toggle {
  grid-template-columns: 1fr auto;
}
.set-toggle label {
  font-size: 13.5px;
}
.set-toggle input[type="checkbox"] {
  grid-column: 2;
  grid-row: 1;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #2563eb;
}

.set-actions {
  display: flex;
  align-items: center;
  padding: 16px 0 4px;
  border-top: 1px solid #c9d4e3;
}
.set-actions .btn-save {
  background: #2563eb;
  color: #fff;
  border: 0;
  padding: 11px 24px;
  border-radius: 2px;
  font-size: 13.5px;
  font-weight: 800;
  cursor: pointer;
  letter-spacing: -0.01em;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.set-actions .btn-save:hover {
  background: #1d4ed8;
}

.pnl {
  padding: 18px;
}
.pnl h3 {
  font-size: 13.5px;
  font-weight: 700;
  margin: 0 0 14px;
}
.pnl-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13.5px;
}
.pnl-tbl th,
.pnl-tbl td {
  padding: 9px 10px;
  text-align: left;
  border-bottom: 1px solid #1a2a45;
}
.pnl-tbl th {
  font-weight: 600;
  opacity: 0.6;
  font-size: 13px;
}
.pnl-tbl .mono {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
}
.stat {
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 13px;
  font-weight: 700;
}
.stat.ok {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.stat.wn {
  background: rgba(245, 158, 11, 0.18);
  color: #fbbf24;
}
.stat.no {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
}
.btn-save {
  margin-top: 14px;
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 9px 16px;
  border-radius: 6px;
  font-size: 13.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.set-msg {
  margin-top: 10px;
  font-size: 13px;
  color: #34d399;
}

/* ============================================================
   ★★ 인덱스 페이지 라이트 톤 — 최종 오버라이드 (모든 다크 톤 위에 적용)
   ============================================================ */
.ops-shell .stat.ok,
.ops-shell :deep(.stat.ok) {
  background: rgba(5, 150, 105, 0.12) !important;
  color: #059669 !important;
}
.ops-shell .stat.wn,
.ops-shell :deep(.stat.wn) {
  background: rgba(220, 104, 3, 0.14) !important;
  color: #b45309 !important;
}
.ops-shell .stat.no,
.ops-shell :deep(.stat.no) {
  background: rgba(220, 38, 38, 0.12) !important;
  color: #dc2626 !important;
}

/* 필터 칩 */
.ops-shell .cam-filter {
  color: #0c1f40;
}
.ops-shell .cf {
  background: #f1f5fb !important;
  border: 1px solid #dde8f4 !important;
  color: #0c1f40 !important;
}
.ops-shell .cf.on {
  background: rgba(37, 99, 235, 0.1) !important;
  color: #2563eb !important;
}
.ops-shell .cf.gr {
  background: rgba(5, 150, 105, 0.08) !important;
  color: #059669 !important;
}
.ops-shell .cf.yl {
  background: rgba(220, 104, 3, 0.1) !important;
  color: #b45309 !important;
}
.ops-shell .cf.rd {
  background: rgba(220, 38, 38, 0.08) !important;
  color: #dc2626 !important;
}
.ops-shell .cf-r input,
.ops-shell .cf-r select {
  background: #f8fafc !important;
  border: 1px solid #dde8f4 !important;
  color: #0c1f40 !important;
}

/* 카메라/서버 표 */
.ops-shell .cam-tbl,
.ops-shell .srv-tbl {
  color: #0c1f40 !important;
}
.ops-shell .cam-tbl th,
.ops-shell .srv-tbl th {
  color: #0c1f40 !important;
}
.ops-shell .cam-tbl tbody tr,
.ops-shell .srv-tbl tbody tr {
  border-bottom-color: #e8eff8 !important;
}
.ops-shell .cam-tbl tbody tr:nth-child(even),
.ops-shell .srv-tbl tbody tr:nth-child(even) {
  background: #ecf0f6 !important;
}
.ops-shell .cam-tbl tr.bad {
  background: rgba(220, 38, 38, 0.06) !important;
}
.ops-shell .cam-tbl tr.bad td {
  color: #dc2626 !important;
}
.ops-shell .cam-tbl td > i {
  color: rgba(12, 31, 64, 0.92) !important;
}
.ops-shell .pg-row button {
  background: #ffffff;
  border: 1px solid #dde8f4;
  color: #0c1f40;
}
.ops-shell .pg-row button.on {
  background: #2563eb !important;
  border-color: #2563eb !important;
  color: #fff !important;
}

/* 서버 카드 내부 */
.ops-shell .srv {
  border-bottom-color: #e8eff8 !important;
}
.ops-shell .srv-name i {
  color: #2563eb;
}
.ops-shell .sn-t,
.ops-shell .sn-ip {
  color: #0c1f40;
}
.ops-shell .sn-ip {
  opacity: 0.55;
}
.ops-shell .srv-lab {
  color: #0c1f40;
}
.ops-shell .srv-val {
  color: #0c1f40;
}
.ops-shell .srv-val.yl {
  color: #b45309;
}
.ops-shell .bar {
  background: #e8eff8;
}
.ops-shell .bar span {
  background: #059669;
}

/* 장애 상세 */
.ops-shell .fail-card {
  background: #f7f9fc !important;
  border: 1px solid #e8b4b4 !important;
}
.ops-shell .fl-head {
  background: #fbe8e8 !important;
  border: 1px solid #e8b4b4 !important;
  padding: 9px 11px;
  border-radius: 4px;
}
.ops-shell .fl-title {
  color: #b91c1c !important;
}
.ops-shell .fl-tag {
  background: #fee2e2 !important;
  color: #dc2626 !important;
}
.ops-shell .fl-row span,
.ops-shell .fail-card .fl-row span {
  color: #0c1f40 !important;
  opacity: 1 !important;
  font-weight: 500;
  font-size: 13.5px !important;
}
.ops-shell .fl-row strong,
.ops-shell .fail-card .fl-row strong {
  color: #0c1f40 !important;
  font-weight: 700;
  font-size: 13.5px !important;
}

/* ★ 장애 상세 — 폰트 일괄 ↑ */
.ops-shell .fail-card .fl-title {
  font-size: 13.5px !important;
  font-weight: 700 !important;
}
.ops-shell .fail-card .fl-tag {
  font-size: 13px !important;
  padding: 2px 8px !important;
}
.ops-shell .fail-card .b-rd {
  font-size: 13px !important;
  padding: 2px 8px !important;
}
.ops-shell .fail-card h4 {
  font-size: 13.5px !important;
  font-weight: 700;
}
.ops-shell .fail-card .hst {
  font-size: 13px !important;
}
.ops-shell .fail-card .hst > div {
  padding: 3px 0;
}
.ops-shell .fail-card .hst-t {
  font-size: 13.5px !important;
  font-weight: 700;
}
.ops-shell .fail-card .rec-p {
  font-size: 13px !important;
  line-height: 1.55;
}
.ops-shell .fail-card .ab {
  font-size: 13.5px !important;
  padding: 10px !important;
  font-weight: 700;
}
.ops-shell .fail-card .resp-row,
.ops-shell .fail-card .memo-row {
  font-size: 13px !important;
}
.ops-shell .fail-card .resp-row strong {
  font-size: 13.5px !important;
  font-weight: 700;
}
.ops-shell .fail-card .ab-sm {
  font-size: 13px !important;
  padding: 4px 10px !important;
}
.ops-shell .fail-card .memo-row input {
  font-size: 13px !important;
  padding: 6px 10px !important;
}

/* ★ 서버 상태 — 폰트 일괄 ↑ */
.ops-shell .srv-card .sn-t {
  font-size: 13.5px !important;
  font-weight: 700;
}
.ops-shell .srv-card .sn-tag {
  font-size: 13px !important;
}
.ops-shell .srv-card .sn-ip {
  font-size: 13.5px !important;
}
.ops-shell .srv-card .srv-name > i {
  font-size: 13px !important;
}
.srv-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 3px rgba(12, 31, 64, 0.18));
}
.ops-shell .srv-card .srv-lab {
  font-size: 13px !important;
  font-weight: 500;
}
.ops-shell .srv-card .srv-val {
  font-size: 13.5px !important;
  font-weight: 700;
}
.ops-shell .srv-card .stat {
  font-size: 13px !important;
  padding: 3px 9px !important;
}
.ops-shell .fail-card h4 {
  color: #0c1f40;
}
.ops-shell .hst {
  color: #0c1f40;
}
.ops-shell .hst-t {
  color: #2563eb !important;
}
.ops-shell .rec-p {
  color: #0c1f40;
}
.ops-shell .ch-link {
  color: #2563eb !important;
  cursor: pointer;
  font-size: 13.5px !important;
  font-weight: 600;
  padding: 2px 4px;
  border-radius: 2px;
}
.ops-shell .ch-link:hover {
  background: rgba(37, 99, 235, 0.1);
  text-decoration: underline;
}

/* ★ 보고서 / 알람 / 점검 / 설정 탭 — 라이트 톤 */
.ops-shell .pnl {
  background: #ffffff !important;
  border-color: #b8c5d8 !important;
}
.ops-shell .pnl h3 {
  color: #0c1f40 !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  padding-bottom: 8px;
  border-bottom: 1px solid #c9d4e3;
}
.ops-shell .pnl-tbl {
  color: #0c1f40 !important;
}
.ops-shell .pnl-tbl th {
  color: rgba(12, 31, 64, 0.78) !important;
  border-bottom-color: #c9d4e3 !important;
  font-weight: 700 !important;
}
.ops-shell .pnl-tbl td {
  color: #0c1f40 !important;
  border-bottom-color: #e3e9f2 !important;
}
.ops-shell .pnl-tbl tbody tr:nth-child(even) {
  background: #ecf0f6 !important;
}
.ops-shell .pnl-search {
  background: #f1f5fb !important;
  border: 1px solid #c9d4e3 !important;
  color: #0c1f40 !important;
}
/* 보고서 카드 행 */
.ops-shell .rep-rows .rep-r {
  background: #f1f5fb !important;
  border: 1px solid #c9d4e3 !important;
  color: #0c1f40 !important;
}
.ops-shell .rep-r > i {
  color: #2563eb !important;
}
.ops-shell .rep-r strong {
  color: #0c1f40 !important;
  font-size: 13.5px !important;
  font-weight: 700 !important;
}
.ops-shell .rep-r span {
  color: rgba(12, 31, 64, 0.78) !important;
  opacity: 1 !important;
  font-size: 13.5px !important;
}
.ops-shell .bt-dl {
  background: rgba(37, 99, 235, 0.12) !important;
  color: #2563eb !important;
}
/* 설정 행 */
.ops-shell .set-row {
  color: #0c1f40 !important;
  border-bottom-color: #e3e9f2 !important;
  font-size: 13.5px !important;
}
.ops-shell .set-row input[type="number"],
.ops-shell .set-row select {
  background: #ffffff !important;
  border: 1px solid #c9d4e3 !important;
  color: #0c1f40 !important;
}
.ops-shell .btn-save {
  background: #2563eb !important;
  color: #fff !important;
}
.ops-shell .set-msg {
  color: #059669 !important;
}
/* 장애 관리 탭 */
.ops-shell .fl-head {
  background: #fbe8e8 !important;
  border-color: #e8b4b4 !important;
}
.ops-shell .fl-title {
  color: #b91c1c !important;
}
.ops-shell .fl-tag {
  background: #fee2e2 !important;
  color: #dc2626 !important;
}

/* 액션 버튼 — 인덱스 톤 */
.ops-shell .ab.bl {
  background: #2563eb !important;
  color: #fff !important;
}
.ops-shell .ab.rd {
  background: #dc2626 !important;
  color: #fff !important;
}
.ops-shell .ab.gy {
  background: #f1f5fb !important;
  color: #0c1f40 !important;
  border: 1px solid #dde8f4 !important;
}
.ops-shell .ab.gr {
  background: #059669 !important;
  color: #fff !important;
}
.ops-shell .resp-row span,
.ops-shell .memo-row span {
  color: #0c1f40;
}
.ops-shell .resp-row strong {
  color: #0c1f40;
}
.ops-shell .memo-row input {
  background: #f8fafc !important;
  border: 1px solid #dde8f4 !important;
  color: #0c1f40 !important;
}
.ops-shell .ab-sm {
  background: #f1f5fb !important;
  border: 1px solid #dde8f4 !important;
  color: #2563eb !important;
}

/* 네트워크 5박스 */
.ops-shell .nb {
  background: #ecf0f6 !important;
  border: 1px solid #c9d4e3 !important;
}
.ops-shell .nb-l {
  color: #0c1f40;
}
.ops-shell .nb-v {
  color: #0c1f40 !important;
}
.ops-shell .nb-v .u {
  color: rgba(12, 31, 64, 0.92);
}
.ops-shell .bar-line {
  background: #e8eff8 !important;
}

/* 토폴로지 — 라이트 톤 */
.ops-shell .topo-svg line {
  stroke: #cbd5e1 !important;
}
.ops-shell .topo-svg :deep(circle[fill^="rgba(217"]) {
  fill: rgba(220, 38, 38, 0.1) !important;
}
.ops-shell .topo-legend {
  color: #0c1f40;
}
.ops-shell .dt.gr {
  background: #059669;
}
.ops-shell .dt.yl {
  background: #dc6803;
}
.ops-shell .dt.rd {
  background: #dc2626;
}

/* ============================================================
   ★ 카메라 상세 모달
   ============================================================ */
.cam-modal-bg {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(12, 31, 64, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.cam-modal {
  width: min(900px, 95vw);
  max-height: 90vh;
  background: #ffffff;
  border: 1px solid #b8c5d8;
  border-radius: 6px;
  box-shadow: 0 16px 48px rgba(12, 31, 64, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.cm-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-bottom: 1px solid #c9d4e3;
}
.cm-title {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 700;
  color: #0c1f40;
}
.cm-title i {
  color: #2563eb;
  font-size: 13.5px;
}
.cm-title .stat {
  font-size: 13px !important;
  padding: 3px 9px !important;
}
.cm-x {
  width: 32px;
  height: 32px;
  border-radius: 3px;
  background: transparent;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.cm-x:hover {
  background: #f1f5fb;
}

.cm-body {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  padding: 18px;
  gap: 18px;
  overflow: auto;
}
/* 좌측 스트림 영역 */
.cm-stream {
  position: relative;
  background: #06101e;
  border-radius: 4px;
  aspect-ratio: 16 / 10;
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.cm-stream-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.55);
}
.cm-stream-inner > i {
  font-size: 48px;
  opacity: 0.35;
}
.cm-stream-lab {
  font-size: 13px;
}
.cm-stream-id {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}
.cm-stream-time {
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13.5px;
  color: rgba(255, 255, 255, 0.45);
}
.cm-live {
  position: absolute;
  top: 12px;
  left: 12px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(220, 38, 38, 0.85);
  color: #fff;
  padding: 3px 10px;
  border-radius: 3px;
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.cm-live i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #fff;
  animation: blink 1.2s ease-in-out infinite;
}
@keyframes blink {
  50% {
    opacity: 0.3;
  }
}
.cm-offline {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(180, 83, 9, 0.85);
  color: #fff;
  padding: 3px 10px;
  border-radius: 3px;
  font-size: 13.5px;
  font-weight: 700;
}

/* 우측 정보 */
.cm-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cm-row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  border-bottom: 1px solid #e3e9f2;
  font-size: 13px;
}
.cm-row span {
  color: rgba(12, 31, 64, 0.78);
}
.cm-row strong {
  color: #0c1f40;
  font-weight: 700;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  font-size: 13px;
}
.cm-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  margin-top: 12px;
}
.cm-actions .ab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 3px;
  border: 0;
  cursor: pointer;
  font-family: inherit;
}
.cm-actions .ab.bl {
  background: #2563eb;
  color: #fff;
}
.cm-actions .ab.gy {
  background: #f1f5fb;
  color: #0c1f40;
  border: 1px solid #c9d4e3;
}
.cm-actions .ab.rd {
  background: #dc2626;
  color: #fff;
}

/* ★ 알람 상세 모달 — 간결 */
.alarm-modal {
  width: min(560px, 95vw);
}
.am-body {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.am-msg {
  font-size: 13.5px;
  font-weight: 600;
  color: #0c1f40;
  padding: 12px 14px;
  background: #f1f5fb;
  border-left: 3px solid #2563eb;
  border-radius: 2px;
  line-height: 1.5;
}
.alarm-modal .cm-actions {
  grid-template-columns: 1fr 1fr;
  margin-top: 6px;
}

/* ============================================================
   ★ 탭 패널 상세 — 헤더 / 요약 박스 / 표 / 푸터
   ============================================================ */
.ops-shell .pnl-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 12px;
}
.ops-shell .pnl-tools {
  display: flex;
  gap: 8px;
  align-items: center;
}
.ops-shell .pnl-search-i {
  background: #ffffff !important;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 13px;
  min-width: 240px;
}
.ops-shell .pnl-tools select {
  background: #ffffff !important;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  padding: 6px 12px;
  border-radius: 3px;
  font-size: 13px;
  cursor: pointer;
}

/* 요약 박스 6개 */
.ops-shell .pnl-summary {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}
.ops-shell .ps-box {
  background: #f1f5fb;
  border: 1px solid #c9d4e3;
  border-radius: 3px;
  padding: 10px 12px;
}
.ops-shell .ps-box.gr {
  background: rgba(5, 150, 105, 0.08);
  border-color: rgba(5, 150, 105, 0.3);
}
.ops-shell .ps-box.yl {
  background: rgba(220, 104, 3, 0.08);
  border-color: rgba(220, 104, 3, 0.3);
}
.ops-shell .ps-box.rd {
  background: rgba(220, 38, 38, 0.08);
  border-color: rgba(220, 38, 38, 0.3);
}
.ops-shell .ps-l {
  font-size: 13px;
  color: rgba(12, 31, 64, 0.9);
  margin-bottom: 4px;
}
.ops-shell .ps-v {
  font-size: 13.5px;
  font-weight: 700;
  color: #0c1f40;
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  letter-spacing: -0.01em;
}
.ops-shell .ps-v span {
  font-size: 13px;
  font-weight: 500;
  color: rgba(12, 31, 64, 0.65);
  margin-left: 2px;
}
.ops-shell .ps-box.gr .ps-v {
  color: #047857;
}
.ops-shell .ps-box.yl .ps-v {
  color: #b45309;
}
.ops-shell .ps-box.rd .ps-v {
  color: #b91c1c;
}

/* 푸터 + 페이지네이션 */
.ops-shell .pnl-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #c9d4e3;
  font-size: 13.5px;
  color: rgba(12, 31, 64, 0.78);
}
.ops-shell .pnl-foot .pg-row {
  display: flex;
  gap: 2px;
}
.ops-shell .pnl-foot .pg-row button {
  background: #ffffff;
  border: 1px solid #c9d4e3;
  color: #0c1f40;
  width: 28px;
  height: 28px;
  border-radius: 2px;
  cursor: pointer;
  font-size: 13px;
}
.ops-shell .pnl-foot .pg-row button.on {
  background: #2563eb;
  border-color: #2563eb;
  color: #fff;
}
.ops-shell .pnl-empty {
  text-align: center;
  padding: 24px;
  color: rgba(12, 31, 64, 0.65);
  font-size: 13px;
}

/* 서버 탭 상세 카드 */
.ops-shell .srv-detail {
  border-bottom: 1px solid #c9d4e3 !important;
  padding: 14px 0 !important;
}
.ops-shell .srv-detail:last-of-type {
  border-bottom: 0 !important;
}
.ops-shell .srv-h-r {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ops-shell .srv-uptime {
  font-size: 13px;
  color: rgba(12, 31, 64, 0.78);
  font-family: "IBM Plex Mono", "JetBrains Mono", monospace;
  padding: 3px 8px;
  border: 1px solid #c9d4e3;
  border-radius: 2px;
}
.ops-shell .srv-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #c9d4e3;
  font-size: 13px;
  color: rgba(12, 31, 64, 0.85);
}
.ops-shell .srv-meta i {
  color: #2563eb;
  margin-right: 4px;
}
</style>
