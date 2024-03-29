+++
title = "Hugo"
date = "2022-11-29T23:16:21Z"
author = ""

cover = ""
tags = ["hugo", "aws", "amplify"]
keywords = ["hugo", "aws", "amplify"]
description = "How I set the initial version of this website up; for free"
showFullContent = false
readingTime = false
hideComments = false
color = "" #color from the theme settings
+++

How I set this website up, for free
-----------------------------------

tldr; Hugo + Github + AWS Amplify. Easy peasy.
total time: 1 hour (mostly spent writing content)

Some parameters:

 - free templates. I'm no designer
 - static web asset output is fine. I'm not building a backend (yet)
    - but having the option to do so is a bonus
 - this project should be as low effort as possible
     - so; no html / css / js where possible
     - also; automated deploys on push to $branch
        - ideally I don't need to maintain ci to do this. lowest poss. effort
 - as cheap to host as possible. free, ideally

In summary I want to only write page content. No code. No pipelines. No buttons
to click. But I still want uri's, the abililty to render rich media and a pretty
template that I need to do nothing with. And I'd like to not pay for any of it.

### static web files

I've heard about Hugo for years but never had the opportunity to try it out and
knew from the criteria I had that it should solve getting me the static assets
quickly. Even if it didn't turn out to be the _right_ tool, I knew
experimentation would be cheap.

Install was super easy: https://gohugo.io/installation/linux/

I then jumped over to https://gohugo.io/getting-started/quick-start/

This quick start guide felt like all I'd need so I went searching for a theme.
The power of search engines brought me to https://hugothemesfree.com/. The tags
on the right of this page helped me find the terminal theme quickly
(https://hugothemesfree.com/a-simple-retro-theme-for-hugo/) which reminded me
of my old i3 + polybar configuration. MIT licensed too. Bingo.

A few `hugo new posts/thing.md` and `hugo new otherthing.md`'s later and I had
my static website files. I opted to bake the theme into the repo so that I
could mutate the files. Created a new repository
(https://github.com/peter-mcconnell/petermcconnell.com) and threw my files
there for safe keeping. Now I just needed somewhere to host it.

### a search for cheap hosting solutions

The most obvious route was github pages but I wanted to look at other options
which offered some extra features should I need them in the future.

A quick look around lead me to AWS Amplify - a service I admittedly hadn't
heard of before. A quick look over the marketing material
(https://aws.amazon.com/getting-started/hands-on/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/module-1/)
looked like it was interesting; Lambda, API Gateway, Dynamo DB - all things
that pluck on my cheap-skate heart strings. Pricing:

https://aws.amazon.com/amplify/pricing/

I'm no Madonna - I think my personal website is probably a safe bet to do
"free tier" numbers (<500k req.|15Gb egress|100Gb req. duration per month).

I logged into my personal AWS account, went through the little Amplify setup
wizard, pointed it to my github repo, updated my DNS records to whatever the
wizard was telling me to and voila - https://www.petermcconnell.com/ is up and
running.
