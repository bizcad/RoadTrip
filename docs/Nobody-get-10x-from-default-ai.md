# Nobody Gets 10x From Default AI
- 90% of AI Users Are Getting Mediocre Output. Don't Be One of Them (Stop Prompting, Do THIS Instead)
## Transcript
<!--begin transcript-->
0:00
I'm gonna let you in on a secret. Nobody
0:02
gets 10x results from default vanilla
0:04
chat GPT, vanilla claw, vanilla Gemini.
0:07
It just isn't how it works. But most of
0:10
us have slept on the big levers that
0:13
these model makers have released to help
0:15
us to customize these models to get the
0:17
most out of them. This video is all
0:19
about those levers, what you missed, and
0:22
how you can customize your AI to get the
0:23
most from it. It's how AI averages you
0:26
out and how you can stop it. Lever
0:28
number one is memory. So Chad GBT has a
0:31
way they handle memory. Claude has a way
0:32
they handle memory. We'll get into it.
0:34
Instructions is lever number two. Again,
0:36
Chad GPT, Claude, Gemini, they all have
0:38
their versions of instructions. We're
0:40
going to hop into that. Style controls.
0:42
Chat GPT has like eight different
0:44
personalities. Claude has different
0:46
style summaries. We're going to get into
0:48
that. And then apps and tools. What apps
0:51
and tools do these models support? Look,
0:54
together these are big big changes, but
0:57
most of the time we hear about them in
0:59
clickbait articles and we're told do one
1:01
thing specifically. I don't want to look
1:03
at doing one thing specifically because
1:04
that doesn't change the averaging
1:06
function. You are being averaged out
1:09
into a median AI user and I'm interested
1:12
in you understanding the levers so you
1:14
can customize your AI into something
1:17
that truly allows you to be
1:18
transformative. So what does being
1:20
averaged even mean here? The simplest
1:22
way to understand this is imagine a
1:24
restaurant that wants to create one dish
1:27
to satisfy the widest possible range of
1:29
customers. Let's say it's pizza. They
1:31
don't want to delight anyone in
1:32
particular. They just want to avoid
1:34
disappointing too many people. Papa
1:36
John's, Pizza Hut, you get the idea. The
1:39
chef studies what most diners order.
1:41
They analyze which flavors get
1:43
consistent approval across different
1:44
demographics and they just optimize for
1:46
the middle. What do you get? Well, it's
1:48
edible. It's competent. It's technically
1:50
fine. You can make the cheese look nice
1:52
on an ad, but not your preference,
1:54
right? It's not spicy enough if you like
1:56
heat. It's not subtle enough if you like
1:58
delicate. It's not adventurous enough.
2:00
It's too adventurous if you're feeling
2:02
mild. This is exactly what AI does with
2:05
answers. It's like the Pizza Hut
2:07
approach. It's not trying to give you
2:08
the best response for your situation.
2:10
It's trying to give the best response
2:13
for everybody who might ask a similar
2:15
question. It's the statistical middle.
2:17
It's the median. When you ask for
2:19
restaurant recommendations, you're going
2:21
to get restaurants that would satisfy
### How AI Learns to Be Average
2:23
the most people who ask for restaurant
2:25
recommendations. When you ask for career
2:27
advice, you're getting advice that
2:28
applies to the broadest set of people in
2:30
roughly your situation. When you ask for
2:32
code, you get code that follows the
2:33
conventions most developers would
2:35
expect. This is why your output always
2:38
feels just a little bit off. It's not
2:40
wrong. You can't point to an error
2:42
necessarily. It's just not yours. The
2:44
recommendations hit tourist spots
2:46
instead of the places you'd actually
2:48
like to hit. The advice applies
2:50
generally, but not to your constraints.
2:52
And most people experience this and they
2:54
think to themselves, well, the AI is
2:55
just okay, right? It's probably the AI's
2:57
issue. They don't realize there's a
2:59
mechanical reason and they don't realize
3:01
that it's fixable. So, how do models
3:03
learn to be average in the first place?
3:05
This is not speculation, by the way. We
3:07
we know this. Modern AI assistants go
3:10
through something called reinforcement
3:11
learning from human feedback. And here's
3:13
how it works. The model generates
3:14
multiple responses to the exact same
3:16
prompt. Human raiders compare them and
3:19
pick which one they prefer. The model
3:21
learns to produce outputs that the
3:22
raiders would choose. You catch the
3:24
keyword, right? Raiders, not you. A pool
3:27
of people who rate outputs and judge
3:29
which seems better. The raiders are not
3:31
experts in your field. They're not
3:32
familiar with your constraints. They
3:34
don't know your preferences about where
3:36
you want to go in Paris when you travel
3:37
there. They're looking at two responses
3:40
in picking whichever one seems most
3:41
helpful, most clear, and most
3:43
appropriate. Hint, it's probably the one
3:44
with the Eiffel Tower. The model's
3:46
optimization target is thus not give the
3:49
specific user what they need. Give Nate
3:51
what he needs. It's produced something a
3:53
typical human would rate pretty highly.
3:55
So when thousands of raiders evaluate
3:57
millions of outputs, the model learns to
4:00
hit the middle of the preference
4:01
distribution. It learns the answers that
4:03
would satisfy most people. It learns the
4:05
median. And this is not a secret.
4:07
Anthropic publishes papers describing
4:09
this. So does open AAI. Nobody's hiding
4:12
it. And there's an irony here because
4:13
the training process that makes these
4:15
models so helpful in general is exactly
4:18
what makes them mediocre for you and me
4:20
specifically. The same mechanism that
4:23
prevents the AI from being weird or
4:25
offensive or unhelpful also prevents it
4:27
from being calibrated to your particular
4:29
needs. The implication is significant.
4:32
Every time you use default settings,
4:34
you're getting an answer optimized for a
4:37
hypothetical typical person. The
4:39
training literally encodes what would
4:41
most people want here as the target. And
4:43
you're not most people, you're you. For
4:45
the last couple of years, prompting was
4:47
the only way to escape the average
4:49
lifestyle. You would frontload your
4:51
context into your question. You would
4:52
specify your constraints and your
4:54
preferences, and you would steer the
4:56
model to adjust. And every conversation
4:58
had to start from scratch. That has now
5:00
changed. There are now at least four
5:02
distinct ways to steer AI away from the
### The Four Levers Beyond Prompting
5:04
median. Four levers beyond the prompt
5:07
itself. Most people are using none of
5:09
them or only one. And here's what you
5:11
need to know about each one. Lever
5:13
number one is memory. Memory is the AI
5:16
retaining information about you across
5:18
conversations. So instead of starting
5:21
fresh every time, it remembers your
5:22
context. It remembers your job. It
5:24
remembers your projects, your
5:26
preferences, etc. The promise is very
5:28
powerful, right? The AI knows you and
5:29
builds on that. The reality is platform
5:32
specific. Chad GPT's memory works in
5:34
multiple layers. There are saved
5:36
memories that are facts you explicitly
5:38
ask it to remember. And then there's
5:40
something broader like a sense of chat
5:41
history where chat GPT references your
5:44
entire conversation history to
5:45
understand your preferences. This can be
5:48
very general. When chat GPT pulls from
5:50
past conversations, now it does pull
5:53
clickable citations that let you know
5:55
exactly which chat it's pulling from.
5:57
And while this makes the system
5:59
transparent, I can tell in context that
6:02
it's still not a very good memory
6:04
implementation, it misses stuff I would
6:07
consider obvious. Chat GPT also has
6:10
projectonly memory. When you create a
6:12
project, you can isolate the memory from
6:14
general chat GPT use, and what you
6:16
discuss in that project stays in that
6:18
project. One recent change worth noting
6:20
is that temporary chats now retain your
6:22
memory, style, and personalization
6:24
settings. They used to be very stripped
6:26
down, and now they're less so. So,
6:27
what's your key tactic with chat GPT?
6:30
Tell chat GPT to remember specific
6:34
preferences that you care about.
6:36
Remember that I prefer one-s sentence
6:37
answers to factual questions is a great
6:40
example. Remember that my audience
6:43
always has people that think that they
### Memory: ChatGPT vs Claude vs Gemini
6:46
can build their own local models. That's
6:48
another example. I'm sure there's some
6:50
of you out there. The automatic system
6:52
captures a lot, but intentional memory
6:55
is very reliable if you're starting to
6:58
cultivate it with that mindset. How does
7:00
Claude work differently? Well, it has
7:01
two components. Claude can search past
7:04
conversations, sort of like a rag style
7:06
retrieval, and it can also generate a
7:08
memory summary that synthesizes key
7:11
facts across your chat history. And that
7:13
summary will update periodically. The
7:15
distinguishing feature is that Claude's
7:17
memory is project scoped at default. So
7:20
every project has a very separate memory
7:22
space and your startup discussions don't
7:25
bleed into your vacation planning. The
7:27
isolation is very intentional. Claude
7:29
keeps contexts very focused because it
7:31
needs clean context to work. This gets
7:33
it the way they build their agents.
7:35
Claude also supports memory import
7:37
export. You can bring in memories from
7:39
chat GPT or push them out to cloud
7:41
memory in another account. The
7:43
interoperability is limited. There's not
7:46
a one-click import, but technically the
7:48
capability is there. My recommendation
7:50
with claude is to use your projects very
7:52
deliberately. If you're working on
7:53
something with a very distinct context
7:56
like client engagement, just create a
7:58
project for it. The project gets its own
7:59
memory, its own instructions, and it
8:01
works really well. Gemini has personal
8:04
intelligence that connects to your
8:05
Google apps. It has, you know, Gmail,
8:07
photos, YouTube, etc. The pitch is that
8:09
you can ask about tire options on the
8:11
car and Gemini finds your car model from
8:13
the Gmail receipt and gets the tire
8:14
sizes right. Settings. Personalization
8:17
lets you connect or disconnect specific
8:19
Google apps. So you can kind of tune how
8:20
much personalization it has. The key
8:22
tactic with the Google ecosystem is just
8:25
to decide how much data you're willing
8:28
to give Google. If you want to connect
8:30
them all, you get immediate
8:32
personalization. The trade-off is a
8:35
privacy surface area and you're going to
8:36
have to make that call. So that's lever
8:38
one. That's memory. What about lever
8:40
two? Instructions. Those are persistent
8:43
context about who you are and how you
8:45
want your AI to behave. Severely
8:47
underused by most people. Chad GPT has
8:50
several instruction layers. It has
8:52
custom instructions which are multiple
8:54
text fields where you can talk about
8:55
what it should know about you, how you
8:58
would like chat GPT to respond. It has
9:00
project specific workspaces that come
9:02
with their own instructions. And it even
9:03
has custom GPTs. The key tactic here is
9:06
that your biggest leverage is in being
9:08
specific. Be concise is not super
9:11
effective at steering the model.
9:13
Instead, say, "For factual questions,
9:16
please answer in a sentence. For
9:17
analysis requests, I really need you to
9:20
walk through the reasoning step by
9:21
step." When you are clear about what
9:23
you're looking for, you are helping the
9:25
model to understand under what
9:27
circumstances you want that behavioral
9:30
response. Now, Claude splits
9:31
instructions across multiple places,
9:34
right? There's profile preferences,
9:35
there's project instructions, there's
9:37
styles. The key tactic with Claude is
### Instructions That Actually Steer the Model
9:40
that Claude's style feature is really
9:42
underused. If you have a distinctive
9:44
writing voice, if you upload samples of
9:46
your best work, Claude can generate a
9:49
style profile from them. And every
9:51
response, Claude will then be thinking
9:53
about how to match your tone, how to
9:55
match your sentence structure, etc. This
9:57
is much more powerful than trying to
9:59
describe your style in words. And even
10:01
if Claude doesn't get all the way there,
10:03
it gets you most of the way there on
10:05
first drafts. Claude markdown files
10:07
deserve their own note. So for
10:09
developers using claude code, the
10:11
instruction layer that actually matters
10:12
is a claude markdown file. Boris
10:15
Churnney, who created Claude Code,
10:16
described his team's practice. Whenever
10:18
Claude does something wrong, they add a
10:20
rule to claude. Markdown so it doesn't
10:23
happen again. The file is checked into
10:25
Git. The whole team contributes.
10:26
Essentially, the file contains project
10:28
architecture, coding standards, and
10:30
common commands that everybody on the
10:32
team can see and update all the time.
10:34
Treat this as a living document. Every
10:36
time Claude does something you don't
10:38
want, just add a note. The first version
10:41
is going to feel sparse, but within a
10:42
month, it's it's going to be all filled
10:44
out. So, that's instructions. Lever
10:46
number three is apps and tools. And by
10:48
the way, if you're wondering, I can't
10:50
remember all this. That's fine. It's all
10:51
going to be in the Substack. Tools are
10:53
capabilities the AI can use. Searching
10:56
the web, running code, creating files,
10:58
reading documents, etc. If web search is
11:00
enabled, the AI looks things up. If it's
11:02
disabled, it works from training
11:03
knowledge. So, look, most people have
11:06
default enablement and they don't think
11:08
about it. And that's the issue. And I
11:10
want you to understand that there are a
11:13
lot of different ways to configure your
11:14
apps and tools that will profoundly
11:16
shape your experience. And we should
11:18
start with model context protocol
11:20
because that underlies so much of the
11:21
rest of this. The MCP standard explains
### Claude Markdown Files for Teams
11:24
how most AI systems today connect to
11:26
external tools. Think of it as like USBC
11:29
for AI. It's a universal interface that
11:31
lets any AI connect to any tool through
11:34
the exact same protocol. Enthropic
11:36
created, but everyone's jumped on board.
11:38
There are over 10,000 MCP servers out
11:41
there, and lots more on the way. So, how
11:43
do people use these connectors? ChatGpt
11:45
will call them apps, and you can connect
11:47
to Gmail and Calendar, etc. And once
11:49
connected, ChatGpt will automatically
11:51
reference them where relevant. What I
11:53
have found in practice is that the where
11:55
relevant is very ambiguous. You don't
11:57
have to select them manually, but you
12:00
may have to remind chat GPT. It has the
12:02
capability. It also doesn't have a super
12:04
deep search capability. On claude, you
12:07
have a much wider range of MCP servers,
12:10
but the connectivity isn't always
12:11
reliable. It is, for example, quite
12:13
tricky to connect to Stripe, but very
12:15
easy if you want to connect to Figma.
12:18
And that changes all the time as people
12:19
mature those MCP server implementations.
12:22
So claude is one of those things where
12:23
you have to think intentionally what are
12:25
my tool sets and then look regularly and
12:28
say are there MCP connectors into claude
12:31
where I can use them. Now Asana was just
12:34
added Gemini is shorter on tools than it
12:36
should be and it's one of the big
12:38
weaknesses of the Gemini ecosystem.
12:40
While personal intelligent will connects
12:42
personal intelligence will connect to
12:44
apps. Gemini itself is not big on tool
12:47
use and that is one of the reasons so
12:50
many builders prefer chat GPT or claude
12:53
increasingly claude. So think about if
12:55
you're using this lever your tools are
12:58
really steering the inputs. They're not
13:00
just features that you add. If you want
13:01
the AI to work with your real files,
13:04
think about where they live and connect
13:05
them. If you want verified code, think
13:07
about how you enable code execution.
13:09
Turning tools on and off changes the
### Apps, Tools, and MCP Connectors
13:11
character of responses. A model may lean
13:14
more on web search than you want if you
13:15
enable internet. These tools are not
13:17
always good or bad. It's about you being
13:19
intentional about what you want. And
13:21
lever number four, style and tone
13:23
control. So style controls let you
13:25
adjust how AI communicates. Chad GPT has
13:28
eight different personalities ranging
13:30
from friendly to candid to nerdy all the
13:33
way to cynical. On top of presets, they
13:35
also have granular characteristics
13:37
around warmth, enthusiasm, headers, and
13:39
emojis because apparently people
13:41
complain about emojis. And so you can
13:43
pick a personality and then dial it the
13:45
way you want. Your key tactic there is
13:48
to describe the default personality and
13:51
then to be very clear in your
13:53
instructions and in your settings so
13:56
that there is no conflict. If there is
13:57
ambiguity or conflict between your
13:59
instructions. If you say be verbose in
14:01
your instructions and concise in your
14:03
personality, you're just going to burn
14:05
tokens and make chat GPT sweat. So don't
14:07
do that. Think about what you really
14:09
want. Meanwhile, Claude offers three
14:11
built-in presets: formal, concise, and
14:13
explanatory. The custom style feature is
14:16
quite sophisticated, and it allows you
14:18
to sort of upload what you want, which
14:19
is what I've talked about. But
14:21
fundamentally, if you don't want to
14:23
create a custom style, you should be
14:26
picking a style that reflects how you
14:28
actually behave. Like, if you are
14:30
actually a very casual Claude user,
14:32
don't select formal. Go with something
14:35
like explanatory where you can have
14:36
longer conversations. Think about your
14:39
actual usage, not your aspirational
14:41
usage. Across all four levers, I've
14:43
observed a really common failure mode.
14:46
Being too vague to really steer the
14:48
model. Like I said, be concise doesn't
14:50
move you. Be direct doesn't move you.
### Style and Tone Controls
14:52
The instructions that work need to be
14:55
specific enough to change the shape of
14:57
the output. Compare the difference
14:59
between be more helpful and when I'm
15:02
stuck on a problem, please ask me
15:04
diagnostic questions rather than
15:06
immediately giving solutions. I learn
15:09
better by being guided than by being
15:10
told. Wow, that is so much better.
15:12
You're going to get so much better
15:14
responses. Compare, I'm a professional,
15:16
terrible, with I've been doing product
15:19
for 15 years. Please skip fundamentals
15:21
and go straight to nuance. The specific
15:24
versions tell the AI where you are at
15:26
and help it to help you. So it's not
15:28
just delivering that averaged out median
15:30
answer that always feels off. And this
15:33
is where we start to separate people who
15:35
get real value from AI and people who
15:37
find it perpetually mediocre because
15:39
every interaction is generating
15:41
information about what you need. And if
15:43
you set your levers correctly, it starts
15:45
to compound. Because every time you
15:47
think that's not quite right, think of
15:49
it as discovering a steering input, not
15:52
just something you can get frustrated
15:54
about and say, "Well, AI didn't get it
15:56
again." Because most people will correct
15:58
in their head, get frustrated with AI
16:00
and move on. The people getting 10x
16:03
results, they do something different.
16:05
They capture the corrections and when
16:07
they notice a pattern, they encode it
16:08
back into the AI and add it to their
16:11
instructions. They tell memory to retain
16:12
it. They update their style settings.
16:14
Boris Churnney runs five claude
16:16
instances in parallel and another five
16:18
to 10 on cloud.ai and ships roughly a
16:20
100 PRs a week. His workflow is not
16:23
magic. It's just the discipline to look
16:26
at every mistake that Claude makes and
16:28
update a rule in claude.mmarkdown. You
16:31
don't need to be an engineer to do this,
16:32
right? You can keep a notes file. You
16:35
can find yourself making the same
16:36
correction twice and write it down. You
16:38
can review your instructions manually
16:40
every month. This is actually not that
16:43
hard and the gap will widen over time as
16:47
you start to invest in getting the
16:49
levers right. Now, I want to be honest
16:50
here. Steering fixes the personalization
16:53
problem. It does not fix everything.
16:56
When the model hallucinates, that's not
16:58
an averaging problem. No amount of
17:00
personal context fixes that. There's
17:03
also a ceiling in creative work. When AI
17:05
generates pros or images, its training
17:07
data pulls toward the center of the
17:09
distribution. You can steer against
### How Corrections Compound Into 10x Results
17:11
this, but you're still fighting gravity.
17:13
Steering always takes effort. You're
17:16
figuring out your position. You're
17:17
encoding it. You're maintaining it. It's
17:19
costing you time. And if you use AI only
17:22
occasionally, to be honest, it's
17:23
probably not worth it. But if you use
17:26
your AI multiple times a week for
17:28
similar types of work, the math changes
17:30
because a few hours of investment every
17:33
now and then buys you permanently better
17:35
output. And the compounding effect in
17:37
saving you time is real.
17:40
and it gets better the more you use it.
17:42
Know which kind of user you are. If this
17:44
feels like a lot, you can really start
17:45
very simple. You can pick one task where
17:47
you use your AI regularly and you just
17:50
the output doesn't feel right. And over
17:52
the next few sessions, notice the
17:54
adjustments you're making and write them
17:55
down. And that's it. And then go in and
17:57
find the custom instruction setting for
17:58
your preferred AI and stick those in and
18:01
notice the difference and iterate.
18:02
That's as simple as it gets. I want you
18:05
to know that the median isn't mandatory.
18:08
The AI you're using is trained on
18:10
everybody else's feedback. It learned to
18:12
please everybody a little, which means
18:14
it learned to please no one in
18:15
particular. Default output really is
18:18
median output. It's optimized for very
18:20
typical users with typical needs. And
18:22
you are not typical. I am not t typical.
18:25
Your constraints are specific to you.
18:28
Your goals are specific to you. And the
18:30
farther you are from the average, the
18:31
more default settings will fail you.
18:33
Please don't forget your levers. You can
18:35
you can go beyond prompting. You can do
18:37
memory, instructions, tools, and style.
18:39
And by the way, prompting is still
18:40
useful. I didn't talk about it in this
18:42
video, but it's still helpful for
18:43
steering in conversation. Most people
18:45
are going to ignore these levers or do
18:47
only one. If you are starting to get
18:50
averaged and you're tired of it, you can
18:52
adjust more than one lever and you can
18:54
very quickly start to compound toward a
### What Steering Can and Cannot Fix
18:56
more personalized AI that actually fits
18:59
you. So, the choice is yours. You can
19:01
stay at the median or you can steer the
19:03
ship and get the AI you want. and order.
<!--end transcript-->