"""Guards shared by every test: nothing may touch the machine's containers, services or the real
home folder.

Until Onyx's retirement the first guard here kept tests away from the live web chat: a test that
reached its `configure()` unmocked once rewrote the real Onyx `.env` and recreated the live nginx
container. Its successors are below: no real `docker` command that changes something, no sudo, no
systemd unit, and the one-time offer to remove Onyx's leftovers never made.
"""

import os
import sys
import threading
from pathlib import Path

import pytest

# Resolved before any test changes HOME. Every dreamference module is imported here, so the
# constants they compute from the home folder at import exist to be redirected below.
REAL_HOME = os.path.realpath(os.path.expanduser("~"))
# The checkout may itself live under the home folder; paths into it (the codex submodule, the
# patch series, the desktop project) are source the tests read, not state they could clobber.
CHECKOUT = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir))
import dreamference.cli.dreamference_cli_controller  # noqa: E402,F401 - imports every subsystem
import dreamference.mcp_server  # noqa: E402,F401
from dreamference.chat.google_service import GoogleService  # noqa: E402
from dreamference.chat.retired_web_chat import RetiredWebChat  # noqa: E402

# `server start` starts the Google service on a node, and `google start` creates its container.
REAL_GOOGLE_SERVICE_START = GoogleService.start
# Every interactive `ling-admin` run may offer to remove the retired web chat's containers; the
# fixture below never lets it, and its own tests restore this.
REAL_RETIRED_OFFER = RetiredWebChat.offer
from dreamference.chat.image_search_sidecar import ImageSearchSidecar  # noqa: E402
from dreamference.chat.speech_sidecar import SpeechSidecar  # noqa: E402

# `server start` on a node also starts image search and speech-to-text when absent (ASK §19.6).
REAL_IMAGE_SEARCH_START = ImageSearchSidecar.start
REAL_SPEECH_START = SpeechSidecar.start
from dreamference.node.node_advertiser import NodeAdvertiser as _NodeAdvertiser  # noqa: E402

# Runs a command through sudo; the fixture below replaces it, and a test of it restores it.
REAL_RUN_PRIVILEGED = _NodeAdvertiser.run_privileged
from dreamference.vllm_server.vllm_server_manager import VLLMServerManager  # noqa: E402

# `server start` stops the code index's systemd scopes; the fixture below replaces it.
REAL_STOP_INDEX_SCOPES = VLLMServerManager._stop_index_scopes
from dreamference.vllm_server.sandbox_prerequisite import SandboxPrerequisite  # noqa: E402

# Every `ling-admin` run checks bubblewrap through a transient unit of the user's systemd and may
# ask a question; the fixture below replaces the check, and its own tests restore this.
REAL_SANDBOX_GATE = SandboxPrerequisite.gate
from dreamference.vllm_server.model_gate import ModelGate  # noqa: E402

# Asks the model server's gate what it does: an HTTP request to the configured server, which in the
# suite would be this machine's live one. The fixture below answers "no gate"; its tests restore it.
REAL_GATE_PROBE = ModelGate.probe
# The name MemoryPressureWatchdog gives its thread, and how long a stopped one may take to exit.
PSI_THREAD_NAME = "psi-watchdog"
LEAK_GRACE_S = 2.0


@pytest.fixture(autouse=True)
def _isolate_services(monkeypatch):
    # `server start` stops the code index's scopes and starts the Google service, image search and
    # speech-to-text on a node; a
    # `ling-admin` run may offer to remove Onyx's leftovers. None of it may happen for real.
    monkeypatch.setattr(VLLMServerManager, "_stop_index_scopes", classmethod(lambda cls: None))
    monkeypatch.setattr(GoogleService, "start", classmethod(lambda cls: True))
    monkeypatch.setattr(RetiredWebChat, "offer", classmethod(lambda cls, command: None))
    monkeypatch.setattr(ImageSearchSidecar, "start", classmethod(lambda cls, *a, **k: True))
    monkeypatch.setattr(SpeechSidecar, "start", classmethod(lambda cls, *a, **k: True))


@pytest.fixture(autouse=True)
def _isolate_node_advert(tmp_path_factory, monkeypatch):
    # `server start` and `server stop` rewrite the node's Avahi service file when one exists
    # (specs/DREAMFERENCE_MIGHTLING_NODE.md §5.2). It lives under /etc, which the home isolation
    # below does not reach: without this, a server test on an advertised node would change what
    # the real node tells the network. sudo is never run from a test either.
    from dreamference.node import NodeAdvertiser, NodeServiceFile

    scratch = tmp_path_factory.mktemp("avahi") / "mightling-node.service"
    monkeypatch.setattr(NodeServiceFile, "service_path", scratch)
    monkeypatch.setattr(NodeAdvertiser, "run_privileged", classmethod(lambda cls, command, purpose, yes=False: False))
    # Whether this machine has Avahi must not decide a test (it does not on a CI runner).
    monkeypatch.setattr(NodeAdvertiser, "avahi_installed", classmethod(lambda cls: True))


@pytest.fixture(autouse=True)
def _no_passwordless_sudo(monkeypatch):
    # Whether sudo needs a password on this machine must not decide a test, and asking it is a
    # real sudo; a test of the no-password path says so itself.
    from dreamference.vllm_server import HostSafetySetup

    monkeypatch.setattr(HostSafetySetup, "passwordless_sudo", classmethod(lambda cls: False))


@pytest.fixture(autouse=True)
def _skip_sandbox_gate(monkeypatch):
    monkeypatch.setattr(SandboxPrerequisite, "gate", classmethod(lambda cls, command, subcommand: True))


@pytest.fixture(autouse=True)
def _no_model_gate_probe(monkeypatch):
    monkeypatch.setattr(ModelGate, "probe", classmethod(lambda cls, host, timeout=2.0: None))


@pytest.fixture(autouse=True)
def _refuse_real_docker(monkeypatch):
    # A test that reached the retired web chat's Gmail start ran `docker rm -f dreamference-gmail`
    # and `docker run` for real, replacing the live Gmail sidecar with one mounting a pytest temp
    # folder and a test secret: Gmail search answered "unauthorised" until it was recreated
    # (2026-09-29). Every real docker command from a test now fails that test;
    # tests that exercise docker paths mock subprocess themselves, which replaces this guard.
    import subprocess

    def guarded(original):
        def run(*args, **kwargs):
            argv = args[0] if args else kwargs.get("args")
            program = argv[0] if isinstance(argv, (list, tuple)) and argv else str(argv).split(" ")[0]
            if os.path.basename(str(program)) == "docker" and _changes_something(argv):
                raise AssertionError(f"a test tried to run a real docker command: {argv!r}; mock it")
            # `server start` stops the code index's scopes before its host-safety pre-flight
            # (specs/DREAMFERENCE_MIGHTLING_CODE_INDEX.md §9.2): a test must never stop, freeze or
            # start a unit of the user's own systemd.
            if os.path.basename(str(program)) in ("systemctl", "systemd-run") and _changes_systemd(argv):
                raise AssertionError(f"a test tried to run a real systemd command: {argv!r}; mock it")
            # Provisioning (specs/DREAMFERENCE_MIGHTLING_FLEET.md §14): no test may reach another
            # machine or become root.
            if os.path.basename(str(program)) in ("ssh", "scp", "rsync", "sudo", "sg"):
                raise AssertionError(f"a test tried to run a real {os.path.basename(str(program))}: {argv!r}; mock it")
            return original(*args, **kwargs)
        return run

    for name in ("run", "call", "check_call", "check_output", "Popen"):
        monkeypatch.setattr(subprocess, name, guarded(getattr(subprocess, name)))


# Docker subcommands that only read. Launch-command tests ask `docker info` and `docker image
# inspect`, which change nothing; anything else touches the machine's containers.
READ_ONLY_DOCKER: tuple = ("info", "version", "inspect", "ps", "images", "port", "logs", "stats")


# systemctl verbs that only read.
READ_ONLY_SYSTEMCTL: tuple = ("show", "status", "is-active", "is-enabled", "is-failed", "list-units", "show-environment", "cat")


def _changes_systemd(argv) -> bool:
    words = [str(w) for w in argv[1:]] if isinstance(argv, (list, tuple)) else str(argv).split()[1:]
    if os.path.basename(str(argv[0] if isinstance(argv, (list, tuple)) else str(argv).split()[0])) == "systemd-run":
        return True
    verbs = [w for w in words if not w.startswith("-")]
    return bool(verbs) and verbs[0] not in READ_ONLY_SYSTEMCTL


def _changes_something(argv) -> bool:
    words = [str(w) for w in argv[1:]] if isinstance(argv, (list, tuple)) else str(argv).split()[1:]
    words = [w for w in words if not w.startswith("-")]
    if not words:
        return False
    if words[0] in READ_ONLY_DOCKER:
        return False
    if words[0] in ("image", "container", "network", "volume") and len(words) > 1:
        return words[1] not in ("inspect", "ls")
    return True


@pytest.fixture(autouse=True)
def _no_leaked_watchdog():
    # A background `start_server` leaves its PSI watchdog running. One test did so against the
    # real /proc/pressure/memory, and the thread's `docker inspect` retries were counted by a
    # later test's fake `subprocess.run`, which then failed only when run after it (2026-10-03).
    # A test that starts a watchdog must stop it, or keep it from starting.
    before = {thread.ident for thread in threading.enumerate() if thread.name == PSI_THREAD_NAME}
    yield
    leaked = []
    for thread in threading.enumerate():
        if thread.name != PSI_THREAD_NAME or thread.ident in before:
            continue
        thread.join(timeout=LEAK_GRACE_S)  # a stopped watchdog may still be finishing a sample
        if thread.is_alive():
            leaked.append(thread)
    if leaked:
        pytest.fail(f"the test left {len(leaked)} PSI watchdog thread(s) running; stop them")


@pytest.fixture(autouse=True)
def _isolate_home(tmp_path_factory, monkeypatch):
    # Runners write their agents' configs under `~`: `~/.continue/config.json`, Codex's home,
    # and more. Tests used to run against the real home folder, and every run rewrote the user's
    # Continue config with a test model the machine does not serve. Each test gets its own home.
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    # The HuggingFace cache follows these before HOME; a user's own setting would lead a test
    # that builds a docker command into creating folders in the real cache.
    for name in ("HF_HOME", "HF_HUB_CACHE", "XDG_CACHE_HOME"):
        monkeypatch.delenv(name, raising=False)
    # `ling` exports CODEX_HOME to every command it runs, so a suite started by the agent, or by
    # Night Shift's sandboxed test run, resolved `$CODEX_HOME/night` and the rest to the real
    # ~/.mightling whatever HOME said: outside a sandbox it wrote the real `night/runner.lock`, and
    # inside one that write failed a test (2026-10-02). A test that needs the variable sets it.
    monkeypatch.delenv("CODEX_HOME", raising=False)
    # The rename migration's switch (legacy_name_migration.py): a developer's shell setting must not
    # decide whether a test migrates. A test that means to migrate sets it.
    monkeypatch.delenv("MIGHTLING_LEGACY_MIGRATION", raising=False)

    # HOME alone does not reach paths a module resolved at import, like VLLM_CACHE_HOME: a test
    # that ran start_server stamped the real ~/.cache/dreamference/vllm/.compile_signature with a
    # test model's signature, so the next real `server start` saw a mismatch and discarded a
    # 467 MB torch.compile cache (an 8-12 minute recompile). Every string or Path attribute of a
    # dreamference module that lies under the real home is re-pointed at the same place under the
    # test's home -- including copies another module took with `from ... import`.
    for module_name, module in list(sys.modules.items()):
        if module is None or not (module_name == "dreamference" or module_name.startswith("dreamference.")):
            continue
        for attribute, value in list(vars(module).items()):
            if attribute.startswith("__"):
                continue
            if isinstance(value, (str, Path)) and _under_real_home(value):
                relocated = home / os.path.relpath(str(value), REAL_HOME)
                monkeypatch.setattr(module, attribute, type(value)(relocated) if isinstance(value, Path) else str(relocated))


def _under_real_home(value) -> bool:
    text = str(value)
    if text == CHECKOUT or text.startswith(CHECKOUT + os.sep):
        return False
    return text == REAL_HOME or text.startswith(REAL_HOME + os.sep)


# Test-only vLLM recipes. The registry serves one model, on SGLang, so the vLLM launcher's generic
# machinery (a recipe's speculative config, a pinned image, the KV dtype, self-speculation, env
# vars across the container boundary) is exercised against these instead. Their shapes are those
# of the Qwen 3.5 122B and Qwen 3.6 35B recipes the registry carried until 2026-10-07.
VLLM_TEST_RECIPES = {
    "test-vllm-dflash": dict(
        name="Test vLLM recipe (INT4 AutoRound + external drafter)", params_b=122.0,
        supported_precisions=["AUTOROUND-INT4"], min_memory_gb=71.5, max_memory_gb=120.0,
        compatible_gb10=True, notes="Test only.", hf_repo_id="example/vllm-dflash-int4-AutoRound",
        supports_vision=True,
        launch_overrides={
            "attention_backend": "flash_attn",
            "docker_image": "example-vllm-dflash:1",
            "enable_prefix_caching": True,
            "env": {"VLLM_MARLIN_USE_ATOMIC_ADD": "1"},
            "extra_args": ["--max-num-seqs", "8", "--tensor-parallel-size", "1", "--dtype", "auto",
                           "--default-chat-template-kwargs", '{"enable_thinking": false}'],
            "gpu_memory_utilization": 0.7,
            "kv_cache_dtype": "auto",
            "max_model_len": 32768,
            "max_num_batched_tokens": 9048,
            "reasoning_parser": "qwen3",
            "speculative_config": {"attention_backend": "FLASH_ATTN", "method": "dflash",
                                   "model": "example/vllm-dflash-drafter", "num_speculative_tokens": 12},
            "tool_call_parser": "qwen3_xml",
        },
    ),
    "test-vllm-nvfp4": dict(
        name="Test vLLM recipe (NVFP4 + self-speculation)", params_b=35.0,
        supported_precisions=["NVFP4"], min_memory_gb=25.0, max_memory_gb=60.0,
        compatible_gb10=True, notes="Test only.", hf_repo_id="example/vllm-moe-NVFP4",
        launch_overrides={
            "attention_backend": "flashinfer",
            "env": {"VLLM_MARLIN_USE_ATOMIC_ADD": "1"},
            "extra_args": ["--max-num-seqs", "4", "--tensor-parallel-size", "1", "--dtype", "auto"],
            "gpu_memory_utilization": 0.3,
            "kv_cache_dtype": "fp8",
            "max_model_len": 32768,
            "max_num_batched_tokens": 8192,
            "reasoning_parser": "qwen3",
            "speculative_config": {"method": "mtp", "moe_backend": "triton", "num_speculative_tokens": 3},
            "tool_call_parser": "qwen3_xml",
        },
    ),
    "test-vllm-dflash-draft": dict(
        name="Test drafter", params_b=0.8, supported_precisions=["BF16"], min_memory_gb=1.5,
        max_memory_gb=2.5, compatible_gb10=True, notes="Test only.",
        hf_repo_id="example/vllm-dflash-drafter",
    ),
}


@pytest.fixture
def vllm_recipes(monkeypatch):
    """Adds the test-only vLLM recipes to the model registry for one test."""
    from dreamference.hardware.model_matrix_registry import ModelMatrixRegistry
    from dreamference.hardware.model_spec import ModelSpec

    for key, fields in VLLM_TEST_RECIPES.items():
        monkeypatch.setitem(ModelMatrixRegistry.MATRIX, key, ModelSpec(**fields))
    return VLLM_TEST_RECIPES
