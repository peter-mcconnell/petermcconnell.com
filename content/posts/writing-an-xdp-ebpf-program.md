+++
title = "Building an XDP eBPF Program with C and Golang: A Step-by-Step Guide"
date = "2023-05-17T15:31:43Z"
author = "Peter McConnell"
authorTwitter = "PeteMcConnell_" #do not include @
cover = "https://github.com/peter-mcconnell/petermcconnell.com/blob/main/assets/dilih.png?raw=true"
tags = ["golang", "xdp", "ebpf", "chaos-engineering"]
keywords = ["golang", "xdp", "ebpf", "chaos-engineering"]
description = "Building an XDP eBPF Program with C and Golang: A Step-by-Step Guide is a comprehensive tutorial that walks readers through the process of building an XDP (eXpress Data Path) eBPF (extended Berkeley Packet Filter) program using C and Golang. The article provides a clear overview of XDP and eBPF, highlights the project's goal of creating a simple chaos engineering tool, and guides readers through each step of the development process. From setting up the development environment to writing the XDP eBPF program in C and the accompanying Golang application, readers will gain hands-on experience and learn important concepts such as packet processing, perf event handling, and statistics tracking. By the end of the article, readers will have a solid understanding of how to leverage XDP and eBPF for networking and performance optimization purposes"
showFullContent = false
readingTime = true
hideComments = false
color = "" #color from the theme settings
Toc = true
+++

_note: you can find the entire codebase for this article here: https://github.com/peter-mcconnell/dilih_

Introduction
------------

In today's highly connected and data-driven world, network performance is crucial for ensuring efficient communication and optimal user experience. XDP (eXpress Data Path) and eBPF (extended Berkeley Packet Filter) have emerged as powerful technologies that enable high-performance packet processing and network optimization. In this step-by-step guide, we will explore the process of building an XDP eBPF program using C and Golang. XDP allows for early packet interception at the network interface driver level, while eBPF provides a flexible and efficient execution environment for custom packet processing logic. Together, they offer an unprecedented level of control and performance in networking applications. Our project, named "dilih" (drop it like it's hot), demonstrates how to build a simple chaos engineering tool that arbitrarily drops packets on a given network interface. Through this guide, you will gain a deep understanding of XDP, eBPF, and their practical applications in network performance optimization.

Credit to Midjourney for the logo.

Project Overview
----------------

The project aims to build an XDP (eXpress Data Path) eBPF (extended Berkeley Packet Filter) program using C and Golang. Named "dilih" (drop it like it's hot), the program serves as a simple chaos engineering tool that selectively drops packets on a given network interface. This project demonstrates the power and flexibility of XDP and eBPF in controlling packet processing at high speed, making it an ideal starting point for understanding these technologies.

The XDP eBPF program, implemented in C, hooks into the Linux kernel's networking stack at an early stage to intercept packets and decide their fate. Using a randomization mechanism, the program selectively drops a configurable percentage of packets, allowing for controlled chaos in network traffic. Additionally, the program utilizes eBPF's perf event mechanism to gather statistics and measure the processing time for dropped and passed packets.

The accompanying Golang application interacts with the XDP eBPF program, providing a user-friendly interface to monitor the packet drop behavior and visualize performance statistics. It leverages the eBPF maps to extract and aggregate the collected data, allowing users to gain insights into the impact of dropped packets and the efficiency of packet processing.

Throughout this guide, we will explore the implementation details of both the XDP eBPF program in C and the Golang application. By the end of the project, you will have a solid understanding of XDP, eBPF, and their practical applications in networking and performance optimization.

Setting Up the Development Environment
--------------------------------------

To get started with building the XDP eBPF program with C and Golang, you need to set up your development environment. Follow these steps to ensure that you have all the necessary tools and dependencies in place:

1. Install Development Tools

    First, ensure that you have the required development tools installed on your system. This includes packages like clang, llvm, and bpftool. You can install these tools using the package manager available on your Linux distribution however I would recommend investing a little time to build these tools from source as it will give you greater control over the flags and features built into these tools.

    If you are curious about my _exact_ LLVM / Clang setup, I use the following ansible tasks for my configuration:

    https://github.com/peter-mcconnell/.dotfiles/blob/master/tasks/llvm.yaml
    https://github.com/peter-mcconnell/.dotfiles/blob/master/tasks/debugtools.yaml
    https://github.com/peter-mcconnell/.dotfiles/blob/master/tasks/docker.yaml

2. Install Golang

    Next, you need to install Golang, which is the programming language used for the accompanying Golang application. Visit the official Golang website at https://golang.org and follow the installation instructions specific to your operating system. Once installed, make sure the go command is accessible from the command line by adding the appropriate binary directory to your system's PATH.

    If you are curious about my _exact_ Golang setup, I use the following ansible task for my configuration:

    https://github.com/peter-mcconnell/.dotfiles/blob/master/tasks/golang.yaml

3. Install Project Dependencies

    Navigate to the project's root directory and install the required Golang dependencies by running the following command:

    ```bash
    go mod download
    ```
    
    This command will fetch and install the necessary Golang packages defined in the project's go.mod file.
    
    With these steps completed, you have successfully set up your development environment. You are now ready to dive into building the XDP eBPF program and the accompanying Golang application.

4. (Optional) IDE configuration

    Whatever your editor of choice should be, invest some time in making sure it is set up for C and Golang. Particularly for autocomplete, linting, symbol detection etc. This will make your life much easier.

    If you are curious about my _exact_ setup, I use the following repo to install neovim and everything else I need for development:

    https://github.com/peter-mcconnell/.dotfiles/

Writing the XDP eBPF Program in C
---------------------------------

The XDP (eXpress Data Path) program is implemented using the eBPF (extended Berkeley Packet Filter) framework in C. It allows us to intercept packets at an early stage in the Linux kernel's networking stack and perform custom packet processing logic. In this section, we will walk through the steps to write the XDP eBPF program in C.

1. Understanding the Program Logic

    Before diving into the code, let's understand the logic of our XDP program. The goal is to selectively drop packets on a given network interface. We will use a randomization mechanism to decide whether to drop or pass each packet. The program will also collect statistics and measure the processing time for dropped and passed packets using eBPF's perf event mechanism.

2. Creating the Program Source File

    Start by creating a new file called dilih\_kern.c in the bpf directory. This file will contain our XDP eBPF program logic. Open the file in your favorite text editor.

3. Defining the required headers and structures

    To begin, include the necessary headers and define the required structures for our XDP program. We need headers like bpf\_helpers.h and bpf\_endian.h, which provide useful helper functions and endianness conversions. We also need headers like linux/bpf.h, linux/in.h, linux/if\_ether.h, and linux/ip.h for network-related structures and constants.

    ```
    #include <stddef.h>
    #include <linux/bpf.h>
    #include <linux/in.h>
    #include <linux/if_ether.h>
    #include <linux/ip.h>
    #include <bpf_helpers.h>
    #include <bpf_endian.h>
    ```

4. Defining Data Structures and Maps

    Next, define the necessary data structures and maps that our XDP program will utilize. We will use a struct to represent the perf event data, and a BPF_MAP_TYPE_PERF_EVENT_ARRAY map to store the perf events. Define the following structures and maps:

    ```c
    struct perf_trace_event {
        __u64 timestamp;
        __u32 processing_time_ns;
        __u8 type;
    };
    
    struct {
        __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
        __uint(key_size, sizeof(int));
        __uint(value_size, sizeof(struct perf_trace_event));
        __uint(max_entries, 1024);
    } output_map SEC(".maps");
    
    ```

    The output\_map map will be used to store the perf events generated by our XDP program.

5. Implementing the XDP Program Function

    Now, it's time to implement the XDP program function itself. Begin by declaring the XDP function with the appropriate signature:

    ```c
    SEC("xdp")
    int xdp_dilih(struct xdp_md *ctx)
    {
        // Add program logic here
    }
    ```

    The xdp\_dilih function will serve as our XDP eBPF program entry point. It will be called for every incoming packet.

6. Handling Perf Events and Collecting Data

    Inside the xdp\_dilih function, we can handle perf events to collect data and measure processing time. We have already defined the output\_map to store these events. Use the bpf\_perf\_event\_output helper function to emit perf events to the map.
    
    ```c
    struct perf_trace_event e = {};
    
    // Perf event for entering xdp program
    e.timestamp = bpf_ktime_get_ns();
    e.type = 1;
    e.processing_time_ns = 0;
    bpf_perf_event_output(ctx, &output_map, BPF_F_CURRENT_CPU, &e, sizeof(e));
    
    // Packet dropping logic
    if (bpf_get_prandom_u32() % 2 == 0) {
        // Perf event for dropping packet
        e.type = 2;
        __u64 ts = bpf_ktime_get_ns();
        e.processing_time_ns = ts - e.timestamp;
        e.timestamp = ts;
        bpf_perf_event_output(ctx, &output_map, BPF_F_CURRENT_CPU, &e, sizeof(e));
    
        bpf_printk("Dropping packet");
        return XDP_DROP;
    }
    
    // Perf event for passing packet
    e.type = 3;
    __u64 ts = bpf_ktime_get_ns();
    e.processing_time_ns = ts - e.timestamp;
    e.timestamp = ts;
    bpf_perf_event_output(ctx, &output_map, BPF_F_CURRENT_CPU, &e, sizeof(e));
    
    bpf_printk("Passing packet");
    
    return XDP_PASS;
    ```

    In this section of the code, we handle the perf events to collect data and measure the processing time of dropped and passed packets. We first emit a perf event when entering the XDP program (type 1). Then, we use a randomization mechanism to decide whether to drop or pass the packet. If the packet is dropped, we emit a perf event with type 2 and return XDP\_DROP. If the packet is passed, we emit a perf event with type 3 and return XDP\_PASS.
    
    The bpf\_ktime\_get\_ns() function is used to measure the timestamp and processing time of the packet. The bpf\_get\_prandom\_u32() function generates a random value that helps in deciding whether to drop or pass the packet.
    
    Additionally, we use bpf\_printk() to print debug messages that can be accessed through the kernel's trace buffer.

That concludes the implementation of the XDP eBPF program in C. This program will selectively drop packets based on a randomization mechanism and emit perf events for collecting data and measuring processing time.


Compiling and Loading the XDP eBPF Program
------------------------------------------

Once we have written the XDP eBPF program in C, the next step is to compile it and load it into the kernel. In this section, we will walk through the steps to compile and load the XDP eBPF program.

1. Compiling the XDP Program

    To compile the XDP program, we will use the LLVM Clang compiler with the appropriate flags. Open a terminal and navigate to the bpf directory where the dilih_kern.c file is located. Then, run the following command:

    ```shell
    clang -O2 -target bpf -c dilih_kern.c -o dilih_kern.o
    ```

    This command compiles the dilih_kern.c file into a BPF object file named dilih_kern.o. The -target bpf flag specifies the target architecture as BPF, and the -O2 flag enables optimization.

2. Loading the XDP Program

    To load the XDP program into the kernel, we will use the bpftool command-line utility. Ensure that you have the bpftool utility installed on your system. If it's not already installed, you can typically install it using your distribution's package manager.

    In the terminal, run the following command to load the XDP program:

   ```shell
   sudo bpftool prog load dilih_kern.o /sys/fs/bpf/dilih
   ```

   This command loads the dilih_kern.o object file into the /sys/fs/bpf/dilih location. Adjust the path as necessary based on your system configuration. The bpftool utility will handle the loading process and verify the program's validity.

3. Attaching the XDP Program

    After loading the XDP program, we need to attach it to a network interface to start intercepting packets. To attach the XDP program, run the following command:

    ```shell
    sudo bpftool net attach xdp pinned /sys/fs/bpf/dilih dev <interface>
    ```
    
    Replace <interface> with the name of the network interface you want to attach the XDP program to. For example, ens160. This command attaches the XDP program to the specified interface, enabling it to intercept incoming packets.

Congratulations! You have successfully compiled and loaded the XDP eBPF program into the kernel and attached it to a network interface. The program is now ready to intercept and process packets based on your defined logic.

Please note that the compilation and loading process may vary slightly depending on your system configuration and specific requirements. Make sure to adjust the commands accordingly and refer to the documentation of the tools and utilities used.

Writing the Golang Application
------------------------------

In this section, we will write a Golang application that interacts with the XDP eBPF program and collects metrics. The Golang application will communicate with the loaded XDP program, read the perf events, and display statistics based on the collected data.

Setting Up the Golang Project
Before we begin writing the Golang application, let's set up the project structure and dependencies. Create a new directory for the Golang application and navigate into it.

```shell
mkdir dilih-app
cd dilih-app
```

Initialize a new Go module using the following command:

```shell
go mod init github.com/your-username/dilih-app
```

This will create a Go module for your application and allow you to manage dependencies.

Next, let's add the required dependencies for our Golang application. Open the go.mod file and add the following lines:

```
require (
    github.com/cilium/ebpf v0.10.0
    github.com/cilium/ebpf/link v0.10.0
    github.com/cilium/ebpf/perf v0.10.0
    github.com/prometheus/client_golang v1.11.0
)
```

Save the file and run `go mod download` to download the dependencies.

Writing the Golang Application Code
Now, let's create a new file named main.go and open it in a text editor. This file will contain the code for our Golang application. Copy and paste the following code into main.go:

```go
package main

import (
        "encoding/binary"
        "fmt"
        "net"
        "os"
        "os/signal"
        "syscall"

        "github.com/cilium/ebpf"
        "github.com/cilium/ebpf/link"
        "github.com/cilium/ebpf/perf"
)

const (
        TYPE_ENTER = 1
        TYPE_DROP  = 2
        TYPE_PASS  = 3
)

type event struct {
        TimeSinceBoot  uint64
        ProcessingTime uint32
        Type           uint8
}

const ringBufferSize = 128 // size of ring buffer used to calculate average processing times
type ringBuffer struct {
        data   [ringBufferSize]uint32
        start  int
        pointer int
        filled bool
}

func (rb *ringBuffer) add(val uint32) {
        if rb.pointer < ringBufferSize {
                rb.pointer++
        } else {
                rb.filled = true
                rb.pointer= 1
        }
        rb.data[rb.pointer-1] = val
}

func (rb *ringBuffer) avg() float32 {
        if rb.pointer == 0 {
                return 0
        }
        sum := uint32(0)
        for _, val := range rb.data {
                sum += uint32(val)
        }
        if rb.filled {
                return float32(sum) / float32(ringBufferSize)
        }
        return float32(sum) / float32(rb.pointer)
}

func main() {
        spec, err := ebpf.LoadCollectionSpec("bpf/dilih_kern.o")
        if err != nil {
                panic(err)
        }

        coll, err := ebpf.NewCollection(spec)
        if err != nil {
                panic(fmt.Sprintf("Failed to create new collection: %v\n", err))
        }
        defer coll.Close()

        prog := coll.Programs["xdp_dilih"]
        if prog == nil {
                panic("No program named 'xdp_dilih' found in collection")
        }

        iface := os.Getenv("INTERFACE")
        if iface == "" {
                panic("No interface specified. Please set the INTERFACE environment variable to the name of the interface to be use")
        }
        iface_idx, err := net.InterfaceByName(iface)
        if err != nil {
                panic(fmt.Sprintf("Failed to get interface %s: %v\n", iface, err))
        }
        opts := link.XDPOptions{
                Program:   prog,
                Interface: iface_idx.Index,
                // Flags is one of XDPAttachFlags (optional).
        }
        lnk, err := link.AttachXDP(opts)
        if err != nil {
                panic(err)
        }
        defer lnk.Close()

        fmt.Println("Successfully loaded and attached BPF program.")

        // handle perf events
        outputMap, ok := coll.Maps["output_map"]
        if !ok {
                panic("No map named 'output_map' found in collection")
        }
        perfEvent, err := perf.NewReader(outputMap, 4096)
        if err != nil {
                panic(fmt.Sprintf("Failed to create perf event reader: %v\n", err))
        }
        defer perfEvent.Close()
        buckets := map[uint8]uint32{
                TYPE_ENTER: 0, // bpf program entered
                TYPE_DROP: 0, // bpf program dropped
                TYPE_PASS: 0, // bpf program passed
        }

        processingTimePassed := &ringBuffer{}
        processingTimeDropped := &ringBuffer{}

        go func() {
                // var event event
                for {
                        record, err := perfEvent.Read()
                        if err != nil {
                                fmt.Println(err)
                                continue
                        }

                        var e event
                        if len(record.RawSample) < 12 {
                                fmt.Println("Invalid sample size")
                                continue
                        }
                        // time since boot in the first 8 bytes
                        e.TimeSinceBoot = binary.LittleEndian.Uint64(record.RawSample[:8])
                        // processing time in the next 4 bytes
                        e.ProcessingTime = binary.LittleEndian.Uint32(record.RawSample[8:12])
                        // type in the last byte
                        e.Type = uint8(record.RawSample[12])
                        buckets[e.Type]++

                        if e.Type == TYPE_ENTER {
                                continue
                        }
                        if e.Type == TYPE_DROP {
                                processingTimeDropped.add(e.ProcessingTime)
                        } else if e.Type == TYPE_PASS {
                                processingTimePassed.add(e.ProcessingTime)
                        }

                        fmt.Print("\033[H\033[2J")
                        fmt.Printf("total: %d. passed: %d. dropped: %d. passed processing time avg (ns): %f. dropped processing time avg (ns): %f\n", buckets[TYPE_ENTER], buckets[TYPE_PASS], buckets[TYPE_DROP], processingTimePassed.avg(), processingTimeDropped.avg())
                }
        }()

        c := make(chan os.Signal, 1)
        signal.Notify(c, os.Interrupt, syscall.SIGTERM)
        <-c
}
```

The code sets up the necessary components for the Golang application. It loads the BPF program, attaches it to the specified network interface, and initializes the perf event reader. However, the code to read and process the perf events is yet to be implemented.

In the next section, we'll continue writing the code to read and process the perf events emitted by the BPF program.

Note: Remember to import the required packages at the beginning of the file.

Save the file and move on to the next section to complete the implementation of the Golang application.

That concludes the content for the "Writing the Golang Application" section. Feel free to modify and customize the content according to your needs.

Building and Running the Project
--------------------------------

Now that we have implemented the XDP eBPF program in C and the Golang application, let's build and run the project.

Building the XDP eBPF Program
Before building the XDP eBPF program, ensure that you have the necessary build tools and dependencies installed on your system. You can refer to the project's README or documentation for the specific requirements.

To build the XDP eBPF program, navigate to the bpf directory and run the following command:

```shell
make
```

This command will compile the C code and generate the dilih\_kern.o object file.

Building the Golang Application
To build the Golang application, make sure you are in the root directory of the project. Run the following command:

```shell
go build
```

This command will compile the Golang code and generate an executable binary file.

Running the Project
To run the project, make sure you have the necessary privileges to load and attach the XDP program to the network interface.

First, load the XDP eBPF program using the following command:

```shell
sudo make xdp
```

This command will load the dilih_kern.o program and attach it to the specified network interface.

Next, run the Golang application using the following command:

```shell
sudo ./dilih-app
```

![sample output](https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/dillih_run.png "sample output")

Make sure to run the application with elevated privileges (sudo) to access the necessary resources.

The Golang application will start collecting data from the XDP program and display statistics based on the received perf events.

Cleaning Up
To clean up the project and remove the XDP program from the network interface, run the following command:

```shell
sudo make clean
```

This command will detach the XDP program from the network interface and remove any associated artifacts.

That's it! You have successfully built and run the project. Experiment with different network interfaces and observe the packet drop statistics displayed by the Golang application.

Feel free to explore additional features and modifications to enhance the project further.

Testing and Verifying the XDP eBPF Program
------------------------------------------

Testing and verifying the functionality of the XDP eBPF program is an essential step to ensure its correctness and effectiveness. In this section, we'll cover some testing techniques and verification methods for the XDP program.

Test Environment Setup
To create a suitable test environment, we'll utilize virtual network interfaces (veth devices) to simulate network traffic and observe the behavior of the XDP program.

Install the iproute2 package if it's not already installed on your system. This package provides the necessary tools to manage network interfaces.

Create a pair of veth devices using the following commands:

```shell
sudo ip link add veth0 type veth peer name veth1
```

This command will create two virtual network interfaces (veth0 and veth1) that are connected to each other.

Set the interfaces up and assign IP addresses to them:

```shell
sudo ip link set veth0 up
sudo ip link set veth1 up
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip addr add 10.0.0.2/24 dev veth1
```

This will bring up the interfaces and assign IP addresses (10.0.0.1 and 10.0.0.2) to them.

With the veth devices set up, we can proceed to test and verify the XDP eBPF program's functionality.

Packet Drop Verification
One of the primary functionalities of the XDP program is to drop a certain percentage of packets. We can verify this behavior by sending packets between the veth devices and observing the packet drop rate.

Open two terminal windows and navigate to the project directory in both of them.

In the first terminal, run the following command to listen for ICMP echo requests (ping):

```shell
sudo tcpdump -i veth1 icmp
```

In the second terminal, send ICMP echo requests (ping) from veth0 to veth1 using the following command:

```shell
sudo ip netns exec veth0 ping 10.0.0.2
```

Observe the output in the first terminal. You should see the ICMP echo requests being captured.

Analyze the packet capture to verify the packet drop rate. If the XDP program is working correctly, approximately 50% of the ICMP echo requests should be dropped, resulting in a reduced number of captured packets.

By performing packet drop verification tests, you can ensure that the XDP program is functioning as expected and dropping packets according to the specified percentage.

Performance Analysis
In addition to functional verification, it's crucial to analyze the performance impact of the XDP eBPF program. This analysis helps evaluate the efficiency and overhead introduced by the program.

1. Use the provided Golang application to collect performance metrics and statistics from the XDP program. Refer to the "Building and Running the Project" section for instructions on how to run the Golang application.

2. Monitor and observe the average processing time for both passed and dropped packets. The Golang application displays the average processing time in nanoseconds (ns) for each packet type.

    If the average processing time is consistently low, it indicates that the XDP program is performing efficiently and causing minimal processing overhead.

    If the average processing time is significantly high, it may indicate that the XDP program is introducing a considerable processing overhead, which may require optimization or further investigation.

3. Collect data and analyze the performance metrics over an extended period of network traffic to identify any patterns or trends. Look for anomalies or deviations in the processing time that could indicate potential bottlenecks or inefficiencies.

4. Experiment with different packet drop percentages and observe their impact on the average processing time. By varying the drop rate, you can assess the trade-off between packet loss and processing efficiency.

5. Performing performance analysis allows you to gain insights into the impact of the XDP eBPF program on network performance and make informed decisions about its optimization and tuning.

Integration and System Testing
To ensure the proper integration of the XDP eBPF program into the overall system, it's essential to perform integration and system testing. This involves testing the interaction between the XDP program, the network stack, and other components of the system.

Construct a test scenario that closely resembles the production environment in which the XDP program will operate. Consider factors such as network traffic patterns, system load, and the presence of other networking components.

Generate realistic network traffic using tools such as packet generators, traffic simulators, or actual production traffic if available.

Monitor the system's behavior, including packet processing, performance metrics, and system resource utilization. Ensure that the XDP program functions as expected and does not introduce any adverse effects on the system.

Test corner cases and edge conditions to validate the robustness and resilience of the XDP program. This includes scenarios such as high network traffic volumes, unusual packet structures, or unexpected network events.

By conducting integration and system testing, you can ensure that the XDP eBPF program seamlessly integrates into the broader system and operates reliably under various conditions.

Conclusion
----------

In this article, we explored the process of building an XDP eBPF program with C and Golang. We started by understanding the basics of XDP and eBPF, followed by setting up the development environment and writing the XDP eBPF program in C. We then integrated the program with a Golang application to collect and analyze performance metrics.

Throughout the journey, we learned how to compile and load the XDP program, build the Golang application, and leverage the power of eBPF and XDP to manipulate network packets and introduce controlled chaos. We also discussed testing methodologies to ensure the correctness, efficiency, and integration of the XDP program within the system.

The ability to leverage eBPF and XDP opens up a world of possibilities for network programmability, performance optimization, and security enhancements. By harnessing the flexibility and programmability of eBPF, developers can create powerful and efficient networking applications.

We encourage you to explore further possibilities with XDP and eBPF, experiment with different scenarios, and dive deeper into the rich ecosystem of eBPF tools and libraries available. Embrace the power of XDP and eBPF to unlock new horizons in network programming and performance optimization.

Happy coding!

Additional Resources
--------------------

To further expand your knowledge and explore the world of XDP, eBPF, and network programming, here are some valuable resources:

 - The Cilium Project: Cilium is an open-source project that provides networking and security capabilities powered by eBPF. Their documentation and codebase offer in-depth insights into eBPF and its applications. Visit their website at cilium.io for more information.

 - The iovisor Project: iovisor is an open-source project that focuses on building tools, libraries, and infrastructure for eBPF-based tracing, monitoring, and networking. Their website at iovisor.org hosts a wealth of resources, including tutorials, documentation, and sample code.

 - The BCC (BPF Compiler Collection): BCC is a collection of powerful command-line tools and libraries that leverage eBPF for various tracing and performance analysis tasks. The official GitHub repository at github.com/iovisor/bcc provides extensive documentation and examples to help you dive deep into eBPF.

 - eBPF.io: eBPF.io is a community-driven website dedicated to providing resources, tutorials, and news about eBPF. It features articles, case studies, and a curated list of tools and libraries related to eBPF. Explore the website at ebpf.io to stay up-to-date with the latest developments in the eBPF ecosystem.

 - Linux Kernel Documentation: The Linux kernel documentation includes a comprehensive section on eBPF and XDP, covering various aspects, including API references, usage examples, and implementation details. Access the documentation at www.kernel.org/doc/html/latest/bpf to gain a deep understanding of the underlying mechanisms.

These resources serve as valuable references and provide opportunities for further learning and exploration. Delve into the world of XDP, eBPF, and network programming, and unlock the full potential of these technologies in your networking projects.

You can also find the entire codebase for this article here: https://github.com/peter-mcconnell/dilih
