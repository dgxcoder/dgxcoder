# Mightling — Claude delegates to ling: fewer Claude tokens, the same answers

**Status:** proposed on 2026-10-08. Nothing is built. The cost figures in §2 were measured on `gx10-9428` from this machine's own Claude Code transcripts (aggregates only; no content is quoted here). Every figure about `ling` doing the delegated work is an estimate until Phase 0 (§9) measures it.
**Target:** a person who uses Claude Code on a machine that runs Mightling, and wants Claude to spend fewer tokens without giving worse answers.
**Builds on:**
- `ling exec` (Codex's non-interactive mode, unmodified): `--output-schema`, `-o/--output-last-message`, `--ephemeral`, `-s/--sandbox`, `-C`, `--worktree` (`codex-rs/exec/src/cli.rs`, `codex-rs/utils/cli/src/shared_options.rs`);
- the launcher, which resolves the model server and writes the catalog ([MIGHTLING_CODEX](./DREAMFERENCE_MIGHTLING_CODEX.md));
- `ling-code`, the code index, which `ling` already queries ([MIGHTLING_CODE_INDEX](./DREAMFERENCE_MIGHTLING_CODE_INDEX.md));
- the skills planner, which links `~/.claude/skills` into `ling`'s catalogue ([MIGHTLING_SKILLS](./DREAMFERENCE_MIGHTLING_SKILLS.md));
- Night Shift's rule that an outside request wins, and the runner lock that SWE-bench holds ([MIGHTLING_NIGHT_SHIFT](./DREAMFERENCE_MIGHTLING_NIGHT_SHIFT.md) §5.5, [MIGHTLING_SWE_BENCH](./DREAMFERENCE_MIGHTLING_SWE_BENCH.md) §12).

**Decisions made here, stated first because each could be read the other way:**

1. **The lever is the number of Claude calls, not the size of what Claude reads.** On this machine a Claude call carries a median of 305k tokens of context (p90 686k), and cache reads are 68% of the price-weighted cost (§2). Every call therefore costs about 30k input-token-equivalents before it does anything. Shrinking tool outputs can save at most the ~19% of cache reads that text tool results account for; collapsing several calls into one saves the whole per-call charge each time.
2. **What `ling` takes over is exploration first.** Runs of three or more consecutive search-and-read calls are 21.6% of the cost; if each became one delegation, the ceiling saving is about 13% of everything Claude spends here (§2.3). Build-and-fix loops, the case one would guess first, are 1.2% of the cost on this machine and come later, if at all.
3. **A task is delegable only when a machine can check the result, or when Claude only ever uses checked parts of it.** `ling` runs Qwen3.8-27B, a model that resolves fewer real issues than Claude. It must never make a judgement Claude would have made differently. So what `ling` returns is split into **evidence that the wrapper has verified mechanically** (a quote that is byte-for-byte the file's text at the cited lines, a command's exit code) and **prose that nobody has verified**. Claude may build on the first and must treat the second as a hint (§5).
4. **A negative answer from `ling` is never evidence of absence.** "Not found" sends Claude to search for itself whenever the absence matters (a security check, "is this function called anywhere", a removal).
5. **It fails open.** No model server, a busy one, a running benchmark, a timeout, an unparsable answer or a failed check all end the same way: one short line to Claude, which does the work itself as it does today. A delegation can make Claude slower; it must never make an answer worse.
6. **Phase 0 is no new code.** A Claude Code skill and `ling exec`'s existing flags are enough to measure everything that matters (§8, §9). A `ling delegate` subcommand comes only after the numbers justify it, and it lives in the launcher, with no Codex patch.
7. **Delegations use this machine's model server only.** `second-puffin` is reserved for ling-engine work by the user's rule (2026-10-08) and is never a delegation target.
8. **A bigger saving exists that does not involve `ling`, and this spec names it.** Subagents are 60% of Claude's cost here, mostly forks that inherit 270k-token contexts. Briefing a fresh subagent instead could save up to about a third of all cost (§2.4). It is Claude Code's behaviour, not Mightling's, so it is a comparison arm in the evaluation, not a deliverable.

---

## 1. Goals and non-goals

**Goals**
- Fewer price-weighted Claude tokens per completed task, measured from Claude Code's own usage records.
- No task that Claude alone gets right is gotten wrong because of a delegation, measured by audit (§9).
- No setup beyond installing one skill; nothing changes for a person who does not use it.
- A side effect worth stating: file contents that `ling` reads in a delegation stay on the machine and are not sent to Anthropic.

**Non-goals**
- Running Claude Code itself on the local model. That replaces the model, which is a quality change by definition.
- Routing Claude Code's small background model (titles, summaries, the command-prefix check) to the local model. Those calls are cheap, and one of them is a safety check.
- `ling` reviewing Claude's code. A weaker reviewer adds noise, not quality ([MIGHTLING_ADVISOR_NODE](./DREAMFERENCE_MIGHTLING_ADVISOR_NODE.md) argues the opposite direction).
- Delegating writing that needs judgement: specs, designs, user-facing text, security-sensitive code.

---

## 2. Where Claude's tokens go on this machine (measured 2026-10-08)

**Source.** Every Claude Code transcript under `~/.claude/projects/` on `gx10-9428`: 78 main sessions and 673 subagent transcripts, **41,337 API responses**. A transcript writes one line per content block, so lines were grouped by `message.id` and each response's `usage` counted once; counting lines instead double-counts (1,947 lines for 963 responses in one session).

**Weights.** Anthropic's list-price ratios: input 1, cache write 1.25 (the five-minute write; the one-hour write is 2.0, which would raise the cache-write share), cache read 0.1, output 5. "Price-weighted tokens" below means tokens times these weights. For a subscription plan whose limits are not published, the assumption is that usage is metered roughly in proportion to cost; this is not verified.

### 2.1 The shape of the bill

| | Share of price-weighted cost |
|---|---|
| Cache reads | **68%** |
| Cache writes | 22% |
| Output | 10% |
| Uncached input | 0% |

| | |
|---|---|
| Context per call | median **305k** tokens, p90 686k |
| Cache reads per token written | 39.5 (a ratio of totals; writes include whole-prefix rewrites after a cache expiry, so this understates how often a *unique* token is read) |
| Subagents' share of cost | **60%** (main sessions 40%) |

A token that enters Claude's context costs about 1.25 + 39.5 × 0.1 ≈ **5.2** input-token-equivalents over its life, and each further Claude call costs about 0.1 × 305k ≈ **30k** before it adds anything.

### 2.2 What the calls do

Each response was classed by its first tool call (heuristic patterns on the command; the classes overlap at the edges). "Search or read" is broad: it includes `cat`, `ls`, `head` and `git diff` used to look at things, not only searches, so 38.7% is not all exploration:

| Class | Share of cost | Calls |
|---|---|---|
| Shell commands that search or read (`grep`, `rg`, `find`, `cat`, `sed -n`, `git log/show/diff`, `ls`) | **38.7%** | 17,591 |
| Shell commands that write a file or a script (heredocs, `tee`) | 16.5% | 6,405 |
| No tool: a text or thinking turn | 12.3% | 4,321 |
| Waiting, polling or status checks (`sleep`, `until`, `gh run view`, `tail`, `docker ps`) | **8.3%** | 2,364 |
| Edit/Write tools | 6.1% | 2,326 |
| Other shell commands | 4.5% | 2,074 |
| Read/Grep/Glob and code-index tools | 4.1% | 2,193 |
| Build and test commands | 3.5% | 1,353 |
| Other tools, web, subagent launches | 5.9% | 2,710 |

Text tool results (images and PDFs excluded) account for at most **19.1%** of cache reads (7.2% from results of 2k tokens or less, 11.9% from larger ones). This is an upper bound: it assumes every result stays in context until the session ends or compacts.

### 2.3 What delegation could reach

A **run** is a sequence of consecutive responses in one transcript that all belong to the same kind of work.

| Run kind (three or more calls) | Runs | Share of cost inside the runs | Ceiling saved if each run became 2 calls |
|---|---|---|---|
| Exploration (search/read shell commands and Read/Grep/Glob) | 2,284 | 21.6% | **13.1%** |
| Build-and-fix (build/test and edits, with at least one build/test) | 130 | 1.2% | 0.6% |

"Became 2 calls" is conservative: a foreground delegation is one call whose result is the answer. It is a ceiling because not every exploration run is delegable (§5.1).

### 2.4 Levers that do not need `ling` (measured, for comparison)

- **Waiting:** 8.3% of the cost is turns spent polling. One background command that ends when the condition holds (Claude Code's `run_in_background`, or an `until` loop) costs one call instead of many. No model is needed.
- **Fresh subagents instead of forks:** subagent calls carry a median of 271k cached tokens. Had every subagent call run at a fresh agent's 40k, the saving would be about **32%** of all cost. This is a ceiling that ignores the extra calls a fresh agent makes to recover context.

These are stated so that the evaluation (§9) can show whether delegation to `ling` beats or adds to them.

---

## 3. The break-even rule

Let **C** be Claude's current context, **R** the number of later calls that will re-read a token (39.5 here on average), **k** the number of calls Claude would make doing the work itself, **t** the tokens those calls would bring back, **b** the brief Claude writes, and **r** what the delegation returns. Each token added to the context costs w = 1.25 + 0.1·R.

Claude alone costs about k·0.1·C + t·w. A foreground delegation costs 0.1·C + b·(5 + w) + r·w. Delegation pays when

> (k − 1)·0.1·C + (t − r)·w > b·(5 + w)

**Worked example** at this machine's medians (C = 305k, R = 39.5, w = 5.2): an exploration Claude would do in five calls that bring back 6k tokens, replaced by a 300-token brief and an 800-token result. Saved: 4 × 30.5k + 5.2k × 5.2 ≈ 149k. Spent: 300 × 10.2 ≈ 3k. Net ≈ **146k token-equivalents**, about five Claude calls.

**Where it does not pay:** one *small* lookup never pays; a deterministic tool (`ling-code refs`, `rg`) answers it in one call for less. A single *large* output does pay with k = 1, through the (t − r)·w term: a 20k-token output replaced by a 1k digest saves about 99k. That is the `digest` case. At a small context (a fresh session, C ≈ 30k) the per-call term shrinks tenfold and only large t makes delegation worth it. The skill (§8) encodes this as: **delegate when you expect three or more search/read calls, or more than ~5k tokens of output, to answer one question.**

---

## 4. Kinds of delegation

| Kind | What `ling` does | What Claude receives | Phase |
|---|---|---|---|
| `find` | Answers one question about the code or files by searching and reading, in a read-only sandbox, with the code index | A verified answer (§5.1), ≤1,500 tokens | 0 |
| `digest` | Runs a command (or reads a file) whose output is large and reports what matters | The deterministic extract plus verified excerpts, and the path of the full output (§5.2), ≤1,500 tokens | 1 |
| `loop` | Makes a mechanical change and iterates until a check Claude names passes, in a separate git worktree | The check's result, the diff's statistics and the diff's path (§5.3) | 2, only if Phase 1's numbers show demand |

**Waiting is not a kind.** A wait needs no model; the skill tells Claude to use one background command (§2.4).

---

## 5. Keeping quality: what is verified, and by whom

### 5.1 `find`

**The brief** is a template with slots, never free prose, because Claude's output costs five times its input:

```
QUESTION: <one question>
SCOPE: <paths or "repository">
ANSWER IS: <what would count: a file:line, a value, a list of call sites>
LIMITS: at most <n> evidence items
```

**The answer** is constrained by `--output-schema`:

```json
{
  "status": "found | partial | not_found",
  "answer": "≤120 words",
  "evidence": [{"path": "...", "start": 10, "end": 12, "quote": "≤3 lines, verbatim", "why": "≤20 words"}],
  "searched": ["≤10 entries: each query or index call and its scope"],
  "confidence": "high | medium | low"
}
```

**The wrapper checks every evidence item before Claude sees it:** the path is inside the scope, the lines exist, and the quote equals the file's text at those lines (whitespace runs normalised, nothing else). An item that fails is removed and counted. If no item survives, the status becomes `unverified`.

**Claude's rules** (in the skill):
- **Quotes are ground truth.** A verified quote is the file's own text, so Claude does not need to reread it before relying on it.
- **The answer sentence is a hint.** Claude decides from the quotes, never from the prose alone.
- **`not_found`, `partial`, `unverified` or `low`** means Claude searches for itself when the result matters. `searched` tells it what was already tried, so it does not repeat it.
- **Absence is never inferred** from `ling` (decision 4).

### 5.2 `digest`

- **The full output is saved** to a file, and its path is returned. Nothing is lost: Claude can read any part of it.
- **A deterministic extract comes first,** by rule, never by the model: failing test names and their assertion lines (pytest, cargo test, ctest), compiler errors with file:line, the last 40 lines, the exit code. The model adds a ≤150-word explanation.
- **Every excerpt the model cites is checked** against the saved file, as in §5.1.
- If the extract is already under the size threshold, no model is called at all.

### 5.3 `loop` (Phase 2)

- **It runs in its own git worktree** (`ling exec --worktree`, `-s workspace-write`), so Claude's checkout is untouched.
- **Claude names the check**, a command whose exit code decides. The wrapper, not `ling`, runs it after `ling` stops, and reports the exit code.
- **Claude reads the whole diff before applying it.** Reading costs input tokens; writing the same change would have cost output tokens at five times the price.
- **After N attempts or T minutes,** `ling` stops and returns a ≤500-token failure summary, never the log, and Claude takes over.

### 5.4 Audit

Every delegation is recorded under `~/.mightling/delegate/`: the brief, the answer, the verification counts, the timings and the model's token counts. Phase 0 and Phase 1 sample these records and redo the work with Claude alone to measure recall (§9).

---

## 6. Where and when a delegation runs

- **Model server:** this machine's (`DREAMFERENCE_VLLM_HOST` is set explicitly, so no network browse happens). Never `second-puffin`.
- **Concurrency:** the server runs at most 8 requests at once. A delegation is one more agent; Night Shift gives way to it, as it does to any outside request.
- **During a SWE-bench run** (the runner lock, `$CODEX_HOME/night/runner.lock`, names its holder), a delegation refuses at once with `busy: benchmark running` and Claude works alone. Benchmark timing must not be disturbed. Phase 0's script does this check; Phase 1 moves it into `ling delegate`.
- **Latency:** the local model generates about 30 tokens/s on agent work and prefills about 1,700 tokens/s. A `find` is expected to take 30–120 s. Claude Code's shell tool waits up to 10 minutes in the foreground. A delegation longer than about 2 minutes runs in the background, and its completion notice is Claude's next turn, so the wait itself costs no calls.
- **Sandbox:** `find` runs read-only and needs no network. It works under `/airgapped on`. If Claude Code's own sandbox is enabled, `ling` must be in its excluded commands, because a sandbox inside Claude Code's sandbox cannot create its own namespaces. This is to be confirmed in Phase 0.

---

## 7. Output hygiene: nothing else may reach Claude's context

`ling exec` writes its progress to the terminal, and the launcher prints a waiting line while the server loads. Whatever the shell command prints enters Claude's context and is paid for about 40 times. So:

- **Phase 0 recipe:** `ling exec ... -o "$out" >/dev/null 2>&1; cat "$out"`.
- **Phase 1:** `ling delegate` prints exactly one JSON object and nothing else, capped at 1,500 tokens (the evidence list is truncated, and the truncation is said in a field).

---

## 8. Phases

**Phase 0: a skill and a recipe (no Mightling code).** Its first step decides whether the rest of Phase 0 works as written: one `ling exec --ephemeral -s read-only --output-schema … -o …` against this machine's server, to see whether the schema reaches SGLang through the local provider and constrains the answer. `--output-schema` exists in the source, but whether the chat-completions path forwards it is not known. If it does not, the script validates the JSON itself and treats a non-conformant answer as a failure (fail open); the schema still goes into the brief as text.
- **The skill:** `~/.claude/skills/ling-delegate/SKILL.md`. Its description is one sentence: "Answer a code question that needs three or more searches by asking the local model; quotes are verified, prose is a hint". Its body holds the break-even rule (§3), the brief template, the rules of §5.1, the output hygiene of §7 and the fail-open rule.
- **The schema and the script:** the skill folder holds `find.schema.json` and a short script that:
  - refuses at once when `$CODEX_HOME/night/runner.lock` is held (a non-blocking `flock`) and the holder it names is a SWE-bench run, and goes ahead when it is a Night Shift run, which gives way by itself (§6);
  - runs `ling exec --ephemeral -s read-only -C <repo> --output-schema find.schema.json -o <file>`, with `DREAMFERENCE_VLLM_HOST` set and all terminal output discarded (§7);
  - validates the JSON, checks the quotes (§5.1) and prints one JSON object.
- **Two conflicts handled at install:**
  - **Mightling's own planner would link this skill back into `ling`'s catalogue,** because it links `~/.claude/skills`. The skill would then tell `ling` to delegate to itself. The install step runs `ling skill disable ling-delegate`, an existing command whose `disabled` list means "never offered" ([MIGHTLING_SKILLS](./DREAMFERENCE_MIGHTLING_SKILLS.md)); Phase 1 makes that exclusion built in.
  - **A user's own CLAUDE.md may prescribe another exploration tool** (on this machine, jCodeMunch "for all code navigation"). The skill does not override it. The install step suggests one line for the user to add: single lookups stay with the user's tool, and questions needing three or more lookups go to `ling-delegate`. The user decides.

**Phase 1: `ling delegate find|digest` in the launcher (`ling-rs`).**
- the same behaviour as the recipe, plus the deterministic extracts of §5.2;
- a fixed JSON output, the busy and benchmark checks of §6, and the audit records of §5.4;
- the `ling-delegate` exclusion built into the skills planner, so no install step is needed for it;
- no Codex patch: it runs its own binary's `exec` as a child.

**Phase 2: `ling delegate loop`.** Built only if the Phase 1 data shows build-and-fix runs matter for this user. On this machine they are 1.2% of the cost today.

**Not planned:** a `PreToolUse` hook that diverts Claude's searches to `ling` automatically. It would take the decision away from the model that knows whether the answer matters, and it adds text to every call. It could be revisited if Phase 1 shows the skill is under-used.

---

## 9. How "the same answers" is measured

**Phase 0a: the ceiling, from transcripts (done in §2).** It is repeated after a month of use, so the shares can be compared before and after.

**Phase 0b: a replay benchmark for `find`.**
1. Sample 60 exploration runs (§2.3) from the transcripts, stratified by length.
2. For each run, Claude reads the run and writes the question it answered and the answer it reached. This is Claude's own conclusion at the time, so it is the reference.
3. Ask `ling` the same question through the recipe.
4. Score:
   - **Recall:** the reference answer's file:line is among the verified evidence.
   - **Answer agreement**, judged blind by Claude.
   - **Verification drop rate:** evidence items removed by the quote check.
   - Time, and the model's token counts.

**Pass bar for Phase 1:**
- recall ≥ 90% on runs where `ling` reports `found` with `high` confidence;
- every miss either reports `partial`/`not_found`/`low`, or fails the quote check.

**What counts as a failure:** a miss that `ling` reports as `found`/`high` with verified evidence, but where the evidence answers a different question. It is the dangerous case, and every one is read by hand.

**Phase 1: a forward A/B in the regime that matters.** A fresh headless session starts near 30–40k tokens of context, where §3 predicts little saving. A fresh-session benchmark therefore cannot confirm the §2.3 ceiling; it could fail for the wrong reason. So each arm works through its tasks **in one continued session**, compacting as Claude Code does, so its context grows into the range of §2.1. The context reached is reported with the results.
- **The tasks:** 30 tasks from this repository's history, each a commit that changed tests. The task is the commit message, the starting point is its parent, and the hidden check is the commit's tests. Each task gets its own worktree inside the session.
- **The runs:** headless `claude -p`, continued between tasks, three arms, the same model:
  - (A) today;
  - (B) with the `ling-delegate` skill;
  - (C) with a rule to brief fresh subagents instead of forking (§2.4).
- **The metrics,** per task:
  - price-weighted Claude tokens, from the run's usage records;
  - pass or fail;
  - wall-clock time;
  - number of delegations and their audit results.
- **Quality bar:** no task passed by A and failed by B where the audit traces the failure to a delegation. Discordant pairs in either direction are reported.
- **Cost bar to ship the skill as recommended:** a median paired saving of at least 10% of price-weighted tokens.

**A field check after the A/B.** The transcript analysis of §2 is repeated after two weeks of real use with the skill: the exploration-run share and the price-weighted cost per user turn, before and after. Different weeks are different work, so this confirms direction, not size.

**Cost of measuring.** The A/B spends Claude tokens: 90 headless runs. Phase 0b spends 60 short Claude readings. Both are run only after the user approves the spend.

**Noise.** Thirty paired tasks cannot detect a small change in pass rate; the benchmark's own noise floor is about 4 in 24. The quality claim therefore rests on the per-delegation audit, not on the pass rate alone.

---

## 10. Risks

| Risk | Effect | Answer |
|---|---|---|
| `ling` reports a confident, verified, but irrelevant answer | Claude builds on the wrong code | Quotes are real but the question may differ: Claude checks that the quotes answer *its* question; Phase 0b counts these by hand |
| The local server is busy (Night Shift yields, but the user's own `ling` sessions do not) | Slow delegations | Timeout, fail open; the skill says "never wait on a delegation you could do faster yourself" |
| Delegations make sessions slower | The user waits | Report wall-clock in the A/B; background mode for long ones |
| Claude over-delegates single lookups | Cost goes up | The break-even rule in the skill; Phase 1 counts delegations with k = 1 |
| The skill loops back into `ling` | `ling` delegates to itself | The planner rule of §8 |
| The price ratios change, or the one-hour cache write (2.0) is in use | The break-even shifts | The rule depends on C and k, which dominate; the ratios are restated where they are used |

---

## 11. What was measured here, and what was not

**Measured:**
- the cost structure of Claude Code on this machine (§2), from 41,337 deduplicated API responses;
- the exploration and build-and-fix run shares;
- the subagent share and the fresh-agent ceiling.

**Read from source:**
- the `ling exec` flags this design relies on (`--output-schema`, `-o`, `--ephemeral`, `-s`, `-C`, `--worktree`). They exist; that is all reading proves;
- that a user's own `[[skills.config]]` entries and the `disabled` list survive the launcher's rewrites (`ling-rs/skills/src/config_entries.rs`, `settings.rs`);
- the runner lock and its holder text (`dreamference/night_shift/night_shift_queue.py`).

**Not measured:**
- **first:** whether `--output-schema` reaches SGLang through the local provider and constrains the answer. Phase 0's first step; the fallback is in §8;
- whether `ling` answers exploration questions well enough (Phase 0b);
- its latency on real questions;
- whether a sandbox inside Claude Code's sandbox works;
- the forward A/B;
- whether a subscription's usage limit tracks the price ratios.

**Heuristic:** the classification in §2.2 uses command patterns, and the run boundaries in §2.3 follow from it. The 13.1% is a ceiling, not a forecast.
