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

The CLI entry point is `dream` (`dreamference.cli:main`). Subcommands: `init`, `chat`, `run`, `status`, `index`, `mcp`, `web`, `endpoints`, `logs request`, `benchmark_server`, `server {start,stop,remove}`, `model {list,download}`, `main-model {set,inspect}`, `clear {model-cache,tensorize-cache}`.

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

**Model matrix is the source of truth for launch flags.** `hardware/model_matrix_registry.py` holds `MATRIX: Dict[str, ModelSpec]`, and each spec carries `launch_overrides`. `VLLMServerManager.build_launch_command()` layers these over the generic defaults, so per-model vLLM tuning (context length, memory ratio, attention/MoE backend, tool-call and reasoning parsers, speculative config) belongs in the registry entry, **not** in the launch builder. Tests assert this layering directly.

**Runner dispatch is a strategy switch on `config.agent_runner`** in `cli/dreamference_cli_controller.py` (~line 346). Each agent has a matching `<agent>_installer.py` / `<agent>_runner.py` pair. Every runner follows the same shape: check vLLM health → provision the agent CLI if missing → translate Dreamference config into that agent's own CLI flags → `subprocess.call`. Adding an agent means adding the pair, exporting both from `runner/__init__.py`, and extending the dispatch chain.

**Host-safety subsystem** (`vllm_server/vllm_server_manager.py` + `psi_watchdog.py`). This is the least obvious part of the codebase and exists because unified memory means a model load can freeze the whole host rather than just OOM the container. Two layers:

- `VLLMServerManager.check_host_safety()` runs *before* a load — inspects swap, `sysctl` values, and whether `earlyoom`/`systemd-oomd` is present and correctly configured, and aborts with an explanation rather than risking a lockup.
- `MemoryPressureWatchdog` runs *during* a load — samples `/proc/pressure/memory` (PSI) on a thread, resolves the container's cgroup, and kills it if `avg10` spikes or `avg60` stays above threshold for the trip duration. The kill has three paths, chosen by what the host can still do: direct `SIGKILL` to the cgroup's PIDs (fastest, but needs root, which `dream` normally is not — `_probe_direct_kill` settles that with signal 0 while the host is healthy), a kill request over dockerd's unix socket (one connect and one write, no fork — the path that actually runs), and the `docker` CLI last, because forking a Go binary is the work least likely to be scheduled during a reclaim livelock. `_kill()` returns whether anything died, and the trip callback only fires when something did.

Host RAM exhaustion and GPU VRAM exhaustion are indistinguishable on GB10; the watchdog exists to make that distinction. Preserve both layers when touching `start_server()`.

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
- **README.md has drifted from the code.** It documents the default model as `qwen3.6-35b-a3b-nvfp4` and the default agent as Goose, but `DEFAULT_MODEL_ALIAS` is `qwen3.5-122b-a10b-int4-dflash` and `DEFAULT_AGENT_RUNNER` is `"aider"`. The test-count badge (15) is also stale — the suite is 109 tests. Trust the code; the README's `dreamference.toml` example is additionally malformed (unterminated strings, mixed TOML/YAML syntax).
- **The default model has never been loaded on this machine.** `qwen3.5-122b-a10b-int4-dflash` (Intel AutoRound INT4 + the z-lab DFlash drafter) was added on 2026-08-15 from an upstream DGX Spark recipe and verified as far as it can be without loading it: `EngineArgs.create_engine_config()` was run inside the pinned image on the exact generated flags and resolved both architectures, auto-detected the `inc` quantization backend, and returned `method='dflash', n=8, parallel_drafting=True` with no warnings — and the memory arithmetic clears every pre-flight gate. But no weights have been loaded. The recipe it came from is documented in that registry entry's `notes`, including every setting deliberately not copied from upstream and why. The previously-loaded `qwen3.5-122b-a10b-nvfp4` recipe is kept as the fallback.
- **The torch.compile cache is persistent and only partly self-invalidating.** Every launch sets `VLLM_CACHE_ROOT` to `/root/.cache/dreamference/vllm`, inside the existing cache mount, so a graph compiled once survives container restarts (a cold compile is 8–12 minutes). vLLM names the cache directory after a hash of the engine config, traced sources and compiler — but `SpeculativeConfig.compute_hash()` contributes only whether the method needs auxiliary hidden states, **not `num_speculative_tokens`**, so retuning `n` alone would reuse the old graph. `VLLMServerManager._reset_stale_compile_cache()` covers that gap with its own `model|method|n` signature. Removal runs inside the image because the cache is written by a root container into a user-owned directory, which makes a host-side `rmtree` fail on the first subdirectory.
- `DREAMFERENCE_SPEC.md` is ~1000 lines. Read the specific numbered section you need (see its table of contents) rather than the whole file.
- `.aider*`, `.gemini/`, `.antigravity/`, `.dreamference/` are gitignored leftovers from other tooling — not part of the project.
