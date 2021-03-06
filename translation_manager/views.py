from django.contrib.admin.views.main import ChangeList

from .settings import get_settings


hint_sql_template = (
    "SELECT te2.* FROM %s AS te1 INNER JOIN %s AS te2 ON "
    "(te1.original = te2.original "
    "AND te1.domain = te2.domain AND te2.locale_path = %s) "
    "WHERE te2.is_published = TRUE "
    "AND te1.id IN (%s) AND te2.language = '%s'")


class TranslationChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        super(TranslationChangeList, self).__init__(*args, **kwargs)

        if self.result_list:
            self.prep_hints()

    def prep_hints(self):
        from .models import TranslationEntry
        entry_ids = [str(entry.id) for entry in self.result_list]

        # hint locale path from settings variable
        hint_locale = get_settings('TRANSLATIONS_HINT_LANGUAGE_FORCED_RELATIVE_LOCALE_PATH')  # noqa
        if not hint_locale:
            hint_locale = 'te1.locale_path'
        else:
            hint_locale = "'%s'" % hint_locale

        # pylint:disable=protected-access
        hint_sql = hint_sql_template % (
            TranslationEntry._meta.db_table,
            TranslationEntry._meta.db_table,
            hint_locale,
            ",".join(entry_ids),
            get_settings('TRANSLATIONS_HINT_LANGUAGE'))

        hint_qs = TranslationEntry.objects.raw(hint_sql)
        hint_dict = dict([(hint.original, hint.translation)
                          for hint in hint_qs])

        for result in self.result_list:
            # pylint:disable=protected-access
            result._hint = hint_dict.get(result.original, "")
