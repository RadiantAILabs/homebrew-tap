class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  url "https://github.com/RadiantAILabs/polaris_code/archive/refs/tags/v0.1.1.tar.gz"
  sha256 "90265c5674a2e57b7bac985c34785029ac9643bb1f6392a6e3778854e4cc1034"
  license "Apache-2.0"

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
