+++
title = "chatGPT - building an automated database testing tool"
date = "2022-12-08T11:41:50Z"
author = ""
authorTwitter = "PeteMcConnell_" #do not include @
cover = "https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/2.png"
tags = ["chatGPT", "SQL", "Python"]
keywords = ["chatGPT", "sql"]
description = ""
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

Creating an automated database testing tool with ChatGPT
--------------------------------------------------------

Last night I thought I'd try to get ChatGPT to make an automated database
testing tool and the results were quite promising.

In conclusion, with guidance, it was able to build a project from scratch that
ran a python script and postgres database. It generated some random schema and
values for the randomly generated tables. It provided a Python script which
would introspect the database and execute queries against it.

Did it all work out of the box? No. There are some bugs to fix in the python
script it generated. However the effort to go in and fix those is not high and
certainly the whole end-to-end process is cheaper, time-wise, compared to
starting from scratch.

I found that the bugs it encountered were largely due to my lack of clarity or
ordering of questions posed to it. It was quite capable of fixing its own
mistakes / updating the existing code to match the new requirements when
requested to do so.

The only _real_ issue I encountered were general API errors that one would
expect of something so popular in an early preview state.

I came away from this experiment viewing ChatGPT and whatever follows it as a
really useful development aide for those who already know how to program. It
helped me build a tool faster than I could have had I sat down to do it from
scratch. I don't view it as a replacement for software engineers yet for two
main reasons - firstly: for non-trivial applications I suspect the person
feeding requirements into the system (or "prompt engineer") needs to have a
reasonable idea of how to build software in the first place, so as to know how
to form requests and to correct mistakes / close gaps. secondly: the code being
generated isn't always sound - without an experienced engineer reviewing and
taking ownership of whatever code is produced (ownership being important for
maintainence reasons) then there's little guarantee that you will get what you
are hoping for.

However; this is still very early days. Can the problems outlined be closed
further? Absolutely. Will this sort of tooling be "bad" for software
engineering as a whole, long-term? Perhaps. Personally I'm very excited to have
this tool in my arsenal - already it has allowed me to scaffold prototype
applications quickly. Would I use it for production code in a workplace? No
more or less than I would snippets from stackoverflow or it's ilk. For now.

Github repository: https://github.com/peter-mcconnell/gpt_sql_test_generator

Screenshots:

![step 2](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/2.png "step 2")
![step 3](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/3.png "step 3")
![step 4](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/4.png "step 4")
![step 5](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/5.png "step 5")
![step 6](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/6.png "step 6")
![step 7](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/7.png "step 7")
![step 8](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/8.png "step 8")
![step 9](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/9.png "step 9")
![step 10](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/10.png "step 10")
![step 11](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/11.png "step 11")
![step 12](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/12.png "step 12")
![step 13](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/13.png "step 13")
![step 14](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/14.png "step 14")
![step 15](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/15.png "step 15")
![step 16](https://raw.githubusercontent.com/peter-mcconnell/gpt_sql_test_generator/master/media/16.png "step 16")
