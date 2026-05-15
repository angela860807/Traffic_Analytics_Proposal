<template>
  <div class="v2-root">
    <!-- ═══════════ HEADER ═══════════ -->
    <header class="v2-header">
      <div class="v2-logo" @click="router.push('/')">
        <span class="v2-logo-dot"></span>
        <span class="v2-logo-text">TrafficAS <em>Analytics Hub</em></span>
      </div>
      <nav class="v2-tab-nav">
        <button
          v-for="tab in TABS"
          :key="tab.id"
          class="v2-tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>
      <div class="v2-header-right">
        <div class="v2-notif-wrap">
          <button class="v2-notif" @click="showNotif = !showNotif">
            <i class="bi bi-bell"></i>
            <span class="v2-notif-n">{{ notifications.length }}</span>
          </button>
          <div v-if="showNotif" class="v2-notif-panel" @click.stop>
            <div class="v2-notif-ph">
              <span><i class="bi bi-bell-fill me-1"></i>알림</span>
              <div class="v2-notif-tools">
                <span class="v2-notif-badge">{{ notifications.length }}건</span>
                <button
                  class="v2-notif-edit"
                  :class="{ active: notifEdit }"
                  @click="notifEdit = !notifEdit"
                >
                  <i class="bi" :class="notifEdit ? 'bi-check2' : 'bi-pencil'"></i>
                  {{ notifEdit ? "완료" : "편집" }}
                </button>
              </div>
            </div>
            <div v-if="notifications.length === 0" class="v2-notif-empty">
              알림이 없습니다.
            </div>
            <div
              v-for="n in notifications"
              :key="n.id"
              class="v2-ni"
              :class="{ 'v2-ni-edit': notifEdit }"
            >
              <span class="v2-ni-dot" :style="{ background: n.color }"></span>
              <div class="v2-ni-body">
                <div class="v2-ni-msg">{{ n.msg }}</div>
                <div class="v2-ni-t mono">{{ n.time }}</div>
              </div>
              <button
                v-if="notifEdit"
                class="v2-ni-del"
                @click="removeNotif(n.id)"
                title="삭제"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>
            <div v-if="notifEdit && notifications.length > 0" class="v2-notif-foot">
              <button class="v2-notif-clear" @click="clearAllNotif">
                <i class="bi bi-trash"></i> 전체 삭제
              </button>
            </div>
          </div>
        </div>
        <div class="v2-user-wrap">
          <div class="v2-user" @click="showUserMenu = !showUserMenu">
            <div class="v2-avatar">{{ (displayName[0] || "A").toUpperCase() }}</div>
            <span>{{ displayName }}</span>
            <i class="bi bi-caret-down-fill v2-caret" :class="{ open: showUserMenu }"></i>
          </div>
          <div v-if="showUserMenu" class="v2-user-menu" @click.stop>
            <div class="v2-um-header">
              <div class="v2-avatar v2-avatar-lg">
                {{ (displayName[0] || "A").toUpperCase() }}
              </div>
              <div class="v2-um-info">
                <div class="v2-um-name">{{ displayName }}</div>
                <div class="v2-um-role">시스템 관리자</div>
              </div>
            </div>
            <div class="v2-um-divider"></div>
            <button class="v2-um-item" @click="onUserMenu('profile')">
              <i class="bi bi-person-circle"></i><span>내 정보</span>
            </button>
            <button class="v2-um-item" @click="onUserMenu('password')">
              <i class="bi bi-key-fill"></i><span>비밀번호 변경</span>
            </button>
            <button class="v2-um-item" @click="onUserMenu('notify')">
              <i class="bi bi-bell-fill"></i><span>알림 설정</span>
            </button>
            <button class="v2-um-item" @click="onUserMenu('settings')">
              <i class="bi bi-gear-fill"></i><span>환경설정</span>
            </button>
            <button class="v2-um-item" @click="onUserMenu('help')">
              <i class="bi bi-question-circle-fill"></i><span>도움말</span>
            </button>
            <div class="v2-um-divider"></div>
            <button class="v2-um-item v2-um-logout" @click="onUserMenu('logout')">
              <i class="bi bi-box-arrow-right"></i><span>로그아웃</span>
            </button>
          </div>
        </div>
        <button class="v2-fs" @click="toggleFullscreen" title="전체화면">
          <i class="bi bi-arrows-fullscreen"></i>
        </button>
      </div>
    </header>

    <!-- ═══════════ BODY ═══════════ -->
    <div class="v2-body">
      <!-- ═══ LEFT SIDEBAR ═══ -->
      <aside class="v2-side">
        <div class="v2-panel v2-aq-panel">
          <div class="v2-panel-h">
            <span><i class="bi bi-cloud-sun-fill"></i>날씨 / 대기</span>
            <div class="v2-aq-tools">
              <span class="v2-aq-loc">{{ currentDistrictName }}</span>
              <button class="v2-aq-fs" @click="showWeatherDetail = true" title="자세히 보기">
                <i class="bi bi-arrows-fullscreen"></i>
              </button>
            </div>
          </div>
          <div class="v2-aq-body">
            <Transition name="v2-aq-slide" mode="out-in">
              <div :key="currentDistrictName" class="v2-aq-slide-content">
                <!-- 메인: 날씨 -->
                <div class="v2-aq-weather">
                  <i class="v2-aq-w-icon" :class="weather.icon" :style="{ color: weather.color }"></i>
                  <div class="v2-aq-w-mid">
                    <div class="v2-aq-w-cond">{{ weather.condition }}</div>
                    <div class="v2-aq-w-aqi" :style="{ color: aqGrade.color }">
                      <span class="v2-aq-w-dot" :style="{ background: aqGrade.color }"></span>
                      {{ aqGrade.label }}
                    </div>
                  </div>
                  <div class="v2-aq-w-temp">
                    <div class="v2-aq-w-tnum">{{ weather.temp }}<small>°C</small></div>
                    <div class="v2-aq-w-tsub">습도 {{ weather.humidity }}%</div>
                  </div>
                </div>
                <!-- 대기질 지표 -->
                <div class="v2-aq-list">
                  <div class="v2-aq-item">
                    <span class="v2-aq-k">미세먼지</span>
                    <div class="v2-aq-bar"><div class="v2-aq-fill" :style="{ width: pm10Pct + '%', background: pmGrade(weather.pm10, 'pm10').color }"></div></div>
                    <span class="v2-aq-v mono" :style="{ color: pmGrade(weather.pm10, 'pm10').color }">{{ weather.pm10 }}</span>
                  </div>
                  <div class="v2-aq-item">
                    <span class="v2-aq-k">초미세먼지</span>
                    <div class="v2-aq-bar"><div class="v2-aq-fill" :style="{ width: pm25Pct + '%', background: pmGrade(weather.pm25, 'pm25').color }"></div></div>
                    <span class="v2-aq-v mono" :style="{ color: pmGrade(weather.pm25, 'pm25').color }">{{ weather.pm25 }}</span>
                  </div>
                  <div class="v2-aq-item">
                    <span class="v2-aq-k">오존</span>
                    <div class="v2-aq-bar"><div class="v2-aq-fill" :style="{ width: o3Pct + '%', background: '#a78bfa' }"></div></div>
                    <span class="v2-aq-v mono">{{ weather.o3 }}</span>
                  </div>
                </div>
              </div>
            </Transition>
            <!-- 진행 표시 (클릭 가능) -->
            <div class="v2-aq-progress">
              <button
                v-for="(d, i) in DISTRICT_LIST" :key="d"
                type="button"
                class="v2-aq-pgdot"
                :class="{ active: i === currentDistrictIdx }"
                :title="d"
                @click="currentDistrictIdx = i"
              ></button>
            </div>
          </div>
        </div>

        <div class="v2-panel v2-cam-panel">
          <div class="v2-panel-h">
            <span><i class="bi bi-camera-video-fill"></i>카메라 그룹</span>
            <i class="bi bi-chevron-down"></i>
          </div>
          <div class="v2-search">
            <i class="bi bi-search"></i>
            <input v-model="camQuery" placeholder="카메라 검색" />
          </div>
          <div class="v2-tree">
            <div class="v2-tree-root">
              <i class="bi bi-camera-video-fill v2-tree-ico"></i>
              <span>전체 카메라</span>
              <span class="v2-cnt">{{ totalCamCount }}</span>
            </div>
            <div v-for="g in filteredGroups" :key="g.region" class="v2-tree-group">
              <div class="v2-tree-gh" @click="g.expanded = !g.expanded">
                <i
                  class="bi"
                  :class="g.expanded ? 'bi-chevron-down' : 'bi-chevron-right'"
                ></i>
                <i class="bi bi-folder-fill v2-tree-folder"></i>
                <span>{{ g.region }}</span>
                <span class="v2-cnt">{{ g.cams.length }}</span>
              </div>
              <div v-show="g.expanded" class="v2-tree-children">
                <div
                  v-for="c in g.cams" :key="c.name"
                  class="v2-tree-leaf"
                  :class="{ active: c.name === selectedCamName }"
                  @click="selectCamera(c)"
                  title="클릭: 지도 이동 + 영상 강조"
                >
                  <span class="v2-tree-dot" :class="c.status"></span>
                  <span>{{ c.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- ═══ MAIN ═══ -->
      <main class="v2-main">
        <!-- ════════ 대시보드 탭 ════════ -->
        <div v-show="activeTab === 'overview'" class="v2-tab-page">
          <!-- ROW 1: KPIs -->
          <div class="v2-kpi-row">
            <div
              v-for="k in kpiCards"
              :key="k.label"
              class="v2-kpi"
              :class="`v2-kpi-${k.theme}`"
            >
              <div class="v2-kpi-icon">
                <i :class="k.icon"></i>
              </div>
              <div class="v2-kpi-body">
                <div class="v2-kpi-label">{{ k.label }}</div>
                <div class="v2-kpi-value">
                  <span class="v2-kpi-num">{{ k.value }}</span>
                  <span class="v2-kpi-unit">{{ k.unit }}</span>
                </div>
                <div class="v2-kpi-diff" :class="{ down: !k.up }">
                  전일 대비
                  <i class="bi" :class="k.up ? 'bi-caret-up-fill' : 'bi-caret-down-fill'"></i>
                  {{ k.diff }}
                </div>
              </div>
            </div>
          </div>

          <!-- ROW 2 : 실시간 카메라 + (시간대별 혼잡도 + 차량 통행 분석) -->
          <div class="v2-row v2-row-2">
            <section class="v2-card v2-cam-grid-card">
              <div class="v2-card-h">
                <span><i class="bi bi-camera-video-fill"></i>실시간 카메라 모니터링</span>
              </div>
              <div class="v2-cam-grid">
                <div
                  v-for="f in cameraFeeds"
                  :key="f.name"
                  class="v2-cam-cell"
                  :class="{ active: f.name === selectedCamName }"
                  :data-cam="f.name"
                  @click="openModal(f)"
                >
                  <div class="v2-cam-top">
                    <span class="v2-cam-live-dot"></span>
                    <span class="v2-cam-name">{{ f.name }}</span>
                    <span class="v2-cam-live-badge">LIVE</span>
                  </div>
                  <video
                    :src="f.src"
                    autoplay
                    muted
                    loop
                    playsinline
                    preload="metadata"
                    disablepictureinpicture
                    disableremoteplayback
                    class="v2-cam-video"
                    @loadedmetadata="onCamLoaded"
                  ></video>
                  <button class="v2-cam-zoom">
                    <i class="bi bi-arrows-fullscreen"></i>
                  </button>
                </div>
              </div>
            </section>

            <div class="v2-col-right-r2">
              <section class="v2-card v2-cong-card">
                <div class="v2-card-h">
                  <span><i class="bi bi-graph-up"></i>시간대별 혼잡도</span>
                  <div class="v2-legend">
                    <span class="v2-lg"><i class="dot" style="background: #4caf7d"></i>원활</span>
                    <span class="v2-lg"><i class="dot" style="background: #d4845a"></i>혼잡</span>
                    <span class="v2-lg"><i class="dot" style="background: #e05260"></i>정체</span>
                  </div>
                </div>
                <div ref="congEl" class="v2-chart"></div>
              </section>

              <section class="v2-card v2-flow-card">
                <div class="v2-card-h">
                  <span><i class="bi bi-arrow-left-right"></i>차량 통행 분석 (진입 / 이탈)</span>
                  <span class="v2-flow-net">순진입 <b>{{ (inCount - outCount).toLocaleString() }}</b>대</span>
                </div>
                <div class="v2-flow-body">
                  <div class="v2-flow-cell v2-flow-in">
                    <div class="v2-flow-label">
                      <i class="bi bi-box-arrow-in-down-right"></i> 진입 (IN)
                    </div>
                    <div class="v2-flow-value">
                      <span class="v2-flow-num">{{ inCount.toLocaleString() }}</span>
                      <span class="v2-flow-unit">대</span>
                    </div>
                  </div>
                  <div class="v2-flow-cell v2-flow-out">
                    <div class="v2-flow-label">
                      <i class="bi bi-box-arrow-up-right"></i> 이탈 (OUT)
                    </div>
                    <div class="v2-flow-value">
                      <span class="v2-flow-num">{{ outCount.toLocaleString() }}</span>
                      <span class="v2-flow-unit">대</span>
                    </div>
                  </div>
                  <div class="v2-flow-chart-wrap">
                    <div class="v2-flow-spark-label">최근 12시간 추이</div>
                    <div ref="sparkEl" class="v2-spark"></div>
                  </div>
                </div>
                <div class="v2-dup-bar">
                  <i class="bi bi-shield-check"></i>
                  <span>중복 제거 처리</span>
                  <span class="v2-dup-val">총 감지 {{ (totalVehicles + dupRemoved).toLocaleString() }}건 중 <b>{{ dupRemoved }}</b>건 제거 → 순 <b>{{ totalVehicles.toLocaleString() }}</b>건</span>
                </div>
              </section>
            </div>
          </div>

          <!-- ROW 3: OCR / HeatMap / Status -->
          <div class="v2-row3-grid">
              <section class="v2-card v2-ocr-card">
                <div class="v2-card-h">
                  <span><i class="bi bi-upc-scan"></i>OCR 인식 결과 (실시간)</span>
                  <div style="display:flex;align-items:center;gap:6px">
                    <span v-if="latestPlate.id"
                          class="v2-plate-status"
                          :class="`v2-plate-status-${plateStatus(latestPlate.status).cls}`">
                      <i :class="plateStatus(latestPlate.status).icon"></i>
                      {{ plateStatus(latestPlate.status).label }}
                    </span>
                    <button v-if="selectedPlateId != null" class="v2-ocr-reset" @click="selectedPlateId = null">
                      <i class="bi bi-arrow-counterclockwise"></i> 최신
                    </button>
                  </div>
                </div>
                <div class="v2-ocr-body">
                  <div class="v2-ocr-photo">
                    <img
                      v-if="latestPlate.id && plateDisplayImage(latestPlate)"
                      :src="plateDisplayImage(latestPlate)"
                      class="v2-ocr-photo-img"
                      :alt="latestPlate.num"
                      @error="markPlateImageFailed(plateDisplayImage(latestPlate))"
                    />
                    <div v-else-if="latestPlate.id" class="v2-ocr-photo-empty">
                      <i class="bi bi-image"></i>
                      <span>이미지 없음</span>
                    </div>
                    <div class="v2-plate-vis">
                      <div class="v2-plate-num mono">{{
                        latestPlate.status === 'OCR_FAILED' ? '미인식' : (latestPlate.num || '128가 4567')
                      }}</div>
                    </div>
                  </div>
                  <div class="v2-ocr-info">
                    <div v-for="d in ocrDetails" :key="d.label" class="v2-ocr-row">
                      <span class="v2-ocr-k">{{ d.label }}</span>
                      <span
                        class="v2-ocr-v"
                        :class="{
                          'v2-ocr-conf': d.label === '신뢰도',
                          [`v2-ocr-dir-${d.dirClass}`]: d.dirClass,
                        }"
                      >
                        <i v-if="d.dirClass === 'in'" class="bi bi-arrow-down-left-circle-fill"></i>
                        <i v-if="d.dirClass === 'out'" class="bi bi-arrow-up-right-circle-fill"></i>
                        {{ d.value }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="v2-ocr-thumbs">
                  <div
                    v-for="p in recentPlates" :key="p.id"
                    class="v2-ocr-thumb"
                    :class="{ active: p.id === latestPlate.id }"
                    @click="selectPlate(p)"
                  >
                    <img
                      v-if="plateDisplayImage(p)"
                      :src="plateDisplayImage(p)"
                      class="v2-ocr-thumb-img"
                      :alt="p.num"
                      @error="markPlateImageFailed(plateDisplayImage(p))"
                    />
                    <div v-else class="v2-ocr-thumb-empty"><i class="bi bi-image"></i></div>
                    <div class="v2-ocr-thumb-time mono">{{ p.time }}</div>
                    <div class="v2-ocr-thumb-plate mono">{{ p.num }}</div>
                  </div>
                </div>
              </section>

              <section
                class="v2-card v2-heat-card"
                :class="{ 'v2-heat-expanded': heatExpanded }"
              >
                <div class="v2-card-h">
                  <span><i class="bi bi-fire"></i>교통량 HeatMap</span>
                <div class="v2-heat-tools">
                  <label class="v2-toggle">
                    <input type="checkbox" v-model="heatLive" />
                    <span>실시간</span>
                  </label>
                  <div class="v2-hotspot-wrap" @click.stop>
                    <button
                      class="v2-heat-fs"
                      :class="{ active: showHotspot }"
                      @click="showHotspot = !showHotspot"
                      title="혼잡 지점으로 이동"
                    >
                      <i class="bi bi-geo-alt-fill"></i>
                      <span>혼잡 지점</span>
                      <i class="bi bi-caret-down-fill" style="font-size: 8px"></i>
                    </button>
                    <div v-if="showHotspot" class="v2-hotspot-menu">
                      <div class="v2-hotspot-header">
                        <i class="bi bi-fire"></i> 혼잡 지점 (강도순)
                      </div>
                      <button
                        v-for="spot in hotspots"
                        :key="spot.id"
                        class="v2-hotspot-item"
                        @click="flyToHotspot(spot)"
                      >
                        <span
                          class="v2-hotspot-dot"
                          :style="{ background: heatColor(spot.intensity) }"
                        ></span>
                        <span class="v2-hotspot-name">{{ spot.name }}</span>
                        <span
                          class="v2-hotspot-lv"
                          :class="hotspotLevel(spot.intensity) === '정체' ? 'critical'
                                : hotspotLevel(spot.intensity) === '혼잡' ? 'warning' : 'ok'"
                        >{{ hotspotLevel(spot.intensity) }}</span>
                        <span class="v2-hotspot-int mono">{{ Math.round(spot.intensity * 100) }}%</span>
                      </button>
                    </div>
                  </div>
                  <button
                    class="v2-heat-fs"
                    @click="openHeatFullscreen"
                    title="전체 보기"
                  >
                    <i class="bi bi-arrows-fullscreen"></i>
                    <span>전체 보기</span>
                  </button>
                </div>
              </div>
              <div class="v2-heat-wrap">
                <div ref="heatmapEl" class="v2-heat-map"></div>
                <div v-if="osmFailed" class="v2-heat-notice">
                  <i class="bi bi-exclamation-triangle-fill"></i>
                  OSM 도로 데이터 로드 실패 — 지도 타일만 표시 중
                  <button @click="retryOSMRoads">
                    <i class="bi bi-arrow-clockwise"></i> 다시 시도
                  </button>
                </div>
                <div v-if="!heatReady" class="v2-heat-loading">
                  <i class="bi bi-geo-alt-fill"></i>
                  <span>지도 로딩 중…</span>
                </div>
                <!-- 하단 가로 범례 바 -->
                <div class="v2-road-legend">
                  <span class="v2-road-legend-val">0</span>
                  <div class="v2-road-legend-bar"></div>
                  <span class="v2-road-legend-val right">133,151<small>대/일</small></span>
                </div>
              </div>
            </section>

              <section class="v2-card v2-status-card">
                <div class="v2-card-h">
                  <span><i class="bi bi-camera-video"></i>카메라 상태 모니터링</span>
                  <span class="v2-status-total">전체 {{ totalCamCount }}대</span>
                </div>
              <div class="v2-status-body">
                <div class="v2-donut-wrap">
                  <div ref="donutEl" class="v2-donut"></div>
                  <div class="v2-donut-center">
                    <div class="v2-donut-num">{{ totalCamCount }}</div>
                    <div class="v2-donut-lbl">전체</div>
                  </div>
                </div>
                <div class="v2-status-legend">
                  <div class="v2-sl-item">
                    <span class="v2-sl-dot" style="background: #4caf7d"></span>
                    <span class="v2-sl-name">정상</span>
                    <span class="v2-sl-val"
                      >{{ stats.online }} ({{ pct(stats.online) }}%)</span
                    >
                  </div>
                  <div class="v2-sl-item">
                    <span class="v2-sl-dot" style="background: #e05260"></span>
                    <span class="v2-sl-name">오프라인</span>
                    <span class="v2-sl-val"
                      >{{ stats.offline }} ({{ pct(stats.offline) }}%)</span
                    >
                  </div>
                  <div class="v2-sl-item">
                    <span class="v2-sl-dot" style="background: #d4845a"></span>
                    <span class="v2-sl-name">오류</span>
                    <span class="v2-sl-val"
                      >{{ stats.error }} ({{ pct(stats.error) }}%)</span
                    >
                  </div>
                </div>
              </div>
              <div class="v2-status-table">
                <div class="v2-st-head">
                  <span>카메라 이름</span>
                  <span>상태</span>
                  <span>마지막 연결</span>
                </div>
                <div v-for="c in statusList" :key="c.name" class="v2-st-row">
                  <span class="v2-st-name">{{ c.name }}</span>
                  <span class="v2-st-status" :class="c.status">{{
                    statusLabel(c.status)
                  }}</span>
                  <span class="v2-st-time mono">{{ c.lastSeen || "-" }}</span>
                </div>
              </div>
              </section>
          </div>

          <!-- ROW 4: OCR 로그 (풀폭) -->
          <section class="v2-card v2-log-card v2-log-row">
            <div class="v2-card-h">
              <span><i class="bi bi-list-ul"></i>OCR 인식 로그 (중복 제거 후)</span>
              <button class="v2-log-more" @click="activeTab = 'search'">전체 보기 ›</button>
            </div>
            <div class="v2-log-table">
              <div class="v2-lt-head">
                <span>번호</span>
                <span>인식 시간</span>
                <span>카메라</span>
                <span>차량 번호</span>
                <span>상태</span>
                <span>흐름 방향</span>
                <span>신뢰도</span>
              </div>
              <div
                v-for="(p, i) in logPlates" :key="p.id"
                class="v2-lt-row"
                :class="{ active: p.id === latestPlate.id }"
                @click="selectPlate(p)"
                title="클릭하면 위 OCR 카드에 표시"
              >
                <span>{{ i + 1 }}</span>
                <span class="mono">{{ todayStr }} {{ p.time }}</span>
                <span>{{ p.cam }}</span>
                <span class="mono">{{ p.status === 'OCR_FAILED' ? '미인식' : p.num }}</span>
                <span class="v2-plate-status" :class="`v2-plate-status-${plateStatus(p.status).cls}`">
                  <i :class="plateStatus(p.status).icon"></i>
                  {{ plateStatus(p.status).label }}
                </span>
                <span class="v2-lt-dir" :class="p.dir">
                  <i
                    :class="
                      p.dir === 'in'
                        ? 'bi bi-arrow-down-left-circle-fill'
                        : 'bi bi-arrow-up-right-circle-fill'
                    "
                  ></i>
                  {{ dirLabel(p.dir) }}
                </span>
                <span class="v2-lt-conf">{{ p.conf }}%</span>
              </div>
            </div>
          </section>
        </div>
        <!-- /대시보드 탭 -->

        <!-- ════════ 모니터링 탭 ════════ -->
        <MonitoringTab v-if="visitedTabs.has('monitoring')" :active="activeTab === 'monitoring'" />

        <!-- ════════ 이벤트 탭 ════════ -->
        <EventsTab v-if="visitedTabs.has('events')" v-show="activeTab === 'events'" />

        <!-- ════════ 검색 탭 ════════ -->
        <SearchTab v-if="visitedTabs.has('search')" v-show="activeTab === 'search'" />

        <!-- ════════ 통계 탭 ════════ -->
        <StatsTab v-if="visitedTabs.has('stats')" :active="activeTab === 'stats'" />

        <!-- ════════ 설정 탭 ════════ -->
        <SettingsTab v-if="visitedTabs.has('settings')" v-show="activeTab === 'settings'" />

        <footer class="v2-foot">© 2026 TrafficAS Analytics Hub</footer>
      </main>
    </div>

    <!-- ═══ 카메라 모달 ═══ -->
    <Teleport to="body">
      <div v-if="modalCam" class="v2-modal" @click.self="modalCam = null">
        <div class="v2-modal-box">
          <div class="v2-modal-h">
            <span><i class="bi bi-camera-video-fill"></i> {{ modalCam.name }}</span>
            <button @click="modalCam = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <video :src="modalCam.src" autoplay muted loop playsinline></video>
        </div>
      </div>
    </Teleport>

    <!-- ═══ 날씨/대기 상세 모달 ═══ -->
    <Teleport to="body">
      <div v-if="showWeatherDetail" class="v2-modal" @click.self="showWeatherDetail = false">
        <div class="v2-modal-box v2-wd-box">
          <div class="v2-modal-h">
            <span><i class="bi bi-cloud-sun-fill"></i> 강남 3구 날씨 / 대기 환경</span>
            <button @click="showWeatherDetail = false"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="v2-wd-body">
            <div class="v2-wd-grid">
              <div
                v-for="d in DISTRICT_LIST" :key="d"
                class="v2-wd-card"
                :class="{ active: d === currentDistrictName }"
                @click="selectDistrict(d); showWeatherDetail = false"
              >
                <div class="v2-wd-name">{{ d }}</div>
                <i class="v2-wd-icon" :class="districtsWeather[d].icon" :style="{ color: districtsWeather[d].color }"></i>
                <div class="v2-wd-cond">{{ districtsWeather[d].condition }}</div>
                <div class="v2-wd-temp">{{ districtsWeather[d].temp }}<small>°C</small></div>
                <div class="v2-wd-rows">
                  <div class="v2-wd-row"><span>습도</span><b>{{ districtsWeather[d].humidity }}%</b></div>
                  <div class="v2-wd-row"><span>풍속</span><b>{{ districtsWeather[d].wind }} m/s</b></div>
                  <div class="v2-wd-row"><span>가시거리</span><b>{{ districtsWeather[d].visibility }} km</b></div>
                  <div class="v2-wd-row"><span>자외선</span><b>{{ districtsWeather[d].uv }}</b></div>
                  <div class="v2-wd-divider"></div>
                  <div class="v2-wd-row">
                    <span>대기질 지수</span>
                    <b :style="{ color: aqLabel(districtsWeather[d].aqi).color }">{{ aqLabel(districtsWeather[d].aqi).label }} ({{ districtsWeather[d].aqi }})</b>
                  </div>
                  <div class="v2-wd-row">
                    <span>미세먼지</span>
                    <b :style="{ color: pmGrade(districtsWeather[d].pm10, 'pm10').color }">{{ districtsWeather[d].pm10 }} ({{ pmGrade(districtsWeather[d].pm10, 'pm10').label }})</b>
                  </div>
                  <div class="v2-wd-row">
                    <span>초미세먼지</span>
                    <b :style="{ color: pmGrade(districtsWeather[d].pm25, 'pm25').color }">{{ districtsWeather[d].pm25 }} ({{ pmGrade(districtsWeather[d].pm25, 'pm25').label }})</b>
                  </div>
                  <div class="v2-wd-row"><span>오존</span><b>{{ districtsWeather[d].o3 }} ppm</b></div>
                </div>
                <div class="v2-wd-tip">
                  <i :class="weatherTip(d).icon"></i>
                  <span>{{ weatherTip(d).text }}</span>
                </div>
                <!-- 내일 날씨 예보 -->
                <div class="v2-wd-tomorrow">
                  <div class="v2-wd-tm-header">
                    <i class="bi bi-sunrise-fill"></i>
                    <span>내일 예보</span>
                  </div>
                  <div class="v2-wd-tm-body">
                    <i class="v2-wd-tm-icon" :class="districtsWeather[d].tomorrow.icon" :style="{ color: districtsWeather[d].tomorrow.color }"></i>
                    <div class="v2-wd-tm-mid">
                      <div class="v2-wd-tm-cond">{{ districtsWeather[d].tomorrow.condition }}</div>
                      <div class="v2-wd-tm-temp">
                        <span class="hi">{{ districtsWeather[d].tomorrow.tempHi }}°</span>
                        <span class="sep">/</span>
                        <span class="lo">{{ districtsWeather[d].tomorrow.tempLo }}°</span>
                      </div>
                    </div>
                    <div class="v2-wd-tm-rain">
                      <i class="bi bi-droplet-fill"></i>
                      <span>{{ districtsWeather[d].tomorrow.rainProb }}%</span>
                    </div>
                  </div>
                  <div class="v2-wd-tm-meta">
                    <div><span>습도</span><b>{{ districtsWeather[d].tomorrow.humidity }}%</b></div>
                    <div><span>미세</span><b :style="{ color: pmGrade(districtsWeather[d].tomorrow.pm10, 'pm10').color }">{{ districtsWeather[d].tomorrow.pm10 }}</b></div>
                    <div><span>초미세</span><b :style="{ color: pmGrade(districtsWeather[d].tomorrow.pm25, 'pm25').color }">{{ districtsWeather[d].tomorrow.pm25 }}</b></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch, defineAsyncComponent } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";
import { useDashboardData } from "@/composables/useDashboardData";
import { useVideoOptimize } from "@/composables/useVideoOptimize";
import * as echarts from "echarts";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { DISTRICT_LIST, INITIAL_DISTRICTS_WEATHER } from "@/data/weather";
import { apiGet } from "@/api/client";

/* 대시보드 탭은 클릭 시점에 로드 — 첫 진입 시 overview만 빠르게 표시 */
const EventsTab     = defineAsyncComponent(() => import("@/components/dashboard/EventsTab.vue"));
const SearchTab     = defineAsyncComponent(() => import("@/components/dashboard/SearchTab.vue"));
const StatsTab      = defineAsyncComponent(() => import("@/components/dashboard/StatsTab.vue"));
const SettingsTab   = defineAsyncComponent(() => import("@/components/dashboard/SettingsTab.vue"));
const MonitoringTab = defineAsyncComponent(() => import("@/components/dashboard/MonitoringTab.vue"));

/* ── 공유 상태(composable) ── */
const {
  totalVehicles,
  inCount,
  outCount,
  dupRemoved,
  plates,
  cameraFeeds,
  cameraGroups,
  todayStr,
  dirLabel,
  plateImg,
  plateStatus,
  totalCamCount,
  stats,
  camCongestion,
  tickCamCongestion,
  notifications,
} = useDashboardData();

const router = useRouter();
const { currentUser, logout } = useAuth();
const displayName = computed(
  () => currentUser.value?.name || currentUser.value?.email?.split("@")[0] || "관리자"
);

/* ── 탭 ── */
const TABS = [
  { id: "overview",   label: "대시보드" },
  { id: "monitoring", label: "모니터링" },
  { id: "events",     label: "이벤트" },
  { id: "search",     label: "검색" },
  { id: "stats",      label: "통계" },
  { id: "settings",   label: "설정" },
];
const activeTab = ref("overview");
/* 한 번이라도 클릭된 탭만 마운트 — 첫 진입 시 overview 외 탭 컴포넌트는 다운로드/렌더 안 됨 */
const visitedTabs = ref(new Set(["overview"]));
watch(activeTab, (v) => { visitedTabs.value.add(v); });

/* 비디오 최적화 — overview 탭일 때만 6분할 영상 재생, 탭 비활성/뷰포트 밖 자동 정지 */
useVideoOptimize({ active: () => activeTab.value === "overview", selector: ".v2-cam-video" });

/* ── 헤더 ── */
const showNotif = ref(false);
const showUserMenu = ref(false);

function onUserMenu(action) {
  showUserMenu.value = false;
  if (action === "logout") {
    if (confirm("로그아웃 하시겠습니까?")) {
      logout();
      router.push("/");
    }
    return;
  }
  if (action === "settings" || action === "notify") {
    activeTab.value = "settings";
    return;
  }
  alert(`'${action}' 기능은 준비 중입니다.`);
}

function handleClickOutside(e) {
  if (showUserMenu.value && !e.target.closest(".v2-user-wrap"))
    showUserMenu.value = false;
  if (showNotif.value && !e.target.closest(".v2-notif-wrap")) showNotif.value = false;
  if (showHotspot.value && !e.target.closest(".v2-hotspot-wrap")) showHotspot.value = false;
}
const notifEdit = ref(false);
function removeNotif(id) {
  notifications.value = notifications.value.filter((n) => n.id !== id);
}
function clearAllNotif() {
  if (confirm("모든 알림을 삭제하시겠습니까?")) {
    notifications.value = [];
    notifEdit.value = false;
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
  else document.exitFullscreen?.();
}

/* ── KPI 카드 정의 ── */
const kpiCards = computed(() => [
  { label: '총 감지 차량', value: totalVehicles.value.toLocaleString(), unit: '대', diff: '8.2%',  up: true, theme: 'blue',   icon: 'bi bi-car-front' },
  { label: '진입 (IN)',    value: inCount.value.toLocaleString(),       unit: '대', diff: '5.4%',  up: true, theme: 'green',  icon: 'bi bi-box-arrow-in-down-right' },
  { label: '이탈 (OUT)',   value: outCount.value.toLocaleString(),      unit: '대', diff: '4.1%',  up: true, theme: 'orange', icon: 'bi bi-box-arrow-up-right' },
  { label: '혼잡도',       value: '혼잡',                                unit: '',   diff: '12.4%', up: true, theme: 'purple', icon: 'bi bi-exclamation-triangle' },
])

/* ── 카메라 그룹 (사이드바) ── */
/* ── 날씨/대기 환경 (사이드바 하단) ── */
const districtsWeather = ref({ ...INITIAL_DISTRICTS_WEATHER })
const currentDistrictIdx = ref(0)
const currentDistrictName = computed(() => DISTRICT_LIST[currentDistrictIdx.value])
const weather = computed(() => districtsWeather.value[currentDistrictName.value])
function selectDistrict(name) {
  const i = DISTRICT_LIST.indexOf(name)
  if (i >= 0) currentDistrictIdx.value = i
}
const showWeatherDetail = ref(false)
function weatherTip(d) {
  const w = districtsWeather.value[d]
  if (w.condition === '비' || w.condition === '뇌우')
    return { icon: 'bi bi-umbrella-fill', text: '우산 챙기세요. 도로 미끄러움 주의.' }
  if (w.condition === '눈')
    return { icon: 'bi bi-snow', text: '결빙 주의. 안전 운전 필수.' }
  if (w.pm25 > 35) return { icon: 'bi bi-shield-fill-exclamation', text: '초미세먼지 나쁨. 마스크 권장.' }
  if (w.pm10 > 80) return { icon: 'bi bi-shield-fill-exclamation', text: '미세먼지 나쁨. 외출 자제.' }
  if (w.aqi <= 50) return { icon: 'bi bi-check-circle-fill', text: '대기 좋음. 야외 활동 권장.' }
  return { icon: 'bi bi-info-circle-fill', text: '평소대로 외출 가능합니다.' }
}
function aqLabel(aqi) {
  if (aqi <= 50)  return { label: '좋음',     color: '#4caf7d' }
  if (aqi <= 100) return { label: '보통',     color: '#60a5fa' }
  if (aqi <= 150) return { label: '나쁨',     color: '#d4845a' }
  return                  { label: '매우나쁨', color: '#e05260' }
}
const aqGrade = computed(() => aqLabel(weather.value.aqi))
function pmGrade(v, kind) {
  const limits = kind === 'pm10' ? [30, 80, 150] : [15, 35, 75]
  if (v <= limits[0]) return { label: '좋음',     color: '#4caf7d' }
  if (v <= limits[1]) return { label: '보통',     color: '#60a5fa' }
  if (v <= limits[2]) return { label: '나쁨',     color: '#d4845a' }
  return                     { label: '매우나쁨', color: '#e05260' }
}
const pm10Pct = computed(() => Math.min(100, (weather.value.pm10 / 150) * 100))
const pm25Pct = computed(() => Math.min(100, (weather.value.pm25 / 75)  * 100))
const o3Pct   = computed(() => Math.min(100, (weather.value.o3   / 0.1) * 100))

const camQuery = ref("");
const allCams = computed(() => cameraGroups.flatMap((g) => g.cams));
function pct(n) {
  return ((n / totalCamCount.value) * 100).toFixed(1);
}
function statusLabel(s) {
  return s === "online" ? "정상" : s === "offline" ? "오프라인" : "오류";
}
const filteredGroups = computed(() => {
  const q = camQuery.value.trim();
  if (!q) return cameraGroups;
  return cameraGroups
    .map((g) => ({ ...g, cams: g.cams.filter((c) => c.name.includes(q)) }))
    .filter((g) => g.cams.length > 0);
});
const statusList = computed(() => allCams.value.slice(0, 5));

/* ── 카메라 모달 ── */
const modalCam = ref(null);
function openModal(f) {
  if (f.online) modalCam.value = f;
}

/* 영상 디코더 부하 완화 — 재생 속도 살짝 낮춰 CPU 부담 감소 */
function onCamLoaded(e) {
  try {
    const v = e.target
    v.playbackRate = 0.85
  } catch {}
}

/* ── OCR (오버뷰) ── */
/* 선택된 번호판 ID — 로그 클릭 시 메인 OCR 카드에 해당 항목 표시 */
const selectedPlateId = ref(null)
const latestPlate = computed(() => {
  if (selectedPlateId.value != null) {
    const found = plates.value.find(p => p.id === selectedPlateId.value)
    if (found) return found
  }
  return plates.value[0] || {}
})
const recentPlates = computed(() => plates.value.slice(0, 5))
const logPlates = computed(() => plates.value.slice(0, 8))
const failedPlateImageUrls = ref(new Set())

function plateDisplayImage(plate) {
  const url = plateImg(plate)
  return url && !failedPlateImageUrls.value.has(url) ? url : ''
}

function markPlateImageFailed(url) {
  if (!url) return
  const next = new Set(failedPlateImageUrls.value)
  next.add(url)
  failedPlateImageUrls.value = next
}

/* 이미지 우선순위: plateCropImageUrl → cropUrl → imageUrl → placeholder */
/* 백엔드 응답 → 프론트 데이터 정규화 (설계서 필드명 호환) */
function normalizePlate(p) {
  let d = '', t = ''
  if (p.detectedAt) {
    const dt = new Date(p.detectedAt)
    if (!isNaN(dt)) {
      d = dt.toLocaleDateString('sv-SE')
      t = dt.toLocaleTimeString('en-GB', { hour12: false })
    }
  }
  return {
    id:       p.logId ?? p.id ?? p.detectionLogId,
    num:      p.plateNumber ?? p.num ?? '미인식',
    cam:      p.cameraName ?? p.cameraCode ?? p.cam ?? '-',
    date:     p.date ?? d ?? todayStr,
    time:     p.time ?? t,
    conf:     p.conf ?? Math.round((p.confidenceScore ?? 0) * 100),
    dir:      (p.dir ?? p.directionType ?? 'IN').toLowerCase(),
    cropUrl:  p.cropUrl ?? p.plateCropImageUrl,
    imageUrl: p.imageUrl,
    ocrUrl:   p.ocrUrl ?? p.ocrImageUrl,
    status:   p.status ?? 'FLOW_EVENT_CREATED',
  }
}
function selectPlate(p) {
  selectedPlateId.value = p.id
}
/* 사이드바 카메라 클릭 → 6분할 강조 + HeatMap 위치로 이동 */
const selectedCamName = ref(null)
function selectCamera(cam) {
  selectedCamName.value = cam.name
  // HeatMap 좌표 이동
  if (heatMap && cam.coords) {
    heatMap.flyTo(cam.coords, 16, { duration: 1, easeLinearity: 0.25 })
  }
  // 메인 6분할에 있으면 해당 셀로 스크롤 (사용자 시선 유도)
  setTimeout(() => {
    const el = document.querySelector(`.v2-cam-cell[data-cam="${CSS.escape(cam.name)}"]`)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, 50)
}
const ocrDetails = computed(() => [
  { label: "인식 시간", value: `${todayStr} ${latestPlate.value.time || "-"}` },
  { label: "카메라", value: latestPlate.value.cam || "-" },
  {
    label: "흐름 방향",
    value: dirLabel(latestPlate.value.dir),
    dirClass: latestPlate.value.dir,
  },
  { label: "신뢰도", value: latestPlate.value.conf ? latestPlate.value.conf + "%" : "-" },
]);

/* ── 차트 (오버뷰) ── */
const congEl = ref(null);
const sparkEl = ref(null);
const donutEl = ref(null);
const charts = {};

const H24 = Array.from({ length: 25 }, (_, i) => `${String(i).padStart(2, "0")}:00`);
const rawS = [
  5,
  4,
  3,
  3,
  5,
  8,
  18,
  25,
  30,
  28,
  25,
  22,
  20,
  22,
  25,
  28,
  35,
  45,
  38,
  30,
  22,
  18,
  12,
  8,
  5,
];
const rawC = [
  3,
  2,
  2,
  2,
  3,
  6,
  22,
  42,
  55,
  60,
  58,
  52,
  48,
  52,
  60,
  70,
  78,
  85,
  82,
  72,
  55,
  38,
  22,
  12,
  6,
];
const rawJ = [
  1,
  0,
  0,
  0,
  1,
  3,
  12,
  28,
  42,
  58,
  70,
  80,
  75,
  78,
  90,
  95,
  92,
  88,
  78,
  60,
  38,
  22,
  10,
  4,
  2,
];
const TT = {
  trigger: "axis",
  backgroundColor: "#0a1727",
  borderColor: "rgba(255,255,255,.12)",
  textStyle: { color: "#e4eeff", fontSize: 12 },
};

function mkArea(name, data, color) {
  return {
    name,
    type: "line",
    data,
    smooth: true,
    symbol: "circle",
    symbolSize: 4,
    lineStyle: { color, width: 2 },
    itemStyle: { color, borderColor: "#0a1727", borderWidth: 1 },
    areaStyle: {
      color: {
        type: "linear",
        x: 0,
        y: 0,
        x2: 0,
        y2: 1,
        colorStops: [
          { offset: 0, color: color + "aa" },
          { offset: 1, color: color + "00" },
        ],
      },
    },
  };
}

function congOpt() {
  return {
    backgroundColor: "transparent",
    grid: { top: 18, right: 18, bottom: 28, left: 48 },
    tooltip: TT,
    xAxis: {
      type: "category",
      data: H24,
      boundaryGap: false,
      axisLine: { lineStyle: { color: "rgba(255,255,255,.08)" } },
      axisTick: { show: false },
      axisLabel: { color: "rgba(228,238,255,.4)", fontSize: 11, interval: 3 },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      axisLabel: { color: "rgba(228,238,255,.4)", fontSize: 11, formatter: "{value}%" },
      splitLine: { lineStyle: { color: "rgba(255,255,255,.05)" } },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      mkArea("원활", rawS, "#4caf7d"),
      mkArea("혼잡", rawC, "#d4845a"),
      mkArea("정체", rawJ, "#e05260"),
    ],
  };
}

function sparkOpt() {
  const d = [3200, 3400, 3600, 3500, 3750, 3800, 3842, 3820, 3900, 3950, 3842, 3900];
  return {
    backgroundColor: "transparent",
    grid: { top: 4, right: 4, bottom: 4, left: 4 },
    xAxis: { type: "category", show: false },
    yAxis: { type: "value", show: false },
    series: [
      {
        type: "line",
        data: d,
        smooth: true,
        symbol: "circle",
        symbolSize: 4,
        lineStyle: { color: "#60a5fa", width: 2 },
        itemStyle: { color: "#60a5fa" },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(96,165,250,.45)" },
              { offset: 1, color: "rgba(96,165,250,0)" },
            ],
          },
        },
      },
    ],
  };
}

function donutOpt() {
  const s = stats.value;
  return {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "item",
      backgroundColor: "#0a1727",
      borderColor: "rgba(255,255,255,.12)",
      textStyle: { color: "#e4eeff" },
    },
    series: [
      {
        type: "pie",
        radius: ["62%", "88%"],
        center: ["50%", "50%"],
        avoidLabelOverlap: false,
        label: { show: false },
        labelLine: { show: false },
        data: [
          { value: s.online, name: "정상", itemStyle: { color: "#4caf7d" } },
          { value: s.offline, name: "오프라인", itemStyle: { color: "#e05260" } },
          { value: s.error, name: "오류", itemStyle: { color: "#d4845a" } },
        ],
      },
    ],
  };
}

function initChart(key, el, opt) {
  if (!el) return;
  if (charts[key]) {
    try {
      charts[key].dispose();
    } catch {}
  }
  const c = echarts.init(el, null, { renderer: "canvas" });
  c.setOption(opt);
  charts[key] = c;
}
function resizeAll() {
  Object.values(charts).forEach((c) => {
    try {
      c.resize();
    } catch {}
  });
  try {
    heatMap?.invalidateSize();
  } catch {}
}

/* ── FastAPI 연동 (기존 유지) ── */
const FASTAPI_BASE = import.meta.env.VITE_FASTAPI_BASE_URL;
async function fetchRoadCongestion() {
  if (!FASTAPI_BASE) return null;
  try {
    const r = await fetch(`${FASTAPI_BASE}/api/v1/road-congestion`, {
      signal: AbortSignal.timeout(2000),
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}
/* Spring 연동: 최근 detection log를 OCR 패널/로그 테이블 계약으로 사용 */
async function fetchRecentPlates(limit = 20) {
  try {
    const body = await apiGet('/api/v1/detection-logs')
    return (body.data || []).slice(0, limit)
  } catch (error) {
    console.warn('Failed to load detection logs', error)
    return null
  }
}

async function refreshRecentPlates() {
  const apiPlates = await fetchRecentPlates(20);
  if (Array.isArray(apiPlates)) {
    plates.value = apiPlates.map(normalizePlate);
  }
}

/* ══ 지도 (Leaflet) ══ */
const heatmapEl = ref(null);
const heatLive = ref(true);
const heatReady = ref(false);
const osmFailed = ref(false);
let heatMap = null;

function heatColor(intensity) {
  return intensity > 0.8 ? "#e05260" : intensity > 0.6 ? "#d4845a" : "#4caf7d";
}
/* 도로 혼잡도(0~1) → 색상 5단계 */
function congestionColor(c) {
  if (c >= 0.85) return '#e74c3c'  // 정체 (빨강)
  if (c >= 0.65) return '#f39c12'  // 혼잡 (주황)
  if (c >= 0.45) return '#f1c40f'  // 보통 (노랑)
  if (c >= 0.25) return '#7dc242'  // 양호 (연두)
  return '#2ecc71'                 // 원활 (녹색)
}
function congestionLabel(c) {
  if (c >= 0.85) return '정체'
  if (c >= 0.65) return '혼잡'
  if (c >= 0.45) return '보통'
  if (c >= 0.25) return '양호'
  return '원활'
}
/* 폴리라인 인스턴스 보관 — 실시간 혼잡도 갱신 시 사용 */
const roadPolylines = new Map()

/* OSM Overpass에서 강남권 주요 도로 geometry 받아오기 (다중 미러 + 캐시) */
const OVERPASS_MIRRORS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
  'https://lz4.overpass-api.de/api/interpreter',
]
const OVERPASS_CACHE_KEY = 'osm-roads-v1-gangnam'
const OVERPASS_CACHE_TTL = 24 * 60 * 60 * 1000 // 24h

async function loadOSMRoads() {
  // 1) 캐시 확인 (24시간 유효)
  try {
    const raw = localStorage.getItem(OVERPASS_CACHE_KEY)
    if (raw) {
      const { ts, data } = JSON.parse(raw)
      if (Date.now() - ts < OVERPASS_CACHE_TTL && Array.isArray(data) && data.length) {
        console.info(`[OSM] 캐시 사용 (${data.length}개 도로)`)
        return data
      }
    }
  } catch {}

  const bbox = '37.470,127.000,37.540,127.140'
  const query = `[out:json][timeout:25];
(
  way["highway"~"^(motorway|trunk|primary|secondary)$"](${bbox});
);
out geom;`

  // 2) 미러 순차 시도
  for (const url of OVERPASS_MIRRORS) {
    try {
      const r = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'data=' + encodeURIComponent(query),
        signal: AbortSignal.timeout(12000),
      })
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data = await r.json()
      const ways = data.elements?.filter(e => e.type === 'way' && e.geometry?.length >= 2) || []
      if (ways.length) {
        try { localStorage.setItem(OVERPASS_CACHE_KEY, JSON.stringify({ ts: Date.now(), data: ways })) } catch {}
        console.info(`[OSM] ${url} ← ${ways.length}개 도로 로드 완료`)
        return ways
      }
    } catch (e) {
      console.warn(`[OSM Overpass] ${url} 실패: ${e.message}`)
    }
  }
  console.warn('[OSM Overpass] 모든 미러 실패 — 도로 표시 생략')
  return null
}

function renderOSMRoads(map, ways) {
  // 도로 종류별 굵기/우선순위
  const weights = { motorway: 6, trunk: 5.5, primary: 5, secondary: 4 }
  ways.forEach(way => {
    const path = way.geometry.map(p => [p.lat, p.lon])
    const hwy = way.tags?.highway
    const w = weights[hwy] || 4
    // 도로명 추출 (한글 우선)
    const name = way.tags?.['name:ko']
              || way.tags?.name
              || way.tags?.['name:en']
              || `${hwy} #${way.id}`
    // 초기 혼잡도는 도로 등급별로 다르게 + 약간의 랜덤성
    const baseCong = hwy === 'motorway' || hwy === 'trunk' ? 0.75
                   : hwy === 'primary' ? 0.55 : 0.35
    const c = Math.max(0.1, Math.min(0.95, baseCong + (Math.random() - 0.5) * 0.3))
    const seg = { name, c, hwy }
    const poly = L.polyline(path, {
      color: congestionColor(c),
      weight: w, opacity: 0.88,
      lineCap: 'round', lineJoin: 'round',
    })
    .bindTooltip('', {
      sticky: true, className: 'v2-road-tooltip',
      direction: 'top', offset: [0, -6],
    })
    .addTo(map)
    poly.__seg = seg
    updateRoadTooltip(poly)
    // 중복 이름 방지: 이미 있으면 인덱스 부여
    let key = name
    if (roadPolylines.has(key)) key = `${name}#${way.id}`
    roadPolylines.set(key, poly)
  })
  console.info(`[OSM] 도로 ${ways.length}개 로드 완료`)
}

async function retryOSMRoads() {
  if (!heatMap) return
  try { localStorage.removeItem(OVERPASS_CACHE_KEY) } catch {}
  osmFailed.value = false
  const ways = await loadOSMRoads()
  if (ways && ways.length > 0) {
    roadPolylines.forEach(p => { try { heatMap.removeLayer(p) } catch {} })
    roadPolylines.clear()
    renderOSMRoads(heatMap, ways)
  } else {
    osmFailed.value = true
  }
}

function updateRoadTooltip(poly) {
  const s = poly.__seg
  if (!s) return
  poly.setTooltipContent(
    `${s.name}<br/><b style="color:${congestionColor(s.c)}">${congestionLabel(s.c)}</b> · ${Math.round(s.c * 100)}%`
  )
}
/* 실시간 갱신 — 백엔드에서 [{ name, c }, ...] 받으면 폴리라인 색상 즉시 변경 */
function applyRoadCongestion(updates) {
  if (!Array.isArray(updates)) return
  updates.forEach(({ name, c }) => {
    const poly = roadPolylines.get(name)
    if (!poly) return
    poly.__seg.c = c
    poly.setStyle({ color: congestionColor(c) })
    updateRoadTooltip(poly)
  })
}

/* 혼잡 지점 — 사이드바 카메라 그룹의 24개 카메라를 그대로 사용, 혼잡도만 실시간 흔들림 */
const showHotspot = ref(false)
const hotspots = computed(() =>
  cameraGroups
    .flatMap(g => g.cams)
    .filter(c => c.status === 'online' && c.coords)
    .map((c, i) => ({
      id: 'cam-' + i,
      lat: c.coords[0],
      lng: c.coords[1],
      intensity: camCongestion.value[c.name] ?? 0.5,
      name: c.name,
    }))
    .sort((a, b) => b.intensity - a.intensity)
)
function hotspotLevel(intensity) {
  return intensity > 0.8 ? '정체' : intensity > 0.6 ? '혼잡' : '원활'
}
function flyToHotspot(spot) {
  showHotspot.value = false
  if (!heatMap) return
  heatMap.flyTo([spot.lat, spot.lng], 16, { duration: 1.2, easeLinearity: 0.25 })
}

async function initHeatMap() {
  if (!heatmapEl.value || heatMap) return;
  try {
    await new Promise((r) => setTimeout(r, 50));
    heatMap = L.map(heatmapEl.value, {
      center: [37.5025, 127.0480],
      zoom: 12,
      minZoom: 10,
      maxZoom: 20,
      zoomControl: true,
      attributionControl: false,
    });
    // 국내 지도(국토부 VWorld 다크) — 실패 시 CartoDB Dark Matter 폴백
    const vworld = L.tileLayer(
      "https://xdworld.vworld.kr/2d/midnight/202002/{z}/{x}/{y}.png",
      {
        maxZoom: 20,
        maxNativeZoom: 18,
      }
    );
    const cartoDark = L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
      {
        maxZoom: 20,
        maxNativeZoom: 19,
        subdomains: "abcd",
      }
    );
    vworld.on("tileerror", () => {
      heatMap.removeLayer(vworld);
      cartoDark.addTo(heatMap);
    });
    vworld.addTo(heatMap);

    // OSM Overpass API에서 실제 강남권 도로 geometry 가져오기
    // 실패 시 어긋난 하드코딩 폴백을 그리지 않고 도로 없이 지도만 표시(시각 정합성 우선)
    const osmRoads = await loadOSMRoads()
    if (osmRoads && osmRoads.length > 0) {
      renderOSMRoads(heatMap, osmRoads)
      osmFailed.value = false
    } else {
      osmFailed.value = true
    }
    heatReady.value = true;
    setTimeout(() => heatMap?.invalidateSize(), 200);
    setTimeout(() => heatMap?.invalidateSize(), 800);
  } catch (e) {
    console.warn("[Leaflet HeatMap] 로드 실패:", e.message);
    heatReady.value = false;
  }
}

const heatExpanded = ref(false);
function openHeatFullscreen() {
  heatExpanded.value = !heatExpanded.value;
  // CSS 토글이므로 Leaflet은 한 번만 재계산하면 됨
  nextTick().then(() => {
    if (!heatMap) return;
    const c = heatMap.getCenter();
    const z = heatMap.getZoom();
    heatMap.invalidateSize(true);
    heatMap.setView(c, z, { animate: false });
    // 일부 브라우저용 추가 안전망
    setTimeout(() => heatMap?.invalidateSize(true), 100);
  });
}
function onEscClose(e) {
  if (e.key === 'Escape' && heatExpanded.value) {
    heatExpanded.value = false;
    nextTick().then(() => heatMap?.invalidateSize(true));
  }
}

/* ── 라이프사이클 ── */
let dataT = null;
let districtT = null;

async function waitForRef(refObj, maxAttempts = 30) {
  for (let i = 0; i < maxAttempts; i++) {
    if (refObj.value) return true
    await new Promise(r => setTimeout(r, 30))
  }
  return false
}

onMounted(async () => {
  await nextTick()
  await nextTick()
  // vuedraggable 스코프 슬롯 안의 ref들이 바인딩될 때까지 대기
  await Promise.all([
    waitForRef(congEl),
    waitForRef(sparkEl),
    waitForRef(donutEl),
    waitForRef(heatmapEl),
  ])
  initChart("cong", congEl.value, congOpt())
  initChart("spark", sparkEl.value, sparkOpt())
  initChart("donut", donutEl.value, donutOpt())
  initHeatMap()
  window.addEventListener("resize", resizeAll)
  document.addEventListener("click", handleClickOutside)
  document.addEventListener("keydown", onEscClose)
  // 레이아웃 안정화 후 강제 리사이즈
  setTimeout(resizeAll, 80)
  setTimeout(resizeAll, 300)

  // 구별 날씨 5초마다 자동 회전
  districtT = setInterval(() => {
    currentDistrictIdx.value = (currentDistrictIdx.value + 1) % DISTRICT_LIST.length
  }, 5000)

  refreshRecentPlates()

  // 드래그로 카드 순서 바뀌면 차트 컨테이너가 재마운트되므로 재초기화
  watch([congEl, sparkEl, heatmapEl], async () => {
    await nextTick()
    setTimeout(() => {
      if (congEl.value && !charts.cong) initChart("cong", congEl.value, congOpt())
      if (sparkEl.value && !charts.spark) initChart("spark", sparkEl.value, sparkOpt())
      if (heatmapEl.value && !heatMap) initHeatMap()
      resizeAll()
    }, 80)
  })

  // 탭 전환 시 해당 탭 차트 초기화/리사이즈
  dataT = setInterval(async () => {
    if (!heatLive.value) return;
    totalVehicles.value = 2200 + Math.round(Math.random() * 400);
    inCount.value = 1100 + Math.round(Math.random() * 300);
    outCount.value = 1050 + Math.round(Math.random() * 280);
    dupRemoved.value = 150 + Math.round(Math.random() * 50);

    // 카메라별 혼잡도 한 틱 갱신 → 혼잡 지점 드롭다운 실시간 반영
    tickCamCongestion();

    // 실시간 도로 혼잡도 갱신 (현재 그려진 OSM 도로 기준)
    const apiCong = await fetchRoadCongestion();
    if (apiCong && Array.isArray(apiCong)) {
      applyRoadCongestion(apiCong);
    } else {
      // 백엔드 미연결 시 데모용으로 현재 도로의 혼잡도를 ±15% 범위에서 흔들기
      const demo = []
      roadPolylines.forEach((poly, name) => {
        const cur = poly.__seg?.c ?? 0.5
        demo.push({ name, c: Math.max(0.05, Math.min(0.99, cur + (Math.random() - 0.5) * 0.15)) })
      })
      applyRoadCongestion(demo);
    }

    await refreshRecentPlates()

    if (charts.donut) charts.donut.setOption(donutOpt());
  }, 3000);
});

onUnmounted(() => {
  clearInterval(dataT);
  clearInterval(districtT);
  window.removeEventListener("resize", resizeAll);
  document.removeEventListener("click", handleClickOutside);
  document.removeEventListener("keydown", onEscClose);
  Object.values(charts).forEach((c) => {
    try {
      c.dispose();
    } catch {}
  });
  try {
    heatMap?.remove();
  } catch {}
  heatMap = null;
});
</script>

<style src="@/styles/dashboard.css"></style>
