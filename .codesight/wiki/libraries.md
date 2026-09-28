# Libraries

> **Navigation aid.** Library inventory extracted via AST. Read the source files listed here before modifying exported functions.

**81 library files** across 4 modules

## Dreamference (61 files)

- `dreamference/hardware/__init__.py` — resolve_model_hf_repo, get_model_launch_overrides, get_speculative_draft_repo, model_supports_vision, model_is_diffusion, model_declares_own_quantization, …
- `dreamference/chat/image_search_service.py` — sniff_image_type, phash64, hamming, openapi_definition, build_service, serve, …
- `dreamference/vllm_server/diffusion_openai_service.py` — build_handler, main, DiffusionModelRunner
- `dreamference/chat/gmail_search_service.py` — openapi_definition, GmailSearchService
- `dreamference/cli/dreamference_cli_controller.py` — main, DreamferenceCLIController
- `dreamference/mcp_server/mcp_server.py` — main, MCPServer
- `dreamference/vllm_server/model_loading_monitor.py` — create_model_loading_monitor, ModelLoadingMonitor
- `dreamference/vllm_server/psi_watchdog.py` — read_memory_pressure_full, MemoryPressureWatchdog
- `dreamference/web_canvas.py` — start_web_canvas_server, CanvasHandler
- `dreamference/chat/desktop_installer.py` — DesktopInstaller
- `dreamference/chat/desktop_runner.py` — DesktopRunner
- `dreamference/chat/gmail_credentials.py` — GmailCredentials
- `dreamference/chat/onyx_brand_assets.py` — OnyxBrandAssets
- `dreamference/chat/onyx_installer.py` — OnyxInstaller
- `dreamference/chat/onyx_runner.py` — OnyxRunner
- `dreamference/chat/onyx_ui_fonts.py` — OnyxUIFonts
- `dreamference/chat/onyx_ui_labels.py` — OnyxUILabels
- `dreamference/chat/onyx_ui_overrides.py` — OnyxUIOverrides
- `dreamference/chat/onyx_ui_scripts.py` — OnyxUIScripts
- `dreamference/cli/model_deep_inspector.py` — ModelDeepInspector
- `dreamference/config/config_file_storage_manager.py` — ConfigFileStorageManager
- `dreamference/config/config_generator.py` — generate_default_init_config
- `dreamference/config/config_path_resolver.py` — ConfigPathResolver
- `dreamference/config/dreamference_config.py` — DreamferenceConfig
- `dreamference/context_engine/ast_symbol_extractor.py` — ASTSymbolExtractor
- _…and 36 more files_

## Scratch (12 files)

- `scratch/vllm_files/engine_protocol.py` — validate_structural_tag_response_format, validate_structural_tag_payload, validate_structured_outputs_structural_tag, get_logits_processors, OpenAIBaseModel, ErrorInfo, …
- `scratch/vllm_files/api_server.py` — build_app, create_server_socket, create_server_unix_socket, validate_api_server_args, setup_server, build_async_engine_client, …
- `scratch/vllm_files/protocol.py` — ChatMessage, ChatCompletionLogProb, ChatCompletionLogProbsContent, ChatCompletionLogProbs, ChatCompletionResponseChoice, ChatCompletionResponse, …
- `scratch/vllm_extract/sampling_params.py` — validate_thinking_token_budget, SamplingType, StructuredOutputsParams, RepetitionDetectionParams, RequestOutputKind, SamplingParams, …
- `scratch/vllm_files/sampling_params.py` — validate_thinking_token_budget, SamplingType, StructuredOutputsParams, RepetitionDetectionParams, RequestOutputKind, SamplingParams, …
- `scratch/vllm_files/chat_api_router.py` — chat, batch_chat, attach_router, create_chat_completion, create_batch_chat_completion
- `scratch/vllm_files/block_pool.py` — BlockHashToBlockMap, BlockPool
- `scratch/vllm_files/kv_cache_manager.py` — KVCacheBlocks, KVCacheManager
- `scratch/test_api.py` — test_request
- `scratch/vllm_files/chat_serving.py` — OpenAIServingChat
- `scratch/vllm_files/comp_serving.py` — OpenAIServingCompletion
- `scratch/vllm_files/scheduler.py` — Scheduler

## Runtime (7 files)

- `runtime/patch_opt_in_cache.py` — apply_patch, main
- `runtime/patch_int8_lmhead_v3.py` — main
- `runtime/patch_kv_unify.py` — main
- `runtime/patch_mamba_checkpoint_chunks.py` — main
- `runtime/patch_mamba_chunk_align.py` — main
- `runtime/patch_prefix_align.py` — main
- `runtime/patch_unify_downscale.py` — main

## Squash_todays_commits.py (1 files)

- `squash_todays_commits.py` — run_git, main

---
_Back to [overview.md](./overview.md)_