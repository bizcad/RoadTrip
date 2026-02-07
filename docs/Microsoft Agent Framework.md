# Using Github copilot CLI and SDK for .Net dev
## Transcript
<!--begin Transcript-->
Countdown
2:25
Hello and welcome to the .NET AI community standup. Um, I'm John
2:30
Galloway. I am your guest host today because Bruno is in Boston.
2:37
Yes. Oh my god, you make me feel so bad. That's how you are supposed to start the show. I always start to do talking
2:43
something about hey this is amazing and more introduce yourself and no thanks everyone and thanks Steve also to be
2:49
here. I'm really looking forward to learn more about this and I only going to be here for two minutes and then
2:55
switch to the chat because as you see not in the standard office I am in the middle of post on also supporting
3:00
another event. So thanks a lot also John for helping hosting this because the the
3:06
SDK is super cool man I am building so small and crappy application so much fun
3:11
I'm having with this and it's amazing I love it. All right. And we are both very
3:17
excited to be joined by Steve today to talk about the CLI and the SDK for .NET
3:23
developers. Hello. Awesome. Well, I have just a few
3:28
community links I'll share and then we'll turn it over to you. Um, so let me share my screen
3:35
and that is this one here. Okay. And
Community Links
3:40
add stage. There we go. All right. So we have uh last week we had a fun exciting
3:46
announcement. This was using the um the SDK with work IQ. Um so this is this is
3:53
a really neat example of connecting your um all your communications and all your
4:00
kind of business intelligence uh you know whether that's SharePoint or anything that goes on you can think of
4:06
like the Microsoft graph. So, this connects all that context as an MCP server and um you'll see some neat
4:13
examples. There's some demo videos um showing this and uh things like
4:19
generating an architecture diagram based on conversations which is which is mind-blowing. And then Burke has a
4:25
really cool uh video where he does where he um he talks about building a VS Code
4:31
extension that does some things like pull in uh upcoming meetings and documents and things that he's going to
4:38
need to review before those meetings. So this that's he I love his scenario because he's like I'm deep in this, you
4:44
know, I'm like I'm deep in my code. I'm coding away. All of a sudden no, I got a meeting coming up and it like inside of
4:51
VS Code has something popping up telling you about that. So, uh, information in here about how to get set up for that.
4:58
Um, and you'll see, uh, it's configured as an MCP server. I helped behind the
5:03
scenes on this post, so I got to, uh, do a little Easter egg in here and put make sure my name was featured at least once
5:10
in the post. So, so that is that thing. Um, another neat thing, we just had a
5:15
blog post go out this morning. This is from Jeremy. Um here he's talking about uh he's starting a series on the core
5:23
building blocks of .NET AI essentials. So he's starting here with MEAI and he's
5:29
going to be going through vector data agent framework and MCP. So this uh he's
5:35
he's done some other posts on this just kind of like stepping back and let's look at the fundamentals. A lot of the
5:40
time we get really kind of like uh you know we'll say hey here's a new release it adds all these great new features and
5:47
we've got some folks that are saying like hey step back a bit and just explain the bigger context and so that's
5:52
what this series does. So excited to see the rest of these as they go out. One
5:58
other just random grabag thing here. This was something that I just saw come by in a chat yesterday. It's a public
6:04
PR, so feel like I'm okay to share it. But this is um this is a neat thing. Uh adding into the agent framework exposing
6:11
an AI agent implementation of the GitHub copilot SDK. So it took me a little bit
6:16
to wrap my mind around this one here, but general idea is being able to um
6:22
treat the GitHub Copilot SDK as an agent, be able to include it in tasks
6:27
and workflows and all that kind of stuff. So this is just a merge PR. It'll go out at some point, but I just thought
6:33
that was a pretty neat thing. And um I'm done. [laughter]
6:40
So, Steve, I guess should we turn it over to you? Yeah. All right. Brilliant. Well, I am
6:45
very happy to be here and to chat to everybody about all this stuff. Um so,
On today's stream
6:51
we put the the to title down as using Copilot CLI and SDK for .NET
6:56
development. And uh we of course will talk about that but I also really want
7:02
to have a slightly broader conversation. So quite a lot of what I going to will show and talk about is not really going
7:08
to be net specific because it doesn't need to be like when you're doing agentic coding a lot of the time it
7:15
doesn't really make any difference what language you're using and sometimes you might not even know or care yourself.
7:22
Um, so you know, it's the the broader set of concepts that I think are perhaps a little bit more interesting right now.
7:27
And honestly, it feels like it's a big moment in the whole history of software that we're going through and I and I
7:34
want to like open up a slightly broader conversation with with this group and find out what people are feeling about
7:39
the whole thing um like and what techniques uh uh and tips people have got for for being successful as this new
7:46
world evolves. So, let me share my screen and we'll start talking through some of this stuff. And uh Bruno and
7:52
John, anytime you feel like it, by all means, just interject and um we will uh
7:58
we'll discuss whatever you want. So, I've got about half an hour or so of content to go through. Um but, you know,
8:05
we can adjust as we go. I'm trying to share my screen, but right now here we
8:10
go. Entire screen. As you're doing that, I'll just funny side story, but
8:16
there is really an interesting thing like you're saying at this moment where the actual language or code itself is a
8:23
bit of an artifact and I recently built um a single page app and I built it with React and Vit
8:30
and hosted on GitHub pages. I'm not I'm a net person. I barely like I feel very
8:36
uncomfortable building with those languages and it worked just fine using Copilot. It it was something that was
8:42
slightly smoother in this, you know, using it with um GitHub pages hosting
8:47
and I was like shocked at like, yeah, it all worked, you know, it was kind of fun. So, all right, let me pop you down
8:54
to the screen. All right. Okay. Right. So, let's think about the the broad picture of what's
Using the GitHub Copilot CLI and SDK for .NET development
8:59
going on in the industry and in fact what our industry even is like what do we do all day? All right. So, let's
9:05
think of ourselves as software developers. So um why did we get into
9:10
this in the first place? I imagine that just about everyone on the call has got some major things in common like we like
9:17
computers right it's very general point but we do probably most of us since we were kids and we like solving problems
9:25
using our brains we enjoy the entire experience of thinking carefully about
9:31
stuff coming up with solutions and designs and turning it into a real thing that delights people in the external
9:38
world um and you know it's a good lifestyle for us We get to hang around with our computers, drink coffee, chat
9:45
to other nerds, and you know, solve interesting problems. That's great.
9:50
We've all, you know, benefited a lot from that. I know I have. Um, but stuff
9:57
feels a bit like it's changing right now because up until this point, the we were able to do this because we had a unique
10:04
ability that other people didn't. We could create working code and other people could not. But that's not really
10:10
the case anymore because now humans are not the only things that can create
10:15
code, right? Machines can create code as well now. And so the the landscape around us is starting to change. So how
10:23
did this happen? Well, it all happened really in the last couple years and and I'm sure everyone here has seen it. So
AI-powered code editing
10:29
um a bunch of products showed up in the market in pretty quick succession. So uh
10:34
initially we had a wave of IDE and web- based coding system coding agents. So uh
10:40
cursor showed us how it was possible to add a bunch of AI powered uh coding uh
10:46
tools into an IDE. Pretty quickly after that VS Code added its agent mode. So VS
10:51
Code already had a a co-pilot feature but that was basically just AI autocomplete. Uh and then agent mode
10:58
came along to turn that into something that uh was able to tackle big problems and go through a multi-step process to
11:04
solve things for you. And we had uh GitHub Copilot on the web as well uh the
11:10
thing that's able to respond to your comments and create pull requests for you uh against your repo. And that's
11:16
changed the way that we were able to produce code for the first time. But then also a second wave came along and
Arrival of CLI multi-agent review
11:22
believe it or not this was only just from about six months ago. the the arrival of the CLIs. So we had Claude
11:28
code came along and created this new product category um of the the agent
11:34
experience inside a CLI which was pretty quickly followed by uh Gemini CLI and
11:39
Codeex CLI and GitHub Copilot. And these things have become incredibly popular.
11:46
Um they are popular perhaps because they give you such a sense of immediacy. They're not tied to a particular IDE or
11:53
particular concept of source control or whatever. They can run in any directory. You just pop them open, tell them what
11:59
they do, and they just start working. And they're really addictive. Like some people think of them as kind of like dopamine machines. You just give it a
12:05
thing to like tell solve a problem for me and like 5 seconds later, you've got some kind of progress on that. So people
12:11
uh are very very enthusiastically adopted these kinds of things. Okay. So,
12:18
I know that there's a mixture of different opinions that people have there uh about uh this kind of thing.
12:24
Some people on this call are going to be very much into all this stuff and using it all the time. Other people will be,
12:30
"Oh, I just haven't tried it yet." And some people probably think, "Oh, I actively dislike this this direction
12:36
that our industry is going in." Um, so I think that what would be useful for us
12:41
is to go through some of the experience of what it's like to do stuff with this and and get into what are the ways that
12:48
we can be successful um with it and what kind of questions does this bring up for
12:53
us about how we do our work and what kind of future of an industry we're creating for ourselves. Okay, so people
Impact on productivity
13:01
say that this gives them a phenomenal increase in productivity. Now I don't
13:06
know whether you believe them or not but I'm going to give you some stats from the team that I work on. So I uh about
13:14
three four months ago or something I got access to an early build of Copilot CLI
13:19
and I was so convinced by that that within a couple of hours I started
13:25
making inquiries about going to move and work on that team. And so that's what I
13:30
do now. Now I work on the co-pilot CLI team and um we've uh obviously very heavily adopted our
13:37
own products for our own work and this [laughter] is just some stats I pulled up this morning. So we've got a team of
13:42
about 7 to 10 people and we've shipped over 200 things just in the last week.
13:49
Now that level of progress is for me unheard of prior to this. Um, admittedly
13:55
some of those PRs are just like oneline tweaks or documentation changes or whatever, but I'd say realistically
14:01
we've shipped more than a hundred non-trivial things in the last week. Um,
14:06
so yeah, it's absolutely making uh a radical difference to us. And for anyone
14:12
who's not really tried it, I think it's it's worth giving this a go. um to get a quick experience of what that's like,
14:18
let's imagine that uh we're on the the copilot uh CLI team right now and we
Demo 1 - adding a feature
14:24
wanted to add a feature to the product. Like how easy or hard would it be for us to ship something? So let's say that we
14:31
want to have a way of knowing what models, what AI models you can use within Copilot CLI. And maybe we would
14:38
like there to be a command like copilot show models. Now there isn't any command like that right now. If you try and do
14:45
it, you're just going to get an error. So, let's see if we can implement that feature ourselves uh using copilot
14:52
obviously. So, we pop that open. We get the classic um coding agent CLI view and
14:58
then we give it some instruction. So, let's say uh add a show models command
15:05
to CLI that lists available models to process standard out. and we will let
15:13
that get going. So obviously it's not a very um complex instruction we've given
15:19
it. It's going to get working on exploring that. You'll see that initially it's decided to use a sub
15:25
agent here called explore. That's a feature that we've uh only just produced. So it's able to run background
15:31
tasks potentially in parallel. It's just doing one here at the moment. So it's got a specialized agent that knows how
15:37
to search the codebase and figure out what to do. Um that has just completed.
15:42
So, what's it going to do now? Um, it's looking through the rest of the code to figure out where to put stuff. Um, it's
15:48
decided that it needs to decide where to add the flag. Um, it's working out how
15:55
we register flags and it's continuing there. It's found an
16:02
example of something similar to that. uh it's decided where okay it's made an edit to the code already and now it
16:09
needs to add an actual implementation for that. So let's just wait for it to complete. All right it's decided it
16:16
wants to build the the CLI which it does. What's it going to do next? It's
16:22
going to test that it actually works. So it's running it itself to see what output comes. It's decided that the
16:29
output is correct and it's finished. So I've exited from there.
16:35
All right. So let's see what have we got. Let's do a get diff. We've now got All
16:42
right. So it's added this show models and it's added a handler for that. It's very very simple bit of code. Um but
16:48
let's see if it works. It does. All right. Cool. So you know 30
16:55
seconds we've added our feature. Now you might think okay but it's only like a sixline feature. Uh that's true. It's
17:01
obviously very trivial. The hard part is deciding where to add the six lines and knowing that you're following all the
17:06
existing patterns correctly, but I hope you give you a sense there of how it's
17:12
possible for each developer to ship like 10 features in a day. Um, obviously most
17:18
of them are going to be more sophisticated than this, but uh it definitely changes the experience of
17:23
producing code. Okay. So, this forces us to think differently
Prototyping
17:30
about how we produce software. Some of the rules that we've been working with
17:35
for our entire careers up until this point start to feel a little bit different. So, one of the big changes is
17:42
now it feels like you can produce any amount of code you want really quickly.
17:47
So, you don't have to be precious about I I implemented something therefore we have to ship it. We implement stuff all
17:54
the time and then don't ship it because you know we change our minds about stuff or we find a better way. When it comes
17:59
to prototyping, you don't have to dedicate three days to produce a prototype of most things. Now
18:06
you can do it in, you know, half an hour if you're just doing something at prototype quality. Um it it means that
18:12
we approach design in a different way. In the past, we would think, okay, before we invest a week's work into
18:17
something, we better have a series of meetings to make sure we've got consensus and have thought everything through. We don't really do that
18:23
anymore. We just implement it possibly multiple times in different ways to see
18:29
how it works out. And we learn by actually doing something. When you've actually got the feature implemented, you can then think, well, does it
18:36
actually work well? Does it fit in with the rest of the system? Do we have any weird problems that we didn't anticipate? and then we can just throw
18:43
it away if we do, you know. Do you mind if I jump in with a quick question?
18:48
A lot of folks know you as the inventor of Blazer and I'm curious with this context how you
18:55
would think about your the way that you prototyped and built that if you had had co-pilot these
19:02
sort of tools available back then. Yeah, I mean I guess it would have been
19:07
a lot faster and easier. I'm not saying all of software is faster and easier. We're going to get on to some of the
19:12
ways in which it's potentially even more difficult and and and new problems might
19:17
occur. This is not just going to be like pure sales pitch. I'll I'll point out up front. Um but I would say that for the
19:24
for this specifically [laughter] the task of building prototypes where you don't have to care if all the
19:29
details are really right then absolutely it would have been way way way faster.
19:35
Um, and probably a lot of details that we had to leave until we could spend a
19:42
lot of time solving, we could have just dealt with up front. Like, you know, it took us so long to get debugger support on web assembly. I maybe it would have
19:49
been there in the first week if you know we could just throw a coding agent at it. I don't know. Wow.
19:55
Cool. All right. And hey, sorry I am going to jump also here. By the way, this is amazing. This is the fastest and
20:01
most amazing demo that I've seen in two seconds of copilot CLI. So I love it. I need to drop. And the last sentence is I
20:08
going to check the the YouTube channel and comment there. You I love that you said that this is the classic Copilot
20:14
CLI and it's been alive for a couple of weeks, but it's already [laughter] the classic one. It's it's everything is
20:20
moving so fast that I really enjoy I really enjoy that having this is kind of cool to do this. So hey, once again,
20:27
thanks everyone. See you all online and see you next one. Awesome. All right. Cool. So, changes the way we start to
What becomes harder
20:34
think about things, but some things might get harder for us.
20:40
And we don't yet know what we don't know. Let's try and think through the ways in which this might actually cause
20:48
problems for us, might make our jobs not even what we want anymore to try and anticipate where things going and try
20:55
and direct stuff so that it is what we want and we can anticipate problems that might otherwise occur. So, we'll get to
21:01
some of that as we go through this talk. Now,
21:06
there are so many things going on with coding agents. is incredibly hard to keep track of all the different features
21:13
and capabilities and strategies and so on that are available for people uh using them. So some of the features here
21:21
that we've list actually I'll come back to this in a minute. I'm going to give do a demo of sub aents right now but it
21:26
takes a few minutes to run. So I want to start that running and then we'll come back to it in a second. All right so let's just think about um a code review
Code review
21:34
scenario right that's a classic thing that we all have to do. So, if I could just get a browser up here. Um, so I I I
21:43
need to come up with something to code review. So, um, here's an interesting .NET project that I don't know if you've
21:49
all aware of. Um, it's an implementation of the Doom game engine innet. And, uh,
21:55
it's all open source. It's all written in C. It's pretty complicated codebase. Like, it's a large and complicated
22:01
thing. Here's a pull request that came in what, a few weeks ago. And if we go in there, we say, "Oh, it's going to be
22:07
quite easy to review, isn't it? It's only got two files changed." But then you see those two files that have been changed, and you think, "Oh my goodness,
22:15
who is going to review this? How am I going to make sense of all that stuff?" All right, what if there's a subtle bug
22:20
in all this math somewhere? Who's going to spot that? Um, all right. So, let's have a go at using Copilot to review
Demo 2 - code review
22:27
that. So, I'm in the um the game engine source code here, and I'm going to go
22:33
into Copilot, and I'm going to get it to do a review for me, but I'm going to do it in a special way that you might not
22:38
have seen done before. So, I'm going to say review the PR. I'll put the URL in,
22:44
but do it in parallel across Opus, Haiku, and Gemini. All right, so those
22:50
are three different um agent models that are available. Um, so Opus and Haiku are
22:57
both versions of Claude and Gemini is um, Google's model. So that is going to
23:02
start looking at that pull request. It's going to use the git commands to uh, to
23:07
get the details from GitHub. It's going to start uh, checking out the diff. It's doing an interesting technique here of
23:14
large output handling. So because we got a large block of data back from this pull request, 96 kilobytes, it's not
23:20
going to push all that into the context window because it would start to, you know, blow up the context window. So it saves it to disk and then it can read
23:26
different parts of that. And once it's got its bearings, it says now I'm going to launch parallel code reviews with
23:32
different models. And so it started up agents for Opus, Haiku, and uh Gemini 3
23:39
there. All right. Now, it might take a minute for them to go through. So while that does that, let's look at this again. Right. So if you've been around
Agents features overview
23:48
coding agents for more than a couple of weeks, you will know that things are changing very rapidly. Um these are a
23:54
bunch of features and as I look at this, probably about half or more than half of them have shipped in the last two weeks.
24:01
So like things are just moving so quickly, it's hard to keep track of. So sub aents are a way that um copilot or
24:09
other coding agents can start up subprocesses within themselves potentially with different context different models uh and check out the
24:16
results. Plan mode I'll do a demo of and that's a way of guiding a large piece of work up front. Skills are a way of
24:23
producing reusable um context that you can uh download and share uh and gain
24:30
the ability to do particular tasks. I'll do an example of that. Delegates a way that we can start some work locally and
24:35
send it up into the cloud to be continued if you don't want to use up your uh local resources to do it.
24:40
Memories keep track of context across different sessions and even across different developers on your team. So
24:46
when one developer teaches it something like this is how we like to write tests. Then that knowledge will be picked up
24:52
for other developers on your team. Uh hooks are a way of doing deterministic callbacks when the agent does a thing so
24:58
that you can invoke your own like helper code to like you know check that you're
25:04
happy with the tools that it's using or whatever. MCP I'm sure most people have heard of that. It's a way of plugging in
25:10
external tools. Uh infinite sessions are a way of never running out of context that we only just shipped about two
25:16
weeks ago. Um plugins are a way of fetching things like hooks and skills and so on. I'll demo that in a minute.
25:21
And this mention of git here is a realization that a lot of us have come to in the last few weeks that you don't
25:28
need to call run git yourself anymore. Like you never have to solve your own merge conflicts any now. You don't even
25:34
have to write your own PR descriptions. You can just tell an agent to do it and it will do that stuff. It's so liberating to not write PR descriptions
25:42
or deal with anything to do with git branching and merging and stuff. The agent just does it all.
25:48
All right. you're mentioning that there was a great comment on that earlier. Um, uh, let me see from KJ Betts saying
25:57
automating the agent using the the GitHub CLI and, um, I'm not sure if
26:03
that's intentional, but the there's the GitHub CLI and the GitHub copilot CLI. I've been using the GitHub CLI
26:08
automating and saying like use the GitHub CLI to create an issue or whatever, right? and like having that
26:15
abstraction like you're saying being able to say to talk not just to the git command line
26:21
but also the GitHub command line and just say like use the GitHub command line create this issue or whatever.
26:27
Yeah, absolutely. Yeah. Well, I spend all my time inside Copilot CLI. So, I would just say things like create a PR
26:33
from this. I don't tell it how to do that. I don't say you have to use the GH command or whatever. It it knows, you
26:39
know, it will figure that stuff out and do a good job of it. All right. So, our multi-agent review
26:45
has completed. So, we've got feedback from Claude Opus, from Haiku, and from Gemini. And they've all got slightly
26:50
different opinions. And this is a great way of dealing with things like the risk of hallucination. So, just because one
26:56
of them hallucinates doesn't mean the others will, and they'll effectively be checking each other. So, let's ask uh
27:02
how the uh results differ. So, I'm going to say, what were the main
27:07
disagreements? and we'll ask our council of AIS um you know what different
27:13
opinions they had about uh this particular massive pull request. Okay,
27:19
so it says um Opus identified a bug while Haiku
27:25
concluded the logic was correct. Opus was more rigorous. Gemini has an architectural concern, but whether or
27:31
not it's a real bug depends on stuff. Uh blah blah blah. Haiku was the most
27:36
lenient. Gemini was critical. Opus was in the middle. So that actually matters what I often see. So Gemini does tend to
27:43
be a bit fussier. It will point out a lot of issues, even ones that are debatable whether they're really issues.
27:49
Um Haiku is is the least smart of these three and Opus just tends to, you know,
27:54
focus on things that really are real. So uh it's a pretty nice way of being able
28:00
to combine uh the abilities across multiple agents. Okay, so that's an
28:06
example of using sub aents there. All right, but it's not just these things
Recent trends
28:11
that are being built into the uh CLIs and IDEs themselves. People are starting
28:18
to create their own workflows on top of it that become sort of higher level AI
28:24
capabilities. Um, and this is where it all starts to get really hard to keep track of. So, uh, in the last few weeks,
28:31
we've seen things come out like this. So, Gas Town, Steve Yaggi is a guy who's been well known in the in the software
28:37
industry for many years, and he's been exploring this way of creating this like fictional town of AI agents where you've
28:44
got a mayor and convoys that send beads to agents and, you know, they all collaborate to work together on your
28:51
projects. It's sort of wild and experimental, but you know, this sort of thing people are are getting interested
28:57
in. And another thing that you might well have heard of, this was incredibly hot about two weeks ago for maybe 3 days
29:03
was Ralph Wigum. U I'm sure many of you are thinking, what on earth is going on? Why are you talking about Ralph Wigum in
29:10
this context? Well, um so Jeffrey Huntley came up with this observation that AI agents tend to be pretty lazy,
29:17
right? You you give it a task like, you know, do these six things and it will do four of them and it will say, I've done
29:24
four of the six things. I'm finished. And you say what? do the other two. And it says, "Okay, sure, I will." And then
29:30
it will go, "The other two are quite hard. We'll leave those as a future task." And you say, "No, I want you to
29:36
do them now." And it says, "You're right. I will do them." And then it goes, "I've added some to-do comments to
29:41
say that we will do these in the future." And it's just ridiculous and annoying. So, the Ralph Wigan concept is
29:48
a way of forcing the agent to just never give up. It's literally just a while loop that keeps saying, "No, keep
29:54
working. No, keep working." and you you leave it running overnight and then you know hopefully it's done a massive
30:00
amount of work in the morning. Uh people say that they've done like big projects
30:05
like this like take an entire web browser and port it to Rust or something like that. Um kind of mad. Uh but
30:12
anyway, this is the sort of thing that people are come up coming up with. It's really interesting, but it's also
30:18
impossible to keep track of and you never know which of these things is really worth learning about. And it it
30:23
does create this quite difficult sense of pressure for us as developers that like how am I really going to keep up to
30:30
date on all this stuff? Um you know if it was hard enough to keep track of all the JavaScript frameworks, this is this
30:35
is on another level. So to minimize some
30:40
of the FOMO effect, let's do a bit of a step back and think about some of the the fundamentals and understand what's
30:48
really worth doing uh amongst all this stuff.
31:03
Sorry, one sec. Uh, John, can you still hear me?
31:09
I do. You do? Okay. Right. Sorry. Everything just went weird on my computer. All right. Let's trust that we're good and
Fundamentals of coding agents
31:15
we can keep going. All right. So let's think about some of the fundamentals if you want to be successful uh working
31:21
with coding agents. So here are some of the things that I think that we have observed are genuinely effective. These
31:29
are like the treasures amongst all the many many different um tools and techniques and it's basically the same
31:35
sort of things that are successful if you want to be successful as a human. Um, so most of the time that uh work
31:42
with AI agents fail, it's usually because the task you've given it is underspecified and AI agents are
31:48
unbelievably lazy. If there's any way they can avoid doing the work and just doing it in a rubbish cheap way instead,
31:54
they usually will. So planning is a a process that a lot of people go through in order to ensure they've really
32:00
specified what they want up front. and it became popular enough that it ended up becoming uh a native tool in many of
32:07
the AI uh CLI tools and it is in copilot CLI. So I'm going to show you an example
32:12
of that right now. So over here I've got another .NET project called Simple
Demo 3 - planning mode
32:17
Commerce and this is like the most classic mainstream uh business scenario
32:22
I can possibly think of. It's a classic e-commerce site. So this is totally
32:28
normal e-commerce with the only exception that the sample prices are utterly outrageous and for some reason
32:34
it just switches from language, you know, between different languages in the middle. Other than that, it's a completely normal e-commerce website.
32:41
Let's say I want to add some sophisticated feature to this. Here's how we can do it. Uh using the planning
32:48
feature that's just been shipped a couple of weeks ago. So let's go into co-pilot here.
32:54
Right. So you'll see that we've now got this shift tab to cycle mode that we've just added. And if I do a shift tab,
33:01
then I am going to switch into planning mode. Right? So I'm in plan mode now. And that means that when I give it some
33:07
instruction like uh add a product customization feature. Normally it would
33:15
just go ahead and start writing some code. But because I'm in plan mode, it knows I just want to work through the
33:21
process of designing this. So, it's going to start thinking about that. It's going to work out what might be meant by
33:27
this. It's doing an exploration of the codebase and it's decided to ask me a
33:33
question. What type of product customization do you have in mind? Uh, we got various options. I can type in a
33:38
custom answer if I want, but I'm going to go with build your own product. So, it thinks a bit more. And is it okay,
33:46
it's asking me another question. What's the use case? Let's go with the custom PC builder. And what does it do now?
33:54
It's going to think a bit more. Uh, should we enforce compatibility? Uh, how
34:00
about no more questions, please? All right. So, uh, it's going to now
34:06
start working on a plan. And it's going to do that as a markdown document that we're going to be able to read and edit.
34:12
And that's also going to be a way of tracking progress as we go through it.
34:18
So, it's uh, creating this plan for us. It's uh thinking through exactly how to
34:23
do it. All right. So, it's created a plan and um it's writing up the details
34:29
for us. And you'll notice we've got this control Y to uh viewedit the plan. I've
34:34
sort of done something weird there. All right. So, we will do a control Y. And
34:39
that's opened a uh code instance over here. All right.
34:45
So, we can see the plan that it's written. It's this build your own product feature. uh it's got all this kind of information. It's got the work
34:51
phases. It's got an example of the uh impact on the files, the database schema
34:57
and so on. And if we were really doing a feature of this size, we would probably want to spend like a good hour iterating
35:03
on this design with the agent to refine it into something that we're really confident is going to produce the
35:09
outcome we want. One thing I often want to do is tell it that I want to know how
35:14
to validate the work as it goes because otherwise it just does a bunch of code changes and I don't know whether it's
35:19
right or not. So, I'll go back over here. As you're doing that, I just want to that has been such a like a tip that
35:26
I've learned from people and I'm glad that it's becoming part of the standard workflow is that plan, review the plan.
35:34
And that's really the time where I'm most involved really is making sure that the plan is what I want, right? Because
35:41
I'll see people complain that, hey, I told AI to build a website and it built it wrong. It's like,
35:48
well, if you just say build a website, you didn't, you know what I mean? But if you really give that, if you take your
35:54
time with the plan and think about that, then you're kind of working a level up.
35:59
So, I just want to if people are kind of like not getting how important that is. I
36:05
think that's a really important step there that you're showing. 100% agreed. All right. So, so this is
36:10
one thing I often do is I tell it that I want to know how to validate the work. So you can see it started adding all
36:15
these validation entries at different points. Now some of them I I I would
36:21
probably go back to it and say no I want to be able to validate each thing in the UI somehow organize your work so that I
36:27
can always see like something that the user would be able to see. Anyway, once you've refined that a bunch you then
36:33
tell it to start working and it's going to update the plan as it goes. It will mark things off as done as they're done
36:39
and this allows you to really retain context over a long block of work. So just to to show that um and this is
36:45
going to be a bit fake, but I'll tell it um for testing mark all of phase one as
36:52
done. So it's going to think about that for a second and then hopefully phase one is going to get marked as done just
36:58
to show you that it can do that. It's kind of obvious. There we go. So it's marked those all as done and it would do that while it's in the middle of its
37:04
work. All right. So that's an an example of planning and we'll come back to do a
37:10
bit more with that application in a minute. Um, so, uh, let's talk about
Composition
37:15
some of these other fundamental abilities. And we're going to get into skills and feedback here. So, what you
37:24
don't want to waste your time doing with these systems is reinventing everything from scratch every time you tell it what
37:29
to do. You want it to know how to be effective within the context of your application and with the technologies
37:35
that you already use uh, with readymade capabilities and scripts and helpers and things like that. And that's something
37:41
that skills can allow you to do. Let me give you an example of skills. This is another relatively new feature that's
37:48
just shipped in the last couple of weeks. So, I'm going to come over here
Demo 4 - skills
37:53
and I'm going to start on that. So, I'm going to go and show you how you can install uh skills first. If I list the
38:01
skills that are available, you'll see I've just got this one skill right now. That's from a demo that we're going to get to in a minute. So, just ignore that
38:07
for now. Pretend it's not there. and I'm going to install some ready-made skills that someone else has provided. So, I'm
38:13
going to go to plug-in marketplace and list what marketplaces I've got. Marketplaces are basically just git
38:19
repos. So, this one is one that Anthropics has provided. And if I go over to that repo, you'll see what
38:25
they've put in there. So, Anthropic has provided this nice set of sample skills
38:30
for us. And we can go in there and see them all. And we can go and see how they're all implemented. I'll show you a
38:37
bit of how they're implemented in a minute, but what a skill actually is, it's a bunch of files that provides
38:42
context for an agent. So, it's a file called skill.md that's got information about how to do stuff. And it's got a
38:49
bit of header text here, this description. And this is the important and interesting part. Uh, AI models have
38:55
got a limited amount of context. So, instead of dropping all of the skill cont uh information into context, it
39:01
only puts this header part for each of the skills. And that's just enough for the agent to discover the skills there
39:07
and decide when it wants to use it. And when it does, it can look up the full details. So you can have tens, hundreds,
39:13
or thousands of skills and it won't blow up the context window. It will look up individual bits of information as it
39:19
goes. Now, my understanding of that a little bit, I used to put tons of information in a copilot instructions
39:27
and I would include code snippets. I'd include all this information. But then the problem with that is that's part of
39:33
the context. It's going back and forth in every request. Okay, so with this you're just saying
39:39
here's how to generate a PDF if you need it later. Go read the rest of it and that's and then it's able to
39:46
just put that metadata in the context. Exactly. And it's not just markdown context. It can be actual helpers like
39:52
scripts and so on that it can invoke. I'll show you that in a sec. So let's um register the um the skills from this
40:00
marketplace. So, I'm going to install something called document skills there. And once I've done that, if I go back to
40:05
my list of skills, you can see I've got now got all these things that you just saw inside my web browser. And these
40:11
[laughter] persist across sessions. So, if I uh create a new session and then have a look at my skills now, you'll see
40:18
that I've still got all this stuff here. So, let's have a go at using that. I'll say use the Slack GIF creator skill to
40:26
make me a GIF about installing Copilot CLI. All right. So, it's going to think
40:32
and that is going to use this skill from here, the Slack GIF creator and this
40:39
contains some utilities like these Python scripts here that it can use in order to build the and so you see it's
40:46
reading them so it knows how to use them. It's now making sure it's installed whatever dependencies are needed and then it's going to be able to
40:53
use that to create me a GIF hopefully. Okay, so it's created a little script
41:00
that it now invokes and it's checking the output. Let's just
41:06
quit that. Yeah. All right. So, let's see what it's just
41:13
created right now. All right. So we check our timestamps.
41:18
So this was created literally just now. Copilot CLI.GIF. And if we want to view that, let's bring
41:24
that into our browser. And nothing. Oh, it's a zero byte file. Oh
41:31
no, something's gone wrong. Okay. I don't know what happened there. All right.
41:36
If the [laughter] if the um skill had worked correctly, it would have created a file for us that would have worked.
41:42
You can see it tried, but there's obviously something wrong with maybe it was a tracking gif where it's one pixel by one pixel. [laughter]
41:48
Well, it's zero kilobytes, so I think nothing in there. All right. Anyway, you get the idea that that's how to install
41:54
and use a skill. But the more interesting bit is creating your own skills. So, let's say that we want to
41:59
create a skill ourselves right now. So, let's go back in here and we'll have a
42:05
look at how to do that. So firstly I've just got all those skills from before but now I want to use a skill called the
42:11
skill creator skill to create a skill. Um and I'll tell it where to put it. It
42:17
should ask user which project uh we'll do net spet core or github copilot
42:24
copilot cli no copilot SDK and we'll get build status for that. All right so that
42:31
is going to discover that it's got a skill creator skill. Hopefully it does.
42:37
And it's going to read in the details of how to create skills and then it's going to get started on
42:45
that. Hopefully. All right. So, it's initializing the
42:50
skill. Now, let's have a look at the code that it's producing as it does it. So, it's just created this skill. Oh,
42:56
it's an empty file. Oops. Something's not going wrong again.
43:01
What's going on? The file is empty. Yes. Oh, okay. Fine.
43:06
It's done it now. Right. So, it's populated the this skill and you can see that it's got this description and it's
43:13
doing what I said about how things should work. And we can read that and we can edit it ourselves if we want to
43:18
change how that works. For example, let's say I want it to only fetch build status from the main branch. I could
43:24
edit it myself or I can just go back and say actually only get status from main
43:33
and it edits it. Has it finished editing? Oh, it's done it now. Right. So, you can see it's just
43:40
added this thing here. U workflow runs filter branch main. All right. So, we've now got our skill.
43:47
All right. So, let's go out of there and finally uh we can try and use it. So
43:53
let's see if we check what our list of skills are. You can see we've now got our build status skill and this has
43:59
stored in source control in our project in this particular case. So we can share it with other people on the team and
44:05
also it's now available as a slash command. So you can get to it very quickly with autocomp completion. So I
44:11
ask for build status and it's going to think it's going to realize that there's a skill that it needs to load into
44:18
context and it's choosing to ask the user just like I said which project do you want it for? Uh let's do it for uh
44:25
copilot SDK and it's now going to follow the instructions that are in that skill.
44:32
Oh it's doing the large output handling again. And so that explicitly invoking is sorry to
44:40
interrupt. That's great that you can explicitly invoke it. I've I've noticed with MCPs
44:48
they'll have tools but you don't ever really I mean you don't really directly call a tool.
44:54
You can kind of hint but but here you're actually able to with the slash command say invoke this skill.
45:00
Yeah. In some cases some things that support MTP do let you invoke them directly. VS Code has a slash command
45:06
equivalent for MCP. Um, but yeah, I would say it's very useful either way,
45:11
whether it's a skill or MCP or whatever. If you know that's what you want it to do, then why why type it out when you
45:17
can just get autocomp completion on the slash. Yeah. Makes stuff easier for you. So, just FYI, we've got a few good
45:23
comment or questions in here that I want to take, but I don't want to interrupt where you're at in the flow. So, if now's good, I'll take them or later's
45:30
fine, too. All right, let's just finish the uh this stuff about uh skills and then we'll get to the questions.
45:37
All right, so we've been looking at composition skills and specialized tools, but the other
Feedback loop
45:43
piece of this is the feedback loop. So the another main antiattern that coding
45:49
agents get into is you tell them to do something and they say, "I've done it." And you ch try it and it doesn't work
45:54
and you say it doesn't work and it says, "Oh, I'm sorry. I'll fix it. I've fixed it now." And you try it and it still doesn't work. and it says, "Oh, I'm
46:00
sorry. I'll fix it." And you try it and it still doesn't work. And it's incredibly annoying. It's kind of like how other people feel
46:08
if they ask you to fix a bug in software, but they don't specify it very well, and you do some change, and then
46:14
the bug is still there. They're going to think that you're not very smart for not fixing the bug properly, but it's really their fault for underspecifying or for
46:21
not being able to, you know, show you what the bug really was. Same problem happens with coding agents. If they
46:28
can't actually run your application, they have a really hard time knowing whether the change they've made is right. So, anything you can do to give
46:35
it feedback will enable it to be more successful. Allow it to invoke a compiler, llinters, tests, whatever. But
46:41
even more than that, the ability to actually run your application. This is something we can achieve through skills
46:47
as well. So, I'm going to have a go at doing that for um back for this simple
Demo 5 - feedback loop
46:55
commerce application as well. Uh I've already created a skill actually over here called simple commerce automation
47:00
which teaches it how to in automate the browser using playrite and all about how
47:06
to operate this particular web application. Now obviously I didn't write this myself. I got it out of the skill creator wizard. Um I took me about
47:14
half an hour or something to keep iterating until it had capabilities. It knows how to log in as an admin. It
47:19
knows how to set up the site. It knows how to um you know populate things. It
47:26
knows how to start the browser in the first place. It knows how to discover what links are on a page and things like
47:31
that. So using this skill I can do something like the following.
47:40
Right. So let's just check firstly it's loaded our skill and it has. You can see that up there. So that being the case, I
47:47
can run it and let's just say start browser. So it'll think it'll load the skill into
47:55
context and hopefully it should know how to start a browser now. So it runs uh
48:01
one of the scripts that are in there and you can see a browser pops up for us. Okay, cool. Now this browser is one that
48:07
it can automate. So I could go back to it and give it some instruction like uh
48:13
I would like you to register a new user Steve. Okay. So it thinks about how to
48:20
do that. It checks its instructions in the skill there and then it should hopefully be able to load that
48:27
capability in. And so it's using the automate. There we go. It's done it. It was a bit fast but you can see it says
48:33
hello Steve up there now. It's successfully registered the user. Now, the point of this is not for you to give
48:39
it instructions manually. The point is that if you were getting it to work on a feature, it can decide for itself to pop
48:45
open a browser and literally try it out itself. And if it doesn't work, it can then see what the problem was and go
48:50
back and fix it. So, for example, if we were working on something to do with order management, we might say, um, as
48:58
admin, create a new product. Um, let's say super headphones.
49:06
uh then place five orders for it as Steve. Actually, five separate orders.
49:15
All right. So, it's going to think about that. That's quite a complicated process for it to go through. Um but hopefully
49:20
using this skill, it's going to be able to do all of that. So, it's generated a
49:26
script. What's it doing now? It's logged in as an admin. It's is it going to create a product for us? Oh, it's yes,
49:33
it's rapidly created the Super Headphones product. Now, it's logged in as Steve and it's placing a series of
49:39
orders for it and it can observe what's going on. You know, it can use the
49:44
Chrome DevTools protocol to read the contents of what's in the browser. Um, if for some reason the order placement
49:51
fails, like there was a validation error, whatever, it would be able to see that. It would be able to go back to its
49:56
code and start fixing whatever it was doing. So, does that make sense? this idea of wiring up um a feedback loop.
50:06
Yeah, that's really cool. I I love that whole like you're showing the cutting out the repetitive nature of like
50:13
specify work, test it manually, all that to be able to just say like you go automate doing all of that. So, that's
50:20
great. Awesome. Wow. Right. Um you wanted to ask any
50:28
questions? Yeah. Okay. We've got a bunch here. Let me see. Okay. Uh I'll go through some
Q&A
50:34
quick ones. Um so is the CLI built with Spectre console?
50:39
No, the CLI is implemented as a node application with React Inc.
50:46
Okay. Uh can we get unlimited requests
50:51
if you have unlimited money? Yes. [laughter] Okay, great. Um let me see. Uh so this
50:58
goes back to we were talking about uh GitHub automating the GitHub CLI etc. Um and
51:05
just kind of mentioning here like uh Azure DevOps. One thing that I've used for this there's an Azure DevOps MCP
51:12
server um that's been pretty useful. So just sharing. Cool. Um see uh how do you prompt it to create
51:21
the plan for review without having it dive in and start making the changes already? So basically
51:28
what plan mode is sorry go ahead. Oh sorry yeah I was speaking over you. Uh yeah that's literally what plan mode
51:34
is. Plan mode is a is a mode that when you are in it the agent is instructed not to dive in and start implementing
51:41
stuff but only to work with you on the plan document. Then you come back out of that mode when you want it to start making other code changes.
51:48
Great. Okay. Uh does plan mode remove the need for tools like spec kit?
51:54
Um, plum mode is in a sense a very light equivalent to spec kit. If you are using
52:00
spec kit and you're enjoying it and you find that workflow to be what you want, there's no reason you should stop doing
52:05
so. Uh, but I think that most people on my team at least are feel that they're
52:12
they're doing good work using plan mode. So, it's up to you.
52:18
Okay. A great comment from Winterfred just uh likes to keep the plans inside
52:24
the repo. So then you you tell it create them in a specific folder. Nice to be able to kind of have that as an
52:30
artifact. Yeah, that's another good workflow. A lot of people do that. We don't do that by default because
52:37
often these plan documents are quite ephemeral like that. It's just I want to work out how to make you do half an hour
52:43
of work successfully. It doesn't mean that it's long-term documentation for the project, but in some cases it might be or it
52:50
might be that you go through a bunch of planning in using the ephemeral document and then at the end of it you say to it
52:55
something like add dev docs based on this and then you know it will go and
53:00
look at that and work out what the the long-term information is that you want to store in source control and actually
53:05
writes that up as a nice document. Um you can do it whatever way you want. I I like that. That's something I've
53:11
kind of evolved into exactly is I'll say explicitly do not create you know
53:17
temporary markdown documents and then at the end of a work cycle say update the
53:22
you know official document on here's how we do things or cool um are using claude opus 45 for a
53:30
specific reason it's a bit expensive for the pro plan um opus just produces amazingly good
53:37
results um I would say if you can use it, it's great. Sauna is
53:44
very good as well though. Like I'm using it because it's a luxury that we have access to um on our team. But uh I think
53:53
there would be nothing stopping us from being very productive with Sonnet as well. Uh so I know some tools I I for I don't
54:00
know if CLI has this but there's like an auto mode um where it does auto selection. Does CLI have that?
54:07
So by that you mean never ask me any questions? Never prompt just No, sorry. Um, model selection.
54:13
Oh, got it. Yeah. Um, well, in a sense we do because the we pick a default
54:19
model for you every time you start a session. Um, but I don't think there's explicitly a model called auto. Um, no, there isn't.
54:28
But yeah, if if there's a reason for it, please give us a feature request. That's uh something I've been like I've
54:34
noticed in um like in the SWE on on GitHub. Yeah. or just kind of generally is just
54:40
use the auto model and then it'll only bump up to like Opus when it needs that,
54:45
you know, advanced thinking. Um, do you always invoke skills explicitly? I think you showed no, but I
54:52
just want Yeah, you don't have to invoke them explicitly. It's supposed to make its own decisions about when to run them.
54:59
But if I'm doing a demo of a skill, I might as well just like or if I literally know that it's going to be a
55:04
specific skill and I know there's a slash command for it, then it's fewer keystrokes for me to for use it than not
55:12
or have it accidentally guess the wrong thing and, you know, pick the wrong skill, that sort of thing.
55:18
Uh, do slash commands allow reference prompts? I'm using spec kit and I'm unable to see prompts the same way I'm
55:25
able to reference skills. Uh I don't think in copilot CLI we've got a concept of predefined prompts like
55:32
that. If it's something you find useful again please send us a feature request and you know we can ship features like
55:38
that incredibly quickly. Uh here's kind of a bigger question. I think you kind of talked generally about
55:44
this but just to kind of get it out there uh what is the difference between skills and MCP?
55:51
Uh yeah, so MCP is the effectively a protocol for communicating with some
55:56
external process. Um whereas skills is just a bunch of context.
56:03
Okay, that they're just different technically. Like MCP is useful if you um if you have
56:09
some external service that you must interact with, whereas uh skills is
56:14
useful if what you're trying to get it to do can be reduced to a bunch of
56:20
information and Python scripts and so on. Okay. Um let me see. Will an agent
56:28
implicitly invoke skills if it thinks it would be useful? I think you basically covered this, but just Yep.
56:34
Um, okay. And then this is just kind of a general idea here. Sirly Dev, longtime
56:40
viewer here, um, says, uh, because of software policies, they've been using C-pilot to build a couple of utilities
56:47
here. They're talking about basically wrapping things like SP who um and then the next comment they said they're going
56:53
to be wanting to use um you know create the skill for doing this with um copilot
57:00
copilot CLI as well. Cool. I think that's about all the um let me
57:07
see well all right well I know we've coming up to almost an hour and I still got another
57:12
cool thing I want to show so forwards a little bit. But I want I'm going to spend less time talking about uh you
57:20
know conceptual stuff and more about uh let's let's talk about one other very
GitHub Copilot SDK intro
57:26
interesting bit of tech that's coming out at the moment. So um Copilot CLI or
57:33
C-Pilot on the web coding agent whatever you want or other coding agents you know they're they all very helpful they give
57:39
you very um useful powers as a developer when it comes to writing code. So that's
57:45
brilliant for you, but it's also something that you can use to bring
57:51
additional powers into the products that you make available to your customers as
57:56
well. And to enable that, we have very recently shipped the copilot coding
58:02
agent SDK. And that allows you to use our agent and all of its prompts and
58:09
tools and skills and so on within your application to accomplish all this stuff. So let me give you an example of
58:15
doing that. So let's get back to u this thing of um
58:22
managing our own workflows. Let's say I want to make a a little tool called issue sizer and it's going to be
Demo 6 - GitHub Copilot SDK
58:30
something that estimates the difficulty of implementing particular issues that
58:36
have been filed against my repo. And I'm going to do that using the GitHub
58:41
copilot SDK. So, I've installed the current pre-release version of that and
58:48
then I'm going to be able to use it from my .NET code. Now, from this slide, you can see we've got SDKs currently for
58:53
Node, Python, Net, and Go. Those are the official SDKs. There's also community provided SDKs for Java, Rust, and C++.
59:00
I'm sure that list will keep growing over time. Now, obviously, I'm going to use the .NET one right now. And to do
59:07
this, it's pretty easy. I can start by instantiating a copilot client here. And
59:13
this is going to use whatever instance of copilot is installed on my machine right now. We don't have a way of
59:19
bundling it yet, but we are looking at doing that. And then I'm going to create a session against that and I can then
59:25
use that to do stuff like I can say list the files in this directory. I don't
59:31
have to tell it how to do that because it is the coding agent. It's got all the tools that the coding agent has. Obviously, it knows how to find files on
59:38
disk. So, if I run this now, then hopefully we'll see that produce some
59:43
useful output. If a terminal window appears, here it does.
59:50
Okay. Now, this might take a moment the first time that it has to run. It always does the first time I run it. Um, that's
59:56
going to be going through the all of the flows that the coding agent would do to look at the files on disk and decide how
1:00:02
to respond to you. And we'll get a little bit more insights into how it works in a minute once it's finished
1:00:08
responding. There we go. So you can see that that was running in the context of the build output directory. And so it's
1:00:14
telling us about all the DLS and stuff that it managed to find in there. All right. But it took a while and we didn't
1:00:19
get any obvious feedback on the screen. So to get a bit more information, we can subscribe to events. So we've got
1:00:26
session.on and then we'll get events back. And there are about 20 different types of events. They've all got nice
1:00:31
strongly typed .NET classes to represent them. For now, I'm just going to look at tool executions and then everything
1:00:37
else. And I'm just going to log all this stuff to the console when it happens. So if I run that again now, then instead of
1:00:43
showing us no output while it works, we're going to start to see this stream of events that are taking place. Uh we
1:00:51
can see that it's reporting its intent of listing directory contents. It's using a tool to look at the files on
1:00:57
disk and then eventually it comes back with its response to us. All right, cool. So that's some of the basics. Uh
1:01:04
so you can use that if you want to automate the CLI like you can send messages in, you can receive messages
1:01:11
back and automate things. But you can also plug in your own capabilities uh in
1:01:16
uh an even better way by just providing functions that it can call. So here I am
1:01:22
going to use a normal C# function to create uh this function here called get
1:01:28
issue size label that will take in a number of days work and then it uses this absolutely outrageous syntax. What
1:01:34
on earth is that? To uh return different strings depending on what that value is
1:01:40
and I can plug that into my session up here. So here I'm going to say uh I'm
1:01:46
going to use the Microsoft extensions AI helpers here to turn that uh net method
1:01:52
into an AI function that our copilot agent is going to be able to call. So to prove that it actually does, let's put a
1:01:59
break point there. And we better change our prompt to make it use that. What's the label for an issue that takes six
1:02:05
days? I'll run that with the debugger. And hopefully it will start up. It will
1:02:11
start the session. and it will start thinking about how to satisfy the users's requests and it will decide
1:02:17
presumably to call that net method. There we go. It's done it and it's
1:02:23
passed in six days work. We're going to return size m from that and it's going to say the the issue is size m. All
1:02:31
right. Cool. So that's all very well. But the more important thing here is
1:02:36
that we can now chain this together with all the other capabilities that built into the coding agent by default. So for
1:02:43
example, I could implement a whole thing that's going to uh produce uh estimates
1:02:50
of how long it takes to implement stuff. So now I've given it this prompt saying you're a software engineer. Check if the
1:02:55
issue corresponds to source code in this directory. investigate the existing code and provide an accurate estimate of the
1:03:02
size uh respond in this particular format. All right, so let's run that.
1:03:07
See if it works. Going to need to have an issue to uh estimate the size of.
1:03:14
So let's go and find something. It's the wrong one.
1:03:20
Where's my other browser? Here it is. Right. So I'm going to go
1:03:26
into copilot SDK which is open source and let's find some issue that we can
1:03:31
estimate the difficulty of. Let's have
1:03:36
connect to active CLI session. That's going to be a difficult one. So
1:03:42
I'll paste that in. Paste. There we go. All right. And you can see that it's
1:03:48
going to start using all of its agent smarts to decide uh how to get information about that. It's going to do
1:03:54
a web fetch. It's going to be comparing that to the source code on disk which doesn't even match that repo. So it'll
1:04:00
give up on that pretty quickly. And then eventually hopefully it will call our tool to get the size label and it's
1:04:05
going to provide a nice response for us. Okay. So it's come up with size large implementing an interactive diff tool is
1:04:12
large and so on. Yeah, that's probably true. All right. Cool. All right. So overall point of this is that uh this is
1:04:19
a higher level way to interact with AI rather than just using something like a plain chat completion endpoint. You can
1:04:25
use the whole agentic loop that copilot comes with the same one that's used in the CLI and that's used on the web and
1:04:31
all of the built-in prompts that we've been carefully optimizing and benchmarking for months now. Uh and
1:04:37
bring that kind of smartness into your project. Cool. Um that's enough about that. Um,
1:04:45
yeah. Any other questions or things you want to bring up, John?
1:04:51
Yeah, there were a few. Um, let me see. There's tons of questions. I'm actually trying to pick the the top here. Um, is
1:04:58
there a tool that can price out plans? This was talking about, I think, you know, like the different models and
1:05:04
stuff. Uh, price out the plans of using Copilot. Is that
1:05:10
I think so. Yeah. I don't think we have something like that, but that would be a really interesting thing to do. On the
1:05:15
other hand, how would you even run it if you don't already have Copilot? Um maybe we should uh put that up on the
1:05:22
web somewhere. Yeah, it's an interesting idea. I don't think that we've got that. Ideally, our documentation would be
1:05:28
clear enough that you don't even need AI to tell you what the price is going to be. Um if it's not, please complain at
1:05:35
us and then we'll start poking people to do something about that. It does sound interesting though like taking metadata
1:05:41
about you know different things and saying like here's my planned document for this thing like give me some
1:05:46
estimates and like help me you know make that um that sounds like a skill or something.
1:05:51
Yeah. Um okay this is a question about um from
1:05:57
Danielle loves copilot and SDK wondering about agent framework. Yeah. Um what's the value prop between the
1:06:05
different things? Yeah. So we've got a little sort of stack of like higher and lower level
1:06:12
things now I suppose in net specifically. So the lowest level thing in net for this stuff would be the
1:06:18
Microsoft extensions AI libraries which give you raw access to the chat completion endpoints which is a pretty
1:06:25
thin layer on top of the the language models themselves. And the these have no opinions about what kind of tasks to do,
1:06:31
what tools should be available, what prompts should be available, what workflows it should follow or anything to do with that. It's got no opinions
1:06:37
about any of it. And if that's what you want, if you want to provide all that logic yourself, then going in directly
1:06:44
at the chat completion layer is the one for you. Higher level thing on top of that is agent framework. that defines
1:06:50
this notion of agents that are stateful, that you can have an ongoing conversation with, and that potentially
1:06:56
know how to interact with each other to distribute work among themselves, but it's still unopinionated about what kind
1:07:02
of work it is that they do. And a more high level thing on top of that would be
1:07:08
well it's not on top of it it's actually separately implemented but a more high level thing would be the copilot SDK
1:07:14
which is not just an agent but it's specifically the coding agent that we've optimized uh for solving realistic
1:07:22
largecale difficult professional software tasks and it's got all the tools needed to find files on disk look
1:07:28
stuff up on GitHub um you know be able to keep track of what permissions you've given to it the ability to uh start up
1:07:36
MCP servers and interact with skills and you know all the things that Copilot CLI
1:07:41
does um but oriented around uh coding scenarios you can actually remove all
1:07:47
the coding specific stuff from it if you want to when you create one of these sessions with um this stuff here in
1:07:55
addition to just passing tools into it you can also say excluded tools and then you can remove stuff that's coding agent
1:08:02
related if you want to you can also pass a system message
1:08:08
and I wonder if I remember that content equals
1:08:14
and then we could say uh mode equals modereplace.
1:08:21
Yeah. So the default mode for system messages append. So that would be adding additional system message content to all
1:08:27
the stuff that's default for copilot CLI. But if you change it to replace then it throws away all the built-in
1:08:34
prompts completely and uh you know now your instruction the are the only
1:08:39
instructions it would use. So it's up to you really whether you want to use that stuff or not. Would it be like at a
1:08:46
simple level would it be okay to say that the most natural fit for co-pilot
1:08:52
is as an agent more in the development role whereas agent framework I would think to use that more in integrating
1:09:00
into my application. Well while you could move you can do
1:09:05
anything with anything. It seems like more natural fit maybe. Now it depends how much stuff you
1:09:12
want to work out by yourself. So getting creating some some kind of agent from scratch is easy. You can do it in 10
1:09:20
minutes probably. But is it going to behave well? What's the difference between something that behaves well and
1:09:25
doesn't? Well, it's like world-class expertise in prompt engineering and
1:09:32
months of very expensive benchmarking. And that's what's gone into all of the stuff that we're shipping in Copilot
1:09:39
SDK. So if you want to make it up yourself, go for it. But if you want to
1:09:44
build on this incredibly wellproven um battle tested agent that knows how to
1:09:50
make good judgments about how much work to do about stuff and and how to pick between different tools and things like
1:09:55
that, then Copilot SDK is a great point starting point for that. And it's not
1:10:01
although out of the box it's oriented around software development tasks, it's not a big step to give it instructions
1:10:07
to do other things. Like if you want to make a something that's going to process all your emails and decide what like
1:10:13
important tasks to do or something like that, the coding agent is going to do a really good job of that pretty much out
1:10:19
of the box. Um, I don't know about the rest of the people on this call, but I know that I and all the other people on
1:10:25
my team use Copilot CLI to do a lot of things that are not coding related. Like, if I have to do anything on my
1:10:31
computer that's more than a few clicks, I would just tell C-Pilot CLI to do it. If I need to write some documentation,
1:10:37
I'm going to tell Copilot CLI to do it. If I have to, you know, process a lot of files of of any kind for any reason,
1:10:44
again, going to be using the CLI. Um, so yeah, it's a very flexible tool.
1:10:50
One more related question here and just Wifred saying if you're integrating aic
1:10:56
features into products and I guess what I'm thinking of if I'm shipping software or I'm putting software on a server
1:11:04
would I kind of think of that more as agent framework versus copilot CLI or
1:11:09
SDK for running on my machine locally to do a task for me.
1:11:15
Yeah, it could be. Yeah. So certainly at the moment with Copilot SDK, we're we're optimized the the thing around uh stuff
1:11:23
that just runs for you with your credentials on your machine. Uh it's definitely not oriented around running
1:11:29
on a server with you know shared credentials and uh you know sessions that span multiple users and things like
1:11:35
that. I think we will get to that point and probably very soon but right now we're not at that point. So um so
1:11:42
certainly at the moment you'd be better off with agent framework for that. Um but I would imagine that these things
1:11:48
are just going to co-evolve and it might be that they end up solving similar pro problems in certain cases and that's
1:11:55
fine. You know people will just pick uh what thing is a good match for whatever they're doing and if you're using our
1:12:02
stuff we're not we're not trying to push you to one or the other like whatever is good for you. Okay. Um, last question and kind of
1:12:09
along that line generally because we're talking to dev audience that I think is more used to Visual Studio or VS Code.
1:12:17
Yeah. Um, I like this from Alexander. What's the difference from CLI and Copilot in
1:12:22
VS or VS Code? So, I want to reframe this a bit more as a question to you're
1:12:28
talking to developers who are probably experienced with using Copilot in VS or
1:12:33
VS Code. Y and you've shown a ton of compelling stuff, but like kind of the takeaway to
1:12:39
hey, give this a shot, try it out. What how would you kind of wrap that up?
1:12:45
Yeah, that that is what I would say. So, I would say that my my call to action for everyone from this is is just to
1:12:50
give it a go and specifically to try doing something that you wouldn't normally do because then you'll get a sense of this like, oh my goodness, I
1:12:57
just did that. Like an example of uh of that for me in the last week was uh I
1:13:02
was using this screen recording software and it had a bug where it would just crash when I did a certain thing which
1:13:08
is kind of annoying. I I found it it's git repo and I was about to file an
1:13:13
issue with it because I wasn't like going to do anything about it myself. It was written in Rust and I don't even speak Rust. So I was about to file an
1:13:18
issue and I thought why file an issue? Let's just try doing this myself. I opened copilot CLI. I told it to clone I
1:13:25
didn't even clone the reper. I just said clone this repo. fix this bug and submit a pull request. And it literally did it
1:13:30
like in less than 10 minutes. It cloned the repo, it diagnosed the problem, it fixed it, it submitted a pull request with a nice write up and the next day
1:13:38
that change was actually merged into the project. And that for me was like a pretty amazingly empowering moment. I
1:13:44
can just do stuff like that now. And so, so that's my recommendation is try doing something that you wouldn't normally do.
1:13:50
Prototype a thing that you've been putting off for a while. implement a crazy feature in your software that you
1:13:55
wouldn't think that you've normally got time for, just give it a go and just see how quickly you're able to make progress
1:14:01
with that. If you want to do stuff inside VS or VS Code, that's absolutely fine. Um, but I think it's worth giving
1:14:08
a go to the CLI. It's weirdly addictive. I don't know what it is about the the
1:14:13
way that the UI works, the way that the agent is set up. Something about it just feels really successful. So give it a go
1:14:20
and um yeah see see how it goes for you. Last last thing, can you um show us okay
1:14:26
I'm convinced how do we actually get started? Where's the best place to go to kind of learn about installing and
Get started
1:14:33
setting up copilot CLI? Yeah. Yeah. So you can go to the this git repo github/copilot
1:14:41
CLI currently in public preview and that's where you'll find all the documentation and where you will find
1:14:47
the getting started steps. So you can see what platforms are supported. Uh you can see you can install it through
1:14:52
Winger if you want to. I think Scott Hansen just put it on the Windows Store as well. Um or on all platforms you can
1:14:59
install it through npm as well if you want to. So there's plenty of easy ways to get started with that and uh then
1:15:06
hopefully that will step you through all the process of authenticating and and getting going.
1:15:11
Awesome. Okay, this has been fascinating. Thanks for all the amazing demos. Uh um great. I'll
<!--end Transcript-->

## Web References
https://learn.microsoft.com/en-us/azure/developer/ai/how-to/switching-endpoints?tabs=openai&pivots=dotnet
https://github.com/scottaddie/AIDevDaysOpenAI
https://developer.microsoft.com/blog/bringing-work-context-to-your-code-in-github-copilot
https://devblogs.microsoft.com/dotnet/dotnet-ai-essentials-the-core-building-blocks-explained/?hide_banner=true
https://github.com/microsoft/agent-framework/pull/3395
https://github.com/anthropics/skills/tree/main/skills
https://agentskills.io/what-are-skills
https://github.com/github/copilot-sdk
https://github.com/github/copilot-cli
https://github.blog/news-insights/company-news/build-an-agent-into-any-app-with-the-github-copilot-sdk/
https://github.com/github/copilot-sdk/blob/main/docs/getting-started.md
Methodology bullet list:

*   **PLANNING**
    *   *Say what you want, track progress*

*   **COMPOSITION**
    *   *Skills and specialised tools*

*   **FEEDBACK LOOP**
    *   *Compilers, linters, tests, running your app*


## ✅ Extracted Text of Microsoft Agent Framework/ Aspire
### tech list
SUBAGENTS
PLAN MODE
SKILLS
DELEGATE
MEMORIES
HOOKS
MCP
INFINITE SESSIONS
PLUGINS
GIT WORKFLOW

## Prompt
Yes I would like that. create a markdown document with bullet points about how they map into AgentFramework and how they fit into my Aspire app architecture. A bullet point about how they would be used in the Copilot SDK and copilot cli would also be good. A high level look at how they could be used in improving my Aspire app would also be appreciated. 

## Response
Below is a concise, skimmable **Markdown document** that ties each concept from your image to **Microsoft Agent Framework**, how it can fit into your **.NET Aspire** architecture for your Blazor/Survey system, plus how it shows up in the **Copilot SDK** and **Copilot CLI**.

***

# Agent Capabilities → Agent Framework ↔ Aspire App Architecture ↔ Copilot SDK/CLI

> **Legend**  
> **AF** = Microsoft Agent Framework • **Aspire** = .NET Aspire app model/hosting • **Copilot** = GitHub Copilot SDK / Copilot CLI

***

## SUBAGENTS

*   **AF mapping** — Create *composed* or *hierarchical* agents and wire them with the built‑in orchestrators (sequential, concurrent, handoff, group chat). Parent agents can assign tasks to subagents with different tools/models. [\[github.com\]](https://github.com/microsoft/agent-framework), [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/)
*   **Aspire fit** — Host each subagent as its own service (e.g., `SurveyPlannerAgent`, `DataCleanserAgent`, `ExportAgent`). Use AppHost to declare services and service-to-service bindings; add OpenTelemetry for cross‑agent tracing. [\[github.com\]](https://github.com/dotnet/aspire), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — With the **Copilot SDK** integrated in Agent Framework, you can include a Copilot‑backed agent as one of the subagents, alongside Azure OpenAI or others, under the same `AIAgent` abstraction. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/github-copilot-agent)

***

## PLAN MODE

*   **AF mapping** — Use a *planner* (a manager agent) that breaks a goal into steps and routes work to subagents via the framework’s orchestration patterns (sometimes called “magnetic” or manager‑style orchestration in learning material). [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/)
*   **Aspire fit** — Run the planner as an `Agent.Orchestrator` service. Persist plan state to your existing SQL/Redis resources registered in AppHost so plans survive restarts. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Copilot SDK sessions provide multi‑turn state + tools; your *planner* can call Copilot as a provider when steps require coding/file ops/shell execution. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)

***

## SKILLS

*   **AF mapping** — Treat *skills* as reusable capabilities (instructions + scripts + resources) that agents can load on demand; the community “Agent Skills” format is commonly used with agents. [\[agentskills.io\]](https://agentskills.io/home), [\[github.com\]](https://github.com/microsoft/agent-skills)
*   **Aspire fit** — Store skills alongside each agent service (e.g., in `./.github/skills` or `/app/skills`) and mount them as volumes; manage versioning via your Git repos in the Aspire solution. [\[github.com\]](https://github.com/dotnet/aspire)
*   **Copilot** — Copilot SDK/CLI can discover repo‑checked skills and use them in sessions; you can seed your repo with skills from `microsoft/agent-skills` (Azure SDK, Foundry, MCP configs). [\[github.com\]](https://github.com/microsoft/agent-skills), [\[docs.github.com\]](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices)

***

## DELEGATE

*   **AF mapping** — Implement *handoff* orchestration where a manager agent delegates a subtask and monitors completion. Built‑in orchestrators support this style of agent‑to‑agent handoff. [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/)
*   **Aspire fit** — Surface delegation events as traces/metrics via OpenTelemetry; helpful for diagnosing when a planner hands off to, say, a *Validation* or *Compliance* agent. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Copilot CLI has a `/delegate` capability (remote PRs/changes) and the SDK’s agent loop can automate steps; combine with Agent Framework to route some tasks to a Copilot agent while others use different providers. [\[docs.github.com\]](https://docs.github.com/en/copilot/reference/cli-command-reference), [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)

***

## MEMORIES

*   **AF mapping** — Use the framework’s session and tool patterns with external memory stores (vector DBs, files, Cosmos, etc.). Samples/docs show RAG, provider‑agnostic memory, and session management. [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/)
*   **Aspire fit** — Add Redis/Cosmos resources in AppHost for short‑term (session) and long‑term (profile/survey knowledge) memory. Wire tracing to see memory hits across services. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Copilot SDK supports persisted sessions and file context; combine with MCP servers for knowledge access so Copilot sessions “remember” your repo and external knowledge. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/github-copilot-agent), [\[github.com\]](https://github.com/microsoft/mcp)

***

## HOOKS

*   **AF mapping** — Use *tool functions*, *middleware*, and *eventing* in the framework to intercept turns, validate JSON/function calls, or inject audit/logging policies. (Samples and user guide cover tools + workflow hooks.) [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/user-guide/overview)
*   **Aspire fit** — Centralize hooks as shared libraries referenced by each agent service; export telemetry to the Aspire dashboard via OpenTelemetry. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — In the Copilot SDK, register function tools (file ops, shell, URL fetch) and your own domain tools as “hooks” the agent can call during a run. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)

***

## MCP (Model Context Protocol)

*   **AF mapping** — Use MCP for standards‑based tool/data access across agents (and even across products). Microsoft ships official MCP servers (Azure, GitHub, etc.) that your agents can call. [\[github.com\]](https://github.com/microsoft/mcp)
*   **Aspire fit** — Run MCP servers as sidecar services in your Aspire solution (e.g., a “Survey Knowledge MCP” that exposes your question bank and data dictionaries). Wire via service discovery and secure with env‑scoped creds. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Copilot SDK/CLI natively integrate MCP; Copilot Studio also supports MCP for adding tools/actions to low‑code copilots. This lets your agent estate share the same tool plane. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/), [\[microsoft.com\]](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/introducing-model-context-protocol-mcp-in-copilot-studio-simplified-integration-with-ai-apps-and-agents/), [\[microsoft.com\]](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)

***

## INFINITE SESSIONS (Long‑running/Durable Agents)

*   **AF mapping** — Agent Framework includes durability patterns (pause/resume, long‑running threads) and Azure hosting guidance so agents can run over extended periods. [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/)
*   **Aspire fit** — Persist *agent thread state* in durable storage (SQL/Cosmos/Queues). Host long‑running orchestration services and observe health with Aspire’s diagnostics. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Use Copilot SDK sessions for long‑lived conversations; when coding tasks are offloaded to the Copilot *coding agent*, progress is visible in PR/session logs. [\[github.blog\]](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/github-copilot-agent)

***

## PLUGINS

*   **AF mapping** — Represent external capabilities as *tools/functions* or via MCP servers; you can mix providers (Azure OpenAI, GitHub Copilot, Anthropic) behind one agent API. [\[github.com\]](https://github.com/microsoft/agent-framework)
*   **Aspire fit** — Run plugin backends (e.g., a browser tool, a file search, or custom HTTP APIs) as Aspire services; configure connections in AppHost for consistent dev→prod deployments. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — Copilot CLI has a **plugin** system and marketplace; the **Copilot SDK** exposes tool orchestration so your own “plugins” become callable tools. [\[docs.github.com\]](https://docs.github.com/en/copilot/reference/cli-command-reference), [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)

***

## GIT WORKFLOW

*   **AF mapping** — Use the workflow orchestrators to propose changes (plan → implement → validate) and then call Git/MCP tools to open PRs or update markdown specs. Samples show end‑to‑end workflows. [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples)
*   **Aspire fit** — Add a `GitOpsService` (CLI container) in AppHost to standardize repo access (tokens, allowed commands). Surface PR events into your telemetry. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Copilot** — The **Copilot coding agent** turns GitHub issues into PRs in a secure, auditable loop; **Copilot CLI** provides `/diff`, `/delegate`, timeline logs, and background agents that work in Git worktrees. [\[github.blog\]](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/), [\[docs.github.com\]](https://docs.github.com/en/copilot/reference/cli-command-reference), [\[code.visua...studio.com\]](https://code.visualstudio.com/docs/copilot/agents/background-agents)

***

# How This Improves Your Aspire‑Hosted Survey App (High‑Level)

*   **Faster feature delivery with a Planner + Subagents**  
    Add a `SurveyPlannerAgent` to break work (e.g., “add Likert variant to tab 4” or “migrate Topic→SurveyQuestion map”) into steps and delegate to subagents: data migration, UI component scaffolding, test generation. Orchestrators make this composition first‑class. [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/), [\[github.com\]](https://github.com/microsoft/agent-framework)
*   **Deterministic testing of agent outputs**  
    Keep using **Detester** in your CI to assert that agent responses and tool calls meet expectations (JSON shape, function params), guarding against regressions in prompts/tools. (You already found the repo; it complements AF quite well.) [\[github.com\]](https://github.com/sa-es-ir/detester)
*   **Enterprise‑grade tool plane via MCP**  
    Expose your *survey schema dictionary*, *role matrix*, and *question templates* as an MCP server. Both AF agents and Copilot (SDK/CLI/Studio) can consume the same tools/data, reducing duplication. [\[github.com\]](https://github.com/microsoft/mcp), [\[microsoft.com\]](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/introducing-model-context-protocol-mcp-in-copilot-studio-simplified-integration-with-ai-apps-and-agents/)
*   **Durable sessions for long surveys and offline work**  
    Agents keep state across tabs/sessions (“infinite sessions”) and resume after outages. Backed by Aspire‑declared storage + queues, you get resilience and observability out‑of‑the‑box. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/), [\[microsoft.github.io\]](https://microsoft.github.io/ai-agents-for-beginners/14-microsoft-agent-framework/)
*   **Git‑native changes and reviews**  
    Let the **Copilot coding agent** handle low‑risk refactors or scaffolding via PRs while you review. Use CLI `/diff` and background sessions so agent changes don’t collide with your active workspace (VS Code worktrees). [\[github.blog\]](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/), [\[docs.github.com\]](https://docs.github.com/en/copilot/reference/cli-command-reference), [\[code.visua...studio.com\]](https://code.visualstudio.com/docs/copilot/agents/background-agents)
*   **Unified telemetry**  
    Stream AF traces (planning, tool calls, handoffs) into Aspire’s OpenTelemetry pipelines and dashboard, so you can answer “which agent decided what, and why?” in production. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
*   **Provider flexibility**  
    Because AF abstracts providers, you can mix **Copilot SDK** for code/file/shell tasks with Azure OpenAI for language tasks without changing your orchestration code. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)

***

# Concrete Starting Point (Nick‑optimized)

1.  **Add Agent Framework to your Aspire solution**
    *   Create services: `Planner`, `SurveyBuilderAgent`, `DataMigrationAgent`, `ValidationAgent`, `GitOpsAgent`.
    *   Wire storage (Redis/SQL/Cosmos) + tracing in AppHost. [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/)
2.  **Integrate Copilot SDK through AF**
    *   Add `Microsoft.Agents.AI.GitHub.Copilot` to the repo; start a Copilot agent for code/shell/file tasks (scaffolding Blazor pages, EF migrations, doc updates). [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/)
3.  **Publish an MCP server for Survey Knowledge**
    *   Implement endpoints for “GetQuestionTemplate(id)”, “ListValidations(type)”, “MapLegacyTopic(row)”. Host it as an Aspire service; point AF and Copilot to it. [\[github.com\]](https://github.com/microsoft/mcp)
4.  **Adopt Skills**
    *   Pull targeted skills from `microsoft/agent-skills` (e.g., GitHub issue/PR skills, azd deploy) and keep them repo‑scoped for your agents/Copilot. [\[github.com\]](https://github.com/microsoft/agent-skills)
5.  **Operationalize**
    *   Add OpenTelemetry exporters; set CI to run Detester checks and basic AF workflow tests on PRs; enable Copilot coding agent for “issue→PR” on tagged tasks. [\[github.com\]](https://github.com/sa-es-ir/detester), [\[github.blog\]](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/)

***

## References

*   **Microsoft Agent Framework** – repo & docs, orchestrators, samples. [\[github.com\]](https://github.com/microsoft/agent-framework), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/), [\[github.com\]](https://github.com/microsoft/Agent-Framework-Samples)
*   **Copilot SDK integration with Agent Framework** – official dev blog; Learn page for GitHub Copilot Agents in AF. [\[devblogs.m...rosoft.com\]](https://devblogs.microsoft.com/semantic-kernel/build-ai-agents-with-github-copilot-sdk-and-microsoft-agent-framework/), [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/github-copilot-agent)
*   **MCP (Model Context Protocol)** – Microsoft MCP servers repo; Copilot Studio blog (preview→GA). [\[github.com\]](https://github.com/microsoft/mcp), [\[microsoft.com\]](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/introducing-model-context-protocol-mcp-in-copilot-studio-simplified-integration-with-ai-apps-and-agents/), [\[microsoft.com\]](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)
*   **Copilot CLI** – command reference & best practices; background agents in VS Code. [\[docs.github.com\]](https://docs.github.com/en/copilot/reference/cli-command-reference), [\[docs.github.com\]](https://docs.github.com/en/copilot/how-tos/copilot-cli/cli-best-practices), [\[code.visua...studio.com\]](https://code.visualstudio.com/docs/copilot/agents/background-agents)
*   **.NET Aspire** – overview and GitHub repo (AppHost, resources, observability). [\[learn.microsoft.com\]](https://learn.microsoft.com/en-us/dotnet/aspire/), [\[github.com\]](https://github.com/dotnet/aspire)
*   **Detester** – deterministic testing library for AI responses (nice fit for your CI). [\[github.com\]](https://github.com/sa-es-ir/detester)

***

If you want, I can scaffold an **Aspire solution layout** with these services and a sample **AF + Copilot SDK** agent wired to a placeholder MCP server—ready for you to fill in the survey specifics.

