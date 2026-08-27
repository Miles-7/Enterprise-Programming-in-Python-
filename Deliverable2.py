 # validate learner info
    # enforce business rules
    # maintain accurate registration records throughout the process

# solution must:
'''
1) prevent duplicate registrations 
2) enforce course capacity limits
3) updates registration statuses appropriately 
4) generate a summary showing the outcome of processed registrations, including successful and unsuccessful transactions

NB* to demonstrate scalability, application must be capable of processing at least 10 simulated registration requests
'''

'''
Deliverable 2
Talk about data structures that I used, no code 
'''



'''
Deliverable 3
Concurrent request processing, implement it in te registrationEngine and run registrations concurrently 
While protecting Course.__registrations from race conditions 

eg. two threads both passing the capacity check simultaneously before either has appended, OVERSHOOTING max_capacity
'''

from Deliverable3_extended import Bugzot
from Deliverable1 import Learner, Course, Registration
import threading 
import concurrent.futures # I will be creating a thread pool with the library 



class RegistrationResult:
    def __init__(self,learner,course,success,reason=""):
        self.learner = learner
        self.course = course
        self.success = success
        self.reason = reason


class RegistrationEngine:

    def __init__(self):
        self.__results = [] # List to hold an registration result per processed request
        self.__bugzot = Bugzot() # instance of bugzot to log what is monitored

    @Bugzot().track  # performance wrapper created in deliverable 3
    def process_registration(self,learner,course):

        # firstly validate that both learner and course objects exist 
        if learner is None or course is None:
            self.__results.append(RegistrationResult(learner,course,False,"Invalid Learner or Course"))
            self.__bugzot.log("ERROR", "Validation Failure", "Registration attempt with invalid Learner or Course")
            return
        
        # check for duplication
        if self.__is_duplicate(learner,course):
            self.__results.append(RegistrationResult(learner,course,False,"Duplicate registration"))
            self.__bugzot.log("WARNING","Duplicate Registration",f"Learner {learner.get_name()} is already registered for {course.get_name()}.")
            return

        # attempt to register user after passing validation
        try:
            Registration(learner,course)
            self.__results.append(RegistrationResult(learner,course,True,"Registration Successful"))
            self.__bugzot.log("INFO", "Registration Success", f"{learner.get_name()} registered successfully.")
        except ValueError as e:
            self.__results.append(RegistrationResult(learner,course,False,f"Error: {str(e)}"))
            self.__bugzot.log("ERROR", "Registration Failure", f"{learner.get_name()} tried to register for: {course.get_name()}: error: {str(e)}")
            


    # check for duplicates 
    def __is_duplicate(self,learner,course):
        for registration in learner.get_registrations():
            if registration.get_course() is course:
                return True
        return False

    def process_batch_concurrent(self,requests,max_workers=5):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_registration,learner,course) for learner, course in requests]
            concurrent.futures.wait(futures)

    def print_summary(self):
        # list comprehension to create a list of the successful and failed registrations 
        successful = [r for r in self.__results if r.success]
        failed = [r for r in self.__results if not r.success]
        print("Registration Processing Summary")
        print("-"*40)
        print(f"Total processed: {len(self.__results)}")  # display total registrations via the length of the list
        print(f"Successful: {len(successful)}") # display the total amount of  successful registrations via the length of the list
        print(f"Failed: {len(failed)}") # display the total amount of  failed registrations via the length of the list
        print()
        for r in self.__results:
            status = "[SUCCESS]" if r.success else "[FAILED]"
            print(f"{status} Learner: {r.learner.get_name()} Course: {r.course.get_name()}")

        self.__bugzot.generate_report()





# ... RegistrationResult and RegistrationEngine classes here ...

if __name__ == "__main__":
    # --- Sequential run (10+ requests, no contention) ---
    course = Course("PY701", "Enterprise Python Development", 10)
    learners = [Learner(f"Eduv{i}", f"Learner {i}") for i in range(1, 11)]

    engine = RegistrationEngine()
    print("REGISTRATION PROCESSING ENGINE")
    print("=" * 60)
    for learner in learners:
        engine.process_registration(learner, course)
    engine.print_summary()

    # --- Concurrent run (competing requests, capacity contention) ---
    course2 = Course("PY702", "Concurrent Systems", 4)
    concurrent_learners = [Learner(f"Eduv{i}", f" Learner {i}") for i in range(1, 18)]

    engine2 = RegistrationEngine()
    requests = [(learner, course2) for learner in concurrent_learners]
    engine2.process_batch_concurrent(requests)
    engine2.print_summary()

    # bugzot = Bugzot()
    # bugzot.generate_report



