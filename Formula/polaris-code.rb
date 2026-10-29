class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  url "https://github.com/RadiantAILabs/polaris_code/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "90265c5674a2e57b7bac985c34785029ac9643bb1f6392a6e3778854e4cc1034"
  license "Apache-2.0"

  bottle do
    root_url "https://github.com/RadiantAILabs/homebrew-tap/releases/download/polaris-code-0.1.1-bottles-40920147681-1"
    sha256 cellar: :any_skip_relocation, arm64_sequoia: "24d4484541107b6c522f9fc45a7bfefb0b0c240bfb5087e3f2b31296c669da18"
    sha256 cellar: :any,                 x86_64_linux:  "eff478a85768ad037b58ac7a44be2b96d826f92449536a75ceb007225dfa4004"
  end

  depends_on "cmake" => :build
  depends_on "rust" => :build

  conflicts_with "polaris", because: "both install a polaris executable"

  def fetch
    system "cargo", "fetch", *std_cargo_fetch_args
  end

  def install
    system "cargo", "install", *std_cargo_args(path: "crates/polaris_code"), "--bin", "polaris"
  end

  test do
    assert_match "polaris #{version}", shell_output("#{bin}/polaris --version")
    assert_match "Usage: polaris", shell_output("#{bin}/polaris --help")
    inventory = JSON.parse(shell_output("#{bin}/polaris #{testpath} --list-topologies --output-format json"))
    assert_includes inventory.fetch("entries").map { |entry| entry.fetch("id") }, "code.direct-edit"
  end
end
