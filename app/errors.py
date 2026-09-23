class ArgusRuntimeError(RuntimeError):
    """Erro operacional esperado do backend ARGUS."""

    code = "INFERENCE_FAILED"
    status_code = 500

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.code)
        self.message = message or self.code


class ModelNotReadyError(ArgusRuntimeError):
    code = "MODEL_NOT_READY"
    status_code = 503


class DepthUnavailableError(ArgusRuntimeError):
    code = "DEPTH_UNAVAILABLE"
    status_code = 503


class TargetDetectorUnavailableError(ArgusRuntimeError):
    code = "TARGET_DETECTOR_UNAVAILABLE"
    status_code = 503


class BackendBusyError(ArgusRuntimeError):
    code = "BACKEND_BUSY"
    status_code = 429
