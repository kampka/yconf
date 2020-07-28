{ nixpkgs ? import <nixpkgs> {} }:

nixpkgs.mkShell {
    name = "yconf";
    venvDir = "./.venv";
    buildInputs = [
      nixpkgs.python38Full
      nixpkgs.python38Packages.venvShellHook
    ];
    postShellHook = ''
      pip install -r requirements.txt
      pip install -r requirements-test.txt
    '';
}
