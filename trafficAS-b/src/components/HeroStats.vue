<template>
  <div class="stats-band" :class="variant">
    <div class="sc" v-for="(s,i) in stats" :key="i">
      <div class="badge"><span class="dot" v-if="s.live"></span>{{ s.badge }}</div>
      <div><span class="num">{{ s.display }}</span><span class="unit">{{ s.unit }}</span></div>
      <div class="lbl">{{ s.label }}</div>
    </div>
  </div>
</template>
<script setup>
defineProps({ stats: Array, variant: { type:String, default:'cyan' } })
</script>
<style scoped>
.stats-band{position:relative;z-index:2;display:grid;grid-template-columns:repeat(4,1fr)}
.stats-band.cyan{gap:1px;background:rgba(0,229,255,.09);border-top:1px solid rgba(0,229,255,.15)}
.stats-band.navy{background:rgba(2,11,24,.78);backdrop-filter:blur(14px);border-top:1px solid rgba(96,165,250,.12)}
.sc{padding:24px 30px;position:relative;overflow:hidden;cursor:default;transition:background .22s}
.stats-band.navy .sc{border-right:1px solid rgba(96,165,250,.1)}
.stats-band.cyan .sc{background:var(--bg)}
.sc:last-child{border-right:none}
.sc:hover{background:rgba(255,255,255,.04)}
.sc::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:var(--a);transform:scaleX(0);transition:transform .4s;transform-origin:left}
.sc:hover::after{transform:scaleX(1)}
.sc:first-child::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,var(--a),transparent);opacity:.7}
.sc:first-child .num{text-shadow:0 0 36px color-mix(in srgb,var(--a) 45%,transparent)}
.badge{font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.18em;
  color:var(--a);opacity:.62;display:flex;align-items:center;gap:6px;margin-bottom:10px}
.dot{width:5px;height:5px;border-radius:50%;background:var(--a);animation:livePulse 1.8s ease-in-out infinite}
.num{font-family:'Syne',sans-serif;font-size:clamp(26px,3.5vw,48px);
  font-weight:700;letter-spacing:-2px;line-height:1;color:var(--t)}
.unit{font-size:13px;color:var(--t3);margin-left:4px}
.lbl{font-size:11px;color:var(--t3);margin-top:7px}
/* navy variant는 항상 다크 배경 → 라이트모드에서도 밝은 텍스트 고정 */
.stats-band.navy .num{color:#e4eeff}
.stats-band.navy .unit{color:rgba(228,238,255,.45)}
.stats-band.navy .lbl{color:rgba(228,238,255,.45)}
.stats-band.navy .badge{color:#60a5fa;opacity:1}
@media(max-width:768px){
  .stats-band{grid-template-columns:1fr 1fr}
  .sc:nth-child(2){border-right:none}
}
</style>
