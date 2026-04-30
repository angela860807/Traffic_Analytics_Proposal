import { reactive, onMounted, onUnmounted } from 'vue'
export function useStats() {
  const stats = reactive([
    { badge:'TODAY LIVE',  label:'오늘 감지 차량',     unit:'대', live:true,  target:4821, dec:0, display:'0' },
    { badge:'FLOW EVENTS', label:'유입·유출 이벤트',   unit:'건', live:true,  target:9203, dec:0, display:'0' },
    { badge:'ACCURACY',    label:'번호판 인식 정확도',  unit:'%',  live:false, target:96.2, dec:1, display:'0' },
    { badge:'LATENCY',     label:'AI 응답 레이턴시',   unit:'ms', live:false, target:48,   dec:0, display:'0' },
  ])
  let timer = null
  function countUp() {
    stats.forEach((s, i) => {
      let cur = 0, step = 0, steps = 60
      const t = setInterval(() => {
        step++; cur = Math.min(cur + s.target / steps, s.target)
        s.display = s.dec > 0 ? cur.toFixed(s.dec) : Math.round(cur).toLocaleString('ko-KR')
        if (step >= steps) clearInterval(t)
      }, (1500 + i * 180) / steps)
    })
  }
  onMounted(() => {
    countUp()
    timer = setInterval(() => {
      stats[0].target += Math.floor(Math.random() * 3 + 1)
      stats[0].display  = stats[0].target.toLocaleString('ko-KR')
      stats[1].target += Math.floor(Math.random() * 5 + 1)
      stats[1].display  = stats[1].target.toLocaleString('ko-KR')
    }, 1800)
  })
  onUnmounted(() => clearInterval(timer))
  return { stats }
}
