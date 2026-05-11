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
        <button
          class="v2-edit-btn"
          :class="{ active: editMode }"
          @click="editMode = !editMode"
          :title="editMode ? '편집 완료' : '카드 위치 편집'"
        >
          <i class="bi" :class="editMode ? 'bi-check2-circle' : 'bi-grip-horizontal'"></i>
          <span>{{ editMode ? '편집 완료' : '편집' }}</span>
        </button>
        <button class="v2-fs" @click="toggleFullscreen" title="전체화면">
          <i class="bi bi-arrows-fullscreen"></i>
        </button>
      </div>
    </header>

    <!-- ═══════════ BODY ═══════════ -->
    <div class="v2-body">
      <!-- ═══ LEFT SIDEBAR ═══ -->
      <aside class="v2-side">
        <draggable
          v-model="sideOrder"
          tag="div"
          item-key="key"
          class="v2-side-inner"
          :animation="200"
          :disabled="!editMode"
          ghost-class="v2-drag-ghost"
          chosen-class="v2-drag-chosen"
          filter="button, input, select, label, .v2-cam-cell, .v2-hotspot-wrap, .v2-heat-tools, .v2-aq-tools, .v2-aq-progress, .v2-log-more, .leaflet-container"
          :prevent-on-filter="false"
          @end="onDragEnd"
        >
          <template #item="{ element }">
            <div
              v-if="element.key === 'weather'"
              class="v2-panel v2-aq-panel"
              :class="{ 'v2-drag-on': editMode }"
            >
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

            <div
              v-else-if="element.key === 'cameras'"
              class="v2-panel v2-cam-panel"
              :class="{ 'v2-drag-on': editMode }"
            >
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
                    <div v-for="c in g.cams" :key="c.name" class="v2-tree-leaf">
                      <span class="v2-tree-dot" :class="c.status"></span>
                      <span>{{ c.name }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </draggable>
      </aside>

      <!-- ═══ MAIN ═══ -->
      <main class="v2-main">
        <!-- ════════ 대시보드 탭 ════════ -->
        <div v-show="activeTab === 'overview'" class="v2-tab-page">
          <!-- ROW 1: KPIs (드래그 가능) -->
          <draggable
            v-model="kpiOrder"
            tag="div"
            item-key="key"
            class="v2-kpi-row"
            :animation="200"
            :disabled="!editMode"
            ghost-class="v2-drag-ghost"
            chosen-class="v2-drag-chosen"
            filter="button, input, select, label, .v2-cam-cell, .v2-hotspot-wrap, .v2-heat-tools, .v2-aq-tools, .v2-aq-progress, .v2-log-more, .leaflet-container"
            :prevent-on-filter="false"
            @end="onDragEnd"
          >
            <template #item="{ element }">
              <div
                class="v2-kpi"
                :class="[`v2-kpi-${kpiByKey(element.key).theme}`, { 'v2-drag-on': editMode }]"
              >
                <div class="v2-kpi-icon">
                  <i :class="kpiByKey(element.key).icon"></i>
                </div>
                <div class="v2-kpi-body">
                  <div class="v2-kpi-label">{{ kpiByKey(element.key).label }}</div>
                  <div class="v2-kpi-value">
                    <span class="v2-kpi-num">{{ kpiByKey(element.key).value }}</span>
                    <span class="v2-kpi-unit">{{ kpiByKey(element.key).unit }}</span>
                  </div>
                  <div class="v2-kpi-diff" :class="{ down: !kpiByKey(element.key).up }">
                    전일 대비
                    <i class="bi" :class="kpiByKey(element.key).up ? 'bi-caret-up-fill' : 'bi-caret-down-fill'"></i>
                    {{ kpiByKey(element.key).diff }}
                  </div>
                </div>
              </div>
            </template>
          </draggable>

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

            <draggable
              v-model="r2RightOrder"
              tag="div"
              item-key="key"
              class="v2-col-right-r2"
              :animation="200"
              :disabled="!editMode"
              ghost-class="v2-drag-ghost"
              chosen-class="v2-drag-chosen"
              filter="button, input, select, label, .v2-cam-cell, .v2-hotspot-wrap, .v2-heat-tools, .v2-aq-tools, .v2-aq-progress, .v2-log-more, .leaflet-container"
              :prevent-on-filter="false"
              @end="onDragEnd"
            >
              <template #item="{ element }">
                <section
                  v-if="element.key === 'cong'"
                  class="v2-card v2-cong-card"
                  :class="{ 'v2-drag-on': editMode }"
                >
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

                <section
                  v-else-if="element.key === 'flow'"
                  class="v2-card v2-flow-card"
                  :class="{ 'v2-drag-on': editMode }"
                >
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
              </template>
            </draggable>
          </div>

          <!-- ROW 3: OCR / HeatMap / Status (드래그 가능) -->
          <draggable
            v-model="r3Order"
            tag="div"
            item-key="key"
            class="v2-row3-grid"
            :animation="200"
            :disabled="!editMode"
            ghost-class="v2-drag-ghost"
            chosen-class="v2-drag-chosen"
            filter="button, input, select, label, .v2-cam-cell, .v2-hotspot-wrap, .v2-heat-tools, .v2-aq-tools, .v2-aq-progress, .v2-log-more, .leaflet-container"
            :prevent-on-filter="false"
            @end="onDragEnd"
          >
            <template #item="{ element }">
              <section
                v-if="element.key === 'ocr'"
                class="v2-card v2-ocr-card"
                :class="{ 'v2-drag-on': editMode }"
              >
                <div class="v2-card-h">
                  <span><i class="bi bi-upc-scan"></i>OCR 인식 결과 (실시간)</span>
                </div>
                <div class="v2-ocr-body">
                  <div class="v2-ocr-photo">
                    <div class="v2-plate-vis">
                      <div class="v2-plate-num mono">{{ latestPlate.num || "128가 4567" }}</div>
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
                  <div v-for="p in recentPlates" :key="p.id" class="v2-ocr-thumb">
                    <div class="v2-ocr-thumb-time mono">{{ p.time }}</div>
                    <div class="v2-ocr-thumb-plate mono">{{ p.num }}</div>
                  </div>
                </div>
              </section>

              <section
                v-else-if="element.key === 'heat'"
                class="v2-card v2-heat-card"
                :class="{ 'v2-drag-on': editMode, 'v2-heat-expanded': heatExpanded }"
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
                <!-- 카카오맵 로드 실패 시 SVG 폴백 -->
                <svg
                  v-if="!heatReady"
                  class="v2-heat-fb"
                  viewBox="0 0 400 320"
                  preserveAspectRatio="xMidYMid slice"
                >
                  <defs>
                    <radialGradient
                      v-for="(p, i) in heatPts"
                      :key="'g' + i"
                      :id="'hg' + i"
                    >
                      <stop
                        offset="0%"
                        :stop-color="heatColor(p[2])"
                        stop-opacity="0.85"
                      />
                      <stop
                        offset="55%"
                        :stop-color="heatColor(p[2])"
                        stop-opacity="0.35"
                      />
                      <stop
                        offset="100%"
                        :stop-color="heatColor(p[2])"
                        stop-opacity="0"
                      />
                    </radialGradient>
                  </defs>
                  <rect width="400" height="320" fill="#0a1929" />
                  <!-- 도로 격자 -->
                  <g stroke="rgba(140, 170, 210, .18)" stroke-width="1">
                    <line
                      v-for="x in [40, 80, 130, 180, 220, 260, 310, 360]"
                      :key="'vx' + x"
                      :x1="x"
                      y1="0"
                      :x2="x"
                      y2="320"
                    />
                    <line
                      v-for="y in [40, 80, 120, 160, 200, 240, 280]"
                      :key="'hy' + y"
                      x1="0"
                      :y1="y"
                      x2="400"
                      :y2="y"
                    />
                  </g>
                  <!-- 주요 간선도로 -->
                  <g stroke="rgba(160, 190, 230, .35)" stroke-width="2">
                    <line x1="0" y1="160" x2="400" y2="160" />
                    <line x1="200" y1="0" x2="200" y2="320" />
                    <line x1="0" y1="80" x2="400" y2="80" />
                    <line x1="130" y1="0" x2="130" y2="320" />
                  </g>
                  <!-- 히트 원 -->
                  <g v-for="(p, i) in heatPts" :key="'h' + i">
                    <circle
                      :cx="fbX(p[1])"
                      :cy="fbY(p[0])"
                      :r="60 * p[2]"
                      :fill="`url(#hg${i})`"
                    />
                    <circle
                      :cx="fbX(p[1])"
                      :cy="fbY(p[0])"
                      r="4"
                      :fill="heatColor(p[2])"
                    />
                  </g>
                  <!-- 라벨 -->
                  <g
                    fill="rgba(200, 215, 235, .5)"
                    font-size="9"
                    font-family="Pretendard, sans-serif"
                  >
                    <text x="180" y="155">테헤란로</text>
                    <text x="140" y="75">강남대로</text>
                    <text x="305" y="200">잠실</text>
                    <text x="55" y="245">서초</text>
                  </g>
                </svg>
                <div class="v2-heat-legend">
                  <span class="v2-heat-legend-label top">높음</span>
                  <div class="v2-heat-bar"></div>
                  <span class="v2-heat-legend-label bot">낮음</span>
                </div>
              </div>
            </section>

              <section
                v-else-if="element.key === 'status'"
                class="v2-card v2-status-card"
                :class="{ 'v2-drag-on': editMode }"
              >
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
            </template>
          </draggable>

          <!-- ROW 4: OCR 로그 (풀폭, 드래그 불가) -->
          <section class="v2-card v2-log-card v2-log-row">
            <div class="v2-card-h">
              <span><i class="bi bi-list-ul"></i>OCR 인식 로그 (중복 제거 후)</span>
              <button class="v2-log-more">전체 보기 ›</button>
            </div>
            <div class="v2-log-table">
              <div class="v2-lt-head">
                <span>번호</span>
                <span>인식 시간</span>
                <span>카메라</span>
                <span>차량 번호</span>
                <span>흐름 방향</span>
                <span>신뢰도</span>
              </div>
              <div v-for="(p, i) in logPlates" :key="p.id" class="v2-lt-row">
                <span>{{ i + 1 }}</span>
                <span class="mono">{{ todayStr }} {{ p.time }}</span>
                <span>{{ p.cam }}</span>
                <span class="mono">{{ p.num }}</span>
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
        <MonitoringTab :active="activeTab === 'monitoring'" />

        <!-- ════════ 이벤트 탭 ════════ -->
        <EventsTab v-show="activeTab === 'events'" />

        <!-- ════════ 검색 탭 ════════ -->
        <SearchTab v-show="activeTab === 'search'" />

        <!-- ════════ 통계 탭 ════════ -->
        <StatsTab :active="activeTab === 'stats'" />

        <!-- ════════ 설정 탭 ════════ -->
        <SettingsTab v-show="activeTab === 'settings'" />

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
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "@/composables/useAuth";
import { useDashboardData } from "@/composables/useDashboardData";
import EventsTab from "@/components/dashboard/EventsTab.vue";
import SearchTab from "@/components/dashboard/SearchTab.vue";
import StatsTab from "@/components/dashboard/StatsTab.vue";
import SettingsTab from "@/components/dashboard/SettingsTab.vue";
import MonitoringTab from "@/components/dashboard/MonitoringTab.vue";
import draggable from "vuedraggable";
import * as echarts from "echarts";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

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
  totalCamCount,
  stats,
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
const notifications = ref([
  {
    id: 1,
    msg: "테헤란로 교차로 혼잡 감지 — 진입 +42%",
    time: "14:32",
    color: "#e05260",
  },
  { id: 2, msg: "CAM-03 강남역 OCR 인식률 저하 (78%)", time: "14:28", color: "#d4845a" },
  { id: 3, msg: "반포IC 이탈 차량 급증", time: "14:15", color: "#d4845a" },
  { id: 4, msg: "올림픽대로 흐름 원활 전환", time: "13:58", color: "#4caf7d" },
  { id: 5, msg: "OCR 파이프라인 정상 가동", time: "13:45", color: "#4caf7d" },
  { id: 6, msg: "잠실역 사거리 진입 트래픽 급증", time: "13:30", color: "#d4845a" },
  { id: 7, msg: "양재역 사거리 흐름 정상화", time: "13:02", color: "#4caf7d" },
  { id: 8, msg: "남부터미널 정체 시작 — 평균 12 km/h", time: "12:36", color: "#e05260" },
  { id: 9, msg: "석촌역 이탈 차량 통행 증가", time: "12:14", color: "#d4845a" },
  { id: 10, msg: "강남구 전역 평균 정상", time: "11:55", color: "#4caf7d" },
  { id: 11, msg: "중복 감지 178건 자동 제거 완료", time: "11:30", color: "#4caf7d" },
  { id: 12, msg: "WebSocket 연결 정상", time: "11:00", color: "#4caf7d" },
]);
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

/* ── 편집 모드 + 드래그 순서 ── */
const editMode = ref(false)
function loadOrder(key, defaults) {
  try {
    const saved = JSON.parse(localStorage.getItem(key))
    if (Array.isArray(saved) && saved.length === defaults.length &&
        saved.every(k => defaults.includes(k))) {
      return saved.map(k => ({ key: k }))
    }
  } catch {}
  return defaults.map(k => ({ key: k }))
}
const kpiOrder     = ref(loadOrder('kpiOrder',     ['total', 'in', 'out', 'congestion']))
const r2RightOrder = ref(loadOrder('r2RightOrder', ['cong', 'flow']))
const r3Order      = ref(loadOrder('r3Order',      ['ocr', 'heat', 'status']))
const sideOrder    = ref(loadOrder('sideOrder',    ['weather', 'cameras']))
function persistOrders() {
  localStorage.setItem('kpiOrder',     JSON.stringify(kpiOrder.value.map(x => x.key)))
  localStorage.setItem('r2RightOrder', JSON.stringify(r2RightOrder.value.map(x => x.key)))
  localStorage.setItem('r3Order',      JSON.stringify(r3Order.value.map(x => x.key)))
  localStorage.setItem('sideOrder',    JSON.stringify(sideOrder.value.map(x => x.key)))
}
function onDragEnd() { persistOrders() }

/* ── KPI 카드 정의 (값은 composable의 ref와 연결) ── */
function kpiByKey(key) {
  const defs = {
    total:      { label: '총 감지 차량', value: totalVehicles.value.toLocaleString(), unit: '대', diff: '8.2%',  up: true, theme: 'blue',   icon: 'bi bi-car-front' },
    in:         { label: '진입 (IN)',    value: inCount.value.toLocaleString(),       unit: '대', diff: '5.4%',  up: true, theme: 'green',  icon: 'bi bi-box-arrow-in-down-right' },
    out:        { label: '이탈 (OUT)',   value: outCount.value.toLocaleString(),      unit: '대', diff: '4.1%',  up: true, theme: 'orange', icon: 'bi bi-box-arrow-up-right' },
    congestion: { label: '혼잡도',       value: '혼잡',                                unit: '',   diff: '12.4%', up: true, theme: 'purple', icon: 'bi bi-exclamation-triangle' },
  }
  return defs[key]
}

/* ── 카메라 그룹 (사이드바) ── */
/* ── 날씨/대기 환경 (사이드바 하단) ── */
const WEATHER_PRESETS = {
  clear:   { condition: '맑음',     icon: 'bi bi-sun-fill',                color: '#fbbf24' },
  pcloud:  { condition: '구름 조금', icon: 'bi bi-cloud-sun-fill',          color: '#93c5fd' },
  cloudy:  { condition: '흐림',     icon: 'bi bi-clouds-fill',             color: '#94a3b8' },
  rain:    { condition: '비',       icon: 'bi bi-cloud-rain-heavy-fill',   color: '#60a5fa' },
  drizzle: { condition: '이슬비',   icon: 'bi bi-cloud-drizzle-fill',      color: '#7dd3fc' },
  snow:    { condition: '눈',       icon: 'bi bi-cloud-snow-fill',         color: '#e0f2fe' },
  thunder: { condition: '뇌우',     icon: 'bi bi-cloud-lightning-rain-fill', color: '#a78bfa' },
  fog:     { condition: '안개',     icon: 'bi bi-cloud-fog2-fill',         color: '#cbd5e1' },
  haze:    { condition: '미세먼지', icon: 'bi bi-cloud-haze2-fill',        color: '#d4845a' },
}
const DISTRICT_LIST = ['강남구', '서초구', '송파구']
const districtsWeather = ref({
  강남구: {
    ...WEATHER_PRESETS.cloudy, aqi: 75, temp: 22, humidity: 60, pm10: 45, pm25: 22, o3: 0.038, wind: 2.4, uv: 5,  visibility: 8,
    tomorrow: { ...WEATHER_PRESETS.clear,  tempHi: 25, tempLo: 17, humidity: 55, pm10: 32, pm25: 16, rainProb: 10 },
  },
  서초구: {
    ...WEATHER_PRESETS.pcloud, aqi: 62, temp: 21, humidity: 55, pm10: 38, pm25: 18, o3: 0.032, wind: 3.1, uv: 6,  visibility: 11,
    tomorrow: { ...WEATHER_PRESETS.clear,  tempHi: 24, tempLo: 16, humidity: 52, pm10: 28, pm25: 13, rainProb: 5 },
  },
  송파구: {
    ...WEATHER_PRESETS.rain,   aqi: 88, temp: 20, humidity: 78, pm10: 52, pm25: 28, o3: 0.041, wind: 4.5, uv: 2,  visibility: 5,
    tomorrow: { ...WEATHER_PRESETS.cloudy, tempHi: 22, tempLo: 15, humidity: 70, pm10: 42, pm25: 20, rainProb: 40 },
  },
})
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
const latestPlate = computed(() => plates.value[0] || {});
const recentPlates = computed(() => plates.value.slice(0, 5));
const logPlates = computed(() => plates.value.slice(0, 8));
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
    kakaoHeat?.invalidateSize();
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

/* ══ 지도 (Leaflet) ══ */
const heatmapEl = ref(null);
const heatLive = ref(true);
const heatReady = ref(false);
let kakaoHeat = null;

function heatColor(intensity) {
  return intensity > 0.8 ? "#e05260" : intensity > 0.6 ? "#d4845a" : "#4caf7d";
}
// 위경도 → 폴백 SVG 좌표(서울 강남권 대략 매핑)
function fbX(lng) {
  return ((lng - 127.0) / 0.11) * 400;
}
function fbY(lat) {
  return 320 - ((lat - 37.47) / 0.05) * 320;
}
const heatPts = [
  [37.4979, 127.0276, 0.95, '강남대로 교차로'],
  [37.5013, 127.0375, 0.88, '테헤란로 사거리'],
  [37.5005, 127.0368, 0.82, '역삼역 사거리'],
  [37.5044, 127.049,  0.75, '선릉역 사거리'],
  [37.513,  127.1,    0.65, '잠실역 부근'],
  [37.4934, 127.0139, 0.78, '강남역 사거리'],
  [37.4833, 127.0116, 0.55, '양재역 부근'],
  [37.4849, 127.0339, 0.52, '도곡역 사거리'],
  [37.496,  127.0285, 0.9,  '강남파이낸스센터'],
  [37.502,  127.044,  0.7,  '선정릉 사거리'],
  [37.5088, 127.0603, 0.62, '잠실 종합운동장'],
  [37.489,  127.019,  0.72, '강남구청 사거리'],
];

/* 혼잡 지점 (강도 순 정렬) */
const showHotspot = ref(false)
const hotspots = computed(() =>
  heatPts
    .map(([lat, lng, intensity, name], i) => ({ id: i, lat, lng, intensity, name }))
    .sort((a, b) => b.intensity - a.intensity)
)
function hotspotLevel(intensity) {
  return intensity > 0.8 ? '정체' : intensity > 0.6 ? '혼잡' : '원활'
}
function flyToHotspot(spot) {
  showHotspot.value = false
  if (!kakaoHeat) return
  kakaoHeat.flyTo([spot.lat, spot.lng], 16, { duration: 1.2, easeLinearity: 0.25 })
}

async function initHeatMap() {
  if (!heatmapEl.value || kakaoHeat) return;
  try {
    await new Promise((r) => setTimeout(r, 50));
    kakaoHeat = L.map(heatmapEl.value, {
      center: [37.4979, 127.0276],
      zoom: 13,
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
      kakaoHeat.removeLayer(vworld);
      cartoDark.addTo(kakaoHeat);
    });
    vworld.addTo(kakaoHeat);

    // 펄스 라이프 마커 — 각 핫스팟이 애니메이션 글로우로 빛남
    heatPts.forEach(([lat, lng, intensity]) => {
      const color = heatColor(intensity);
      const lv = intensity > 0.8 ? "high" : intensity > 0.6 ? "mid" : "low";
      const icon = L.divIcon({
        className: "v2-radar-marker",
        html: `
          <div class="rm-pulse" style="border-color:${color}"></div>
          <div class="rm-pulse rm-pulse-2" style="border-color:${color}"></div>
          <div class="rm-glow" style="background:${color}"></div>
          <div class="rm-core" style="background:${color};box-shadow:0 0 14px ${color},0 0 28px ${color}"></div>
        `,
        iconSize: [50, 50],
        iconAnchor: [25, 25],
      });
      L.marker([lat, lng], { icon, interactive: false }).addTo(kakaoHeat);
      // 보조 히트 글로우 (반경 표현)
      L.circle([lat, lng], {
        radius: 350 * intensity,
        weight: 0,
        fillColor: color,
        fillOpacity: 0.12,
        interactive: false,
        className: `v2-heat-blob v2-heat-${lv}`,
      }).addTo(kakaoHeat);
    });
    heatReady.value = true;
    setTimeout(() => kakaoHeat?.invalidateSize(), 200);
    setTimeout(() => kakaoHeat?.invalidateSize(), 800);
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
    if (!kakaoHeat) return;
    const c = kakaoHeat.getCenter();
    const z = kakaoHeat.getZoom();
    kakaoHeat.invalidateSize(true);
    kakaoHeat.setView(c, z, { animate: false });
    // 일부 브라우저용 추가 안전망
    setTimeout(() => kakaoHeat?.invalidateSize(true), 100);
  });
}
function onEscClose(e) {
  if (e.key === 'Escape' && heatExpanded.value) {
    heatExpanded.value = false;
    nextTick().then(() => kakaoHeat?.invalidateSize(true));
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

  // 드래그로 카드 순서 바뀌면 차트 컨테이너가 재마운트되므로 재초기화
  watch([congEl, sparkEl, heatmapEl], async () => {
    await nextTick()
    setTimeout(() => {
      if (congEl.value && !charts.cong) initChart("cong", congEl.value, congOpt())
      if (sparkEl.value && !charts.spark) initChart("spark", sparkEl.value, sparkOpt())
      if (heatmapEl.value && !kakaoHeat) initHeatMap()
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

    const apiCong = await fetchRoadCongestion();
    if (apiCong && Array.isArray(apiCong)) {
      // FastAPI 응답 처리 (기존 인터페이스 유지)
    }

    const now = new Date();
    const ts = [now.getHours(), now.getMinutes(), now.getSeconds()]
      .map((v) => String(v).padStart(2, "0"))
      .join(":");
    const cams = cameraFeeds.map((c) => c.name);
    plates.value = [
      {
        id: Date.now(),
        num: `${Math.floor(10 + Math.random() * 89)}${
          "가나다라마바사아자차"[Math.floor(Math.random() * 10)]
        } ${Math.floor(1000 + Math.random() * 9000)}`,
        cam: cams[Math.floor(Math.random() * cams.length)],
        time: ts,
        conf: 88 + Math.round(Math.random() * 10),
        dir: Math.random() > 0.5 ? "in" : "out",
      },
      ...plates.value,
    ].slice(0, 20);

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
    kakaoHeat?.remove();
  } catch {}
  kakaoHeat = null;
});
</script>

<style>
/* ═════════ ROOT ═════════ */
.v2-root {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: #0b1726;
  color: #e4eeff;
  font-family: "Pretendard Variable", Pretendard, "Noto Sans KR", sans-serif;
  font-size: 13px;
}
.mono {
  font-family: "JetBrains Mono", monospace;
  font-variant-numeric: tabular-nums;
}

/* ═════════ HEADER ═════════ */
.v2-header {
  display: flex;
  align-items: center;
  height: 56px;
  flex-shrink: 0;
  padding: 0 20px;
  background: #0f1d30;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-right: 32px;
}
.v2-logo:hover {
  opacity: 0.85;
}
.v2-logo-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #60a5fa;
  box-shadow: 0 0 10px #60a5fa;
  flex-shrink: 0;
  animation: v2-live-pulse 2s ease-in-out infinite;
}
@keyframes v2-live-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.25; transform: scale(0.85); }
}
.v2-logo-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.3px;
}
.v2-logo-text em {
  font-style: normal;
  font-weight: 500;
  color: rgba(228, 238, 255, 0.65);
  margin-left: 4px;
}

.v2-tab-nav {
  display: flex;
  align-items: center;
  height: 56px;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.v2-tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 22px;
  height: 36px;
  background: transparent;
  border: none;
  color: rgba(228, 238, 255, 0.55);
  font-size: 14px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.15s;
  font-weight: 500;
}
.v2-tab-btn:hover {
  color: #e4eeff;
  background: rgba(255, 255, 255, 0.04);
}
.v2-tab-btn.active {
  color: #fff;
  background: rgba(96, 165, 250, 0.18);
  font-weight: 600;
}

.v2-header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.v2-notif-wrap {
  position: relative;
}
.v2-notif {
  position: relative;
  background: none;
  border: none;
  color: rgba(228, 238, 255, 0.7);
  font-size: 18px;
  cursor: pointer;
  padding: 4px 6px;
}
.v2-notif:hover {
  color: #e4eeff;
}
.v2-notif-n {
  position: absolute;
  top: -2px;
  right: -4px;
  background: #e05260;
  color: #fff;
  font-size: 10px;
  min-width: 18px;
  height: 16px;
  border-radius: 8px;
  padding: 0 5px;
  display: grid;
  place-items: center;
  font-weight: 700;
}
.v2-notif-panel {
  position: absolute;
  right: 0;
  top: 36px;
  width: 320px;
  max-height: 420px;
  overflow-y: auto;
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
  z-index: 100;
}
.v2-notif-ph {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 13px;
  font-weight: 600;
}
.v2-notif-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}
.v2-notif-badge {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.55);
}
.v2-notif-edit {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  font-size: 11px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(228, 238, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  transition: all 0.15s;
}
.v2-notif-edit:hover {
  background: rgba(255, 255, 255, 0.12);
}
.v2-notif-edit.active {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
  border-color: rgba(96, 165, 250, 0.35);
}
.v2-notif-empty {
  padding: 20px 14px;
  text-align: center;
  font-size: 12px;
  color: rgba(228, 238, 255, 0.4);
}
.v2-ni {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s;
}
.v2-ni-edit {
  background: rgba(255, 255, 255, 0.02);
}
.v2-ni-edit:hover {
  background: rgba(224, 82, 96, 0.06);
}
.v2-ni-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}
.v2-ni-body {
  flex: 1;
  min-width: 0;
}
.v2-ni-msg {
  font-size: 12px;
  color: rgba(228, 238, 255, 0.85);
}
.v2-ni-t {
  font-size: 10px;
  color: rgba(228, 238, 255, 0.4);
  margin-top: 2px;
}
.v2-ni-del {
  background: none;
  border: none;
  color: #e05260;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 6px;
  line-height: 1;
  border-radius: 3px;
  flex-shrink: 0;
}
.v2-ni-del:hover {
  background: rgba(224, 82, 96, 0.15);
}
.v2-notif-foot {
  padding: 10px 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-notif-clear {
  width: 100%;
  padding: 7px 10px;
  background: rgba(224, 82, 96, 0.1);
  color: #e05260;
  border: 1px solid rgba(224, 82, 96, 0.2);
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.v2-notif-clear:hover {
  background: rgba(224, 82, 96, 0.2);
}

/* 히트맵 펄스 라이프 마커 */
.v2-radar-marker {
  position: relative;
  width: 50px;
  height: 50px;
  pointer-events: none;
}
.v2-radar-marker .rm-core {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  z-index: 4;
}
.v2-radar-marker .rm-glow {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  opacity: 0.45;
  filter: blur(4px);
  z-index: 3;
}
.v2-radar-marker .rm-pulse {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border-width: 2px;
  border-style: solid;
  opacity: 0;
  animation: rm-ping 2.4s cubic-bezier(0.16, 1, 0.3, 1) infinite;
  z-index: 2;
}
.v2-radar-marker .rm-pulse-2 {
  animation-delay: 1.2s;
}
@keyframes rm-ping {
  0% {
    width: 14px;
    height: 14px;
    opacity: 0.85;
  }
  60% {
    opacity: 0.4;
  }
  100% {
    width: 70px;
    height: 70px;
    opacity: 0;
  }
}
.v2-heat-map .v2-heat-blob {
  filter: blur(8px);
  mix-blend-mode: screen;
}

.v2-user {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: background 0.15s;
}
.v2-user:hover {
  background: rgba(255, 255, 255, 0.09);
}
.v2-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa, #2a7de1);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 12px;
}
.v2-user span {
  font-size: 13px;
  color: rgba(228, 238, 255, 0.9);
}
.v2-caret {
  font-size: 9px;
  color: rgba(228, 238, 255, 0.5);
  transition: transform 0.2s;
}
.v2-caret.open {
  transform: rotate(180deg);
}

/* ─── 관리자 드롭다운 메뉴 ─── */
.v2-user-wrap {
  position: relative;
}
.v2-user-menu {
  position: absolute;
  right: 0;
  top: 44px;
  width: 260px;
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
  padding: 8px 0;
  z-index: 200;
  overflow: hidden;
}
.v2-um-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
}
.v2-avatar-lg {
  width: 38px;
  height: 38px;
  font-size: 14px;
}
.v2-um-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.v2-um-name {
  font-size: 13px;
  font-weight: 600;
  color: #e4eeff;
}
.v2-um-role {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.55);
}
.v2-um-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin: 4px 0;
}
.v2-um-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 14px;
  background: none;
  border: none;
  color: rgba(228, 238, 255, 0.85);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}
.v2-um-item:hover {
  background: rgba(255, 255, 255, 0.05);
}
.v2-um-item i {
  font-size: 14px;
  color: rgba(96, 165, 250, 0.85);
  width: 16px;
}
.v2-um-logout i {
  color: #e05260;
}
.v2-um-logout:hover {
  background: rgba(224, 82, 96, 0.08);
}
.v2-fs {
  background: none;
  border: none;
  color: rgba(228, 238, 255, 0.7);
  font-size: 16px;
  cursor: pointer;
  padding: 6px;
}
.v2-fs:hover {
  color: #e4eeff;
}

/* 편집 모드 버튼 */
.v2-edit-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 12px; font-size: 12px; font-weight: 500;
  background: rgba(255,255,255,.06); color: rgba(228,238,255,.85);
  border: 1px solid rgba(255,255,255,.08); border-radius: 16px;
  cursor: pointer; transition: all .15s;
}
.v2-edit-btn:hover { background: rgba(255,255,255,.12); }
.v2-edit-btn.active {
  background: rgba(96,165,250,.2); color: #60a5fa;
  border-color: rgba(96,165,250,.45);
}
.v2-edit-btn i { font-size: 13px; }

/* 드래그 시각 효과 */
.v2-drag-on {
  cursor: grab;
  outline: 1px dashed rgba(96,165,250,.4);
  outline-offset: -3px;
}
.v2-drag-on:active { cursor: grabbing; }
.v2-drag-ghost {
  opacity: 0.4;
  background: rgba(96,165,250,.1) !important;
}
.v2-drag-chosen {
  outline: 2px solid #60a5fa !important;
  outline-offset: -3px;
}

/* ═════════ BODY ═════════ */
.v2-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

/* ═════════ LEFT SIDEBAR ═════════ */
.v2-side {
  width: 240px;
  flex-shrink: 0;
  padding: 12px;
  background: #0b1726;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.v2-side-inner {
  flex: 1; min-height: 0;
  display: flex; flex-direction: column; gap: 12px;
}
.v2-panel {
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.v2-cam-panel {
  flex: 1;
  min-height: 0;
}
.v2-map-panel {
  height: 200px;
  flex-shrink: 0;
}

/* ─── 날씨 / 대기 환경 패널 ─── */
.v2-aq-panel { flex-shrink: 0; }
.v2-aq-loc {
  font-size: 10px; color: rgba(228,238,255,.5);
  padding: 1px 7px; background: rgba(255,255,255,.05); border-radius: 8px;
}
.v2-aq-body { padding: 10px 12px 12px; display: flex; flex-direction: column; gap: 10px; }

/* 날씨 메인 */
.v2-aq-weather {
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 10px; align-items: center;
  padding: 8px 6px;
  background: rgba(255,255,255,.03);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 6px;
}
.v2-aq-w-icon {
  font-size: 32px;
  filter: drop-shadow(0 0 8px currentColor);
  transition: color .3s;
}
.v2-aq-w-mid { min-width: 0; }
.v2-aq-w-cond { font-size: 13px; font-weight: 700; color: #e4eeff; line-height: 1.1; }
.v2-aq-w-aqi {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 10px; font-weight: 600; margin-top: 4px;
}
.v2-aq-w-dot {
  width: 6px; height: 6px; border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}
.v2-aq-w-temp { text-align: right; }
.v2-aq-w-tnum { font-size: 18px; font-weight: 800; color: #e4eeff; line-height: 1; }
.v2-aq-w-tnum small { font-size: 11px; font-weight: 500; color: rgba(228,238,255,.55); margin-left: 1px; }
.v2-aq-w-tsub { font-size: 9px; color: rgba(228,238,255,.5); margin-top: 3px; }

/* 대기질 지표 */
.v2-aq-list { display: flex; flex-direction: column; gap: 5px; }
.v2-aq-item {
  display: grid; grid-template-columns: 44px 1fr 32px;
  gap: 6px; align-items: center;
}
.v2-aq-k { font-size: 10px; color: rgba(228,238,255,.6); font-weight: 500; }
.v2-aq-bar {
  height: 4px; background: rgba(255,255,255,.06); border-radius: 2px; overflow: hidden;
}
.v2-aq-fill { height: 100%; border-radius: 2px; transition: width .4s, background .4s; }
.v2-aq-v { font-size: 11px; font-weight: 700; text-align: right; color: #e4eeff; }

/* 헤더 도구 */
.v2-aq-tools { display: flex; align-items: center; gap: 6px; }
.v2-aq-fs {
  background: none; border: none; color: rgba(228,238,255,.5);
  font-size: 11px; cursor: pointer; padding: 2px 4px; border-radius: 3px;
}
.v2-aq-fs:hover { color: #60a5fa; background: rgba(96,165,250,.1); }

/* 자동 슬라이드 트랜지션 */
.v2-aq-slide-content { display: flex; flex-direction: column; gap: 10px; }
.v2-aq-slide-enter-active,
.v2-aq-slide-leave-active { transition: opacity .35s ease, transform .35s ease; }
.v2-aq-slide-enter-from { opacity: 0; transform: translateX(24px); }
.v2-aq-slide-leave-to   { opacity: 0; transform: translateX(-24px); }

/* 진행 표시 점 */
.v2-aq-progress {
  display: flex; gap: 5px; justify-content: center;
  padding-top: 6px; border-top: 1px solid rgba(255,255,255,.04);
}
.v2-aq-pgdot {
  width: 18px; height: 4px; border-radius: 2px;
  background: rgba(255,255,255,.12);
  border: none; padding: 0; cursor: pointer;
  transition: background .25s, width .25s, transform .15s;
}
.v2-aq-pgdot:hover { background: rgba(255,255,255,.25); transform: scaleY(1.3); }
.v2-aq-pgdot.active {
  background: #60a5fa; width: 28px;
  box-shadow: 0 0 6px rgba(96,165,250,.5);
}
.v2-aq-pgdot.active:hover { background: #3b82f6; }

/* 날씨 상세 모달 */
.v2-wd-box { width: min(960px, 92vw); max-width: 1100px; }
.v2-wd-body { padding: 20px; }
.v2-wd-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.v2-wd-card {
  background: #0b1726; border: 1px solid rgba(255,255,255,.06);
  border-radius: 8px; padding: 18px 16px;
  display: flex; flex-direction: column; align-items: center;
  cursor: pointer; transition: all .15s;
  position: relative;
}
.v2-wd-card:hover { border-color: rgba(96,165,250,.3); transform: translateY(-2px); }
.v2-wd-card.active {
  border-color: rgba(96,165,250,.5);
  box-shadow: 0 0 0 1px rgba(96,165,250,.25), 0 8px 24px rgba(96,165,250,.1);
}
.v2-wd-card.active::after {
  content: '현재'; position: absolute; top: 8px; right: 8px;
  font-size: 9px; font-weight: 700; padding: 2px 6px;
  background: #60a5fa; color: #fff; border-radius: 8px;
}
.v2-wd-name { font-size: 13px; font-weight: 600; color: rgba(228,238,255,.7); margin-bottom: 8px; }
.v2-wd-icon { font-size: 52px; filter: drop-shadow(0 0 14px currentColor); margin: 4px 0; }
.v2-wd-cond { font-size: 14px; font-weight: 700; color: #e4eeff; margin-top: 4px; }
.v2-wd-temp { font-size: 32px; font-weight: 800; color: #e4eeff; line-height: 1.1; margin: 6px 0 14px; }
.v2-wd-temp small { font-size: 16px; font-weight: 500; color: rgba(228,238,255,.55); margin-left: 2px; }
.v2-wd-rows { width: 100%; display: flex; flex-direction: column; gap: 8px; }
.v2-wd-row {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px;
}
.v2-wd-row span { color: rgba(228,238,255,.55); }
.v2-wd-row b { color: #e4eeff; font-weight: 600; }
.v2-wd-divider { height: 1px; background: rgba(255,255,255,.06); margin: 4px 0; }
.v2-wd-tip {
  margin-top: 14px; width: 100%;
  padding: 10px 12px;
  background: rgba(96,165,250,.08);
  border: 1px solid rgba(96,165,250,.15);
  border-radius: 6px;
  display: flex; align-items: center; gap: 8px;
  font-size: 11px; color: rgba(228,238,255,.85);
}
.v2-wd-tip i { color: #60a5fa; font-size: 14px; flex-shrink: 0; }

/* 내일 예보 카드 (모달 내부) */
.v2-wd-tomorrow {
  width: 100%; margin-top: 14px;
  background: linear-gradient(135deg, rgba(96,165,250,.06), rgba(167,139,250,.06));
  border: 1px solid rgba(96,165,250,.18);
  border-radius: 6px;
  overflow: hidden;
}
.v2-wd-tm-header {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,.06);
  font-size: 11px; font-weight: 600; color: rgba(228,238,255,.7);
}
.v2-wd-tm-header i { color: #fbbf24; font-size: 14px; }
.v2-wd-tm-body {
  display: grid; grid-template-columns: auto 1fr auto;
  gap: 10px; align-items: center; padding: 10px 12px;
}
.v2-wd-tm-icon { font-size: 32px; filter: drop-shadow(0 0 8px currentColor); }
.v2-wd-tm-cond { font-size: 13px; font-weight: 700; color: #e4eeff; }
.v2-wd-tm-temp {
  font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 700;
  margin-top: 3px;
}
.v2-wd-tm-temp .hi  { color: #e05260; }
.v2-wd-tm-temp .lo  { color: #60a5fa; }
.v2-wd-tm-temp .sep { color: rgba(228,238,255,.3); margin: 0 4px; }
.v2-wd-tm-rain {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  font-size: 11px; color: rgba(228,238,255,.7);
}
.v2-wd-tm-rain i { color: #60a5fa; font-size: 16px; }
.v2-wd-tm-rain span { font-weight: 700; color: #60a5fa; font-size: 13px; }
.v2-wd-tm-meta {
  display: grid; grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid rgba(255,255,255,.05);
}
.v2-wd-tm-meta > div {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  padding: 8px 4px;
  border-right: 1px solid rgba(255,255,255,.05);
  font-size: 11px;
}
.v2-wd-tm-meta > div:last-child { border-right: none; }
.v2-wd-tm-meta span { color: rgba(228,238,255,.5); font-size: 10px; }
.v2-wd-tm-meta b { color: #e4eeff; font-weight: 700; font-size: 13px; }

@media (max-width: 900px) {
  .v2-wd-grid { grid-template-columns: 1fr; }
}
.v2-panel-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.v2-panel-h span {
  display: flex;
  align-items: center;
  gap: 6px;
}
.v2-panel-h i {
  color: rgba(96, 165, 250, 0.8);
}
.v2-search {
  position: relative;
  padding: 10px 12px 8px;
}
.v2-search i {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-30%);
  color: rgba(228, 238, 255, 0.35);
  font-size: 11px;
}
.v2-search input {
  width: 100%;
  background: #0b1726;
  border: 1px solid rgba(255, 255, 255, 0.06);
  color: #e4eeff;
  padding: 6px 10px 6px 26px;
  border-radius: 4px;
  font-size: 12px;
  outline: none;
}
.v2-search input::placeholder {
  color: rgba(228, 238, 255, 0.3);
}
.v2-search input:focus {
  border-color: rgba(96, 165, 250, 0.35);
}

.v2-tree {
  padding: 4px 8px 8px;
  flex: 1;
  overflow-y: auto;
}
.v2-tree-root {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(228, 238, 255, 0.9);
}
.v2-tree-ico {
  color: rgba(96, 165, 250, 0.8);
  font-size: 12px;
}
.v2-cnt {
  margin-left: auto;
  font-size: 10px;
  padding: 1px 7px;
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
  border-radius: 10px;
  font-weight: 600;
}
.v2-tree-group {
  margin-top: 2px;
}
.v2-tree-gh {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 6px;
  font-size: 12px;
  color: rgba(228, 238, 255, 0.75);
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s;
}
.v2-tree-gh:hover {
  background: rgba(255, 255, 255, 0.03);
}
.v2-tree-gh > i:first-child {
  font-size: 9px;
  color: rgba(228, 238, 255, 0.4);
  width: 10px;
}
.v2-tree-folder {
  color: #d4845a;
  font-size: 11px;
}
.v2-tree-children {
  padding-left: 14px;
}
.v2-tree-leaf {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 6px 4px 14px;
  font-size: 12px;
  color: rgba(228, 238, 255, 0.65);
  border-radius: 4px;
  cursor: pointer;
}
.v2-tree-leaf:hover {
  background: rgba(255, 255, 255, 0.03);
  color: #e4eeff;
}
.v2-tree-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.v2-tree-dot.online {
  background: #4caf7d;
  box-shadow: 0 0 6px rgba(76, 175, 125, 0.6);
}
.v2-tree-dot.offline {
  background: #6b7280;
}
.v2-tree-dot.error {
  background: #d4845a;
}

/* ═════════ MAIN ═════════ */
.v2-main {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: #0b1726;
  min-width: 0;
}

/* KPI (compact, centered) */
.v2-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.v2-kpi {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 10px 12px;
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}
.v2-kpi-icon {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  display: grid;
  place-items: center;
  font-size: 16px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.06);
  color: rgba(228, 238, 255, 0.75);
}
.v2-kpi-body {
  flex: 0 1 auto;
  min-width: 0;
  text-align: center;
}
.v2-kpi-label {
  font-size: 10px;
  color: rgba(228, 238, 255, 0.55);
  margin-bottom: 2px;
}
.v2-kpi-value {
  display: flex;
  align-items: baseline;
  gap: 3px;
  justify-content: center;
}
.v2-kpi-num {
  font-size: 18px;
  font-weight: 700;
  color: #e4eeff;
  line-height: 1.1;
}
.v2-kpi-unit {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.55);
}
.v2-kpi-diff {
  font-size: 10px;
  color: rgba(228, 238, 255, 0.5);
  margin-top: 2px;
  display: flex;
  align-items: center;
  gap: 3px;
  justify-content: center;
}
.v2-kpi-diff i {
  color: #4caf7d;
  font-size: 9px;
}
.v2-kpi-diff.down i {
  color: #e05260;
}

/* CARD COMMON */
.v2-card {
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}
.v2-card-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
}
.v2-card-h > span:first-child {
  display: flex;
  align-items: center;
  gap: 6px;
}
.v2-card-h i {
  color: rgba(96, 165, 250, 0.85);
}

/* ROW 2 */
.v2-row-2 {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 14px;
  min-height: 560px;
}
.v2-col-right-r2 {
  display: grid;
  grid-template-rows: 1.4fr 1fr;
  gap: 14px;
  min-height: 0;
}
.v2-cam-grid-card {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.v2-cam-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 8px;
  flex: 1;
  min-height: 0;
}
.v2-cam-cell {
  position: relative;
  background: #000;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  min-height: 0;
}
.v2-cam-top {
  position: absolute;
  top: 6px;
  left: 6px;
  right: 6px;
  display: flex;
  align-items: center;
  gap: 5px;
  z-index: 2;
}
.v2-cam-live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #4caf7d;
  box-shadow: 0 0 6px #4caf7d;
  animation: pulse 1.6s ease-in-out infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}
.v2-cam-name {
  font-size: 11px;
  color: #fff;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.55);
  padding: 2px 7px;
  border-radius: 3px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}
.v2-cam-live-badge {
  margin-left: auto;
  font-size: 9px;
  font-weight: 800;
  color: #fff;
  background: #e05260;
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 0.5px;
}
.v2-cam-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.v2-cam-zoom {
  position: absolute;
  bottom: 6px;
  right: 6px;
  z-index: 2;
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: #fff;
  width: 22px;
  height: 22px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 10px;
}

.v2-cong-card {
  display: flex;
  flex-direction: column;
}
.v2-legend {
  display: flex;
  gap: 14px;
}
.v2-lg {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  font-weight: 500;
  color: rgba(228, 238, 255, 0.7);
}
.v2-lg .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}
.v2-chart {
  flex: 1;
  min-height: 0;
}

/* ROW 3 : OCR / HeatMap / Status (드래그 가능한 3분할) */
.v2-row3-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 14px;
  min-height: 320px;
  margin-bottom: 14px;
}
/* ROW 4 : OCR 로그 (풀폭) */
.v2-log-row { width: 100%; }
.v2-status-card {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* OCR */
.v2-ocr-card {
  display: flex;
  flex-direction: column;
}
.v2-ocr-body {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 14px;
  margin-bottom: 12px;
  flex: 1;
  min-height: 0;
}
.v2-ocr-photo {
  background: linear-gradient(135deg, #1a2b44, #0f1d30);
  border-radius: 6px;
  display: grid;
  place-items: center;
  position: relative;
  overflow: hidden;
  min-height: 130px;
}
.v2-ocr-photo::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(
      circle at 30% 70%,
      rgba(96, 165, 250, 0.15),
      transparent 50%
    ),
    radial-gradient(circle at 70% 30%, rgba(167, 139, 250, 0.1), transparent 50%);
}
.v2-plate-vis {
  background: #fff;
  padding: 10px 22px;
  border-radius: 4px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  position: relative;
  z-index: 1;
  border: 2px solid #d4d4d4;
}
.v2-plate-num {
  font-size: 22px;
  font-weight: 900;
  color: #1a1a1a;
  letter-spacing: 1.5px;
}
.v2-ocr-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}
.v2-ocr-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 6px;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.06);
  font-size: 12px;
}
.v2-ocr-row:last-child {
  border-bottom: none;
}
.v2-ocr-k {
  color: rgba(228, 238, 255, 0.55);
}
.v2-ocr-v {
  color: #e4eeff;
  font-weight: 600;
}
.v2-ocr-conf {
  color: #4caf7d;
}

.v2-ocr-thumbs {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  flex-shrink: 0;
}
.v2-ocr-thumb {
  background: #0b1726;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  padding: 6px;
  text-align: center;
}
.v2-ocr-thumb-time {
  font-size: 9px;
  color: rgba(228, 238, 255, 0.45);
  margin-bottom: 3px;
}
.v2-ocr-thumb-plate {
  font-size: 10px;
  font-weight: 700;
  color: #e4eeff;
  background: #fff;
  color: #1a1a1a;
  padding: 3px 4px;
  border-radius: 2px;
  letter-spacing: 0.5px;
}

/* HeatMap */
.v2-heat-card {
  display: flex;
  flex-direction: column;
}
.v2-heat-tools {
  display: flex;
  align-items: center;
  gap: 12px;
}
.v2-heat-fs {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(96, 165, 250, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(96, 165, 250, 0.25);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s;
}
.v2-heat-fs:hover {
  background: rgba(96, 165, 250, 0.22);
  border-color: rgba(96, 165, 250, 0.45);
}
.v2-heat-fs.active {
  background: rgba(96, 165, 250, 0.3);
  border-color: rgba(96, 165, 250, 0.55);
}

/* 혼잡 지점 드롭다운 (Leaflet 위에 표시되도록 z-index 충분히 높임) */
.v2-hotspot-wrap { position: relative; z-index: 1000; }
.v2-hotspot-menu {
  position: absolute; right: 0; top: 28px; width: 280px;
  background: #0f1d30; border: 1px solid rgba(255,255,255,.08);
  border-radius: 6px; box-shadow: 0 12px 36px rgba(0,0,0,.6);
  padding: 6px 0; z-index: 9999; max-height: 360px; overflow-y: auto;
}
/* Leaflet 컨테이너의 stacking context를 강제로 하향 조정 (드롭다운 보호) */
.v2-heat-card .v2-card-h { position: relative; z-index: 500; }
.v2-heat-map { z-index: 1; }
.v2-heat-map .leaflet-pane,
.v2-heat-map .leaflet-top,
.v2-heat-map .leaflet-bottom { z-index: 100; }
.v2-hotspot-header {
  padding: 8px 12px; font-size: 11px; font-weight: 600;
  color: rgba(228,238,255,.55);
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.v2-hotspot-header i { color: #e05260; margin-right: 4px; }
.v2-hotspot-item {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 8px 12px; background: none; border: none;
  color: rgba(228,238,255,.85); font-size: 12px; cursor: pointer;
  text-align: left; transition: background .15s;
}
.v2-hotspot-item:hover { background: rgba(96,165,250,.08); }
.v2-hotspot-dot {
  width: 8px; height: 8px; border-radius: 50%;
  box-shadow: 0 0 6px currentColor;
}
.v2-hotspot-name { flex: 1; }
.v2-hotspot-lv {
  font-size: 10px; padding: 1px 6px; border-radius: 8px; font-weight: 700;
}
.v2-hotspot-lv.critical { background: rgba(224,82,96,.18); color: #e05260; }
.v2-hotspot-lv.warning  { background: rgba(212,132,90,.18); color: #d4845a; }
.v2-hotspot-lv.ok       { background: rgba(76,175,125,.18); color: #4caf7d; }
.v2-hotspot-int { font-size: 11px; color: rgba(228,238,255,.6); min-width: 32px; text-align: right; }
.v2-heat-fs i {
  font-size: 11px;
}
/* CSS 기반 확대 — fullscreen API 대신 position:fixed 토글 */
.v2-heat-card.v2-heat-expanded {
  position: fixed !important;
  inset: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 99999 !important;
  border-radius: 0 !important;
  margin: 0 !important;
  padding: 16px 20px !important;
  border: none !important;
  box-shadow: 0 0 0 9999px rgba(0,0,0,.5);
}
.v2-heat-card.v2-heat-expanded .v2-heat-wrap {
  height: calc(100vh - 60px);
}

.v2-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(228, 238, 255, 0.6);
  cursor: pointer;
}
.v2-toggle input {
  accent-color: #60a5fa;
}
.v2-heat-wrap {
  flex: 1;
  min-height: 0;
  position: relative;
  border-radius: 4px;
  overflow: hidden;
  background: #0a1929;
}
.v2-heat-map {
  position: absolute;
  inset: 0;
}
.v2-heat-fb {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
}
.v2-heat-legend {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 5;
  pointer-events: none;
}
.v2-heat-bar {
  width: 8px;
  height: 120px;
  border-radius: 4px;
  background: linear-gradient(to bottom, #e05260, #d4845a, #4caf7d);
}
.v2-heat-legend-label {
  font-size: 9px;
  color: rgba(228, 238, 255, 0.65);
  writing-mode: horizontal-tb;
  background: rgba(15, 29, 48, 0.85);
  padding: 2px 4px;
  border-radius: 2px;
}
.v2-heat-legend-label.top {
  margin-bottom: 4px;
}
.v2-heat-legend-label.bot {
  margin-top: 4px;
}

/* 차량 통행 분석 (진입/이탈) */
.v2-flow-card {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
}
.v2-flow-net {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.6);
}
.v2-flow-net b {
  color: #60a5fa;
  font-size: 13px;
  font-weight: 700;
}
.v2-flow-body {
  display: grid;
  grid-template-columns: 1fr 1fr 1.6fr;
  gap: 10px;
  flex: 1;
  min-height: 0;
}
.v2-flow-cell {
  background: #0b1726;
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 6px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  position: relative;
}
.v2-flow-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 11px;
  color: rgba(228, 238, 255, 0.6);
  font-weight: 500;
}
.v2-flow-in .v2-flow-label i {
  color: #4caf7d;
  font-size: 13px;
}
.v2-flow-out .v2-flow-label i {
  color: #d4845a;
  font-size: 13px;
}
.v2-flow-value {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 6px;
  padding-bottom: 4px;
}
.v2-flow-num {
  font-size: 30px;
  font-weight: 800;
  color: #e4eeff;
  line-height: 1;
}
.v2-flow-unit {
  font-size: 14px;
  color: rgba(228, 238, 255, 0.7);
  font-weight: 600;
  margin-bottom: 4px;
}
.v2-flow-in .v2-flow-num {
  color: #4caf7d;
}
.v2-flow-out .v2-flow-num {
  color: #d4845a;
}
.v2-flow-chart-wrap {
  background: #0b1726;
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 6px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
}
.v2-flow-spark-label {
  font-size: 10px;
  color: rgba(228, 238, 255, 0.5);
}
.v2-spark {
  flex: 1;
  min-height: 40px;
}
.v2-dup-bar {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(76, 175, 125, 0.07);
  border: 1px solid rgba(76, 175, 125, 0.15);
  border-radius: 6px;
  font-size: 11px;
  color: rgba(228, 238, 255, 0.7);
}
.v2-dup-bar i {
  color: #4caf7d;
  font-size: 13px;
}
.v2-dup-val b {
  color: #4caf7d;
  font-weight: 700;
}
.v2-dup-val {
  margin-left: auto;
}

/* 카메라 상태 */
.v2-status-card {
  display: flex;
  flex-direction: column;
}
.v2-status-total {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.5);
}
.v2-status-body {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 14px;
  margin-bottom: 12px;
}
.v2-donut-wrap {
  position: relative;
  width: 110px;
  height: 110px;
  flex-shrink: 0;
}
.v2-donut {
  width: 110px;
  height: 110px;
}
.v2-donut-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}
.v2-donut-num {
  font-size: 22px;
  font-weight: 700;
  color: #e4eeff;
  line-height: 1;
}
.v2-donut-lbl {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.55);
  margin-top: 4px;
}
.v2-status-legend {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
}
.v2-sl-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.v2-sl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.v2-sl-name {
  color: rgba(228, 238, 255, 0.7);
}
.v2-sl-val {
  margin-left: auto;
  color: #e4eeff;
  font-weight: 600;
}

.v2-status-table {
  font-size: 11px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}
.v2-st-head,
.v2-st-row {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 1.4fr;
  gap: 6px;
  padding: 6px 4px;
  align-items: center;
}
.v2-st-head {
  color: rgba(228, 238, 255, 0.4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  font-weight: 600;
}
.v2-st-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}
.v2-st-name {
  color: rgba(228, 238, 255, 0.85);
}
.v2-st-status.online {
  color: #4caf7d;
}
.v2-st-status.offline {
  color: #e05260;
}
.v2-st-status.error {
  color: #d4845a;
}
.v2-st-time {
  color: rgba(228, 238, 255, 0.5);
  font-size: 10px;
}

/* OCR 로그 */
.v2-log-card {
  flex-shrink: 0;
}
.v2-log-more {
  background: none;
  border: none;
  color: rgba(96, 165, 250, 0.85);
  font-size: 12px;
  cursor: pointer;
}
.v2-log-more:hover {
  color: #60a5fa;
}
.v2-log-table {
  font-size: 12px;
}
.v2-lt-head,
.v2-lt-row {
  display: grid;
  grid-template-columns: 0.4fr 1.6fr 1.4fr 1.2fr 0.9fr 0.8fr;
  gap: 8px;
  padding: 8px 4px;
  align-items: center;
}
.v2-lt-dir {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  font-size: 11px;
}
.v2-lt-dir.in {
  color: #4caf7d;
}
.v2-lt-dir.out {
  color: #d4845a;
}
.v2-lt-dir i {
  font-size: 13px;
}
.v2-ocr-dir-in {
  color: #4caf7d !important;
}
.v2-ocr-dir-out {
  color: #d4845a !important;
}
.v2-ocr-v i {
  font-size: 13px;
  margin-right: 2px;
}
.v2-lt-head {
  color: rgba(228, 238, 255, 0.4);
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-lt-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: rgba(228, 238, 255, 0.85);
}
.v2-lt-row:hover {
  background: rgba(255, 255, 255, 0.02);
}
.v2-lt-conf {
  color: #4caf7d;
  font-weight: 600;
}

/* ═════════ TAB PAGES (이벤트/검색/통계/설정) ═════════ */
.v2-tab-page {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.v2-page-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 2px 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-page-h h2 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #e4eeff;
}
.v2-page-h h2 i {
  color: #60a5fa;
}
.v2-page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.v2-select,
.v2-search-form select,
.v2-search-form input,
.v2-settings-list input[type="number"] {
  background: #0b1726;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #e4eeff;
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 12px;
  outline: none;
  min-width: 140px;
}
.v2-select:focus,
.v2-search-form input:focus,
.v2-search-form select:focus,
.v2-settings-list input[type="number"]:focus {
  border-color: rgba(96, 165, 250, 0.5);
}

.v2-btn-primary,
.v2-btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.v2-btn-primary {
  background: #60a5fa;
  color: #fff;
}
.v2-btn-primary:hover {
  background: #3b82f6;
}
.v2-btn-secondary {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(228, 238, 255, 0.85);
}
.v2-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}
.v2-empty {
  padding: 30px;
  text-align: center;
  color: rgba(228, 238, 255, 0.4);
  font-size: 12px;
}

/* 이벤트 탭 */
.v2-events-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.v2-evs-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}
.v2-evs-card i {
  font-size: 26px;
}
.v2-evs-card::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
}
.v2-evs-critical i {
  color: #e05260;
}
.v2-evs-critical::before {
  background: #e05260;
}
.v2-evs-warning i {
  color: #d4845a;
}
.v2-evs-warning::before {
  background: #d4845a;
}
.v2-evs-info i {
  color: #60a5fa;
}
.v2-evs-info::before {
  background: #60a5fa;
}
.v2-evs-total i {
  color: #a78bfa;
}
.v2-evs-total::before {
  background: #a78bfa;
}
.v2-evs-n {
  font-size: 22px;
  font-weight: 700;
  color: #e4eeff;
  line-height: 1.1;
}
.v2-evs-l {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.55);
  margin-top: 2px;
}

.v2-event-table {
  font-size: 12px;
}
.v2-et-head,
.v2-et-row {
  display: grid;
  grid-template-columns: 1.5fr 0.7fr 1.2fr 2.4fr 0.6fr;
  gap: 8px;
  padding: 9px 6px;
  align-items: center;
}
.v2-et-head {
  color: rgba(228, 238, 255, 0.4);
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-et-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  color: rgba(228, 238, 255, 0.85);
}
.v2-et-row:hover {
  background: rgba(255, 255, 255, 0.02);
}
.v2-et-level {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  text-align: center;
  max-width: 60px;
}
.v2-et-level.critical {
  background: rgba(224, 82, 96, 0.15);
  color: #e05260;
}
.v2-et-level.warning {
  background: rgba(212, 132, 90, 0.15);
  color: #d4845a;
}
.v2-et-level.info {
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
}
.v2-et-btn {
  padding: 4px 10px;
  background: rgba(96, 165, 250, 0.12);
  color: #60a5fa;
  border: 1px solid rgba(96, 165, 250, 0.25);
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
}
.v2-et-btn:hover {
  background: rgba(96, 165, 250, 0.2);
}

/* 검색 탭 */
.v2-search-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.v2-form-row {
  display: grid;
  grid-template-columns: 100px 1fr auto 1fr;
  gap: 10px;
  align-items: center;
}
.v2-form-row label {
  font-size: 12px;
  color: rgba(228, 238, 255, 0.6);
}
.v2-form-row input,
.v2-form-row select {
  width: 100%;
  min-width: 0;
}
.v2-form-row > span {
  color: rgba(228, 238, 255, 0.5);
  font-size: 12px;
}
.v2-form-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 6px;
}

/* 통계 탭 */
.v2-stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.v2-stat-chart {
  height: 260px;
}

/* 설정 탭 */
.v2-settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.v2-settings-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.v2-setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 4px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.v2-setting-row:last-child {
  border-bottom: none;
}
.v2-setting-stack {
  flex-direction: column;
  align-items: stretch;
  gap: 6px;
}
.v2-set-name {
  font-size: 13px;
  color: rgba(228, 238, 255, 0.9);
  font-weight: 500;
}
.v2-set-desc {
  font-size: 11px;
  color: rgba(228, 238, 255, 0.45);
  margin-top: 2px;
}
.v2-setting-info {
  font-size: 12px;
  color: rgba(228, 238, 255, 0.7);
}
.v2-set-status.ok {
  color: #4caf7d;
  font-weight: 600;
  font-size: 11px;
}
.v2-switch {
  position: relative;
  display: inline-block;
  width: 38px;
  height: 20px;
  flex-shrink: 0;
}
.v2-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}
.v2-switch span {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  transition: 0.2s;
}
.v2-switch span::before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  left: 3px;
  top: 3px;
  background: #fff;
  border-radius: 50%;
  transition: 0.2s;
}
.v2-switch input:checked + span {
  background: #60a5fa;
}
.v2-switch input:checked + span::before {
  transform: translateX(18px);
}

/* FOOT */
.v2-foot {
  font-size: 10px;
  color: rgba(228, 238, 255, 0.3);
  padding: 4px 4px 12px;
  letter-spacing: 0.5px;
}

/* MODAL */
.v2-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: grid;
  place-items: center;
  z-index: 1000;
}
.v2-modal-box {
  width: 80vw;
  max-width: 960px;
  background: #0f1d30;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}
.v2-modal-h {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.v2-modal-h span {
  display: flex;
  align-items: center;
  gap: 8px;
}
.v2-modal-h button {
  background: none;
  border: none;
  color: rgba(228, 238, 255, 0.6);
  font-size: 16px;
  cursor: pointer;
}
.v2-modal-box video {
  width: 100%;
  display: block;
  background: #000;
}

/* Scrollbars */
.v2-side::-webkit-scrollbar,
.v2-tree::-webkit-scrollbar,
.v2-status-table::-webkit-scrollbar,
.v2-main::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.v2-side::-webkit-scrollbar-thumb,
.v2-tree::-webkit-scrollbar-thumb,
.v2-status-table::-webkit-scrollbar-thumb,
.v2-main::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
}
.v2-side::-webkit-scrollbar-thumb:hover,
.v2-tree::-webkit-scrollbar-thumb:hover,
.v2-main::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.16);
}

/* Responsive */
@media (max-width: 1400px) {
  .v2-row3-grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 1100px) {
  .v2-kpi-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .v2-row-2 {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  .v2-col-right-r2 {
    grid-template-rows: auto auto;
  }
  .v2-row3-grid {
    grid-template-columns: 1fr;
  }
}
</style>
