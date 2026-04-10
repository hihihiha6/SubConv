# SubConv Agent Notes

## What matters

- SubConv ships three parts: a FastAPI backend in `subconv/`, a Vue/Vite frontend in `mainpage/`, and VitePress docs in `docs/`.
- `api.py` must keep exporting `app` from `subconv.app`; Vercel routes API traffic to `api.py`, and the CLI entrypoint also lives there.
- The public converter entrypoint is `subconv.converter.ConvertsV2Ray`; `subconv/subscription.py` falls back to it when incoming content is not Clash YAML.
- Runtime settings live in repo-root `config.yaml`; keep `config.yaml.example` in sync with the required fields.
- Runtime templates live in the repo-root `template/` directory. `zju.yaml` is the default template when `/sub` or `/proxy` omits the `template` query parameter.

## Local commands

- Install Python deps with `uv sync`.
- Backend runtime settings load from `config.yaml` when present, otherwise fall back to `config.yaml.example`; user-specific changes belong in `config.yaml`.
- Start the backend with `uv run python api.py` (host/port come from `config.yaml`).
- Frontend dev server: `cd mainpage && bun install && bun run dev`.
- Frontend production build: `cd mainpage && bun install && bun run build`.
- Docs dev server: `cd docs && bun install && bun run dev`.
- Docs production build: `cd docs && bun install && bun run build`.
- Nuitka/build dependencies are in the `build` group: use `uv sync --locked --group build` before local binary or image build work.

## Verification

- There is no dedicated backend test suite in this repo; the reliable checks are targeted Python validation plus buildability.
- For backend changes, prefer: `python3 -m compileall subconv api.py` and any focused smoke script needed for the touched parser/route.
- For frontend-only changes, the CI-equivalent check is `cd mainpage && bun install && bun run build`.
- For docs-only changes, the CI-equivalent check is `cd docs && bun install && bun run build`.
- If you touch packaging/build flow, also read the matching workflow under `.github/workflows/` and keep local verification aligned with it.
- After backend, frontend, config, CLI, deployment, or other user-facing changes, review `docs/` and `README*.md` to see whether documentation needs updating; when behavior or examples changed, update the docs in the same change.

## Architecture boundaries

- `subconv/app.py` owns all HTTP routes: `/`, `/sub`, `/provider`, `/proxy`, `/robots.txt`, plus static file serving from `mainpage/dist`.
- `subconv/cli.py` owns CLI parsing and `uvicorn.run(...)`; `api.py` is intentionally thin.
- `subconv/config.py` loads runtime settings from `config.yaml` and validates local templates from `template/*.yaml`; startup should fail fast if the configured default template is missing.
- `subconv/packer.py` assembles the final mihomo config. Its proxy-group filtering intentionally mutates the first group’s `proxies` list when removing empty groups.
- `subconv/converter/` is protocol-specific share-link parsing. Keep field aliases aligned with mihomo YAML keys.
- `docs/` is a standalone VitePress site deployed by GitHub Pages; keep it separate from app/Vercel runtime assumptions.

## Repo-specific gotchas

- `DISALLOW_ROBOTS` is evaluated with `eval()` in both `subconv.app` and `subconv.cli`; only use literal string values like `"True"` or `"False"`.
- `_split_sources()` in `subconv/app.py` treats `https://t.me/...` specially as standalone share links rather than remote subscription URLs.
- Converter behavior should stay aligned with mihomo’s converter/source conventions. Preserve the rule that per-line parsing only skips malformed links by catching `ParseError`, not broad exceptions.
- `static/` and frontend build output are not committed. Local backend UI serving depends on a manual `mainpage/dist` build.
- Frontend package management is Bun-based; keep `mainpage/package.json` and `mainpage/bun.lock` in sync.
- Docs package management is Bun-based; keep `docs/package.json` and `docs/bun.lock` in sync.

## Deployment and CI facts

- Vercel uses legacy `builds` in `vercel.json`: `@vercel/python` for `api.py` and `@vercel/static-build` for `mainpage/package.json`. Keep existing API paths (`/sub`, `/provider`, `/proxy`, `/robots.txt`) intact.
- Docker build is Alpine-based and compiles the backend with Nuitka, then copies `mainpage/dist`, `config.yaml.example`, and `template/` into the runtime image.
- `docker-compose.yml` mounts `./config.yaml:/app/config.yaml` and `./template:/app/template`; keep runtime template examples under `template/`, not `subconv/`.
- CI pins Python 3.13 and Bun 1.3.11 for the frontend build. `build.yml` builds binaries plus the frontend; `test-mainpage.yml` only verifies `mainpage` buildability.
- Docs deploy separately through a GitHub Pages workflow rooted at `docs/`; keep that workflow aligned with the original docs repo behavior, just using Bun.

## Contribution workflow

- README says contributors branch from `main` and open PRs against `dev` (or merge `main` into `dev` first, then PR to `dev`).
