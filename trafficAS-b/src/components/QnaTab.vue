<template>
  <div class="qna">
    <div class="top-row">
      <p class="info">궁금한 점을 질문하고 전문가 답변을 받으세요.</p>
      <button class="wbtn">✏️ 질문하기</button>
    </div>
    <div class="tbl">
      <div class="th grid3"><span>질문</span><span>작성자</span><span>상태</span></div>
      <div class="tr grid3" v-for="q in items" :key="q.id">
        <span class="ttl">{{ q.title }}<span class="nb" v-if="q.isNew">NEW</span></span>
        <span class="sub">{{ q.author }}</span>
        <span><span class="sts" :class="q.cls">{{ q.status }}</span></span>
      </div>
    </div>
  </div>
</template>
<script setup>
const items = [
  { id:1,title:'WebSocket 연결이 자꾸 끊기는 문제',      author:'user06',status:'답변완료',cls:'done',isNew:false },
  { id:2,title:'카메라 RTSP 주소 형식이 어떻게 되나요?', author:'user07',status:'답변완료',cls:'done',isNew:false },
  { id:3,title:'번호판 인식률이 70%대에 머물러요',        author:'user08',status:'답변중',  cls:'ing', isNew:true  },
  { id:4,title:'Docker 환경에서 GPU 설정 방법',          author:'user09',status:'대기중',  cls:'wait',isNew:true  },
  { id:5,title:'Spring Boot 토큰 만료 시간 설정',        author:'user10',status:'답변완료',cls:'done',isNew:false },
]
</script>
<style scoped>
.top-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.info{font-size:13px;color:var(--t2);font-weight:300}
.wbtn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;
  background:var(--a);color:var(--bg);font-family:'IBM Plex Mono',monospace;
  font-size:11px;font-weight:500;letter-spacing:.08em;border-radius:4px;cursor:pointer;border:none}
.wbtn:hover{opacity:.87}
.tbl{background:var(--bg2);border:1px solid var(--b);border-radius:7px;overflow:hidden}
.th{padding:10px 16px;border-bottom:1px solid var(--b);background:rgba(255,255,255,.025);
  font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.1em;color:var(--t3)}
.tr{padding:11px 16px;border-bottom:1px solid var(--b);font-size:12px;align-items:center;transition:background .15s}
.tr:last-child{border-bottom:none}.tr:hover{background:rgba(255,255,255,.03)}
.grid3{display:grid;grid-template-columns:1fr 80px 80px;gap:8px;align-items:center}
.ttl{color:var(--t);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sub{font-size:11px;color:var(--t3)}
.nb{font-family:'IBM Plex Mono',monospace;font-size:8px;background:rgba(255,255,255,.1);
  color:var(--a);padding:1px 5px;border-radius:100px;margin-left:5px}
.sts{font-family:'IBM Plex Mono',monospace;font-size:9px;padding:2px 8px;border-radius:3px}
.done{background:rgba(52,211,153,.1);color:#34d399}
.ing{background:rgba(251,146,60,.1);color:#fb923c}
.wait{background:rgba(255,255,255,.05);color:var(--t3)}
</style>
