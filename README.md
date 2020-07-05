# BaseTools_IncrementalBuildTest_Framework
1. Clone the repo
2. install requirements.txt using pip. cmd: pip install -r requirements.txt
3. Change "workdir" and "Workspace" to your edk2 repo in " incrementalbuild_platform_manifest.toml" and make sure you able to build ovmf pakage. 
4. run "test_incrementalbuild.py" with pytest. cmd: python -m pytest -s -q test_incrementalbuild.py
