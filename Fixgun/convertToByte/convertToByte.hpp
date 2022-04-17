#ifndef CONVERTTOBYTE_HPP_
#define CONVERTTOBYTE_HPP_
#include <QByteArray>
QByteArray shortTo2Byte(int16_t data);
int16_t QByteToShort(QByteArray byte);

QByteArray doubleTo8Byte(qreal data);
double QByteToDouble(QByteArray byte);

QByteArray longTo8Byte(int64_t data);
int64_t QByteToLong(QByteArray byte);
#endif
