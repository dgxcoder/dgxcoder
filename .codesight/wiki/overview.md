# dgxcoder — Overview

> **Navigation aid.** This article shows WHERE things live (routes, models, files). Read actual source files before implementing new features or making changes.

**dgxcoder** is a javascript project built with raw-http.

## Scale

81 library files · 24 environment variables

**Libraries:** 81 files — see [libraries.md](./libraries.md)

## High-Impact Files

Changes to these files have the widest blast radius across the codebase:

- `dreamference/hardware.py` — imported by **18** files
- `dreamference/config.py` — imported by **12** files
- `dreamference/vllm_server.py` — imported by **11** files
- `dreamference/hardware/model_matrix_registry.py` — imported by **11** files
- `dreamference/chat/onyx_brand_assets.py` — imported by **8** files
- `dreamference/vllm_server/vllm_server_manager.py` — imported by **7** files

## Required Environment Variables

- `DREAMFERENCE_CONFIG_PATH` — `dreamference/config/config_path_resolver.py`
- `DREAMFERENCE_DIFFUSION_MODEL` — `dreamference/config/dreamference_config.py`
- `DREAMFERENCE_HF_TOKEN` — `dreamference/hardware/model_downloader.py`
- `DREAMFERENCE_MODEL` — `dreamference/config/dreamference_config.py`
- `DREAMFERENCE_SPECULATIVE_TOKENS` — `dreamference/config/dreamference_config.py`
- `DREAMFERENCE_USE_TENSORIZER` — `dreamference/config/dreamference_config.py`
- `HF_HOME` — `dreamference/hardware/model_downloader.py`
- `VLLM_WORKER_MULTIPROC_METHOD` — `scratch/vllm_files/api_server.py`

---
_Back to [index.md](./index.md) · Generated 2026-08-31_