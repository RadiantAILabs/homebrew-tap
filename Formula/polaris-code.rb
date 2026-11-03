# Generated from verified release archives by scripts/homebrew_formula.py.
class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  version "0.3.0"
  license "Apache-2.0"

  on_macos do
    depends_on arch: :arm64
    depends_on macos: :sequoia

    on_arm do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.3.0/polaris-code-0.3.0-aarch64-apple-darwin.tar.gz"
      sha256 "a86a23b47163eef632339bf2e9c11e2177591410d599f8f2870deb02016f63f4"
    end
  end

  on_linux do
    depends_on "patchelf" => :build
    depends_on arch: :x86_64
    depends_on "gcc"

    on_intel do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.3.0/polaris-code-0.3.0-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "9c72f4bb0289d8a53610e4947784afaf94e35c4891cbde153321a6ab2137b333"
    end
  end

  conflicts_with "polaris", because: "both install a polaris executable"

  def install
    bin.install "polaris"
    if OS.linux?
      # Use Homebrew's GCC runtime and, when present, its glibc loader.
      rpath = "#{formula_opt_lib("gcc")}/gcc/current:#{HOMEBREW_PREFIX}/lib"
      args = ["--set-rpath", rpath]
      patcher = [formula_opt_bin("patchelf")/"patchelf"]
      loader = HOMEBREW_PREFIX/"lib/ld.so"
      if loader.exist?
        args += ["--set-interpreter", loader.to_s]
        # The patchelf bottle can also require Homebrew's newer glibc.
        patcher.prepend(loader.to_s, "--library-path", rpath)
      end
      system(*patcher, *args, bin/"polaris")
    end
  end

  test do
    assert_match "polaris #{version}", shell_output("#{bin}/polaris --version")
    assert_match "Usage: polaris", shell_output("#{bin}/polaris --help")
    inventory = JSON.parse(shell_output("#{bin}/polaris #{testpath} --list-topologies --output-format json"))
    assert_includes inventory.fetch("entries").map { |entry| entry.fetch("id") }, "code.direct-edit"
  end
end
