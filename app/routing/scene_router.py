from app.config import (
    ENABLE_CLASSIC_TACTILE,
    ENABLE_OCR,
    ENABLE_SEMANTIC_SEGMENTATION,
    ENABLE_TACTILE_SPECIALIST,
)
from app.detection.priority import normalize_class_name
from app.routing.detection_plan import DetectionPlan, GeneralistFinding


FAST_MODE = "fast"
POI_MODE = "poi"
TACTILE_MODE = "tactile"
AUTO_MODE = "auto"
EXPLORATION_ALIAS = "exploration"
NAVIGATION_ALIAS = "navigation"

ROUTED_MODES = {FAST_MODE, POI_MODE, TACTILE_MODE, AUTO_MODE, EXPLORATION_ALIAS, NAVIGATION_ALIAS}


class SceneRouter:
    """Monta um plano simples para nao rodar todos os modelos em todo frame."""

    def build_plan(
        self,
        mode: str,
        target_class: str | None = None,
        findings: list[GeneralistFinding] | None = None,
        use_open_vocab: bool = False,
        use_semantic_segmentation: bool = False,
        use_tactile_specialist: bool = False,
        use_classic_tactile: bool = False,
        use_ocr: bool = False,
    ) -> DetectionPlan:
        normalized_mode = _normalize_mode(mode)
        plan = DetectionPlan(
            mode=normalized_mode,
            target_class=target_class,
            use_default_yolo=True,
            use_local_navigation=bool(target_class) or mode == NAVIGATION_ALIAS,
        )

        if normalized_mode == FAST_MODE:
            plan.use_open_vocab = use_open_vocab
            plan.use_semantic_segmentation = use_semantic_segmentation
            plan.use_tactile_specialist = use_tactile_specialist
            plan.use_classic_tactile = use_classic_tactile
            plan.use_ocr = use_ocr
            plan.reason.append("Modo fast: somente YOLO padrao e profundidade.")
            return plan

        if normalized_mode == POI_MODE:
            plan.use_open_vocab = True
            plan.use_semantic_segmentation = use_semantic_segmentation or ENABLE_SEMANTIC_SEGMENTATION
            plan.reason.append("Modo poi: ativa generalista para pontos de interesse.")
        elif normalized_mode == TACTILE_MODE:
            plan.use_open_vocab = True
            plan.use_tactile_specialist = use_tactile_specialist or ENABLE_TACTILE_SPECIALIST
            plan.use_classic_tactile = use_classic_tactile or ENABLE_CLASSIC_TACTILE
            plan.reason.append("Modo tactile: foca em piso tatil e acessibilidade.")
        else:
            plan.use_open_vocab = use_open_vocab or bool(target_class)
            plan.use_semantic_segmentation = use_semantic_segmentation or ENABLE_SEMANTIC_SEGMENTATION
            plan.reason.append("Modo auto: roteia especialistas conforme alvo ou indicios.")

        plan.use_ocr = use_ocr or ENABLE_OCR
        plan = _apply_target_rules(plan, target_class)
        plan = _apply_findings_rules(plan, findings or [])
        return plan


def _normalize_mode(mode: str) -> str:
    if mode == EXPLORATION_ALIAS:
        return FAST_MODE
    if mode == NAVIGATION_ALIAS:
        return AUTO_MODE
    if mode in ROUTED_MODES:
        return mode
    return AUTO_MODE


def _apply_target_rules(plan: DetectionPlan, target_class: str | None) -> DetectionPlan:
    if not target_class:
        return plan

    target = normalize_class_name(target_class)
    plan.target_classes.append(target)
    plan.use_open_vocab = True
    if target in {"door", "porta", "entrance", "exit"}:
        plan.target_classes.extend(["door", "elevator door", "entrance", "exit"])
        plan.reason.append("Alvo de porta/entrada ativa open-vocabulary focado.")
    if target in {"elevator", "elevador"}:
        plan.target_classes.extend(["elevator", "elevator door"])
        plan.use_ocr = True
        plan.reason.append("Alvo elevador ativa OCR opcional para placas.")
    if target in {"stairs", "stair", "escada", "degrau"}:
        plan.target_classes.extend(["stairs", "staircase"])
        plan.use_stair_ramp_heuristics = True
        plan.reason.append("Alvo escada ativa heuristicas de linhas/degraus.")
    if target in {"tactile paving", "piso tatil"}:
        plan.use_tactile_specialist = True
        plan.use_classic_tactile = True
        plan.reason.append("Alvo piso tatil ativa especialistas/fallback OpenCV.")
    if target in {"ramp", "rampa", "wheelchair ramp"}:
        plan.target_classes.extend(["ramp", "accessibility ramp", "wheelchair ramp"])
        plan.use_stair_ramp_heuristics = True
        plan.reason.append("Alvo rampa ativa open-vocabulary e heuristicas.")
    return _dedupe_plan_lists(plan)


def _apply_findings_rules(plan: DetectionPlan, findings: list[GeneralistFinding]) -> DetectionPlan:
    for finding in findings:
        name = normalize_class_name(finding.class_name)
        plan.poi_candidates.append(name)
        if name in {"door", "elevator door", "entrance", "exit"}:
            plan.use_open_vocab = True
            plan.target_classes.extend(["door", "elevator door", "entrance", "exit"])
            plan.reason.append("Indicio de porta/entrada encontrado.")
        elif name in {"elevator"}:
            plan.use_open_vocab = True
            plan.use_ocr = True
            plan.target_classes.extend(["elevator", "elevator door"])
            plan.reason.append("Indicio de elevador encontrado.")
        elif name in {"stairs", "staircase", "stair"}:
            plan.use_open_vocab = True
            plan.use_semantic_segmentation = True
            plan.use_stair_ramp_heuristics = True
            plan.reason.append("Indicio de escada encontrado.")
        elif name in {"reception desk", "reception area", "front desk", "reception"}:
            plan.use_open_vocab = True
            plan.use_ocr = True
            plan.target_classes.extend(["reception desk", "reception area", "front desk"])
            plan.reason.append("Indicio de recepcao encontrado.")
        elif name in {"tactile paving", "tactile floor", "guiding block", "warning block"}:
            plan.use_tactile_specialist = True
            plan.use_classic_tactile = True
            plan.reason.append("Indicio de piso tatil encontrado.")
        elif name in {"ramp", "accessibility ramp", "wheelchair ramp"}:
            plan.use_open_vocab = True
            plan.use_semantic_segmentation = True
            plan.use_stair_ramp_heuristics = True
            plan.reason.append("Indicio de rampa encontrado.")
    return _dedupe_plan_lists(plan)


def _dedupe_plan_lists(plan: DetectionPlan) -> DetectionPlan:
    plan.target_classes = list(dict.fromkeys(plan.target_classes))
    plan.poi_candidates = list(dict.fromkeys(plan.poi_candidates))
    plan.reason = list(dict.fromkeys(plan.reason))
    return plan
