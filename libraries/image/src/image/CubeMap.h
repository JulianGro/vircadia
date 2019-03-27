//
//  CubeMap.h
//  image/src/image
//
//  Created by Olivier Prat on 03/27/2019.
//  Copyright 2019 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#ifndef hifi_image_CubeMap_h
#define hifi_image_CubeMap_h

#include <gpu/Forward.h>
#include <glm/vec4.hpp>
#include <vector>
#include <array>
#include <atomic>

namespace image {

    class CubeMap {
    public:
        
        using Face = std::vector<glm::vec4>;
        using Faces = std::array<Face, 6>;

        CubeMap(int width, int height, int mipCount);

        gpu::uint16 getMipCount() const { return (gpu::uint16)_mips.size(); }
        Faces& editMip(gpu::uint16 mipLevel) { return _mips[mipLevel]; }
        const Faces& getMip(gpu::uint16 mipLevel) const { return _mips[mipLevel]; }

        void convolveForGGX(CubeMap& output, const std::atomic<bool>& abortProcessing) const;
        glm::vec4 fetchLod(const glm::vec3& dir, float lod) const;

    private:

        struct GGXSamples;

        int _width;
        int _height;
        std::vector<Faces> _mips;

        static void generateGGXSamples(GGXSamples& data, float roughness, const int resolution);
        void convolveMipFaceForGGX(const GGXSamples& samples, CubeMap& output, gpu::uint16 mipLevel, int face, const std::atomic<bool>& abortProcessing) const;
        glm::vec4 computeConvolution(const glm::vec3& normal, const GGXSamples& samples) const;
    };

}

#endif // hifi_image_CubeMap_h
