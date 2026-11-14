# Mastermind rebrand tooling

Mastermind is a fork of [HKUDS/DeepTutor](https://github.com/HKUDS/DeepTutor) (Apache-2.0).
The fork changes branding only; LICENSE and upstream attribution are kept.

After merging a new upstream release:

```bash
python3 -I scripts/mastermind/rebrand.py . --dry-run   # preview
python3 -I scripts/mastermind/rebrand.py .             # rebrand UI text, locales, prompts
uv run --no-project --with pillow python scripts/mastermind/make_brand.py web/public   # logos
```

Then update test expectations that assert the old name, and run `npx tsc --noEmit`,
`npx vitest run` (in `web/`) and the Python tests for changed prompt modules.

Left unchanged on purpose: `OpenDeepTutor` (desktop user-agent), `HKUDS/DeepTutor`
repo links, `DeepTutor_*` file names, and lowercase `deeptutor` package/route ids.

## Update policy (fork hardening)

`deeptutor/services/fork_policy.py` is hooked into `get_update_installation()` in
`deeptutor/api/routers/system.py`. It keeps the upstream release check as a signal
(Settings → About shows the latest **upstream DeepTutor** release) but disables every
in-app/PyPI self-update, because `pip install -U deeptutor` would replace Mastermind
with upstream DeepTutor. After an upstream merge, check that this one-line hook in
`system.py` survived the merge; `tests/services/test_fork_policy.py` fails if it did not.
The About page "GitHub" link points to the fork.
