#ifndef CONVERTTOBYTE_GLOBAL_H
#define CONVERTTOBYTE_GLOBAL_H

#include <QtCore/qglobal.h>

#if defined(CONVERTTOBYTE_LIBRARY)
#  define CONVERTTOBYTE_EXPORT Q_DECL_EXPORT
#else
#  define CONVERTTOBYTE_EXPORT Q_DECL_IMPORT
#endif

#endif // CONVERTTOBYTE_GLOBAL_H
