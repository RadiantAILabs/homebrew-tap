# Radiant AI Homebrew tap

Install the Polaris coding agent on macOS or Linux:

```bash
brew install radiantailabs/tap/polaris-code
polaris --help
```

The command is `polaris`. The formula is named `polaris-code` to distinguish
it from Homebrew's unrelated Kubernetes tool, which also installs `polaris`;
those two formulae cannot be linked at the same time.

Prebuilt Homebrew bottles are available for Apple Silicon on macOS Sequoia
and newer, and Linux x86-64. Homebrew downloads the tested binary package on
those platforms, skipping the Rust and CMake build dependencies. Other
configurations build the checksummed source release with Homebrew's Rust
toolchain.

A model API key is needed to run agent turns; `--help`, `--version`, and
`--list-topologies` work without a key.

GitHub Actions builds, tests, and publishes bottles, then verifies a bottle
installation on fresh Linux and macOS runners. The macOS verification also
checks bottle selection for Apple Silicon on Golden Gate.

Publishing a stable `vMAJOR.MINOR.PATCH` GitHub Release in
`RadiantAILabs/polaris_code` triggers this tap's workflow. The source repository
needs the `HOMEBREW_TAP_TOKEN` Actions secret: a fine-grained token restricted
to this tap with **Actions: write** permission. See the application's
[release guide](https://github.com/RadiantAILabs/polaris_code/blob/main/docs/publishing.md#one-time-automation-setup)
for setup. Tag pushes alone do not trigger builds; prereleases are excluded.

The workflow validates the tagged crate version and executable, computes the
source checksum, and builds both platforms while the live formula keeps its
current bottles. It publishes immutable release assets and switches the source
and bottle metadata together after both builds pass. Duplicate notifications
skip an already bottled release; delayed older releases cannot roll back the
formula. Queued releases prepare against the latest tap commit and pin their
builds to that commit.

To replay a notification, run the application's **Homebrew release** workflow
with `release_tag`. You can also run this tap's **Homebrew bottles** workflow
with that input; enable `force_rebuild` to replace bottles for the same version.
An empty tag rebuilds the current formula. After a failure, use **Re-run all
jobs** so both platforms use the new attempt's immutable release URL. If the
tap changed during the build, start a new run from the latest `main`.

Update with `brew update && brew upgrade radiantailabs/tap/polaris-code`.

Source, usage, and license: [RadiantAILabs/polaris_code](https://github.com/RadiantAILabs/polaris_code).

Enable the workflow's `verify_only` input to check the published bottles
without rebuilding them.
