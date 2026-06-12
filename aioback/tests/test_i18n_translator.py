"""Tests for i18n/translator.py — Translator, t(), set_locale()."""
import pytest
from i18n.translator import Translator, t, set_locale, get_locale


@pytest.fixture
def translator():
    """Use real locale files from i18n/locales/."""
    return Translator(default_locale="en")


class TestTranslator:
    def test_simple_key_en(self, translator):
        result = translator.translate("app.name", locale="en")
        assert result == "Aioback"

    def test_simple_key_ru(self, translator):
        result = translator.translate("app.name", locale="ru")
        assert result == "Aioback"

    def test_nested_key(self, translator):
        result = translator.translate("auth.login.success", locale="en")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_placeholder_substitution(self, translator):
        result = translator.translate("app.welcome", locale="en", name="Alice")
        assert "Alice" in result

    def test_missing_key_returns_key(self, translator):
        result = translator.translate("nonexistent.key.path", locale="en")
        assert result == "nonexistent.key.path"

    def test_fallback_to_default_locale(self, translator):
        # Use a key that exists in default but not forcing locale that doesn't exist
        result = translator.translate("app.name", locale="xx_MISSING")
        assert result == "Aioback"

    def test_available_locales_includes_ru_and_en(self, translator):
        locales = translator.available_locales()
        assert "ru" in locales
        assert "en" in locales

    def test_error_not_found_with_entity(self, translator):
        result = translator.translate("errors.not_found", locale="en", entity="User")
        assert "User" in result

    def test_reload_keeps_translations(self, translator):
        translator.reload()
        result = translator.translate("app.name", locale="en")
        assert result == "Aioback"


class TestGlobalT:
    def test_t_returns_translation(self):
        result = t("app.name")
        assert result == "Aioback"

    def test_t_with_locale_override(self):
        result = t("auth.login.success", locale="en")
        assert isinstance(result, str)

    def test_set_and_get_locale(self):
        set_locale("ru")
        assert get_locale() == "ru"
        set_locale("en")
        assert get_locale() == "en"
