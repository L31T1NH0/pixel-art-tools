# Pixel Art Tools

Conjunto de utilitários em Python para corrigir, simplificar e inspecionar pixel art. A CLI e a API oferecem operações de pixelização, redução, ampliação, aproximação de cores e verificação de paletas, mantendo blocos nítidos e previsíveis.

## Funcionalidades
- **Pixelizar**: corrige blocos irregulares, reduz e reamostra para realinhar pixels.
- **Reduzir**: diminui imagens em fatores inteiros preservando bordas.
- **Ampliar**: aumenta imagens em múltiplos inteiros sem suavização.
- **Aproximar cores**: substitui cores discrepantes usando tolerância e vizinhança.
- **Verificar cores**: contabiliza ocorrências de cada cor e exporta um resumo.

## Algoritmo de detecção de blocos (resumo)
A classe `PixelArtProcessor` converte a imagem em array NumPy, percorre linhas e colunas e mede sequências consecutivas de pixels idênticos para estimar o tamanho médio dos blocos (`detectar_tamanho`). A média das larguras e alturas encontradas é usada para reamostrar a imagem e alinhar blocos antes das transformações (`calcular_blocos`).【F:processing.py†L39-L85】

## Instalação
### Requisitos
- Python 3.11+ (testado)
- [Pillow](https://python-pillow.org/)
- [NumPy](https://numpy.org/)

### Instalando dependências
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install --upgrade pip
pip install -r requirements.txt  # ou: pip install pillow numpy
```

## Como usar a CLI
### Sintaxe geral
```bash
python cli.py [--interactive] <comando> [opções]
```
- `--interactive` executa o modo legado com perguntas em sequência.
- Quando nenhum comando é informado, o modo interativo é usado por padrão.

### Comandos
- `pixelizar` — Corrige blocos e reamostra a imagem.
- `reduzir` — Diminui a imagem mantendo o estilo pixelado.
- `ampliar` — Aumenta a imagem sem suavização.
- `aproximar-cores` — Ajusta cores discrepantes considerando tolerância.
- `verificar-cores` — Gera resumo das cores presentes.

### Opções comuns
- `--input PATH` (obrigatório): caminho da imagem de entrada.
- `--output PATH` (opcional): arquivo de saída; se omitido, é gerado a partir do nome de entrada.
- `--factor N` (opcional): fator numérico usado pelo comando (redução, ampliação ou tolerância).

### Exemplos
Pixelizar uma imagem com fator 2 e saída automática:
```bash
python cli.py pixelizar --input sprites.png --factor 2
```

Reduzir uma sprite em 3x salvando em arquivo específico:
```bash
python cli.py reduzir --input sprite.png --factor 3 --output sprite_reduzida.png
```

Ampliar uma imagem em 4x:
```bash
python cli.py ampliar --input tiles.png --factor 4
```

Aproximar cores com tolerância padrão e salvar resultado:
```bash
python cli.py aproximar-cores --input cena.png --output cena_corrigida.png
```

Gerar resumo de cores em texto:
```bash
python cli.py verificar-cores --input hud.png --output hud_cores.txt
```

## Uso como biblioteca
### Importando a classe principal
```python
from processing import PixelArtProcessor
from PIL import Image

processor = PixelArtProcessor()
img = Image.open("sprites.png")

corrigida = processor.pixelizar(img, fator_reducao=2)
resumo = processor.verificar_cores(img)
```

### Funções utilitárias
```python
from utils import pixel_fora_da_tolerancia, obter_vizinhos, cor_referencia_mais_proxima
```
Essas funções auxiliam em análises de vizinhança e escolha de cores de referência.【F:utils.py†L1-L52】

## Estrutura do projeto
```
README.md            # Visão geral e instruções
cli.py               # Interface de linha de comando e modo interativo
processing.py        # Implementação das operações de pixel art e detecção de blocos
errors.py            # Exceções específicas do domínio
utils.py             # Funções auxiliares de cor e vizinhança
file3.py             # Módulo de reexportação com ponto de entrada alternativo
tests/               # Testes automatizados (pytest)
```

## Notas de desempenho, limitações e algoritmos
- O processamento usa PIL e NumPy; imagens muito grandes podem consumir memória considerável.
- Os fatores (`--factor`) devem ser inteiros positivos para reduzir/ampliar e não negativos para tolerância; valores inválidos geram `InvalidParameterError`.
- A aproximação de cores calcula a média dos vizinhos 8-conectados e substitui apenas pixels fora da tolerância e com discrepância mínima configurável.【F:processing.py†L165-L234】
- O resumo de cores faz contagem pixel a pixel; em sprites grandes pode ser mais lento, mas preserva exatidão.【F:processing.py†L236-L314】

## Licença
Recomenda-se licenciar como MIT ou outra licença permissiva adequada. Defina a licença conforme a política do projeto antes de distribuição.
