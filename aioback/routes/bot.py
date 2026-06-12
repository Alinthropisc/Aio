from core.routes import BotRouter

router = BotRouter(name="main")

# ── Пример: раскомментируй и добавляй свои хэндлеры ─────────────────────────

# from bot.handlers.start import StartHandler
# from bot.handlers.profile import ProfileHandler
# from bot.callbacks.profile import ProfileCallback

# start = StartHandler()
# profile = ProfileHandler()

# router.command("start", start.handle)
# router.command("help",  start.help)

# with router.group("profile"):
#     router.callback(F.data == "profile", profile.show)
#     router.callback_data(ProfileCallback, profile.handle)
#     router.text("👤 Профиль", profile.show)

# with router.group("settings"):
#     router.state(SettingsStates.language, SettingsHandler().set_language)


def get_router():
    return router.build()
