from ib_insync import IB

def test_ibkr_connection(host, port):
    ib = IB()
    try:
        print("Connecting to IBKR...")
        ib.connect(host, port, clientId=1)
        print("Connected successfully!")
        ib.disconnect()
    except Exception as e:
        print(f"Failed to connect to IBKR: {e}")
    
if __name__ == "__main__":
    host = "127.0.0.1"  # Local TWS/IB Gateway
    port = 7496          # IB Gateway port
    test_ibkr_connection(host, port)
