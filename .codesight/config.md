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
- `DREAMFERENCE_SANDBOX` (has default) — dreamference/config/dreamference_config.py
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
