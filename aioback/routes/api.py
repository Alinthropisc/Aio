from core.routes import ApiRouter

router = ApiRouter()

# ── Пример: раскомментируй и добавляй свои контроллеры ───────────────────────

# from app.controllers.health import HealthController
# from middleware.http.auth import AuthMiddleware

# with router.group("/api/v1", tags=["v1"]):
#     router.get("/health", HealthController.check)
#
#     with router.group("/users"):
#         router.resource("/", UserController)
#
#     with router.group("/admin", middleware=[AuthMiddleware]):
#         router.resource("/users", AdminUserController)


def get_routes():
    return router.build()
