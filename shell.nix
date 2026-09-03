with (import <nixpkgs> {});
mkShell {
  buildInputs = [
    gnumake
    openroad
    klayout
    python3
  ];
}

