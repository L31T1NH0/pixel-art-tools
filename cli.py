"""Interface de linha de comando para ferramentas de pixel art."""

from PIL import Image

from processing import ampliar, aproximar_cores, pixelizar, reduzir, verificar_cores


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
