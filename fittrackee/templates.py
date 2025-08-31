from typing import Dict, List

from babel.support import Translations
from jinja2 import Environment, FileSystemLoader, select_autoescape


class I18nTemplate:
    def __init__(
        self,
        template_directory: str,
        translations_directory: str,
        languages: List[str],
    ) -> None:
        self._translations = self._get_translations(
            translations_directory, languages
        )
        self._env = Environment(
            autoescape=select_autoescape(["html", "htm", "xml"]),
            loader=FileSystemLoader(template_directory),
            extensions=["jinja2.ext.i18n"],
        )

    @staticmethod
    def _get_translations(
        translations_directory: str, languages: List[str]
    ) -> Dict:
        translations = {}
        for language in languages:
            translations[language] = Translations.load(
                dirname=translations_directory, locales=[language]
            )
        return translations

    def _load_translation(self, lang: str) -> None:
        self._env.install_gettext_translations(  # type: ignore
            self._translations[lang],
            newstyle=True,
        )

    def get_content(
        self, template_name: str, lang: str, part: str, data: Dict
    ) -> str:
        self._load_translation(lang)
        template = self._env.get_template(f"{template_name}/{part}")
        return template.render(data)

    def get_all_contents(
        self, template: str, lang: str, parts: List[str], data: Dict
    ) -> Dict:
        output = {}
        for part in parts:
            output[part] = self.get_content(template, lang, part, data)
        return output
