<template>
  <div class="chat">
    <div class="online-bar">
      <span class="olabel"><span class="odot"></span>{{ count }}명 접속 중</span>
      <span class="meta">· WebSocket · 실시간</span>
    </div>
    <div class="msgs" ref="msgsEl">
      <template v-for="m in messages" :key="m.id">
        <div class="sys" v-if="m.type==='sys'">{{ m.text }}</div>
        <div class="msg" :class="{mine:m.mine}" v-else>
          <div class="av">{{ m.avatar }}</div>
          <div class="body">
            <div class="name">{{ m.name }}</div>
            <div class="bubble">{{ m.text }}</div>
            <div class="time">{{ m.time }}</div>
          </div>
        </div>
      </template>
    </div>
    <div class="bar">
      <input class="ci" v-model="input" placeholder="메시지를 입력하세요... (Enter)" @keyup.enter="send" />
      <button class="sbtn" @click="send">전송</button>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, nextTick } from 'vue'
const count = ref(6)
const input = ref('')
const msgsEl = ref(null)
let seq = 100
const messages = reactive([
  { id:1, type:'sys',  text:'채팅방에 입장했습니다.' },
  { id:2, type:'msg',  mine:false, avatar:'👤', name:'관리자', text:'안녕하세요! 궁금한 점을 자유롭게 물어보세요.', time:'10:30' },
  { id:3, type:'msg',  mine:false, avatar:'🙂', name:'user01', text:'v1.2 업데이트 이후 OCR이 확실히 좋아졌어요!', time:'10:31' },
  { id:4, type:'msg',  mine:false, avatar:'😊', name:'user02', text:'야간 조도 환경도 개선됐나요?', time:'10:32' },
  { id:5, type:'msg',  mine:false, avatar:'👤', name:'관리자', text:'네, 야간 저조도 인식률을 94% 이상으로 개선했습니다.', time:'10:32' },
])
const replies = ['감사합니다!','확인해드리겠습니다.','추가 문의사항이 있으시면 알려주세요 😊','좋은 의견 감사합니다.','잠시만 기다려주세요...']
function now() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}
function send() {
  const text = input.value.trim(); if (!text) return
  messages.push({ id:++seq, type:'msg', mine:true, avatar:'😀', name:'나', text, time:now() })
  input.value = ''
  nextTick(() => { if (msgsEl.value) msgsEl.value.scrollTop = msgsEl.value.scrollHeight })
  setTimeout(() => {
    messages.push({ id:++seq, type:'msg', mine:false, avatar:'👤', name:'관리자',
      text: replies[Math.floor(Math.random()*replies.length)], time:now() })
    nextTick(() => { if (msgsEl.value) msgsEl.value.scrollTop = msgsEl.value.scrollHeight })
  }, 600 + Math.random()*800)
}
</script>
<style scoped>
.chat{display:flex;flex-direction:column;height:100%;min-height:400px}
.online-bar{padding:10px 20px;border-bottom:1px solid var(--b);background:var(--bg2);
  display:flex;align-items:center;gap:8px}
.olabel{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--in);
  display:flex;align-items:center;gap:5px}
.odot{width:5px;height:5px;border-radius:50%;background:var(--in);animation:livePulse 1.5s ease-in-out infinite}
.meta{font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--t3)}
.msgs{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msgs::-webkit-scrollbar{width:3px}
.msgs::-webkit-scrollbar-thumb{background:var(--b);border-radius:2px}
.sys{text-align:center;font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--t3);
  display:flex;align-items:center;gap:8px}
.sys::before,.sys::after{content:'';flex:1;height:1px;background:var(--b)}
.msg{display:flex;gap:10px;align-items:flex-start}
.msg.mine{flex-direction:row-reverse}
.av{width:32px;height:32px;border-radius:50%;border:1px solid var(--b);
  display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0}
.body{max-width:65%}
.name{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--t3);margin-bottom:4px}
.msg.mine .name{text-align:right}
.bubble{padding:10px 14px;border-radius:8px;font-size:13px;line-height:1.65;
  background:var(--card);border:1px solid var(--b);color:var(--t)}
.msg.mine .bubble{background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.12)}
.time{font-family:'IBM Plex Mono',monospace;font-size:9px;color:var(--t3);margin-top:4px}
.msg.mine .time{text-align:right}
.bar{padding:14px 20px;border-top:1px solid var(--b);display:flex;gap:10px;background:var(--bg2)}
.ci{flex:1;background:var(--bg);border:1px solid var(--b);border-radius:6px;
  padding:10px 14px;font-size:13px;color:var(--t);font-family:'Noto Sans KR',sans-serif;
  outline:none;transition:border-color .2s}
.ci:focus{border-color:var(--ba)}.ci::placeholder{color:var(--t3)}
.sbtn{padding:10px 20px;background:var(--a);color:var(--bg);border:none;border-radius:6px;
  font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:500;cursor:pointer;white-space:nowrap}
.sbtn:hover{opacity:.87}
</style>
