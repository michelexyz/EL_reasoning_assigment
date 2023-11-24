from py4j.java_gateway import JavaGateway as Py4JJavaGateway, Py4JNetworkError

class JavaGateway:
    def __init__(self):
        
        self.gateway = None

    def start(self):
        
        try:
            self.gateway = Py4JJavaGateway()  # Attempt to connect to the Java Gateway regardless
        except Py4JNetworkError:
            print("Failed to connect to the Java Gateway. It might not be running.")
            self.gateway = None

    def stop(self):
        if self.gateway is not None:
            self.gateway.shutdown()   # Shutdown the Py4J gateway 
            self.gateway = None

    def get_parser(self):
        if self.gateway:
            return self.gateway.getOWLParser()
        else:
            print("Java Gateway is not running.")

    def get_formatter(self):
        if self.gateway:
            return self.gateway.getSimpleDLFormatter()
        else:
            print("Java Gateway is not running.")

    def get_factory(self):
        if self.gateway:
            return self.gateway.getELFactory()
        else:
            print("Java Gateway is not running.")






gateway_class = JavaGateway()
gateway_class.start()



# Access Java methods through the gateway
parser = gateway_class.get_parser()
formatter = gateway_class.get_formatter()
elFactory = gateway_class.get_factory()

# Stop the Java Gateway when done
#gateway.stop()

