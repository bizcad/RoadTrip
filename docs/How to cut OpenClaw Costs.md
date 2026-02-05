# How to cut costs with OpenClaw
## Transcript
<!--begin transcript-->
Transcript


0:00
Hi, this is Matt Ganzac and this is the
0:02
OpenClaw token optimization guide. And
0:05
if you're not familiar with OpenClaw,
0:06
it's an AI personal assistant that you
0:08
can deploy locally. A couple of things
0:10
that I want to tell you. One, you
0:13
probably shouldn't do this if you're not
0:15
a developer or if you haven't deployed
0:18
apps locally before, developed any apps
0:20
before. So, I definitely don't recommend
0:22
it for you. Uh, number two is um be sure
0:26
to deploy it on a controlled
0:29
environment. So on a PC or Mac,
0:33
definitely Mac is better. Uh deploy it
0:35
on its own device. Like do not deploy
0:38
this on your own machine. It's going to
0:41
try to log in to your apps. It's going
0:43
to try to access things. It's going to
0:47
um one guy even said that it accesses
0:49
credit card. he went and asked it to
0:51
rebuild his brand and it went and bought
0:53
a $3,000 course, consumed the course in
0:56
order to help him to build his brand.
0:59
So, yeah, like it will literally go do
1:02
things for you and you need to be very
1:04
careful. So, I need to preface that
1:07
entire thing here. Uh, another preface
1:09
that I should add and a disclaimer here
1:12
is that I'm giving you the steps that I
1:15
took and if you're trying to follow
1:17
these exact same steps, there is a
1:19
chance that you'll possibly break your
1:22
open claw if you don't know what you're
1:23
doing. So, please don't try to do these
1:26
customization things uh if you don't
1:29
know what you're doing. So, it's not my
1:30
fault. I'm not doing the coding work.
1:32
I'm just giving you exactly what it is
1:34
that I did. And hopefully this will help
1:36
some people. I've been posting over on
1:38
Tik Tok and Instagram and I've been
1:41
helping a lot of people just in those
1:42
one minute videos. So, I want to make
1:45
something a little bit more
1:46
comprehensive to dive in a little bit
1:47
deeper uh to answer some of those
1:49
questions that I've been getting. So,
1:52
first off, uh OpenClaw again, it's an AI
1:55
that connects to um other platforms like
1:59
Claude, O Open AI, so forth. When I
2:03
first built my V1, I tried to use OpenAI
2:07
and it built the app like terribly and
2:11
it was uh it didn't do anything really.
2:14
So like I was just fighting it and it
2:17
was lying to me and it was really
2:18
frustrating. [snorts] So I terminated it
2:21
and did um uh V2 and I created V2 of my
2:25
app with Sonnet. And when I went through
2:29
um Sonnet's a little bit cheaper than
2:30
Opus and Haiku is cheaper than Sonnet.
2:34
So it's this hierarchy of um spend. But
2:38
that being said, it cost me about $3, a
2:41
little less than $3 to deploy and
2:44
configure the entire app for using
2:47
Sonnet. And it it it was definitely
2:49
worth it. Like it really gave me a good
2:52
foundation and a good architecture to
2:54
build on top of. But I noticed some
2:56
issues as I was running Sonnet. And
3:00
these are the steps that I took to
3:02
reduce my cost by 97%.
3:05
So it's a pretty massive shift in the
3:09
amount of tokens that were being used
3:10
and expensed. and I'll give you the um
3:13
exact reasoning and exactly how I found
3:16
it in the token audits that I do once a
3:19
day and how I fixed it step by step so
3:22
it's not you know real complex. All
3:24
right. Uh also below this video I'm
3:27
going to give you a link to this guide
3:28
so you can actually go through it and
3:30
copy and paste everything so you can
3:32
have a download to this. But let's run
3:34
through it. I'm not going to read every
3:35
single word on this page. You can read
3:37
it yourself. Um key thing is uh just
3:41
keying in down here before and after
3:44
like daily usage. Um uh this was daily
3:48
usage like just running one or two tasks
3:50
was like $2 to $3. So monthly would have
3:53
been you know $90 and and this is just
3:56
it almost just sitting idle. It was
3:59
still spending $2 to $3 a day just
4:02
sitting idle. And um now after
4:05
technically I'm at zero sitting idle and
4:08
I'll explain that in a moment. Uh but
4:10
you know you want this to be able to run
4:12
tests. So what sort of tasks do I have
4:14
it running? I have it finding
4:16
opportunities for us. Uh we run venture
4:20
companies. So I have it finding
4:22
opportunities and crafting outreach
4:25
messages. And I'm not letting it send
4:28
emails yet. I'm not letting it be fully
4:30
autonomous and do things like that. But
4:32
it's doing the research and um uh
4:35
getting valid email addresses. Uh I do
4:38
B2B business so a lot of our apps like
4:41
our hospital app um you know I can't run
4:45
ads to a hospital app and find the
4:48
specific you know VP of patient safety
4:53
at XYZ hospital. I'm not going to find
4:55
them through ads. Sure, I could do cold
4:57
outreach on LinkedIn, but you know, this
5:01
app is finding their LinkedIn profile,
5:03
but it's also finding their email
5:04
address, so I can send them an email and
5:06
kind of tell them about what it is that
5:07
we do and find a opportunity to work
5:09
together. So, B2B business, this is
5:11
phenomenal. Uh, you can do so much with
5:14
this. That's just one use case that you
5:16
can do.
5:17
Now, one of the things that I found was
5:19
wrong, and this is a core logic of the
5:23
architecture of OpenClaw is that it's
5:26
loading your entire history on every
5:28
message. It's loading all your context
5:31
files. It's loading and your context
5:33
files are a little bloated and the more
5:36
you know you put in your context files,
5:38
soul, user identity, etc., uh, the more
5:41
bloated it's going to be every single
5:43
time. So every heartbeat it's going to
5:46
um expense tokens. Every single time you
5:48
ask it to do something, it's going to
5:50
run your context files and so forth. So
5:53
I was wasting 2 to three million tokens
5:56
just on heartbeats. Like my heartbeat
5:59
was like running every 30 minutes and I
6:01
was expensing that many tokens every 30
6:03
minutes. I was like what's going on
6:05
here? Like I loaded up $25 to Anthropic
6:09
and uh I was on target like just sitting
6:13
idle to spend almost $20 in the day just
6:17
doing nothing. And that's definitely an
6:19
issue. Um and it it's not something
6:22
that's written into um you know the the
6:25
web platform and so forth. Uh so it's
6:28
not something that you could just go and
6:30
just do. You need to provision your app
6:32
in order to do these things. So this is
6:35
one thing that I did is I'm not loading
6:38
all the context files every single time
6:40
now. So that alone saved me like 80% of
6:43
my context overload just on that alone.
6:46
So that was a huge Here's my before and
6:49
after. So before it was about 50
6:51
kilobytes on context on startup and also
6:55
every single time I prompted it and also
6:57
every single time there was a heartbeat
6:59
like every single time it was just
7:01
bloating and getting bigger and bigger
7:03
and bigger as the memory was getting
7:05
bigger and bigger and bigger it like
7:07
that's just compiling the amount of
7:09
tokens. So if you've been using it for
7:11
weeks or months, you know, the context
7:13
might be much bigger for you and every
7:16
single time you take any sing any
7:18
action, your uh context file size could
7:21
be going from 50 to 75 to 100 and
7:24
beyond. And that's really compiling the
7:27
data usage for no reason. Like you're
7:30
literally doing nothing and you're
7:32
having to pay money for no reason. So
7:34
that's essential. The other thing is uh
7:37
a lot of people are saying that you can
7:39
only run one um AI model and it's wrong.
7:44
So I'm actually running three AI models
7:47
actually technically four because I made
7:51
another change just recently uh this
7:53
morning. But just going ahead and giving
7:55
you some understanding of this you'll be
7:58
able to go to your open claw uh your
8:01
config file. So this is your config
8:02
file. Inside of there you'll see agents
8:04
default model and then you'll see
8:06
whatever your primary model is. So if
8:09
you're setting it up initially on sonnet
8:11
this would be sonnet. You can set it up
8:13
this way to have multiple models. And I
8:16
also added a third one here for opus
8:19
that I have like 1% of my task going
8:23
through opus. So currently it's like 85%
8:27
is running through haiku somewhere
8:28
around there. uh 10% on sonnet and 5% on
8:33
uh or less on um opus. So the point of
8:37
saying that is you can segment tasks and
8:40
and put it into the memory and you can
8:43
segment tasks for this to say that task
8:47
is a brainless task and I don't need to
8:49
run opus for some brainless task uh you
8:52
know such as moving files around
8:54
organizing things like compiling CSVs uh
8:58
all into one or whatever it is that
9:00
you're doing as like a brainless data
9:04
entry task. You don't need to be using
9:07
Opus or Sonnet. You could use Haiku, but
9:10
I'm actually using um Olama, which is a
9:14
free LLM, and I'll explain that in a
9:16
second, but I'm using that to do my
9:19
brainless tasks and also my heartbeats
9:21
and so forth. getting ahead of myself,
9:22
but um point being you can have four
9:25
different models running at the same
9:26
time and then have your critical um and
9:31
uh different levels of the criticalness
9:34
of the tasks based upon what it needs to
9:37
be reasoning and thinking. You can
9:39
assign each model based upon your use
9:43
case, based upon what reasoning needs to
9:46
be included or what needs to be written
9:49
or so forth. and you can run things on
9:52
Haiku, which is like 10x 50x cheaper,
9:56
and be able to have the same output. So,
9:58
if you're just running Opus or you're
10:00
just running Sonnet or some other AI
10:03
model, you're probably burning tokens
10:07
for no reason because you could have one
10:09
of the cheaper models do the tokens for
10:12
you, right? So, you're adding routing
10:14
for it and you'll have to define what it
10:17
is that your business does and and what
10:20
it is that you need it to accomplish.
10:22
And then you assign which model based
10:25
upon which tasks you want it to do. And
10:28
if it hits a block, if there's like a a
10:30
block that will happen, it escalates to
10:33
the next highest model. If there's a
10:34
block there, it escal escalates to the
10:37
next highest model. So you can set it up
10:39
that maybe it it even starts with the
10:42
free, you know, uh, local LLM and then
10:45
maybe it goes to Haiku and then maybe it
10:47
goes to Sonnet and maybe it goes up
10:50
there to Opus as as a final and so
10:53
forth. So there are ways to do this. So
10:56
[snorts] before I was using Sonnet for
10:57
everything. So it was like a fraction of
11:00
a penny for a,000 tokens. Um, and I
11:04
brought it down considerably just by
11:07
having Haiku do like 80% of the lifting.
11:11
And, and now with that, I even have LLM
11:14
on the front. So, it can do probably 15%
11:18
of my front-end tasks. And it's probably
11:20
75% now if I were to say on Haiku, maybe
11:24
10% on Sonnet, and like 3 to 5% on Opus.
11:27
So, I can escalate things without
11:30
burning tokens. So, uh, you can put your
11:33
heartbeat on Olama. So, heartbeat is
11:36
when it it kind of pings the system to
11:39
let it know like, hey, everything's kind
11:41
of running. I do you have any active
11:43
tasks? If you don't have heartbeat
11:45
running, um, it it could just put itself
11:48
to sleep and not finish the task that is
11:51
at hand. But if you have heartbeat
11:53
running, it'll give it a little poke and
11:54
just say like, hey, what's going on
11:56
here? Um, you know, do you have any open
11:58
tasks? Do you need to move along on
12:00
these tasks? what what's going on. And
12:02
every single time it runs heartbeat, it
12:06
is sending context files and also um uh
12:10
searching u uh history, session history
12:14
as well. Um some people it's not
12:16
searching session history, but what I
12:19
found when I did my token audit is that
12:21
it is actually uploading my session
12:24
history. And we'll talk about session
12:26
history in a moment, but session history
12:29
is like if you're using Slack to
12:32
communicate with your bot or WhatsApp,
12:35
it's looking at everything that you've
12:37
ever said in Slack and it's compiling
12:40
that. When when I looked at my logs and
12:41
I I did a token audit, I had 111
12:45
kilobytes of session of just text that
12:49
was being sent. every single time I
12:52
prompted it again, it was putting it
12:54
into the context, putting it in, you
12:56
know, with the memory and uploading it
12:58
every single time. And I saw it, it was
13:01
in the logs. I was like, we don't need
13:03
to do that. So, you have to build a
13:05
command to kill your session and then
13:08
when you do a new prompt, it's not going
13:10
to be loading the context of every
13:13
single thing you've ever talked to it
13:14
about. kind of going off the rails here,
13:17
but um so you'll install this local LLM
13:21
and you can add it just like this. So
13:23
this is what mine looks like and you can
13:26
add the OAMA like this is the latest
13:29
version right now. If you're watching
13:30
this couple weeks or a couple months
13:32
from now, that version might be a little
13:33
bit different. So, I would just make
13:35
sure you have the latest version of it
13:37
and when you do run it, you can run it
13:40
here and then you can find the latest
13:42
version and make sure you install the
13:45
latest version, etc. So, with that being
13:48
said, now I can have Olama run my
13:51
heartbeats and uh purpose of that is I
13:55
don't want to expense tokens for
13:57
heartbeats. Like that's it sitting idle
14:01
and you are paying money. Like why would
14:03
you do that if you're on Opus and you
14:05
don't configure these things? You might
14:07
be spending $5 a day just to have it up
14:09
running and it's sitting idle not doing
14:12
anything. So why would you do that? So
14:15
why not set it up and configure it that
14:18
the heartbeat is just running locally
14:20
cuz it's it's brainless. Like there's
14:22
really nothing to it. It's like check
14:24
your memory and check your task and make
14:26
sure everything's okay. Um and then it
14:28
comes back system okay. um you know
14:30
heartbeat check okay or whatever words
14:32
are that it says but the point of that
14:35
is you don't need to be making API calls
14:37
for heartbeats period end of story this
14:39
should be a core integration into
14:43
openclaw and if it like hopefully like
14:46
somebody can commit this to it or maybe
14:48
I'll go and commit it to it but this
14:50
should be a core integration because
14:52
there is no reason that you should
14:55
expense uh API um uh tokens on
14:59
heartbeats period. Like I I can't I
15:02
can't think of any use case in why that
15:05
would be needed like that. There's no
15:08
reason for it because all it's doing is
15:10
just checking its local memory and
15:13
checking its local um uh task that it
15:16
has running. So why would you do that?
15:18
Another issue that I was running into
15:20
was rate limits. So, when you initially
15:23
sign up for Anthropic to have an API
15:25
key, it gives you something like 30,000
15:28
uh tokens per minute. And like I was
15:31
saying, and and this is where I found
15:33
the session history problem. And I
15:36
probably would have never found it if it
15:38
wasn't for the rate limit. So, thank you
15:39
for having a low rate limit that I could
15:41
see that. And it was pinging like a
15:45
million tokens and and uploading way too
15:48
much all at once for no reason. And what
15:51
I found was it was uh compressing all my
15:55
cont well it wasn't compressing it was
15:57
uncompressed all my context files and
16:00
then it was doing the call but it was
16:02
uploading my entire session history from
16:04
Slack every single time. So when I made
16:07
a command and I prompted it to make a
16:10
command and we came up with a command
16:11
name uh new session. So anytime I say
16:14
new session, dump all of your previous
16:16
session history but save it in your
16:19
memory so we can recall it at a later
16:22
time. So that's how my memory is
16:24
configured and I can dump my Slack
16:27
session. So it's not compiling every
16:30
single thing I've ever said in Slack
16:32
every single time I prompt it to send it
16:35
to the API in order to make a call. So
16:39
yeah, that was huge. And so that made a
16:42
huge difference with the rate limits.
16:44
And now I have built-in pacing. And uh
16:47
you can read how I did the built-in
16:48
pacing and so forth. And it's so
16:51
important so you're not hitting those
16:52
rate limits every single time. I was
16:54
getting uh 429 every single time I was
16:58
submitting. And um I figured out it was
17:01
Slack because I went to the web version
17:03
of it and I was doing the same exact
17:06
prompt in the web version, not in Slack.
17:09
and the calls were going through fine.
17:11
So I read the logs and read what was
17:13
being sent and looked at the tokens in a
17:14
token audit and then I went side by side
17:17
to say Slack is compiling every single
17:19
message I have ever sent Slack every
17:22
single time I prompted again. And I
17:24
haven't tested that on WhatsApp. If if
17:26
you have on WhatsApp like leave a
17:27
comment below and let me know. But I
17:29
would imagine that any um any messaging
17:33
platform that uh uh that does this and
17:36
allows you to communicate with it, it
17:38
probably does the same thing and it's
17:40
compressing it. It's taking your entire
17:42
session history and sending it uh to
17:45
expense AI tokens every single time uh
17:48
you use it. So, some other things I did
17:51
is I took my work plate uh my workspace
17:54
files and I compressed some of these and
17:55
I brought them down and then I told it
17:58
exactly what to do with my model
18:00
selection and the switching too and
18:02
switching back and forth. I put all the
18:04
rate limits in there and breaking that
18:06
all down as what it needs to do. Um, and
18:09
then I define some key metrics in here.
18:11
And you can put one of the metrics being
18:14
uh one of the metrics that you want to
18:16
accomplish is low token usage. So you
18:18
can literally tell it to optimize for
18:20
tokens. So now every single time I
18:22
prompt it, it tells me how many tokens
18:25
it's going to expense in order to
18:26
achieve the goal. Like go find me a,000
18:29
leads for this business and you know
18:31
find the best email address and find
18:33
their LinkedIn and find the decision
18:34
maker and yada yada yada yada whatever
18:37
and tell me how many tokens you're going
18:38
to expense. Now it's like you know it'll
18:40
use 60 tokens or 60 cents on that uh in
18:44
order to achieve that. I'm like okay
18:46
great do it. Then at the end uh it tells
18:49
me how many tokens it actually used and
18:53
uh I'm able to say like oh well we were
18:55
close or you know what was wrong what
18:58
was the block what was the problem and
19:00
then we can work through that and and
19:02
work through it but in the um you know
19:05
success metrics that is one thing I
19:07
added in there run efficiently like run
19:10
efficiently so I'm not expensing tokens
19:14
for you know no reason. I've had some
19:16
people messaging me um uh and you can
19:19
verify your entire setup and go through
19:21
these steps and you have a little uh
19:23
checklist here. I had some people
19:24
messaging me saying like, "I went to bed
19:26
and I woke up in the morning and it
19:28
burned $500." Like that's another thing
19:32
is don't like until you really get this
19:35
thing dialed in, don't allow for
19:37
Anthropic to automatically bill you.
19:40
Like just add a couple of dollars on
19:42
there and then be like really mindful of
19:44
how that's being spent. So I have on my
19:48
screen if you were looking at my screen
19:51
of my agent. This is not my agent. This
19:53
is my laptop. Uh but on my agent, I keep
19:57
the um the dashboard for the tokens up
20:00
and then each time that you know I run a
20:04
test um I I take a screenshot of the
20:06
tokens and I give it back to the
20:09
OpenClaw bot and I say you know uh uh
20:13
compare what you think the token usage
20:16
was and what you thought the cost was to
20:18
the actual cost and the actual token
20:21
usage. So, I give it a couple of
20:22
screenshots from the dashboard and then
20:24
it's like, "Okay, great." You know, I'm
20:26
I'm calibrating now to make sure that
20:28
it's more accurate. I had to do that
20:30
like three times and once I did it three
20:32
times, it got to the point that it was
20:34
like 99% accurate to um figure out what
20:39
the cost would be. Another thing really
20:42
important to do, and I didn't add it in
20:44
here, but I probably will, is caching.
20:47
So you the cache API cost is way lower
20:52
than anything else. So, I ran a task and
20:55
it was like 95% of the task was on uh
20:59
cached um uh tokens and so forth. And I
21:03
ran this like massive task overnight and
21:05
it was probably like 6 hours of just um
21:08
doing research and looking things up and
21:10
writing emails for me and writing
21:12
followup and you know putting it all
21:14
into the right folders and organizing
21:16
everything and and doing all that for
21:18
me. And at the end it was like that cost
21:22
you $6. I'm like that is insane because
21:26
you know we pay as a venture studio like
21:29
we pay people to go and do research for
21:31
us, do data entry and go find decision
21:35
makers. So, we pay people to do that and
21:37
it cost us tens of thousands of dollars
21:39
and the performance of what it is that
21:42
they do versus what uh OpenClaw did
21:45
overnight for me in one day overnight is
21:48
basically what I would pay that company
21:51
a month to do research on. And it did it
21:54
overnight and it was like $6. I'm like,
21:57
this is absolutely insane. So, you know,
21:59
I can do my work and work, you know,
22:01
work through my day and have it help me
22:03
out and and help me through things, but
22:05
at the end of the day, I can say, "Hey,
22:07
go find me some new um, you know, go
22:10
find me a new hit list for XYZ." And
22:14
when I wake up in the morning, it'll
22:15
have a hit list all organized and all
22:18
refined, everything compiled in a master
22:20
list, etc. So, it's incredible. So when
22:24
I set this up and the way that mine's
22:26
set up is we spin up these sub agents in
22:30
order to you know do the the crawling
22:33
work and I'm using uh Brave search API
22:36
and then I'm using like hunter.io to go
22:39
and find their real email addresses both
22:41
APIs and what it's doing is it's
22:45
spinning up these sub aents. It spinned
22:47
up like spun up like 14 sub aents for me
22:51
and it did all the work based upon this
22:53
one was doing this and then Sonnet was
22:56
doing the research and writing the thing
22:58
and Haiku's going out there and running
23:00
it and then on the back LLM the uh Olama
23:04
is organizing all the files. So they're
23:07
feeding the data in and then the sub
23:10
agent for OAMA it was just organizing
23:13
files and putting things together and
23:15
making sure the headers and the CSVs
23:17
look good and everything. So I had three
23:19
different agents running. I didn't have
23:21
Opus running at all in the task last
23:23
night. I had um I I had haiku going out
23:28
there and finding the information like
23:30
it was reading blogs and you know I was
23:33
looking for distressed businesses and
23:36
and so forth. So it was reading blogs,
23:38
it was reading like all these insights
23:39
and you know doing all this research and
23:41
everything and then it was finding one
23:44
pushing it over to Sonnet. Sonnet was
23:46
writing my emails and my cold outreach
23:49
and what I need to do for today to reach
23:51
out to them and structuring all the
23:53
followup and all of that of what it
23:54
needs to do. And then the Lama uh on the
23:58
LLM was organizing the files and getting
24:01
my file structure put together and
24:02
making sure everything was clean. So
24:04
when I wake up in the morning, I can
24:06
just do the task and I'm doing the
24:08
outreach. I'm not letting this machine
24:09
do outreach right now. Maybe in the
24:11
future I will, but today no. So, like
24:15
then I can set up my outreach and and
24:18
set up, you know, getting demo calls
24:20
booked and and getting situations going
24:22
on. And it ran for $6. It ran all night,
24:27
six hours for $6. So, it's like a dollar
24:31
like an hour. It's [laughter] like just
24:34
put your head around that. If I had it
24:37
running 24 hours a day, um it would be
24:41
about a dollar an hour. And no one is
24:44
working for a dollar an hour this
24:46
efficiently, having 14 sub aents running
24:50
and doing things all at the same time
24:52
and working interchangeably.
24:55
That's what is insane about this
24:57
platform. But if you know some people
25:00
are just run Opus. If you're literally
25:03
just running Opus, that task would have
25:05
been like $150 that happened last night
25:08
and it cost me $1, right, for an hour,
25:12
right? So, that is what's insane about
25:16
this, but you need to be mindful of the
25:18
token optimization and that's why I put
25:20
this thing together. If you have any
25:22
specific questions, you can mention them
25:23
in the comments. I'll jump in and try to
25:25
help you guys out along the way. But, I
25:27
want you guys to reduce your token cost
25:29
because you're not going to run this
25:31
thing and it's not going to be
25:32
efficient. You're not going to be happy
25:34
with it if you're expensing 50 or even
25:37
what the one guy said $500 in tokens
25:40
overnight. uh and it it's doing a little
25:43
bit but really not crushing it for you.
25:46
Right? So hopefully this was helpful. Um
25:48
leave a comment below if you have any
25:50
questions and you can link below to this
25:52
document and follow the steps and get
25:54
yours optimized to have those multiple
25:56
sub aents and then run the different
25:59
tasks based upon um you know the
26:02
reasoning that you need. Haiku is great
26:04
for like most things. Haiku can do most
26:06
things. um you know, sonnet for writing,
26:09
uh doing some coding, opus for like the
26:12
most complex and so forth, but install
26:15
the lama, install the local LLM to do
26:18
the basic things, heartbeat and
26:20
everything, and you're going to reduce
26:22
your AI cost significantly by doing
26:24
this. So, thank you guys so much. See
26:26
you on the next video.
<!--end transcript-->

## Summary
