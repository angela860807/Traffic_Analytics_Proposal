from dataclasses import dataclass
import threading


@dataclass
class DurationMetric:
    count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0
    max_duration_ms: float = 0.0

    def record(self, *, duration_ms: float, failed: bool) -> None:
        self.count += 1
        if failed:
            self.error_count += 1
        self.total_duration_ms += duration_ms
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    def snapshot(self) -> dict[str, int | float]:
        average = self.total_duration_ms / self.count if self.count else 0.0
        return {
            "count": self.count,
            "errorCount": self.error_count,
            "averageDurationMs": round(average, 3),
            "maxDurationMs": round(self.max_duration_ms, 3),
        }


class PredictiveRuntimeMetrics:
    def __init__(self) -> None:
        self._endpoint_metrics: dict[str, DurationMetric] = {}
        self._detector_metrics: dict[str, DurationMetric] = {}
        self._lock = threading.Lock()

    def record_endpoint(
        self,
        *,
        endpoint: str,
        duration_ms: float,
        failed: bool,
    ) -> None:
        with self._lock:
            metric = self._endpoint_metrics.setdefault(
                endpoint,
                DurationMetric(),
            )
            metric.record(duration_ms=duration_ms, failed=failed)

    def record_detector(
        self,
        *,
        function_name: str,
        duration_ms: float,
        failed: bool,
    ) -> None:
        with self._lock:
            metric = self._detector_metrics.setdefault(
                function_name,
                DurationMetric(),
            )
            metric.record(duration_ms=duration_ms, failed=failed)

    def snapshot(self) -> tuple[dict[str, dict], dict[str, dict]]:
        with self._lock:
            endpoints = {
                name: metric.snapshot()
                for name, metric in self._endpoint_metrics.items()
            }
            detectors = {
                name: metric.snapshot()
                for name, metric in self._detector_metrics.items()
            }
        return endpoints, detectors


predictive_runtime_metrics = PredictiveRuntimeMetrics()
