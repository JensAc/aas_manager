
with (import ./inputs.nix);
let
  basyx-sdk = mach-nix.buildPythonPackage {
  src = builtins.fetchGit{
    url = "https://github.com/zrgt/basyx-python-sdk";
    ref = "main";
  };
  requirements = ''
        python-dateutil>=2.8,<3
        lxml>=4.2,<5
        urllib3>=1.26,<2.0
        pyecma376-2>=0.2.4
  '';};

  qpageview = mach-nix.buildPythonPackage {
  src = builtins.fetchGit{
    url = "https://github.com/frescobaldi/qpageview";
    ref = "refs/tags/v0.6.0";
  };
  pname = "qpageview";
  version = "0.6.0";
  requirements = ''
       PyQt5==5.15.4
 '';
  };
in
mach-nix.mkPython {
  requirements = builtins.readFile ./requirements.txt;
  packagesExtra = [basyx-sdk qpageview];
  providers.pyqt5 = "nixpkgs";
  providers.pyqtwebengine = "nixpkgs";
}
