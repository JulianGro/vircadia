include(vcpkg_common_functions)

vcpkg_check_linkage(ONLY_STATIC_LIBRARY)

vcpkg_from_github(
  OUT_SOURCE_PATH SOURCE_PATH
  REPO KhronosGroup/glslang
  REF 11.6.0
  SHA512 f7c1affdb4923758f9ff5cae894c40ca86e723850a6265d9c13f996311451bd84c70a178d8d6c0961dcee39c19d724f02d19a21ee6f67f1bb4cdbc618fdc12cf
  HEAD_REF master
)

vcpkg_configure_cmake(
  SOURCE_PATH ${SOURCE_PATH}
  PREFER_NINJA
  OPTIONS -DCMAKE_DEBUG_POSTFIX=d
)

vcpkg_install_cmake()

file(REMOVE_RECURSE ${CURRENT_PACKAGES_DIR}/debug/include)
file(RENAME "${CURRENT_PACKAGES_DIR}/bin" "${CURRENT_PACKAGES_DIR}/tools")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/bin")

# Handle copyright
file(COPY ${CMAKE_CURRENT_LIST_DIR}/copyright DESTINATION ${CURRENT_PACKAGES_DIR}/share/glslang)
