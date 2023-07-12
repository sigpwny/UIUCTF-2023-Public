{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, poetry2nix }:
  let
    system = "x86_64-linux";
    inherit (poetry2nix.legacyPackages.${system}) mkPoetryApplication mkPoetryEnv;
    pkgs = nixpkgs.legacyPackages.${system};
  in rec
    {
      packages.${system}.default = mkPoetryApplication {
        projectDir = self;
      };

      devShells.${system}.default = pkgs.mkShellNoCC {
        packages = [
          (mkPoetryEnv { projectDir = self; preferWheels = true; })
          pkgs.poetry
          pkgs.poppler_utils
          pkgs.texlive.combined.scheme-medium
        ];
      };
    };
}
