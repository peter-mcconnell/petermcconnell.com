+++
title = "Golang_debugging"
date = "2023-01-03T12:33:02Z"
author = "Peter McConnell"
authorTwitter = "PeteMcConnell_" #do not include @
cover = ""
tags = ["golang", "delve", "debugging"]
keywords = ["golang", "delve", "dlv", "debugging"]
description = "I was asked recently how to debug a Golang application and after-the-fact thought I should spend some time detailing the steps incase it's of benefit to others. In short I use a debugger called Delve"
showFullContent = false
readingTime = true
hideComments = false
color = "" #color from the theme settings
Toc = true
+++

what do we want to achieve?
---------------------------

This is the tool I reach for when a program isn't behaving how I expect it to and I want to dig into the internals / browse the state of the program at particular points so as to realise why my understanding of the program is wrong.

what are the requirements?
--------------------------

Install `delve`: https://github.com/go-delve/delve

```sh
git clone https://github.com/go-delve/delve
cd delve
go install github.com/go-delve/delve/cmd/dlv
```

Have the following pieces of information:

 - a list of 1 or more points in my code where I'd like to set breakpoints
    - filename and line numbers

example program
---------------

For the sake of this article we'll create a simple application to debug:


```golang
// main.go
package main

import "fmt"

func doubleit(val int) int {
        return val * 3  // should be * 2
}

func main() {
        fmt.Printf("doubleit 2: %d\n", doubleit(2))
        fmt.Printf("doubleit 4: %d\n", doubleit(4))
        fmt.Printf("doubleit 8: %d\n", doubleit(8))
}
```

When we run this with `go run main.go` we want it to double the numbers we pass but for _some reason_ we're getting different results.

We will also need a `go.mod` for Delve to run so also perform a `go mod init` from this directory.

debug it
--------

To get started from the project directory

```sh
dlv debug
Type 'help' for list of commands.
(dlv)
```

Now set some breakpoints. For this example we'll say we want to debug our `doubleit` method - the first line of which is at `:7`:

```sh
dlv debug
Type 'help' for list of commands.
(dlv) b main.go:7
Breakpoint 1 set at 0x49c8bb for main.doubleit() ./main.go:7
```

When we've added all of the breakpoints that we need we can instruct the program to run with `c`:


```sh
dlv debug
Type 'help' for list of commands.
(dlv) b main.go:7
Breakpoint 1 set at 0x49c8bb for main.doubleit() ./main.go:7
(dlv) c
> main.doubleit() ./main.go:7 (hits goroutine(1):1 total:1) (PC: 0x49c8bb)
     2:	package main
     3:
     4:	import "fmt"
     5:
     6:	func doubleit(val int) int {
=>   7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
    12:		fmt.Printf("doubleit 4: %d\n", doubleit(4))
(dlv)
```

Now we've ran our program with an attached debugger and it has paused execution at the breakpoint we set. We can run `args` to see which arguments where passed to the method:

```sh
(dlv) c
> main.doubleit() ./main.go:7 (hits goroutine(1):1 total:1) (PC: 0x49c8bb)
     2:	package main
     3:
     4:	import "fmt"
     5:
     6:	func doubleit(val int) int {
=>   7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
    12:		fmt.Printf("doubleit 4: %d\n", doubleit(4))
(dlv) args
val = 2
~r0 = 0
```

So in this point in the program we're in the `doubleit` method when it was invoked with a `val` value of `2`. We can print this and other variables using `p`:

```sh
(dlv) p val
2
```

We can even call methods from this point using `call`:

```sh
(dlv) call doubleit(6)
> main.doubleit() ./main.go:7 (hits goroutine(6):1 total:2) (PC: 0x49c8bb)
     2:	package main
     3:
     4:	import "fmt"
     5:
     6:	func doubleit(val int) int {
=>   7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
    12:		fmt.Printf("doubleit 4: %d\n", doubleit(4))
(dlv) args
val = 6
```

In the example above we hit our own breakpoint set earlier allowing us to print the `args` for the `call`.

To walk over the execution we can press `n` to go to the next point of execution:

```sh
(dlv) n
> main.doubleit() ./main.go:6 (PC: 0x49c8a0)
     1:	// main.go
     2:	package main
     3:
     4:	import "fmt"
     5:
=>   6:	func doubleit(val int) int {
     7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
(dlv) n
> main.doubleit() ./main.go:7 (hits goroutine(6):2 total:3) (PC: 0x49c8bb)
     2:	package main
     3:
     4:	import "fmt"
     5:
     6:	func doubleit(val int) int {
=>   7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
    12:		fmt.Printf("doubleit 4: %d\n", doubleit(4))
(dlv) n
```

and view the backtrace with `bt`:

```sh
(dlv) bt
0  0x000000000049c8bb in main.doubleit
   at ./main.go:7
1  0x000000000046251f in debugCall256
   at :0
2  0x0000000000407484 in runtime.debugCallWrap2
   at /usr/local/go/src/runtime/debugcall.go:251
3  0x00000000004073b3 in runtime.debugCallWrap1
   at /usr/local/go/src/runtime/debugcall.go:203
4  0x0000000000464ca1 in runtime.goexit
   at /usr/local/go/src/runtime/asm_amd64.s:1594
```

To view the code around the current point of execution just press `l`:

```sh
(dlv) l
> main.doubleit() ./main.go:7 (hits goroutine(6):3 total:4) (PC: 0x49c8bb)
     2:	package main
     3:
     4:	import "fmt"
     5:
     6:	func doubleit(val int) int {
=>   7:		return val * 3 // should be * 2
     8:	}
     9:
    10:	func main() {
    11:		fmt.Printf("doubleit 2: %d\n", doubleit(2))
    12:		fmt.Printf("doubleit 4: %d\n", doubleit(4))
```

Which of course shows our very hard to find logic error, `* 3` instead of `* 2`.

Note: you can also set breakpoints in the stdlib functions (paths will vary depending on your setup):

```sh
(dlv) b src/net/http/request.go:899
Breakpoint 1 set at 0x794599 for net/http.NewRequestWithContext() /usr/local/go./net/http/request.go:899
```

summary
-------

The example above is extremely trivial - where `dlv` and it's ilk shine are on complex usecases where you may not even know what methods are between the input and output, such as debugging the stdlib. Just this week I used `dlv` to identify why a `POST` wasn't honouring a `307` temporary redirect - on inspection, using `dlv`, I learned that the `body` is disregarded if it is an unrecognised `type` https://github.com/golang/go/blob/master/src/net/http/request.go#L899. Having to do this without a debugger would have taken quite a bit of code hopping - the debugger took care of that for me and allowed me to validate argument values as I did it.

why not gdb?
------------

I know some folk feel strongly that `gdb` is the tool to use for debugging go code, but given the Golang docs itself encourage you to use Delve over GDB I personally stay away from it:

> Note that Delve is a better alternative to GDB when debugging Go programs built with the standard toolchain. It understands the Go runtime, data structures, and expressions better than GDB. Delve currently supports Linux, OSX, and Windows on amd64. For the most up-to-date list of supported platforms, please see the Delve documentation.

Exceptions here may be usage of cgo but I'll leave that out for now.

_source: https://tip.golang.org/doc/gdb_
