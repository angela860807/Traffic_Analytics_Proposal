// 부서별 보고서 CSV 생성·다운로드 헬퍼
// 사용: const { downloadCSV, makeDeptReport } = useReportDownload()

function csvEscape(v) {
  if (v == null) return "";
  const s = String(v);
  if (/[",\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function rowsToCSV(rows) {
  return rows.map((row) => row.map(csvEscape).join(",")).join("\r\n");
}

function todayStr() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function downloadCSV(filename, rows) {
  const csv = "﻿" + rowsToCSV(rows); // BOM for Excel UTF-8
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    URL.revokeObjectURL(url);
    a.remove();
  }, 100);
}

// 부서별 기본 보고서 템플릿
const DEPT_TEMPLATES = {
  ops: {
    name: "시설운영팀",
    reports: {
      daily: {
        title: "일일 장비 가동 보고서",
        header: ["장비ID", "유형", "위치", "상태", "가동률(%)", "최근 점검"],
        sample: [
          ["NSN-N-0023", "카메라", "내부순환로 03K+150", "장애", "94.2", "2026-05-19"],
          ["CAM-K-014", "카메라", "강변북로 한남TG", "정상", "99.8", "2026-05-18"],
          ["EDGE-04", "엣지서버", "정릉터널", "정상", "99.5", "2026-05-15"],
        ],
      },
      weekly: {
        title: "주간 장애 분석 보고서",
        header: ["발생일", "장비ID", "장애 유형", "복구 시간(분)", "담당자"],
        sample: [
          ["2026-05-19", "NSN-N-0023", "RTSP 타임아웃", "12", "김기사"],
          ["2026-05-17", "CAM-O-019", "디스크 풀", "34", "이엔지"],
          ["2026-05-15", "EDGE-02", "OCR 큐 적체", "8", "박기사"],
        ],
      },
    },
  },
  control: {
    name: "교통정보센터",
    reports: {
      daily: {
        title: "일일 운영 보고서",
        header: ["시각", "구간", "이벤트", "처리 상태", "담당자"],
        sample: [
          ["14:24", "강변북로 한남TG", "차량 정체 (사고)", "진행", "김관제"],
          ["11:08", "올림픽대로 가양", "차량 고장", "복구", "이관제"],
          ["08:42", "내부순환 정릉", "출근 정체", "복구", "박관제"],
        ],
      },
      weekly: {
        title: "주간 정체 분석 보고서",
        header: ["구간", "총 정체 시간(분)", "사고 건수", "평균 속도(km/h)"],
        sample: [
          ["강변북로", "428", "3", "32"],
          ["올림픽대로", "276", "1", "41"],
          ["내부순환로", "512", "2", "28"],
        ],
      },
    },
  },
  review: {
    name: "단속관리팀",
    reports: {
      daily: {
        title: "일일 단속 보고서",
        header: ["시각", "장소", "차량번호", "감지속도", "제한속도", "상태"],
        sample: [
          ["14:32:18", "강변북로 (구리→한남)", "12가 4567", "112", "70", "검토 대기"],
          ["14:31:22", "내부순환로 (정릉→성수)", "34더 5678", "108", "70", "검토 대기"],
          ["14:30:11", "강변북로 (한남 TG)", "11가 2233", "121", "70", "검토 대기"],
        ],
      },
      weekly: {
        title: "주간 단속 통계",
        header: ["구간", "총 단속", "승인", "반려", "평균 OCR 신뢰도(%)"],
        sample: [
          ["강변북로", "428", "382", "46", "95"],
          ["올림픽대로", "215", "201", "14", "94"],
          ["내부순환로", "187", "172", "15", "93"],
        ],
      },
    },
  },
  analytics: {
    name: "교통분석팀",
    reports: {
      daily: {
        title: "일일 교통흐름 리포트",
        header: ["구간", "평균속도(km/h)", "전일 대비", "피크 시간", "혼잡도"],
        sample: [
          ["강변IC", "61", "+4", "09시", "원활"],
          ["일산IC", "23", "-9", "08시", "혼잡"],
          ["원효대교", "27", "-11", "18시", "혼잡"],
        ],
      },
      weekly: {
        title: "주간 구간 성능 분석",
        header: ["구간", "주간 평균(km/h)", "최저 시간대", "혼잡 지속(분)"],
        sample: [
          ["강변북로", "42", "08:00-09:30", "428"],
          ["올림픽대로", "56", "18:00-19:00", "276"],
          ["내부순환로", "38", "07:30-09:00", "512"],
        ],
      },
    },
  },
  reports: {
    name: "운영기획팀",
    reports: {
      monthly: {
        title: "월간 운영성과 보고서",
        header: ["KPI", "목표", "실적", "달성률(%)"],
        sample: [
          ["평균 응답시간", "200ms", "168ms", "108"],
          ["장비 가동률", "99.5%", "99.6%", "100"],
          ["단속 처리율", "95%", "94.2%", "99"],
        ],
      },
      quarterly: {
        title: "분기 KPI 종합 보고서",
        header: ["부서", "주요 KPI", "전분기 대비", "비고"],
        sample: [
          ["시설운영팀", "장비 가동률 99.6%", "+0.2%p", "안정"],
          ["교통정보센터", "이벤트 평균 복구 31분", "-4분", "개선"],
          ["단속관리팀", "OCR 신뢰도 94.6%", "+1.1%p", "개선"],
        ],
      },
    },
  },
  super: {
    name: "경영전략본부",
    reports: {
      monthly: {
        title: "월간 종합 운영 보고서",
        header: ["부서", "주요 지표", "값", "상태"],
        sample: [
          ["시설운영팀", "장비 가동률", "99.6%", "정상"],
          ["교통정보센터", "평균 처리 시간", "31분", "정상"],
          ["단속관리팀", "단속 처리율", "94.2%", "정상"],
          ["교통분석팀", "분석 완료율", "98.4%", "정상"],
        ],
      },
      audit: {
        title: "보안·감사 로그 보고서",
        header: ["시각", "사용자", "역할", "행위", "결과"],
        sample: [
          ["10:24", "SUPER ADMIN", "최고관리자", "보고서 승인", "성공"],
          ["09:58", "교통분석팀 정민혁", "분석가", "리포트 발행", "성공"],
          ["09:32", "단속관리팀 김지현", "검토자", "이벤트 승인", "성공"],
        ],
      },
    },
  },
};

function makeDeptReport(deptKey, reportKey, opts = {}) {
  const dept = DEPT_TEMPLATES[deptKey];
  if (!dept) return null;
  const r = dept.reports[reportKey];
  if (!r) return null;
  const baseDate = opts.date || todayStr();
  const periodLabel = opts.endDate
    ? `${baseDate} ~ ${opts.endDate}`
    : baseDate;
  return {
    title: r.title,
    dept: dept.name,
    rows: [
      [`${dept.name} — ${r.title}`],
      [`기간`, periodLabel],
      [`생성일`, todayStr()],
      [],
      r.header,
      ...r.sample,
    ],
    filename: `${dept.name}_${r.title}_${baseDate}.csv`,
  };
}

export function useReportDownload() {
  function downloadDeptReport(deptKey, reportKey, opts = {}) {
    const report = makeDeptReport(deptKey, reportKey, opts);
    if (!report) return;
    downloadCSV(report.filename, report.rows);
  }
  function downloadCustom(filename, header, rows) {
    downloadCSV(filename, [header, ...rows]);
  }
  return { downloadDeptReport, downloadCustom, downloadCSV };
}
