"""Exceções customizadas para as ferramentas de pixel art."""


class PixelArtError(Exception):
    """Base para erros relacionados ao processamento de pixel art."""


class InvalidParameterError(PixelArtError):
    """Erro para parâmetros inválidos fornecidos às operações."""


class ProcessingError(PixelArtError):
    """Erro genérico durante o processamento ou IO de imagens."""

