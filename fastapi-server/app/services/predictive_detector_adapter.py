from dataclasses import asdict, is_dataclass
from datetime import datetime
from importlib import import_module
import logging
from pathlib import Path
import time
from types import ModuleType
from typing import Any, Mapping

from pydantic import ValidationError

from app.core.exceptions import DetectorUnavailableError
from app.core.request_context import get_request_id
from app.core.config import (
    PREDICTIVE_ARTIFACT_REQUIRED,
    PREDICTIVE_ARTIFACT_SHA256,
    PREDICTIVE_MODEL_DIR,
)
from app.schemas.predictive_detection import (
    DegradationEvaluationRequest,
    DetectionEvaluationResponse,
    DetectorHealth,
    DetectorHealthResponse,
    RuleEvaluationRequest,
    ShadowPrediction,
)
from app.services.predictive_artifacts import (
    PredictiveArtifactStatus,
    PredictiveArtifactValidator,
)
from app.services.runtime_metrics import predictive_runtime_metrics


logger = logging.getLogger(__name__)


class PredictiveDetectorAdapter:
    def __init__(
        self,
        module: ModuleType | None = None,
        *,
        model_dir: str = PREDICTIVE_MODEL_DIR,
        artifact_required: bool = PREDICTIVE_ARTIFACT_REQUIRED,
        artifact_sha256: Mapping[str, str] = PREDICTIVE_ARTIFACT_SHA256,
    ) -> None:
        self._module = module
        self._import_error: Exception | None = None
        self._model_dir = Path(model_dir)
        self._artifact_validator = PredictiveArtifactValidator(
            model_dir=self._model_dir,
            required=artifact_required,
            expected_sha256=artifact_sha256,
        )
        self._artifact_status = PredictiveArtifactStatus(
            status="NOT_CONFIGURED",
            model_dir=str(self._model_dir),
        )
        self._initialized = False

        if module is None:
            try:
                self._module = import_module("predictive_ml")
            except Exception as exc:
                self._import_error = exc
                logger.warning(
                    "predictive_ml package is unavailable: %s",
                    exc,
                )

    @property
    def available(self) -> bool:
        return self._module is not None and self._import_error is None

    def initialize(self) -> None:
        if self._initialized:
            return

        self._artifact_status = self._artifact_validator.inspect()
        if self.available and self._module is not None:
            load_artifacts = getattr(self._module, "load_artifacts", None)
            if callable(load_artifacts) and self._artifact_status.status == "READY":
                try:
                    load_artifacts(self._model_dir)
                except Exception as exc:
                    self._artifact_status = PredictiveArtifactStatus(
                        status="INVALID",
                        model_dir=str(self._model_dir),
                        feature_schema_version=(
                            self._artifact_status.feature_schema_version
                        ),
                        verified_files=self._artifact_status.verified_files,
                        errors=(f"predictive_ml artifact loading failed: {exc}",),
                    )
                    logger.exception("predictive artifact loading failed")
        self._initialized = True
        logger.info(
            "predictive detector initialized: "
            "packageAvailable=%s packageVersion=%s artifactStatus=%s "
            "featureSchemaVersion=%s verifiedFiles=%s",
            self.available,
            self._package_version(),
            self._artifact_status.status,
            self._artifact_status.feature_schema_version,
            list(self._artifact_status.verified_files),
        )

    def evaluate_rules(
        self,
        request: RuleEvaluationRequest,
    ) -> DetectionEvaluationResponse:
        detector_input = self._build_rule_detector_input(request)
        result = self._call_detector("detect_rules", detector_input)
        response = self._validate_detection_response(
            result,
            fallback_sampled_at=detector_input.sample.sampled_at,
            fallback_evaluated_at=request.evaluated_at,
        )
        self._validate_response_context(
            response=response,
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
        )
        if response.detector.method != "RULE":
            raise DetectorUnavailableError(
                "Rule 평가 결과의 detector method가 RULE이 아닙니다."
            )
        logger.info(
            "predictive rule evaluation completed: "
            "requestId=%s cameraId=%s detector=%s detectorVersion=%s "
            "candidateCount=%s",
            get_request_id(),
            request.camera_id,
            response.detector.name,
            response.detector.version,
            len(response.candidates),
        )
        return response

    def evaluate_degradation(
        self,
        request: DegradationEvaluationRequest,
    ) -> DetectionEvaluationResponse:
        detector_input = self._build_degradation_detector_input(request)
        result = self._call_detector("detect_degradation", detector_input)
        response = self._validate_detection_response(
            result,
            fallback_sampled_at=detector_input.sample.sampled_at,
            fallback_evaluated_at=request.evaluated_at,
        )
        self._validate_response_context(
            response=response,
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
        )
        if response.baseline_status is None:
            raise DetectorUnavailableError(
                "기준선·추세 평가 결과에 baselineStatus가 없습니다."
            )

        if (
            response.baseline_status != "LEARNING"
            and self._is_shadow_artifact_available()
            and self._has_detector("predict_anomaly")
        ):
            shadow_result = self._call_optional_detector(
                "predict_anomaly",
                self._build_detector_input(
                    "ModelPredictionInput",
                    self._build_model_prediction_payload(request),
                ),
            )
            if shadow_result is not None:
                response = response.model_copy(
                    update={
                        "shadow_candidates": self._validate_shadow_predictions(
                            shadow_result
                        )
                    }
                )
                self._validate_response_context(
                    response=response,
                    camera_id=request.camera_id,
                    evaluated_at=request.evaluated_at,
                )

        elif (
            response.baseline_status != "LEARNING"
            and self._artifact_status.status
            in {"NOT_CONFIGURED", "MISSING", "INVALID"}
        ):
            logger.warning(
                "predictive shadow inference skipped due to artifact status: "
                "requestId=%s cameraId=%s artifactStatus=%s errors=%s",
                get_request_id(),
                request.camera_id,
                self._artifact_status.status,
                list(self._artifact_status.errors),
            )

        logger.info(
            "predictive degradation evaluation completed: "
            "requestId=%s cameraId=%s detector=%s detectorVersion=%s "
            "baselineStatus=%s candidateCount=%s shadowCandidateCount=%s",
            get_request_id(),
            request.camera_id,
            response.detector.name,
            response.detector.version,
            response.baseline_status,
            len(response.candidates),
            len(response.shadow_candidates),
        )
        return response

    def get_health(self) -> DetectorHealthResponse:
        self.initialize()
        if not self.available:
            return DetectorHealthResponse(
                status="DEGRADED",
                detectors=[],
                artifact_status=self._artifact_status.status,
                artifact_errors=list(self._artifact_status.errors),
            )

        try:
            raw_manifest = self._call_detector("get_detector_manifest")
            detectors = self._validate_manifest(raw_manifest)
        except DetectorUnavailableError:
            logger.exception("predictive detector manifest is unavailable")
            return DetectorHealthResponse(
                status="DOWN",
                package_version=self._package_version(),
                detectors=[],
                artifact_status=self._artifact_status.status,
                artifact_errors=list(self._artifact_status.errors),
            )

        detector_up = all(item.active for item in detectors)
        artifact_up = (
            self._artifact_status.status == "READY"
            or (
                self._artifact_status.status == "NOT_CONFIGURED"
                and not self._has_detector("predict_anomaly")
            )
        )
        status = "UP" if detector_up and artifact_up else "DEGRADED"
        return DetectorHealthResponse(
            status=status,
            package_version=self._package_version(),
            detectors=detectors,
            artifact_status=self._artifact_status.status,
            artifact_errors=list(self._artifact_status.errors),
        )

    def _build_detector_input(
        self,
        contract_name: str,
        payload: dict[str, Any],
    ) -> Any:
        contract_type = self._find_contract_type(contract_name)
        if contract_type is None:
            raise DetectorUnavailableError(
                f"predictive_ml.{contract_name} 입력 계약을 사용할 수 없습니다."
            )

        try:
            model_validate = getattr(contract_type, "model_validate", None)
            if callable(model_validate):
                return model_validate(payload)
            return contract_type(**payload)
        except Exception as exc:
            raise DetectorUnavailableError(
                f"{contract_name} 입력 변환에 실패했습니다."
            ) from exc

    def _build_rule_detector_input(
        self,
        request: RuleEvaluationRequest,
    ) -> Any:
        sample = self._build_camera_sample(
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
            observation=max(request.samples, key=lambda item: item.sampled_at),
        )
        return self._build_detector_input(
            "RuleDetectionInput",
            {
                "sample": sample,
                "consecutive_windows": self._count_rule_consecutive_windows(
                    request
                ),
            },
        )

    def _build_degradation_detector_input(
        self,
        request: DegradationEvaluationRequest,
    ) -> Any:
        latest_observation = (
            max(request.recent_health_samples, key=lambda item: item.sampled_at)
            if request.recent_health_samples
            else None
        )
        sample = self._build_camera_sample(
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
            observation=latest_observation,
        )
        baseline_metrics = {
            metric_name: self._build_baseline_metric(
                metric,
                sample_count=request.baseline.sample_count,
                baseline_from=request.baseline.from_at,
                baseline_to=request.baseline.to_at,
            )
            for metric_name, metric in request.baseline.metrics.items()
        }
        trend_metric_names = set(baseline_metrics) | {
            "fps_avg",
            "frame_drop_rate",
            "latency_p95_ms",
            "blur_score_avg",
            "ocr_fail_rate",
            "cpu_usage_pct",
            "memory_usage_pct",
            "network_rtt_ms",
        }
        ordered_observations = sorted(
            request.recent_health_samples,
            key=lambda item: item.sampled_at,
        )
        return self._build_detector_input(
            "DegradationDetectionInput",
            {
                "sample": sample,
                "baselines": baseline_metrics,
                "trends": {
                    metric_name: [
                        self._build_trend_point(observation, metric_name)
                        for observation in ordered_observations
                    ]
                    for metric_name in trend_metric_names
                },
                "prediction_horizon_minutes": (
                    request.policy.prediction_horizon_minutes
                ),
            },
        )

    def _build_model_prediction_payload(
        self,
        request: DegradationEvaluationRequest,
    ) -> dict[str, Any]:
        return {
            "camera_id": request.camera_id,
            "sampled_at": request.evaluated_at,
            "sequence": [
                self._build_camera_sample(
                    camera_id=request.camera_id,
                    evaluated_at=request.evaluated_at,
                    observation=observation,
                )
                for observation in sorted(
                    request.recent_health_samples,
                    key=lambda item: item.sampled_at,
                )
            ],
        }

    def _build_camera_sample(
        self,
        *,
        camera_id: int,
        evaluated_at: datetime,
        observation: Any | None,
    ) -> Any:
        contract_type = self._find_contract_type("CameraSample")
        if contract_type is None:
            raise DetectorUnavailableError(
                "predictive_ml.CameraSample 입력 계약을 사용할 수 없습니다."
            )

        sampled_at = observation.sampled_at if observation else evaluated_at
        last_frame_age_seconds = None
        if observation is not None and observation.last_frame_at is not None:
            last_frame_age_seconds = max(
                0.0,
                (evaluated_at - observation.last_frame_at).total_seconds(),
            )

        return contract_type(
            camera_id=camera_id,
            sampled_at=sampled_at,
            fps_avg=getattr(observation, "fps_avg", None),
            frame_drop_rate=getattr(observation, "frame_drop_rate", None),
            latency_p95_ms=getattr(observation, "latency_p95_ms", None),
            blur_score_avg=getattr(observation, "blur_score_avg", None),
            ocr_fail_rate=getattr(observation, "ocr_fail_rate", None),
            cpu_usage_pct=getattr(observation, "cpu_usage_pct", None),
            memory_usage_pct=getattr(observation, "memory_usage_pct", None),
            network_rtt_ms=getattr(observation, "network_rtt_ms", None),
            last_frame_age_seconds=last_frame_age_seconds,
            ocr_attempt_count=getattr(observation, "ocr_attempt_count", None),
            quality_status=getattr(observation, "quality_status", "COMPLETE"),
            is_imputed=getattr(observation, "is_imputed", False),
        )

    def _build_baseline_metric(
        self,
        metric: Any,
        *,
        sample_count: int,
        baseline_from: datetime,
        baseline_to: datetime,
    ) -> Any:
        contract_type = self._find_contract_type("BaselineMetric")
        if contract_type is None:
            raise DetectorUnavailableError(
                "predictive_ml.BaselineMetric 입력 계약을 사용할 수 없습니다."
            )
        return contract_type(
            median=metric.median,
            mad=metric.mad,
            sample_count=sample_count,
            baseline_from=baseline_from,
            baseline_to=baseline_to,
        )

    def _build_trend_point(
        self,
        observation: Any,
        metric_name: str,
    ) -> Any:
        contract_type = self._find_contract_type("TrendPoint")
        if contract_type is None:
            raise DetectorUnavailableError(
                "predictive_ml.TrendPoint 입력 계약을 사용할 수 없습니다."
            )
        return contract_type(
            sampled_at=observation.sampled_at,
            value=getattr(observation, metric_name, None),
            quality_status=observation.quality_status,
            is_imputed=observation.is_imputed,
        )

    def _find_contract_type(self, contract_name: str) -> Any | None:
        if not self.available or self._module is None:
            raise DetectorUnavailableError()

        contract_type = getattr(self._module, contract_name, None)
        if contract_type is not None:
            return contract_type

        contracts_module = getattr(self._module, "contracts", None)
        if contracts_module is None:
            try:
                contracts_module = import_module("predictive_ml.contracts")
            except Exception:
                return None
        return getattr(contracts_module, contract_name, None)

    def _has_detector(self, function_name: str) -> bool:
        return (
            self.available
            and self._module is not None
            and callable(getattr(self._module, function_name, None))
        )

    def _is_shadow_artifact_available(self) -> bool:
        self.initialize()
        return self._artifact_status.status == "READY"

    def _call_detector(self, function_name: str, request: Any = None) -> Any:
        if not self.available or self._module is None:
            raise DetectorUnavailableError()

        function = getattr(self._module, function_name, None)
        if function is None or not callable(function):
            raise DetectorUnavailableError(
                f"predictive_ml.{function_name} 함수를 사용할 수 없습니다."
            )

        started_at = time.perf_counter()
        failed = False
        try:
            if request is None:
                return function()
            return function(request)
        except DetectorUnavailableError:
            failed = True
            raise
        except Exception as exc:
            failed = True
            logger.exception(
                "predictive detector call failed: function=%s",
                function_name,
            )
            raise DetectorUnavailableError() from exc
        finally:
            predictive_runtime_metrics.record_detector(
                function_name=function_name,
                duration_ms=(time.perf_counter() - started_at) * 1000,
                failed=failed,
            )

    def _call_optional_detector(
        self,
        function_name: str,
        request: Any,
    ) -> Any | None:
        if not self.available or self._module is None or request is None:
            return None

        function = getattr(self._module, function_name, None)
        if function is None or not callable(function):
            return None

        started_at = time.perf_counter()
        failed = False
        try:
            return function(request)
        except Exception as exc:
            failed = True
            logger.exception(
                "optional predictive detector call failed: function=%s",
                function_name,
            )
            raise DetectorUnavailableError() from exc
        finally:
            predictive_runtime_metrics.record_detector(
                function_name=function_name,
                duration_ms=(time.perf_counter() - started_at) * 1000,
                failed=failed,
            )

    def _validate_detection_response(
        self,
        result: Any,
        *,
        fallback_sampled_at: datetime,
        fallback_evaluated_at: datetime,
    ) -> DetectionEvaluationResponse:
        try:
            return DetectionEvaluationResponse.model_validate(
                self._to_detection_response_value(
                    result,
                    fallback_sampled_at=fallback_sampled_at,
                    fallback_evaluated_at=fallback_evaluated_at,
                )
            )
        except ValidationError as exc:
            raise DetectorUnavailableError(
                "AI 탐지 결과가 FastAPI 응답 계약과 일치하지 않습니다."
            ) from exc

    def _validate_shadow_predictions(
        self,
        result: Any,
    ) -> list[ShadowPrediction]:
        raw_value = self._to_shadow_validation_value(result)
        if isinstance(raw_value, dict) and "shadowCandidates" in raw_value:
            raw_value = raw_value["shadowCandidates"]
        elif isinstance(raw_value, dict) and "shadow_candidates" in raw_value:
            raw_value = raw_value["shadow_candidates"]
        elif not isinstance(raw_value, list):
            raw_value = [raw_value]

        try:
            return [
                ShadowPrediction.model_validate(item)
                for item in raw_value
                if _shadow_prediction_has_required_scores(item)
            ]
        except ValidationError as exc:
            raise DetectorUnavailableError(
                "SHADOW 모델 결과가 FastAPI 응답 계약과 일치하지 않습니다."
            ) from exc

    def _validate_manifest(self, result: Any) -> list[DetectorHealth]:
        raw_value = self._to_validation_value(result)
        if isinstance(raw_value, dict) and "detectors" in raw_value:
            raw_value = raw_value["detectors"]
        elif not isinstance(raw_value, list):
            raw_value = [raw_value]

        try:
            return [DetectorHealth.model_validate(item) for item in raw_value]
        except ValidationError as exc:
            raise DetectorUnavailableError(
                "AI detector manifest가 health 계약과 일치하지 않습니다."
            ) from exc

    @staticmethod
    def _validate_response_context(
        *,
        response: DetectionEvaluationResponse,
        camera_id: int,
        evaluated_at: Any,
    ) -> None:
        if response.evaluated_at != evaluated_at:
            raise DetectorUnavailableError(
                "AI 탐지 결과의 evaluatedAt이 요청과 일치하지 않습니다."
            )

        response_camera_ids = {
            candidate.camera_id
            for candidate in response.candidates
        } | {
            candidate.camera_id
            for candidate in response.shadow_candidates
        }
        if response_camera_ids.difference({camera_id}):
            raise DetectorUnavailableError(
                "AI 탐지 결과의 cameraId가 요청과 일치하지 않습니다."
            )

    @staticmethod
    def _to_validation_value(result: Any) -> Any:
        if hasattr(result, "model_dump"):
            return result.model_dump(by_alias=True, mode="python")
        if is_dataclass(result):
            return asdict(result)
        if isinstance(result, Mapping):
            return dict(result)
        return result

    def _to_detection_response_value(
        self,
        result: Any,
        *,
        fallback_sampled_at: datetime,
        fallback_evaluated_at: datetime,
    ) -> Any:
        if isinstance(result, Mapping) and "detector" in result:
            return dict(result)
        if not hasattr(result, "detector") or not hasattr(result, "candidates"):
            return self._to_validation_value(result)

        detector = result.detector
        return {
            "detector": {
                "name": detector.name,
                "version": detector.version,
                "method": detector.method,
            },
            "evaluatedAt": fallback_evaluated_at,
            "baselineStatus": getattr(result, "baseline_status", None),
            "requiredSampleCount": getattr(
                result,
                "required_sample_count",
                None,
            ),
            "currentSampleCount": getattr(
                result,
                "current_sample_count",
                None,
            ),
            "candidates": [
                self._to_candidate_value(
                    result.camera_id,
                    candidate,
                    fallback_sampled_at=fallback_sampled_at,
                )
                for candidate in result.candidates
                if getattr(candidate, "severity", None)
                in {"WARNING", "CRITICAL"}
            ],
            "shadowCandidates": [],
        }

    @staticmethod
    def _to_candidate_value(
        camera_id: int,
        candidate: Any,
        *,
        fallback_sampled_at: datetime,
    ) -> dict[str, Any]:
        trend = None
        if (
            getattr(candidate, "trend_slope", None) is not None
            or getattr(candidate, "trend_confidence", None) is not None
            or getattr(candidate, "projected_threshold_crossing_at", None)
            is not None
        ):
            trend = {
                "slope": getattr(candidate, "trend_slope", 0.0) or 0.0,
                "confidence": (
                    getattr(candidate, "trend_confidence", 0.0) or 0.0
                ),
                "predictionHorizonMinutes": 10,
                "projectedThresholdCrossingAt": getattr(
                    candidate,
                    "projected_threshold_crossing_at",
                    None,
                ),
            }

        return {
            "targetType": "CAMERA",
            "cameraId": camera_id,
            "anomalyType": candidate.anomaly_type,
            "severity": candidate.severity,
            "anomalyScore": candidate.anomaly_score or 0.0,
            "policyCode": candidate.policy_code,
            "trend": trend,
            "suspectedCauses": list(candidate.suspected_causes or []),
            "evidence": [
                {
                    "metricName": evidence.metric_name,
                    "observedValue": evidence.observed_value,
                    "baselineValue": evidence.baseline_value,
                    "thresholdValue": evidence.threshold_value,
                    "metricScore": evidence.metric_score,
                    "unit": evidence.unit,
                    "sampledAt": getattr(
                        evidence,
                        "sampled_at",
                        fallback_sampled_at,
                    ),
                    "context": dict(evidence.context or {}),
                }
                for evidence in candidate.evidence
            ],
        }

    def _to_shadow_validation_value(self, result: Any) -> Any:
        raw_value = self._to_validation_value(result)
        if isinstance(raw_value, list):
            return [self._to_shadow_prediction_value(item) for item in raw_value]
        return self._to_shadow_prediction_value(raw_value)

    @staticmethod
    def _to_shadow_prediction_value(item: Any) -> Any:
        if isinstance(item, Mapping):
            if "camera_id" in item:
                return {
                    "targetType": item.get("target_type", "CAMERA"),
                    "cameraId": item["camera_id"],
                    "detectionMethod": item.get(
                        "detection_method",
                        "LSTM_AUTOENCODER",
                    ),
                    "operatingMode": item.get("operating_mode", "SHADOW"),
                    "anomalyScore": item.get("anomaly_score"),
                    "warningThreshold": item.get("warning_threshold"),
                    "criticalThreshold": item.get("critical_threshold"),
                    "predictedAnomaly": item.get("predicted_anomaly", False),
                    "predictedSeverity": item.get("predicted_severity"),
                    "inputWindowFrom": item.get("input_window_from"),
                    "inputWindowTo": item.get("input_window_to"),
                    "featureSchemaVersion": item.get(
                        "feature_schema_version"
                    ),
                    "topFeatures": [
                        {
                            "featureName": feature.get("feature_name"),
                            "featureValue": feature.get("feature_value"),
                        }
                        if isinstance(feature, Mapping)
                        else feature
                        for feature in item.get("top_features", [])
                    ],
                }
            return item
        if not hasattr(item, "camera_id"):
            return item
        return {
            "targetType": getattr(item, "target_type", "CAMERA"),
            "cameraId": item.camera_id,
            "detectionMethod": getattr(
                item,
                "detection_method",
                "LSTM_AUTOENCODER",
            ),
            "operatingMode": getattr(item, "operating_mode", "SHADOW"),
            "anomalyScore": item.anomaly_score,
            "warningThreshold": item.warning_threshold,
            "criticalThreshold": item.critical_threshold,
            "predictedAnomaly": item.predicted_anomaly,
            "predictedSeverity": item.predicted_severity,
            "inputWindowFrom": item.input_window_from,
            "inputWindowTo": item.input_window_to,
            "featureSchemaVersion": item.feature_schema_version,
            "topFeatures": [
                {
                    "featureName": feature.feature_name,
                    "featureValue": feature.feature_value,
                }
                for feature in item.top_features
            ],
        }

    @staticmethod
    def _count_rule_consecutive_windows(
        request: RuleEvaluationRequest,
    ) -> dict[str, int]:
        policies_by_metric = {
            metric_name: policy
            for policy in request.policies
            for metric_name in _metrics_for_policy_code(policy.policy_code)
        }
        ordered_samples = sorted(
            request.samples,
            key=lambda item: item.sampled_at,
            reverse=True,
        )
        consecutive_windows: dict[str, int] = {}
        for metric_name, policy in policies_by_metric.items():
            threshold = policy.warning_threshold
            if threshold is None:
                threshold = policy.critical_threshold
            if threshold is None:
                consecutive_windows[metric_name] = len(ordered_samples)
                continue

            count = 0
            for sample in ordered_samples:
                value = getattr(sample, metric_name, None)
                if value is None:
                    break
                if _is_policy_threshold_violated(
                    policy.policy_code,
                    metric_name,
                    float(value),
                    float(threshold),
                ):
                    count += 1
                    continue
                break
            consecutive_windows[metric_name] = count
        return consecutive_windows

    def _package_version(self) -> str | None:
        if self._module is None:
            return None
        raw_version = getattr(self._module, "__version__", None)
        return str(raw_version) if raw_version is not None else None


def _metrics_for_policy_code(policy_code: str) -> tuple[str, ...]:
    if policy_code == "CAMERA_OFFLINE_RULE_V1":
        return ("last_frame_age_seconds",)
    if policy_code == "FPS_DEGRADATION_RULE_V1":
        return ("fps_avg",)
    if policy_code == "FRAME_DROP_DEGRADATION_RULE_V1":
        return ("frame_drop_rate",)
    if policy_code == "LATENCY_DEGRADATION_RULE_V1":
        return ("latency_p95_ms",)
    if policy_code == "BLUR_DEGRADATION_RULE_V1":
        return ("blur_score_avg",)
    if policy_code == "OCR_QUALITY_DEGRADATION_RULE_V1":
        return ("ocr_fail_rate",)
    if policy_code == "RESOURCE_SATURATION_RULE_V1":
        return ("cpu_usage_pct", "memory_usage_pct")
    if policy_code == "NETWORK_INSTABILITY_RULE_V1":
        return ("network_rtt_ms", "last_frame_age_seconds")
    return ()


def _is_policy_threshold_violated(
    policy_code: str,
    metric_name: str,
    value: float,
    threshold: float,
) -> bool:
    if policy_code == "FPS_DEGRADATION_RULE_V1":
        return value < threshold
    if metric_name == "last_frame_age_seconds":
        return value > threshold
    return value > threshold


def _shadow_prediction_has_required_scores(item: Mapping[str, Any]) -> bool:
    return (
        item.get("anomalyScore", item.get("anomaly_score")) is not None
        and item.get("warningThreshold", item.get("warning_threshold"))
        is not None
        and item.get("criticalThreshold", item.get("critical_threshold"))
        is not None
    )


predictive_detector_adapter = PredictiveDetectorAdapter()
