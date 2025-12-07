"""Funções utilitárias para manipulação de pixel art."""

from typing import List, Tuple

import numpy as np


def pixel_fora_da_tolerancia(
    pixel_atual: Tuple[int, int, int],
    cores_referencia: List[Tuple[int, int, int]],
    tolerancia: int,
) -> bool:
    """Indica se o pixel está fora da tolerância das cores de referência."""

    return not any(
        all(abs(c1 - c2) <= tolerancia for c1, c2 in zip(pixel_atual, ref))
        for ref in cores_referencia
    )


def obter_vizinhos(
    arr: np.ndarray,
    x: int,
    y: int,
) -> List[Tuple[int, int, int]]:
    """Retorna a vizinhança 8 de um pixel em formato de lista RGB."""

    altura, largura, _ = arr.shape
    vizinhos: List[Tuple[int, int, int]] = []
    for delta_y in [-1, 0, 1]:
        for delta_x in [-1, 0, 1]:
            if delta_y == 0 and delta_x == 0:
                continue

            novo_y, novo_x = y + delta_y, x + delta_x
            if 0 <= novo_y < altura and 0 <= novo_x < largura:
                vizinhos.append(tuple(arr[novo_y, novo_x]))

    return vizinhos


def cor_referencia_mais_proxima(
    cor_base: Tuple[int, int, int],
    cores_referencia: List[Tuple[int, int, int]],
) -> Tuple[int, int, int]:
    """Escolhe a cor de referência mais próxima da cor base."""

    def distancia_cor(
        cor1: Tuple[int, int, int],
        cor2: Tuple[int, int, int],
    ) -> float:
        diferenca_quadrada = sum(
            (cor1_valor - cor2_valor) ** 2
            for cor1_valor, cor2_valor in zip(cor1, cor2)
        )
        return float(np.sqrt(diferenca_quadrada))

    distancias: List[float] = [
        distancia_cor(cor_base, referencia) for referencia in cores_referencia
    ]
    indice_menor_distancia = int(np.argmin(distancias))

    return cores_referencia[indice_menor_distancia]
