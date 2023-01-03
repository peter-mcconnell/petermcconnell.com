+++
title = "What is DevOps?"
date = "2022-12-30T20:34:57Z"
author = "Peter McConnell"
authorTwitter = "PeteMcConnell_" #do not include @
cover = ""
tags = ["devops", "platform", "engineering"]
keywords = ["devops", "platform", "engineering"]
description = "'What is DevOps?' - according to me. To cut to the chase, I think the term is bollocks and we should stop using it"
showFullContent = false
readingTime = true
hideComments = false
color = "" #color from the theme settings
+++

The term "devops" has been floating around since the late  2000s and frankly has
always annoyed me. Not that I think the intent was bad but rather the adoption
was so varied and confusing that simply saying the word out loud seemed to make
things worse and lead to fear and confusion. I'd like to make "DevOps" the
"Voldermort" of tech buzzwords - "He-Who-Must-Not-Be-Named". This happened with
Agile also which is even more confusing given it has a "manifesto" that's all
but a single paragraph, but I'll leave that for another day.

The Wikipedia (https://en.wikipedia.org/wiki/DevOps) page for DevOps is fairly
hand-wavey which somewhat highlights the issue. Like most documents talking to
"organisational change" it's a word-salad with no real actionable takeaways.

I've had several "DevOps" jobs and each of them were functionally and
organisationally different. All projects were delivered but done so more often
than not via silos. Wasn't this the problem "DevOps" was meant to solve?

Speaking of ... What _is_ the problem to solve? Shipping code to production
quickly and reliably. In ye olden times there were issues of siloed development
teams and operations teams meaning the devs wouldn't optimise for production
workloads and the operators wouldn't have a clue what they were shipping onto
their servers. There's a lot of domain expertise in both camps - asking people
to become experts of both was unreasonable.

But that was also a different time ... we didn't have the abundance of tooling
and services that we do today. Kubernetes didn't exist. Docker didn't exist.
Cloud offerings were pretty light. With the tools available today, asking SWEs
to take on more responsibility to account for their applications in production
is a reasonable ask.

so what should we do?
---------------------

Frankly I think we're now in a world that looks more like the pre-devops days.
SWE teams are no longer handing over a package of code and saying "hey, take my
source code, install these dependencies and run this" but are now in control of
their applications deployment manifest and can containerise their applications.
The original problem to solve feels like much smaller a problem now.

Operators can run a platform such as Kubernetes which for the most part the
other engineering teams can treat like a PAAS. "How will devs know how to
configure their apps to run on the platform" - they'll have to learn. Somehow.
Guardrails should be put in place (e.g. policies) to stop people "doing bad
things" but it shouldn't go as far as "that devops engineer will write your
cicd config" or "that devops engineer will write your kubernetes config". Teams
MUST own their config, and to own it they need to understand it.

So it shouldn't be a team or a job title. There shouldn't be "devops tools" or a
"devops environment". A problem can never be "a devops issue". You might have a
kubernetes team, an OPA/IAM/network policy team, a streaming services team etc.
Just don't have a "devops" team.

We shouldn't give it a new name either. Stop giving everything a name just so
you can sell books and tshirts. This just creates distance from the problem to
solve - we all just want to ship code reliably so that our business meets its
goals and so that we don't spend overtime fixing bugs or doing manual work that
could have been done by a computer.
