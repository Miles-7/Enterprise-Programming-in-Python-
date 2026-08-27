from abc import ABC,abstractmethod
import threading
'''
1.1) classes must support: 
    management of learner information
    course enrollments 
    assessment activities 
    validation and class interactions 

    -that reflect large-scale training 
    and certification environment 
'''

'''
1.2) Design pattern:
    Singleton pattern - manage app configuration settings
    & ensure only 1 config instance exists through the app

    Factory pattern- creates different support ticket types
    based on user requirements

    Strategy Pattern- support different approaches for 
    calculating assessment results 
'''


# Singleton Pattern

class AppConfig:
    __instance = None # Class variable - that will hold one-and-only instance

    # Override the "__new__" method which handles the creation of object instance before __innit__ runs
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None: # ensures that only one instance can be created 
            cls.__instance = super().__new__(cls)
            cls.__instance.__initialized = False # flag/attribute added to __instance to prevent second objects from overwriting existing attributes like max_course_capacity
        return cls.__instance


    def __init__(self,max_course_capacity =50, support_email="support@training.com"):
        if self.__initialized:
            return
        self.id = 1
        self.max_course_capacity = max_course_capacity
        self.support_email = support_email
        self.__initialized = True

class Learner():
    def __init__(self,id,name):
        # OOP - encapsulation 
        self.__id = id
        self.__name = name
        self.__registrations = [] # will hold registration objects - composition
        self.__support_tickets = [] # will show learner to support ticket relationship 

    def add_registration(self,registration):
        self.__registrations.append(registration)


    def add_support_ticket(self,ticket):
        self.__support_tickets.append(ticket)

    # Getters for learner attributes
    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_registrations(self):
        return self.__registrations

    

class Course():
    def __init__(self,course_id,name,max_capacity):
        self.__course_id = course_id
        self.__name = name
        self.__max_capacity = max_capacity  # added max capacity as a form of validation 
        self.__registrations = [] # all of the learners enrolled in this course 
        self.__lock = threading.Lock()

    def add_registration(self,registration):
            with self.__lock:
                if len(self.__registrations) >= self.__max_capacity:
                    raise ValueError("Course is full")
                
                self.__registrations.append(registration)

    # Getters for course attributes
    def get_course_id(self):
        return self.__course_id

    def get_name(self):
        return self.__name

            
            

   


class Registration():
    def __init__(self,learner,course,registration_date=None):

        self.__learner = learner # will be an instance of Learner
        self.__course = course # will be an instance of Course 
        self.__registration_date = registration_date
        self.__assessments = [] #assessments that are tied to the registration 
        self.__status = "Active"

        # Connect/ Create a relationship between Learner, Course, and Registrations by calling both the course and learner classes'  "add_registration" methods
        learner.add_registration(self)
        course.add_registration(self)

        #getters
    def get_course(self):
        return self.__course

    
    def get_learner(self):
        return self.__learner



# Strategy Pattern
# Abstract base class for strategy pattern
class ResultStrategy(ABC):
    @abstractmethod
    def calculate_results(self,score,max_score):
        pass

# sub classes for the abstract base class to calculate percentage and whether the learner passed or not 
class PercentageStrategy(ResultStrategy):
    def calculate_results(self, score, max_score):
        return (score/max_score)*100

class PassFailStrategy(ResultStrategy):
    def calculate_results(self, score, max_score):
        percentage = (score/max_score) * 100
        if percentage >= 50:
            return "Pass"
        else:
            return "Fail"
            


# In my assessment class, I "plug in" the strategy pattern class by passing it as a constructor parameter
# My assessment class will not do any calculation (It intentionally doesnt know how to), instead through using the strategy pattern, it will simply hold a reference to an object that knows how to.
class Assessment():
    def __init__(self, assessment_id,title,max_score,result_strategy: ResultStrategy = None):
        self.__assessment_id = assessment_id
        self.__title = title 
        self.__max_score = max_score
        self.__score = 0   # not an constructor parameter because upon instantiating the class the there will not yet be a score
        self.__result_strategy = result_strategy if result_strategy else PercentageStrategy() # default to Percentage Sub class if no strategy is specified 

    # score setting validation -- No calculations, just setting the score
    def set_score(self,score):
        if score < 0 or score > self.__max_score: 
            raise ValueError(f"SCore must be between 0 and {self.__max_score}")
        self.__score = score 

    # actual calculations will be done by the objects in the Strategy Pattern
    def get_result(self):
        return self.__result_strategy.calculate_results(self.__score,self.__max_score) #########TODO

    # The CORE of the factory pattern's implementation: Swap the "ResultStrategy" at any given point in the object's lifetime
    def set_strategy(self, result_strategy: ResultStrategy):
        self.__result_strategy = result_strategy

#factory pattern
# OOP - abstraction, SupportTicket is an abstract base class 
class SupportTicket(ABC):
    def __init__(self,learner,description):
        self.__learner = learner  # instance of the learner 
        self.__description = description
        self.__status = "Open"
        self.__priority = "None"

        # create relationship between learner and support ticket
        learner.add_support_ticket(self)

        
    @abstractmethod
    def createTicket(self):
        pass


# implementations of the factory pattern
# OOP principle - example of inheritance 
class AcademicTicket(SupportTicket):
    def createTicket(self):
        print("Created: Academic ticket")


class TechnicalTicket(SupportTicket):
    def createTicket(self):
        print("Created: Technical ticket")



class RegistrationTicket(SupportTicket):
    def createTicket(self):
        print("Created: Registration ticket")



# Actual Factory for the support ticket
class SupportTicketFactory:
    @staticmethod
    def create_ticket(ticket_type: str,learner,description) ->SupportTicket: # the str is a hint, as well as SupportTicket- says the method will 
        ticket_type = ticket_type.lower()

        if ticket_type == "academic":
            return AcademicTicket(learner,description)
        elif ticket_type == "technical":
            return TechnicalTicket(learner,description)    
        elif ticket_type == "registration":
            return RegistrationTicket(learner,description)  
        else:
            raise ValueError(f"Unknown ticket type: {ticket_type}")






# learner1 = Learner("L201","Dian")
# course = Course("PY701", "Enterprise Python Development", max_capacity=30)
# registration = Registration(learner1,course)

# print("Domain Model Output")
# print("-"*40)
# print(f"LearnerID: {learner1.get_id()} Name: {learner1.get_name()}")
# print(f"Course: {course.get_name()}")
# print(f"Learner {learner1.get_name()} registered for {course.get_name()}")



# TODO Display Polymorphism during driver code 
# learner = Learner(1,"Jane")

# print("Factory Pattern Demonstration")
# print("-"*40)
# tickets = [
#     SupportTicketFactory.create_ticket("academic", learner, "Missed exam submission"),
#     SupportTicketFactory.create_ticket("technical", learner, "Can't access course portal"),
#     SupportTicketFactory.create_ticket("registration", learner, "Wrong course enrolled"),
# ]

# for ticket in tickets:
#     ticket.createTicket() 





#Driver code for strategy pattern:
# print("Strategy Pattern Demonstration")
# print("-"*40)
# assessment = Assessment("A1", "Python Basics Quiz", 100)  # This will default to PercentageStrategy
# assessment.set_score(85)
# print(assessment.get_result())          # 85.0

# assessment.set_strategy(PassFailStrategy())   # swap strategy to assess whether the student passed 
# print(assessment.get_result())          # Pass




#driver code for singleton pattern
# config1 = AppConfig()
# config2 = AppConfig(max_course_capacity=100)  # tries to pass different settings

# print("If config 1 is config 2 display 'True':")
# print(config1 is config2 )         # True — same object
# print(f"\nConfig 1 ID: {config1.id}\nConfig 2 ID: {config2.id}")
# print(config1.max_course_capacity)     # 50 — second call didn't override it

