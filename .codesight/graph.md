# Dependency Graph

## Most Imported Files (change these carefully)

- `dreamference/hardware.py` — imported by **18** files
- `dreamference/config.py` — imported by **12** files
- `dreamference/vllm_server.py` — imported by **11** files
- `dreamference/hardware/model_matrix_registry.py` — imported by **11** files
- `dreamference/chat/onyx_brand_assets.py` — imported by **8** files
- `dreamference/vllm_server/vllm_server_manager.py` — imported by **7** files
- `dreamference/chat/gmail_search_service.py` — imported by **6** files
- `dreamference/runner/goose_runner.py` — imported by **6** files
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

- `dreamference/hardware.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/cli/model_deep_inspector.py`, `dreamference/config/dreamference_config.py`, `dreamference/runner/aider_runner.py` +13 more
- `dreamference/config.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/runner/aider_runner.py`, `dreamference/runner/cline_runner.py`, `dreamference/runner/codex_runner.py` +7 more
- `dreamference/vllm_server.py` ← `dreamference/chat/onyx_runner.py`, `dreamference/cli/dreamference_cli_controller.py`, `dreamference/runner/aider_runner.py`, `dreamference/runner/cline_runner.py`, `dreamference/runner/codex_runner.py` +6 more
- `dreamference/hardware/model_matrix_registry.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/dreamference_config.py`, `dreamference/hardware/__init__.py`, `dreamference/hardware/hardware_manager.py`, `dreamference/hardware/model_downloader.py` +6 more
- `dreamference/chat/onyx_brand_assets.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/desktop_runner.py`, `dreamference/chat/onyx_runner.py`, `dreamference/chat/onyx_ui_fonts.py`, `dreamference/chat/onyx_ui_labels.py` +3 more
- `dreamference/vllm_server/vllm_server_manager.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/dreamference_config.py`, `dreamference/hardware/model_downloader.py`, `dreamference/vllm_server/__init__.py`, `dreamference/vllm_server/diffusion_server_manager.py` +2 more
- `dreamference/chat/gmail_search_service.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/gmail_credentials.py`, `dreamference/chat/onyx_runner.py`, `dreamference/chat/onyx_ui_scripts.py`, `tests/test_onyx_runner.py` +1 more
- `dreamference/runner/goose_runner.py` ← `dreamference/runner/__init__.py`, `dreamference/runner/aider_runner.py`, `dreamference/runner/cline_runner.py`, `dreamference/runner/codex_runner.py`, `dreamference/runner/continue_runner.py` +1 more
- `dreamference/config/dreamference_config.py` ← `dreamference/cli/dreamference_cli_controller.py`, `dreamference/config/__init__.py`, `dreamference/vllm_server/vllm_server_manager.py`, `tests/test_config.py`, `tests/test_vllm_server.py`
- `dreamference/chat/onyx_ui_overrides.py` ← `dreamference/chat/__init__.py`, `dreamference/chat/onyx_runner.py`, `tests/test_onyx_runner.py`, `tests/test_onyx_ui_scripts.py`
