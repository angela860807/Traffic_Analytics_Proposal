<template>
  <aside class="sidebar">
    <div class="group">
      <div class="glbl">GUIDE</div>
      <div class="item" :class="{on:modelValue==='usage'}" @click="$emit('update:modelValue','usage')">
        <span class="ico">📖</span><span>사용법</span>
      </div>
      <div class="item" :class="{on:modelValue==='intro'}" @click="$emit('update:modelValue','intro')">
        <span class="ico">🖥️</span><span>시스템 소개</span>
      </div>
    </div>
    <div class="group">
      <div class="glbl">SUPPORT</div>
      <div class="item" :class="{on:modelValue==='support'}" @click="$emit('update:modelValue','support')">
        <span class="ico">🎧</span><span>고객 지원</span>
        <span class="new-dot"></span>
      </div>
    </div>
  </aside>
</template>
<script setup>
defineProps({ modelValue: String })
defineEmits(['update:modelValue'])
</script>
<style scoped>
.sidebar{width:210px;flex-shrink:0;position:fixed;top:62px;left:0;bottom:0;
  background:var(--bg2);border-right:1px solid var(--b);overflow-y:auto;padding:20px 0;z-index:100}
.group{padding:0 0 14px;border-bottom:1px solid var(--b);margin-bottom:14px}
.group:last-child{border-bottom:none;margin-bottom:0}
.glbl{font-family:'IBM Plex Mono',monospace;font-size:8px;letter-spacing:.2em;
  color:var(--t3);padding:0 18px;margin-bottom:6px}
.item{display:flex;align-items:center;gap:9px;padding:9px 18px;font-size:13px;
  color:var(--t2);cursor:pointer;transition:all .2s;border-left:2px solid transparent}
.item:hover{color:var(--t);background:rgba(255,255,255,.04);border-left-color:rgba(255,255,255,.18)}
.item.on{color:var(--a);background:rgba(255,255,255,.04);border-left-color:var(--a)}
.ico{font-size:14px;width:20px;flex-shrink:0}
.new-dot{width:5px;height:5px;border-radius:50%;background:var(--in);
  margin-left:auto;animation:livePulse 2s ease-in-out infinite}
</style>
