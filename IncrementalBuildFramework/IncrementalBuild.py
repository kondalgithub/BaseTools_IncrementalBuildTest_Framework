#! python3
#
# This file contains 'Framework Code' and is licensed as such
# under the terms of your license agreement with Intel or your
# vendor. This file may not be modified, except as allowed by
# additional terms of your license agreement.
#
## @file
# Incremental build test
#
# Copyright (c) 2020, Intel Corporation. All rights reserved.
# This software and associated documentation (if any) is furnished
# under a license and may only be used or copied in accordance
# with the terms of the license. Except as permitted by such
# license, no part of this software or documentation may be
# reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of
# Intel Corporation.
#
import pytest
import os
import shutil
import collections
import subprocess
from filehash import FileHash

from UnifiedBuild.BuildPlatform import BuildPlatform
import  Manifest
EXCLUDE_FILELIST_TYPE = [".obj", ".map", ".lib", ".dll", ".bin"]
FileHashResult = collections.namedtuple("FileHashResult", ["filename", "hash"])

class PlatformIncrementalBuild:
    """Class for platform incremental build test framework."""
    def __init__(self, framework_path=None):
        """Initialization."""
        self.framework_path = framework_path
        self.platform_manifest_file = os.path.join(framework_path, "incrementalbuild_platform_manifest.toml")
        self.platform_manifest =  Manifest.Manifest(self.platform_manifest_file)
        self.platform_workspace = None
        self.build_dir = None
        self.working_dir = None
        self.set_workspace()

    def set_workspace(self):
        """Setup build workspace for given manifest file."""
        self.platform_workspace = self.platform_manifest.Defines.get("workspace")
        self.build_dir = os.path.join(self.platform_workspace,"Build")
        self.build_steps = self.platform_manifest.BuildCate.get("Basic")
        self.working_dir = self.platform_manifest.Defines.get("workdir")

    def get_incremental_build_hash(self):
        """Do incremental build and get hash of build folder."""
        BuildPlatform(self.working_dir, self.build_steps,['BuildClean'])
        return self.get_build_hash(self.build_dir)
    
    def get_clean_build_hash(self):
        """Do incremental clean build and get hash of build folder."""
        BuildPlatform(working_dir,build_steps)
        return self.get_build_hash(self.build_dir)
    
    def get_buildfiles(self, build_dir):
        """Return file list from a build folder."""
        build_file_list = []
        for root,_,files in os.walk(build_dir):
            for file_name in files:
                name, ext = os.path.splitext(file_name)
                if ext not in EXCLUDE_FILELIST_TYPE:
                    build_file_list.append(os.path.join(root,file_name))
        return build_file_list

    def apply_patch(self, patchfile):
        self.git_cmd("apply", patchfile)

    def revert_patch(self, patchfile):
        self.git_cmd("apply", "-R", patchfile) 

    def get_patches(self):
        patchfiles_list = []
        for root,_,files in os.walk(os.path.join(self.framework_path, "IncrementalTestPatches")):
            for file_name in files:
                name, ext = os.path.splitext(file_name)
                if ext == ".patch":
                    patchfiles_list.append(os.path.join(root,file_name))
        return patchfiles_list

    def get_build_hash(self, build_dir):
        """Compute hash of directory."""
        sha256 = FileHash('sha256')
        build_files = self.get_buildfiles(build_dir)
        return sha256.cathash_files(build_files)

    def git_cmd(self, *args):
        with cd(self.working_dir):
            error, lines = cli_cmd('git', *args)
            if error:
                raise git_error(message = self.get_giterror(['git']+list(args), error, lines))
            return lines

    def get_giterror(self, cmd, error_code, subprocess_lines):
        "Format and returns error message received from subprocess."
        git_command = " ".join([argument for argument in  cmd])
        error_message = " ".join([line for line in  subprocess_lines])
        return "\n Command:{} \n Code:{} \n Message:{}".format(git_command, error_code, error_message)

class cd:
    """Context manager for changing the current working directory.
    """
    def __init__(self, newPath):
        """
        with utilities.cd(targetDir):
            ...do something in the target directory
        """
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class git_error(Exception):
    """Error to raise when Git commands fail."""
    def __init__(self, message):
        super().__init__(message)
        
def cli_cmd(command, *args):
    """Run a shell command and return its error code and the lines it
    printed to stdout or stderr.
    """
    cmdline = [command] + list(args)
    p = subprocess.Popen(cmdline,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         shell=False,
                         universal_newlines=True,
                         encoding='ascii',
                         errors="ignore")

    lines = []
    for line in p.stdout:
        lines.append(line)

    return p.wait(), lines
