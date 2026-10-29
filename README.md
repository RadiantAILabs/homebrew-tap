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

To publish a new batch, update the formula's source URL and checksum or run
the Homebrew bottles workflow manually. When bumping the source version, remove the previous
`bottle` block until the new batch is published. Each batch gets an immutable
GitHub release URL. The workflow validates archive checksums before publishing,
updates the formula with Homebrew's generated metadata, and verifies the
published packages with `--force-bottle`.

Update with `brew update && brew upgrade radiantailabs/tap/polaris-code`.

Source, usage, and license: [RadiantAILabs/polaris_code](https://github.com/RadiantAILabs/polaris_code).

Enable the workflow's `verify_only` input to check the published bottles
without rebuilding them.
