import cProfile
import pstats # convert my raw output to sorted tables
import io   # capture the output as a text 
import time

from line_profiler import LineProfiler

from Deliverable1 import Learner, Course
from Deliverable2 import RegistrationEngine
from Deliverable3_extended import Bugzot   

# list to store my logs
REPORT = []


# logging helper to append text to my REPORT list
def log(text=""):
    print(text)
    REPORT.append(text)


# Function level breakdown
def run_cprofile():
    engine = RegistrationEngine()
    course = Course("ITEPA", "Enterprise Programming in Python", max_capacity=50)
    learners = [Learner(f"Eduv{i}", f"Learner {i}") for i in range(1, 11)]

    # create Profile object
    profiler = cProfile.Profile()

    # start recording
    profiler.enable()

    for learner in learners:
        engine.process_registration(learner, course)

    #stop recording
    profiler.disable()


    # Build the report with the raw profiler data by writing into the in memory buf
    buf = io.StringIO()
    stats = pstats.Stats(profiler, stream=buf)

    # Sort the results by total time spent in a function
    stats.sort_stats("cumulative")
    stats.print_stats(10)   


    log("\n=== cProfile: function-level results ===")
    log(buf.getvalue())
    engine.print_summary()


# Sequential vs concurrent time - context for the cProfile numbers
def compare_sequential_vs_concurrent():
    import concurrent.futures

    # sequential timing
    engine1 = RegistrationEngine()
    course1 = Course("ITOPA", "Cloud Computing", max_capacity=10)
    learners1 = [Learner(f"Eduv{i}", f"Learner {i}") for i in range(20)]

    start = time.perf_counter()  # grab current time
    for learner in learners1:
        engine1.process_registration(learner, course1)
    sequential_time = time.perf_counter() - start  #grab time again and subtract elapsed seconds

    # concurrent timing with the same volume, run through a thread pool
    engine2 = RegistrationEngine()
    course2 = Course("ITCOA", "Concurrent Systems", max_capacity=20)
    learners2 = [Learner(f"Eduv{i}", f"Learner {i}") for i in range(20)]
    requests = [(learner, course2) for learner in learners2]

    start = time.perf_counter()  # grab current time
    engine2.process_batch_concurrent(requests, max_workers=5)
    concurrent_time = time.perf_counter() - start  #grab time again and subtract elapsed seconds

    log("\n=== Sequential vs concurrent wall-clock time ===")
    log(f"Sequential : {sequential_time*1000:.2f} ms") # convert to milliseconds with :.2f format
    log(f"Concurrent : {concurrent_time*1000:.2f} ms  (5 worker threads)")


# line_profiler: line-level breakdown of Bugzot.log
# specifically watch the function line by line
def run_line_profiler():
    lp = LineProfiler()
    lp.add_function(Bugzot.log)

    engine = RegistrationEngine()
    course = Course("ITLPC", "Line Profile Course", max_capacity=5)
    learners = [Learner(f"Eduv{i}", f"Learner {i}") for i in range(1, 8)]  # 8 requests, 5 seats

    lp.enable_by_count()  # start counter
    for learner in learners:
        engine.process_registration(learner, course)     # exercises success + capacity-violation
    engine.process_registration(learners[0], course)       # exercises duplicate-registration branch
    lp.disable_by_count()   # end counter

    # capture report into a string buffer, log it, and then print the registration summary
    buf = io.StringIO()
    lp.print_stats(stream=buf)

    log("\n=== line_profiler: line-level results (Bugzot.log) ===")
    log(buf.getvalue())
    engine.print_summary()


if __name__ == "__main__":
    log("Deliverable 5.2 Application Profiling")
    log("=" * 40)

    
    run_cprofile()
    compare_sequential_vs_concurrent()
    run_line_profiler()

    # write results to a file 
    with open("profiling_results.txt", "w") as f:
        f.write("\n".join(REPORT))

    print("\nResults saved to: profiling_results.txt")