# Bugzot Monitoring system


'''
Must record:
- Record validation failures 
- duplicate registration attempts 
- Course capacity violations
- other application errors generated during processing


--- 
'''

import logging 
import threading # for the lock
import time



# use singleton pattern for monitoring system
class Bugzot():
    __instance = None 

    # Creation, not instantiating 
    def __new__(cls,*args,**kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    # Instantiation 
    def __init__(self,log_file ="bugzot_log.txt"):
        # return if already initialized 
        if self.__initialized:
            return  

        # set the "flag" that was added to __instance to true, indicating an instance exists
        self.__initialized = True 

        # Logging configuration
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
            )

        # keep track of the total amount of errors
        self.error_count = 0

        # variables that will help log the performance of my system
        self.transaction_count = 0
        self.total_time = 0

        # Since multiple threads can log errors at once, I will protect it with a lock
        self.__lock = threading.Lock()

        


    # for question 3.1 -- Just monitor registration attempts, errors and warnings such as duplicate registrations
    def log(self,level,category,message):
        full_message = f"{category} | {message}"
        level = level.upper() # just make it all caps 

        if level == "ERROR":
            with self.__lock:
                logging.error(full_message)
                self.error_count += 1 
        elif level == "WARNING":
            logging.warning(full_message)
        else:
            logging.info(full_message)


    # for question 3.2 -- logging performance, see how long transactions take to complete as well as how many transactions happen
    
    '''
    The "track" function will server as a decorator, which I will use 
    on the "process_registrations" method inside the Registration engine 
    class in deliverable 2 to monitor, log, and generate a report of the performance metrics 

    I will use the time.perf_counter to benchmark and measure my code execution time for performance 
    '''
    def track(self,func):
        def wrapper(*args,**kwargs): # args - takes input and puts into a tuple  |  kwargs - takes input (ex num =1) and puts it into a dict 
            start = time.perf_counter() #  what happens before function wrapped by decorator runs 
            result = func(*args,**kwargs)
            elapsed = time.perf_counter()-start  #what happens after function wrapped by decorator runs

            # use lock again to prevent multiple threads from accessing and modifying 
            # the vars that help me track the performance of the transactions
            with self.__lock:
                self.transaction_count += 1
                self.total_time += elapsed

            # Now i will use the logging configuration which is already inside the 
            # deliverable 2 function to log this 
            self.log("INFO","Performance",f"{func.__name__} completed in {elapsed*1000:.2f}ms") # convert to milliseconds for better readability

            return result 

        return wrapper 



    def generate_report(self):
        total_errors = self.error_count
        total_time = self.total_time
        transaction_count = self.transaction_count

        print("------ Performance Report -----")
        print(f"Total amount of errors: {total_errors}\nTotal amount of time: {total_time}\nTotal amount of transactions: {transaction_count}")

        # now reset these values with the Lock
        with self.__lock:
            self.error_count = 0
            self.total_time = 0
            self.transaction_count = 0

        return


        

        




    
        

    

    
    
