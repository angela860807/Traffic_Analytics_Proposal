// ECharts tree-shaken setup — 사용 중인 차트/컴포넌트만 등록해 번들 크기 최소화
import * as echarts from "echarts/core";
import { LineChart, BarChart, GaugeChart, PieChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  MarkAreaComponent,
  MarkPointComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart,
  BarChart,
  GaugeChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
  MarkAreaComponent,
  MarkPointComponent,
  CanvasRenderer,
]);

export default echarts;
export { echarts };
