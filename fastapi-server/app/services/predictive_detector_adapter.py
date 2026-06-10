from importlib import import_module
import logging
from types import ModuleType
from typing import Any

from pydantic import ValidationError

from app.core.exceptions import DetectorUnavailableError
from app.schemas.predictive_detection import (
    DegradationEvaluationRequest,
    DetectionEvaluationResponse,
    DetectorHealth,
    DetectorHealthResponse,
    RuleEvaluationRequest,
    ShadowPrediction,
)


logger = logging.getLogger(__name__)


class PredictiveDetectorAdapter:
    def __init__(self, module: ModuleType | None = None) -> None:
        self._module = module
        self._import_error: Exception | None = None

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

    def evaluate_rules(
        self,
        request: RuleEvaluationRequest,
    ) -> DetectionEvaluationResponse:
        result = self._call_detector("detect_rules", request)
        response = self._validate_detection_response(result)
        self._validate_response_context(
            response=response,
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
        )
        if response.detector.method != "RULE":
            raise DetectorUnavailableError(
                "Rule 평가 결과의 detector method가 RULE이 아닙니다."
            )
        return response

    def evaluate_degradation(
        self,
        request: DegradationEvaluationRequest,
    ) -> DetectionEvaluationResponse:
        result = self._call_detector("detect_degradation", request)
        response = self._validate_detection_response(result)
        self._validate_response_context(
            response=response,
            camera_id=request.camera_id,
            evaluated_at=request.evaluated_at,
        )
        if response.baseline_status is None:
            raise DetectorUnavailableError(
                "기준선·추세 평가 결과에 baselineStatus가 없습니다."
            )

        if response.baseline_status != "LEARNING":
            shadow_result = self._call_optional_detector(
                "predict_anomaly",
                request,
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

        return response

    def get_health(self) -> DetectorHealthResponse:
        if not self.available:
            return DetectorHealthResponse(status="DEGRADED", detectors=[])

        try:
            raw_manifest = self._call_detector("get_detector_manifest")
            detectors = self._validate_manifest(raw_manifest)
        except DetectorUnavailableError:
            logger.exception("predictive detector manifest is unavailable")
            return DetectorHealthResponse(status="DOWN", detectors=[])

        status = "UP" if all(item.active for item in detectors) else "DEGRADED"
        return DetectorHealthResponse(status=status, detectors=detectors)

    def _call_detector(self, function_name: str, request: Any = None) -> Any:
        if not self.available or self._module is None:
            raise DetectorUnavailableError()

        function = getattr(self._module, function_name, None)
        if function is None or not callable(function):
            raise DetectorUnavailableError(
                f"predictive_ml.{function_name} 함수를 사용할 수 없습니다."
            )

        try:
            if request is None:
                return function()
            return function(request)
        except DetectorUnavailableError:
            raise
        except Exception as exc:
            logger.exception(
                "predictive detector call failed: function=%s",
                function_name,
            )
            raise DetectorUnavailableError() from exc

    def _call_optional_detector(
        self,
        function_name: str,
        request: Any,
    ) -> Any | None:
        if not self.available or self._module is None:
            return None

        function = getattr(self._module, function_name, None)
        if function is None or not callable(function):
            return None

        try:
            return function(request)
        except Exception as exc:
            logger.exception(
                "optional predictive detector call failed: function=%s",
                function_name,
            )
            raise DetectorUnavailableError() from exc

    def _validate_detection_response(
        self,
        result: Any,
    ) -> DetectionEvaluationResponse:
        try:
            return DetectionEvaluationResponse.model_validate(
                self._to_validation_value(result)
            )
        except ValidationError as exc:
            raise DetectorUnavailableError(
                "AI 탐지 결과가 FastAPI 응답 계약과 일치하지 않습니다."
            ) from exc

    def _validate_shadow_predictions(
        self,
        result: Any,
    ) -> list[ShadowPrediction]:
        raw_value = self._to_validation_value(result)
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
        return result


predictive_detector_adapter = PredictiveDetectorAdapter()
