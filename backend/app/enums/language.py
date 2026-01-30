"""Enum definitions for language."""

from enum import Enum as PyEnum


class LanguageCode(str, PyEnum):
    """Enum for language code."""

    en = 'en'
    de = 'de'


LANGUAGE_NAME = {
    LanguageCode.en: 'English',
    LanguageCode.de: 'German',
}
