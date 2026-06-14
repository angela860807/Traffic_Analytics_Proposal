from dataclasses import asdict, is_dataclass
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

    def evaluate_rules(
        self,
        request: RuleEvaluationRequest,
    ) -> DetectionEvaluationResponse:
        detector_input = self._build_detector_input(
            "RuleDetectionInput",
            request.model_dump(mode="python"),
        )
        result = self._call_detector("detect_rules", detector_input)
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
        request_payload = request.model_dump(mode="python")
        detector_input = self._build_detector_input(
            "DegradationDetectionInput",
            request_payload,
        )
        result = self._call_detector("detect_degradation", detector_input)
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

        if (
            response.baseline_status != "LEARNING"
            and self._has_detector("predict_anomaly")
        ):
            shadow_result = self._call_optional_detector(
                "predict_anomaly",
                self._build_detector_input(
                    "ModelPredictionInput",
                    request_payload,
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
        artifact_up = self._artifact_status.status in {
            "READY",
            "NOT_CONFIGURED",
        }
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
        if is_dataclass(result):
            return asdict(result)
        if isinstance(result, Mapping):
            return dict(result)
        return result

    def _package_version(self) -> str | None:
        if self._module is None:
            return None
        raw_version = getattr(self._module, "__version__", None)
        return str(raw_version) if raw_version is not None else None


predictive_detector_adapter = PredictiveDetectorAdapter()
