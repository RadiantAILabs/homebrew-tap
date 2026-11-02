class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  url "https://github.com/RadiantAILabs/polaris_code/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "c496a20f68408a4b4d91d3d6f37acc8dd0f0ed5b059585ec96cf6ee6b750234c"
  license "Apache-2.0"

  bottle do
    root_url "https://github.com/RadiantAILabs/homebrew-tap/releases/download/polaris-code-0.2.0-bottles-41483782997-1"
    sha256 cellar: :any_skip_relocation, arm64_sequoia: "f7f309a8a289fbeeafd65fbb15328efc2ea053e3e5aafc878ee1d3f676b7ede5"
    sha256 cellar: :any,                 x86_64_linux:  "f168087abd74f104d1a81762b20c9d6ce161e9630ef9d0f8eac008e67e3e76b0"
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
