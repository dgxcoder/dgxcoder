# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Dreamference — a local, air-gapped agentic pair programmer targeting single-node **NVIDIA GB10 (Blackwell, SM121)** systems with 128 GB unified LPDDR5X memory. It wraps a third-party coding agent (Aider/Goose/Cline/Continue/OpenHands) around a locally-launched vLLM server running in Docker.

The venv is at `.venv/`. Use `.venv/bin/python` explicitly — there is no activation step assumed.

## Commands

```bash
# Install (editable)
.venv/bin/pip install -e .

# Full test suite (~8s, no GPU or Docker required — all hardware/subprocess calls are mocked)
.venv/bin/python -m pytest tests/ -q

# Single file / single test
.venv/bin/python -m pytest tests/test_vllm_server.py -q
.venv/bin/python -m pytest tests/test_vllm_server.py::test_nvfp4_model_applies_registry_launch_recipe -q

# Docs (mkdocs-material; CI publishes to GitHub Pages on push to main)
mkdocs serve

# Optional tensorizer-enabled vLLM image (only needed if the NGC tag lacks `tensorizer`)
docker build -t dreamference-vllm-tensorizer:26.07-py3 .
```

The CLI entry point is `dream` (`dreamference.cli:main`). Subcommands: `init`, `chat`, `run`, `status`, `index`, `mcp`, `web`, `endpoints`, `search`, `fetch`, `logs request`, `benchmark_server`, `server {start,stop,remove}`, `onyx {start,configure,status,logs,stop,uninstall}`, `model {list,download}`, `main-model {set,inspect}`, `clear {model-cache,tensorize-cache}`.

There is no linter or formatter configured.

## Architecture

Six subsystems under `dreamference/`, each a package whose `__init__.py` is a re-export facade with an explicit `__all__`:

| Package | Role |
| --- | --- |
| `config/` | 4-tier config resolution |
| `hardware/` | Model matrix registry, HF downloads/tensorization, GB10 telemetry |
| `vllm_server/` | Docker vLLM lifecycle, launch-arg construction, host-safety guards |
| `runner/` | Per-agent installer + runner pairs, sandbox prefixes |
| `context_engine/` | AST symbol extraction + TF-IDF/dense retrieval |
| `mcp_server/` | stdio MCP server for JetBrains/VS Code |

**Config precedence** (`config/dreamference_config.py`) — every field resolves through the same 4-step chain, in `DreamferenceConfig.__init__`: constructor kwarg → `DREAMFERENCE_*` env var → `dreamference.toml` (local, then `~/.config/dreamference/config.toml`) → module-level `DEFAULT_*` constant. `save_config()` deliberately writes only values that differ from the defaults, so a round-trip does not fossilize defaults into the TOML.

**A model may pin its own vLLM image.** `launch_overrides['docker_image']` overrides `DEFAULT_VLLM_IMAGE` for that model alone, because the engine is part of a recipe just as much as the flags are — `qwen3.5-122b-a10b-int4-dflash` runs on the thread's `ghcr.io/aeon-7/aeon-vllm-ultimate` build because the project image's vLLM trips a KV page-size assert on the DFlash drafter. Two consequences worth knowing before touching this: `ensure_docker_image()` *pulls* anything registry-qualified (a `/` in the name) and only *builds* the project's own bare-tag image, and `probe_image()` deliberately does not acquire an image — it reports on one that is already present, because it is called from `build_launch_command`, where a missing image must not start a multi-gigabyte download.

**Model matrix is the source of truth for launch flags.** `hardware/model_matrix_registry.py` holds `MATRIX: Dict[str, ModelSpec]`, and each spec carries `launch_overrides`. `VLLMServerManager.build_launch_command()` layers these over the generic defaults, so per-model vLLM tuning (context length, memory ratio, attention/MoE backend, tool-call and reasoning parsers, speculative config) belongs in the registry entry, **not** in the launch builder. Tests assert this layering directly.

**Runner dispatch is a strategy switch on `config.agent_runner`** in `cli/dreamference_cli_controller.py` (~line 346). Each agent has a matching `<agent>_installer.py` / `<agent>_runner.py` pair. Every runner follows the same shape: check vLLM health → provision the agent CLI if missing → translate Dreamference config into that agent's own CLI flags → `subprocess.call`. Adding an agent means adding the pair, exporting both from `runner/__init__.py`, and extending the dispatch chain.

**Host-safety subsystem** (`vllm_server/vllm_server_manager.py` + `psi_watchdog.py`). This is the least obvious part of the codebase and exists because unified memory means a model load can freeze the whole host rather than just OOM the container. Two layers:

- `VLLMServerManager.check_host_safety()` runs *before* a load — inspects swap, `sysctl` values, and whether `earlyoom`/`systemd-oomd` is present and correctly configured, and aborts with an explanation rather than risking a lockup.
- `MemoryPressureWatchdog` runs *during* a load — samples `/proc/pressure/memory` (PSI) on a thread, resolves the container's cgroup, and kills it if `avg10` spikes or `avg60` stays above threshold for the trip duration. The kill has three paths, chosen by what the host can still do: direct `SIGKILL` to the cgroup's PIDs (fastest, but needs root, which `dream` normally is not — `_probe_direct_kill` settles that with signal 0 while the host is healthy), a kill request over dockerd's unix socket (one connect and one write, no fork — the path that actually runs), and the `docker` CLI last, because forking a Go binary is the work least likely to be scheduled during a reclaim livelock. `_kill()` returns whether anything died, and the trip callback only fires when something did.

Host RAM exhaustion and GPU VRAM exhaustion are indistinguishable on GB10; the watchdog exists to make that distinction. Preserve both layers when touching `start_server()`.

**Onyx Lite is a service, not an agent** (`runner/onyx_runner.py`). It is a browser chat UI in front of the same vLLM endpoint the terminal agents use, so it lives under `dream onyx {start,configure,…}` rather than in the `--agent` switch — every entry in that switch is a CLI that Dreamference execs and waits on, and Onyx is a set of long-lived containers. Dreamference never writes Onyx's compose files; `onyx-cli deploy install --lite --no-prompt` selects the reduced stack (no Vespa, Redis, Celery, model servers or object storage — API server, web server and PostgreSQL only, ~900 MB resident). Two things are worth knowing before touching `configure()`: Onyx has **no environment variable for the LLM provider** — providers live in its database and are normally created by clicking through the Admin panel, so `configure` drives the same admin API, registering the first account (which becomes admin) if login fails; and `PUT /admin/llm/provider` **is not an upsert** despite the name — an `is_creation` query flag picks create or update and the endpoint rejects the mismatching case in both directions, which is why the provider is looked up by name first. The vLLM base URL is rewritten from loopback to the Docker bridge gateway, because vLLM runs with `--network host` while Onyx is on the default bridge, where `localhost` is the Onyx container itself.

**The Puffin rebrand stops at the licence boundary.** `apply_branding()` sets `company_name`, creates a public **Puffin** assistant carrying whatever `GET /tool` reports (minus `coding_agent`, which overlaps the terminal agents), and sets `disable_default_assistant` so users land on it — all community-edition settings. Onyx's actual whitelabelling (`application_name`, `hide_onyx_branding`, custom logo/greeting) lives in `ee/` behind `ENABLE_PAID_ENTERPRISE_EDITION_FEATURES` and is a **paid Enterprise feature**; Dreamference does not set that flag, so the browser tab, favicon and top-left logo stay Onyx's. The stock assistant is only retired once the Puffin one exists — a test covers that ordering, because reversing it leaves a user with no assistant at all. `--no-brand` skips the whole step.

The **logos are a separate matter from the settings**: `/logo.png`, `/logo-dark.png`, `/logotype*.png`, `/logo.svg` and `/onyx.ico` are ordinary static files the Next.js server hands out, so `onyx_brand_assets.py` renders Puffin versions with Pillow and `docker cp`s them into the web-server container — a file swap, not the licensed `use_custom_logo` path. They match the originals' dimensions exactly, since the frontend lays them out against those aspect ratios. Being container-filesystem writes, they do **not** survive an image upgrade or `deploy install --force`; re-running `dream onyx configure` restores them, and nothing binary is checked into the repo.

**The UI typeface is swapped at the `@font-face`, not at the `font-family`.** `onyx_ui_fonts.py` makes Onyx look like Telegram by replacing the three faces it ships — Hanken Grotesk (interface), KH Teka (a few headings), DM Mono (code) — with Roboto and Roboto Mono. Onyx names its UI face in around forty CSS declarations, most through the `--font-hanken-grotesk` variable `next/font` writes onto `<html>`; rewriting the four `@font-face` blocks instead leaves every declaration alone and only changes which file the name resolves to, so **the served CSS still says `Hanken Grotesk` everywhere and renders Roboto**. Roboto is fetched once from google/fonts, converted from variable TTF to WOFF2 with fontTools on the host, cached in `~/.cache/dreamference/fonts`, and served by Onyx itself from `/app/public/fonts` — no font CDN at page load. One non-obvious step: Next.js builds its static routes from `public/` **at boot**, so a face copied into a running container is on disk with no URL until the server restarts; `install()` restarts it, but only when it actually copied something. The stylesheets need no restart, being read per request.

**Dreamference's own CSS is appended, not substituted** (`onyx_ui_overrides.py`). Five rules today. The assistant message action bar (copy / like / dislike / TTS / regenerate) is hidden at `opacity:0` and revealed on hover of `[data-testid="onyx-ai-message"]`, the per-message wrapper that is the toolbar's own parent — targeting the `AgentMessage/*` controls and explicitly **not** their `AgentMessage/toolbar` parent, because that same flex row holds the citation list and the message switcher, which are content; using `opacity` rather than `display:none`, because the toolbar owns a layout row and removing it makes messages below jump as the pointer crosses; and pairing `:hover` with `:focus-within`, since there is no hover on a keyboard. And the sidebar is white (`html:not(.dark) .opal-sidebar-root__column`, scoped because `--background-tint-02` is what makes dark mode dark) with the selected row filled Tiffany Blue. **That second one is where specificity bites.** Onyx styles the row with `.interactive[data-interactive-variant=…][data-interactive-state=selected]` — a class plus two attributes — and its hover rule adds `:hover:not([data-disabled])`, so an override has to mirror that shape exactly and win on source order; the first attempt dropped the leading class, lost the tie, and left the row grey. The label and icons are recoloured through `--interactive-foreground` and its icon twin, not `color`, because `.interactive` is what reads and transitions them. And the user's own message bubble is white with a soft shadow instead of Onyx's grey fill — Telegram separates bubbles from the page with a shadow rather than a tint, and without one a white bubble on the near-white chat background has no edge at all; `#onyx-human-message` is a hand-written id, so it scopes the rule and outranks the Tailwind utility unaided. The chat canvas is white too, and **the grey is painted twice**: `body` carries it and so does a full-height app shell stacked on top, so whitening `body` alone repaints a surface nothing can see and leaves the visible canvas exactly as grey as before. The shell is pinned by `.bg-background` *and* `.min-h-screen` — the alias alone means "the app background" and is also what the citation chips inline in a response use as their fill, so whitening it outright leaves them blank. A white canvas is what makes the white bubble read as Telegram's rather than as a mistake: bubble and canvas are the same white, separated by the shadow alone. All four white surfaces use `--background-tint-00`, Onyx's own token for a plain surface (`#fff` in light mode), rather than a literal, and all three are scoped to `html:not(.dark)`, which leaves dark mode exactly as Onyx ships it. Finally the per-message agent avatar is hidden. Onyx lays each assistant message on a timeline — a fixed-width rail holding the avatar, a content column beside it — and the avatar is an SVG octagon with the agent's initial absolutely positioned inside, all Tailwind utilities with no id or test id; the one stable handle is the rail cell's arbitrary-value class, matched as `[class*="--timeline-rail-width"]` on the CSS variable it is built from rather than as an escaped class name. It is hidden with `visibility`, not `display`, because the rail is what the header row and the indented message body are aligned against — collapsing it slides the "Thought for Ns" header out from over the text it labels.

The block is appended to *every* stylesheet under `.next`, because Next.js splits CSS per route and no single sheet is loaded by every page. `OVERRIDE_MARKER` opens it and everything after is Dreamference's, so a re-run cuts at the marker and rewrites — appending only when the marker is absent would make later edits to the CSS unappliable. Selectors are pinned to `data-testid`, `data-*` state attributes and Onyx's hand-written BEM classes, never to Tailwind utilities, which are a fresh permutation on every build.

**Verifying a UI change means logging in, which means a same-origin page.** The Onyx chat view is client-rendered and behind auth, so `curl` shows an empty shell and a headless screenshot shows the login form. The way through: `docker cp` a scratch HTML file into `/app/public`, restart (Next.js builds its static routes at boot), then point headless Chromium at it — the page can `fetch('/api/auth/login')` and iframe `/app?chatId=…` because it is same-origin, and `frame-ancestors 'self'` permits the frame. From there `getComputedStyle` answers what actually applied. Two traps: overwriting that file needs no restart (only *new* routes do), and **the Chromium profile caches the CSS chunks** — reuse `--user-data-dir` across runs and you will verify against the stylesheet from before your change.

**The microphone needs a second model server.** Onyx's voice subsystem is complete but shows no mic button until an STT provider is registered, and vLLM cannot supply one — it serves a single model and has no `/v1/audio/transcriptions`. `enable_voice()` runs `speaches` (OpenAI-compatible Whisper) as the `dream-stt` sidecar on **CPU** — ctranslate2's CUDA support does not cover SM121, and dictation-length audio transcribes in ~5 s on GB10's cores with no GPU contention — joins it to Onyx's network, and registers it as an `openai` voice provider. One obstacle is not configurable: Onyx hardcodes the private-address exemption for voice endpoints to Azure alone (`allow_private_network = provider_type.lower() == "azure"`), ignoring the SSRF Protection setting, and its Azure provider speaks Azure Speech REST rather than OpenAI's protocol. `_allow_local_voice_endpoint()` widens that one line and **restarts the API server** (unlike the frontend patches, this is already-imported Python). A shim presenting Azure's protocol in front of Whisper would need no patch and survive upgrades — the better answer if this becomes load-bearing. `--no-voice` skips it all.

**Image input is a client-side claim, not a server capability.** `Qwen3_5MoeForConditionalGeneration` carries a `vision_config`, so vLLM accepts images for both Qwen3.5-122B entries without being told — but Onyx refuses the upload with *"The current model does not support image input"* unless its own model entry says otherwise. `ModelSpec.supports_vision` records it (verified against each checkpoint's `config.json`, never inferred from the alias), `model_supports_vision()` exposes it, and `configure()` sends it as `supports_image_input` **and** registers `POST /admin/llm/default-vision` — two separate settings, and uploads stay refused if only the first is set.

**Onyx web search is a provider registration, not a prompt.** Unlike the Codex runner — which appends `WEB_ACCESS_INSTRUCTIONS` to the system prompt because Codex has no search tool — Onyx ships **first-class SearXNG support** (`WebSearchProviderType.SEARXNG`, no API key), so `configure()` registers it at `POST /admin/web-search/search-providers` and Onyx's own base prompt already knows to search and then open results. `--no-web` skips it. Two constraints make the alternatives worse and are worth not rediscovering: appending to the prompt is capped at **500 characters** (`user_preferences` is the only global hook — the default assistant is a *builtin* persona and the API refuses to modify one), and reaching SearXNG through the LLM-driven `open_url` tool requires SSRF protection set all the way to `disabled`, since `outbound_allow_private_network()` is true for that level alone. The provider path is admin-configured and its client does no SSRF validation, so it reaches a private container address with the secure `validate_all` default untouched. SearXNG publishes only on `127.0.0.1`, so `_attach_searxng()` joins its container to Onyx's network — the bridge gateway that reaches vLLM does not reach it.

**Context engine** writes two artifacts into a gitignored `.dreamference/` at the workspace root: `context_index.json` (AST symbols + TF-IDF) and `context.db` (SQLite with FTS5 virtual tables and sqlite-vec embeddings). Both are rebuilt by `dream index --force`.

## Searching this codebase

`ast-grep` (v0.45) is installed and is the right tool for structural queries — "every call site of this shape", "every method with this signature" — which `rg` can only approximate with regex. The heavy repetition across the five runners makes these queries genuinely useful here.

**Always constrain the output.** `ast-grep` prints the *entire matched AST node*, so any pattern matching a declaration dumps the whole body. Measured on this repo: `-p 'class VLLMServerManager'` prints **1,306 lines**; `rg -n "^class VLLMServerManager"` prints **1**. The default output is a token bomb.

Use this form instead — it collapses matches to `file:line` (offset verified against `rg`):

```bash
ast-grep -p '<pattern>' -l python dreamference/ --json=compact \
  | jq -r '.[] | "\(.file):\(.range.start.line + 1)"'
```

On `def $N(cls, $$$A)` (25 matches) that is **1,223 bytes vs. 74,553** for the bare command — 61x smaller. Use `--files-with-matches` (465 bytes) when only the file set matters.

Patterns verified working on this tree:

```bash
'subprocess.call($$$)'              # 5 hits — every agent launch point
'self.vllm_manager.check_health()'  # 4 hits — the health gate each runner shares
'resolve_model_hf_repo($ARG)'       # 15 hits — alias→HF-repo translation sites
'shutil.which($X)'                  # 19 hits — every CLI-presence probe
'def $N(cls, $$$A)'                 # every classmethod
```

**Use `rg` for locating a definition** (`rg -n "^class Foo"` → one line, ~7 ms) and `ast-grep` for enumerating call sites by shape. Reaching for `ast-grep` to find a single symbol is strictly worse.

## Conventions

- **One class per file**, file named after the class in snake_case. `__init__.py` does the re-exporting; module files hold no top-level logic beyond constants.
- **Class-level `@classmethod` over instances** for stateless helpers — the codebase has ~56 classmethods against 16 `__init__`s. `SandboxManager`, `ModelMatrixRegistry`, and the installers are pure classmethod namespaces.
- Module docstrings and full Google-style Args/Returns docstrings on public methods are the norm; match this density.
- `typing.Final` annotations on module constants.
- User-facing output goes through `rich` console or emoji-prefixed `print` (`✅ ⚠️ ❌ 🚀 💡`). Match the existing voice in CLI paths.

## Gotchas

- **`dreamference/<name>.py` shim modules are dead code.** Files like `dreamference/config.py` containing `from dreamference.config.__init__ import *` are shadowed by the same-named package directory — Python resolves packages before modules, so these never execute. Editing them has no effect; edit the package.
- **README.md has drifted from the code.** It documents the default model as `qwen3.6-35b-a3b-nvfp4` and the default agent as Goose, but `DEFAULT_MODEL_ALIAS` is `qwen3.5-122b-a10b-int4-dflash` and `DEFAULT_AGENT_RUNNER` is `"aider"`. The test-count badge (15) is also stale — the suite is 114 tests. Trust the code; the README's `dreamference.toml` example is additionally malformed (unterminated strings, mixed TOML/YAML syntax).
- **The default model has not yet served a token on this machine.** `qwen3.5-122b-a10b-int4-dflash` (Intel AutoRound INT4 + the z-lab DFlash drafter) was added on 2026-08-15. Two load attempts on the project's own image both failed, and both failures are now understood and recorded: the first on `--kv-cache-dtype fp8`, which the config layer was forcing over the recipe and which FlashAttention rejects outright; the second, after all 72 GB of weights were resident, on `unify_kv_cache_spec_page_size`'s `assert new_spec.page_size_bytes == max_page_size` during KV profiling — the failure upstream's `runtime/patch_unify2.py` exists to fix, still live in vLLM 0.24. That is why the entry pins its own image. Neither attempt came near freezing the host: the pre-flight gates passed on real numbers and memory came straight back both times. The previously-loaded `qwen3.5-122b-a10b-nvfp4` recipe is kept as the fallback.
- **The torch.compile cache is persistent and only partly self-invalidating.** Every launch sets `VLLM_CACHE_ROOT` to `/root/.cache/dreamference/vllm`, inside the existing cache mount, so a graph compiled once survives container restarts (a cold compile is 8–12 minutes). vLLM names the cache directory after a hash of the engine config, traced sources and compiler — but `SpeculativeConfig.compute_hash()` contributes only whether the method needs auxiliary hidden states, **not `num_speculative_tokens`**, so retuning `n` alone would reuse the old graph. `VLLMServerManager._reset_stale_compile_cache()` covers that gap with its own `model|method|n` signature. Removal runs inside the image because the cache is written by a root container into a user-owned directory, which makes a host-side `rmtree` fail on the first subdirectory.
- `DREAMFERENCE_SPEC.md` is ~1000 lines. Read the specific numbered section you need (see its table of contents) rather than the whole file.
- `.aider*`, `.gemini/`, `.antigravity/`, `.dreamference/` are gitignored leftovers from other tooling — not part of the project.
