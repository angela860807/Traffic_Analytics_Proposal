<template>
  <footer class="ftw">
    <div class="ft-top">
      <div class="ft-brand">
        <div class="ft-logo">
          <span class="ft-logo-dot"></span>
          Traffic<em>AS</em>
        </div>
        <p class="ft-tag">YOLO 기반 실시간 차량 감지와<br />번호판 OCR로 교통 흐름을 분석합니다.</p>
      </div>

      <div class="ft-col">
        <div class="ft-h">서비스</div>
        <ul>
          <li><RouterLink to="/sub/intro">시스템 소개</RouterLink></li>
          <li><RouterLink to="/sub/support">공지사항</RouterLink></li>
          <li><RouterLink to="/dashboard">관리자 대시보드</RouterLink></li>
        </ul>
      </div>

      <div class="ft-col">
        <div class="ft-h">팀 · 산출물</div>
        <ul>
          <li><a href="https://github.com/angela860807/Traffic_Analytics_Proposal" target="_blank" rel="noopener"><i class="bi bi-github"></i> GitHub Repository</a></li>
          <li><a href="#" rel="noopener"><i class="bi bi-journal-text"></i> 프로젝트 산출물</a></li>
          <li><a href="mailto:chlehdgb123@naver.com"><i class="bi bi-envelope"></i> chlehdgb123@naver.com</a></li>
        </ul>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>

<style scoped>
.ftw {
  border-top: 1px solid var(--b);
  background: var(--bg2);
  padding: 24px 60px 22px;
}
.ft-top {
  max-width: 1440px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.6fr 1fr 1.2fr;
  gap: 48px;
}
.ft-brand .ft-logo {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.3;
  letter-spacing: -0.5px;
  color: var(--t);
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.ft-logo em { color: var(--a); font-style: normal; }
.ft-logo-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--a);
  box-shadow: 0 0 8px var(--a);
  animation: livePulse 2s ease-in-out infinite;
}
.ft-tag {
  font-size: 13.5px;
  font-weight: 400;
  line-height: 1.55;
  color: var(--t);
  opacity: 0.62;
  max-width: 320px;
  margin-bottom: 8px;
}
.ft-col {
  text-align: center;
}
.ft-col .ft-h {
  font-family: "Pretendard Variable", Pretendard, sans-serif;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.2px;
  color: var(--t);
  opacity: 0.88;
  margin-bottom: 10px;
}
.ft-col ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 7px;
}
.ft-col a {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--t);
  opacity: 0.62;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  transition: opacity 0.18s, color 0.18s;
}
.ft-col a:hover { color: var(--a); opacity: 1; }
.ft-col a i { font-size: 13.5px; opacity: 0.85; }

@media (max-width: 1100px) {
  .ft-top { grid-template-columns: 1fr 1fr; gap: 40px; }
}
@media (max-width: 768px) {
  .ftw { padding-left: 24px; padding-right: 24px; }
  .ft-top { grid-template-columns: 1fr; gap: 32px; }
}
</style>
