# How OpenClaw works
## Transcript
Intro
0:00
OpenClaw isn't sentient. It doesn't
0:02
think. It doesn't reason. It's just
0:04
inputs, cues, and a loop. But you've
0:06
seen the videos. Agents calling their
0:08
owners at 3:00 a.m. Agents texting
0:11
people's wives and having full
0:12
conversations. Agents that browse
0:14
Twitter overnight and improve
0:15
themselves. A 100,000 GitHub stars in 3
0:18
days. Everyone's losing their minds. So,
0:21
why does it feel so alive? The answer is
0:23
simpler than you think. And once you
0:25
understand it, you can build your own.
The viral phenomenon
0:27
Let me show you what's got everyone
0:28
worked up. This guy's open claw agent
0:30
got itself a Toio phone number
0:31
overnight, connected to a voice API, and
0:34
called him at 3:00 a.m. without being
0:36
asked. This one set up his agent to text
0:38
his wife, "Good morning." 24 hours
0:41
later, they were having full
0:42
conversations, and he wasn't even
0:43
involved. Open Claw hit a 100,000 GitHub
0:46
stars in 3 days. That's one of the
0:48
fastest growing repositories in GitHub
0:50
history. Wired covered it. Forbes
0:52
covered it. In the reactions, people are
0:55
genuinely asking if this thing's
0:56
sentient. If we've crossed some kind of
0:58
threshold, if this is the beginning of
1:00
something we can't control. Here's the
1:02
thing. I get the excitement. And when I
1:05
first saw these demos, I had the same
1:07
reaction. But when I started asking how
1:09
it actually works, and the answer isn't
1:11
magic. It's elegant engineering.
1:13
First, let's get the basics out of the
What OpenClaw actually is
1:15
way. Open Claw is an open source AI
1:17
assistant created by Peter Steinberger,
1:19
the founder of PSP PDF kit. The
1:21
technical description is simple. Open
1:23
Claw is an agent runtime with a gateway
1:25
in front of it. That's it. A gateway
1:28
that routes inputs to agents. The agents
1:30
do the work. The gateway manages the
1:32
traffic. The gateway is the key to
1:35
understanding everything. It's a
1:36
longunning process that sits on your
1:38
machine, constantly accepting
1:39
connections. It connects to your
1:41
messaging apps, WhatsApp, Telegram,
1:44
Discord, iMessage, Slack, and it routes
1:47
messages to AI agents that can actually
1:49
do things on your computer. But here's
1:51
what most people miss. The gateway
1:53
doesn't think. It doesn't reason.
1:55
Doesn't decide anything interesting. All
1:57
it does is accept inputs and route them
1:59
to the right place. This is the part
2:02
that matters. Open Cloud treats many
2:04
different things as input, not just your
2:06
chat messages. Once you understand what
2:08
counts as an input, the whole alive
2:10
feeling starts to make more sense. There
2:12
are five types of input. When you
2:14
combine them, you get a system that
2:16
looks autonomous. But it's not. It's
The 5 input types
2:18
just reactive. Let me break them down.
2:21
Everything OpenCloud does starts with an
2:22
input. Messages from humans, heartbeats
2:25
from a timer, crown jobs on a schedule,
2:27
hooks from internal state changes, and
2:29
web hooks from external systems. There's
2:31
also one bonus. Agents can message other
2:34
agents. Let's step through each one.
2:37
Messages are the obvious one. You send a
2:39
text, whether it's WhatsApp, iMessage,
2:41
or Slack. The gateway receives it and
2:43
routes it to an agent, and then you get
2:44
a response. This is what most people
2:46
think of when they imagine AI
2:48
assistance. You talk, it responds.
2:50
Nothing revolutionary here. But here's a
2:52
nice detail. Sessions are per channel.
2:54
So, if you message on WhatsApp and then
2:56
also ping it on Slack, those are going
2:58
to be separate sessions with separate
3:00
contexts. But within one conversation,
3:02
if you fire off three requests while the
3:04
agent is still busy, they queue up and
3:06
process in order. No jumbled responses.
3:09
It just finishes one thought before
3:10
moving on to the next.
3:13
Now, here's where things get
3:14
interesting. There's heartbeats. The
3:16
heartbeat is just a timer. By default,
3:18
it fires every 30 minutes. When it
3:20
fires, the gateway schedules an agent
3:22
turn just like it would a chat message.
3:25
You can figure what it does. You write
3:27
the prompt. Think about what this means.
3:30
Every 30 minutes, the timer fires and
3:32
sends the agent a prompt. That prompt
3:33
might say, "Check my inbox for anything
3:35
urgent. Review my calendar. Look for
3:37
overdue tasks." The agent doesn't decide
3:39
on its own to check these things. It's
3:42
responding to instructions just like any
3:43
other message. It uses its tools, email
3:47
access, calendar access, whatever you've
3:49
connected, gathers the information, and
3:51
reports back. If nothing needs
3:53
attention, it responds with a special
3:55
token. Heartbeat, okay? And the system
3:57
suppresses it. You never see it, but if
3:59
something is urgent, you get a ping. You
4:02
can configure the interval, the prompt
4:04
it uses, and even the hours it's active.
4:06
But the core idea is simple. Time itself
4:09
becomes an input.
4:11
This is the secret sauce. This is why
4:13
Open Claw feels so proactive. The agent
4:15
keeps doing things even when you're not
4:17
talking to it. But it's not really
4:18
thinking. It's just responding to these
4:20
timer events that you've preconfigured.
4:22
Similarly, you configure crowns. These
4:24
give you more control than heartbeats.
4:26
Instead of a regular interval, you can
4:28
specify exactly when they fire and what
4:30
instructions to send. One example, at
4:32
9:00 a.m. every day, check my email and
4:34
flag anything urgent. Another, every
4:36
Monday at 3 p.m., review my calendar for
4:38
the week and remind me of conflicts. At
4:41
midnight, browse my Twitter feed and
4:42
save some interesting posts. Each crown
4:45
is scheduled event with its own prompt.
4:47
When the time hits, the event fires and
4:49
the prompt gets sent to the agent and
4:50
the agent executes. Remember the guy
4:53
whose agent started texting his wife? He
4:55
set up a crown job. Good morning at 8
4:57
a.m. Good night at 10 p.m. Random
4:59
check-ins during the day. The agent
5:00
wasn't deciding to text her. A crown
5:02
event fired. The agent processed it. The
5:05
action happened to be send a message.
5:07
Simple as that.
5:10
Hooks are for internal state changes.
5:12
The system itself triggers these events.
5:14
When a gateway fires up, it fires a
5:16
hook. When an agent begins a task,
5:18
there's another hook. When you issue a
5:20
command like stop, there's a hook. It's
5:23
very much event- driven development.
5:24
This is how Open Claw manages itself. It
5:27
can save memory on reset, run setup
5:29
instructions on startup, or modify
5:31
context before an agent runs. Finally,
5:34
there's web hooks. They've been around
5:35
for a long time. They allow external
5:37
systems to talk to one another. When an
5:39
email hits your inbox, a web hook might
5:41
fire, notifying Open Claw about it. A
5:43
Slack reaction comes in, another web
5:45
hook fires. A Jira ticket gets created,
5:47
another web hook. Open Claw can receive
5:49
web hooks from basically anything.
5:51
Slack, Discord, GitHub, they all have
5:53
web hooks. So now your agent doesn't
5:56
just respond to you, it responds to your
5:58
entire digital life. Email comes in,
6:01
agent processes it. Calendar event
6:03
approaches, agent reminds you. Jira
6:05
ticket assigned, agent can start
6:06
researching. There's also one more type
6:08
of input that's agents that can message
6:11
other agents. Open clause supports
6:13
multi- aent setups. You can have
6:15
separate agents with isolated workspaces
6:17
and you can enable them to pass messages
6:19
between each other. Each agent can have
6:21
different profiles. For example, you can
6:23
have one that's a research agent and
6:24
another that's a writing agent. When
6:26
agent A finishes its job, it can queue
6:28
up work for agent B. It can look like
6:30
collaboration, but again, it's just
6:31
messages entering cues. So, let's go
6:34
back to our most dramatic example. The
6:36
agent that called its owner at 3:00 a.m.
Deconstructing the "3am call"
6:38
From the outside, this looks like an
6:39
autonomous behavior. The agent decided
6:41
to get a phone number. It decided to
6:43
call. It waited until 3:00 a.m. But
6:46
here's what we know happened under the
6:48
hood. At some point, some event fired.
6:51
Maybe a crown, maybe a heartbeat. We
6:53
don't know the exact configuration. The
6:55
event entered the queue. The agent
6:56
processed it. Based on whatever
6:58
instructions it had and the available
7:00
tools it had, it acquired a Toyo phone
7:02
number and made the call. The owner
7:04
didn't ask for this in the moment, but
7:06
somewhere in the setup, the behavior was
7:07
enabled. Time produced an event. The
7:10
event kicked off the agent. The agent
7:12
followed its instructions. Nothing was
7:15
thinking overnight. Nothing was
7:16
deciding. Time produced an event. The
7:19
events kicked off an agent. The agent
7:21
followed its instructions. Put it all
7:24
together and here's what you get. Time
7:26
creates events through heartbeats and
7:27
crowns. Humans create events through
The formula revealed
7:29
messages. External systems create events
7:31
through web hooks. Internal state
7:33
changes create events through hooks. And
7:35
agents create events for other agents.
7:38
All of them enter a queue. The queue
7:40
gets processed. Agents execute. State
7:42
persists. And that's the key. Open cloud
7:45
storage's memory is local markdown
7:46
files. your preferences, your
7:48
conversation history, context from
7:49
previous sessions, so that when the
7:51
agent wakes up on a heartbeat, it
7:52
remembers what you talked about
7:53
yesterday. It's not learning in real
7:56
time. It's reading from files you could
7:58
open in a text editor and the loop just
8:00
continues from the outside. That looks
8:02
like sentience, a system that acts on
8:04
its own, that makes decisions, that
8:07
seems alive.
8:09
But really, it's inputs, cues, and a
8:11
loop.
8:12
Now, I'd be doing you a disservice if I
8:14
didn't mention the other side of this.
8:15
OpenClaw can do all of this because it
Security reality check
8:17
has deep access to your system. It can
8:19
run shell commands, read and write
8:21
files, execute scripts, and control your
8:23
browser. Cisco's security team analyzed
8:26
the OpenClaw ecosystem and found that
8:27
26% of the 31,000 available skills
8:30
contain at least one vulnerability. They
8:33
called it, and I quote, a security
8:34
nightmare. The risks are real. Prompt
8:38
injection through emails or documents.
8:39
Malicious skills in the marketplace.
8:41
Credential exposure. command
8:43
misinterpretation that deletes the files
8:45
you didn't even mean to. Open Claw's own
8:48
documentation says there's no perfectly
8:50
secure setup. I'm not saying not to use
8:53
it. I'm just saying you need to know
8:54
what you're deploying. This is powerful
8:56
precisely because it has access and
8:58
access cuts both ways. If you're going
9:01
to run this, run it on a secondary
9:02
machine using isolated accounts. Limit
9:04
the skills you enable. Monitor the logs.
9:07
If you want to try it out without giving
9:08
it full access to your machine, Railway
9:10
has a one-click deployment that runs in
9:12
an isolated container. Link in the
9:14
description.
9:15
So, what's the takeaway here? Open Claw
9:18
isn't magic. It's a well-designed system
9:20
with four components. Time that produces
9:22
events, events that trigger agents,
9:25
state that persists across interactions,
9:27
and a loop that keeps processing. You
9:29
can build this architecture yourself.
9:31
You don't need open clause specifically.
9:33
You need a way to schedule events, cue
9:35
them, and then process them with an LLM
9:37
and maintain state. This pattern is
9:39
going to show up everywhere. Every AI
9:41
agent framework that feels alive is
9:43
doing some version of this. Heartbeats,
9:46
crowns, web hooks, event loops.
9:48
Understanding this architecture means
9:50
you can evaluate these tools
9:51
intelligently. You can build your own
9:53
and you won't get caught up in the hype
9:55
when the next one goes viral. If you
9:57
want to go deeper on agent
9:59
architectures, I've linked the open claw
10:01
docs, clairvo's original thread that
10:03
inspired this breakdown, and the
10:04
security research in the description. If
10:06
you're building AI powered applications,
10:08
especially with Ruby on Rails, that's
10:10
what this channel's all about.
10:11
Subscribe, and I'll see you in the next
10:13
one.

