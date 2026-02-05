# Sam Altman's Confession
## Workflows have changed
## Transcript
<!--begin transcript-->
Transcript
0:00
Sam Alman, CEO of OpenAI, made a
0:02
confession recently. He shared that
0:04
despite being the CEO, despite having
0:06
the best access to the most capable AI
0:08
tools on the planet, despite his own
0:10
internal data showing that AI now beats
0:12
human experts on 3/4 of well scopeed
0:15
knowledge tasks, guess what? He still
0:18
hasn't really changed how he works.
0:20
Altman admitted at a town hall recently
0:22
that he still runs his workflow in the
0:25
same way. Even though, quote, he says,
0:28
"I know that I could be using AI much
0:30
more than I am." That's Sam Alman. This
0:33
is the strange paradox at the center of
0:35
AI right now. Something fundamental
0:37
shifted in December 2025. The people
0:40
closest to technology are calling it a
0:42
phase transition, a threshold crossing,
0:45
a break in the timeline. Andre Carpathy,
0:47
who helped build open AAI and has been
0:49
writing code professionally for decades,
0:51
says his workflow has now inverted in
0:53
just a matter of a couple of weeks. From
0:55
80% manual coding to 80% AI agents.
0:58
Ethan Mollik, the Wharton professor who
1:00
tracks AI adoption, has put it really
1:02
bluntly. Projects from 6 weeks ago may
1:04
now already be obsolete. And yet, most
1:07
people, including the CEO of Open AI,
1:10
haven't caught up. The capability is
1:12
there. The adoption is not. It's just
1:15
going too fast. Understanding this gap
1:17
and what to do about it is the real
1:19
story of January 2026. So what actually
1:22
happened in December? The shift was not
1:25
just one thing and I think that by
1:27
itself is part of the story because
1:29
previously I could point to this model
What Actually Changed in December
1:31
released and this was the change. Not
1:33
anymore. This is a convergence of model
1:35
releases. It's a convergence of
1:37
releases, orchestration patterns and
1:39
proof points that all together crossed a
1:42
bunch of respective thresholds in the
1:44
same compressed window. This is exactly
1:46
what AI accelerationists have been
1:49
telling us is coming. Change will happen
1:51
slowly and then all at once. This is one
1:55
of those all at once moments. Start with
1:57
the models. In the space of just 6 days
1:59
late last year, three frontier releases
2:02
landed. Google's Gemini 3 Pro, OpenAI's
2:05
GPT 5.1 Codeex Max, and then 5.2 came
2:09
out soon after that. And then also
2:11
Anthropics Claude Opus 4.5. All of these
2:14
models are explicitly optimized for
2:17
something previous models could not do
2:19
well. Sustained autonomous work over
2:22
hours or days rather than minutes. GPT's
2:26
5.1 and now 5.2 class models are
2:29
designed for continuous operation more
2:31
than a day of autonomous work. Claude
2:34
Opus 4.5 has introduced an effort
2:37
parameter that lets developers dial
2:38
reasoning up or down. And Enthropic has
2:41
priced it 2/3 cheaper than the previous
2:43
version. And now we have techniques like
2:46
context compaction from both OpenAI and
2:48
Anthropic that lets the model summarize
2:50
its own work as sessions extend so that
2:53
the model can more easily maintain
2:55
coherence again over longer time frames.
2:58
Are you getting the theme? Look, the
3:00
cursor team has tested these models.
3:02
Other teams have tested these models.
3:04
We're seeing reports come back of models
3:06
being able to do a week of work
3:08
autonomously and code up to three
3:10
million lines before coming back for
3:11
more. This is not the same category of
3:14
work as we were seeing even in September
3:16
and October of 2025. It's a new
3:19
category. Things have changed all at
3:21
once. And you know what? Better models,
3:23
as much as I like them, were necessary,
3:25
but they were not sufficient. The real
3:28
unlock came from orchestration patterns
3:30
that went viral in late December. The
3:32
first was Ralph, named after the
3:34
Simpsons character known for cheerful
3:35
obliviousness. Jeffrey Huntley, an
3:37
open-source developer way out in rural
3:39
Australia, grew frustrated with Agentic
3:41
coding central limitation. Models keep
3:44
stopping to ask permission or they
3:46
report progress and they're wrong or
3:47
they're overoptimistic. And every pause
3:50
requires human attention and often
3:51
you're frustrated because you're telling
3:52
the model the same thing. So all
3:55
Jeffoffrey did is he wrote a bash script
3:57
that runs claude code in a loop using
3:59
git commits and files as memory between
4:01
these iterations and when the context
4:03
window fills up a fresh agent picks up
4:05
where the last one left off and you just
4:07
wipe the previous context window and
4:09
keep going against that task. The
4:11
technique is embarrassingly simple for
4:13
an engineer. And while the AI industry
4:15
was building elaborate multi- aent
4:17
frameworks, all Jeffree did was discover
4:19
that you can just be really persistent.
4:21
You can repeat the goal. You can wipe
4:23
the context window and you're going to
4:25
get somewhere. A loop that keeps running
4:27
until tests pass is more reliable than
4:30
very carefully choreographed agent
4:33
handoffs. Venture Beat called it the
Ralph: The Bash Loop That Went Viral
4:35
biggest name in AI right now and they
4:37
weren't wrong. The pattern spread
4:39
because it enabled you to do much more
4:40
autonomous work for a long period of
4:42
time. The second viral piece was Gas
4:44
Town. It was released by Steve Yagi on
4:46
January 1st. While Ralph is minimalist,
4:49
Gast Town is unabashedly maximalist.
4:53
It's a completely insane workspace
4:55
manager that spawns and coordinates
4:58
dozens of AI agents working in parallel.
5:00
And honestly, Gas Town is something that
5:03
reflects Steve Yagi's brain more than it
5:06
reflects a coherent enterprise agentic
5:08
pattern. But but but it's still relevant
5:12
because both patterns share the same
5:14
core insight. The bottleneck has
5:16
shifted. You are now the manager of
5:19
however many agents you can keep track
5:21
of productively. Your productive
5:23
capacity is limited now only by your
5:26
attention span and your ability to scope
5:29
tasks well. And then things kept
5:31
changing because in late January,
5:32
Anthropic shipped Claude Code's new task
5:35
system. And suddenly even Ralph looked
5:38
like a clever workaround to a problem
5:40
that now has native infrastructure. You
5:42
don't have to get Ralph anymore. CJ
5:43
Hess, a developer who stress tests new
5:45
AI tooling, was in the middle of a large
5:47
author factor when Claude codes task
5:49
system. He pushed it to its limits,
5:51
right? He created a massive task list.
5:54
He had it orchestrate sub agents to
5:56
execute the entire thing. And he reports
5:58
that it completely nailed it. And that's
6:01
weird. We're used to things where agents
6:04
fumble, where they don't get it done.
6:06
And in this case, a simple task system
6:08
that just looks like a to-do list was
6:11
what it took to coordinate agents across
6:14
a complex multi-agent problem. Now, to
6:16
be fair, the task list that Anthropic
6:19
released is more than just a simple tick
6:21
box. Under the surface, each task can
6:24
spawn its own sub agent, and each sub
6:26
agent can get a fresh 200,000 token
Claude Code's Task System
6:29
context window that's completely
6:31
isolated from the main conversation. So
6:34
you can have a clean focused job for
6:37
that sub agent. Let's say agent one is
6:39
digging through authentication code and
6:40
agent two is refactoring database
6:42
queries and agent three is working
6:44
through tests. None of them are
6:46
polluting each other's context or
6:48
getting confused by what the others are
6:49
doing because they don't know each other
6:51
exists which is the same insight Yaggi
6:54
had in Gastone. The old approach was
6:56
Claude trying to hold everything in one
6:58
long threaded conversation, remembering
7:00
decisions from earlier while
7:01
implementing new things and it just got
7:04
complicated and Claude lost the plot.
7:06
That still works for small stuff, but
7:08
for stuff that's complex, context
7:10
management becomes the bottleneck and
7:12
stuff falls through the cracks. The task
7:14
system changes that architecture. Each
7:17
agent focuses on just one thing. When a
7:19
task completes, anything blocked by it
7:22
then automatically unblocks and the next
7:24
wave of agent just magically kicks off.
7:28
So you can have between seven and 10 sub
7:30
aents running simultaneously and the
7:32
system just picks the right model for
7:34
the job. Haiku for quick searches,
7:36
Sonnet for implementation, opus for
7:38
reasoning. All you do is define your
7:40
dependencies and the system handles all
7:42
of that orchestration for you. Look, the
7:44
key innovation here is the realization
7:46
that dependencies are structural.
7:49
They're not cognitive. Without them,
7:51
Claude has to hold the entire plan in
7:53
working memory. And the plan will
7:55
degrade the moment the context window
7:57
fills up. You end up reexplaining over
7:59
and over to the agent. This is what's
8:01
done. This is what's left. This is what
8:03
depends on what. But when you
8:05
externalize the dependencies, the graph
8:08
doesn't forget and doesn't drift. you
8:10
never need to reexplain to the agent
8:12
because it never got stored in memory to
8:15
begin with. It's just a task sheet. It's
8:17
going back to Ralph was a bash loop
8:19
workaround to this same problem. The
8:22
task system is Anthropic's answer. It's
8:24
a native platform infrastructure for the
8:26
same capability and it illustrates how
8:29
fast things are moving. Patterns can go
8:31
viral and just a couple of weeks later
8:33
they're obsolete because they've been
8:34
absorbed into the platform. Cursor is
8:37
carrying the flag for very large running
8:40
autonomous projects. I've talked about
8:42
their project to build a browser and how
8:44
it took 3 million lines of code. They've
8:47
written about it extensively, but
8:49
they're not done with the browser.
8:51
Cursor is running similar experiments
8:53
using AI agents to build a Windows
8:55
emulator. They're building an Excel
8:56
clone. They're building a Java language
8:58
server. These are big code bases. They
9:01
range from half a million to one and a
9:02
half million lines. They're all being
9:05
generated autonomously. Now, the point
9:07
here is not that cursor is immediately
9:10
going to start shipping Excel and
9:11
competing with Windows. The point is
9:13
that they are proving that autonomous AI
9:16
agents can build complex software. At
9:19
Davos in late January, Dario Amade
9:21
described what he called the most
9:22
important dynamic in AI today, the self
9:25
acceleration loop. And it's important
9:27
that we understand it. He said, I have
9:29
engineers at Anthropic who tell me, I
9:31
don't write code anymore. I let the
9:33
model write the code. Now, we've heard
9:35
that on Twitter a lot and the mechanism
9:38
is simple. But the fact that Anthropic
9:40
is doing it is really important to
9:42
understand because fundamentally they
9:45
are accelerating the production of the
9:47
next AI systems using AI. AI has entered
9:52
a self acceleration loop. This is also
9:55
why OpenAI is starting to slow hiring.
9:57
Just this past week, Altman announced
Cursor's Autonomous Megaprojects
9:59
that OpenAI plans to dramatically slow
10:01
down hiring. And he said he did it
10:04
because of the capabilities and the span
10:07
he sees from existing engineers. Now,
10:09
they're not stopping hiring altogether,
10:11
but one of the things he shared is that
10:13
the expectation he has for new hires is
10:16
now skyhigh because of what AI tooling
10:18
can give. He said literally they're
10:20
having new hires sit down if you're in
10:22
the interview loop. and he said, "We're
10:23
asking them to do something that would
10:25
normally take weeks using AI tools in 10
10:28
or 20 minutes." That's a reasonable
10:30
request. I've shared earlier how you can
10:32
use Claude in Excel to do weeks worth of
10:35
work in 10 to 15 minutes. This is the
10:38
reality of work in 2026. And what Sam is
10:41
choosing to do is responsible because as
10:43
he said, he doesn't want to have awkward
10:46
conversations and overhire. He would
10:48
rather hire the right people, keep them
10:50
around and expand their span with AI
10:53
tooling. The numbers behind this
10:55
decision come from OpenAI's own
10:57
benchmark GDP val. It measures how often
Dario Amodei's Self-Acceleration Loop
11:00
AI output is preferred over human expert
11:02
output on a well scope knowledge work.
11:05
And we see the tipping point hitting
11:07
around this same time that the last few
11:10
weeks of the year of 2025 because GPT
11:13
thinking tied or beat humans only 38% of
11:16
the time. That was the model in the
11:17
fall. GPT 5.2 Pro which was released
11:20
much more recently at the very end of
11:21
the year early this year reached 74%. It
11:24
doubled. So on three quarters of scope
11:27
knowledge tasks the AI is now preferred.
11:29
And that is you can read that as a
11:31
general pattern for cutting edge models.
11:33
Now it's not just chat GPT. And as Sam
11:35
put it, right, if you can assign your
11:37
co-workers something that takes an hour
11:39
and you get something that's better than
11:41
what a human would do 74% of the time
11:43
and it's taking vastly less time, it's
11:45
pretty extraordinary feeling. And this
11:47
brings us back to the paradox. If models
11:50
are beating human experts like this on
11:52
scope tasks and doing it faster, why
11:55
hasn't work transformed more? Why is the
11:58
CEO of OpenAI, Sam himself, still
12:00
running his workflow, as he says, in
12:02
much the same way? This is a capability
12:04
overhang because capability has jumped
12:08
way ahead and humans don't change that
12:10
fast. Adoption hasn't. Most knowledge
12:12
workers are still using AI at I would
12:15
say a chat GPT 3.5 chat GPT4 level. Ask
12:19
a question, get an answer, move on.
12:22
Summarize this document for me. Please
12:24
draft this email. They're not running AI
12:26
agent loops overnight. They're not
12:28
assigning hour-long tasks to their AI
The Capability Overhang
12:30
co-workers. They're not managing fleets
12:33
of parallel workers across their
12:35
backlog. The overhang explains why the
12:38
discourse feels so disconnected. Why it
12:40
feels like you have constant jet lag if
12:43
you are living at the edge of the
12:45
capability and you're going back to look
12:47
at how work looks today. Someone running
12:49
task loops in Anthropic or Ralph is
12:51
living in a different technical reality
12:54
than someone who queries chat GPT four
12:56
or five times a day even though they
12:57
have daily access to the exact same
13:00
underlying tools. One person is seeing
13:02
the acceleration, everything happening
13:04
all at once, the other is seeing
13:06
incremental improvement and wondering
13:08
why AI is such a big deal. This creates
13:10
a very temporary arbitrage. If you
13:12
figure out how to use these models
13:15
before your competitors do, if you can
13:17
get your teams to do that, you have a
13:20
massive edge. And if you're waiting for
13:22
AI to get smart enough before changing
13:24
the workflow, you are already behind and
13:26
you're showing that you're not using AI
13:29
well. So what does closing this overhang
13:31
that's developed especially in the last
13:33
few weeks look like? What are specific
13:35
skills that power users describe? Well,
13:38
a few patterns emerge. Number one, power
13:40
users that are really on the edge are
13:42
assigning tasks. They are not asking
13:44
questions. When you treat AI as an
13:46
oracle, you are in the wrong mental
13:49
model. The shift is very much toward
13:52
what I would call declarative spec.
13:54
Describe the end state you want. provide
13:57
the success criteria and let the system
14:00
figure out how to get there. This is
14:02
sort of a pro postprompting world. It's
14:05
still prompting, but it looks a lot more
14:07
like a specification. Number two, accept
14:10
imperfections and start to iterate.
14:12
Ralph works because it embraces failure.
14:15
The AI will produce broken code, so
14:17
we're just going to make it retry till
14:19
it fixes it. And it never gets tired and
14:22
it keeps retrying. And you go and make
14:24
coffee or lunch and you come back and
14:25
it's done. This requires abandoning the
14:28
expectation that AI should get things
14:29
right the first time. It often won't and
14:32
it doesn't matter because it doesn't get
14:33
tired. Third, invest in specification.
14:37
Invest in reviews. Invest less in
14:39
implementation. The work is shifting.
14:41
It's less time writing code. It's much
14:43
more time defining what you want. It's
14:45
much more time evaluating whether you
14:47
got there. This is a real big skill
Closing the Gap: What Power Users Do Differently
14:49
change. Most engineers have spent years
14:51
developing their intuitions around
14:53
implementation and those are now not
14:55
super useful. The new skill is
14:58
describing the system precisely enough
15:00
that AI can build it and then writing
15:02
tests that capture the real success
15:04
criteria and reviewing AI generated code
15:08
for subtle conceptual area and then
15:10
reviewing AI generated code for subtle
15:12
conceptual errors rather than simple
15:14
syntax mistakes. The errors get very
15:17
interesting here. Maggie Appleton is a
15:19
designer who's been analyzing these
15:20
tools for a bit. I think she puts it
15:22
really well. When agents write the code,
15:25
design becomes a bottleneck. And so the
15:28
questions that slow you down are less
15:30
and less about the details of code
15:32
syntax. They're more and more about
15:34
architecture, about user experience,
15:36
about composability. What should this
15:39
feel like? Do we have the right
15:41
abstraction here? These are the
15:43
decisions that agents cannot make for
15:45
you. and they require your context and
15:47
your taste and your vision. I will say
15:50
the speed is dangerous in and of itself.
15:52
Watch out for the foot gun. You can move
15:55
really really fast with AI agents and
15:57
you can forget how much trash you are
16:01
putting out there. To be honest, if you
16:02
are not thinking through what you want
16:05
done, the speed can lead you to very
16:08
quickly build a giant pile of code that
16:11
is not very useful. That is a superpower
16:13
that everyone has been handed for better
16:15
or worse and we are about to see who is
16:18
actually able to think well. Yes, it is
16:20
time to use multiple agents in parallel.
16:22
That's another lesson. It's it's
16:25
transformative because every single one
16:27
stacks your capability. Some developers
16:29
are going from a few PRs per day to
16:31
dozens. The constraint moves from coding
16:33
to coordination. How can you scope your
16:35
tasks? How can you review outputs? Etc.
16:38
Fundamentally, even if it's tricky and
16:40
you have to figure out what review looks
16:42
like in this new world, this is where
16:44
we're all going because of the
16:45
multiplicative effect of agents pointing
16:48
in the right direction that you're
16:49
thinking about where you're going. Just
16:51
stacking up on top of each other and
16:53
solving multiple tasks at once. And this
16:55
includes letting agents run all the
16:56
time. Ralph was designed for overnight
16:58
sessions. Define the work, start the
17:00
loop, and go to bed is a new engineer's
17:02
day. Now, of course, this only works
Design Becomes the Bottleneck
17:04
with proper guardrails, but when it
17:06
works, you're getting productive hours
17:07
around the clock from time that was
17:09
previously idle. And look, the last
17:11
thing from power users, which I think is
17:13
true, is you got to actually try it.
17:15
This sounds incredibly obvious, but it
17:18
is the main barrier. Most people haven't
17:20
run an agent loop for more than a couple
17:21
of minutes, and the models improved a
17:24
lot in December. If you have not
17:26
revisited your AI workflow since, you're
17:28
probably operating on stale assumptions
17:31
about what is actually possible. To be
17:33
honest with you, the shape of work
17:35
itself is changing. Andre noted
17:38
something really important about the
17:39
errors that current models make. They're
17:41
not these simple syntax errors. And he
17:44
thinks, and I think he's correct, that a
17:46
hasty junior developer would make very
17:49
similar conceptual errors to the quality
17:52
of errors the models are making now. And
17:53
that's a good thing. It means the models
17:55
are getting stronger and getting to the
17:56
level of a junior developer because
17:58
they're making wrong assumptions and
18:00
they're running without checking.
18:01
They're failing to surface trade-offs
18:03
sometimes. Those are things that junior
18:05
developers do. These are supervision
18:07
problems, not capability problems. And
18:10
the solution isn't to do the work
18:12
yourself. It's to get better at your
18:14
management skills. You do have to watch
18:16
the agents, but if you do, you can catch
18:19
the moments when you've implemented a
18:21
thousand lines to solve a problem that
18:23
could have taken a hundred. And this is
18:25
something where to be quite frank, our
18:27
technical teams need to level up. So
Running Multiple Agents in Parallel
18:29
they're able to do this kind of
18:31
management of agents and they're able to
18:34
write evals that test correctly. There
18:37
are evals you can write that test
18:39
whether the agent is writing a simple
18:42
enough solution for this problem. Those
18:44
are the kinds of eval we need to think
18:46
about, not just traditional functional
18:47
tests. This is what Sam means when he
18:50
talks about being an engineer changing
18:53
so quickly. You're not spending time
18:55
typing. You're not debugging. You're
18:57
spending most of your time, frankly, as
18:59
a manager. And yes, we should be honest,
19:02
the ability to code manually is going to
19:04
start to atrophy as a skill set because
19:06
you're just not using it as much.
19:08
Generation and discrimination are very
19:10
different skill sets, and you're using
19:11
those every day. This is not a failure
19:14
and it's not something to be embarrassed
19:15
about. It's a reallocation of very
19:18
scarce human cognitive resources toward
19:20
a skill that has higher leverage. Now,
19:22
this obviously leads to a debate. How
19:24
close should developers stay to the
19:26
code? There are widely differing
19:28
opinions by senior developers here and I
19:31
would argue that I think the right
19:32
answer is a function of what you are
19:34
building. If your risk tolerance for a
19:37
mistake is very low, you are going to
19:40
have to watch the agent coding in an IDE
19:43
and write your eval super carefully if
19:45
you want to leave it alone. If you are
19:47
trying to write really good front-end
19:49
code, that is more complicated right now
19:51
than backend code because defining what
The Errors Models Make Now
19:53
something looks like remains a
19:55
challenge. But if you're willing to
19:58
experiment, if you're willing to
19:59
iterate, if it's a green field project
20:00
and it's a prototype, you really can
20:02
step back. And so I think what this
20:04
calls for is another level of
20:06
abstraction from engineering. We need to
20:09
think as technical leaders about where
20:12
engineers should stand in relation to
20:14
the code based on the risk profile of
20:18
that codebase itself. That becomes
20:20
something we can intentionally set as a
20:22
policy for teams. Hey, this is
20:23
production. This is not something we can
20:25
mess up. This is our expectation as
20:28
leadership for how you code with agents
20:30
against this codebase. That is something
20:32
we're going to have to start to do
20:34
because otherwise it's just going to be
20:36
a free-for-all and everyone will make
20:37
their own rules and you're going to get
20:39
all sorts of issues in production. So
20:40
where does all of this leave us? The
20:43
December convergence of models of
20:44
orchestration patterns of of tools like
20:46
Ralph established a new baseline. Models
20:49
can now maintain coherence for days.
20:52
Orchestration patterns do exist that
20:54
manage fleets of agents and the
20:56
economics absolutely work. This doesn't
20:58
mean you have to use Ralph specifically.
21:01
The point is that the problems these
21:04
tools wrestle with are fundamentally
21:06
different and point to a very rapid
21:09
change in how we work particularly in
21:11
technical domains. If you're wrestling
21:13
with context persistence and parallel
21:15
coordination and those problems suddenly
21:17
get an order of magnitude easier which
21:19
they did because of exactly what I've
21:22
described around how we handle tasks and
21:24
workflow and more capable models
21:26
designed to run long running work
21:29
patterns. Well, suddenly it's like the
21:32
ceiling lifts. Everything gets an order
21:34
of magnitude easier when you're building
21:36
big stuff. And the overhang that that
21:38
generates when this happens all at once
21:41
is real. If Amade is right and AI can
21:44
handle endtoend software engineering
21:46
tasks within 6 to 12 months, then the
21:49
gap between what we are doing today and
21:53
full automation has never felt larger.
21:57
If the overhang feels big after the last
22:00
few weeks, as you listen to what I'm
22:01
describing here, the overhang is only
22:03
going to get bigger because AI is
22:05
continuing to accelerate. Look at how
22:08
quickly Anthropic was able to turn
22:09
around and ship co-work just 10 days.
22:11
Look at how quickly they turned around
22:13
and shipped their version of Ralph that
22:15
was more natively integrated. Yes, the
22:17
people who are building this moment
22:19
sometimes aren't fully into it yet.
22:21
They're still moving their furniture
Setting Policy for Agent-Assisted Code
22:23
into the new AI way of working to use a
22:25
metaphor. Sam Alman admitted that about
22:26
himself. But the future is here now. And
22:30
if you can get through the overhang and
22:32
start to accelerate into a world where
22:35
you are asking the AI to do big tasks
22:38
for you, you're moving from prompting
22:40
with questions to defining
22:41
specifications. You're running multi-
22:44
aent patterns. This is going to
22:46
fundamentally change your day. If you
22:48
have not seen, on a personal note, if
22:50
you have not felt the power of having
22:53
five or six clawed code windows up on
22:55
your screen at once, it's it's hard to
22:57
get past it. Like there's nothing like
22:59
how fast you feel you can go. And the
23:02
future belongs to people who know how to
23:04
handle that speed responsibly and be
23:07
thoughtful with it. the overhang is
23:09
going to continue and the benefits to
23:11
those who can get over it are just going
23:13
to get greater and greater and greater
23:14
because these are exponential gains that
23:16
we're looking at. Every single agent you
23:18
can run in parallel multiplies your
23:20
productivity. And so this is the future
23:22
we're looking at. A future made not by
23:24
one model maker or not one breakthrough
23:27
but a collective phase transition where
23:30
model capabilities as a whole over the
23:32
last couple of weeks, five, six weeks
23:35
have moved us from a world where it was
23:37
kind of irrational to run a dozen agents
The Overhang Is Only Getting Bigger
23:40
to a world where if you're not running a
23:41
dozen agents doing autonomous tasks for
23:44
days at a time, you're behind and things
23:47
are only going to go faster from here.
23:49
Good luck. I have a full write up on
23:50
this on Substack. Let me know where you
23:53
have questions and we'll all get through
23:54
it
<!--end transcript-->

## Summary