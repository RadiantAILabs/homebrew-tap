# Radiant AI Homebrew tap

Install the Polaris coding agent on macOS or Linux:

```bash
brew install radiantailabs/tap/polaris-code
polaris --help
```

The command is `polaris`. The formula is named `polaris-code` to distinguish
it from Homebrew's unrelated Kubernetes tool, which also installs `polaris`;
those two formulae cannot be linked at the same time.

This formula builds a checksummed, tagged public source release with
Homebrew's Rust toolchain. It downloads the locked Rust dependencies before
building offline. A model API key is needed to run agent turns; `--help`,
`--version`, and `--list-topologies` work without a key.

GitHub Actions checks source installation and the formula's functional test
on Linux and macOS. No precompiled Homebrew bottles are published yet.

Update with `brew update && brew upgrade radiantailabs/tap/polaris-code`.

Source, usage, and license: [RadiantAILabs/polaris_code](https://github.com/RadiantAILabs/polaris_code).
