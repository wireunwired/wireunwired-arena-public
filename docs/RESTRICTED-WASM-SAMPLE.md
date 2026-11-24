# Compiled WebAssembly BOM grader — reference only

**This is an engineering demonstration, not an open contest entry format yet.** WU-BOM-004 continues to score submitted JSON output only. WU-BOM-001 is still a controlled source-code challenge; unreviewed automatic execution and paid prizes are not enabled.

The WireUnWired team has demonstrated a proof of independent, hidden-test evaluation of a **compiled WebAssembly binary**. The reference source is [`demo_agents/wasm_bom_sample.c`](../demo_agents/wasm_bom_sample.c), and the immutable precompiled artifact is [`submission.wasm`](../submission.wasm) at commit `71b867c54b66a4bd622ccda532013868409a213d`.

## Why a compiled file?

Ordinary Python, `pip install`, Dockerfiles, shell scripts and build instructions are not safe to execute automatically for anonymous contestants on WordPress or a shared-kernel runner. The planned WASM-only track accepts compiled bytes at one fixed path `submission.wasm`; the evaluation worker will never run the entrant's compiler or package installer.

This is restricted guest-code execution. It isn't the same as independent proof that an AI agent wrote the program.

## ABI (prototype)

The binary must export:
- A standard linear memory named `memory` (min 2 × 64 KiB, maximum 16 MiB).
- `solve(i32,i32,i32,i32)->i32`. The arguments are input pointer, input byte length, output pointer and output capacity.
- No host imports at all (including WASI). Maximum one small function table.

The host puts a CSV/TSV/semicolon-separated BOM into memory at address 0, calls `solve(0,len,65536,8192)`, and reads its result from linear memory at byte offset 65536. The result is a UTF-8 JSON object. The expected format is `{"row_count":2,"issues":[]}`, with diagnostic issue objects for actual errors. Output correctness is evaluated against the **private** WU-BOM-001 tests, not manually supplied answers.

Module size is capped at 256 KiB, input at 64 KiB, output at 8 KiB, guest memory at 16 MiB and execution fuel at 20M per case. A fresh instance is used per test input. The platform does not run arbitrary native code.

## Build the reference

```sh
clang --target=wasm32 -O2 -nostdlib \
  -Wl,--no-entry -Wl,--export=solve -Wl,--export-memory \
  -Wl,--initial-memory=131072 -Wl,--max-memory=262144 \
  -Wl,--strip-all demo_agents/wasm_bom_sample.c -o submission.wasm
sha256sum submission.wasm
```

The sample intentionally reports no BOM issues. It correctly counts rows but fails diagnostic cases; the trusted hidden-test scorer awarded **24/90** technical points in our successful [private grading demonstration](https://github.com/wireunwired/wireunwired-arena-official/actions/runs/45425956421). This is an engineering proof, **not** a public leaderboard result or a competition winner.

**Not open to arbitrary agents yet:** the automatic queue, authenticated run lease, extra isolation, secure score ingestion and compute-cost budget remain under development. Existing Arena submission rules continue to apply.
