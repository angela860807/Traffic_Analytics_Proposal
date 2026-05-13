<template>
  <div class="v2-tab-page">
    <div class="v2-page-h">
      <h2><i class="bi bi-gear-fill"></i> 시스템 설정</h2>
    </div>
    <div class="v2-settings-grid">
      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-bell-fill"></i> 알림 설정</span></div>
        <div class="v2-settings-list">
          <div class="v2-setting-row">
            <div><div class="v2-set-name">중요 이벤트 푸시 알림</div><div class="v2-set-desc">사고/정체 등 중요 이벤트 발생 시 알림</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.notifyCritical" /><span></span></label>
          </div>
          <div class="v2-setting-row">
            <div><div class="v2-set-name">경고 알림</div><div class="v2-set-desc">혼잡, 인식률 저하 등 경고성 이벤트</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.notifyWarning" /><span></span></label>
          </div>
          <div class="v2-setting-row">
            <div><div class="v2-set-name">정보성 알림</div><div class="v2-set-desc">시스템 상태, 정기 보고서</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.notifyInfo" /><span></span></label>
          </div>
          <div class="v2-setting-row">
            <div><div class="v2-set-name">이메일 알림</div><div class="v2-set-desc">중요 이벤트를 이메일로 전송</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.notifyEmail" /><span></span></label>
          </div>
        </div>
      </section>

      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-sliders"></i> 임계값 설정</span></div>
        <div class="v2-settings-list">
          <div class="v2-setting-row v2-setting-stack">
            <div class="v2-set-name">혼잡도 경고 임계값 (%)</div>
            <input type="number" v-model.number="settings.congestionThreshold" min="0" max="100" />
          </div>
          <div class="v2-setting-row v2-setting-stack">
            <div class="v2-set-name">OCR 신뢰도 최소값 (%)</div>
            <input type="number" v-model.number="settings.ocrConfidence" min="0" max="100" />
          </div>
          <div class="v2-setting-row v2-setting-stack">
            <div class="v2-set-name">데이터 갱신 주기 (초)</div>
            <input type="number" v-model.number="settings.refreshInterval" min="1" max="60" />
          </div>
        </div>
      </section>

      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-shield-fill-check"></i> 중복 제거 정책</span></div>
        <div class="v2-settings-list">
          <div class="v2-setting-row v2-setting-stack">
            <div class="v2-set-name">중복 제거 간격 (초)</div>
            <div class="v2-set-desc">동일 번호판·구역·방향이 이 시간 내 재감지되면 중복으로 처리</div>
            <input type="number" v-model.number="settings.dedupSeconds" min="1" max="60" />
          </div>
          <div class="v2-setting-row">
            <div><div class="v2-set-name">방향 변경 시 별도 카운트</div><div class="v2-set-desc">IN→OUT 또는 OUT→IN 변경 시 새 이벤트로 기록</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.dedupDirSplit" /><span></span></label>
          </div>
          <div class="v2-setting-row">
            <div><div class="v2-set-name">WebSocket 실시간 알림</div><div class="v2-set-desc">중요 이벤트를 즉시 전송</div></div>
            <label class="v2-switch"><input type="checkbox" v-model="settings.wsEnabled" /><span></span></label>
          </div>
        </div>
      </section>

      <section class="v2-card">
        <div class="v2-card-h"><span><i class="bi bi-shield-lock-fill"></i> 시스템 정보</span></div>
        <div class="v2-settings-list">
          <div class="v2-setting-row v2-setting-info"><span>버전</span><span class="mono">v1.0.0</span></div>
          <div class="v2-setting-row v2-setting-info"><span>최종 업데이트</span><span class="mono">{{ todayStr }}</span></div>
          <div class="v2-setting-row v2-setting-info"><span>등록 카메라</span><span class="mono">{{ totalCamCount }}대</span></div>
          <div class="v2-setting-row v2-setting-info"><span>API 상태</span><span class="v2-set-status ok">정상</span></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useDashboardData } from '@/composables/useDashboardData'
const { settings, totalCamCount, todayStr } = useDashboardData()
</script>
