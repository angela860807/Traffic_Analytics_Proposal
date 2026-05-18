<template>
  <div class="side-weather">
    <div class="sw-h">
      <span><i class="bi bi-cloud-sun-fill"></i> 날씨 / 대기</span>
      <div class="sw-tabs">
        <button v-for="d in districts" :key="d" class="sw-t" :class="{ on: active === d }" @click="active = d">
          {{ d.replace('구', '') }}
        </button>
      </div>
    </div>

    <div class="sw-main">
      <i class="sw-icon" :class="cur.icon" :style="{ color: cur.color }"></i>
      <div class="sw-c">
        <div class="sw-cond">{{ cur.condition }}</div>
        <div class="sw-temp">{{ cur.temp }}<small>°C</small></div>
      </div>
    </div>

    <div class="sw-stats">
      <div class="sw-st"><i class="bi bi-droplet-half"></i><span>습도</span><strong>{{ cur.humidity }}%</strong></div>
      <div class="sw-st"><i class="bi bi-wind"></i><span>풍속</span><strong>{{ cur.wind }}m/s</strong></div>
      <div class="sw-st"><i class="bi bi-eye"></i><span>가시거리</span><strong>{{ cur.visibility }}km</strong></div>
    </div>

    <div class="sw-aq">
      <div class="sw-aq-i">
        <div class="sw-aq-l">미세먼지 PM10</div>
        <div class="sw-aq-bar"><span :style="{ width: pm10Pct + '%', background: pm10Grade.color }"></span></div>
        <div class="sw-aq-v" :style="{ color: pm10Grade.color }">{{ cur.pm10 }}<small>μg</small> · {{ pm10Grade.label }}</div>
      </div>
      <div class="sw-aq-i">
        <div class="sw-aq-l">초미세 PM2.5</div>
        <div class="sw-aq-bar"><span :style="{ width: pm25Pct + '%', background: pm25Grade.color }"></span></div>
        <div class="sw-aq-v" :style="{ color: pm25Grade.color }">{{ cur.pm25 }}<small>μg</small> · {{ pm25Grade.label }}</div>
      </div>
    </div>

    <div class="sw-tip" v-if="tip">
      <i :class="tip.icon" :style="{ color: tip.color }"></i>
      <span>{{ tip.text }}</span>
    </div>

    <div class="sw-tomo">
      <span class="sw-tomo-l">내일</span>
      <i :class="cur.tomorrow.icon" :style="{ color: cur.tomorrow.color }"></i>
      <span class="sw-tomo-t">{{ cur.tomorrow.tempLo }}° / {{ cur.tomorrow.tempHi }}°</span>
      <span class="sw-tomo-r">강수 {{ cur.tomorrow.rainProb }}%</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { DISTRICT_LIST, INITIAL_DISTRICTS_WEATHER } from "@/data/weather";

const districts = DISTRICT_LIST;
const active = ref(districts[0]);
const cur = computed(() => INITIAL_DISTRICTS_WEATHER[active.value]);

function pmGrade(v, kind) {
  const t = kind === "pm10"
    ? [{ max: 30, label: "좋음",   color: "#059669" },
       { max: 80, label: "보통",   color: "#2563eb" },
       { max: 150, label: "나쁨",  color: "#b45309" },
       { max: 9999, label: "매우나쁨", color: "#dc2626" }]
    : [{ max: 15, label: "좋음",   color: "#059669" },
       { max: 35, label: "보통",   color: "#2563eb" },
       { max: 75, label: "나쁨",   color: "#b45309" },
       { max: 9999, label: "매우나쁨", color: "#dc2626" }];
  return t.find(g => v <= g.max);
}

const pm10Grade = computed(() => pmGrade(cur.value.pm10, "pm10"));
const pm25Grade = computed(() => pmGrade(cur.value.pm25, "pm25"));
const pm10Pct = computed(() => Math.min(100, (cur.value.pm10 / 150) * 100));
const pm25Pct = computed(() => Math.min(100, (cur.value.pm25 / 75) * 100));

const tip = computed(() => {
  const c = cur.value;
  if (c.condition === "비" || c.condition === "뇌우") {
    return { icon: "bi bi-exclamation-triangle-fill", color: "#dc2626", text: "강수 영향 — 사고·정체 주의" };
  }
  if (c.condition === "안개" || c.visibility < 5) {
    return { icon: "bi bi-exclamation-triangle-fill", color: "#b45309", text: "가시거리 저하 — OCR 신뢰도 감소" };
  }
  if (c.pm10 > 80 || c.pm25 > 35) {
    return { icon: "bi bi-cloud-haze2-fill", color: "#b45309", text: "대기질 나쁨 — 카메라 영상 흐림" };
  }
  if (c.wind > 7) {
    return { icon: "bi bi-wind", color: "#b45309", text: "강풍 — 설비 흔들림 주의" };
  }
  return null;
});
</script>
