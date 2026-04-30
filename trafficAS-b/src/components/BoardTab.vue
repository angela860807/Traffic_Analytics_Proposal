<template>
  <div class="board">
    <div class="top-row">
      <p class="info">사용 후기, 활용 사례, 공지사항을 공유하세요.</p>
      <button class="wbtn">✏️ 글쓰기</button>
    </div>
    <div class="tbl">
      <div class="th grid4"><span>제목</span><span>작성자</span><span>날짜</span><span>조회</span></div>
      <div class="tr grid4" v-for="p in posts" :key="p.id">
        <span class="ttl">{{ p.title }}<span class="nb" v-if="p.isNew">NEW</span></span>
        <span class="sub">{{ p.author }}</span>
        <span class="sub mono">{{ p.date }}</span>
        <span class="sub mono">{{ p.views }}</span>
      </div>
    </div>
    <div class="pagi">
      <button class="pg on">1</button>
      <button class="pg" v-for="n in 4" :key="n">{{ n+1 }}</button>
    </div>
  </div>
</template>
<script setup>
const posts = [
  { id:1,title:'[공지] 시스템 v1.2 업데이트 안내',      author:'관리자',date:'04.29',views:128,isNew:true  },
  { id:2,title:'야간 번호판 인식률 개선 후기',            author:'user01',date:'04.28',views:87, isNew:true  },
  { id:3,title:'다중 카메라 동시 운영 팁',               author:'user02',date:'04.27',views:64, isNew:false },
  { id:4,title:'Docker Compose 설정 파일 공유',          author:'user03',date:'04.26',views:52, isNew:false },
  { id:5,title:'Spring Boot + FastAPI 연동 주의사항',    author:'user04',date:'04.25',views:41, isNew:false },
  { id:6,title:'PostgreSQL 인덱스 최적화 경험담',        author:'user05',date:'04.24',views:38, isNew:false },
]
</script>
<style scoped>
.top-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.info{font-size:13px;color:var(--t2);font-weight:300}
.wbtn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;
  background:var(--a);color:var(--bg);font-family:'IBM Plex Mono',monospace;
  font-size:11px;font-weight:500;letter-spacing:.08em;border-radius:4px;cursor:pointer;border:none}
.wbtn:hover{opacity:.87}
.tbl{background:var(--bg2);border:1px solid var(--b);border-radius:7px;overflow:hidden;margin-bottom:14px}
.th{padding:10px 16px;border-bottom:1px solid var(--b);background:rgba(255,255,255,.025);
  font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.1em;color:var(--t3)}
.tr{padding:11px 16px;border-bottom:1px solid var(--b);font-size:12px;align-items:center;transition:background .15s}
.tr:last-child{border-bottom:none}.tr:hover{background:rgba(255,255,255,.03)}
.grid4{display:grid;grid-template-columns:1fr 80px 70px 50px;gap:8px;align-items:center}
.ttl{color:var(--t);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sub{font-size:11px;color:var(--t3)}.mono{font-family:'IBM Plex Mono',monospace;font-size:10px}
.nb{font-family:'IBM Plex Mono',monospace;font-size:8px;background:rgba(255,255,255,.1);
  color:var(--a);padding:1px 5px;border-radius:100px;margin-left:5px}
.pagi{display:flex;gap:5px;justify-content:center}
.pg{width:30px;height:30px;border-radius:4px;border:1px solid var(--b);background:transparent;
  color:var(--t3);font-family:'IBM Plex Mono',monospace;font-size:11px;cursor:pointer;transition:all .2s}
.pg:hover,.pg.on{border-color:var(--ba);color:var(--a);background:rgba(255,255,255,.04)}
</style>
