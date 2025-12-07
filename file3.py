from typing import Dict, List, Tuple

from PIL import Image
import numpy as np


def detectar_tamanho(bw: np.ndarray, axis: int) -> int:
    sizes: List[int] = []
    for line in np.swapaxes(bw, 0, axis):
        count: int = 0
        last = line[0]
        for pixel in line:
            if np.any(pixel != last):
                if count > 0:
                    sizes.append(count)
                count = 1
                last = pixel
            else:
                count += 1
        if count > 0:
            sizes.append(count)
    return int(round(np.mean(sizes)))


def pixelizar(img: Image.Image, fator_reducao: int) -> Image.Image:
    # === Pixelizar (Código 1) ===
    arr: np.ndarray = np.array(img)
    bw: np.ndarray = np.all(arr == arr[0, 0], axis=-1) == False
    bloco_larg: int = detectar_tamanho(arr, 1)
    bloco_alt: int = detectar_tamanho(arr, 0)
    print(f"Tamanho médio detectado: {bloco_larg}x{bloco_alt}")
    bloco_tam: int = int(round((bloco_larg + bloco_alt) / 2))
    nova_larg: int = int(round(img.width / bloco_larg * bloco_tam))
    nova_alt: int = int(round(img.height / bloco_alt * bloco_tam))
    corrigida: Image.Image = img.resize((nova_larg, nova_alt), Image.NEAREST)
    reduzida: Image.Image = corrigida.resize(
        (corrigida.width // fator_reducao, corrigida.height // fator_reducao),
        Image.NEAREST
    )
    final: Image.Image = reduzida.resize(corrigida.size, Image.NEAREST)
    final.save("pixel_art_corrigida.png")
    return final


def reduzir(img: Image.Image, fator_reducao: int) -> Image.Image:
    # === Reduzir (Código 2) ===
    arr: np.ndarray = np.array(img)
    bw: np.ndarray = np.all(arr == arr[0, 0], axis=-1) == False
    bloco_larg: int = detectar_tamanho(arr, 1)
    bloco_alt: int = detectar_tamanho(arr, 0)
    bloco_tam: int = int(round((bloco_larg + bloco_alt) / 2))
    nova_larg: int = img.width
    nova_alt: int = img.height
    corrigida: Image.Image = img.resize((nova_larg, nova_alt), Image.NEAREST)
    larg_reduzida: int = img.width // fator_reducao
    alt_reduzida: int = img.height // fator_reducao
    reduzida: Image.Image = corrigida.resize((larg_reduzida, alt_reduzida), Image.NEAREST)
    reduzida.save("pixel_art_reduzida.png")
    return reduzida


def ampliar(img: Image.Image, fator_aumento: int) -> Image.Image:
    # === Ampliar (Código 3) ===
    arr: np.ndarray = np.array(img)
    bw: np.ndarray = np.all(arr == arr[0, 0], axis=-1) == False
    bloco_larg: int = detectar_tamanho(arr, 1)
    bloco_alt: int = detectar_tamanho(arr, 0)
    bloco_tam: int = int(round((bloco_larg + bloco_alt) / 2))
    nova_larg: int = img.width
    nova_alt: int = img.height
    corrigida: Image.Image = img.resize((nova_larg, nova_alt), Image.NEAREST)
    larg_ampliada: int = img.width * fator_aumento
    alt_ampliada: int = img.height * fator_aumento
    ampliada: Image.Image = corrigida.resize((larg_ampliada, alt_ampliada), Image.NEAREST)
    ampliada.save("pixel_art_ampliada.png")
    return ampliada


def aproximar_cores(
    img: Image.Image,
    cores_referencia: List[Tuple[int, int, int]] = [(0, 0, 0), (255, 255, 255)],
    tolerancia: int = 5,
    limiar_discrepancia: float = 0.75,
) -> Image.Image:
    # === Aproximar Cores (Melhorada) ===
    arr: np.ndarray = np.array(img)
    height, width, _ = arr.shape

    # Criar uma cópia do array para modificação
    arr_novo: np.ndarray = arr.copy()

    # Função para calcular distância euclidiana entre duas cores RGB
    def distancia_cor(cor1: Tuple[int, int, int], cor2: Tuple[int, int, int]) -> float:
        return float(np.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(cor1, cor2))))

    # Processar cada pixel
    for y in range(height):
        for x in range(width):
            pixel_atual: Tuple[int, int, int] = tuple(arr[y, x])
            # Verificar se o pixel está fora da tolerância de preto ou branco
            if not any(all(abs(c1 - c2) <= tolerancia for c1, c2 in zip(pixel_atual, ref)) for ref in cores_referencia):
                # Obter vizinhos (vizinhança 8: cima, baixo, esquerda, direita, diagonais)
                vizinhos: List[Tuple[int, int, int]] = []
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < height and 0 <= nx < width:
                            vizinhos.append(tuple(arr[ny, nx]))

                if vizinhos:
                    # Calcular a cor média dos vizinhos
                    vizinhos_rgb: np.ndarray = np.array(vizinhos)
                    cor_media: Tuple[int, int, int] = tuple(np.round(np.mean(vizinhos_rgb, axis=0)).astype(int))

                    # Encontrar a cor de referência mais próxima
                    distancias: List[float] = [distancia_cor(cor_media, ref) for ref in cores_referencia]
                    cor_referencia: Tuple[int, int, int] = cores_referencia[int(np.argmin(distancias))]

                    # Substituir o pixel pela cor de referência
                    arr_novo[y, x] = cor_referencia

    # Converter de volta para imagem e salvar
    img_final: Image.Image = Image.fromarray(arr_novo)
    img_final.save("pixel_art_cores_aproximadas.png")
    return img_final


def verificar_cores(img: Image.Image) -> None:
    # === Verificar Cores (Corrigida com conversão para RGB) ===
    # Converter a imagem para RGB para garantir 3 canais
    img = img.convert("RGB")
    arr: np.ndarray = np.array(img)
    height, width, _ = arr.shape
    cor_contagem: Dict[str, int] = {}

    # Função para converter RGB para hexadecimal
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'.upper()

    # Contar cada pixel individualmente
    for y in range(height):
        for x in range(width):
            pixel: Tuple[int, int, int] = tuple(arr[y, x])
            hex_cor: str = rgb_to_hex(pixel)
            cor_contagem[hex_cor] = cor_contagem.get(hex_cor, 0) + 1

    # Resumo final, ordenado por contagem decrescente
    print("\nResumo de cores na imagem:")
    for hex_cor, contagem in sorted(cor_contagem.items(), key=lambda x: x[1], reverse=True):
        print(f"{hex_cor} se repetiu {contagem} vezes")
    return None


def main() -> None:
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

    arquivo_entrada: str = input("Digite o nome do arquivo de imagem (ex.: imagem.png): ")

    try:
        img: Image.Image = Image.open(arquivo_entrada)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_entrada}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao abrir a imagem: {e}")
        return

    if opcao in ["1", "2"]:
        fator: str | None = input("Digite o fator de redução (ex.: 2 para 2x): ")
    elif opcao == "3":
        fator = input("Digite o fator de aumento (ex.: 2 para 2x): ")
    else:  # opcao == "4" ou "5"
        fator = None  # Não requer fator

    if opcao != "4" and opcao != "5":
        try:
            fator_int: int = int(fator) if fator is not None else 0
            if fator_int <= 0:
                raise ValueError("Fator deve ser um número positivo.")
        except ValueError as e:
            print(f"Erro: {e}")
            return
    else:
        fator_int = 0

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
        print("Imagem com cores aproximadas salva como 'pixel_art_cores_aproximadas.png'")
    elif opcao == "5":
        print("Verificando cores da imagem...")
        verificar_cores(img)


if __name__ == "__main__":
    main()
