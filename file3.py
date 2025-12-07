"""Ferramentas para manipulação simples de pixel art."""

from cli import main
from processing import PixelArtProcessor
from utils import cor_referencia_mais_proxima, obter_vizinhos, pixel_fora_da_tolerancia

__all__ = [
    "main",
    "PixelArtProcessor",
    "cor_referencia_mais_proxima",
    "obter_vizinhos",
    "pixel_fora_da_tolerancia",
]


if __name__ == "__main__":
    main()
