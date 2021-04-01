message(STATUS "boop1")
vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO assimp/assimp
    REF d1ef28fa523ee0a07628d9dec2494d5dfea8c209
    SHA512 d8464c0a2d87e9b6e083585fbb1f1fe1a80ec1875aec96f242d998c5f424c27f9b573c55ecf2593b9e722b579d8cd49c8da60d1f7ffd946d143a6b724b803a15
    HEAD_REF master
)

string(COMPARE EQUAL "${VCPKG_LIBRARY_LINKAGE}" "dynamic" ASSIMP_BUILD_SHARED_LIBS)

message(STATUS "boop2")
vcpkg_configure_cmake(
    SOURCE_PATH ${SOURCE_PATH}
    PREFER_NINJA
    OPTIONS -DASSIMP_BUILD_ASSIMP_TOOLS=OFF
            -DASSIMP_BUILD_TESTS=OFF
            -DBUILD_SHARED_LIBS=${ASSIMP_BUILD_SHARED_LIBS}
)

message(STATUS "boop3")
vcpkg_install_cmake()
message(STATUS "boop4")
# vcpkg_copy_pdbs()

file(INSTALL ${SOURCE_PATH}/LICENSE DESTINATION ${CURRENT_PACKAGES_DIR}/share/${PORT} RENAME copyright)
message(STATUS "boop5")