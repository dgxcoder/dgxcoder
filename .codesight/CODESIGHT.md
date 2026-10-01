# dgxcoder — AI Context Map

> **Stack:** raw-http | none | unknown | javascript

> 0 routes | 0 models | 0 components | 81 lib files | 24 env vars | 0 middleware | 0% test coverage
> **Token savings:** this file is ~4 400 tokens. Without it, AI exploration would cost ~33 300 tokens. **Saves ~28 900 tokens per conversation.**
> **Last scanned:** 2026-08-31 20:37 — re-run after significant changes

---

# Libraries

- `dreamference/chat/desktop_installer.py` — class DesktopInstaller
- `dreamference/chat/desktop_runner.py` — class DesktopRunner
- `dreamference/chat/gmail_credentials.py` — class GmailCredentials
- `dreamference/chat/gmail_search_service.py` — function openapi_definition: (base_url) -> Dict[str, Any], class GmailSearchService
- `dreamference/chat/image_search_service.py`
  - function sniff_image_type: (payload) -> Optional[str]
  - function phash64: (image) -> int
  - function hamming: (a, b) -> int
  - function openapi_definition: (base_url) -> Dict[str, Any]
  - function build_service: () -> ImageSearchService
  - function serve: (port, secret) -> None
  - _...7 more_
- `dreamference/chat/onyx_brand_assets.py` — class OnyxBrandAssets
- `dreamference/chat/onyx_installer.py` — class OnyxInstaller
- `dreamference/chat/onyx_runner.py` — class OnyxRunner
- `dreamference/chat/onyx_ui_fonts.py` — class OnyxUIFonts
- `dreamference/chat/onyx_ui_labels.py` — class OnyxUILabels
- `dreamference/chat/onyx_ui_overrides.py` — class OnyxUIOverrides
- `dreamference/chat/onyx_ui_scripts.py` — class OnyxUIScripts
- `dreamference/cli/dreamference_cli_controller.py` — function main: () -> None, class DreamferenceCLIController
- `dreamference/cli/model_deep_inspector.py` — class ModelDeepInspector
- `dreamference/config/config_file_storage_manager.py` — class ConfigFileStorageManager
- `dreamference/config/config_generator.py` — function generate_default_init_config: (target_path) -> Path
- `dreamference/config/config_path_resolver.py` — class ConfigPathResolver
- `dreamference/config/dreamference_config.py` — class DreamferenceConfig
- `dreamference/context_engine/ast_symbol_extractor.py` — class ASTSymbolExtractor
- `dreamference/context_engine/code_symbol.py` — class CodeSymbol
- `dreamference/context_engine/context_engine.py` — class ContextEngine
- `dreamference/context_engine/embedding_calculator.py` — class EmbeddingCalculator
- `dreamference/context_engine/indexed_file.py` — class IndexedFile
- `dreamference/context_engine/sqlite_context_storage.py` — class SQLiteContextStorage
- `dreamference/context_engine/tfidf_calculator.py` — class TFIDFCalculator
- `dreamference/hardware/__init__.py`
  - function resolve_model_hf_repo: (model_key) -> str
  - function get_model_launch_overrides: (model_key) -> Dict[str, Any]
  - function get_speculative_draft_repo: (model_key) -> Optional[str]
  - function model_supports_vision: (model_key) -> bool
  - function model_is_diffusion: (model_key) -> bool
  - function model_declares_own_quantization: (model_key) -> bool
  - _...12 more_
- `dreamference/hardware/hardware_manager.py` — class HardwareManager
- `dreamference/hardware/hardware_telemetry.py` — class HardwareTelemetry
- `dreamference/hardware/memory_metrics.py` — class MemoryMetrics
- `dreamference/hardware/model_downloader.py` — class ModelDownloader
- `dreamference/hardware/model_matrix_registry.py` — class ModelMatrixRegistry
- `dreamference/hardware/model_spec.py` — class ModelSpec
- `dreamference/mcp_server/editor_selection.py` — class EditorSelection
- `dreamference/mcp_server/ide_state.py` — class IDEState
- `dreamference/mcp_server/mcp_server.py` — function main: () -> None, class MCPServer
- `dreamference/mcp_server/mcp_tool_registry.py` — class MCPToolRegistry
- `dreamference/mcp_server/web_tools.py` — class WebTools
- `dreamference/runner/cline_installer.py` — class ClineInstaller
- `dreamference/runner/cline_runner.py` — class ClineRunner
- `dreamference/runner/codex_installer.py` — class CodexInstaller
- `dreamference/runner/codex_runner.py` — class CodexRunner
- `dreamference/runner/continue_installer.py` — class ContinueInstaller
- `dreamference/runner/continue_runner.py` — class ContinueRunner
- `dreamference/runner/openhands_installer.py` — class OpenHandsInstaller
- `dreamference/runner/openhands_runner.py` — class OpenHandsRunner
- `dreamference/vllm_server/diagnostics.py` — class ContainerDiagnostics
- `dreamference/vllm_server/diffusion_openai_service.py`
  - function build_handler: (runner) -> type
  - function main: () -> None
  - class DiffusionModelRunner
- `dreamference/vllm_server/diffusion_server_manager.py` — class DiffusionServerManager
- `dreamference/vllm_server/model_loading_monitor.py` — function create_model_loading_monitor: (vllm_manager, recipe_env_keys) -> ModelLoadingMonitor, class ModelLoadingMonitor
- `dreamference/vllm_server/psi_watchdog.py` — function read_memory_pressure_full: () -> Optional[Tuple[float, float]], class MemoryPressureWatchdog
- `dreamference/vllm_server/vllm_launch_options.py` — class VLLMLaunchOptions
- `dreamference/vllm_server/vllm_log_streamer.py` — class VLLMLogStreamer
- `dreamference/vllm_server/vllm_server_manager.py` — class VLLMServerManager
- `dreamference/vllm_server/vllm_server_status.py` — class VLLMServerStatus
- `dreamference/vllm_server/vllm_startup_monitor.py` — class VLLMStartupMonitor
- `dreamference/web_canvas.py` — function start_web_canvas_server: (port, daemon) -> threading.Thread, class CanvasHandler
- `runtime/patch_int8_lmhead_v3.py` — function main: ()
- `runtime/patch_kv_unify.py` — function main: () -> int
- `runtime/patch_mamba_checkpoint_chunks.py` — function main: () -> int
- `runtime/patch_mamba_chunk_align.py` — function main: () -> int
- `runtime/patch_opt_in_cache.py` — function apply_patch: (target, old, new, name) -> bool, function main: () -> int
- `runtime/patch_prefix_align.py` — function main: () -> int
- `runtime/patch_unify_downscale.py` — function main: () -> int
- `scratch/test_api.py` — function test_request: (enable_cache)
- `scratch/vllm_extract/sampling_params.py`
  - function validate_thinking_token_budget: (value) -> int | None
  - class SamplingType
  - class StructuredOutputsParams
  - class RepetitionDetectionParams
  - class RequestOutputKind
  - class SamplingParams
  - _...1 more_
- `scratch/vllm_files/api_server.py`
  - function build_app: (args, supported_tasks, ...] | None, model_config) -> FastAPI
  - function create_server_socket: (addr, int]) -> socket.socket
  - function create_server_unix_socket: (path) -> socket.socket
  - function validate_api_server_args: (args)
  - function setup_server: (args)
  - function build_async_engine_client: (args, *, usage_context, client_config, Any] | None) -> AsyncIterator[EngineClient]
  - _...7 more_
- `scratch/vllm_files/block_pool.py` — class BlockHashToBlockMap, class BlockPool
- `scratch/vllm_files/chat_api_router.py`
  - function chat: (request) -> OpenAIServingChat | None
  - function batch_chat: (request) -> OpenAIServingChatBatch | None
  - function attach_router: (app)
  - function create_chat_completion: (request, raw_request)
  - function create_batch_chat_completion: (request, raw_request)
- `scratch/vllm_files/chat_serving.py` — class OpenAIServingChat
- `scratch/vllm_files/comp_serving.py` — class OpenAIServingCompletion
- `scratch/vllm_files/engine_protocol.py`
  - function validate_structural_tag_response_format: (response_format, Any]) -> None
  - function validate_structural_tag_payload: (payload, *, parameter) -> None
  - function validate_structured_outputs_structural_tag: (structured_outputs) -> None
  - function get_logits_processors: (processors, pattern) -> list[Any] | None
  - class OpenAIBaseModel
  - class ErrorInfo
  - _...22 more_
- `scratch/vllm_files/kv_cache_manager.py` — class KVCacheBlocks, class KVCacheManager
- `scratch/vllm_files/protocol.py`
  - class ChatMessage
  - class ChatCompletionLogProb
  - class ChatCompletionLogProbsContent
  - class ChatCompletionLogProbs
  - class ChatCompletionResponseChoice
  - class ChatCompletionResponse
  - _...7 more_
- `scratch/vllm_files/sampling_params.py`
  - function validate_thinking_token_budget: (value) -> int | None
  - class SamplingType
  - class StructuredOutputsParams
  - class RepetitionDetectionParams
  - class RequestOutputKind
  - class SamplingParams
  - _...1 more_
- `scratch/vllm_files/scheduler.py` — class Scheduler
- `squash_todays_commits.py` — function run_git: (cmd) -> str, function main: ()

---

# Config

## Environment Variables

- `DISABLE_TELEMETRY` (has default) — dreamference/chat/onyx_runner.py
- `DOCKER_HOST` (has default) — dreamference/vllm_server/psi_watchdog.py
- `DREAMFERENCE_AGENT` (has default) — dreamference/config/dreamference_config.py
- `DREAMFERENCE_CHECKPOINT_CHUNK_BLOCKS` (has default) — runtime/patch_mamba_checkpoint_chunks.py
- `DREAMFERENCE_CHECKPOINT_DENSE_BLOCKS` (has default) — runtime/patch_mamba_checkpoint_chunks.py
- `DREAMFERENCE_CONFIG_PATH` **required** — dreamference/config/config_path_resolver.py
- `DREAMFERENCE_DIFFUSION_MODEL` **required** — dreamference/config/dreamference_config.py
- `DREAMFERENCE_DRAFT_MODEL` (has default) — dreamference/config/dreamference_config.py
- `DREAMFERENCE_HF_TOKEN` **required** — dreamference/hardware/model_downloader.py
- `DREAMFERENCE_MODEL` **required** — dreamference/config/dreamference_config.py
- `DREAMFERENCE_SEARXNG_URL` (has default) — dreamference/mcp_server/web_tools.py
- `DREAMFERENCE_SPECULATIVE_TOKENS` **required** — dreamference/config/dreamference_config.py
- `DREAMFERENCE_USE_TENSORIZER` **required** — dreamference/config/dreamference_config.py
- `DREAMFERENCE_VLLM_HOST` (has default) — dreamference/config/dreamference_config.py
- `GOA_GOOGLE_CLIENT_ID` (has default) — dreamference/chat/gmail_search_service.py
- `GOA_GOOGLE_CLIENT_SECRET` (has default) — dreamference/chat/gmail_search_service.py
- `HF_HOME` **required** — dreamference/hardware/model_downloader.py
- `HF_TOKEN` (has default) — dreamference/config/dreamference_config.py
- `PUFFIN_GMAIL_CONFIG` (has default) — dreamference/chat/gmail_search_service.py
- `PUFFIN_GMAIL_SECRET` (has default) — dreamference/chat/gmail_search_service.py
- `RUST_LOG` (has default) — dreamference/runner/codex_runner.py
- `SPARK_KEEP_BF16_LMHEAD` (has default) — runtime/patch_int8_lmhead_v3.py
- `VLLM_WORKER_MULTIPROC_METHOD` **required** — scratch/vllm_files/api_server.py

## Config Files

- `Dockerfile`

---

# Dependency Graph

## Most Imported Files (change these carefully)

- `dreamference/hardware.py` — imported by **18** files
- `dreamference/config.py` — imported by **12** files
- `dreamference/vllm_server.py` — imported by **11** files
- `dreamference/hardware/model_matrix_registry.py` — imported by **11** files
- `dreamference/chat/onyx_brand_assets.py` — imported by **8** files
- `dreamference/vllm_server/vllm_server_manager.py` — imported by **7** files
- `dreamference/chat/gmail_search_service.py` — imported by **6** files
- `dreamference/config/dreamference_config.py` — imported by **5** files
- `dreamference/chat/onyx_ui_overrides.py` — imported by **4** files
- `dreamference/context_engine.py` — imported by **4** files
- `dreamference/chat/__init__.py` — imported by **4** files
- `dreamference/context_engine/code_symbol.py` — imported by **4** files
- `dreamference/chat/desktop_installer.py` — imported by **3** files
- `dreamference/chat/onyx_runner.py` — imported by **3** files
- `dreamference/chat/onyx_ui_fonts.py` — imported by **3** files
- `dreamference/chat/onyx_ui_labels.py` — imported by **3** files
- `dreamference/chat/onyx_ui_scripts.py` — imported by **3** files
- `dreamference/chat/image_search_service.py` — imported by **3** files
- `dreamference/config/config_path_resolver.py` — imported by **3** files

## Import Map (who imports what)

- `dreamference/hardware.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/cli/model_deep_inspector.py`, `dreamference/config/dreamference_config.py`
- `dreamference/config.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/runner/cline_runner.py`, `dreamference/runner/codex_runner.py` +7 more
- `dreamference/vllm_server.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/runner/cline_runner.py`, `dreamference/runner/codex_runner.py` +6 more
- `dreamference/hardware/model_matrix_registry.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/dreamference_config.py`, `dreamference/hardware/__init__.py`, `dreamference/hardware/hardware_manager.py`, `dreamference/hardware/model_downloader.py` +6 more
- `dreamference/chat/onyx_brand_assets.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/desktop_runner.py`, `dreamference/chat/onyx_runner.py`, `dreamference/chat/onyx_ui_fonts.py`, `dreamference/chat/onyx_ui_labels.py` +3 more
- `dreamference/vllm_server/vllm_server_manager.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/dreamference_config.py`, `dreamference/hardware/model_downloader.py`, `dreamference/vllm_server/__init__.py`, `dreamference/vllm_server/diffusion_server_manager.py` +2 more
- `dreamference/chat/gmail_search_service.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/gmail_credentials.py`, `dreamference/chat/onyx_runner.py`, `dreamference/chat/onyx_ui_scripts.py`, `tests/test_onyx_runner.py` +1 more
- `dreamference/config/dreamference_config.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/__init__.py`, `dreamference/vllm_server/vllm_server_manager.py`, `tests/test_config.py`, `tests/test_vllm_server.py`
- `dreamference/chat/onyx_ui_overrides.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/onyx_runner.py`, `tests/test_onyx_runner.py`, `tests/test_onyx_ui_scripts.py`

---

# Test Coverage

> **0%** of routes and models are covered by tests
> 13 test files found

---

# CI/CD Pipelines

## GitHub Actions (1 workflow)

| Workflow | Triggers | Jobs | Deploy | Environments |
|---|---|---|---|---|
| Deploy docs to GitHub Pages | push | 2 | — | github-pages |

### Deploy docs to GitHub Pages

> `.github/workflows/docs.yml`

> Concurrency: `pages`

- **build** on `ubuntu-latest` — 6 steps
  - `actions/checkout@v4`
  - `actions/configure-pages@v4`
  - `actions/setup-python@v5`
  - `actions/upload-pages-artifact@v3`
- **deploy** on `ubuntu-latest` — 1 steps (needs: build)
  - `actions/deploy-pages@v4`

---
_Source: .github/workflows/docs.yml_
_Generated by codesight-cicd-plugin_

---

_Generated by [codesight](https://github.com/Houseofmvps/codesight) — see your codebase clearly_