//
//  QtCompatibility.h
//
//  Created by Julian Groß on 2022-02-04
//  Copyright 2022 Overte e.V.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#include <QtGlobal>

// Compatibility with Qt < 5.13
#ifndef Q_DISABLE_COPY
    #define Q_DISABLE_COPY(className) \
        className(const className &) = delete;\
        className &operator=(const className &) = delete;
#endif

// Compatibility with Qt < 5.13
#ifndef Q_DISABLE_COPY_MOVE
    #define Q_DISABLE_COPY_MOVE(className) \
        className(className & other) = delete;\
        className(className && other) = delete;
#endif

// Compatibility with Qt < 5.15
#if (QT_VERSION < QT_VERSION_CHECK(5, 15, 0))
    #define oEndl endl
#else
    #define oEndl Qt::endl
#endif

// Compatibility with Qt < 5.15
#if (QT_VERSION < QT_VERSION_CHECK(5, 15, 0))
    #define oKeepEmptyParts QString::KeepEmptyParts
#else
    #define oKeepEmptyParts Qt::KeepEmptyParts
#endif

// Compatibility with Qt < 5.15
#if (QT_VERSION < QT_VERSION_CHECK(5, 15, 0))
    #define oSplitBehavior QString::SplitBehavior
#else
    #define oSplitBehavior Qt::SplitBehavior
#endif

// Compatibility with Qt < 5.15
#if (QT_VERSION < QT_VERSION_CHECK(5, 15, 0))
    #define oSkipEmptyParts QString::SkipEmptyParts
#else
    #define oSkipEmptyParts Qt::SkipEmptyParts
#endif

// TODO
#ifndef QRecursiveMutex
    #define QRecursiveMutex privateVariable  QMutex privateVariable { QMutex::Recursive }
#endif

//#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
//    mutable QMutex _changeCursorLock { QMutex::Recursive };
//#else
//    mutable QRecursiveMutex _changeCursorLock;
//#endif

// TODO
//#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
//            output.edit0() = hfmModelIn->meshes.toStdVector();
//#else
//            output.edit0() = std::vector<hfm::Mesh>(hfmModelIn->meshes.begin(), hfmModelIn->meshes.end());
//#endif

#if (QT_VERSION < QT_VERSION_CHECK(5, 14, 0))
    #define _mutex() _mutex(QMutex::Recursive)
#endif

