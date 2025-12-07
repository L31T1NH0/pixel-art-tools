"""Ferramentas para manipulação simples de pixel art."""

from typing import Dict, List, Tuple

import numpy as np
from PIL import Image


def calcular_blocos(img: Image.Image) -> Tuple[int, int, int]:
    """Retorna a largura, altura e tamanho médio dos blocos de pixel art."""

    arr: np.ndarray = np.array(img)
    bloco_largura: int = detectar_tamanho(arr, 1)
    bloco_altura: int = detectar_tamanho(arr, 0)
    bloco_tamanho: int = int(round((bloco_largura + bloco_altura) / 2))

    return bloco_largura, bloco_altura, bloco_tamanho


def detectar_tamanho(bw: np.ndarray, axis: int) -> int:
    """Calcula o tamanho médio de blocos consecutivos de pixels iguais.

    Percorre o array de imagem, trocando o eixo analisado para avaliar linhas
    ou colunas conforme `axis`, e mede sequências de pixels idênticos. A média
    dessas sequências é arredondada para obter o tamanho característico de
    blocos homogêneos.

    Args:
        bw: Array NumPy representando a imagem, com dimensões (H, W, C).
        axis: Eixo a ser analisado, 0 para linhas (altura) ou 1 para colunas
            (largura).

    Returns:
        Tamanho médio inteiro das sequências de pixels iguais ao longo do
        eixo fornecido.
    """
    tamanhos: List[int] = []
    for linha in np.swapaxes(bw, 0, axis):
        contagem = 0
        ultimo_pixel = linha[0]
        for pixel in linha:
            if np.any(pixel != ultimo_pixel):
                if contagem > 0:
                    tamanhos.append(contagem)
                contagem = 1
                ultimo_pixel = pixel
            else:
                contagem += 1
        if contagem > 0:
            tamanhos.append(contagem)

    return int(round(np.mean(tamanhos)))


def pixelizar(img: Image.Image, fator_reducao: int) -> Image.Image:
    """Corrige blocos de pixel art e aplica redução seguida de reamostragem.

    Detecta o tamanho médio dos blocos na imagem para calcular uma nova escala
    proporcional, aplica uma correção para alinhar os blocos, reduz a imagem
    pelo fator informado e, em seguida, reamplia para restaurar o tamanho,
    preservando o efeito pixelado.

    Args:
        img: Imagem PIL a ser processada.
        fator_reducao: Fator inteiro usado para reduzir temporariamente a
            imagem antes de reamostrar.

    Returns:
        Nova imagem PIL com blocos corrigidos e efeito pixelizado.
    """
    # === Pixelizar (Código 1) ===
    bloco_largura, bloco_altura, bloco_tamanho = calcular_blocos(img)
    print(f"Tamanho médio detectado: {bloco_largura}x{bloco_altura}")

    nova_largura: int = int(round(img.width / bloco_largura * bloco_tamanho))
    nova_altura: int = int(round(img.height / bloco_altura * bloco_tamanho))

    corrigida: Image.Image = img.resize(
        (nova_largura, nova_altura),
        Image.NEAREST,
    )
    reduzida: Image.Image = corrigida.resize(
        (
            corrigida.width // fator_reducao,
            corrigida.height // fator_reducao,
        ),
        Image.NEAREST,
    )
    final: Image.Image = reduzida.resize(corrigida.size, Image.NEAREST)
    final.save("pixel_art_corrigida.png")

    return final


def reduzir(img: Image.Image, fator_reducao: int) -> Image.Image:
    """Reduz uma imagem mantendo a estética pixelada.

    Converte a imagem para array, estima o tamanho dos blocos e ajusta as
    dimensões preservando o modo `NEAREST`. Em seguida, reduz pelas proporções
    fornecidas e salva o resultado.

    Args:
        img: Imagem PIL original.
        fator_reducao: Fator inteiro de redução aplicado à largura e altura.

    Returns:
        Imagem PIL reduzida com reamostragem por vizinho mais próximo.
    """
    # === Reduzir (Código 2) ===
    nova_largura: int = img.width
    nova_altura: int = img.height
    corrigida: Image.Image = img.resize(
        (nova_largura, nova_altura),
        Image.NEAREST,
    )
    largura_reduzida: int = img.width // fator_reducao
    altura_reduzida: int = img.height // fator_reducao
    reduzida: Image.Image = corrigida.resize(
        (largura_reduzida, altura_reduzida),
        Image.NEAREST,
    )
    reduzida.save("pixel_art_reduzida.png")

    return reduzida


def ampliar(img: Image.Image, fator_aumento: int) -> Image.Image:
    """Amplia uma imagem de pixel art sem suavizar os blocos.

    Calcula dimensões ampliadas com base no fator fornecido, reamostra usando
    `NEAREST` para preservar bordas e salva o arquivo resultante.

    Args:
        img: Imagem PIL a ser ampliada.
        fator_aumento: Fator inteiro pelo qual largura e altura serão
            multiplicadas.

    Returns:
        Imagem PIL ampliada mantendo o estilo pixelado.
    """
    # === Ampliar (Código 3) ===
    nova_largura: int = img.width
    nova_altura: int = img.height
    corrigida: Image.Image = img.resize(
        (nova_largura, nova_altura),
        Image.NEAREST,
    )
    largura_ampliada: int = img.width * fator_aumento
    altura_ampliada: int = img.height * fator_aumento
    ampliada: Image.Image = corrigida.resize(
        (largura_ampliada, altura_ampliada),
        Image.NEAREST,
    )
    ampliada.save("pixel_art_ampliada.png")

    return ampliada


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


def aproximar_cores(
    img: Image.Image,
    cores_referencia: List[Tuple[int, int, int]] | None = None,
    tolerancia: int = 5,
    limiar_discrepancia: float = 0.75,
) -> Image.Image:
    """Aproxima cores discrepantes usando vizinhança como referência.

    Analisa cada pixel que não esteja dentro da tolerância das cores de
    referência. Para esses casos, calcula a cor média dos vizinhos imediatos e
    escolhe a cor de referência mais próxima, gerando uma imagem com paleta
    mais consistente quando a discrepância em relação à vizinhança ultrapassa o
    limiar informado.

    Args:
        img: Imagem PIL de entrada.
        cores_referencia: Lista de cores RGB usadas como alvo de aproximação.
        tolerancia: Desvio máximo permitido para considerar um pixel próximo
            das cores de referência.
        limiar_discrepancia: Distância mínima em relação à cor média dos
            vizinhos para que a substituição de cor ocorra.

    Returns:
        Imagem PIL com cores aproximadas às referências fornecidas.
    """
    cores_referencia = (
        cores_referencia
        if cores_referencia is not None
        else [(0, 0, 0), (255, 255, 255)]
    )

    # === Aproximar Cores (Melhorada) ===
    arr: np.ndarray = np.array(img)
    height, width, _ = arr.shape

    # Criar uma cópia do array para modificação
    arr_novo: np.ndarray = arr.copy()

    # Processar cada pixel
    for y in range(height):
        for x in range(width):
            pixel_atual: Tuple[int, int, int] = tuple(arr[y, x])
            pixel_toleravel = pixel_fora_da_tolerancia(
                pixel_atual,
                cores_referencia,
                tolerancia,
            )
            if not pixel_toleravel:
                continue

            vizinhos: List[Tuple[int, int, int]] = obter_vizinhos(arr, x, y)
            if not vizinhos:
                continue

            vizinhos_rgb: np.ndarray = np.array(vizinhos)
            cor_media: Tuple[int, int, int] = tuple(
                np.round(np.mean(vizinhos_rgb, axis=0)).astype(int)
            )

            discrepancia_quadrada = sum(
                (valor_atual - valor_medio) ** 2
                for valor_atual, valor_medio in zip(pixel_atual, cor_media)
            )
            discrepancia: float = float(np.sqrt(discrepancia_quadrada))
            if discrepancia < limiar_discrepancia:
                continue

            cor_referencia: Tuple[int, int, int] = cor_referencia_mais_proxima(
                cor_media,
                cores_referencia,
            )
            arr_novo[y, x] = cor_referencia

    # Converter de volta para imagem e salvar
    img_final: Image.Image = Image.fromarray(arr_novo)
    img_final.save("pixel_art_cores_aproximadas.png")
    return img_final


def verificar_cores(img: Image.Image) -> None:
    """Conta e exibe a ocorrência de cada cor em uma imagem.

    Converte a imagem para RGB, contabiliza cada pixel transformando-o em
    hexadecimal e imprime um resumo ordenado por frequência.

    Args:
        img: Imagem PIL a ser analisada.

    Returns:
        None: Apenas exibe as informações no console.
    """
    # === Verificar Cores (Corrigida com conversão para RGB) ===
    # Converter a imagem para RGB para garantir 3 canais
    img = img.convert("RGB")
    arr: np.ndarray = np.array(img)
    height, width, _ = arr.shape
    cor_contagem: Dict[str, int] = {}

    # Função para converter RGB para hexadecimal
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Converte um valor RGB para sua representação hexadecimal."""
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'.upper()

    # Contar cada pixel individualmente
    for y in range(height):
        for x in range(width):
            pixel: Tuple[int, int, int] = tuple(arr[y, x])
            hex_cor: str = rgb_to_hex(pixel)
            cor_contagem[hex_cor] = cor_contagem.get(hex_cor, 0) + 1

    # Resumo final, ordenado por contagem decrescente
    print("\nResumo de cores na imagem:")
    for hex_cor, contagem in sorted(
        cor_contagem.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{hex_cor} se repetiu {contagem} vezes")

    return None


def obter_fator(opcao: str) -> int | None:
    """Solicita e valida o fator numérico usado pelas transformações."""

    if opcao in ["1", "2"]:
        fator: str | None = input(
            "Digite o fator de redução (ex.: 2 para 2x): "
        )
    elif opcao == "3":
        fator = input("Digite o fator de aumento (ex.: 2 para 2x): ")
    else:
        return 0

    try:
        fator_int: int = int(fator) if fator is not None else 0
        if fator_int <= 0:
            raise ValueError("Fator deve ser um número positivo.")
    except ValueError as e:
        print(f"Erro: {e}")
        return None

    return fator_int


def main() -> None:
    """Interface de linha de comando para ferramentas de pixel art.

    Solicita ao usuário a operação desejada, valida entradas, abre a imagem e
    aciona a função correspondente para pixelizar, reduzir, ampliar, aproximar
    cores ou verificar paleta.

    Returns:
        None: O fluxo é conduzido por efeitos colaterais (arquivos salvos ou
        saídas no console).
    """
    print("Escolha uma opção:")
    print("1 - Pixelizar (corrigir blocos e limpar imagem)")
    print("2 - Reduzir (diminuir tamanho da imagem)")
    print("3 - Ampliar (aumentar tamanho da imagem)")
    print("4 - Aproximar Cores (substituir cores discrepantes)")
    print("5 - Verificar Cores (resumo de cores)")
    opcao: str = input("Digite o número da opção (1, 2, 3, 4 ou 5): ")

    if opcao not in ["1", "2", "3", "4", "5"]:
        print("Opção inválida! Escolha 1, 2, 3, 4 ou 5.")
        return

    arquivo_entrada: str = input(
        "Digite o nome do arquivo de imagem (ex.: imagem.png): "
    )

    try:
        img: Image.Image = Image.open(arquivo_entrada)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao abrir a imagem: {e}")
        return

    fator_int = obter_fator(opcao)
    if fator_int is None:
        return

    if opcao == "1":
        print("Pixelizando a imagem...")
        pixelizar(img, fator_int)
        print("Imagem pixelizada salva como 'pixel_art_corrigida.png'")
    elif opcao == "2":
        print("Reduzindo a imagem...")
        reduzir(img, fator_int)
        print("Imagem reduzida salva como 'pixel_art_reduzida.png'")
    elif opcao == "3":
        print("Ampliando a imagem...")
        ampliar(img, fator_int)
        print("Imagem ampliada salva como 'pixel_art_ampliada.png'")
    elif opcao == "4":
        print("Aproximando cores da imagem...")
        aproximar_cores(img)
        print(
            "Imagem com cores aproximadas salva como "
            "'pixel_art_cores_aproximadas.png'"
        )
    elif opcao == "5":
        print("Verificando cores da imagem...")
        verificar_cores(img)


if __name__ == "__main__":
    main()
