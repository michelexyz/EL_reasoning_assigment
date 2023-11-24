import time
import subprocess
from py4j.java_gateway import JavaGateway as Py4JJavaGateway, Py4JNetworkError
import os

print("Current Working Directory:", os.getcwd())

class JavaGateway:
    def __init__(self):
        # Get the directory in which the current script is located
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to the JAR file
        jar_file_path = os.path.join(current_directory, 'dl4python-0.1-jar-with-dependencies.jar')

        #print("Path to the JAR file:", jar_file_path)
        self.jar_path = jar_file_path
        self.process = None
        self.gateway = None

    def start(self):
        try:
            self.process = subprocess.Popen(["java", "-jar", self.jar_path])
    
            print("AAAAAAAA")

        except Exception as e:
            print(f"Failed to start the Java  process: {e}")
            print("if there is already one running this shouldn")
            self.process = None
        else:
            print(f"Java Gateway started with PID: {self.process.pid}")

        print("Sleeeping for 5 seconds")
        time.sleep(5)
        print("Done sleeping")
        try:
            self.gateway = Py4JJavaGateway()  # Attempt to connect to the Java Gateway regardless
        except Py4JNetworkError:
            print("Failed to connect to the Java Gateway. It might not be running.")
            self.gateway = None

    def stop(self):
        if self.gateway is not None:
            self.gateway.shutdown()   # Shutdown the Py4J gateway first
            self.gateway = None

        if self.process is not None:
            self.process.terminate()  # Then, gracefully terminate the Java process
            self.process.wait()       # Wait for the process to terminate
            print("Java Gateway stopped.")
            self.process = None

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
gateway_class.stop()

