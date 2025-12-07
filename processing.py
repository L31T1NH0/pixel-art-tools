"""Funções de processamento para ferramentas de pixel art."""

from typing import Dict, List, Tuple

import numpy as np
from PIL import Image

from errors import InvalidParameterError, ProcessingError
from utils import cor_referencia_mais_proxima, obter_vizinhos, pixel_fora_da_tolerancia


class PixelArtProcessor:
    """Processador de pixel art com operações de manipulação de imagem."""

    @staticmethod
    def _ensure_positive_int(nome: str, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise InvalidParameterError(
                f"O parâmetro '{nome}' precisa ser um inteiro maior que zero."
            )

    @staticmethod
    def _ensure_non_negative_int(nome: str, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise InvalidParameterError(
                f"O parâmetro '{nome}' precisa ser um inteiro maior ou igual a zero."
            )

    @staticmethod
    def _ensure_non_negative_float(nome: str, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0:
            raise InvalidParameterError(
                f"O parâmetro '{nome}' precisa ser numérico e não negativo."
            )

    @staticmethod
    def _ensure_image_has_data(img: Image.Image) -> Image.Image:
        if img.width <= 0 or img.height <= 0:
            raise InvalidParameterError("A imagem não possui dimensões válidas.")
        return img

    @staticmethod
    def _save_image(image: Image.Image, output_path: str) -> None:
        try:
            image.save(output_path)
        except OSError as exc:  # pragma: no cover - dependente do sistema de arquivos
            raise ProcessingError(
                f"Não foi possível salvar a imagem em '{output_path}': {exc}"
            ) from exc

    def calcular_blocos(self, img: Image.Image) -> Tuple[int, int, int]:
        """Retorna a largura, altura e tamanho médio dos blocos de pixel art."""

        img = self._ensure_image_has_data(img).convert("RGB")
        arr: np.ndarray = np.array(img)
        if arr.size == 0:
            raise ProcessingError("A imagem não contém dados para processamento.")

        bloco_largura: int = self.detectar_tamanho(arr, 1)
        bloco_altura: int = self.detectar_tamanho(arr, 0)
        bloco_tamanho: int = int(round((bloco_largura + bloco_altura) / 2))

        return bloco_largura, bloco_altura, bloco_tamanho

    @staticmethod
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
        if bw.size == 0:
            raise ProcessingError("A imagem convertida está vazia.")

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

        if not tamanhos:
            raise ProcessingError(
                "Não foi possível detectar o tamanho dos blocos na imagem fornecida."
            )

        return int(round(np.mean(tamanhos)))

    def pixelizar(
        self,
        img: Image.Image,
        fator_reducao: int,
        output_path: str = "pixel_art_corrigida.png",
    ) -> Image.Image:
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
        self._ensure_positive_int("fator_reducao", fator_reducao)
        img = self._ensure_image_has_data(img)

        # === Pixelizar (Código 1) ===
        bloco_largura, bloco_altura, bloco_tamanho = self.calcular_blocos(img)

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
        self._save_image(final, output_path)

        return final

    def reduzir(
        self,
        img: Image.Image,
        fator_reducao: int,
        output_path: str = "pixel_art_reduzida.png",
    ) -> Image.Image:
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
        self._ensure_positive_int("fator_reducao", fator_reducao)
        img = self._ensure_image_has_data(img)

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
        self._save_image(reduzida, output_path)

        return reduzida

    def ampliar(
        self,
        img: Image.Image,
        fator_aumento: int,
        output_path: str = "pixel_art_ampliada.png",
    ) -> Image.Image:
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
        self._ensure_positive_int("fator_aumento", fator_aumento)
        img = self._ensure_image_has_data(img)

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
        self._save_image(ampliada, output_path)

        return ampliada

    def aproximar_cores(
        self,
        img: Image.Image,
        cores_referencia: List[Tuple[int, int, int]] | None = None,
        tolerancia: int = 5,
        limiar_discrepancia: float = 0.75,
        output_path: str = "pixel_art_cores_aproximadas.png",
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
        self._ensure_non_negative_int("tolerancia", tolerancia)
        self._ensure_non_negative_float("limiar_discrepancia", limiar_discrepancia)
        if cores_referencia is not None and len(cores_referencia) == 0:
            raise InvalidParameterError(
                "A lista de cores de referência não pode estar vazia."
            )

        img = self._ensure_image_has_data(img).convert("RGB")
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
        self._save_image(img_final, output_path)
        return img_final

    def verificar_cores(
        self, img: Image.Image, output_path: str | None = None
    ) -> List[str]:
        """Conta e exibe a ocorrência de cada cor em uma imagem.

        Converte a imagem para RGB, contabiliza cada pixel transformando-o em
        hexadecimal e imprime um resumo ordenado por frequência.

        Args:
            img: Imagem PIL a ser analisada.

        Returns:
            List[str]: Resumo textual com a contagem de cores.
        """
        if output_path is not None and not isinstance(output_path, str):
            raise InvalidParameterError(
                "O caminho de saída deve ser uma string ou None."
            )

        # === Verificar Cores (Corrigida com conversão para RGB) ===
        # Converter a imagem para RGB para garantir 3 canais
        img = self._ensure_image_has_data(img).convert("RGB")
        arr: np.ndarray = np.array(img)
        if arr.size == 0:
            raise ProcessingError("A imagem não contém dados para processamento.")

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
        linhas_resumo = ["Resumo de cores na imagem:"]
        for hex_cor, contagem in sorted(
            cor_contagem.items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            linha = f"{hex_cor} se repetiu {contagem} vezes"
            linhas_resumo.append(linha)

        if output_path:
            try:
                with open(output_path, "w", encoding="utf-8") as arquivo:
                    arquivo.write("\n".join(linhas_resumo))
            except OSError as exc:  # pragma: no cover - dependente do sistema
                raise ProcessingError(
                    f"Não foi possível salvar o resumo em '{output_path}': {exc}"
                ) from exc

        return linhas_resumo
