from Deliverable1 import *
from Deliverable2 import RegistrationEngine
from Deliverable3_extended import Bugzot


def reset_bugzot():

    'I will have to rest the bugzot instance because its a singleton pattern'
    'I will call this method at the start of every test function'
    Bugzot._Bugzot__instance = None



# Testing the singleton pattern for my App Config
def test_AppConfig_same_instance():
    config1 = AppConfig()
    config2 = AppConfig(max_course_capacity=999)
    assert config1 is config2

# Test my SupportTicketFactory 
def test_creates_academic_ticket():
    learner = Learner("Eduv1","Test Learner")
    ticket = SupportTicketFactory.create_ticket("academic",learner,"Missed Exam")
    assert isinstance(ticket,AcademicTicket)

def test_creates_technical_ticket():
    learner = Learner("Eduv2","Test Learner")
    ticket = SupportTicketFactory.create_ticket("technical",learner,"myLMS is down")
    assert isinstance(ticket,TechnicalTicket)

def test_creates_registration_ticket():
    learner = Learner("Eduv3","Test Learner")
    ticket = SupportTicketFactory.create_ticket("registration",learner,"Incorrect Course")
    assert isinstance(ticket,RegistrationTicket)

# Test strategy pattern - Assessment result calculation
'Check that correct percentage is calculated'
def test_percentage_strategy_calculation():
    assessment = Assessment("ITDSA","Data Structures in Python",100,PercentageStrategy())
    assessment.set_score(85)
    assert assessment.get_result() == 85.0

'Check that the default strategy is percentage calculation'
def test_default_strategy_is_percentage():
    assessment = Assessment("ITSEA","Software Architecture",50)
    assessment.set_score(25)
    assert assessment.get_result() == 50

'Check that if a learner '
def test_pass_fail_strategy_pass():
    assessment = Assessment("ITDMA", "Pass Fail Quiz", 100, PassFailStrategy())
    assessment.set_score(60)
    assert assessment.get_result() == "Pass"

def test_pass_fail_strategy_fail():
    assessment = Assessment("ITDMA", "Pass Fail Quiz", 100, PassFailStrategy())
    assessment.set_score(30)
    assert assessment.get_result() == "Fail"

def swop_strategy_at_runtime():
    assessment = Assessment("ITOPA", "Swap",100,PercentageStrategy())
    assessment.set_score(70)
    assert assessment.get_result() == 70.0
    # swop the method
    assessment.set_strategy(PassFailStrategy())
    assert assessment.get_result() == "Pass"


# Test business rules 

def test_registration_within_capacity_succeeds():
    course = Course("ITJA","Testing in Java",max_capacity=2)
    learner1 = Learner("Eduv1", "Alice")
    learner2 = Learner("Eduv2", "Bob")


    Registration(learner1,course)
    Registration(learner2,course)

    assert len(course._Course__registrations) == 2


def test_registration_beyond_capacity():
    course = Course("ITDMA","Research course FULL CAPACITY",max_capacity=1)
    learner1 = Learner("Eduv45","Chris")
    learner2 = Learner("Eduv46","Monje")

    Registration(learner1,course)
    raised = False
    try:
        Registration(learner2,course)
    except ValueError:
        raised = True
    assert raised



# RegistrationEngine test - validations, duplicates, summaries

def test_successful_registrations_is_recorded():
    reset_bugzot()
    engine = RegistrationEngine()
    course = Course("ITSSA","Networking and Security",max_capacity=5)
    learner = Learner("L10","Eve")

    engine.process_registration(learner,course)

    results = engine._RegistrationEngine__results
    assert len(results) == 1
    assert results[0].success


def test_duplicate_registration_is_rejected():
    reset_bugzot()
    engine = RegistrationEngine()
    course = Course("ITSEA","Software Architecture",max_capacity=5)
    learner = Learner("L11","Frank")

    engine.process_registration(learner,course) # my first registration should succeed
    engine.process_registration(learner,course) # my second registration should fail due to duplicate registration


    results = engine._RegistrationEngine__results
    assert len(results) == 2
    assert results[0].success # success for first
    assert not results[1].success # should fail
    assert "Duplicate" in results[1].reason # reason should be duplicate registration


def test_none_learner_is_rejected():
    reset_bugzot()
    engine = RegistrationEngine()
    course = Course("ITEPA", "Enterprise Python", max_capacity=5)

    engine.process_registration(None,course)
    results = engine._RegistrationEngine__results
    assert len(results) == 1
    assert not results[0].success
    assert "Invalid" in results[0].reason

def test_none_is_rejected():
    reset_bugzot()
    engine = RegistrationEngine()
    learner = Learner("Eduv67","Thato")

    engine.process_registration(learner,None)

    results = engine._RegistrationEngine__results
    assert not results[0].success
    assert "Invalid" in results[0].reason


def test_capacity_violation_is_caught():
    reset_bugzot()
    engine = RegistrationEngine()
    course = Course("ITPPA","Programming in Python",max_capacity=1)
    learner1 = Learner("Eduv1","James")
    learner2 = Learner("Eduv5","Rassie")

    engine.process_registration(learner1, course)  # fills capacity
    engine.process_registration(learner2, course)  # should fail and catch violation

    results = engine._RegistrationEngine__results
    assert results[0].success
    assert not results[1].success

    #the engine should no not crash and properly handle the error
    assert "Error" in results[1].reason



def test_batch_of_ten_sequential_registrations_all_succeed():
    reset_bugzot()
    engine = RegistrationEngine()
    course = Course("ITAPA","Concurrent Systems",max_capacity=10)
    # create a few learners
    learners = [Learner(f"Eduv{i}",f"Learner {i}") for i in range(10)]

    for learner in learners:
        engine.process_registration(learner,course)

    results = engine._RegistrationEngine__results
    assert len(results) == 10
    assert all(r.success for r in results)



# Arguably the most important part of my system
# - Test the concurrency safety of concurrent processes 


def test_concurrent_requests_never_exceed_course_capacity():
    reset_bugzot()
    capacity = 4
    num_requests = 30
    course = Course("ITEPA","Enterprise Programming in Python",max_capacity=capacity)

    learners = [Learner(f"Eduv{i}",f"Concurrent learner {i}") for i in range(num_requests)]

    engine = RegistrationEngine()
    requests = [(learner,course) for learner in learners] # create tuple of learners that want to enroll for the course 
    engine.process_batch_concurrent(requests,max_workers=10)

    results = engine._RegistrationEngine__results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    assert len(results) == num_requests # check that 30 learners tried to register
    assert len(successful) == capacity # only 4 learners should have registered successfully 
    assert len(failed) == num_requests - capacity # total amount of failed learner should be max capacity - total successful registrations

    # check that the course's own internal list actually matches the capacity 
    assert len(course._Course__registrations) == capacity



    






