import asyncio
from pathlib import Path

import typer

app      = typer.Typer(name="aioback", help="Aioback CLI", no_args_is_help=True)
db_app   = typer.Typer(help="Database commands")
make_app = typer.Typer(help="Code generators")

app.add_typer(db_app,   name="db")
app.add_typer(make_app, name="make")


# ── DB ────────────────────────────────────────────────────────────────────────

@db_app.command("migrate")
def db_migrate(revision: str = typer.Argument("head")) -> None:
    """Apply migrations."""
    import subprocess
    typer.echo(f"Migrating → {revision}")
    r = subprocess.run(["alembic", "upgrade", revision], check=False)
    typer.secho("Done!" if r.returncode == 0 else "Failed!", fg=typer.colors.GREEN if r.returncode == 0 else typer.colors.RED)
    if r.returncode != 0:
        raise typer.Exit(1)


@db_app.command("rollback")
def db_rollback(steps: int = typer.Option(1, "--steps", "-s")) -> None:
    """Rollback migrations."""
    import subprocess
    subprocess.run(["alembic", "downgrade", f"-{steps}"], check=True)
    typer.secho(f"Rolled back {steps} step(s)", fg=typer.colors.YELLOW)


@db_app.command("revision")
def db_revision(
    message: str = typer.Option(..., "--message", "-m"),
    autogenerate: bool = typer.Option(True, "--auto/--no-auto"),
) -> None:
    """Create migration."""
    import subprocess
    cmd = ["alembic", "revision", "-m", message]
    if autogenerate:
        cmd.append("--autogenerate")
    subprocess.run(cmd, check=True)
    typer.secho("Migration created!", fg=typer.colors.GREEN)


@db_app.command("status")
def db_status() -> None:
    """Show current revision."""
    import subprocess
    subprocess.run(["alembic", "current"], check=True)


@db_app.command("seed")
def db_seed(seeder: str = typer.Argument("all")) -> None:
    """Run database seeders."""
    async def _run():
        from config import get_settings
        from core.db import create_engine, session_factory, get_session
        settings = get_settings()
        engine = create_engine(url=settings.db.url)
        factory = session_factory(engine)
        async with get_session(factory) as session:
            typer.echo(f"Running seeder: {seeder}")
            # from database.seeders.user import UserSeeder
            # await UserSeeder().run(session)
            typer.secho("Seeding done!", fg=typer.colors.GREEN)
        await engine.dispose()
    asyncio.run(_run())


# ── Worker ────────────────────────────────────────────────────────────────────

@app.command("worker")
def run_worker(
    queues: str = typer.Option("default", "--queues", "-q"),
    concurrency: int = typer.Option(3, "--concurrency", "-c"),
) -> None:
    """Start queue worker."""
    async def _run():
        from config import get_settings
        from core.cache import RedisClient
        from core.queue import Queue, Worker
        from core.logging import Log
        settings = get_settings()
        Log.setup(debug=settings.app.is_debug, env=settings.app.env)
        redis = RedisClient(url=settings.redis.url, max_connections=10, decode_responses=False)
        queue_list = [q.strip() for q in queues.split(",")]
        typer.secho(f"Worker | queues={queue_list} concurrency={concurrency}", fg=typer.colors.CYAN)
        worker = Worker(Queue(redis.client), queues=queue_list, concurrency=concurrency)
        try:
            await worker.run()
        finally:
            await redis.close()
    asyncio.run(_run())


# ── Info ──────────────────────────────────────────────────────────────────────

@app.command("info")
def info() -> None:
    """Show project info."""
    from config import get_settings
    s = get_settings()
    typer.echo(f"App:   {s.app.name} v{s.app.version}")
    typer.echo(f"Env:   {s.app.env}  Debug: {s.app.debug}")
    typer.echo(f"DB:    {s.db.driver}://{s.db.host}:{s.db.port}/{s.db.name}")
    typer.echo(f"Redis: {s.redis.host}:{s.redis.port}/{s.redis.db}")


# ── Make generators ───────────────────────────────────────────────────────────

def _write(path: str, content: str, label: str) -> None:
    full = Path(path)
    if full.exists():
        typer.secho(f"Exists: {path}", fg=typer.colors.YELLOW)
        raise typer.Exit()
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    typer.secho(f"Created: {path}", fg=typer.colors.GREEN)


@make_app.command("model")
def make_model(name: str = typer.Argument(...)) -> None:
    """Generate SQLAlchemy model."""
    _write(f"app/models/{name.lower()}.py", f'''from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from core.db import BaseModel


class {name}(BaseModel):
    __tablename__ = "{name.lower()}s"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
''', f"Model {name}")


@make_app.command("service")
def make_service(name: str = typer.Argument(...)) -> None:
    """Generate service class."""
    _write(f"services/{name.lower()}.py", f'''from services import BaseService
from app.models.{name.lower()} import {name}
from repositories.{name.lower()} import {name}Repository


class {name}Service(BaseService[{name}, {name}Repository]):
    pass
''', f"Service {name}Service")


@make_app.command("repository")
def make_repository(name: str = typer.Argument(...)) -> None:
    """Generate repository class."""
    _write(f"repositories/{name.lower()}.py", f'''from repositories import BaseRepository
from app.models.{name.lower()} import {name}


class {name}Repository(BaseRepository[{name}]):
    model = {name}
''', f"Repository {name}Repository")


@make_app.command("controller")
def make_controller(name: str = typer.Argument(...)) -> None:
    """Generate Litestar controller."""
    _write(f"app/controllers/{name.lower()}.py", f'''from dishka.integrations.litestar import FromDishka, inject
from litestar import get, post, delete

from app.controllers import BaseWebController
from services.{name.lower()} import {name}Service


class {name}Controller(BaseWebController):
    path = "/{name.lower()}s"

    @get()
    @inject
    async def index(self, service: FromDishka[{name}Service]) -> list:
        return await service.get_all()
''', f"Controller {name}Controller")


@make_app.command("job")
def make_job(name: str = typer.Argument(...)) -> None:
    """Generate Job class."""
    _write(f"jobs/{name.lower()}.py", f'''from dataclasses import dataclass
from core.queue import BaseJob
from core.logging import Log


@dataclass
class {name}Job(BaseJob):
    queue: str = "default"
    max_retries: int = 3

    async def handle(self) -> None:
        Log.get("{name}Job").info("Executing")

    async def failed(self, exc: Exception) -> None:
        Log.error(f"{name}Job permanently failed: {{exc}}")
''', f"Job {name}Job")


@make_app.command("observer")
def make_observer(name: str = typer.Argument(...)) -> None:
    """Generate Observer class."""
    _write(f"observers/{name.lower()}.py", f'''from core.events.observer import ModelObserver
from core.logging import Log


class {name}Observer(ModelObserver):
    async def created(self, instance) -> None:
        Log.info(f"{name} created: {{instance.id}}")

    async def updated(self, instance) -> None:
        Log.info(f"{name} updated: {{instance.id}}")

    async def deleted(self, instance) -> None:
        Log.info(f"{name} deleted: {{instance.id}}")
''', f"Observer {name}Observer")


@make_app.command("listener")
def make_listener(name: str = typer.Argument(...)) -> None:
    """Generate Listener class."""
    _write(f"listeners/{name.lower()}.py", f'''from core.events.bus import BaseEvent
from listeners.base import BaseListener


class {name}Listener(BaseListener):
    async def handle(self, event: BaseEvent) -> None:
        self._log.info(f"Handling {{event.name}}")
''', f"Listener {name}Listener")


if __name__ == "__main__":
    app()
