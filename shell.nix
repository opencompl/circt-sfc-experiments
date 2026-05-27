with (import <nixpkgs> {});
mkShell {
  buildInputs = [
    gnumake
    openroad
    klayout
    yosys
    firrtl
  ];
}

