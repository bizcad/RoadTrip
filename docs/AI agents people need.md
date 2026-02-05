# AI agents people need

These are the 4 AI Agents Non-Technical People Actually Need (And How to Use Them Today)
<!--begin transcript-->
0:00
The AI industry has a big terminology
0:02
problem with agents. Everything's an
0:04
agent now. Chat bots, assistants,
0:06
co-pilots, automations. The word has
0:08
stretched so thin it means almost
0:10
nothing. So, let me give you a
0:12
definition that is really, really
0:14
simple, but actually holds up. An agent
0:17
is an AI that can do things, not just
0:20
talk. If you ask it a question and it
0:23
answers, then it's a chatbot. If you
0:25
assign it a task and it goes away, it
0:27
executes work. comes back with a
0:29
deliverable like a spreadsheet or a
0:31
document or a working application that
0:34
counts as an agent. That distinction
0:36
matters because it changes your
0:38
relationship with the AI. If you are not
0:41
having conversations and instead you're
0:43
delegating outcomes, you are working
0:46
with an agent. The technical
0:47
architecture behind this is simpler than
0:49
the industry probably wants you to
0:51
believe. Every agent consists of three
0:53
components. A language model that
0:55
reasons and makes decisions. tools that
0:57
let it take actions in the world,
0:59
browsing websites, editing files,
1:02
calling APIs, and guidance that
1:05
constrains what it should and should not
1:07
do. That's it. That's it. LLM plus tools
1:10
plus guidance equals agent. The magic is
1:12
not in any one of those pieces. It's in
1:15
the combination. The sum is greater than
1:17
the parts here. A language model without
1:19
tools can only talk. Tools without
1:22
language models require you to operate
1:24
them manually. guidance without both is
1:27
just a document nobody's going to read.
1:29
But if you combine all three and you get
1:30
something that can receive a goal,
1:32
figure out how to accomplish it and
1:34
execute the steps and report back the
1:37
results, now you have an agent. I want
1:39
to suggest a way of thinking about
1:41
agents that will make them much much
1:45
easier to understand if you're not a
1:46
technical person. I call it the little
1:48
guy theory and I think it corresponds to
1:50
how a lot of us think of agents anyway,
1:52
which is kind of handy. Every agent is a
1:54
little guy that you hire to do a
1:57
particular job. Little guy is not a
1:58
genius. Little guy is not a replacement
2:00
for human judgment, just a competent
2:03
helper with particular skills and
2:05
particular limitations. This framing
2:07
matters because it sets the right
2:08
expectations. You wouldn't want a new
2:11
hire to have your company credit card on
2:13
day one and say, "Figure it out." You'd
2:15
give them a very clear assignment. You'd
2:17
give them limited permissions. You check
2:19
their work before trusting them with
2:20
more. Agents work the same way. The
2:22
little guy framing also clarifies what
2:24
you're optimizing for. You're not trying
2:27
to build artificial general intelligence
2:29
in your notion workspace. You're trying
2:31
to get tasks done without doing them
2:33
yourself. That means reliability beats
2:36
capability every single time. I would
2:38
rather have an agent that correctly
2:41
researches 20 companies than one that
2:44
attempts to research 100 and
2:46
hallucinates half the data. I'd rather
2:48
have an automation that handles 80% of
2:50
cases perfectly than one that tries to
2:52
handle 100% and and fails unpredictably
2:55
so I have to manually check every single
2:57
one. The goal is not to be impressed by
2:59
what agents can do. The goal is not to
3:01
put AI agents on your website. I I know
3:03
that's a surprise to some of you. The
3:05
goal is to trust what the agent can
3:08
deliver so you can delegate outcomes.
3:11
One small note on agents and pricing. If
3:14
you are thinking about a hiring frame
3:16
for your little guy, it helps you to
3:18
understand pricing because in most cases
3:20
with these agents, you're paying by the
3:23
hour the way we would pay a little guy
3:25
to do work because these agents work by
3:28
the token. And so it's a very similar
3:29
mindset where like you're paying for the
3:31
tokens that this agent will use to do
3:34
the task just as you would pay someone
3:36
to help you to do a task by the hour.
3:38
And so you're hiring the agent for this
3:40
job. This also sets back the reliability
3:43
conversation right at the forefront of
3:44
your mind. Right? If you're hiring
3:46
someone to do the work, you expect them
3:48
to be reliable. You need to be able to
3:50
expect the agent to be reliable, too,
3:52
which is something that doesn't get
3:53
talked about enough. I think we spend a
3:55
lot more time talking about whisbang top
3:57
1% AI agent implementations and a lot
4:00
less about very basic AI implementations
4:03
that we can execute reliably that save
4:06
us a ton of time and make a real
4:08
difference. And that's what this video
4:09
is about. So this leads to what I call
4:11
the four knobs of agent reliability. The
4:14
first knob you can turn is the habitat.
4:16
Where does the agent operate? Where does
4:17
your little guy live? Some live on the
4:19
open web, browsing websites, extracting
4:22
information. Others are going to live
4:23
inside your workspace, right? They're
4:25
organizing and transforming content you
4:26
already have. Others build software.
4:29
Others connect applications and and move
4:31
data between them. Pick one habitat to
4:34
start. Mixing them together is totally
4:36
possible, but if you're just getting
4:38
started, it can also create a lot more
4:40
complexity than you need. Second thing,
4:42
agents need hands. What can the agent
4:44
touch for tools? Readonly access is
4:47
probably the safest. That means the
4:49
agent essentially has a pair of glasses
4:51
and eyes, and it can read stuff, but it
4:52
can't write. The ability to click
4:54
buttons and take actions is more
4:56
powerful, but it is riskier. The ability
4:59
to spend money or make irreversible
5:01
changes, I would keep it off until you
5:03
deeply trust the system. The third knob
5:05
that you can turn is what you would call
5:08
the constraints or the guidance or even
5:09
even the leash for the agent. How much
5:12
freedom does this agent have? A tightly
5:14
leashed agent follows explicit
5:16
step-by-step instructions every time. A
5:19
loosely leashed agent will get goals and
5:22
figure out their own approach.
5:24
Beginners, I would say if you're just
5:25
getting started, you want to define it
5:27
as carefully as you can so that you
5:29
avoid confusion and you avoid unhappy
5:31
outcomes for your agents. The fourth
5:33
knob is proof. Can the agent show it did
5:37
the job correctly? And so, can you
5:40
specify what good looks like, what an
5:42
outcome that's successful looks like
5:44
that an agent needs to demonstrate?
5:46
Things like providing source links or
5:48
screenshots or the logs of the work or
5:50
the before and after comparisons. If an
5:52
agent cannot show you its work, it's
5:54
really hard for you to verify its work,
5:56
which means it's hard for you to trust
5:57
its work. So, with that introduction to
6:00
agents, I want to give you what I would
6:02
say are the best four agents that kind
6:05
of fit this little guy mental model and
6:08
that will help you get started if you're
6:10
trying to get agents that do reliable
6:13
work. And these four agents cover most
6:16
of what a non-technical person needs to
6:18
accomplish. I've tested a lot. There are
6:20
a dime a dozen. These are the ones that
6:22
you can actually use. And I'm going to
6:24
tell you what they're good for. Manis is
6:26
your internet researcher. It lives in
6:28
the cloud. It spins up a browser you can
6:31
watch in real time. It can navigate
6:33
websites the way a human would. It
6:35
compiles findings into structured
6:37
deliverables. Think spreadsheets or
6:39
documents or slide decks. And the
6:41
experience, it can be a little eerie the
6:43
first time, right? You assign a task
6:45
like compare pricing and features for
6:47
these top 10 competitors. and you will
6:50
literally watch as it opens tabs, it
6:52
scrolls through pages, it copies data
6:54
into a table, it delivers a CSV 20
6:56
minutes later. You don't have to watch,
6:59
but you can. And there's some proof of
7:01
work there. What would have taken you 3
7:03
hours of clicking, copying, and pasting,
7:06
and building a deck happens while you do
7:08
other things. The free tier is going to
7:10
give you, I think, 300 credits daily
7:12
right now, which is enough to test it
7:14
out. But paid plans get more expensive.
7:16
They run from $19 to $199 a month
7:19
depending on how much complexity and how
7:22
much multiple little guys concurrency
7:24
that you need. The key to using
7:26
Maniswell is specificity. Tell it what
7:29
columns you want. Tell it what sources
7:31
are acceptable and what format you need
7:33
the output in. Vague instructions
7:35
produce vague results. That's kind of a
7:37
hint for most of LLM work. Actually, I
7:39
am not just recommending Mannis because
7:41
it's good for beginners. I am
7:43
recommending Manis because it is a very
7:45
powerful computer use agent for people
7:49
who want to get real work done and who
7:52
don't want to be in the code all the
7:54
time. So there are a lot of folks who
7:56
are in what I would call the
7:58
professional class who use Manis as
8:00
their secret weapon because Manis lets
8:03
them get this comprehensive deep
8:06
research stuff done in a way that they
8:09
could not get any other way. And this is
8:11
true even if you use something like Chad
8:14
GPT deep research because you might
8:16
think this is really an overlap with
8:17
Gemini deep research or Chad GPT deep
8:19
research. It turns out that Manis is
8:22
generally speaking more complete at the
8:25
kinds of deep research thinking and
8:27
organization tasks and it can output in
8:30
multiple formats which is handy. So, for
8:32
example, if you want to find a list of
8:34
emails to reach out to about a potential
8:36
fund raise and you need to reach
8:38
everybody in a Y combinator class or
8:41
everybody at a particular series of
8:43
funds, that is a complex task that would
8:45
take a junior associate several hours.
8:48
It takes Manis a few minutes and unlike
8:50
chat GPT deep research, it actually
8:52
finds them all. It actually gets the
8:54
whole job done and then it comes back
8:56
and then it can give you a spreadsheet.
8:58
It can even help to start to craft the
8:59
email, etc. And so people who want work
9:02
completely finished are often using
9:04
Manis. And I hear back when I recommend
9:07
Manis. This is expensive. And I come
9:09
back to that little agent hiring
9:10
paradigm. You're hiring this agent to do
9:13
reliable work just as you'd hire someone
9:15
to do reliable work. If you can get in a
9:17
few minutes of work all of the emails
9:19
you need for a major fund raise, it's
9:21
probably worth the money. And so think
9:23
about the value of the work you're
9:24
assigning the agent and budget
9:26
accordingly. Notion AI is another great
9:28
agent. Think of it as a workspace brain.
9:31
Unlike Manis, which goes out into the
9:33
world to find information, Notion AI
9:35
works with the content you already have.
9:37
And I will just not hide the ball here.
9:39
It works in notion. So if you are not in
9:42
Notion, this is not going to be as
9:43
useful for you. If you are in Notion, it
9:46
is tremendously useful. It works across
9:48
your notes, your databases, your meeting
9:50
transcripts, your project documentation.
9:53
The September 2025 update introduces
9:56
truly agentic work where you don't just
9:58
answer questions about your workspace,
10:00
but you execute multi-step tasks across
10:03
your workspace. You can update a uh
10:06
pipeline and sales estimate within
10:09
notion based on a meeting transcript
10:11
automatically. For example, you can
10:12
extract it to instruct it to extract
10:15
every action item from your meeting
10:17
notes and group them by owner and then
10:19
create a task database and and it will
10:21
just do that. The limitation is that
10:23
notion comes with the business or
10:25
enterprise plans because that's where
10:27
they think you're going to use it. So if
10:28
you're on the free plan or the plus plan
10:30
on notion, you're going to have to
10:32
upgrade to get access. If your knowledge
10:34
already lives in Notion, this is
10:35
probably the fastest way to organize
10:37
search and transform it. The key to
10:39
using Notion AI is essentially feeding
10:42
it all of your rich context. And that's
10:44
why it works best with a rich existing
10:47
database in Notion. Lovable is your app
10:50
builder. I've talked about it before.
10:51
You describe a piece of software in
10:53
plain English. I want a personal CRM,
10:55
right? I want to track my professional
10:57
network with a form for adding contacts
10:59
and a searchable card grid. I want to
11:01
make a travel website for my family.
11:03
Whatever it is, it generates a working
11:05
application. It generates front end now.
11:07
It generates backend. It generates a
11:09
database. It gives you a live URL. It
11:11
lets you iterate through the
11:12
conversation. It helps you set up
11:14
payments. This is not a toy. The
11:16
applications Lovable produces use real
11:18
code, usually React and Tailwind, and
11:21
you can export to GitHub and continue
11:23
developing yourself or even hand off to
11:25
a developer later. What used to require
11:27
hiring someone or learning to code
11:30
yourself now requires describing what
11:32
you want clearly enough to build
11:33
something simple. I have been using
11:35
Lovable since the beginning, and I have
11:37
seen it becomes easier to describe what
11:40
you want and get a reliable build. Paid
11:42
plans will increase your message limits.
11:44
Kind of like Manis, you hire what you
11:46
get, right? If you want an assistant to
11:48
build you a working web application,
11:50
it's vastly cheaper than a developer.
11:51
The key to using lovable well is
11:54
starting with a very clear mental
11:55
picture of what you want and describing
11:57
it precisely. The AI cannot read your
11:59
mind, but it's really good at
12:01
interpreting detailed instructions and
12:03
lovable keeps investing in features like
12:06
visual editing that help you to more
12:08
precisely realize your vision. So if
12:11
you're looking to build a small
12:12
application to start a business or a
12:14
small application to show what's
12:15
possible and demonstrate uh a proof of
12:18
concept, Lovable is great. The last
12:20
little agent that I want to call out is
12:22
Zapier. Zapier is your logistics
12:24
manager. It connects applications. It
12:26
automates workflows. When something
12:28
happens in app A, do something in app B.
12:31
When something happens in Salesforce,
12:32
please put this into Slack. Right? We've
12:35
had Zapier for a while. So why am I
12:37
bringing it up now? Well, Zapier has
12:40
added agents which add AI reasoning to
12:42
these traditional workflows. So instead
12:44
of rigid if then rules, agents can
12:46
analyze your incoming data, make
12:48
decisions based on context, and choose
12:51
appropriate actions dynamically. I would
12:53
recommend starting with basic Zaps until
12:56
you've built a few of them and
12:58
understand how this works. If you've
12:59
never used Zapier before, once you
13:01
understand how they work, then start to
13:03
add AI features where it makes sense.
13:06
There's no point in adding an AI
13:08
reasoning agent to a system that has
13:11
very simple if then rules and works
13:13
better without it. The key to using
13:14
Zapier well is starting with one
13:17
trigger, one action, getting that
13:18
working and adding the complexity of the
13:21
agent when you really need it. So, for
13:23
example, if you're trying to classify
13:25
your incoming leads, that might take
13:27
reasoning with a prompt from an agent.
13:29
Maybe it works better to have an agent
13:31
do that. But you might start by just
13:34
seeing if you can get your leads into a
13:35
spreadsheet and then you can add the
13:37
classification column later with an LLM
13:39
agent and see if that helps. That's an
13:41
example of how I would progress through.
13:43
So theory is like this is easy to talk
13:45
about, but but let's try some specific
13:48
examples here that you could actually do
13:51
with each of these agents so you can see
13:53
what I mean. Each of these does not take
13:55
very long and I'm just going to give
13:56
them to you briefly. They're designed
13:58
for this agent and I hope they give you
14:00
a sense of how easy and concrete it is
14:03
to go out and get work done with agents.
14:06
I don't want agents to feel
14:08
inaccessible. And so this entire video
14:10
is about making it easier to use them.
14:12
Try Manis. You can just open Manis and
14:15
say, "Compare these top five email
14:17
marketing tools for small creators in
14:19
2025. Please output a CSV with columns
14:22
for tool name, starting price, free plan
14:24
limits, one sentence best for
14:26
description, and a source URL. Please
14:28
visit the official pricing page. Please
14:30
do not guess prices. And then, by the
14:32
way, you can say, I don't know what the
14:34
top five tools are. Please research and
14:36
determine the top five tools. Then you
14:38
can just watch it work. When it delivers
14:40
a spreadsheet, you can open the source
14:42
links. You can verify that it got them
14:43
right. Basically, it gives you a small
14:45
research exercise that helps you to see
14:48
how Manis works. With Notion, find the
14:50
messiest page in your notion workspace.
14:52
Whatever it is that's a brain dump in
14:54
there or copied text from elsewhere.
14:56
Then ask Notion AI, "Please read this
14:58
page. Extract every action item into a
15:01
checkbox list. Group it by person
15:03
responsible. If no deadline is
15:05
specified, please mark it as TBD. If no
15:08
owner is clear, mark it as unassigned."
15:10
This sounds really boring, but one of
15:12
the most critical pieces that AI agents
15:15
can help us with is our own hygiene in
15:18
meetings as humans. Humans like to talk
15:20
in meetings and then we don't follow up
15:22
and then nothing changes. And so just
15:24
little things like this, making the AI a
15:27
passive always on feature is really
15:30
helpful. And so Notion AI lets us do
15:32
that. We can just define the action
15:34
items, label the owners, label the due
15:36
dates, and move on with our lives.
15:38
Lovable. Go to Lovable and just say,
15:40
"Hey, build me up my personal CRM app."
15:42
It needs a form to add a person with
15:44
fields for name, company, the last time
15:46
I met them, and any notes. Please
15:48
display people in a card grid. Add a
15:50
search bar at the top to filter by
15:51
company. Please use a modern clean
15:53
design. And uh right now, I don't need
15:55
authentication. You can add
15:56
authentication, by the way, but we're
15:57
just keeping it simple. Watch it build,
15:59
click the preview, play around with it.
16:01
You can even hit publish with it. You
16:03
don't need to code. You don't need to
16:05
hire someone. You just need to
16:06
articulate what you want. Lastly, with
16:08
Zapier, create a new Zap. Just say
16:10
schedule by Zapier set to every day at
16:13
9:00 a.m. The action is send yourself a
16:15
Slack message that says daily check
16:17
what's the one thing you must complete
16:18
today. Integrate it with Slack and see
16:21
if at 9:00 a.m. every day you get that
16:23
little message. The most reliable
16:25
workflows are just ones that are
16:27
deterministic. When X happens, do Y.
16:30
Now, this is not truly LLM powered yet,
16:33
but you can see how it could be, right?
16:35
You can see how you could then take read
16:38
my last days worth of work in Slack,
16:40
turn it into a digest, turn it around,
16:42
and give it to me at 9:00 a.m. Now,
16:44
that's an LLM job. And so, you can
16:46
easily add that complexity over the top
16:48
when you're ready. I want you to
16:49
understand the core loop here. You are
16:51
assigning work. You're verifying the
16:53
output. You're iterating on the
16:55
instructions. Everything else is
16:57
refinement. So, you can start with just
16:59
one agent. You can start with running a
17:01
couple of missions for your agent in
17:03
Manis or in notion until you develop an
17:05
intuition about what works. And then
17:07
once you have something reliable, make
17:09
sure you just do that use case well
17:12
before you add another one. So many
17:13
people try and say, "Let me do all of
17:15
the things. Let me be let me have a
17:18
Claude code instance and let me set up
17:21
all of my files so Claude Code can grab
17:23
them and work with them." I love that.
17:26
I've done whole videos on cloud code.
17:28
It's an amazing tool. But the people who
17:30
thrive with AI agents don't have to have
17:32
technical backgrounds. It's just being
17:34
able to articulate what done looks like
17:36
to be able to understand where you have
17:38
unclear instructions so you can clarify
17:41
them for the agent. I will be happy to
17:43
do a follow-up on non-technical use for
17:46
technical tools. I think that's a whole
17:48
separate video, but for today, let's
17:50
just focus on our team of little guys
17:52
that handle work that used to eat our
17:54
days. I think if we can get that far,
17:56
that is already a huge win. The future
17:59
is not learning to code. It's learning
18:02
to delegate and having enough technical
18:05
understanding of what those agents are
18:07
doing using LLM and tools and guidance
18:10
that you can troubleshoot. There you go.
18:12
I think you have everything you need to
18:13
set up your little guy and do your first
18:16
agent mission. Cheers.
<!--end transcript-->
## Summary
