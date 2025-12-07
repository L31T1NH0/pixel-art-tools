"""Interface de linha de comando para ferramentas de pixel art."""

import argparse
from pathlib import Path
from typing import Callable

from PIL import Image

from errors import PixelArtError
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

    arquivo_entrada = Path(
        input("Digite o nome do arquivo de imagem (ex.: imagem.png): ")
    ).expanduser()

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

    try:
        if opcao == "1":
            print("Pixelizando a imagem...")
            destino = gerar_caminho_saida(arquivo_entrada, "pixelizado")
            processor.pixelizar(img, fator_int, destino)
            print(f"Imagem pixelizada salva como '{destino}'")
        elif opcao == "2":
            print("Reduzindo a imagem...")
            destino = gerar_caminho_saida(arquivo_entrada, "reduzida")
            processor.reduzir(img, fator_int, destino)
            print(f"Imagem reduzida salva como '{destino}'")
        elif opcao == "3":
            print("Ampliando a imagem...")
            destino = gerar_caminho_saida(arquivo_entrada, "ampliada")
            processor.ampliar(img, fator_int, destino)
            print(f"Imagem ampliada salva como '{destino}'")
        elif opcao == "4":
            print("Aproximando cores da imagem...")
            destino = gerar_caminho_saida(arquivo_entrada, "cores_aproximadas")
            processor.aproximar_cores(img, output_path=destino)
            print(f"Imagem com cores aproximadas salva como '{destino}'")
        elif opcao == "5":
            print("Verificando cores da imagem...")
            destino = gerar_caminho_saida(
                arquivo_entrada, "cores", extensao=".txt"
            )
            resumo = processor.verificar_cores(img, destino)
            for linha in resumo:
                print(linha)
            if destino:
                print(f"Resumo de cores salvo em '{destino}'")
    except PixelArtError as exc:
        print(f"Erro durante o processamento: {exc}")


def carregar_imagem(caminho: Path) -> Image.Image | None:
    """Abre a imagem indicada, tratando erros comuns de IO."""

    caminho = caminho.expanduser()
    try:
        return Image.open(caminho)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho}' não encontrado.")
    except Exception as exc:  # pragma: no cover - mensagens explícitas
        print(f"Erro ao abrir a imagem: {exc}")
    return None


def gerar_caminho_saida(
    caminho_entrada: Path, sufixo: str, extensao: str | None = None
) -> Path:
    """Gera automaticamente um caminho de saída baseado no arquivo de entrada."""

    entrada = caminho_entrada.expanduser()
    extensao_saida = extensao if extensao is not None else entrada.suffix or ".png"
    return entrada.with_name(f"{entrada.stem}_{sufixo}{extensao_saida}")


def processar_pixelizar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    output = args.output or gerar_caminho_saida(args.input, "pixelizado")

    try:
        processor.pixelizar(imagem, args.factor, output)
    except PixelArtError as exc:
        print(f"Erro ao pixelizar: {exc}")
        return

    print(f"Imagem pixelizada salva como '{output}'")


def processar_reduzir(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    output = args.output or gerar_caminho_saida(args.input, "reduzida")

    try:
        processor.reduzir(imagem, args.factor, output)
    except PixelArtError as exc:
        print(f"Erro ao reduzir: {exc}")
        return

    print(f"Imagem reduzida salva como '{output}'")


def processar_ampliar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    output = args.output or gerar_caminho_saida(args.input, "ampliada")

    try:
        processor.ampliar(imagem, args.factor, output)
    except PixelArtError as exc:
        print(f"Erro ao ampliar: {exc}")
        return

    print(f"Imagem ampliada salva como '{output}'")


def processar_aproximar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    tolerancia = args.factor if args.factor is not None else 5
    output = args.output or gerar_caminho_saida(args.input, "cores_aproximadas")

    try:
        processor.aproximar_cores(imagem, tolerancia=tolerancia, output_path=output)
    except PixelArtError as exc:
        print(f"Erro ao aproximar cores: {exc}")
        return

    print(f"Imagem com cores aproximadas salva como '{output}'")


def processar_verificar(args: argparse.Namespace) -> None:
    processor = PixelArtProcessor()
    imagem = carregar_imagem(args.input)
    if imagem is None:
        return

    output = args.output or gerar_caminho_saida(args.input, "cores", extensao=".txt")

    try:
        resumo = processor.verificar_cores(imagem, output)
    except PixelArtError as exc:
        print(f"Erro ao verificar cores: {exc}")
        return

    for linha in resumo:
        print(linha)
    if output:
        print(f"Resumo de cores salvo em '{output}'")


def adicionar_argumentos_comuns(
    parser: argparse.ArgumentParser,
    sufixo_padrao: str | None,
    fator_padrao: int | None = None,
) -> None:
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Caminho do arquivo de imagem de entrada.",
    )
    ajuda_saida = (
        "Arquivo de saída (opcional; padrão derivado do nome de entrada)."
        if sufixo_padrao
        else "Arquivo de saída (opcional)."
    )
    parser.add_argument(
        "--output",
        default=None,
        type=Path,
        help=ajuda_saida,
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
    adicionar_argumentos_comuns(parser_pixelizar, "pixelizado", 2)
    parser_pixelizar.set_defaults(handler=processar_pixelizar)

    parser_reduzir = subparsers.add_parser(
        "reduzir",
        help="Reduz a imagem mantendo o estilo pixelado.",
    )
    adicionar_argumentos_comuns(parser_reduzir, "reduzida", 2)
    parser_reduzir.set_defaults(handler=processar_reduzir)

    parser_ampliar = subparsers.add_parser(
        "ampliar",
        help="Amplia a imagem em múltiplos inteiros sem suavizar os blocos.",
    )
    adicionar_argumentos_comuns(parser_ampliar, "ampliada", 2)
    parser_ampliar.set_defaults(handler=processar_ampliar)

    parser_aproximar = subparsers.add_parser(
        "aproximar-cores",
        help="Aproxima cores discrepantes usando vizinhança como referência.",
    )
    adicionar_argumentos_comuns(
        parser_aproximar,
        "cores_aproximadas",
    )
    parser_aproximar.set_defaults(handler=processar_aproximar)

    parser_verificar = subparsers.add_parser(
        "verificar-cores",
        help="Exibe um resumo das cores presentes na imagem.",
    )
    adicionar_argumentos_comuns(parser_verificar, "cores")
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
