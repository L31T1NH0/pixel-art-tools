"""Interface de linha de comando para ferramentas de pixel art."""

import argparse
from typing import Callable

from PIL import Image

from processing import PixelArtProcessor


def inteiro_positivo(valor: str) -> int:
    """Converte uma string em inteiro positivo para o argparse."""

    try:
        numero = int(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "O fator precisa ser um número inteiro."
        ) from exc

    if numero <= 0:
        raise argparse.ArgumentTypeError("O fator deve ser maior que zero.")

    return numero


def obter_fator_interativo(opcao: str) -> int | None:
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


def executar_interativo() -> None:
    """Mantém o modo de operação interativa legado."""

    processor = PixelArtProcessor()

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
    except Exception as e:  # pragma: no cover - mensagens explícitas
        print(f"Erro ao abrir a imagem: {e}")
        return

    fator_int = obter_fator_interativo(opcao)
    if fator_int is None:
        return

    if opcao == "1":
        print("Pixelizando a imagem...")
        processor.pixelizar(img, fator_int)
        print("Imagem pixelizada salva como 'pixel_art_corrigida.png'")
    elif opcao == "2":
        print("Reduzindo a imagem...")
        processor.reduzir(img, fator_int)
        print("Imagem reduzida salva como 'pixel_art_reduzida.png'")
    elif opcao == "3":
        print("Ampliando a imagem...")
        processor.ampliar(img, fator_int)
        print("Imagem ampliada salva como 'pixel_art_ampliada.png'")
    elif opcao == "4":
        print("Aproximando cores da imagem...")
        processor.aproximar_cores(img)
        print(
            "Imagem com cores aproximadas salva como "
            "'pixel_art_cores_aproximadas.png'"
        )
    elif opcao == "5":
        print("Verificando cores da imagem...")
        processor.verificar_cores(img)


def carregar_imagem(caminho: str) -> Image.Image | None:
    """Abre a imagem indicada, tratando erros comuns de IO."""

    try:
        return Image.open(caminho)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho}' não encontrado.")
    except Exception as exc:  # pragma: no cover - mensagens explícitas
        print(f"Erro ao abrir a imagem: {exc}")
    return None


def processar_pixelizar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    processor.pixelizar(imagem, args.factor, args.output)
    print(f"Imagem pixelizada salva como '{args.output}'")


def processar_reduzir(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    processor.reduzir(imagem, args.factor, args.output)
    print(f"Imagem reduzida salva como '{args.output}'")


def processar_ampliar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    processor.ampliar(imagem, args.factor, args.output)
    print(f"Imagem ampliada salva como '{args.output}'")


def processar_aproximar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    tolerancia = args.factor if args.factor is not None else 5
    processor.aproximar_cores(imagem, tolerancia=tolerancia, output_path=args.output)
    print(f"Imagem com cores aproximadas salva como '{args.output}'")


def processar_verificar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    processor.verificar_cores(imagem, args.output)
    if args.output:
        print(f"Resumo de cores salvo em '{args.output}'")


def adicionar_argumentos_comuns(
    parser: argparse.ArgumentParser,
    padrao_saida: str | None,
    fator_padrao: int | None = None,
) -> None:
    parser.add_argument(
        "--input",
        required=True,
        help="Caminho do arquivo de imagem de entrada.",
    )
    if padrao_saida is None:
        parser.add_argument(
            "--output",
            default=None,
            help="Arquivo de saída (opcional).",
        )
    else:
        parser.add_argument(
            "--output",
            default=padrao_saida,
            help=f"Arquivo de saída (padrão: {padrao_saida}).",
        )
    parser.add_argument(
        "--factor",
        type=inteiro_positivo,
        default=fator_padrao,
        help="Fator numérico usado na operação.",
    )


def construir_parser() -> argparse.ArgumentParser:
    """Cria o parser principal com subcomandos profissionais."""

    parser = argparse.ArgumentParser(
        description="Ferramentas de pixel art com subcomandos especializados.",
    )
    parser.add_argument(
        "-I",
        "--interactive",
        action="store_true",
        help="Executa o modo interativo legado.",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="comando")

    parser_pixelizar = subparsers.add_parser(
        "pixelizar",
        help="Corrige blocos, reduz e reamplia a imagem pixel art.",
    )
    adicionar_argumentos_comuns(parser_pixelizar, "pixel_art_corrigida.png", 2)
    parser_pixelizar.set_defaults(handler=processar_pixelizar)

    parser_reduzir = subparsers.add_parser(
        "reduzir",
        help="Reduz a imagem mantendo o estilo pixelado.",
    )
    adicionar_argumentos_comuns(parser_reduzir, "pixel_art_reduzida.png", 2)
    parser_reduzir.set_defaults(handler=processar_reduzir)

    parser_ampliar = subparsers.add_parser(
        "ampliar",
        help="Amplia a imagem em múltiplos inteiros sem suavizar os blocos.",
    )
    adicionar_argumentos_comuns(parser_ampliar, "pixel_art_ampliada.png", 2)
    parser_ampliar.set_defaults(handler=processar_ampliar)

    parser_aproximar = subparsers.add_parser(
        "aproximar-cores",
        help="Aproxima cores discrepantes usando vizinhança como referência.",
    )
    adicionar_argumentos_comuns(
        parser_aproximar,
        "pixel_art_cores_aproximadas.png",
    )
    parser_aproximar.set_defaults(handler=processar_aproximar)

    parser_verificar = subparsers.add_parser(
        "verificar-cores",
        help="Exibe um resumo das cores presentes na imagem.",
    )
    adicionar_argumentos_comuns(parser_verificar, None)
    parser_verificar.set_defaults(handler=processar_verificar)

    return parser


def main() -> None:
    """Despacha subcomandos ou inicia o modo interativo legado."""

    parser = construir_parser()
    args = parser.parse_args()

    if args.interactive or args.command is None:
        executar_interativo()
        return

    handler: Callable[[argparse.Namespace], None] | None = getattr(
        args, "handler", None
    )
    if handler is None:
        parser.print_help()
        return

    handler(args)


if __name__ == "__main__":
    main()
