import numpy as np
import pytest
from PIL import Image

from errors import InvalidParameterError, ProcessingError
from processing import PixelArtProcessor


def create_block_image(block_size: int = 2, colors=None) -> Image.Image:
    colors = colors or [(255, 0, 0), (0, 255, 0)]
    width = height = block_size * 2
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    # Top-left and bottom-right one color, others the second
    arr[:block_size, :block_size] = colors[0]
    arr[block_size:, block_size:] = colors[0]
    arr[:block_size, block_size:] = colors[1]
    arr[block_size:, :block_size] = colors[1]
    return Image.fromarray(arr)


def test_detectar_tamanho_and_calcular_blocos():
    processor = PixelArtProcessor()
    img = create_block_image(block_size=2)
    array = np.array(img)

    tamanho_linhas = processor.detectar_tamanho(array, axis=0)
    tamanho_colunas = processor.detectar_tamanho(array, axis=1)
    largura, altura, media = processor.calcular_blocos(img)

    assert tamanho_linhas == 2
    assert tamanho_colunas == 2
    assert (largura, altura, media) == (2, 2, 2)


def test_detectar_tamanho_empty_array():
    processor = PixelArtProcessor()
    vazio = np.zeros((0, 0, 3), dtype=np.uint8)
    with pytest.raises(ProcessingError):
        processor.detectar_tamanho(vazio, axis=0)


def test_pixelizar_and_reduzir_and_ampliar(tmp_path):
    processor = PixelArtProcessor()
    img = create_block_image(block_size=2)

    pixelizada = processor.pixelizar(img, fator_reducao=2, output_path=tmp_path / "pixel.png")
    reduzida = processor.reduzir(img, fator_reducao=2, output_path=tmp_path / "reduced.png")
    ampliada = processor.ampliar(img, fator_aumento=2, output_path=tmp_path / "scaled.png")

    assert pixelizada.size == img.size
    assert reduzida.size == (img.width // 2, img.height // 2)
    assert ampliada.size == (img.width * 2, img.height * 2)


def test_pixelizar_invalid_factor():
    processor = PixelArtProcessor()
    img = create_block_image()
    with pytest.raises(InvalidParameterError):
        processor.pixelizar(img, fator_reducao=0)


def test_reduzir_and_ampliar_invalid_factor():
    processor = PixelArtProcessor()
    img = create_block_image()
    with pytest.raises(InvalidParameterError):
        processor.reduzir(img, fator_reducao=-1)
    with pytest.raises(InvalidParameterError):
        processor.ampliar(img, fator_aumento=0)


def test_aproximar_cores_replaces_outlier(tmp_path):
    processor = PixelArtProcessor()
    # Three black pixels and one red outlier
    arr = np.array(
        [
            [[0, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [255, 0, 0]],
        ],
        dtype=np.uint8,
    )
    img = Image.fromarray(arr)

    result = processor.aproximar_cores(img, cores_referencia=[(0, 0, 0), (255, 255, 255)], output_path=tmp_path / "approx.png")

    assert np.array_equal(np.array(result)[1, 1], np.array([0, 0, 0]))


def test_aproximar_cores_invalid_parameters():
    processor = PixelArtProcessor()
    img = create_block_image()
    with pytest.raises(InvalidParameterError):
        processor.aproximar_cores(img, cores_referencia=[])
    with pytest.raises(InvalidParameterError):
        processor.aproximar_cores(img, tolerancia=-1)


def test_verificar_cores_counts_and_output(tmp_path):
    processor = PixelArtProcessor()
    img = Image.new("RGB", (1, 1), (255, 255, 255))

    resumo = processor.verificar_cores(img, output_path=tmp_path / "cores.txt")

    assert resumo[0] == "Resumo de cores na imagem:"
    assert resumo[1] == "#FFFFFF se repetiu 1 vezes"
    assert (tmp_path / "cores.txt").exists()


def test_verificar_cores_invalid_output_path():
    processor = PixelArtProcessor()
    img = create_block_image()
    with pytest.raises(InvalidParameterError):
        processor.verificar_cores(img, output_path=123)
