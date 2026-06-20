from dataclasses import dataclass

from app.detection.priority import normalize_class_name
from app.guidance.accessibility_rules import get_accessibility_class


@dataclass(frozen=True)
class ClassInfo:
    canonical_name: str
    label_pt: str
    gender: str
    semantic_group: str
    base_score: float


CLASS_GROUPS: dict[str, ClassInfo] = {
    "door": ClassInfo("porta", "porta", "f", "ponto_interesse", 100),
    "porta": ClassInfo("porta", "porta", "f", "ponto_interesse", 100),
    "doorway": ClassInfo("passagem", "passagem", "f", "ponto_interesse", 94),
    "corridor": ClassInfo("corredor", "corredor", "m", "ponto_interesse", 92),
    "corredor": ClassInfo("corredor", "corredor", "m", "ponto_interesse", 92),
    "hallway": ClassInfo("corredor", "corredor", "m", "ponto_interesse", 92),
    "stairs": ClassInfo("escada", "escada", "f", "ponto_interesse", 96),
    "stair": ClassInfo("escada", "escada", "f", "ponto_interesse", 96),
    "downstair": ClassInfo("escada", "escada", "f", "ponto_interesse", 96),
    "upstair": ClassInfo("escada", "escada", "f", "ponto_interesse", 96),
    "escada": ClassInfo("escada", "escada", "f", "ponto_interesse", 96),
    "elevator": ClassInfo("elevador", "elevador", "m", "ponto_interesse", 90),
    "elevador": ClassInfo("elevador", "elevador", "m", "ponto_interesse", 90),
    "reception": ClassInfo("recepcao", "recepcao", "f", "ponto_interesse", 86),
    "recepcao": ClassInfo("recepcao", "recepcao", "f", "ponto_interesse", 86),
    "recepção": ClassInfo("recepcao", "recepcao", "f", "ponto_interesse", 86),
    "passage": ClassInfo("passagem", "passagem", "f", "ponto_interesse", 94),
    "passagem": ClassInfo("passagem", "passagem", "f", "ponto_interesse", 94),
    "entrance": ClassInfo("entrada", "entrada", "f", "ponto_interesse", 88),
    "entrada": ClassInfo("entrada", "entrada", "f", "ponto_interesse", 88),
    "exit": ClassInfo("saida", "saida", "f", "ponto_interesse", 88),
    "saida": ClassInfo("saida", "saida", "f", "ponto_interesse", 88),
    "saída": ClassInfo("saida", "saida", "f", "ponto_interesse", 88),
    "ramp": ClassInfo("rampa", "rampa", "f", "acessibilidade", 98),
    "rampa": ClassInfo("rampa", "rampa", "f", "acessibilidade", 98),
    "curb ramp": ClassInfo("rampa de acesso", "rampa de acesso", "f", "acessibilidade", 98),
    "handrail": ClassInfo("corrimao", "corrimao", "m", "acessibilidade", 92),
    "corrimao": ClassInfo("corrimao", "corrimao", "m", "acessibilidade", 92),
    "corrimão": ClassInfo("corrimao", "corrimao", "m", "acessibilidade", 92),
    "tactile paving": ClassInfo("piso tatil", "piso tatil", "m", "acessibilidade", 94),
    "piso tatil": ClassInfo("piso tatil", "piso tatil", "m", "acessibilidade", 94),
    "piso tátil": ClassInfo("piso tatil", "piso tatil", "m", "acessibilidade", 94),
    "accessibility sign": ClassInfo("sinalizacao de acessibilidade", "sinalizacao de acessibilidade", "f", "acessibilidade", 88),
    "sinalizacao de acessibilidade": ClassInfo("sinalizacao de acessibilidade", "sinalizacao de acessibilidade", "f", "acessibilidade", 88),
    "sinalização de acessibilidade": ClassInfo("sinalizacao de acessibilidade", "sinalizacao de acessibilidade", "f", "acessibilidade", 88),
    "wheelchair ramp": ClassInfo("rampa acessivel", "rampa acessivel", "f", "acessibilidade", 100),
    "rampa acessivel": ClassInfo("rampa acessivel", "rampa acessivel", "f", "acessibilidade", 100),
    "rampa acessível": ClassInfo("rampa acessivel", "rampa acessivel", "f", "acessibilidade", 100),
    "accessible route": ClassInfo("rota acessivel", "rota acessivel", "f", "acessibilidade", 96),
    "rota acessivel": ClassInfo("rota acessivel", "rota acessivel", "f", "acessibilidade", 96),
    "rota acessível": ClassInfo("rota acessivel", "rota acessivel", "f", "acessibilidade", 96),
    "person": ClassInfo("pessoa", "pessoa", "f", "pessoa", 58),
    "pessoa": ClassInfo("pessoa", "pessoa", "f", "pessoa", 58),
    "chair": ClassInfo("cadeira", "cadeira", "f", "obstaculo", 56),
    "cadeira": ClassInfo("cadeira", "cadeira", "f", "obstaculo", 56),
    "table": ClassInfo("mesa", "mesa", "f", "obstaculo", 54),
    "mesa": ClassInfo("mesa", "mesa", "f", "obstaculo", 54),
    "dining table": ClassInfo("mesa", "mesa", "f", "obstaculo", 54),
    "obstacle": ClassInfo("obstaculo", "obstaculo", "m", "obstaculo", 68),
    "objects": ClassInfo("obstaculo", "obstaculo", "m", "obstaculo", 68),
    "obstaculo": ClassInfo("obstaculo", "obstaculo", "m", "obstaculo", 68),
    "obstáculo": ClassInfo("obstaculo", "obstaculo", "m", "obstaculo", 68),
    "wall": ClassInfo("parede", "parede", "f", "obstaculo", 50),
    "parede": ClassInfo("parede", "parede", "f", "obstaculo", 50),
    "step": ClassInfo("degrau", "degrau", "m", "obstaculo", 86),
    "degrau": ClassInfo("degrau", "degrau", "m", "obstaculo", 86),
    "column": ClassInfo("coluna", "coluna", "f", "obstaculo", 62),
    "coluna": ClassInfo("coluna", "coluna", "f", "obstaculo", 62),
    "backpack": ClassInfo("mochila", "mochila", "f", "baixa_prioridade", 8),
    "mochila": ClassInfo("mochila", "mochila", "f", "baixa_prioridade", 8),
    "handbag": ClassInfo("bolsa", "bolsa", "f", "baixa_prioridade", 8),
    "bolsa": ClassInfo("bolsa", "bolsa", "f", "baixa_prioridade", 8),
    "suitcase": ClassInfo("mala", "mala", "f", "baixa_prioridade", 10),
    "mala": ClassInfo("mala", "mala", "f", "baixa_prioridade", 10),
    "bottle": ClassInfo("garrafa", "garrafa", "f", "baixa_prioridade", 4),
    "garrafa": ClassInfo("garrafa", "garrafa", "f", "baixa_prioridade", 4),
    "cell phone": ClassInfo("celular", "celular", "m", "baixa_prioridade", 3),
    "celular": ClassInfo("celular", "celular", "m", "baixa_prioridade", 3),
    "laptop": ClassInfo("notebook", "notebook", "m", "baixa_prioridade", 6),
    "notebook": ClassInfo("notebook", "notebook", "m", "baixa_prioridade", 6),
    "cup": ClassInfo("copo", "copo", "m", "baixa_prioridade", 4),
    "copo": ClassInfo("copo", "copo", "m", "baixa_prioridade", 4),
    "book": ClassInfo("livro", "livro", "m", "baixa_prioridade", 4),
    "livro": ClassInfo("livro", "livro", "m", "baixa_prioridade", 4),
}

DEFAULT_CLASS_INFO = ClassInfo("objeto", "objeto", "m", "contexto", 0)


def map_class(class_name: str) -> ClassInfo:
    accessibility_class = get_accessibility_class(class_name)
    if accessibility_class is not None:
        return ClassInfo(
            canonical_name=accessibility_class.canonical_name,
            label_pt=accessibility_class.label_pt,
            gender=accessibility_class.gender,
            semantic_group="acessibilidade",
            base_score=accessibility_class.base_score,
        )

    return CLASS_GROUPS.get(normalize_class_name(class_name), DEFAULT_CLASS_INFO)
