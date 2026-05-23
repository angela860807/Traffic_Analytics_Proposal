<template>
  <div class="an-shell" :class="{ 'side-collapsed': !sideOpen }">
    <div class="body">
      <aside class="filter">
        <div class="side-top">
          <RouterLink to="/" class="brand" v-if="sideOpen">
            <img src="/TAS.png" alt="TAS" class="brand-img" />
          </RouterLink>
          <button class="side-toggle" @click="sideOpen = !sideOpen"
            :aria-label="sideOpen ? '사이드바 접기' : '사이드바 펼치기'"
            :title="sideOpen ? '사이드바 접기' : '사이드바 펼치기'">
            <i :class="sideOpen ? 'bi bi-arrow-left-short' : 'bi bi-arrow-right-short'"></i>
          </button>
        </div>
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
            <div class="t-user"><i class="bi bi-person-circle"></i> 교통분석팀 매니저 <i class="bi bi-chevron-down"></i></div>
          </div>
        </header>

        <GuideOverlay
          v-model="guideOpen"
          :steps="guideSteps"
          :on-step-enter="onGuideStep"
        />

        <section class="ctx-bar" v-if="anaTab === 'ctx' || anaTab === 'dashboard'">
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
            <button class="ctx-act bl" @click="actStats" title="통계 인사이트로 이동"><i class="bi bi-bar-chart"></i> 통계</button>
            <button class="ctx-act bl" @click="actCompare" title="구간 성능 비교로 이동"><i class="bi bi-calendar3"></i> 비교</button>
            <button class="ctx-act gr" @click="actReport" title="일일 교통흐름 리포트 다운로드"><i class="bi bi-file-earmark-text"></i> 리포트</button>
            <button class="ctx-act pl" @click="actCsv" title="주간 구간 성능 CSV 다운로드"><i class="bi bi-download"></i> CSV</button>
          </div>
        </section>
        <div v-if="opMsg && (anaTab === 'ctx' || anaTab === 'dashboard')" class="ctx-msg">{{ opMsg }}</div>

        <section class="insight-strip" v-if="anaTab === 'insight' || anaTab === 'dashboard'">
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
        </section>

        <section class="row-cmp" v-if="anaTab === 'cmp' || anaTab === 'dashboard'">
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


        <!-- ctx 단독 탭: 현재 설정 요약 + 저장된 분석 -->
        <section class="ctx-extra" v-if="anaTab === 'ctx'">
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-list-check"></i> 현재 분석 설정 요약</h3>
              <span class="seg-sub">선택한 조건이 모든 분석에 적용됩니다.</span>
            </div>
            <div class="cs-grid">
              <div class="cs-cell"><span>도로</span><strong>{{ activeRoadLabel }}</strong></div>
              <div class="cs-cell"><span>비교 기준</span><strong>{{ compareBase === 'prev' ? '전일' : compareBase === 'prevWeek' ? '전주 동일 요일' : '최근 7일 평균' }}</strong></div>
              <div class="cs-cell"><span>기간</span><strong>{{ periods.find(p => p.id === period)?.label }}</strong></div>
              <div class="cs-cell"><span>기간 범위</span><strong class="mono">{{ dateRange }}</strong></div>
              <div class="cs-cell"><span>시간대</span><strong>{{ timeSlot === 'all' ? '전체' : timeSlot === 'am' ? '오전' : timeSlot === 'pm' ? '오후' : timeSlot === 'rush' ? '출퇴근' : '야간' }}</strong></div>
              <div class="cs-cell"><span>자동 새로고침</span><strong :class="autoRefresh ? 'up' : 'dn'">{{ autoRefresh ? 'ON' : 'OFF' }}</strong></div>
            </div>
          </div>
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-bookmark-star"></i> 저장된 분석 프리셋</h3>
              <button class="tp-add"><i class="bi bi-plus-lg"></i> 분석 생성</button>
            </div>
            <table class="tbl-kpi">
              <thead><tr><th>분석명</th><th>유형</th><th>기간</th><th>생성자</th><th>생성</th></tr></thead>
              <tbody>
                <tr v-for="s in savedAnalyses" :key="s.id">
                  <td><strong>{{ s.name }}</strong></td>
                  <td>{{ s.type }}</td>
                  <td class="mono">{{ s.range }}</td>
                  <td>{{ s.by }}</td>
                  <td class="mono">{{ s.created }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- insight 단독 탭: 상세 인사이트 카드 -->
        <section class="ins-extra" v-if="anaTab === 'insight'">
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-clipboard-data"></i> 인사이트 상세 (AI 분석)</h3>
              <span class="seg-sub">최근 24시간 · {{ insightDetails.length }}건</span>
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
          </div>
        </section>

        <!-- cmp 단독 탭: 시간대별 비교 표 -->
        <section class="cmp-extra" v-if="anaTab === 'cmp'">
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-clock-history"></i> 시간대별 성능 비교</h3>
              <span class="seg-sub">24시간 · 전일 대비 변동</span>
            </div>
            <table class="tbl-kpi">
              <thead><tr><th>시간대</th><th>평균 속도</th><th>전일 대비</th><th>혼잡 구간</th><th>통행량</th><th>특징</th></tr></thead>
              <tbody>
                <tr v-for="t in timeSlots" :key="t.slot">
                  <td><strong>{{ t.slot }}</strong></td>
                  <td class="mono">{{ t.speed }} km/h</td>
                  <td><span :class="t.dTone" class="mono">{{ t.delta }}</span></td>
                  <td><span class="cg-tag" :class="t.tone">{{ t.level }}</span> {{ t.cong }}</td>
                  <td class="mono">{{ t.vol.toLocaleString() }}대/h</td>
                  <td>{{ t.note }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-bezier2"></i> 구간별 상세 지표</h3>
              <span class="seg-sub">{{ segKpis.length }}개 구간 · {{ activeRoadLabel }}</span>
            </div>
            <table class="tbl-kpi">
              <thead><tr><th>구간</th><th>평균 속도</th><th>전일 대비</th><th>피크 시간</th><th>통행량</th><th>혼잡도</th></tr></thead>
              <tbody>
                <tr v-for="r in segKpis" :key="r.name">
                  <td><strong>{{ r.name }}</strong></td>
                  <td class="mono">{{ r.speed }} km/h</td>
                  <td><span :class="r.dTone" class="mono">{{ r.delta }}</span></td>
                  <td class="mono">{{ r.peak }}</td>
                  <td class="mono">{{ (r.speed * 80).toLocaleString() }}대/h</td>
                  <td><span class="cg-tag" :class="r.cgTone">{{ r.cg }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="row-mid" v-if="anaTab === 'map' || anaTab === 'dashboard'">
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

        <!-- 설정 탭 -->
        <section class="settings-panel" v-if="anaTab === 'settings'">
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-gear"></i> 분석 환경 설정</h3>
              <span class="seg-sub">자주 사용하는 분석 옵션을 미리 지정합니다.</span>
            </div>
            <div class="st-grid">
              <div class="st-blk">
                <h4>분석 기본값</h4>
                <div class="st-row"><label>기본 도로</label>
                  <select v-model="setDefaultRoad">
                    <option value="gangbyeon">강변북로 (구리 → 한남)</option>
                    <option value="olympic">올림픽대로 (가양 → 여의도)</option>
                    <option value="naebu">내부순환로 (월계 → 성수)</option>
                  </select>
                </div>
                <div class="st-row"><label>기본 비교 기준</label>
                  <select v-model="compareBase">
                    <option value="prev">전일</option>
                    <option value="prevWeek">전주 동일 요일</option>
                    <option value="avg7">최근 7일 평균</option>
                  </select>
                </div>
                <div class="st-row"><label>기본 시간대</label>
                  <select v-model="timeSlot">
                    <option value="all">전체</option>
                    <option value="am">오전</option>
                    <option value="pm">오후</option>
                    <option value="rush">출퇴근</option>
                    <option value="night">야간</option>
                  </select>
                </div>
              </div>
              <div class="st-blk">
                <h4>자동 갱신 · 알림</h4>
                <div class="st-row"><label>자동 새로고침</label><input type="checkbox" v-model="autoRefresh" /></div>
                <div class="st-row"><label>갱신 주기 (초)</label><input type="number" v-model.number="setRefreshSec" min="10" max="600" /></div>
                <div class="st-row"><label>알림 사운드</label><input type="checkbox" v-model="setSound" /></div>
                <div class="st-row"><label>주말 알림 제외</label><input type="checkbox" /></div>
              </div>
              <div class="st-blk">
                <h4>알람 임계값</h4>
                <div class="st-row"><label>혼잡 경보 (≤ km/h)</label><input type="number" value="30" /></div>
                <div class="st-row"><label>주의 경보 (≤ km/h)</label><input type="number" value="40" /></div>
                <div class="st-row"><label>이벤트 알림</label><input type="checkbox" checked /></div>
                <div class="st-row"><label>리포트 자동 발행</label><input type="checkbox" /></div>
              </div>
              <div class="st-blk">
                <h4>데이터 · 보관</h4>
                <div class="st-row"><label>원본 로그 보관</label>
                  <select><option>30일</option><option>60일</option><option>90일</option></select>
                </div>
                <div class="st-row"><label>집계 보관</label>
                  <select><option>1년</option><option>2년</option><option>영구</option></select>
                </div>
                <div class="st-row"><label>익명화 처리</label><input type="checkbox" checked /></div>
              </div>
            </div>
            <div class="st-foot">
              <button class="st-save" @click="saveSettings"><i class="bi bi-check2"></i> 저장</button>
              <span v-if="setMsg" class="st-msg">{{ setMsg }}</span>
            </div>
          </div>
        </section>

        <!-- map 단독 탭: 교차로 분석 + 사고/이벤트 -->
        <section class="map-extra" v-if="anaTab === 'map'">
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-diagram-3"></i> 교차로 분석</h3>
              <span class="seg-sub">{{ crossroads.length }}개 주요 교차로 · 신호 효율 평균 71%</span>
            </div>
            <div class="cross-grid">
              <div class="cross-card" v-for="x in crossroads" :key="x.name">
                <div class="cross-name">
                  <i class="bi bi-stoplights" :style="{ color: x.tone === 'rd' ? '#dc2626' : x.tone === 'or' ? '#b45309' : '#059669' }"></i>
                  {{ x.name }}
                </div>
                <div class="cross-row"><span>평균 대기</span><strong class="mono">{{ x.wait }}초</strong></div>
                <div class="cross-row"><span>혼잡도</span><span class="cg-tag" :class="x.tone">{{ x.level }}</span></div>
                <div class="cross-row"><span>통행량</span><strong class="mono">{{ x.vol.toLocaleString() }}대/h</strong></div>
                <div class="cross-row"><span>신호 효율</span><strong class="mono" :class="x.effTone">{{ x.eff }}%</strong></div>
                <div class="cross-row"><span>좌회전 비율</span><strong class="mono">{{ x.leftPct }}%</strong></div>
                <div class="cross-row"><span>보행 통과</span><strong class="mono">{{ x.pedPass }}건/h</strong></div>
              </div>
            </div>
          </div>
          <div class="card">
            <div class="kpi-head">
              <h3><i class="bi bi-exclamation-triangle"></i> 사고 · 이벤트 로그</h3>
              <span class="seg-sub">최근 24시간 · 진행 1건 · 복구 2건</span>
            </div>
            <table class="tbl-kpi">
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
import GuideOverlay from "@/components/GuideOverlay.vue";
import guideSteps from "@/data/guides/analytics.js";

const guideOpen = ref(false);
async function onGuideStep(step) {
  if (step?.tab && step.tab !== anaTab.value) {
    anaTab.value = step.tab;
  }
}

const roads = [
  { id: "gangbyeon", label: "강변복로 (구리 → 한남)",     subs: ["구리IC", "토평IC", "강일IC", "미사IC", "암사IC", "천호대교", "한남IC"] },
  { id: "olympic",   label: "올림픽대로 (가양 → 여의도)", subs: ["가양IC", "성산IC", "양화대교", "여의도"] },
  { id: "naebu",     label: "내부순환로 (월계 → 성수)",   subs: ["월계IC", "정릉", "홍지문", "성수JC"] },
];

const activeRoad = ref("gangbyeon");
const period = ref("7d");
const timeSlot = ref("all");

const periods = [
  { id: "today", label: "오늘" },
  { id: "yest",  label: "어제" },
  { id: "7d",    label: "최근 7일" },
  { id: "30d",   label: "최근 30일" },
];

const activeRoadObj = computed(() => roads.find(r => r.id === activeRoad.value) || roads[0]);
const activeRoadLabel = computed(() => activeRoadObj.value.label);

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

const aiInsights = [
  { icon: "bi bi-exclamation-circle-fill", color: "#dc2626", title: "피크시간 악화 구간 증가", detail: "출근 시간대 혼잡 악화 구간이 전일 대비 1개 증가했습니다." },
  { icon: "bi bi-exclamation-triangle-fill", color: "#b45309", title: "특정 구간 속도 저하", detail: "일산IC → 원효대교 구간 속도가 전일 대비 12% 감소했습니다." },
  { icon: "bi bi-check-circle-fill", color: "#059669", title: "전반적 흐름 개선", detail: "전체 평균 속도는 전일 대비 6% 개선되었습니다." },
  { icon: "bi bi-info-circle-fill", color: "#2563eb", title: "사고 영향 감소", detail: "사고 다발 구간의 영향이 전일 대비 18% 감소했습니다." },
];

const analysisMenu = [
  { id: "dashboard", icon: "bi bi-grid-1x2",        label: "대시보드" },
  { id: "ctx",       icon: "bi bi-sliders",         label: "분석 기준" },
  { id: "insight",   icon: "bi bi-clipboard-data",  label: "분석 인사이트" },
  { id: "cmp",       icon: "bi bi-bar-chart-line",  label: "구간 성능 비교" },
  { id: "map",       icon: "bi bi-geo-alt",         label: "혼잡 지도 · 지표" },
  { id: "settings",  icon: "bi bi-gear",            label: "설정" },
];

/* ── 헤더 실시간 알림 ── */
const showAlerts = ref(false);
const liveAlerts = ref([
  { id: 1, sev: "critical", icon: "bi bi-exclamation-octagon-fill", title: "피크시간 악화 구간 증가",  detail: "출근 시간대 혼잡 악화 구간이 전일 대비 1개 증가", place: "강변북로 일산IC", time: "08:42" },
  { id: 2, sev: "serious",  icon: "bi bi-graph-down",               title: "특정 구간 속도 저하",      detail: "일산IC → 원효대교 구간 속도 전일 대비 -12%",      place: "강변북로",         time: "08:35" },
  { id: 3, sev: "info",     icon: "bi bi-check-circle-fill",        title: "전반적 흐름 개선",         detail: "전체 평균 속도 전일 대비 +6%",                    place: "전 구간",           time: "08:10" },
  { id: 4, sev: "caution",  icon: "bi bi-file-earmark-text",        title: "보고서 발행 예약",         detail: "주간 구간 성능 분석 리포트 09:00 발행 예정",      place: "교통분석팀",        time: "07:55" },
]);
const hasCritical = computed(() => liveAlerts.value.some(a => a.sev === "critical"));

/* ── 설정 ── */
const setSound = ref(true);
const setRefreshSec = ref(30);
const setDefaultRoad = ref("gangbyeon");
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
const sideOpen = ref(true);
function goHome() {
  anaTab.value = "dashboard";
  window.scrollTo({ top: 0, behavior: "smooth" });
}
const compareBase = ref("prev");
const opMsg = ref("");
const dataUpdated = ref("2025-05-15  08:00");

/* ── ctx-bar 액션 버튼 ── */
let opMsgTimer = null;
function flashMsg(msg) {
  opMsg.value = msg;
  if (opMsgTimer) clearTimeout(opMsgTimer);
  opMsgTimer = setTimeout(() => { opMsg.value = ""; }, 2500);
}
function actStats() {
  anaTab.value = "insight";
  flashMsg(`📊 통계 인사이트로 이동 — ${aiInsights.length}건 분석 완료 (${dateRange.value})`);
}
function actCompare() {
  anaTab.value = "cmp";
  flashMsg(`🔀 ${activeRoadLabel.value} 기간 비교 — 기준: ${compareBase.value === 'prev' ? '전일' : compareBase.value === 'prevWeek' ? '전주 동일 요일' : '최근 7일 평균'}`);
}
function actReport() {
  const reportKey = (period.value === '7d' || period.value === '30d') ? 'weekly' : 'daily';
  downloadDeptReport('analytics', reportKey, { date: dateRange.value.split(' ~ ')[0] });
  flashMsg(`📄 ${reportKey === 'weekly' ? '주간' : '일일'} 리포트 다운로드 시작`);
}
function actCsv() {
  downloadDeptReport('analytics', 'weekly', { date: dateRange.value.split(' ~ ')[0] });
  flashMsg(`💾 CSV 내보내기 — 주간 구간 성능 분석`);
}

const segKpis = [
  { name: "강변IC",   speed: 61, delta: "▲ 4",  dTone: "up",   peak: "09시", cg: "원활", cgTone: "gr" },
  { name: "일산IC",   speed: 23, delta: "▼ 9",  dTone: "dn",   peak: "08시", cg: "혼잡", cgTone: "rd" },
  { name: "원효대교", speed: 27, delta: "▼ 11", dTone: "dn",   peak: "18시", cg: "혼잡", cgTone: "rd" },
];

const savedAnalyses = [
  { id: 1, name: "일산IC 혼잡 원인 분석",       type: "구간 분석",  range: "2025-05-09 ~ 2025-05-15", created: "2025-05-15 07:45", by: "김분석" },
  { id: 2, name: "출근시간 속도 저하 구간 분석", type: "시간대 분석", range: "2025-05-09 ~ 2025-05-15", created: "2025-05-14 18:30", by: "김분석" },
];

// === Leaflet 혼잡도 지도 ===
const jamMapEl = ref(null);
let jamMap = null;

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

<style scoped src="./AnalyticsView.css"></style>
