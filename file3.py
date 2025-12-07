"""Ferramentas para manipulação simples de pixel art."""

from cli import main
from processing import (
    ampliar,
    aproximar_cores,
    calcular_blocos,
    detectar_tamanho,
    pixelizar,
    reduzir,
    verificar_cores,
)
from utils import cor_referencia_mais_proxima, obter_vizinhos, pixel_fora_da_tolerancia

__all__ = [
    "main",
    "ampliar",
    "aproximar_cores",
    "calcular_blocos",
    "detectar_tamanho",
    "pixelizar",
    "reduzir",
    "verificar_cores",
    "cor_referencia_mais_proxima",
    "obter_vizinhos",
    "pixel_fora_da_tolerancia",
]


if __name__ == "__main__":
    main()
