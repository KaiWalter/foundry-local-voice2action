{
  description = "Nix flake that delivers a uv-powered Python workflow with Alejandra formatting.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      mkShellFor = system:
        let
          pkgs = import nixpkgs { inherit system; };
          lib = pkgs.lib;
        in pkgs.mkShell {
          buildInputs = [
            pkgs.alejandra
            pkgs.python314.pkgs.uv
          ];
          shellHook = ''
            exec ${lib.getExe pkgs.zsh} -l
          '';
        };
      mkPackageFor = system:
        let
          pkgs = import nixpkgs { inherit system; };
        in pkgs.stdenv.mkDerivation {
          name = "uv-environment-${system}";
          buildInputs = [ pkgs.alejandra pkgs.python310.pkgs.uv ];
          buildCommand = ''
            mkdir -p $out/bin
            cat <<'EOF' > $out/bin/enter-uv
            echo "Run nix develop to access uv and Alejandra"
            EOF
            chmod +x $out/bin/enter-uv
          '';
        };
      mkAttrList = f: builtins.listToAttrs (map (system: { name = system; value = f system; }) systems);
    in {
      devShells = mkAttrList (system: { default = mkShellFor system; });
      packages = mkAttrList (system: { default = mkPackageFor system; });
      defaultPackage = mkAttrList mkPackageFor;
    };
}
