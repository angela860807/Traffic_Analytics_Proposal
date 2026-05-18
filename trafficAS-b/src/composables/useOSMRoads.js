// OSM Overpass에서 도로 geometry를 받아 Leaflet polyline으로 렌더링하는 공통 모듈
import L from "leaflet";

const OVERPASS_MIRRORS = [
  "https://overpass-api.de/api/interpreter",
  "https://overpass.kumi.systems/api/interpreter",
  "https://overpass.private.coffee/api/interpreter",
  "https://lz4.overpass-api.de/api/interpreter",
];
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24h
// 세션 내 메모리 캐시 + 동시 호출 dedup (다중 사용자 / 빠른 탭 전환 시 OSM 부하 방지)
const memCache = new Map();      // cacheKey → ways
const inflight = new Map();      // cacheKey → Promise

/** 도로 혼잡도(0~1) → 색상 5단계 */
export function congestionColor(c) {
  if (c >= 0.85) return "#e74c3c"; // 정체
  if (c >= 0.65) return "#f39c12"; // 혼잡
  if (c >= 0.45) return "#f1c40f"; // 보통
  if (c >= 0.25) return "#7dc242"; // 양호
  return "#2ecc71";                // 원활
}
export function congestionLabel(c) {
  if (c >= 0.85) return "정체";
  if (c >= 0.65) return "혼잡";
  if (c >= 0.45) return "보통";
  if (c >= 0.25) return "양호";
  return "원활";
}

/**
 * @param {string} cacheKey   - localStorage 캐시 키
 * @param {string} bbox       - "south,west,north,east" 형식
 * @param {string[]} [classes]- 도로 등급 필터 (기본: 주요 간선만)
 */
export async function loadOSMRoads(cacheKey, bbox, classes = ["motorway", "trunk", "primary"]) {
  // 1순위: 메모리 캐시 (즉시 반환)
  if (memCache.has(cacheKey)) return memCache.get(cacheKey);
  // 2순위: 진행 중 동일 요청 dedup (다른 탭/컴포넌트가 같은 데이터 요청 시 공유)
  if (inflight.has(cacheKey)) return inflight.get(cacheKey);
  // 3순위: localStorage 캐시 (24h)
  try {
    const raw = localStorage.getItem(cacheKey);
    if (raw) {
      const { ts, data } = JSON.parse(raw);
      if (Date.now() - ts < CACHE_TTL && Array.isArray(data) && data.length) {
        memCache.set(cacheKey, data);
        return data;
      }
    }
  } catch {}

  const promise = fetchFromOverpass(cacheKey, bbox, classes);
  inflight.set(cacheKey, promise);
  try {
    const result = await promise;
    if (result) memCache.set(cacheKey, result);
    return result;
  } finally {
    inflight.delete(cacheKey);
  }
}

// 미러 시작 인덱스를 분 단위로 분산 — 동시 사용자가 같은 미러로 몰리지 않도록
function pickMirrorOrder(key) {
  const seed = (key.charCodeAt(0) + Math.floor(Date.now() / 60000)) % OVERPASS_MIRRORS.length;
  return [...OVERPASS_MIRRORS.slice(seed), ...OVERPASS_MIRRORS.slice(0, seed)];
}

async function fetchFromOverpass(cacheKey, bbox, classes) {
  const hwyRe = classes.join("|");
  const query = `[out:json][timeout:20];
(
  way["highway"~"^(${hwyRe})$"](${bbox});
);
out geom;`;
  const mirrors = pickMirrorOrder(cacheKey);

  for (const url of mirrors) {
    try {
      const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "data=" + encodeURIComponent(query),
        signal: AbortSignal.timeout(10000),
      });
      // 429 (Too Many Requests) / 504 (Gateway Timeout): 다음 미러로 즉시 폴백
      if (r.status === 429 || r.status === 504) continue;
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const ways = data.elements?.filter(e => e.type === "way" && e.geometry?.length >= 2)
        // 좌표 정밀도 축소(소수점 5자리 ≈ 1m) → 캐시 용량 절반
        .map(w => ({
          id: w.id, tags: w.tags,
          geometry: w.geometry.map(p => ({ lat: +p.lat.toFixed(5), lon: +p.lon.toFixed(5) })),
        })) || [];
      if (ways.length) {
        try { localStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data: ways })); } catch {}
        return ways;
      }
    } catch (e) {
      console.warn(`[OSM] ${url} 실패:`, e.message);
    }
  }
  return null;
}

/**
 * 가져온 도로를 Leaflet에 폴리라인으로 추가
 * @returns Map<string, L.Polyline>
 */
export function renderOSMRoads(map, ways) {
  const weights = { motorway: 6, trunk: 5.5, primary: 5, secondary: 4 };
  // 모든 폴리라인을 layerGroup으로 묶어 한 번에 추가 → reflow 1회
  const group = L.layerGroup();
  ways.forEach(way => {
    const path = way.geometry.map(p => [p.lat, p.lon]);
    const hwy = way.tags?.highway;
    const w = weights[hwy] || 4;
    const name = way.tags?.["name:ko"]
              || way.tags?.name
              || way.tags?.["name:en"]
              || `${hwy} #${way.id}`;
    const baseCong = hwy === "motorway" || hwy === "trunk" ? 0.75
                   : hwy === "primary" ? 0.55 : 0.35;
    const c = Math.max(0.1, Math.min(0.95, baseCong + (Math.random() - 0.5) * 0.3));

    L.polyline(path, {
      color: congestionColor(c),
      weight: w, opacity: 0.88,
      lineCap: "round", lineJoin: "round",
      // smoothFactor 높이면 화면 외 미세 곡선 단순화 → 렌더링 비용 ↓
      smoothFactor: 1.5,
    })
      .bindTooltip(
        `${name}<br/><b style="color:${congestionColor(c)}">${congestionLabel(c)}</b> · ${Math.round(c * 100)}%`,
        { sticky: true, className: "osm-road-tip", direction: "top", offset: [0, -6] }
      )
      .addTo(group);
  });
  group.addTo(map);
  return group;
}
