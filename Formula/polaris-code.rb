# Generated from verified release archives by scripts/homebrew_formula.py.
class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  version "0.4.4"
  license "Apache-2.0"

  on_macos do
    depends_on arch: :arm64
    depends_on macos: :sequoia

    on_arm do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.4.4/polaris-code-0.4.4-aarch64-apple-darwin.tar.gz"
      sha256 "9e267a34acaf06571000a9f686384ee25e2ad167265899fb4bf9bd98f3bf76f8"
    end
  end

  on_linux do
    depends_on "patchelf" => :build
    depends_on arch: :x86_64
    depends_on "gcc"

    on_intel do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.4.4/polaris-code-0.4.4-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "9f5ae55ebefacde74844cc018630e07adba7d4c217c368d5953c3443e7ca581c"
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
