//
//  QtCompatibility.h
//
//  Created by Julian Groß on 2022-02-04
//  Copyright 2022 Overte e.V.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//


// Compatibility with Qt < 5.13
#ifndef Q_DISABLE_COPY
    #define Q_DISABLE_COPY(className) \
        className(const className &) = delete;\
        className &operator=(const className &) = delete;
#endif
