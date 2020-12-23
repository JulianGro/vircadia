# Common Ambient Variables:
#   VCPKG_ROOT_DIR = <C:\path\to\current\vcpkg>
#   TARGET_TRIPLET is the current triplet (x86-windows, etc)
#   PORT is the current port name (zlib, etc)
#   CURRENT_BUILDTREES_DIR = ${VCPKG_ROOT_DIR}\buildtrees\${PORT}
#   CURRENT_PACKAGES_DIR  = ${VCPKG_ROOT_DIR}\packages\${PORT}_${TARGET_TRIPLET}
#
include(vcpkg_common_functions)

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO castano/nvidia-texture-tools
    REF b1a90f36013522b9e5a3a2197859b72188752e3f
    SHA512 13cf04a9856f150f7569c8c256c42fc6a5bc40586c9ca2b3ae553edf5bfcbccbba5b8538924079ed35effdd07b9e3ef4bfdb9733a2ec51f5a95f958885cc6cca
    HEAD_REF master
)

vcpkg_configure_cmake(
    SOURCE_PATH ${SOURCE_PATH}
    OPTIONS
        # FIXME
        -DBUILD_SQUISH_WITH_SSE2=OFF
        -DBUILD_TESTS=OFF
        -DBUILD_TOOLS=OFF
)

vcpkg_install_cmake()

if(VCPKG_LIBRARY_LINKAGE STREQUAL static)
    file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/bin ${CURRENT_PACKAGES_DIR}/debug/bin)
endif()
    
vcpkg_copy_pdbs()

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/share)

# Handle copyright
file(REMOVE ${CURRENT_PACKAGES_DIR}/share/doc/nvtt/LICENSE)
file(COPY ${SOURCE_PATH}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/nvtt)
file(RENAME ${CURRENT_PACKAGES_DIR}/share/nvtt/LICENSE ${CURRENT_PACKAGES_DIR}/share/nvtt/copyright)
