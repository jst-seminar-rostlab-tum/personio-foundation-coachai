from enum import Enum as PyEnum


class LanguageCode(str, PyEnum):
    en = 'en'
    de = 'de'


LANGUAGE_NAME = {
    LanguageCode.en: 'English',
    LanguageCode.de: 'German',
}
