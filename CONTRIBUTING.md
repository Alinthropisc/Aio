# Contributing to Aio

## Branch naming

```
feat/short-description
fix/short-description
chore/short-description
docs/short-description
```

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org):

```
feat(aioback): add refresh token endpoint
fix(aiomobile): resolve auth guard redirect loop
chore(deps): bump flutter_bloc to 9.1.1
docs(readme): update getting started section
```

## Pull requests

1. Branch off `main`
2. Keep PRs focused — one concern per PR
3. All CI checks must pass before merge
4. Add tests for any new behavior

## Code style

| App | Tool |
|---|---|
| aioback | `ruff format .` + `ruff check .` |
| aiofront / aiomini | ESLint + Prettier (via `npm run lint`) |
| aiomobile | `dart format lib/ test/` + `flutter analyze` |

Run `make lint` and `make format` before pushing.
