import time


def run_dummy(numbers):
    for findme in range(100000):
        if findme in numbers:
            print("found", findme)
        else:
            print("missed", findme)


if __name__ == "__main__":
    # create a large sized input to show off inefficiency
    numbers = [i for i in range(20000000)]

    start_time = time.time()  # get the current time [start]
    run_dummy(set(numbers))  # run our inefficient method
    end_time = time.time()  # get the current time [end]

    duration = end_time - start_time  # Calculate the duration
    print(f"Duration: {duration} seconds")  # Print the duration
