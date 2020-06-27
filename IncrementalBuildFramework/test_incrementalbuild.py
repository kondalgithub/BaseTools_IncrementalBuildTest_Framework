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
import sys

import IncrementalBuild

def test_incrementalbuild():
    #Initialize incremental build
    framework_path = os.path.dirname(os.path.abspath(__file__))
    incremental_build = IncrementalBuild.PlatformIncrementalBuild(framework_path)
    
    patch_list = incremental_build.get_patches()
    print (patch_list)
    for patch in patch_list:
        incremental_build.apply_patch(patch)
        #Get paltform clean build hash
        incrementalbuild_hash = incremental_build.get_incremental_build_hash()
        #Get platform clean build hash
        cleanbuild_hash = incremental_build.get_clean_build_hash()
        incremental_build.revert_patch(patch)
        assert(incrementalbuild_hash==cleanbuild_hash)

