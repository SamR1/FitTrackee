from typing import Dict

from fittrackee.templates import I18nTemplate


class FeedItemTemplate(I18nTemplate):
    def get_item_data(self, template: str, lang: str, data: Dict) -> Dict:
        parts = ["title.txt", "body.html"]
        return self.get_all_contents(template, lang, parts, data)
