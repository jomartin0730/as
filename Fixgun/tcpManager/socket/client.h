#ifndef CLIENT_H
#define CLIENT_H

#include <QObject>
//#include <QWidget>
#include <QTcpSocket>

class Client : public QObject
{
    Q_OBJECT

public:
    Client(QString ip_addr, quint16 port = 0, QObject * parent = nullptr);

	void setIP(QString);
	void setPort(quint16);
    bool doConnect();
    bool writeData(QByteArray data);
    bool isConnected();

public slots:
	void doConnect(QString, quint16);
    void doDisConnect();
	void doSend(QString);

signals:
	void readData(QByteArray);
    void connected();
    void disconnected();

private slots:
    void readReceivedData();

private:
    QTcpSocket *socket;
    QString ip_addr;
    quint16 port;
};

#endif // CLIENT_H
