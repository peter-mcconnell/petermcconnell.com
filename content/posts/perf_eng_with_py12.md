+++
title = "Perf engingeering with Python 3.12"
date = "2022-12-26T22:54:29Z"
author = "Peter McConnell"
authorTwitter = "peter-mcconnell" #do not include @
cover = ""
tags = ["python", "linux", "cpython", "perf"]
keywords = ["python", "linux", "cpython", "perf"]
description = ""
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

3.12 brings perf profiling! Take a second to go check out https://docs.python.org/3.12/howto/perf_profiling.html and indeed the changelog at https://www.python.org/downloads/release/python-3120a3/

The important part (for this post) from the links above is:

"""
The Linux perf profiler is a very powerful tool that allows you to profile and obtain information about the performance of your application. perf also has a very vibrant ecosystem of tools that aid with the analysis of the data that it produces.

The main problem with using the perf profiler with Python applications is that perf only allows to get information about native symbols, this is, the names of the functions and procedures written in C. This means that the names and file names of the Python functions in your code will not appear in the output of the perf.

Since Python 3.12, the interpreter can run in a special mode that allows Python functions to appear in the output of the perf profiler. When this mode is enabled, the interpreter will interpose a small piece of code compiled on the fly before the execution of every Python function and it will teach perf the relationship between this piece of code and the associated Python function using perf map files.
"""

writing a "bad" program
-----------------------

I'm excited to try this, so lets get going. Firstly lets create a python script for us to profile. I'm doing this before installing Python 3.12 as I want to create a FlameGraph of how this process looks in 3.10 verses 3.12. Here we have a script that attempts to perform lookups against a large list:

```python
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
    run_dummy(numbers)  # run our inefficient method
    end_time = time.time()  # get the current time [end]

    duration = end_time - start_time  # Calculate the duration
    print(f"Duration: {duration} seconds")  # Print the duration
```

Running this I get the following result:

```sh
python3.10 assets/dummy/perf_py_proj/before.py
...
found 99992
found 99993
found 99994
found 99995
found 99996
found 99997
found 99998
found 99999
Duration: 36.06884431838989 seconds
```

36 seconds is bad enough for us to pick up a reasonable amount of samples.

flamegraphs!
------------

Now we can create our [FlameGraph](https://github.com/brendangregg/FlameGraph):

```sh
# record profile to "perf.data" file (default output)
perf record -F 99 -g -- python3.10 assets/dummy/perf_py_proj/before.py
# read perf.data (created above) and display trace output
perf script > out.perf
# fold stack samples into single lines
# here I reference ~/FlameGraph/ - you can get this from https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# generate flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.10.svg
```

This gives us a nice SVG that visualises the traces:

![python 3.10 perf flamegraph](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.10.svg "python 3.10 perf flamegraph")

This isn't useful ... I can see most of the time was spent in "new_keys_object.lto_priv.0" but that is meaningless in the context of the code.

Time for Python 3.12...
-----------------------

First I need to install it - the steps for this vary depending on OS - follow the build instructions here for your environment: https://github.com/python/cpython/tree/v3.12.0a3#build-instructions


```sh
# for me on ubuntu:22.04
export CFLAGS="-fno-omit-frame-pointer -mno-omit-leaf-frame-pointer"
./configure --enable-optimizations
make
make test
sudo make install
unset CFLAGS

# after this I reset my systems python3 symlink to 3.10 as 3.12 isn't yet stable
# for testing python3.12 I'll call "python3.12" instead of "python3"
ln -sf /usr/local/bin/python3.10 /usr/local/bin/python3
```

With that installed I first need to enable perf support. This is detailed in https://docs.python.org/3.12/howto/perf_profiling.html and there are three options: 1) an environment variable, 2) an -X option or 3) dynamically using `sys`. I'll go for the environment variable approach as I don't mind _everything_ being profiled for a small script:

```sh
export PYTHONPERFSUPPORT=1
```

Now we simply repeat the process above using the `python3.12` binary instead:

```sh
# record profile to "perf.data" file (default output)
perf record -F 99 -g -- python3.12 assets/dummy/perf_py_proj/before.py
# read perf.data (created above) and display trace output
perf script > out.perf
# fold stack samples into single lines
# here I reference ~/FlameGraph/ - you can get this from https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# generate flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.12.before.svg
```

First we'll take a peek at the report with `perf report -g -i perf.data`

![python 3.12 perf report output](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_report.png "python 3.12 perf report")

Awesome! We can see our Python function names and script names!

Now we can take a look at the updated SVG that visualises the traces with Python 3.12:

![python 3.12 perf flamegraph](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.12.before.svg "python 3.12 perf flamegraph")

This is already looking much more useful. We see the majority of the time is being spent doing comparisons and in the list_contains method. We can also see the specific file `before.py` and method `run_dummy` that is calling it.

Investigation time / the fix
----------------------------

Now that we know that can take a look at the source code in CPython to see what it does: https://github.com/python/cpython/blob/199507b81a302ea19f93593965b1e5088195a6c5/Objects/listobject.c#L440

```c
// I found this by going to https://github.com/python/cpython/ and searching for "list_contains"

static int
list_contains(PyListObject *a, PyObject *el)
{
    PyObject *item;
    Py_ssize_t i;
    int cmp;

    for (i = 0, cmp = 0 ; cmp == 0 && i < Py_SIZE(a); ++i) {
        item = PyList_GET_ITEM(a, i);
        Py_INCREF(item);
        cmp = PyObject_RichCompareBool(item, el, Py_EQ);
        Py_DECREF(item);
    }
    return cmp;
}
```

Nasty... looking at this code I can see that each time it is invoked it iterates over the array and performs a comparison against each item. That's far from ideal for our usecase, so lets go back to the Python code we wrote. Our Flamegraph shows us that the problem is in our `run_dummy` method:

```python
def run_dummy(numbers):
    for findme in range(100000):
        if findme in numbers:  #  <- this is what triggers list_contains
            print("found", findme)
        else:
            print("missed", findme)
```

We can't really change that line as it is doing what we want it to do - identifying if an integer is in `numbers`. Perhaps we can change the `numbers` data type to one better suited to lookups. In our existing code we have:

```python
    numbers = [i for i in range(20000000)]

    start_time = time.time()  # get the current time [start]
    run_dummy(numbers)  # run our inefficient method
```

Here we used a LIST data type for our "numbers", which under the hood (in CPython) is implemented as dynamically-sized arrays and as such are nowhere near as efficient (O(N)) as the likes of a Hashtable for looking up an item (which is O(1)). A SET on the other hand (another Python data type) is implemented as a Hashtable and would give us the fast lookup we're looking for. Lets change the data type in our Python code and see what the impact is:

```python
    # we'll just change this line, casting numbers to a set before running run_dummy
    run_dummy(set(numbers))  # passing a set() for fast lookups
```

Now we can repeat the steps as above to generate our new flamegraph:

```sh
# record profile to "perf.data" file (default output)
perf record -F 99 -g -- python3.12 assets/dummy/perf_py_proj/after.py
...
found 99998
found 99999
Duration: 0.8350753784179688 seconds
[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 0.039 MB perf.data (134 samples) ]
```

Already we can see that things have massively improved. Where previously this was taking 36 seconds to run it is now taking 0.8 seconds! Lets continue creating our flamegraph for the new improved code:

```sh
# read perf.data (created above) and display trace output
perf script > out.perf
# fold stack samples into single lines
# here I reference ~/FlameGraph/ - you can get this from https://github.com/brendangregg/FlameGraph
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
# generate flamegraph
~/FlameGraph/flamegraph.pl out.folded > ./assets/perf_example_python3.12.after.svg
```

![python 3.12 perf flamegraph improved](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/perf_example_python3.12.after.svg "python 3.12 perf flamegraph improved")

This is a much healthier looking Flamegraph and our application is now much faster as a result. The perf profiling support in Python 3.12 brings a tremendously useful tool to software engineers that want to deliver fast programs and I'm excited to see the impact this will have on the language.
