from pathlib import Path
from typing import Optional, Callable

from PySide2.QtCore import QObject, QTranslator, QLocale


def get_translator(obj: Optional[QObject], locale: str = 'en') -> QTranslator:
    here = Path(__file__).parent.parent.resolve()
    translator = QTranslator(obj)
    fn, d = 'augmentedsim', str(here / 'i18n')
    translator.load(QLocale(locale), fn, prefix='.', directory=d)
    return translator


def get_tr(context: str, translator: QTranslator) -> Callable:

    def tr(key: str, *args, **kwargs) -> str:
        return translator.translate(context, key, *args, **kwargs)

    return tr
