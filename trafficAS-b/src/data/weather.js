export const WEATHER_PRESETS = {
  clear:   { condition: '맑음',      icon: 'bi bi-sun-fill',                  color: '#fbbf24' },
  pcloud:  { condition: '구름 조금', icon: 'bi bi-cloud-sun-fill',            color: '#93c5fd' },
  cloudy:  { condition: '흐림',      icon: 'bi bi-clouds-fill',               color: '#94a3b8' },
  rain:    { condition: '비',        icon: 'bi bi-cloud-rain-heavy-fill',     color: '#60a5fa' },
  drizzle: { condition: '이슬비',    icon: 'bi bi-cloud-drizzle-fill',        color: '#7dd3fc' },
  snow:    { condition: '눈',        icon: 'bi bi-cloud-snow-fill',           color: '#e0f2fe' },
  thunder: { condition: '뇌우',      icon: 'bi bi-cloud-lightning-rain-fill', color: '#a78bfa' },
  fog:     { condition: '안개',      icon: 'bi bi-cloud-fog2-fill',           color: '#cbd5e1' },
  haze:    { condition: '미세먼지',  icon: 'bi bi-cloud-haze2-fill',          color: '#d4845a' },
}

export const DISTRICT_LIST = ['강남구', '서초구', '송파구']

export const INITIAL_DISTRICTS_WEATHER = {
  강남구: {
    ...WEATHER_PRESETS.cloudy, aqi: 75, temp: 22, humidity: 60, pm10: 45, pm25: 22, o3: 0.038, wind: 2.4, uv: 5,  visibility: 8,
    tomorrow: { ...WEATHER_PRESETS.clear,  tempHi: 25, tempLo: 17, humidity: 55, pm10: 32, pm25: 16, rainProb: 10 },
  },
  서초구: {
    ...WEATHER_PRESETS.pcloud, aqi: 62, temp: 21, humidity: 55, pm10: 38, pm25: 18, o3: 0.032, wind: 3.1, uv: 6,  visibility: 11,
    tomorrow: { ...WEATHER_PRESETS.clear,  tempHi: 24, tempLo: 16, humidity: 52, pm10: 28, pm25: 13, rainProb: 5 },
  },
  송파구: {
    ...WEATHER_PRESETS.rain,   aqi: 88, temp: 20, humidity: 78, pm10: 52, pm25: 28, o3: 0.041, wind: 4.5, uv: 2,  visibility: 5,
    tomorrow: { ...WEATHER_PRESETS.cloudy, tempHi: 22, tempLo: 15, humidity: 70, pm10: 42, pm25: 20, rainProb: 40 },
  },
}
