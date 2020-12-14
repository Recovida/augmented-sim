from pathlib import Path
from typing import Optional, Callable

from PySide2.QtCore import QObject, QTranslator, QLocale


AVAILABLE_LANGUAGES = [
    ('en', 'English'),
    ('pt', 'Português')
]

CHOSEN_LANGUAGE = 'pt'


def get_translator(obj: Optional[QObject], locale: Optional[str] = None) \
        -> QTranslator:
    if not locale:
        locale = CHOSEN_LANGUAGE
    here = Path(__file__).parent.parent.resolve()
    translator = QTranslator(obj)
    fn, d = 'augmentedsim', str(here / 'i18n')
    translator.load(QLocale(locale), fn, prefix='.', directory=d)
    return translator


def get_tr(context: str, translator: QTranslator) -> Callable:

    def tr(key: str, *args, **kwargs) -> str:
        return translator.translate(context, key, *args, **kwargs)

    return tr


def change_language_globally(language: str) -> None:
    global CHOSEN_LANGUAGE
    CHOSEN_LANGUAGE = language
