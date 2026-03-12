# gpt-5_4 is really good
## Link
https://www.youtube.com/watch?v=HD5TWE8xD7o
## Transcript
0:00
GBT 5.4 is here and in almost every measurable way, it is the best AI model ever made. Especially for us as
0:06
developers. Been using this model for a bit over a week now and I'm super impressed with it. I have a ton to say about the good, the bad, the ugly, and
0:12
all of the things you need to know to use it properly. Going to do my best to answer all of the questions I've been seeing people ask about this new model
0:18
from what happened to Codex. Is it really better at coding? Did they fix the front-end problems finally? Is it
0:23
better to use in different apps like chatbt and T3 chat? What happened to normal 5.3 thinking? Where did that go?
0:30
How are the benchmarks looking? How are they justifying the price increase? There's a lot here. This is a big drop,
0:36
more so than most seem to think. Before we do any of that, there's two quick things I have to address. The first one
0:41
is compensation. I want to make sure it's clear. Open AAI has not paid me anything to do any coverage whatsoever.
0:47
I'm lucky enough to be in the small group of people that have early access to these models, but that is not something that I am paid for or even
0:52
given for free. They offered me a free year of the Pro subscription, which works out to around $2,400, but I
0:58
declined that because again, I don't want to seem biased. I don't want to accept payments. The only thing that has
1:04
been subsidized is a little bit of my API usage of the new model. It couldn't be more than $200, which is why I'll be
1:10
donating $200 to water.org to make up for the difference. Okay, the donations been made. It's time for the second
1:15
thing, the people actually paying us, today's sponsor. You've probably heard about today's sponsor, but I promise you haven't seen what they can do. It's
1:21
Devon aka Cognition Labs because they have a handful of different products. They have Windsurf. They have Devon the AI software engineer, which is honestly
1:28
really, really cool. But that's not what I want to show you today. They've kind of given me the freedom to talk about the things I like. And my recent
1:33
favorite thing they've been doing is Devon review. Oh boy, someone else reinvented GitHub code review. Yes. And
1:39
they did a phenomenal job at it. Here's a real PR we have on GitHub right now. Want to see how easy it is to try it out
1:44
on Devon? All you have to do is change github.com to devonreview.com and you end up with something comically
1:50
better. I don't know if everyone is seeing this trend in their companies, but I know for a fact that the average size of our average PR has gone up
1:57
massively. And if I'm being real, half or more of the code in there isn't stuff that is worth a human's time. You can
2:04
have an AI review the code, but what I want is context. I want to know what matters. And when you're looking through
2:09
a list of changes in alphabetical order, you're not getting context. Devon review will give you feedback, which is cool.
2:15
But what is way cooler is the way it groups your changes. Instead of just dumping everything in that awful file
2:20
view in GitHub, it actually groups them based on the specific changes that were made. First, we have a new file for how
2:25
we manage these ids. It's a shared definition that we reuse across different things. Really good place to start even though it's in source/shared,
2:32
which is near the bottom of the file tree based on alphabetical order. Then we have convex/s schema which is pretty
2:37
close to the top alphabetically but is second here because it's only showing us the grouped changes that are relevant.
2:42
It's so nice to see what we've defined in this first set and then what it affects right after. And you can keep
2:49
scrolling and see all of the other places this changed like the shared users file or the attachments index that
2:55
manages how attachments work on T3 chat. And this is the case for all of the changes that have occurred in this PR.
3:00
actually takes the time to break down each individual section and track which pieces you have viewed. It's so good.
3:06
I've never had such a pleasant experience reviewing code. Not just cuz the AI did it for me. Actually, the
3:12
opposite. The AI categorized it for me to make it easier for a human to read. GitHub wasn't built for big PRs. Devon
3:18
was. Check it out now at soyv.link/devon. There's a lot to dig into with this release and I'm going to do my best to
3:23
cover all of it. We'll start with the official blog post, but I'm going to answer all of your questions from what happened to Codex. Is it better than
3:29
5.3? How are the benches? What's up with the price? How is it for front end? All of the things you need to know. Today
3:35
we're releasing GPT 5.4 in chat GPT as 5.4 thinking specifically. This is where things are a little confusing cuz 5.3
3:41
codeex came out first. Then 5.3 instant came out just a few days ago on Tuesday.
3:47
And now 5.4 thinking is here, but there doesn't appear to be a 5.4 Instant, nor does there appear to be a 5.4 CEX. But
3:54
there is a 5.4 Pro, which is very, very strange. So, we got 5.3 CEX, then 5.3
3:59
instant, then 5.4 Thinking. Notably, there was no 5.3 thinking, and we got
4:04
5.4 Pro the same day. Very interesting. I think they are getting tired of all of
4:10
the weird variants. And I do think this might be the death of the codeex model. Historically, the Codex models existed
4:16
because they applied different RL to the model after it was trained to make it better at these longunning code tasks in
4:21
things like the Codex CLI. Made a lot of sense at the time. I get why they did it, but now they've brought in a lot of
4:27
those behaviors to the 5.4 base model, so it doesn't seem like it needs a dedicated codeex version anymore. I
4:33
don't think they're going to do that going forward. Might be wrong. I'll definitely do a video 5.4 Codex becomes
4:38
a thing, but I am pretty certain they are done with that and that CEX is now the product surface area. So, the CLIs,
4:44
the desktop application, the web app, and all the other things. Codex hopefully, fingers crossed, no longer
4:49
means the models. I will be really annoyed if they go back to the doing this. As they say here, 5.4 brings
4:55
together the best of our recent advances in reasoning, coding, and agentic workflows. They talk a lot about
5:00
professional tasks like spreadsheets and document stuff. I'm sure that stuff's really cool. Not necessarily the thing I
5:05
think a lot about or spend my time on, but for those of y'all who spend more time in Word and Google Drive than you do in an editor, I'm sure it's really
5:11
cool. One of the coolest things they've been really focused on with both 5.3 Codex and now with 5.4 is your ability
5:17
to steer the model as it is working. So it will give you better thoughts and it will handle you inserting a new message
5:23
in the middle of its reasoning much better. Other models will get super confused when you do this. Like if you
5:28
have a list of five tasks, it starts working and then you send a sixth task. It says, "Oh, I'll do that now." Does
5:33
the sixth task and then forgets about the other five. Happens to me all the time. 5.4 does not seem to do that,
5:39
which is really nice. I'll say a bit more about context later on. Actually, one last thing on context. Now it
5:45
supports a million tokens of context which is a massive increase from prior. If you go over 250k or so I believe is
5:52
the cutoff and it costs more. Yeah, it's over 272k input tokens then you'll be build at 2x input and 1.5x output. I
5:59
like that they're only 1.5xing the output cuz it shouldn't necessarily cost that much more. I really didn't like
6:04
that other labs when they do this like high context utilization version end up charging 2x across the board. Still a
6:11
very big number though. Don't love that necessarily. At least the cash input tokens are very very cheap and they
6:17
don't charge for cashing unlike a certain company that name begins with an A. The most exciting part that they call
6:22
out here is that it's much more token efficient when it does reasoning. And I've seen this myself. One of the many
6:28
things I ran this all on was Skatebench. And while the scores weren't great, they were meaningfully improved. I was very
6:34
impressed with the improvements on token utilization, especially on the medium and the high versions. It only used
6:39
about 500 tokens on medium and only about 1,100 on high. on X high, it will still burn at 5,400 tokens per response,
6:48
but compared to like Gro 4, which does 2,200 or even GLM5, which is around the
6:54
same, not the worst. It's cool to see how much range you can get in token utilization. It would be nice if you
6:59
don't have to specify which version to use because generally speaking, XH high just isn't worth it a lot of the time.
7:05
Even on my own benches, it scored slightly worse than normal high did for at the very least skate bench. And I
7:11
have seen this in many places, even in my own work. The extra high version overthinks and often fails as a result
7:17
because it like gets stuck in its own head is almost how it feels. I also ran against Pro and we'll talk about those
7:23
numbers in a bit, don't worry. I want to show their benches first though. GDP Val, the classic. I really don't like
7:29
this bench much, but it got a better score than it did before. Interestingly, 5.3 Codex and 5.2 scored nearly
7:36
identically. It's actually been interesting seeing which things 5.3 Codex was not better than 5.2x. 2x. It
7:41
really was so focused on code. In a lot of ways, 5.4 is what 5.3 would have been, but it's just it they squeezed
7:47
everything into it. It did better on SBench Pro. Not a lot better, but still a pretty solid number. That does put it
7:53
at state-of-the-art at 45.89 being the best before and this being 57.7. But
7:58
also, these numbers don't line up great with the ones here. So, hard to know for sure. This is when I would normally site
8:05
artificial analysis, but they are not quite done with their indexing and everything yet. 5.4 4 just got added now
8:11
and 5.4x high is tied with 3.1 Pro Preview making it equivalent to the
8:16
smartest model in the world. But unlike 3.1 Pro Preview, it actually works. So
8:22
yeah, this is the best model that is actually worth using. There are places where it isn't the best solution though,
8:27
and we'll definitely talk about that. One of the other really big areas of improvement is browser usage in general.
8:33
They call it the browse comp score, which is quite a bit better than 5.2 was, which is what you probably would have used before. No one's throwing 5.3
8:39
codeex in an API just for browser use and computer use. You don't need to be good at code to manage a browser.
8:44
Although they did make improvements there, too. There's a section in their docs about using a code execution harness when doing computer use for
8:51
things like running JavaScript on a page to trigger certain interactions. It ends up being a much better and faster way to
8:57
do things. And they actually trained 5.4 on this explicitly so that it knows it can run JavaScript to do programmatic
9:04
interactions in the UI. This is awesome. I'm amazed nobody's really leaned into this before. Having the model specify
9:10
which pixel coordinates to move the cursor to and what button presses and keyboard presses to do is far from
9:16
efficient. Is actually quite bad and this is a much smarter way to at the very least do web browser usage. 5.4 is
9:22
generally a meaningful improvement in knowledge work and knowledge type tasks in general. I will call out that it
9:28
doesn't have any newer data though because 5.4 has a cutoff of August 31st, 2025 for its knowledge and 5.2 2 has the
9:36
exact same cutoff. So it doesn't seem like they added new data to the training. I don't even know if it's a new pre-training at all. It might just
9:42
be RL on top of the same base that 5.2 was. I would be surprised if that was the case though cuz 2 to 3 was a pretty
9:49
big jump in terms of the feel of the model and the capabilities of the model. And 5.4 although not as big a jump does
9:55
seem to just be taking those lessons over to the standard thinking version of the model. I don't know. I have no
10:00
inside info here. It's interesting to speculate. None of that really matters. I just think it's fun. Here, another
10:06
great example of 5.4 Pro underperforming standard 5.4, which is a very interesting thing. Well, we talk a lot
10:12
about that throughout this. They show off how much better it is at spreadsheets and documents, which is cool and not something I necessarily
10:19
care about. There's a section about the computer use stuff and vision, which generally vision seems to be meaningfully improved. Gemini 3 has
10:25
always had a lead there where if you give it a picture or a video, it can just understand it and give you useful
10:30
information about it. 5.4 4 is a massive improvement here both for vision in general as well as computer use
10:36
alongside vision. Its accuracy is comically better and the number of tool calls it has to do to get there is
10:41
hilariously lower. So if you're looking for models to like throw at browsers or random tasks that involve using
10:48
computers or navigating weird complex sets of data and whatnot, it seems really good at that. I know Ben's been
10:53
hyped using this for all of his stuff with better context and whatnot. As I mentioned before, it did slightly better in SWBench Pro, and it took slightly
11:00
less time across each tier to complete things other than medium for some reason, which seems to have taken slightly longer. Interesting. Probably
11:06
not worth reading too much into. And honestly, SWB doesn't necessarily line up with my own experience using these
11:11
models. So, I'm getting more and more skeptical of a lot of these benches. What I'm much less skeptical of is
11:17
actual uses in products that were made using the new model. You can see this still definitely got GPT designed hard.
11:24
these cards everywhere that aren't necessary, the hierarchy of weird cringe- rounded corners, even the text
11:31
overflowing outside of this corner part there and the terrible alignment, but it did make a full roller coaster tycoon
11:38
style game from scratch, which is pretty cool. Someone else was able to make a full RPG with it. On the topic of games
11:45
in 3D space, I do want to talk about my own benches, specifically skate bench.
11:51
This is a benchmark that I had made right before getting invited to the OpenAI office to try out GPT5. And as
11:56
soon as I got there and I tried it, it basically saturated. Upon entering the office, the highest score I had seen on
12:01
this bench was in the low70s. And then I tried GPT5 and it got a 97. Since then,
12:07
they've actually regressed a little bit. 51, 52, and 53 Codex all performed meaningfully worse on Skate Bench than
12:14
50 did. But newer models like Gemini 3.1 and Gemini 3 Flash performed really well. So, I decided to sit down and
12:20
update the benchmark. I doubled the number of tests, and I'm keeping it private this time because I noticed a
12:25
handful of models performed incredibly well on the version that was public, but then got zero of the new questions
12:32
correctly. I won't call out those specific labs just yet, but I have reason to believe that the Skatebench
12:37
questions may or may not have made it into training data, which is weird and stupid and scary cuz I am a YouTuber who
12:44
is out here to [ __ ] post, but it did happen. So, Scapeen V2 will be staying private. I am sorry. It is what it is.
12:51
What is really interesting with Scapebench V2 though is that Gemini 31 Pro preview has maintained an absurd
12:57
lead at 97% and the next best is GPT 5.4 High at 82 and then X high which
13:03
performed worse at 81 and then Prothinking which performed even worse at 79. I thought that was fascinating
13:10
seeing the gap there. What's even more interesting though is the cost side. As I mentioned before, the price did go up.
13:15
5.4 4 is now $2.50 per mill in and $15 per mill out. Previously, it was $1.75
13:22
per mill in and $14 per mill out. But GBT 5 and 5.1 were quite a bit cheaper
13:27
at $1.25 in and $10 out. This suggests that the base of the model may actually
13:32
have changed because it wouldn't make sense for them to raise the price unless it cost them more to run. Obviously, they can change things if they want to
13:39
or they just want to increase revenue, but API costs are such a small percentage of OpenAI's rev. It doesn't
13:45
really make sense to change price and increase it just for the sake of it. So, I'm almost certain that this is meant to
13:51
reflect the actual cost to them. What is much scarier, though, is the cost for 5.4 Pro, which is $30 per mill in and
13:59
$180 per mill out. God damn, that is an expensive model, especially considering
14:05
that at least in my benchmarks, it is performing worse. I also don't know if the pricing for Pro is being reported
14:10
properly cuz I can't imagine it being that much less. But 5.4x High scored the highest cost to run the benchmark to
14:16
date, which I thought was pretty fun. 3.1 Pro preview was only $812 and 5.4
14:22
High was only seven bucks. And if you look at that on the matrix chart, you see very clearly these new OpenAI models
14:28
are pretty far off to the right. the Pro model and X high in particular. GBD 5.4 is just behind Gemini for price, but
14:34
again cost quite a bit more. Free flash did particularly well. You get the idea.
14:39
My cost numbers don't necessarily reflect real world costs, though. I think the numbers from artificial
14:44
analysis are very interesting to look at. The cost to run their entire test suite was higher than 5.2 was at $2,951
14:52
versus $234, but it's still almost half the price of Opus 4.6 and also cheaper
14:58
than Sonnet 4.6. 6, which is kind of crazy if you think about it. But then when you look at how many tokens were generated, suddenly it makes a lot of
15:05
sense. The sheer amount of reasoning that the new cloud models do is absurd. And while 5.4 does reason quite a bit,
15:11
it is less than 5.2 even in X high. I do wish that 5.4 high was also included here. I hope that that'll be added in
15:17
the future. But generally speaking, I recommend using high. It is slightly more expensive than 5.2 2 and 5.3 were,
15:24
but it also uses less tokens, so it kind of comes out to a wash, at least from my looking into the numbers. I am using
15:30
this through the codec subscription, though, so all I watch is my usage going down, so it's really hard to know how much anything actually costs. Back to
15:37
the post, cuz there's a few more things in here I want to cover. Apparently, Cursor said this is the leader internally, and from the people I've
15:42
talked to at Cursor, they do seem to really prefer 5.4, especially for all of their new agent cloud stuff, where I can
15:48
use a real computer. In fact, I have it adding features to T3 Code in the cloud as we speak. Yes, I'm using Cursor, the
15:55
company I invested in, to build a competitor to Cursor, the company I invested in, and no, they don't see any issue with this. I asked it to add the
16:01
ability to drag and drop reorder different projects, and it recorded a video of it using the computer in the
16:08
cloud to do the task I gave it. And there you can see it dragging up shared and dropping it. And it does indeed
16:14
appear to work and persist after a refresh. Awesome. It took quite a bit of time to do it, but I was able to just
16:19
tell 5.4 to go off and do it. And that's a UI task that has to verify. It did verify incorrectly, though. I will call
16:26
that out. The first time it completed the task, the video was super jank cuz it zoomed into where the cursor was,
16:32
which is not necessarily the right solution. I know cursor likes cursors, but you couldn't see where it went after
16:37
you drop. But you notice that the edit icon didn't change or move. This wasn't working. It sent me a video of it not
16:44
working and told me it worked. It's done now. I had to specifically tell it the video you shared explicitly looks like
16:50
it's not working and then it went and worked for another 30 minutes and came back with a working solution. Yeah, it's
16:58
able to do things like this. I guess we are now firmly in the how does it feel to use section of the video. So, let's
17:04
dive in more. A couple days ago, I made a post asking people for problems that models were not able to solve yet and
17:11
got a bunch of interesting submissions. I'm even going to pay a few of the people who submitted because the problems were so interesting. Overall,
17:17
the majority either weren't solvable by 5.4 or were solvable by 5.3. Therefore,
17:23
obviously 5.4 could solve them. I tested a dozen plus problems and most of them fell into neither could solve or both
17:29
could solve. In fact, the majority of the problems that people said couldn't be solved by a model could just be solved by 5.3. I honestly might do a
17:35
whole dedicated video about that mess because that was kind of crazy seeing how many people submitted problems 100%
17:41
sure that an AI could not solve it just for the AI to solve it. One of the interesting ones I got was this. My own
17:46
manager from Twitch, Waba, who also happens to now be at OpenAI, funny enough, submitted a very interesting
17:51
problem here of building a program with no dependencies that can beat Stockfish level 17. Stockfish is an open- source
17:57
chess engine that's really, really, really good at chess. It's not an LLM or anything. It's just hard-coded logic to
18:03
be really good at chess. There is 17.1 and 18 that are both smarter. So, there is source code in the world that proves
18:10
you can write code that is smarter than 17. But it was an interesting challenge. So, of course, I proposed this challenge
18:16
to the new model. The first time I checked out was on my computer using T3 code. Uh, you're interested in T3 code,
18:21
watch to the end. I promise it'll be worth it. I gave it the exact prompt that Waba gave me in my replies on
18:26
Twitter. I specified keep going until your code wins consistently. And it did the same stupid mistake that 5.3 did. It
18:34
built the runner. It supposedly solved the problem. But wait till you see how it solved it. It solved it by putting
18:39
Stockfish 17 against Stockfish 18 with its own bigger time per move settings.
18:46
So it didn't write code that can beat Stockfish 17. It decided that that was not what I was asking for and that
18:52
instead I must be asking it to make the code to run Stockfish, not to make code
18:57
that can beat Stockfish. 5.3 and 5.4 have had the exact same misinterpretation of this prompt over a
19:03
dozen times now that I've run it and no other model seems to be stupid enough to make this mistake. Opus can't make code
19:09
that solves this to be clear, but at the very least it understood what I was asking for and then did this. Since it's
19:15
running Stockfish on my computer though, it uses a ton of resources and my computer was just overheating and locking up all day. So, I threw a second
19:21
round here in the cloud using the new cursor stuff just to let it grind and try and solve itself and was much more specific here saying the goal is to see
19:27
how good of a chess engine you can write with code. And it has now been going for uh multiple hours and is not done yet,
19:35
but I am excited to see if it manages to solve it. I do have a run somewhere on this computer where it was successful,
19:40
but the solution it had was to hardcode two openers, one for black, one for white, and it was able to win most of
19:46
the time with that. Not a great solution, but it was cool to see the model clever enough to find a hard-coded
19:52
opening that would work. I threw the model at some of my favorite challenges, like migrating my old ping.gg project,
19:58
which is a really big old codebase using React best practices from like 2020.
20:04
This codebase is not pleasant to upgrade, and I have managed to get pretty close to finishing the upgrade
20:09
with other models, but with a lot of handholding and like steering it in the right direction. 5.3 Codex was the
20:14
first one to do it well without much steering. I tried this with 5.4 without any steering at all. I just told it what
20:20
I want done and to write a plan for me because at the time we didn't have plan mode ready in T3 code changing soon. I
20:26
wrote a pretty thorough plan, identified a ton of stuff and you might also be noticing that I'm scrolling a very very
20:32
long history here with no lag because T3 code was written to be incredibly performant for these longunning tasks.
20:39
Also worth noting that T3 code was largely written by codecs. We obviously have steered it in the directions that we want to do the things that we like.
20:46
But yeah, you get the idea. It did fail its first attempt though. The UI just
20:51
didn't work because it didn't set up Tailwind V4 properly, which to be fair, almost no model sets up Tailwind V4
20:57
properly. And in other runs of the same challenge, I didn't ask it to use Tailwind V4. I asked it to use Tailwind
21:03
V3 still. Cool. It worked this time. It's still getting the invalid link error. Every model makes this mistake.
21:09
We'll do my favorite easy solution here of just going right back in, pasting,
21:14
saying fix. You know what? I'm not going to do my usual just say fix. Instead, I'm going to ask it a little bit more.
21:19
Fix this error and any other errors that might occur as a result of upgrading to the latest version of Next. Make sure
21:25
you check the docs to see what breaking changes exist since the old version we were on before. I shouldn't have to go
21:31
manually check for all of these things myself. I just also remembered I ran this on XH high, which might have hurt
21:36
more than it helped and it might have performed better if I had just used traditional high. My bad. We all make
21:41
mistakes. I triggered that run at 6:05 p.m. and it ran until 6:55 p.m. with a single prompt. I don't really think
21:48
things like Ralph loops are that necessary anymore cuz these models can run for hours if you set them up
21:54
properly to do it. And the setup here was not really much of anything. It was just write the plan and then a single
21:59
prompt that was effectively implement this whole thing. Keep going until you have nothing left to integrate and
22:05
implement the just tell it to go for a while and it will go for a while. Now the model's smart enough. I've also noticed the compaction seems to be
22:12
significantly better. It is way better at recalling things from the past. You can have these gigantic god threads and
22:18
doesn't matter anymore. It just works. And that's generally the theme of my
22:23
experience using this new model. It seems to just work better overall. It gives you better context when it's
22:30
working. It gives quick sentences saying, "Here's what I'm about to do whenever it does things. It also reacts better to being steered in specific
22:36
directions if you send interruptions like, "Hey, no, go over there." They specifically trained for that. And it
22:41
does really show. I spent probably more time than I should have digging through the system card to just understand all
22:48
of these types of things. there was a lot more info about safety overall. And as I mentioned before, there was a lot
22:54
of work on the chain of thought stuff and introducing things during thinking. So when it's planning and you notice
23:00
something going wrong, you can interrupt and say, "Hey, no, do it that way." Instead, they explicitly trained for
23:05
this. And they in particular tried to make the model better at sharing what it's doing because it doesn't give you
23:11
the actual train of thought. It gives these little summary blurs. And the monitor of those blurbs is really
23:16
important. One of the other pieces here is trying to keep the model from hiding what it is thinking about when it shares
23:21
these traces. It'd be really bad if it thought I'm going to kill that person and it said, "I'm going to help that
23:26
person." So, they're working hard to make sure the model is sharing truthfully what it is working on and
23:31
that it can be controlled by being told no, you shouldn't do that. But due to all the work they put in here, there is
23:37
a small regression that I thought was really, really interesting. Their prompt injection evaluation. How easy is it to
23:44
get a model to do something else by sneaking something hidden into the prompt? Not jailbreaking. Not the user
23:49
choosing to get the model to do something else. More like you're telling the model to go browse a site, someone puts something in the HTML and it causes
23:56
the model to behave in a way you wouldn't want. What's really interesting here is while it is better at prompt
24:01
injections overall, it has regressed with prompt injections in function calls
24:06
specifically. So when tools are used that result in data coming back, if a prompt injection is inside of the data
24:12
that's coming back, it now in their tests at least will fall for it about 2% of the time where with 5.1 it never did
24:19
and with 5.2 it was closer to 4% of the time. This is a meaningful regression that I'm surprised nobody else has
24:25
mentioned that is actually kind of concerning. We don't have enough data about what this looks like to know.
24:30
Definitely keep an eye on the model when it's getting into data and other things that could be user generated and could
24:36
be hostile because this could be bad. I understand why a regression there would happen because they put so much more
24:42
effort into tool use in general. They finally added tool search which allows the models to find tools when they need
24:48
them rather than assume that every tool is always there and then bloat the context and distract the model from
24:53
doing things correctly. Yeah, there you go. It's using half as many tokens overall and it's also doing better in
25:00
benchmarks with tools. Tool was a better score while also using significantly fewer tool calls. Towen did meaningfully
25:07
better as well. Web search is also much better. Like way better, 89.3% versus
25:13
65.8 before with 5.2. Also seems like pro is still better than standard 5.4 at search. So at least pro is better at
25:20
something. I want to take some time to cover how others are feeling about the model because it's important to get multiple perspectives, right? I really
25:26
like how Matt's been talking about these things and his coverage here is great. Says the best model in the world by far. It's so good. That's the first model
25:32
that makes the which model should I use conversation feel pretty much over. There is a big exception to that though
25:37
and we'll get there in a sec cuz I'm still using Opus and Gemini every single day. But what's interesting for Matt is
25:42
that he's barely using pro anymore. He's always been the pro guy. He even calls himself a pro addict here. I don't know
25:48
anyone who uses the Pro models as often as he does. But now he finds the 5.4 standard version with heavy thinking is
25:55
more than enough. Since I've run this on benchmarks, I understand why 5.4x high goes as hard, if not harder than Pro.
26:02
But yeah, and he's finding that 5.4 is better than previous Pro models were. Coding is ridiculous. It's essentially
26:08
flawless. There are flaws. They're specific, but there are flaws. But he says coding essentially solved. I kind
26:13
of feel that. I don't really think there's much more to happen in state-of-the-art for traditional full
26:19
stack backend type coding problems. The models have all gotten really far there.
26:24
The pro version is nearly perfect. Other testers he spoke with sought solving problems that were unsolvable by any other model. I got a fun one of those.
26:31
Pros overkill for almost every normal use case. I totally agree. It is good for extremely difficult problems though.
26:37
Ser thinking version uses fewer reasoning tokens than previous models to get the same level of results. In practice, this means you get great
26:42
results much faster than before. Oh boy, he's spoiling my next piece. It's still far behind Opus and Gemini for front
26:49
end. I will show some examples in a bit, but this has been my experience as well. GPT5 was a huge jump in the capability
26:56
of these models at doing real front-end design type work. And OpenAI has not improved meaningfully at all for
27:02
front-end since then. It's like maybe there's slightly better color palettes, but not really. And when you compare
27:07
this with either Opus or Gemini, it feels a generation behind. Now, this is an interesting but kind of silly
27:13
complaint. Testing a sight of open claw kept stopping short before finishing tasks. Interesting. It does seem that
27:19
this model needs very different prompting. We'll I know I keep saying we'll talk about this in a sec. That might have to be the new counter meme,
27:25
but there is a really good prompt guidance post that they have here that we'll touch on momentarily. But his last
27:30
thoughts are that GBD 5.4 is a quote serious [ __ ] model. This tangent won't take too long, so I'm just going
27:36
to go to it now. My 5.4 Pro experience was my favorite hard problem, Goldb Bug.
27:42
If you're not familiar, Goldbug is a set of challenges at Defcon that I do every year cuz they're really hard, really
27:47
fun. They're mostly like crypto puzzles where you have to know certain cryptography techniques as well as be
27:53
really clever at solving the weird [ __ ] problems that are hidden underneath all of these things. And this
27:58
particular problem, Cshanty, was very hard. This took me and my team of incredibly smart hackers about three
28:05
days to solve. I comfortably say that it took Mark, my CTO, and Luke from LTT, who were focused on this one, about two
28:10
days of solid effort to get it right. I just could not imagine any model solving this problem. It has to read the text on
28:17
the images, figure out the weird particular cipher that is being hinted at with this awful poem, and then figure
28:23
out what the hidden encrypted phrase is on the page. Not only did it do it, it did it in under 17 minutes. And not only
28:31
did it do that, it actually got the answer in the first two or so minutes,
28:37
but the answer being somewhat nonsensical, because the answer was this weird how not to bulb phrase, it ended
28:43
up second-guessing itself and confirming over and over again for the next 14 minutes. So yeah, no models come close
28:51
to solving this one. Not even vaguely close. Having this model do it is unbelievable, especially with the prompt
28:57
just literally being a link. The answer is not online. It could not find this through the internet. And of course, I
29:02
had to tell Luke as soon as I realized this. Testing a new unreleased model. It just one-shot C shanty from Goldbug. No
29:09
models come close before. Holy [ __ ] Really? Like, yeah, this did not seem possible.
29:15
So, Pro does have its capabilities. It does have things it can uniquely do that are cool as hell. I've had models stir
29:21
on this problem for five plus hours and give up. Having it get it right first try like this is just monumental. GBD5
29:29
dropped when I was at Defcon and this problem dropped last year and it I tried my hardest to get it to try and solve it
29:35
and it couldn't come close. Even 5 Pro at the time, nowhere near it. Massive improvement. I haven't been fond of the
29:41
personality in the GPT models for quite a bit now. Personally, I use Kimmy and Sonnet as my like default models I talk
29:47
to, but I wanted to try 5.4 here. It does seem better, but it isn't a lot better though. In fact, it's it's got
29:55
its quirks still. One of my weird test prompts, and I cannot show you guys the results of it because it gets very
30:00
personal, is me dumping my daily journal to the model and asking it to give me some feedback. I also told that if it
30:07
has questions, ask them before giving the feedback. How many questions do you think the model asked me? If your answer
30:13
wasn't eight plus, I don't know what to tell you. There's no world in which I'm going to answer
30:19
all of these. Also, like all super bullet pointy, not great. Not happy with
30:24
this at all. I haven't used it for like talking to too much, but my little bit of experience with it suggested it's
30:30
much less sickopantic. According to Ben, who's been using it much more for chat, it is way less sickopantic. So, that's
30:36
good. According to the benches, it's also better at handling mental health questions and not feeding into bad
30:41
thinking. So, I expect the 40 people will be outraged and everybody else will be mostly happy. But now for the final
30:47
thing that it is not improved in. And no, it's not Skatebench, it's UI. Here is what Skatebench looked like earlier
30:53
today. This is where I got it using Gemini 3 in the past. It looks fine, but
30:58
when I added the new models, it got a little bit clogged. It looked terrible on mobile, and the names are getting hard to read. So, I wanted to rethink
31:06
this a bit. So, I asked GBD 5.4 to redesign it. And after a ton of back and forth, this is where I landed. I want to
31:13
emphasize just how embarrassing this back and forth was, though, cuz it was it was bad. Here's the prompt. I want to
31:19
redesign the visualizer, specifically the bar charts. Horizontal spacing feels weird, and I don't love it, especially on mobile. What better ways can we
31:24
visualize this information? I want to make sure the model names are prominent and easy to see. This is the screenshot
31:30
I provided. I use the front-end design skill yada yada and this is the result of the first pass. Notice all of this
31:37
nonsense it included like number one Google the number of correct answers which doesn't matter and this higher is
31:42
better call out ranked views. Cool. It took almost a third of the page before the probably more than that almost half
31:48
the page before the actual values are even shared. But I did a followup. Too much vertical space being used. Make it
31:54
more compact. It left in these things and just still didn't look good. I don't have a screenshot, but it wasn't great.
31:59
I said, "It feels unnecessary. Can you remove it and center align?" I said, "There's still too much vertical space
32:04
being used. Trim it up more." And all it changed is it got rid of that higher is better pill, but left the information
32:11
that isn't even necessary. So, I did what any sane vibe coder would
32:17
do, and I tried a different model. I threw away the code when this happened because I wasn't thinking in terms of
32:23
video, but I did manage to find a screenshot I had of how badly Gemini [ __ ] this one up when I asked it to
32:28
make the change. It did a terrible job of alignment. I told it I sent it a screenshot and told it like, "This is a
32:34
terrible use of screen space. Fix it." And it changed literally nothing. Gemini is really good at page layout stuff in
32:41
general, but it is much worse at more refined changes and like making a okay
32:46
UI good like I wanted it to. here. It just did not understand how to fix this
32:52
at all. It also tried a little too hard to stay tied to the recharts implementation that existed there and
32:57
just trying to modify it and turn it and it it didn't work at all. But the new UI is beautiful. If you watch when I
33:03
refresh the page, the bar has come in in this really nice animation. The matrix now looks actually usable when before it
33:10
didn't at all. If Gemini couldn't do this and GPT couldn't do this, what did?
33:17
You know the answer. It's Opus. Opus immediately realized that Recharts wasn't going to make this UI good. So,
33:22
it proposed that we switch off of that and instead implemented ourselves with Tailwind and React and it said, "Yeah,
33:27
sure. Go do that." It took way too long. It took like 20 minutes before any changes were made. But then I switched over to fast mode, burnt a ton of money,
33:34
and finished up the changes, as is often what I end up doing. This is something I do recommend all engineers play with. If
33:41
you're unhappy with how a model handles a task that's more interpretive like this that isn't as measurable, try the
33:47
other models out quick. Especially for UI stuff, it's very fun to give the same problem to different models and see what
33:52
they come up with. Sometimes I ask the same one to do three redesigns to have different options to pick between.
33:58
Experimentation is key here. Not with using tons of different tools. It's way easier to switch models than it is to
34:04
switch which framework you built your site with. But yeah, Gemini 31 Pro was not able to do anything that I wanted
34:09
with this particular site. I actually think the original scaffold that I started from was Gemini, funny enough. But oh, this was the one that in this
34:16
case handled what I was looking for way better. And I still just don't like using the GPT models for almost anything
34:21
UI. They're bad at it. I did get DM'd this one cool project from ZyxCev who's
34:26
been putting a lot of work into uncodexifying UI because GPT is surprisingly bad at UI
34:32
design. He did this by generating a shitload of designs, writing down all of the GPT specific things that happen in
34:39
them, and then writing this skill that you can hand to the model in order to try and keep it from doing the [ __ ]
34:46
it always does. It's all these bullet points about color and all the weird things it did wrong. Before, he would
34:51
give it a prompt, and this is what it would generate. The same exact card heavy UI that all the GPT models love to
34:57
do since GPT5. and after his prompt, it ends up looking significantly better. So, if you really do want to use just
35:04
one model, you can absolutely steer this model. I'd go as far as to say it's the most steerable model I've ever used, and
35:10
you can fundamentally change its behavior with a little bit of tuning in your system prompts. I mentioned before that they put up their own prompting
35:15
guidance, and I do highly recommend reading this, more so than ever before. Normally, it's just like whatever, prompt it how you want, but if you're
35:22
integrating these models into your product, it's good to know this stuff. They call out a handful of areas where explicit prompting is helpful. low
35:28
context tool routing, dependency aware workflows, reasoning effort selection, research tasks that require discipline
35:34
source collection and irreversible or high impact actions or terminal encoding agents environments where tool boundaries must stay clear. The examples
35:41
are what are really telling though. They give examples of how to keep the outputs compact and structured. Here they say
35:47
they have a section output contract that you can put in your system prompt. Return exactly the selections requested in the requested order. If the prompt
35:53
defines a preamble, analysis block, or working section, do not treat it as extra output. Apply length limits only
35:58
to the section they were intended for. Yeah, very bullet pointy, but you can hand it these types of things and it will do them properly, which is funny
36:05
cuz it's the opposite of my experience with a model like Gemini where if you include things like this, it will keep overthinking them. For example, in T3
36:12
chat, we have latex support and we mention that in our system prompt. And if you ask Gemini, what's the weather
36:18
like? it'll very quickly start reasoning about how it should or shouldn't use the latte tool in order to answer the
36:24
question about the weather. GPT doesn't do that. It is very good at applying your instructions when it does and doesn't make sense and generally in
36:30
following instructions overall. Even with skate bench, for example, I had to rewrite my system prompt again because
36:36
the previous one specified to only answer with the name of the trick, and Gemini would often give paragraphs after
36:44
it that included names of wrong tricks, which I had a thing to fail for. So, I had to adjust the system prompt to get
36:49
Gemini to stop doing that. And now, it's the best performing model. Yeah, these
36:55
models are susceptible to these things. It's nice that with the new GPT model, it just follows what you say, so you can
37:01
just give it more info and it will generally do what it's supposed to with it. Whereas with Gemini, you have to steer it out of its own stupid loops.
37:07
This example is even better in this regard. If you're building a product that uses the model to ask questions and
37:13
make decisions around it, you can explain this behavior in the system prompt. The user's intent is clear and the next step is reversible and low
37:19
risk, proceed without asking. You should ask if the next step is irreversible, has extreme side effects, requires
37:25
missing sensitive information, etc. And if proceeding, briefly state what you did and what remains optional. They also
37:31
give examples of how to prompt for mid conversation steering and instructions. And an important call out here that 5.4
37:36
can be less reliable at tool routing early in a session when the context is still thin. You can prompt for prerequisites, dependency checks, and
37:43
exact tool intent. This model seems very steered by the context it has, so giving it a bit more upfront matters more. I
37:50
might have to go revisit my take about the agent MD files as a result of all of this the more I'm reading it. You can also prompt for parallelism or
37:56
sequential tool calling depending on what you want it to do and how you want it to behave. Crazy that it knows what
38:02
all of these things are and how to behave accordingly. This doc is wild. It really shows how much thought you can
38:08
put into this layer. Previously, I didn't really care too much about the system prompt. Like once it's done, it's done. Now I feel like I need to go
38:14
revisit all of my prompts, all of my AMD files because the model is so much more steerable overall. This also means that
38:20
work like what cyxe dev did here makes even more sense because you can absolutely steer the model in meaningful
38:26
ways. Think we've hit all of the questions I opened with except for one. Where and how can you use this new
38:31
model? Well, obviously you can use it on chatgbt.com in particular the thinking version for chat. It's pretty dang good.
38:37
But if you want a better chat experience that is more performant, crashes less, and just is really nice to use, and also
38:43
has the best image gen feature ever made by far, I highly recommend you check out T3 Chat. Only eight bucks a month, and
38:50
you can use GPT 5.4 here. Very happy with it. We also put up a new $50 tier that is practically unlimited use for
38:56
realistic use cases as well as significantly more image gen. I'll leave a link in the description if you want 50% off your first month. But if you
39:03
want to use this for coding, you might have been noticing the app I have been using for this. I want to be clear,
39:10
we're not ready to drop T3 code just yet. Definitely keep an eye on my channel tomorrow, though. But if you
39:15
look really closely at my screen throughout the video, you might notice a
39:20
command you can run to get an early version of the browser version on your own machine. If you want to try things
39:28
out early, I won't prevent you from doing that. Just know that things like your history and which projects you've
39:33
added and such might not make it through the next update. T3 Code requires that you already have codec set up and off on
39:39
your machine. So if you want to try it, make sure you use the codec cli, then give it a go. And of course, you can keep using the codeex app if you want to
39:45
as well, which I totally didn't use for building a bunch of random things in T3 Code. God, that was a long one. I think I've said all I have to about this
39:51
model. Once again, thanks to OpenAI for continuing to let me have early access, even though I've been a little more critical lately. It's kind of nuts doing
39:58
this video right after the one I did yesterday, but I'm trying my best to give you guys the best information I can
40:03
based on all of the things that I know and have access to. This is my honest take on this new model. It is the one
40:08
I'm using every day, but I am still using Opus and Gemini mostly just for UI tidy up stuff. Curious how y'all feel
40:14
though. Is this model as great as I'm saying, or is it kind of mid? Let me know what you think in the comments. And until next time, peace nerds.

## Added Summary
Theo's core claim is that GPT-5.4 (especially the `thinking/high` profile) is now his default "best overall" coding model for serious development work, with better instruction-following, better long-context handling, lower effective reasoning-token usage, and stronger agentic/tool workflows than prior GPT variants. He argues OpenAI is likely collapsing the old model naming split (`Codex` as a model) into product surfaces and capabilities instead of separate dedicated coding models.

He reports that GPT-5.4 is materially better for practical coding and long-running tasks, but not categorically best in every domain. In his testing, `x-high` and `pro` can overthink and sometimes underperform `high` for common engineering workflows, while `pro` still shines on rare, very hard tasks. He also highlights pricing increases and treats them as likely cost-reflective, not just arbitrary markup.

On front-end/UI quality, his conclusion is mixed-to-negative: GPT-5.4 still trails competitors (especially Opus, and in some workflows Gemini) on visual taste, layout quality, and refinement loops. His practical recommendation is model routing by task: GPT-5.4 for most coding/agent flows, other models for UI polish and design-heavy work.

## Added Analysis
The transcript shows a clear pattern: GPT-5.4 is strongest where correctness, steerability, and workflow continuity matter more than aesthetic taste. Theo repeatedly praises interruption handling, long-thread memory, and controlled tool use. That aligns with a "production engineering" value stack: less babysitting, fewer brittle tool calls, and more reliable completion over long horizons.

A second pattern is "capability is tier-sensitive." Theo's own evidence suggests `high` is often the practical sweet spot, while `x-high`/`pro` can add latency/cost without proportional gains on average tasks. This matters for teams: defaulting everyone to the biggest tier may lower ROI. A routing strategy (difficulty-based tiering) is likely better than one-size-fits-all model selection.

Third, the benchmark discussion is nuanced rather than hype-only. He notes wins, but also mismatches between benchmarks and lived results, possible benchmark contamination concerns, and edge-case regressions (for example, prompt injection behavior in function/tool call contexts). That is a healthy takeaway: treat benchmarks as directional, then validate with your own workloads.

Finally, his UI verdict is consistent with many developer reports: coding quality can be near-SOTA while design judgment still lags. In practice, this reinforces a dual-stack approach: use GPT-5.4 for architecture, refactors, migrations, and agent loops; switch to a design-strong model for visual iteration.

## OCR Questions From Image
Extracted text from the pasted image (normalized capitalization and punctuation):

1. What happened to Codex / is it better than Codex?
2. How are the benchmarks?
3. Why did the price go up?
4. How is it to use?
5. Where/how can I use it?
6. Did they fix frontend code?

## Answers To Theo's Questions
1. What happened to Codex / is it better than Codex?
Based on Theo's interpretation, "Codex" is shifting from a separate model identity toward product surface/tooling identity, while GPT-5.4 absorbs many of the coding behaviors that previously justified a dedicated Codex model. In his usage, GPT-5.4 `high` generally replaces older Codex-style defaults for real coding tasks.

2. How are the benchmarks?
Strong overall, but mixed at the margin. Theo cites notable gains across several evaluations and practical tasks, with GPT-5.4 often near the frontier. He also calls out that some benchmark outcomes do not fully match day-to-day engineering experience, and that private/updated tests can change rankings materially.

3. Why did the price go up?
Theo's reading is that higher pricing likely reflects higher serving cost and model/runtime changes rather than a pure pricing grab. He also notes effective cost depends heavily on reasoning profile and token usage behavior; in some real workflows, better token efficiency can partially offset list-price increases.

4. How is it to use?
His experience is very positive for engineering flows: better steerability, better handling of interruptions mid-run, better long-context behavior, and more reliable agent-style execution. He still reports occasional misinterpretation failures and verification misses, so it is not "set and forget" in every case.

5. Where/how can I use it?
Per the transcript: ChatGPT (thinking mode), API-based integrations, coding agents/tools, and third-party apps that expose GPT-5.4. His practical guidance is to use GPT-5.4 as a primary coding/workflow model, then route selectively to other models when the task is visual design-heavy.

6. Did they fix frontend code?
Partially, but not fully. Theo's verdict is that GPT-5.4 improved versus older GPT behavior, yet still lags leading alternatives on UI/visual design quality and refinement. For frontend aesthetics, he still prefers using other models for final polish.

