<template>
  <div class="ops-shell">
    <aside class="side">
      <RouterLink to="/" class="brand"
        ><span class="dot"></span> Traffic <em>AS</em></RouterLink
      >
      <nav class="snav">
        <button
          v-for="n in nav"
          :key="n.id"
          class="snav-i"
          :class="{ on: tab === n.id }"
          @click="tab = n.id"
        >
          <i :class="n.icon"></i><span class="snav-lab">{{ n.label }}</span>
          <span v-if="n.bdg" class="snav-bdg">{{ n.bdg }}</span>
        </button>
      </nav>
      <SideWeather />
      <div class="side-foot">시설운영팀 v2.1.0<br />© 2026</div>
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
          <!-- 카메라 상태 -->
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
                  v-for="(c, i) in cams"
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

          <!-- 서버 상태 (3 cards with CPU/메모리/디스크/서비스 bars) -->
          <div class="card srv-card">
            <div class="ch">
              <h3>
                서버 상태 <span class="ch-kpi gr">2/3 정상</span>
                <span class="ch-kpi yl">1 경고</span>
              </h3>
              <a class="ch-link" @click="tab = 'srv'">전체 보기 ›</a>
            </div>
            <div v-for="(s, i) in servers" :key="i" class="srv">
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
              <div class="srv-bars">
                <div v-for="b in s.bars" :key="b.l" class="srv-b">
                  <div class="srv-lab">{{ b.l }}</div>
                  <div class="srv-val" :class="b.tone">{{ b.v }}</div>
                  <div class="bar">
                    <span :style="{ width: b.bar + '%', background: b.color }"></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 장애 상세 (풀 패널) -->
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
              <div class="fl-row"><span>장비 ID</span><strong>NSN-N-0023</strong></div>
              <div class="fl-row">
                <span>위치</span><strong>내부순환로 03K+150</strong>
              </div>
              <div class="fl-row">
                <span>최초 감지</span><strong>10:24:17 (8분 전)</strong>
              </div>
              <div class="fl-row">
                <span>최근 상태</span><strong>10:32:18 — 응답 없음</strong>
              </div>
              <div class="fl-row">
                <span>증상</span><strong>RTSP 스트림 타임아웃 (30s)</strong>
              </div>
              <div class="fl-row">
                <span>추정 원인</span><strong>L2 스위치 측 경로 단절 (의심)</strong>
              </div>
            </div>
            <h4>조치 이력</h4>
            <div class="hst">
              <div><span class="hst-t">10:24:17</span> 장애 자동 감지 — 임계 30s</div>
              <div><span class="hst-t">10:24:20</span> 자동 재연결 1차 — TIMEOUT</div>
              <div><span class="hst-t">10:25:05</span> 자동 재연결 2차 — TIMEOUT</div>
              <div><span class="hst-t">10:25:30</span> 경로 ping 실패 (10.20.13.42)</div>
              <div>
                <span class="hst-t">10:28:11</span> 김기사(IT) 상황 확인 — 현장 점검 예정
              </div>
            </div>
            <a class="ch-link" @click="tab = 'fault'">전체 보기 ›</a>
            <h4>권장 조치</h4>
            <p class="rec-p">
              PoE 스위치 포트(SW3-G14) 재기동 후 카메라 측 전원 확인. 30분 내 미복구 시
              현장 출동.
            </p>
            <div class="act-row">
              <button class="ab bl">재연결</button>
              <button class="ab rd">장애 등록</button>
              <button class="ab gy">점검 요청</button>
              <button class="ab gr">복구 완료</button>
            </div>
            <div class="resp-row">
              <span>담당자</span><strong>김기사 (IT)</strong
              ><button class="ab-sm">변경</button>
            </div>
            <div class="memo-row">
              <span>메모</span
              ><input v-model="failMemo" placeholder="메모를 입력하세요..." /><button
                class="ab-sm"
              >
                저장
              </button>
            </div>
          </div>
          <div class="bot-row">
            <!-- 네트워크 지연 현황 (왼쪽, 비율 3) -->
            <div class="card net-card">
              <div class="ch">
                <h3>네트워크 지연 <span class="ch-kpi">평균 128ms · 최대 286ms</span></h3>
                <a class="ch-link" @click="tab = 'net'">전체 보기 ›</a>
              </div>
              <div class="net-grid">
                <div class="nb">
                  <div class="nb-l">평균 지연</div>
                  <div class="nb-v">128 <span class="u">ms</span></div>
                  <svg viewBox="0 0 100 24" class="ns" preserveAspectRatio="none">
                    <line
                      x1="0"
                      y1="20"
                      x2="100"
                      y2="20"
                      stroke="#1f3055"
                      stroke-dasharray="2 3"
                      stroke-width="0.5"
                    />
                    <polyline
                      points="0,15 20,11 40,13 60,9 80,12 100,7"
                      fill="none"
                      stroke="#7e7ad8"
                      stroke-width="1.2"
                    />
                    <circle cx="100" cy="7" r="1.8" fill="#7e7ad8" />
                  </svg>
                </div>
                <div class="nb">
                  <div class="nb-l">최대 지연</div>
                  <div class="nb-v">286 <span class="u">ms</span></div>
                  <svg viewBox="0 0 100 24" class="ns" preserveAspectRatio="none">
                    <line
                      x1="0"
                      y1="20"
                      x2="100"
                      y2="20"
                      stroke="#1f3055"
                      stroke-dasharray="2 3"
                      stroke-width="0.5"
                    />
                    <polyline
                      points="0,16 20,12 40,15 60,5 80,9 100,3"
                      fill="none"
                      stroke="#d4a652"
                      stroke-width="1.2"
                    />
                    <circle cx="100" cy="3" r="1.8" fill="#d4a652" />
                  </svg>
                </div>
                <div class="nb nb-wide">
                  <div class="nb-l">정상 구간</div>
                  <div class="nb-v">23<span class="u">/25 (92%)</span></div>
                  <svg viewBox="0 0 100 24" class="ns" preserveAspectRatio="none">
                    <line
                      x1="0"
                      y1="20"
                      x2="100"
                      y2="20"
                      stroke="#1f3055"
                      stroke-dasharray="2 3"
                      stroke-width="0.5"
                    />
                    <polyline
                      points="0,9 20,7 40,8 60,6 80,7 100,5"
                      fill="none"
                      stroke="#6fa581"
                      stroke-width="1.2"
                    />
                    <circle cx="100" cy="5" r="1.8" fill="#6fa581" />
                  </svg>
                </div>
                <div class="nb">
                  <div class="nb-l">지연 구간</div>
                  <div class="nb-v">1<span class="u">/25 (4%)</span></div>
                  <div class="bar-line">
                    <span style="width: 4%; background: #fbbf24"></span>
                  </div>
                </div>
                <div class="nb">
                  <div class="nb-l">장애 구간</div>
                  <div class="nb-v">1<span class="u">/25 (4%)</span></div>
                  <div class="bar-line">
                    <span style="width: 4%; background: #ef4444"></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 알람 타임라인 (오른쪽, 비율 7) -->
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
                <div
                  v-for="a in filteredAlarms"
                  :key="a.id"
                  class="tl-row"
                  :class="a.kind"
                  @click="openAlarm(a)"
                  style="cursor:pointer"
                >
                  <span class="tl-t">{{ a.time }}</span>
                  <span class="tl-k">{{
                    a.kind === "recovered" ? "R" : a.kind === "info" ? "I" : "E"
                  }}</span>
                  <span class="tl-sev" :class="a.sev.toLowerCase()">{{ a.sev }}</span>
                  <span class="tl-id">{{ a.dev }}</span>
                  <span class="tl-msg">{{ a.msg }}</span>
                  <span class="tl-who">{{ a.who }}</span>
                  <i class="bi bi-chevron-right tl-arrow"></i>
                </div>
                <div v-if="!filteredAlarms.length" class="tl-empty">해당 분류 없음</div>
              </div>
              <div class="tl-foot">
                <span>표시 {{ filteredAlarms.length }} / 24</span>
                <a class="ch-link" @click="tab = 'alarm'">전체 알람 보기 ›</a>
              </div>
            </div>
          </div>
          <!-- /.bot-row -->
        </section>
      </template>

      <section v-if="tab === 'cams'" class="card pnl">
        <div class="pnl-head">
          <h3>
            카메라 전체 목록
            <span class="ch-kpi">{{ cams.length }}대 (전체 25대 중)</span>
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
          </div>
        </div>
        <div class="pnl-summary">
          <div class="ps-box">
            <div class="ps-l">전체</div>
            <div class="ps-v">25</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">23</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">지연</div>
            <div class="ps-v">1</div>
          </div>
          <div class="ps-box rd">
            <div class="ps-l">장애</div>
            <div class="ps-v">1</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 지연</div>
            <div class="ps-v">94<span>ms</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 가동률</div>
            <div class="ps-v">96.2<span>%</span></div>
          </div>
        </div>
        <table class="pnl-tbl">
          <thead>
            <tr>
              <th>장비 ID</th>
              <th>카메라명</th>
              <th>위치</th>
              <th>IP</th>
              <th>상태</th>
              <th>지연(ms)</th>
              <th>가동률</th>
              <th>최근 응답</th>
              <th>설치일</th>
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
              <td class="mono">{{ c.lat }}</td>
              <td class="mono">{{ (95 + (i % 5)).toFixed(1) }}%</td>
              <td class="mono">{{ c.ts }}</td>
              <td class="mono">
                {{
                  [
                    "2024-03-12",
                    "2024-05-08",
                    "2024-08-22",
                    "2023-11-15",
                    "2024-01-30",
                    "2024-06-17",
                    "2024-02-04",
                    "2024-09-11",
                  ][i]
                }}
              </td>
              <td><i class="bi bi-chevron-right" style="opacity: 0.5"></i></td>
            </tr>
            <tr v-if="!filteredCams.length">
              <td colspan="10" class="pnl-empty">검색 결과 없음</td>
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
      </section>

      <section v-if="tab === 'srv'" class="card pnl">
        <div class="pnl-head">
          <h3>
            서버 / OCR 엔진 상태 <span class="ch-kpi">{{ servers.length }}대 운영</span>
          </h3>
        </div>
        <div class="pnl-summary">
          <div class="ps-box">
            <div class="ps-l">전체</div>
            <div class="ps-v">3</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">2</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">경고</div>
            <div class="ps-v">1</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 CPU</div>
            <div class="ps-v">42<span>%</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 메모리</div>
            <div class="ps-v">55<span>%</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">서비스 가동</div>
            <div class="ps-v">14<span>/15</span></div>
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
      </section>

      <section v-if="tab === 'net'" class="card pnl">
        <div class="pnl-head">
          <h3>
            네트워크 지연 현황
            <span class="ch-kpi">{{ netPaths.length }}개 경로 모니터링</span>
          </h3>
        </div>
        <div class="pnl-summary">
          <div class="ps-box">
            <div class="ps-l">평균 지연</div>
            <div class="ps-v">128<span>ms</span></div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">최대 지연</div>
            <div class="ps-v">286<span>ms</span></div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">정상</div>
            <div class="ps-v">23<span>/25</span></div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">지연</div>
            <div class="ps-v">1<span>/25</span></div>
          </div>
          <div class="ps-box rd">
            <div class="ps-l">장애</div>
            <div class="ps-v">1<span>/25</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">패킷 손실</div>
            <div class="ps-v">0.02<span>%</span></div>
          </div>
        </div>
        <table class="pnl-tbl">
          <thead>
            <tr>
              <th>경로</th>
              <th>출발지</th>
              <th>도착지</th>
              <th>지연(ms)</th>
              <th>지연 24h 평균</th>
              <th>패킷 손실</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(p, i) in netPaths" :key="i">
              <td class="mono">PATH-{{ String(i + 1).padStart(3, "0") }}</td>
              <td>{{ p.from }}</td>
              <td>{{ p.to }}</td>
              <td class="mono">{{ p.lat }}</td>
              <td class="mono">{{ p.avg }}</td>
              <td class="mono">{{ p.loss }}%</td>
              <td>
                <span class="stat" :class="p.tone">{{ p.st }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section v-if="tab === 'alarm'" class="card pnl">
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
          </div>
        </div>
        <div class="pnl-summary">
          <div class="ps-box rd">
            <div class="ps-l">CRIT</div>
            <div class="ps-v">3</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">HIGH</div>
            <div class="ps-v">5</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">MED</div>
            <div class="ps-v">8</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">INFO</div>
            <div class="ps-v">12</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">해결됨 24h</div>
            <div class="ps-v">17</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 응답시간</div>
            <div class="ps-v">4.2<span>분</span></div>
          </div>
        </div>
        <table class="pnl-tbl">
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
            <div class="ps-v" style="font-size: 14px">05-19 02:00</div>
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

      <section v-if="tab === 'fault'" class="card pnl">
        <div class="pnl-head">
          <h3>장애 관리 <span class="ch-kpi rd">진행 1 · 처리중 2 · 완료 5</span></h3>
        </div>
        <div class="pnl-summary">
          <div class="ps-box rd">
            <div class="ps-l">진행 중</div>
            <div class="ps-v">1</div>
          </div>
          <div class="ps-box yl">
            <div class="ps-l">처리 중</div>
            <div class="ps-v">2</div>
          </div>
          <div class="ps-box gr">
            <div class="ps-l">금일 복구</div>
            <div class="ps-v">5</div>
          </div>
          <div class="ps-box">
            <div class="ps-l">평균 복구시간</div>
            <div class="ps-v">18<span>분</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">최장 지연</div>
            <div class="ps-v">2<span>h 14m</span></div>
          </div>
          <div class="ps-box">
            <div class="ps-l">자동 복구율</div>
            <div class="ps-v">73<span>%</span></div>
          </div>
        </div>
        <table class="pnl-tbl">
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
              <td class="mono">{{ f.elapsed }}</td>
              <td>
                <span class="stat" :class="f.stTone">{{ f.st }}</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="faultMsg" class="set-msg">{{ faultMsg }}</div>
      </section>

      <section v-if="tab === 'reports'" class="card pnl">
        <h3>장비 보고서</h3>
        <div class="rep-rows">
          <div v-for="r in reportRows" :key="r.t" class="rep-r">
            <i class="bi bi-file-earmark-text"></i>
            <div>
              <strong>{{ r.t }}</strong
              ><span>{{ r.d }}</span>
            </div>
            <button class="bt-dl"><i class="bi bi-download"></i></button>
          </div>
        </div>
      </section>

      <section v-if="tab === 'settings'" class="card pnl">
        <h3>설정</h3>
        <div class="set-row">
          <label>자동 재연결 시도</label
          ><input type="checkbox" v-model="setAutoReconnect" />
        </div>
        <div class="set-row">
          <label>지연 경고 임계값 (ms)</label
          ><input type="number" v-model.number="setLatThreshold" min="50" max="1000" />
        </div>
        <div class="set-row">
          <label>알림 채널</label>
          <select v-model="setChannel">
            <option>이메일</option>
            <option>SMS</option>
            <option>슬랙</option>
          </select>
        </div>
        <button class="btn-save" @click="saveSet">
          <i class="bi bi-check2"></i> 저장
        </button>
        <div v-if="setMsg" class="set-msg">{{ setMsg }}</div>
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
            <i :class="alarmModal.kind === 'recovered' ? 'bi bi-check-circle-fill'
                     : alarmModal.kind === 'info' ? 'bi bi-info-circle-fill'
                     : 'bi bi-exclamation-triangle-fill'"
               :style="{color: alarmModal.kind === 'recovered' ? '#059669'
                              : alarmModal.kind === 'info' ? '#2563eb' : '#dc2626'}"></i>
            <span>알람 상세</span>
            <span class="stat" :class="alarmModal.sev.toLowerCase() === 'crit' ? 'no'
                                      : alarmModal.sev.toLowerCase() === 'high' || alarmModal.sev.toLowerCase() === 'med' ? 'wn'
                                      : 'ok'">{{ alarmModal.sev }}</span>
          </div>
          <button class="cm-x" @click="alarmModal = null" aria-label="닫기">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
        <div class="am-body">
          <div class="am-msg">{{ alarmModal.msg }}</div>
          <div class="cm-row"><span>발생 시각</span><strong>{{ alarmModal.time }}</strong></div>
          <div class="cm-row"><span>장비</span><strong>{{ alarmModal.dev }}</strong></div>
          <div class="cm-row"><span>심각도</span><strong>{{ alarmModal.sev }}</strong></div>
          <div class="cm-row"><span>담당자</span><strong>{{ alarmModal.who }}</strong></div>
          <div class="cm-row"><span>유형</span><strong>{{
            alarmModal.kind === 'recovered' ? '복구'
            : alarmModal.kind === 'info' ? '정보' : '이벤트' }}</strong></div>
          <div class="cm-actions">
            <button class="ab bl"><i class="bi bi-arrow-right-circle"></i> 처리 시작</button>
            <button class="ab gy"><i class="bi bi-share"></i> 담당자 변경</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink } from "vue-router";
import DeptSwitcher from "@/components/dashboard/DeptSwitcher.vue";
import SideWeather from "@/components/dashboard/SideWeather.vue";

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
function openAlarm(a) { alarmModal.value = a; }
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
  {
    from: "GBS-E-0055",
    to: "ocr-srv-02",
    lat: 19.4,
    avg: 20.1,
    loss: 0.0,
    st: "정상",
    tone: "ok",
  },
  {
    from: "DBG-N-0060",
    to: "ocr-srv-01",
    lat: 18.9,
    avg: 19.7,
    loss: 0.0,
    st: "정상",
    tone: "ok",
  },
  {
    from: "GBG-S-0077",
    to: "ocr-srv-02",
    lat: 286,
    avg: 142.3,
    loss: 1.8,
    st: "지연",
    tone: "wn",
  },
  {
    from: "BBG-E-0088",
    to: "ocr-srv-01",
    lat: 102,
    avg: 98.4,
    loss: 0.0,
    st: "정상",
    tone: "ok",
  },
  {
    from: "SBG-S-0099",
    to: "ocr-srv-02",
    lat: 109,
    avg: 105.2,
    loss: 0.0,
    st: "정상",
    tone: "ok",
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
  {
    id: 4,
    time: "13:55:18",
    sev: "INFO",
    tone: "ok",
    cat: "복구",
    dev: "CAM-IC-0011",
    msg: "연결 복구 (재기동 후 정상)",
    who: "이대리",
    handled: true,
  },
  {
    id: 5,
    time: "13:30:01",
    sev: "INFO",
    tone: "ok",
    cat: "시스템",
    dev: "NET-CORE-1",
    msg: "라우팅 테이블 재구성 완료",
    who: "—",
    handled: true,
  },
  {
    id: 6,
    time: "12:48:22",
    sev: "MED",
    tone: "wn",
    cat: "카메라",
    dev: "GBN-S-0032",
    msg: "이미지 노이즈 임계치 초과 (자동필터)",
    who: "자동",
    handled: true,
  },
  {
    id: 7,
    time: "11:15:09",
    sev: "INFO",
    tone: "ok",
    cat: "복구",
    dev: "OLP-W-0041",
    msg: "전원 차단 후 복구",
    who: "박과장",
    handled: true,
  },
  {
    id: 8,
    time: "10:32:11",
    sev: "CRIT",
    tone: "no",
    cat: "보안",
    dev: "FW-EDGE-1",
    msg: "비정상 패킷 다수 감지 (차단 처리)",
    who: "보안팀",
    handled: true,
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
  {
    id: 4,
    date: "2026-05-23 02:30",
    type: "임시",
    dev: "NSN-N-0023",
    who: "김기사",
    dur: "20분",
    scope: "카메라 1대",
    st: "예정",
    tone: "wait",
  },
  {
    id: 5,
    date: "2026-05-17 02:00",
    type: "정기",
    dev: "search-srv",
    who: "이대리",
    dur: "35분",
    scope: "검색 일시 중단",
    st: "완료",
    tone: "ok",
  },
  {
    id: 6,
    date: "2026-05-15 03:00",
    type: "정기",
    dev: "ocr-srv-02",
    who: "김기사",
    dur: "30분",
    scope: "Standby 점검",
    st: "완료",
    tone: "ok",
  },
  {
    id: 7,
    date: "2026-05-14 02:00",
    type: "임시",
    dev: "BBG-E-0088",
    who: "박과장",
    dur: "15분",
    scope: "카메라 1대",
    st: "완료",
    tone: "ok",
  },
  {
    id: 8,
    date: "2026-05-13 23:00",
    type: "긴급",
    dev: "FW-EDGE-1",
    who: "보안팀",
    dur: "50분",
    scope: "외부 트래픽 5분 차단",
    st: "지연",
    tone: "wn",
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
  {
    id: "FLT-2026-00339",
    time: "06:55:20",
    dev: "OLP-W-0041",
    symp: "전원 차단",
    sev: "HIGH",
    tone: "wn",
    who: "박과장",
    elapsed: "—",
    st: "복구 완료",
    stTone: "ok",
  },
  {
    id: "FLT-2026-00338",
    time: "05:02:48",
    dev: "CAM-IC-0011",
    symp: "신호 단절",
    sev: "MED",
    tone: "wn",
    who: "김기사",
    elapsed: "—",
    st: "복구 완료",
    stTone: "ok",
  },
  {
    id: "FLT-2026-00337",
    time: "04:30:12",
    dev: "FW-EDGE-1",
    symp: "비정상 패킷 감지",
    sev: "CRIT",
    tone: "no",
    who: "보안팀",
    elapsed: "—",
    st: "복구 완료",
    stTone: "ok",
  },
  {
    id: "FLT-2026-00336",
    time: "02:14:09",
    dev: "DB-PRIMARY",
    symp: "슬로 쿼리 다수",
    sev: "MED",
    tone: "wn",
    who: "이대리",
    elapsed: "—",
    st: "복구 완료",
    stTone: "ok",
  },
  {
    id: "FLT-2026-00335",
    time: "01:08:44",
    dev: "NET-CORE-1",
    symp: "라우팅 플랩",
    sev: "HIGH",
    tone: "wn",
    who: "박과장",
    elapsed: "—",
    st: "복구 완료",
    stTone: "ok",
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
  {
    id: 4,
    time: "13:55:18",
    kind: "recovered",
    sev: "-",
    dev: "CAM-IC-0011",
    msg: "연결 복구 (재기동 후 정상)",
    who: "이대리",
  },
  {
    id: 5,
    time: "13:30:01",
    kind: "info",
    sev: "-",
    dev: "NET-CORE-1",
    msg: "라우팅 테이블 재구성 완료",
    who: "—",
  },
  {
    id: 6,
    time: "12:48:22",
    kind: "event",
    sev: "MED",
    dev: "GBN-S-0032",
    msg: "이미지 노이즈 임계치 초과 (자동필터)",
    who: "자동",
  },
  {
    id: 7,
    time: "11:15:09",
    kind: "recovered",
    sev: "-",
    dev: "OLP-W-0041",
    msg: "전원 차단 후 복구",
    who: "박과장",
  },
]);
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
  {
    name: "서울TG_4번부스_A1",
    loc: "경부 13K+450",
    st: "정상",
    stTone: "ok",
    lat: 112,
    ts: "10:32:16",
    id: "GBS-E-0055",
  },
  {
    name: "수락산_분기_D3",
    loc: "동부간선 22K+700",
    st: "정상",
    stTone: "ok",
    lat: 88,
    ts: "10:32:09",
    id: "DBG-N-0060",
  },
  {
    name: "잠원IC_본선_B2",
    loc: "경부 02K+050",
    st: "지연",
    stTone: "wn",
    lat: 286,
    ts: "10:31:42",
    id: "GBG-S-0077",
  },
  {
    name: "월계분기점_C1",
    loc: "북부간선 06K+300",
    st: "정상",
    stTone: "ok",
    lat: 102,
    ts: "10:31:55",
    id: "BBG-E-0088",
  },
  {
    name: "금천IC_본선_A3",
    loc: "서부간선 11K+900",
    st: "정상",
    stTone: "ok",
    lat: 109,
    ts: "10:32:01",
    id: "SBG-S-0099",
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
    name: "ocr-srv-02",
    tag: "Standby",
    ip: "10.20.10.12",
    st: "정상",
    stTone: "ok",
    bars: [
      { l: "CPU", v: "21.5%", bar: 22, color: "#6fa581", tone: "" },
      { l: "메모리", v: "40.9%", bar: 41, color: "#6fa581", tone: "" },
      { l: "디스크", v: "34.6%", bar: 35, color: "#6fa581", tone: "" },
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
  {
    id: 4,
    time: "09:30:48",
    dev: "NET-CORE-1",
    sev: "정보",
    tone: "ok",
    msg: "경로 재구성 완료",
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
  { t: "장비 가동률 보고서", d: "2026-05-17 생성" },
  { t: "장애 발생 이력", d: "최근 30일 누적" },
  { t: "네트워크 지연 분석", d: "주간 분석 보고서" },
]);
const faultMsg = ref("");
const setAutoReconnect = ref(true);
const setLatThreshold = ref(200);
const setChannel = ref("이메일");
const setMsg = ref("");
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
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 100px;
  min-width: 16px;
  text-align: center;
}
.side-foot {
  font-size: 10px;
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

.kpi-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr) auto;
  gap: 12px;
}
.kpi {
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  gap: 10px;
  align-items: center;
}
.k-ic {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}
.k-ic.gr {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
}
.k-ic.rd {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}
.k-ic.bl {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
}
.k-ic.pl {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
}
.k-ic.pk {
  background: rgba(236, 72, 153, 0.15);
  color: #f472b6;
}
.k-body {
  flex: 1;
  min-width: 0;
}
.k-lab {
  font-size: 11.5px;
  opacity: 0.75;
}
.k-val {
  font-size: 22px;
  font-weight: 800;
}
.k-val.rd {
  color: #f87171;
}
.k-val .warn {
  color: #fbbf24;
}
.k-u {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.65;
  margin-left: 2px;
}
.k-tag {
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 4px;
}
.k-tag.yl {
  background: rgba(251, 191, 36, 0.18);
  color: #fbbf24;
}
.k-link,
.k-side {
  font-size: 11.5px;
  opacity: 0.55;
  cursor: pointer;
}
.k-side {
  font-size: 12px;
  font-weight: 700;
  color: #34d399;
  opacity: 1;
}
.kpi-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  justify-content: center;
  font-size: 11px;
  padding: 0 10px;
}
.km-t {
  opacity: 0.65;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.km-r {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid #1f3055;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}
.sw {
  display: inline-block;
  width: 26px;
  height: 14px;
  background: #34d399;
  border-radius: 8px;
  position: relative;
}
.sw-d {
  position: absolute;
  right: 1px;
  top: 1px;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
}

.grid-mid {
  display: grid;
  grid-template-columns: 1.7fr 1fr;
  gap: 14px;
  align-items: stretch;
}
.grid-mid > .card {
  display: flex;
  flex-direction: column;
}
.grid-bot {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 14px;
}
.card {
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 10px;
  padding: 14px;
}
.card h3 {
  font-size: 14px;
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
  font-size: 11.5px;
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
  font-size: 11px;
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
  font-size: 11px;
}

.cam-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
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
  font-size: 10.5px;
}
.cam-tbl tr.bad {
  background: rgba(239, 68, 68, 0.05);
}
.cam-tbl tr.bad td {
  color: #fca5a5;
}
.cam-tbl .mono {
  font-family: "JetBrains Mono", monospace;
}
.cf {
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.03);
}
.cf.on {
  background: rgba(96, 165, 250, 0.18);
  color: #60a5fa;
}
.act-col {
  display: flex;
  gap: 8px;
  align-items: center;
}
.act-col i {
  cursor: pointer;
  opacity: 0.55;
}
.act-col i:hover {
  opacity: 1;
  color: #60a5fa;
}
.dev-empty {
  text-align: center;
  opacity: 0.5;
  padding: 16px 0;
}

.srv-tbl-card {
  display: flex;
  flex-direction: column;
}
.srv-tbl-card .srv-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  flex: 1;
}
.srv-tbl-card .srv-tbl tbody tr {
  height: 100%;
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
.srv-tbl th,
.srv-tbl td {
  padding: 9px 8px;
  text-align: left;
  border-bottom: 1px solid #1a2a45;
}
.srv-tbl th {
  font-weight: 600;
  opacity: 0.55;
  font-size: 11px;
}
.srv-tbl .mono {
  font-family: "JetBrains Mono", monospace;
}
.srv-tbl .sn-tag {
  font-size: 10.5px;
  opacity: 0.55;
  font-weight: 400;
}
.stat {
  padding: 1px 8px;
  border-radius: 100px;
  font-size: 10.5px;
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
  font-size: 11px;
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
  font-size: 10px;
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
  padding: 10px 0;
  border-bottom: 1px solid #1a2a45;
  flex: 1; /* 카드 높이를 3등분 */
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 0;
}
.srv:last-of-type {
  border-bottom: 0;
}
.srv-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.srv-name {
  display: flex;
  gap: 8px;
  align-items: center;
}
.srv-name > i {
  font-size: 18px;
  color: #60a5fa;
}
.sn-t {
  font-size: 12.5px;
  font-weight: 700;
}
.sn-tag {
  font-size: 10.5px;
  opacity: 0.55;
  font-weight: 400;
  margin-left: 4px;
}
.sn-ip {
  font-size: 10.5px;
  opacity: 0.55;
  font-family: "JetBrains Mono", monospace;
}
.srv-bars {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  gap: 8px;
}
.srv-b {
  font-size: 10.5px;
}
.srv-lab {
  opacity: 0.65;
}
.srv-val {
  font-weight: 700;
  font-size: 12px;
  margin: 2px 0 4px;
}
.srv-val.yl {
  color: #fbbf24;
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
  font-size: 10.5px;
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
  font-size: 10.5px;
  padding: 1px 6px;
  border-radius: 3px;
  margin-left: 6px;
}
.fl-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 11.5px;
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
  font-size: 12px;
  font-weight: 700;
  margin: 10px 0 6px;
}
.hst {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11px;
  padding-left: 4px;
  margin-bottom: 4px;
}
.hst-t {
  color: #60a5fa;
  font-family: "JetBrains Mono", monospace;
  margin-right: 6px;
}
.rec-p {
  font-size: 11px;
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
  font-size: 12px;
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
  font-size: 11.5px;
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
  font-size: 11px;
}
.ab-sm {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 10.5px;
  cursor: pointer;
}

.net-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.nb {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid #1a2a45;
  border-radius: 6px;
  padding: 10px;
}
.nb-l {
  font-size: 11px;
  opacity: 0.75;
  margin-bottom: 4px;
}
.nb-v {
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 4px;
}
.nb-v .u {
  font-size: 11px;
  opacity: 0.65;
  font-weight: 500;
}
.ns {
  width: 100%;
  height: 24px;
}
.bar-line {
  height: 4px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
}
.bar-line span {
  display: block;
  height: 100%;
  border-radius: 4px;
}

.topo-legend {
  display: flex;
  gap: 10px;
  font-size: 11px;
  margin-bottom: 8px;
}
.dt {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
}
.dt.gr {
  background: #34d399;
}
.dt.yl {
  background: #fbbf24;
}
.dt.rd {
  background: #ef4444;
}
.topo-svg {
  width: 100%;
  height: 240px;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 18px;
  background: #0f1d34;
  border: 1px solid #1f3055;
  border-radius: 10px;
  flex-wrap: wrap;
}
.sb-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 18px;
  border-right: 1px solid #1a2a45;
  font-size: 13px;
}
.sb-item:last-of-type {
  border-right: 0;
}
.sb-item i {
  font-size: 17px;
}
.sb-l {
  opacity: 0.75;
}
.sb-item strong {
  font-size: 17px;
  font-weight: 800;
}
.sb-item strong.yl {
  color: #fbbf24;
}
.sb-item strong.rd {
  color: #f87171;
}
.sb-u {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.6;
  margin-left: 2px;
}
.sb-spacer {
  flex: 1;
}
.sb-ts {
  font-size: 11.5px;
  opacity: 0.6;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.sb-ts::before {
  content: "○";
  opacity: 0.5;
}
.sb-refresh {
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 12.5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.row-summary {
  display: grid;
  grid-template-columns: 1.4fr 1fr 0.85fr;
  gap: 12px;
  align-items: stretch;
}
.row-summary > .card {
  display: flex;
  flex-direction: column;
}
.row-summary .net-spark,
.row-summary .fault-sum {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.row-summary .dn-grid {
  flex: 1;
  align-items: center;
}
.row-summary .fault-sum .fs-btn {
  margin-top: auto;
}
.dn-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.dn-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.dn-h {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.85;
}
.dn-wrap {
  position: relative;
  width: 160px;
  height: 160px;
}
.dn-wrap .donut {
  width: 100%;
  height: 100%;
}
.dn-c {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.dn-v {
  font-size: 26px;
  font-weight: 800;
}
.dn-s {
  font-size: 11.5px;
  opacity: 0.75;
  margin-top: 2px;
}
.dn-leg {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 11.5px;
  opacity: 0.85;
}
.dn-leg > div {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: space-between;
}
.lg {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.lg.gr {
  background: #34d399;
}
.lg.yl {
  background: #fbbf24;
}
.lg.rd {
  background: #ef4444;
}
.lg.gy {
  background: #6b7280;
}
.dn-leg > div > span:first-child {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}
.dn-leg > div > span:first-child::after {
  content: "";
}
.dn-leg strong {
  font-weight: 700;
}

.net-spark {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ns-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.05);
  gap: 10px;
}
.ns-row:last-of-type {
  border-bottom: 0;
}
.ns-l {
  font-size: 12px;
  opacity: 0.75;
  margin-bottom: 4px;
}
.ns-v {
  font-size: 18px;
  font-weight: 800;
}
.ns-v.gr {
  color: #34d399;
}
.ns-v span {
  font-size: 11px;
  font-weight: 500;
  opacity: 0.65;
  margin-left: 2px;
}
.ns-sp {
  width: 100px;
  height: 30px;
}

.fault-sum h3 {
  margin-bottom: 14px;
}
.fs-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #1a2a45;
  font-size: 12.5px;
}
.fs-row > i {
  font-size: 16px;
}
.fs-row > span {
  flex: 1;
}
.fs-row strong {
  font-weight: 800;
}
.fs-row strong.rd {
  color: #f87171;
}
.fs-row strong.yl {
  color: #fbbf24;
}
.fs-row strong.gr {
  color: #34d399;
}
.fs-btn {
  width: 100%;
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 9px;
  border-radius: 6px;
  margin-top: 12px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

/* 토폴로지(좌, 큰) + 나머지 4개 (우, 2x2) */
.grid-bot-new {
  display: grid;
  grid-template-columns: 1.1fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 12px;
  align-items: stretch;
}
.grid-bot-new > .card {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.topo-new {
  grid-row: 1 / span 2;
  grid-column: 1;
}
.topo-svg-new {
  width: 100%;
  height: 100%;
  min-height: 320px;
  display: block;
  flex: 1;
}
.lat-detail .pnl-tbl.small th,
.lat-detail .pnl-tbl.small td {
  padding: 6px 8px;
  font-size: 11.5px;
}
.lat-btn {
  width: 100%;
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 8px;
  border-radius: 5px;
  margin-top: 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.flt-queue,
.check-sched,
.recent-evt {
  padding: 14px;
}
.ch {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.ch-link {
  font-size: 11px;
  color: #60a5fa;
  cursor: pointer;
}
.fq-row {
  display: grid;
  grid-template-columns: 18px 1fr auto auto;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #1a2a45;
  align-items: center;
  font-size: 12px;
}
.fq-row > i {
  color: #f87171;
}
.fq-t {
  font-size: 12px;
  font-weight: 600;
}
.fq-id {
  font-size: 10.5px;
  opacity: 0.55;
  font-family: "JetBrains Mono", monospace;
}
.fq-time {
  font-size: 10.5px;
  opacity: 0.65;
  font-family: "JetBrains Mono", monospace;
}
.fq-tag {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
}

.cs-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px;
  padding: 8px 0;
  border-bottom: 1px solid #1a2a45;
  align-items: center;
}
.cs-t {
  font-size: 11.5px;
  font-weight: 600;
  grid-column: 1;
}
.cs-d {
  font-size: 11px;
  opacity: 0.7;
  grid-column: 1;
}
.cs-tag {
  grid-column: 2;
  grid-row: 1 / span 2;
  background: rgba(96, 165, 250, 0.18);
  color: #60a5fa;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.re-row {
  display: grid;
  grid-template-columns: 10px 60px 36px 1fr;
  gap: 8px;
  padding: 7px 0;
  border-bottom: 1px solid #1a2a45;
  align-items: center;
  font-size: 11.5px;
}
.re-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.re-dot.rd {
  background: #ef4444;
}
.re-dot.yl {
  background: #fbbf24;
}
.re-dot.gr {
  background: #34d399;
}
.re-time {
  opacity: 0.7;
  font-size: 10.5px;
}
.re-sev {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 3px;
  text-align: center;
}
.re-sev.rd {
  background: rgba(239, 68, 68, 0.18);
  color: #f87171;
}
.re-sev.yl {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}
.re-sev.gr {
  background: rgba(16, 185, 129, 0.18);
  color: #34d399;
}
.re-msg {
  opacity: 0.85;
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
  font-size: 15.5px;
  line-height: 1.55;
  background: #d6deeb !important;
  color: #0c1f40 !important;
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
  font-size: 22px !important;
  font-weight: 700 !important;
}
.ops-shell :deep(.t-sub) {
  color: #0c1f40 !important;
}
.ops-shell :deep(.t-main) {
  color: #0c1f40 !important;
  text-decoration: none !important;
  font-size: 22px !important;
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
  font-size: 12px !important;
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
  font-size: 17px !important;
}
.ops-shell :deep(.ds-t) {
  color: #0c1f40 !important;
  font-weight: 700 !important;
  font-size: 14.5px !important;
}
.ops-shell :deep(.ds-s) {
  color: #0c1f40 !important;
  opacity: 0.8 !important;
  font-size: 12.5px !important;
}
.ops-shell :deep(.ds-arr) {
  color: #0c1f40 !important;
  opacity: 0.55 !important;
  font-size: 12px !important;
}
.ops-shell :deep(.ds-cur) {
  font-size: 11px !important;
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
  font-size: 15.5px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #0c1f40;
  padding-bottom: 8px;
  border-bottom: 1px solid #c9d4e3;
}
.ops-shell :deep(.ch) {
  padding-bottom: 8px;
  border-bottom: 1px solid #e3e9f2;
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
  font-size: 16px;
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
  font-size: 14px;
  padding: 9px 11px;
  border-radius: 2px;
  transition: none;
}
.ops-shell :deep(.snav-i i) {
  font-size: 15px;
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
  font-size: 11.5px;
  border-radius: 2px;
  min-width: 18px;
}
.ops-shell :deep(.top h1) {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.ops-shell :deep(.t-sub) {
  font-size: 14px;
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
  font-size: 14px;
}
.ops-shell :deep(.bdg) {
  background: #b94545;
  min-width: 15px;
  height: 15px;
  font-size: 9.5px;
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

/* 상단 통계 바 */
.stat-bar {
  padding: 12px 16px !important;
  border-radius: 3px !important;
  gap: 20px !important;
}
.sb-item {
  padding-right: 16px !important;
  gap: 8px !important;
  font-size: 12.5px;
}
.sb-item i {
  font-size: 15px !important;
}
.sb-item strong {
  font-size: 17px !important;
  font-weight: 700;
  font-family: "JetBrains Mono", monospace;
}
.sb-u {
  font-size: 11px !important;
}
.sb-ts {
  font-size: 11.5px;
  font-family: "JetBrains Mono", monospace;
}
.sb-refresh {
  background: #2a4a78 !important;
  padding: 6px 12px !important;
  border-radius: 2px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}
.sb-refresh i {
  font-size: 12px;
}

/* 그리드 gap */
.row-summary,
.grid-mid,
.grid-bot-new {
  gap: 10px !important;
}
.main {
  gap: 10px !important;
}

/* 도넛 */
.dn-h {
  font-size: 12px !important;
  opacity: 0.75;
}
.dn-v {
  font-size: 22px !important;
  font-family: "JetBrains Mono", monospace;
}
.dn-s {
  font-size: 11px !important;
}
.dn-leg {
  font-size: 11.5px !important;
  gap: 4px !important;
}
.dn-leg strong {
  font-family: "JetBrains Mono", monospace;
  font-weight: 600;
}
.dn-wrap {
  width: 120px !important;
  height: 120px !important;
}
.lg {
  width: 9px !important;
  height: 9px !important;
  border-radius: 0 !important;
}

/* 네트워크 sparkline */
.ns-row {
  padding: 7px 0 !important;
}
.ns-l {
  font-size: 12px !important;
  opacity: 0.75;
  margin-bottom: 3px !important;
}
.ns-v {
  font-size: 17px !important;
  font-family: "JetBrains Mono", monospace;
}
.ns-v.gr {
  color: #6fa581;
}
.ns-v span {
  font-size: 11px !important;
}
.ns-sp {
  width: 90px !important;
  height: 26px !important;
}

/* 장애 요약 */
.fs-row {
  padding: 9px 0 !important;
  font-size: 13px !important;
}
.fs-row i {
  font-size: 15px !important;
}
.fs-row strong {
  font-family: "JetBrains Mono", monospace;
  font-weight: 600;
  font-size: 13px;
}
.fs-row strong.rd {
  color: #d97070;
}
.fs-row strong.yl {
  color: #d4a652;
}
.fs-row strong.gr {
  color: #6fa581;
}
.fs-btn {
  background: #2a4a78 !important;
  border-radius: 2px !important;
  padding: 8px !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
  margin-top: 10px !important;
}

/* 장비 상태 목록 */
.cam-filter {
  font-size: 13px;
  gap: 6px;
  margin-bottom: 12px;
}
.cf {
  padding: 5px 11px !important;
  border-radius: 2px !important;
  font-size: 12.5px !important;
  font-weight: 500 !important;
}
.cf.on {
  background: rgba(120, 160, 210, 0.22) !important;
  color: #c4d8f5 !important;
}
.cf-r input,
.cf-r select {
  background: #06101e;
  border: 1px solid #1f3055;
  color: #d4dbe7;
  padding: 5px 10px;
  border-radius: 2px;
  font-size: 12.5px;
}

.cam-tbl {
  font-size: 14.5px !important;
}
.cam-tbl th {
  padding: 8px !important;
  font-size: 13px !important;
  opacity: 0.85;
  font-weight: 700;
}
.cam-tbl td {
  padding: 8px !important;
  font-size: 14px;
}
.cam-tbl tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
} /* 격행 */
.cam-tbl tr.bad {
  background: rgba(185, 69, 69, 0.08);
}
.cam-tbl tr.bad td {
  color: #d97070;
}
.cam-tbl tr.bad td.mono {
  color: #d97070;
}
.cam-tbl .mono {
  font-family: "JetBrains Mono", monospace;
  font-size: 12.5px;
}
.cam-tbl td > i {
  font-size: 14px;
  opacity: 0.65;
}

.act-col i {
  font-size: 14px !important;
}
.cam-foot .pg-row button {
  width: 26px;
  height: 26px;
  font-size: 12.5px;
  border-radius: 2px;
}
.cam-foot .pg-row button.on {
  background: #2a4a78;
  border-color: #2a4a78;
}

/* 서버 상태 표 */
.srv-tbl {
  font-size: 14.5px !important;
}
.srv-tbl th {
  padding: 8px !important;
  font-size: 13px !important;
  opacity: 0.85;
  font-weight: 700;
}
.srv-tbl td {
  padding: 8px !important;
}
.srv-tbl tbody tr:nth-child(even) {
  background: rgba(255, 255, 255, 0.015);
}
.srv-tbl .mono {
  font-size: 13.5px;
}

/* 상태 태그 — 채도 다운, 사각 */
.ops-shell .stat,
.ops-shell :deep(.stat) {
  padding: 2px 7px !important;
  border-radius: 2px !important;
  font-size: 10.5px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em;
}
.ops-shell .stat.ok,
.ops-shell :deep(.stat.ok) {
  background: rgba(111, 165, 129, 0.18);
  color: #6fa581;
}
.ops-shell .stat.wn,
.ops-shell :deep(.stat.wn) {
  background: rgba(212, 166, 82, 0.18);
  color: #d4a652;
}
.ops-shell .stat.no,
.ops-shell :deep(.stat.no) {
  background: rgba(217, 112, 112, 0.18);
  color: #d97070;
}

/* 토폴로지 카드 */
.topo-legend {
  font-size: 11.5px !important;
  gap: 10px !important;
}
.dt {
  width: 8px !important;
  height: 8px !important;
  border-radius: 0 !important;
}

/* 지연 상세 */
.pnl-tbl.small th {
  padding: 5px 7px !important;
  font-size: 11px !important;
}
.pnl-tbl.small td {
  padding: 6px 7px !important;
  font-size: 12px;
}
.lat-btn {
  background: #2a4a78 !important;
  border-radius: 2px !important;
  padding: 7px !important;
  font-size: 12px !important;
  font-weight: 500 !important;
}

/* 장애 큐 */
.fq-row {
  padding: 7px 0 !important;
  font-size: 12.5px !important;
}
.fq-row i {
  font-size: 13px !important;
  color: #d97070;
}
.fq-t {
  font-size: 13px !important;
  font-weight: 600 !important;
}
.fq-id {
  font-size: 11px !important;
  font-family: "JetBrains Mono", monospace;
}
.fq-time {
  font-size: 11px !important;
  font-family: "JetBrains Mono", monospace;
}
.fq-tag {
  background: rgba(217, 112, 112, 0.18) !important;
  color: #d97070 !important;
  border-radius: 2px !important;
  font-size: 10px !important;
  padding: 1px 6px !important;
}

/* 점검 일정 */
.cs-row {
  padding: 6px 0 !important;
}
.cs-t {
  font-size: 12.5px !important;
  font-weight: 600 !important;
}
.cs-d {
  font-size: 11.5px !important;
  opacity: 0.7;
}
.cs-tag {
  background: rgba(120, 160, 210, 0.18) !important;
  color: #7ea4d8 !important;
  border-radius: 2px !important;
  font-size: 10px !important;
  padding: 1px 6px !important;
}

/* 최근 이벤트 */
.re-row {
  padding: 6px 0 !important;
  font-size: 12px !important;
  gap: 7px !important;
}
.re-dot {
  width: 7px !important;
  height: 7px !important;
  border-radius: 0 !important;
}
.re-dot.rd {
  background: #d97070 !important;
}
.re-dot.yl {
  background: #d4a652 !important;
}
.re-dot.gr {
  background: #6fa581 !important;
}
.re-time {
  font-size: 11px !important;
  font-family: "JetBrains Mono", monospace;
}
.re-sev {
  font-size: 10px !important;
  padding: 1px 5px !important;
  border-radius: 2px !important;
}
.re-sev.rd {
  background: rgba(217, 112, 112, 0.18);
  color: #d97070;
}
.re-sev.yl {
  background: rgba(212, 166, 82, 0.18);
  color: #d4a652;
}
.re-sev.gr {
  background: rgba(111, 165, 129, 0.18);
  color: #6fa581;
}
.re-msg {
  font-size: 11.5px;
}

/* ch-link */
.ch-link {
  font-size: 11px !important;
  color: #7ea4d8 !important;
}
.ch h3 {
  letter-spacing: -0.01em;
}
.seg-sub {
  font-size: 11px !important;
  opacity: 0.55;
}

/* ============================================================
   ★ KPI 카드 (5개 + 자동 새로고침 토글)
   ============================================================ */
.kpi-row {
  display: grid;
  grid-template-columns: repeat(5, 1fr) 170px;
  gap: 10px;
}

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
  font-family: "JetBrains Mono", monospace;
  font-weight: 700;
  color: #0c1f40;
  margin-left: 2px;
}

/* ★ 카드 헤더 분산 KPI — 칩 형태 X, 텍스트만 (AI 티 제거) */
.ops-shell :deep(.ch-kpi) {
  font-family: "JetBrains Mono", monospace;
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
  font-size: 11px;
  font-family: "JetBrains Mono", monospace;
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
  font-family: "JetBrains Mono", monospace;
}
.tl-row {
  display: grid;
  grid-template-columns: 76px 20px 56px 120px 1fr 80px 14px;
  gap: 8px;
  align-items: center;
  padding: 6px 4px;
  border-bottom: 1px solid #c9d4e3;
  font-size: 13.5px;
  color: #0c1f40;
  cursor: pointer;
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
.tl-k {
  text-align: center;
  font-weight: 700;
  font-size: 12px;
  color: rgba(12, 31, 64, 0.7);
}
.tl-row.event .tl-k {
  color: #dc2626;
}
.tl-row.recovered .tl-k {
  color: #059669;
}
.tl-row.info .tl-k {
  color: #2563eb;
}
.tl-sev {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-align: center;
  padding: 1px 0;
}
.tl-sev.crit {
  color: #b91c1c;
}
.tl-sev.high {
  color: #b45309;
}
.tl-sev.med {
  color: #a16207;
}
.tl-id {
  color: #0c1f40;
  font-weight: 700;
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
  font-size: 12.5px;
  color: #0c1f40;
  text-align: right;
}
.tl-arrow {
  color: rgba(12, 31, 64, 0.55);
  font-size: 12px;
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
  margin-top: 6px;
  border-top: 1px solid #c9d4e3;
  font-size: 12.5px;
  color: #0c1f40;
  font-family: "JetBrains Mono", monospace;
}
.kpi {
  background: #f7f9fc;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 12px 14px;
  display: flex;
  gap: 10px;
  align-items: center;
  box-shadow: 0 1px 2px rgba(12, 31, 64, 0.06);
}
.kpi.rd {
  background: #fbe8e8;
  border-color: #f4a5a5;
}
.k-ic {
  width: 36px;
  height: 36px;
  border-radius: 3px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.k-ic .bi {
  font-size: 16px;
}
.kpi.gr .k-ic {
  background: rgba(5, 150, 105, 0.12);
  color: #059669;
}
.kpi.rd .k-ic {
  background: rgba(220, 38, 38, 0.12);
  color: #dc2626;
}
.kpi.bl .k-ic {
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
}
.kpi.pl .k-ic {
  background: rgba(124, 58, 237, 0.1);
  color: #7c3aed;
}
.kpi.pk .k-ic {
  background: rgba(220, 104, 3, 0.12);
  color: #dc6803;
}
.k-body {
  flex: 1;
  min-width: 0;
}
.k-lab {
  font-size: 12.5px;
  color: #0c1f40;
}
.k-val {
  font-size: 22px;
  font-weight: 700;
  font-family: "JetBrains Mono", monospace;
  color: #0c1f40;
  letter-spacing: -0.01em;
  margin-top: 3px;
}
.kpi.rd .k-val {
  color: #dc2626;
}
.k-u {
  font-size: 13px;
  font-weight: 500;
  color: rgba(12, 31, 64, 0.92);
  margin-left: 2px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
}
.k-inline {
  font-size: 13px;
  font-weight: 600;
  color: #059669;
  margin-left: 8px;
  font-family: "JetBrains Mono", monospace;
  vertical-align: middle;
}
.kpi.rd .k-inline {
  color: #dc2626;
}
.kpi.bl .k-inline {
  color: #2563eb;
}
.kpi.pl .k-inline {
  color: #7c3aed;
}
.kpi.pk .k-inline {
  color: #dc6803;
}
.k-link {
  font-size: 12px;
  color: #2563eb;
  cursor: pointer;
  align-self: flex-start;
}

.kpi-meta {
  background: #f7f9fc;
  border: 1px solid #c9d4e3;
  border-radius: 4px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 1px 2px rgba(12, 31, 64, 0.06);
}
.km-t {
  font-size: 11.5px;
  color: #0c1f40;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}
.km-t > i {
  font-size: 12.5px;
  padding-top: 1px;
}
.km-t strong {
  font-family: "JetBrains Mono", monospace;
  font-weight: 600;
  color: #0c1f40;
  font-size: 13px;
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
  font-size: 12.5px;
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
  font-size: 10.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  font-family: "JetBrains Mono", monospace;
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
  font-size: 10px;
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
  font-size: 11px;
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
  font-size: 12.5px;
  font-weight: 700;
  color: #fca5a5;
}
.fl-tag {
  background: rgba(217, 112, 112, 0.22);
  color: #d97070;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 2px;
  margin-left: 6px;
}
.fl-rows {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 11.5px;
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
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
}
.fail-card h4 {
  font-size: 11.5px;
  font-weight: 600;
  margin: 8px 0 5px;
  opacity: 0.85;
}
.hst {
  display: flex;
  flex-direction: column;
  gap: 3px;
  font-size: 11px;
  padding-left: 2px;
  margin-bottom: 3px;
}
.hst-t {
  color: #7ea4d8;
  font-family: "JetBrains Mono", monospace;
  margin-right: 5px;
}
.rec-p {
  font-size: 11px;
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
  font-size: 11.5px;
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
  font-size: 11px;
}
.resp-row span,
.memo-row span {
  opacity: 0.6;
  width: 50px;
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
  font-size: 11px;
  font-family: inherit;
}
.ab-sm {
  padding: 3px 8px;
  background: rgba(120, 160, 210, 0.12);
  border: 1px solid rgba(120, 160, 210, 0.3);
  color: #7ea4d8;
  border-radius: 2px;
  font-size: 10.5px;
  cursor: pointer;
}

/* ============================================================
   ★ 메인 그리드 — 좌측 2x2 + 우측 풀세로 장애상세
   ============================================================ */
.main-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.95fr;
  grid-template-rows: 1fr auto; /* 상단 늘어남, 하단은 콘텐츠만큼 */
  gap: 8px;
  min-height: calc(100vh - 170px); /* 장애상세 풀세로 화면 꽉 */
}
.main-grid > .card,
.main-grid > .bot-row > .card {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.cam-card {
  grid-column: 1;
  grid-row: 1;
}
.srv-card {
  grid-column: 2;
  grid-row: 1;
}
.fail-card {
  grid-column: 3;
  grid-row: 1 / span 2;
}
.bot-row {
  grid-column: 1 / 3; /* 좌측 2 컬럼 영역을 차지 */
  grid-row: 2;
  display: grid;
  grid-template-columns: 3fr 7fr; /* 네트워크 3 : 토폴로지 7 */
  gap: 8px;
  min-height: 0;
}

.net-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}
.nb-wide {
  grid-column: 1 / -1;
} /* 정상 구간 전체 폭 (이미지 매칭) */
.net-card {
  display: flex;
  flex-direction: column;
}
.net-card .net-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}
.nb {
  background: #06101e;
  border: 1px solid #1f3055;
  border-radius: 2px;
  padding: 7px 9px;
}
.nb-l {
  font-size: 10.5px;
  opacity: 0.65;
  margin-bottom: 3px;
}
.nb-v {
  font-size: 15px;
  font-weight: 700;
  font-family: "JetBrains Mono", monospace;
  color: #c4d8f5;
  margin-bottom: 3px;
}
.ns {
  width: 100%;
  height: 18px;
}
.nb-v .u {
  font-size: 10px;
  opacity: 0.55;
  font-weight: 500;
  margin-left: 1px;
  font-family: "Pretendard Variable", Pretendard, sans-serif;
}
.ns {
  width: 100%;
  height: 22px;
}
.bar-line {
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 1px;
  overflow: hidden;
  margin-top: 6px;
}
.bar-line span {
  display: block;
  height: 100%;
}
.topo-svg {
  width: 100%;
  height: 280px;
  display: block;
  overflow: visible;
}
.topo-card {
  display: flex;
  flex-direction: column;
}

.pnl {
  padding: 18px;
}
.pnl h3 {
  font-size: 14px;
  font-weight: 700;
  margin: 0 0 14px;
}
.pnl-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
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
  font-size: 11.5px;
}
.pnl-tbl .mono {
  font-family: "JetBrains Mono", monospace;
}
.stat {
  padding: 2px 8px;
  border-radius: 100px;
  font-size: 10.5px;
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
.rep-rows {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.rep-r {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #06101e;
  border: 1px solid #1f3055;
  border-radius: 6px;
}
.rep-r > i {
  font-size: 20px;
  color: #60a5fa;
}
.rep-r > div {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.rep-r strong {
  font-size: 13px;
}
.rep-r span {
  font-size: 11px;
  opacity: 0.6;
}
.bt-dl {
  width: 32px;
  height: 32px;
  background: rgba(96, 165, 250, 0.12);
  border: 0;
  color: #60a5fa;
  border-radius: 5px;
  cursor: pointer;
}
.set-row {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 12px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #1a2a45;
  font-size: 13px;
}
.set-row input[type="number"],
.set-row select {
  background: #06101e;
  border: 1px solid #1f3055;
  color: #e4eeff;
  padding: 6px 10px;
  border-radius: 5px;
  font-size: 12.5px;
  max-width: 200px;
}
.set-row input[type="checkbox"] {
  accent-color: #60a5fa;
}
.btn-save {
  margin-top: 14px;
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 9px 16px;
  border-radius: 6px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.set-msg {
  margin-top: 10px;
  font-size: 12px;
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
  font-size: 15px !important;
  font-weight: 700 !important;
}
.ops-shell .fail-card .fl-tag {
  font-size: 11.5px !important;
  padding: 2px 8px !important;
}
.ops-shell .fail-card .b-rd {
  font-size: 11.5px !important;
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
  font-size: 12.5px !important;
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
  font-size: 12px !important;
  padding: 4px 10px !important;
}
.ops-shell .fail-card .memo-row input {
  font-size: 13px !important;
  padding: 6px 10px !important;
}

/* ★ 서버 상태 — 폰트 일괄 ↑ */
.ops-shell .srv-card .sn-t {
  font-size: 14px !important;
  font-weight: 700;
}
.ops-shell .srv-card .sn-tag {
  font-size: 12px !important;
}
.ops-shell .srv-card .sn-ip {
  font-size: 12.5px !important;
}
.ops-shell .srv-card .srv-name > i {
  font-size: 20px !important;
}
.srv-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 3px rgba(12, 31, 64, 0.18));
}
.ops-shell .srv-card .srv-lab {
  font-size: 12px !important;
  font-weight: 500;
}
.ops-shell .srv-card .srv-val {
  font-size: 14px !important;
  font-weight: 700;
}
.ops-shell .srv-card .stat {
  font-size: 11.5px !important;
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
  font-size: 12.5px !important;
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
  font-size: 15.5px !important;
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
  font-size: 12.5px !important;
}
.ops-shell .bt-dl {
  background: rgba(37, 99, 235, 0.12) !important;
  color: #2563eb !important;
}
/* 설정 행 */
.ops-shell .set-row {
  color: #0c1f40 !important;
  border-bottom-color: #e3e9f2 !important;
  font-size: 14px !important;
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
  font-size: 16px;
  font-weight: 700;
  color: #0c1f40;
}
.cm-title i {
  color: #2563eb;
  font-size: 18px;
}
.cm-title .stat {
  font-size: 11.5px !important;
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
  font-family: "JetBrains Mono", monospace;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}
.cm-stream-time {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
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
  font-size: 11px;
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
  font-size: 11px;
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
  font-family: "JetBrains Mono", monospace;
  font-size: 13px;
}
.cm-ok {
  color: #059669 !important;
}
.cm-no {
  color: #dc2626 !important;
}
.cm-wn {
  color: #b45309 !important;
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
.alarm-modal { width: min(560px, 95vw); }
.am-body { padding: 18px; display: flex; flex-direction: column; gap: 10px; }
.am-msg {
  font-size: 15px; font-weight: 600; color: #0c1f40;
  padding: 12px 14px; background: #f1f5fb;
  border-left: 3px solid #2563eb; border-radius: 2px; line-height: 1.5;
}
.alarm-modal .cm-actions { grid-template-columns: 1fr 1fr; margin-top: 6px; }

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
  font-size: 11.5px;
  color: rgba(12, 31, 64, 0.9);
  margin-bottom: 4px;
}
.ops-shell .ps-v {
  font-size: 22px;
  font-weight: 700;
  color: #0c1f40;
  font-family: "JetBrains Mono", monospace;
  letter-spacing: -0.01em;
}
.ops-shell .ps-v span {
  font-size: 12px;
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
  font-size: 12.5px;
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
  font-size: 12px;
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
  font-size: 12px;
  color: rgba(12, 31, 64, 0.78);
  font-family: "JetBrains Mono", monospace;
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
  font-size: 12px;
  color: rgba(12, 31, 64, 0.85);
}
.ops-shell .srv-meta i {
  color: #2563eb;
  margin-right: 4px;
}
</style>
