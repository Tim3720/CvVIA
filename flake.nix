{
inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils = {
        url = "github:numtide/flake-utils";
        inputs.system.follows = "systems";
    };
};

outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem
    (system:
    let
        pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
        };
        libs = [
            pkgs.libcxx
            pkgs.eigen
        ];
    in
        with pkgs;
            {
            devShells.default = mkShell {
                nativeBuildInputs = with pkgs; [
                    bashInteractive
                    pkg-config
                    (pkgs.python312.withPackages(ps: with ps;[
                        numpy
						(opencv4.override {enableGtk3 = true;})
						pyside6
						matplotlib
						scipy
						qdarkstyle
						pydicom
						pyvista
						shapely
						plotly
						scikit-image
						scikit-learn
                    ]))
                ];
                buildInputs = with pkgs; [
                ];
                shellHook = ''
                '';
                LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
