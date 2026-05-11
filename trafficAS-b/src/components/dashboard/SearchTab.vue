<template>
  <div class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-search"></i> 차량 검색</h2>
    </div>

    <section class="v2-card">
      <div class="v2-card-h">
        <span><i class="bi bi-funnel-fill"></i> 검색 조건</span>
      </div>
      <div class="v2-search-form">
        <div class="v2-form-row">
          <label>차량 번호</label>
          <input type="text" v-model="searchQuery.plate" placeholder="예: 128가 4567" />
        </div>
        <div class="v2-form-row">
          <label>카메라</label>
          <select v-model="searchQuery.cam">
            <option value="">전체</option>
            <option v-for="c in cameraFeeds" :key="c.name" :value="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div class="v2-form-row">
          <label>흐름 방향</label>
          <select v-model="searchQuery.dir">
            <option value="">전체</option>
            <option value="in">진입 (IN)</option>
            <option value="out">이탈 (OUT)</option>
          </select>
        </div>
        <div class="v2-form-row">
          <label>최소 신뢰도</label>
          <input type="number" v-model.number="searchQuery.minConf" min="0" max="100" placeholder="0~100" />
        </div>
        <div class="v2-form-actions">
          <button class="v2-btn-primary" @click="runSearch"><i class="bi bi-search"></i> 검색</button>
          <button class="v2-btn-secondary" @click="resetSearch">초기화</button>
        </div>
      </div>
    </section>

    <section class="v2-card">
      <div class="v2-card-h">
        <span><i class="bi bi-card-list"></i> 검색 결과 ({{ searchResults.length }}건)</span>
      </div>
      <div class="v2-log-table">
        <div class="v2-lt-head">
          <span>번호</span><span>인식 시간</span><span>카메라</span>
          <span>차량 번호</span><span>흐름 방향</span><span>신뢰도</span>
        </div>
        <div v-for="(p, i) in searchResults" :key="p.id" class="v2-lt-row">
          <span>{{ i + 1 }}</span>
          <span class="mono">{{ todayStr }} {{ p.time }}</span>
          <span>{{ p.cam }}</span>
          <span class="mono">{{ p.num }}</span>
          <span class="v2-lt-dir" :class="p.dir">
            <i :class="p.dir === 'in' ? 'bi bi-arrow-down-left-circle-fill' : 'bi bi-arrow-up-right-circle-fill'"></i>
            {{ dirLabel(p.dir) }}
          </span>
          <span class="v2-lt-conf">{{ p.conf }}%</span>
        </div>
        <div v-if="searchResults.length === 0" class="v2-empty">검색 결과가 없습니다. 검색 버튼을 눌러주세요.</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useDashboardData } from '@/composables/useDashboardData'

const { plates, cameraFeeds, todayStr, dirLabel } = useDashboardData()

const searchQuery = reactive({ plate: '', cam: '', dir: '', minConf: null })
const searchResults = ref([])

function runSearch() {
  const q = searchQuery
  searchResults.value = plates.value.filter(p =>
    (!q.plate   || p.num.includes(q.plate.trim())) &&
    (!q.cam     || p.cam === q.cam) &&
    (!q.dir     || p.dir === q.dir) &&
    (q.minConf == null || q.minConf === '' || p.conf >= q.minConf)
  )
}
function resetSearch() {
  Object.assign(searchQuery, { plate: '', cam: '', dir: '', minConf: null })
  searchResults.value = []
}
</script>
