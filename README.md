# Radiant AI Homebrew tap

Install the Polaris coding agent on macOS or Linux:

```bash
brew install radiantailabs/tap/polaris-code
polaris --help
```

The command is `polaris`. The formula is named `polaris-code` to distinguish
it from Homebrew's unrelated Kubernetes tool, which also installs `polaris`;
those two formulae cannot be linked at the same time.

The formula installs the prebuilt binary from the application's GitHub
release, for Apple Silicon on macOS Sequoia and newer, and Linux x86-64. No
Rust toolchain or build step is involved. On other platforms, install from
source with `cargo install polaris_code --locked`.

A model API key is needed to run agent turns; `--help`, `--version`, and
`--list-topologies` work without a key.

Publishing a stable `vMAJOR.MINOR.PATCH` GitHub Release in
`RadiantAILabs/polaris_code` triggers this tap's workflow. The application's
CI has already built and tested the archives and attached `polaris-code.rb`
to the release. The workflow downloads that formula and checks that every URL
points at that release and that each archive matches both the formula's and
the release's published SHA-256. It then installs and tests the formula on
fresh macOS and Linux runners and commits it. A release takes a few minutes
to reach the tap.

The source repository needs the `HOMEBREW_TAP_TOKEN` Actions secret: a
fine-grained token restricted to this tap with **Actions: write** permission.
See the application's
[release guide](https://github.com/RadiantAILabs/polaris_code/blob/main/docs/publishing.md#one-time-automation-setup)
for setup. Tag pushes alone do not trigger it; prereleases are excluded.
Duplicate notifications skip a formula that is already current, and a delayed
older release cannot roll back the formula.

To replay a notification, run the application's **Homebrew release** workflow
with `release_tag`, or this tap's **Homebrew formula** workflow with that
input; enable `force_rebuild` to republish the same version. With an empty
tag, the workflow verifies and installs the current formula. If the tap
changed during a run, start a new run from the latest `main`.

Update with `brew update && brew upgrade radiantailabs/tap/polaris-code`.

Source, usage, and license: [RadiantAILabs/polaris_code](https://github.com/RadiantAILabs/polaris_code).
