# Generated from verified release archives by scripts/homebrew_formula.py.
class PolarisCode < Formula
  desc "Composable coding agent with replaceable plugins and typed execution graphs"
  homepage "https://github.com/RadiantAILabs/polaris_code"
  version "0.2.0"
  license "Apache-2.0"

  on_macos do
    depends_on macos: :sequoia
    depends_on arch: :arm64

    on_arm do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.2.0/polaris-code-0.2.0-aarch64-apple-darwin.tar.gz"
      sha256 "d77b8b63c11fd49fd30f84f669c36dbcb68325eec6f0ec5d65f7add9268ed362"
    end
  end

  on_linux do
    depends_on arch: :x86_64
    depends_on "gcc"
    depends_on "patchelf" => :build

    on_intel do
      url "https://github.com/RadiantAILabs/polaris_code/releases/download/v0.2.0/polaris-code-0.2.0-x86_64-unknown-linux-gnu.tar.gz"
      sha256 "efadafe6f49a4043adc93cbcba6c40d5a1cf63f3a2912131d96bb731635500e3"
    end
  end

  conflicts_with "polaris", because: "both install a polaris executable"

  def install
    bin.install "polaris"
    if OS.linux?
      # Use Homebrew's GCC runtime and, when present, its glibc loader.
      rpath = "#{Formula["gcc"].opt_lib}/gcc/current:#{HOMEBREW_PREFIX}/lib"
      args = ["--set-rpath", rpath]
      patcher = [Formula["patchelf"].opt_bin/"patchelf"]
      loader = HOMEBREW_PREFIX/"lib/ld.so"
      if loader.exist?
        args += ["--set-interpreter", loader.to_s]
        # The patchelf bottle can also require Homebrew's newer glibc.
        patcher.prepend(loader.to_s, "--library-path", rpath)
      end
      system *patcher, *args, bin/"polaris"
    end
  end

  test do
    assert_match "polaris #{version}", shell_output("#{bin}/polaris --version")
    assert_match "Usage: polaris", shell_output("#{bin}/polaris --help")
    inventory = JSON.parse(shell_output("#{bin}/polaris #{testpath} --list-topologies --output-format json"))
    assert_includes inventory.fetch("entries").map { |entry| entry.fetch("id") }, "code.direct-edit"
  end
end
