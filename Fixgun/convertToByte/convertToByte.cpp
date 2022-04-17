#include "convertToByte.hpp"

QByteArray shortTo2Byte(int16_t data)
{
    QByteArray qba(reinterpret_cast<const char *>(&data), sizeof(short));

    QByteArray buffer;
    buffer.resize(2);
    buffer[1]=qba[0];
    buffer[0]=qba[1];

    return buffer;
}

int16_t QByteToShort(QByteArray byte)
{
//(int16_t)buffer.toHex().toUShort(nullptr,16)
    return static_cast<int16_t>(byte.toHex().toUShort(nullptr,16));
}

QByteArray doubleTo8Byte(qreal data)
{
    QByteArray qba(reinterpret_cast<const char *>(&data), sizeof(double));

    QByteArray buffer;
    buffer.resize(8);
    buffer[7]=qba[0];
    buffer[6]=qba[1];
    buffer[5]=qba[2];
    buffer[4]=qba[3];
    buffer[3]=qba[4];
    buffer[2]=qba[5];
    buffer[1]=qba[6];
    buffer[0]=qba[7];

    return buffer;
}

double QByteToDouble(QByteArray byte)
{
    return static_cast<double>(byte.toHex().toDouble(nullptr));
}

QByteArray longTo8Byte(int64_t data)
{
    QByteArray qba(reinterpret_cast<const char *>(&data), sizeof(int64_t));

    QByteArray buffer;
    buffer.resize(8);
    buffer[7]=qba[0];
    buffer[6]=qba[1];
    buffer[5]=qba[2];
    buffer[4]=qba[3];
    buffer[3]=qba[4];
    buffer[2]=qba[5];
    buffer[1]=qba[6];
    buffer[0]=qba[7];

    return buffer;
}

int64_t QByteToLong(QByteArray byte)
{
   return static_cast<int64_t>(byte.toHex().toULong(nullptr,16));
}
