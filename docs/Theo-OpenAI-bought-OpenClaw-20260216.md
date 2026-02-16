# Theo - OpenAI bought Openclaw
## Link
- https://www.youtube.com/watch?v=nbB8sMmgYok

## Transcript
0:00
Things move absurdly fast in the AI
0:01
world. It's even getting to me at this
0:03
point. It feels like just last week we
0:05
saw OpenClaw getting renamed from
0:06
Cloudbot because Anthropic was upset.
0:08
Wait, that literally was last week. So,
0:11
why are we here now? Things got crazier.
0:13
That's why Peter's now joining OpenAI to
0:15
work on OpenClaw full-time. This is
0:17
huge. Normally, I'd save the fun details
0:20
for later on, but I think it's important
0:21
to know so I don't get accused of
0:23
clickbait. OpenClaw will live in a
0:25
foundation as an open- source project
0:27
that OpenAI will continue to support. So
0:30
again, to be clear, OpenClaw is its own
0:32
separate thing that exists outside of
0:34
OpenAI, but is now being largely funded
0:36
by them. This is a ton of implications
0:38
for the entire industry. Seeing a
0:40
vibecoded side project getting pulled
0:42
into OpenAI in this way, it says a lot
0:45
about how everyone's thinking from
0:46
OpenAI to anthropic to open source
0:48
builders like Pete himself. And of
0:50
course, there's the Lex Friedman
0:51
interview where a lot of this was
0:53
touched on in such a way that we can dig
0:55
into the details. Things like, how much
0:57
money was Peter paid? What other
0:58
companies were interested and why did he
1:00
not go with Meta. There's a ton to dive
1:02
into here and as always, none of these
1:04
companies are paying me, I want to cover
1:05
this to the best of my ability. But
1:07
since I didn't just get bought by
1:08
OpenAI, someone's got to cover the
1:10
bills. We're going to take a quick break
1:11
for today's sponsor. It's never been
1:12
easier to vibe code an app and actually
1:14
get it to prod. There are some catches,
1:15
though. One of the things that's really
1:17
hard to get right is OTH. Unless you're
1:18
using today's sponsor, work OS. These
1:20
guys really get OTH. And it's not just
1:22
like a quick little library you're
1:23
throwing in and praying and hoping for
1:25
the best. It's enterprise ready off. All
1:27
of the integrations that big businesses
1:29
need are covered. That's why everyone
1:30
from OpenAI to Snowflake to Carta to FAL
1:33
to Vercel to Cursor to T3 Chat are all
1:35
using them. work OS just gives us what
1:37
we need to go to big businesses without
1:39
meaningfully compromising on our DX but
1:41
giving us great packages, libraries, and
1:43
integrations into things like React that
1:45
you would normally have to go build
1:46
yourself. And they're not just a sign-in
1:47
button. They go way further than that.
1:49
All of the things you need like
1:50
enterprise SSO as well as an admin
1:52
portal that you can use to onboard big
1:54
companies and their weird IT setups. The
1:56
vault, which lets you handle encrypted
1:57
data for your users. So for us in T3
2:00
Chat, we need a way to store the API
2:01
keys that users bring if they choose to
2:03
bring their own. We use vault to encrypt
2:04
them so we don't have to worry about
2:05
that data anywhere near as much as we
2:07
would otherwise. They even figured out O
2:09
for MCP which is not a trivial thing to
2:11
do. MCP a rough time. They put a lot of
2:14
work into this and I've heard really
2:15
really good things. And just to
2:16
emphasize the enterprise setup part I
2:18
love this quote. With our in-house
2:20
solution, we had to spend 2 to four
2:21
hours provisioning each SSO connection.
2:24
Wanted to find a solution that would
2:25
allow us to focus on building core
2:26
product. Crazy is something that took
2:27
hours of annoying meetings and emails
2:29
could now just be done by sending a
2:30
link. Stop blocking your enterprise
2:32
sales and sign up now at
2:33
soyb.link/workos.
2:35
In order for any of this to make sense,
2:36
we probably need to cover the timeline
2:38
quick. I should have done a Cladbot
2:40
video forever ago. I did do the molt
2:42
book one, which I know y'all loved, but
2:44
Cloudbots changing so fast that it's
2:46
hard to cover because it almost feels
2:48
like by the time I filmed the video, the
2:49
names change twice. The way the setup
2:51
works is entirely different, and you got
2:53
to go a very different direction with
2:54
it. So, that's why I haven't talked
2:56
about it too in depth. But, believe me,
2:58
I have been using it. not for like
3:00
really big projects, but for lots of
3:02
small one-off things. For example, a
3:04
common thing I do is archive videos. If
3:07
there's a video I see on YouTube,
3:08
Twitter, Twitch, or something like
3:09
Actually, before we even get there, I
3:11
just caught myself describing how I use
3:12
Clawbot and remembered a lot of you guys
3:14
might not know about it yet. Cloudbot,
3:15
now known as OpenClaw, is the AI that
3:18
actually does things. What that means is
3:20
you set it up on a computer, probably
3:21
one on your own network that's an actual
3:23
PC you own rather than something that
3:25
you'd put in the cloud. And you give it
3:27
access to things, everything from your
3:29
iMessage to your Gmail to in my case, it
3:31
has access to my NAS, which is my local
3:33
network storage that I keep a lot of
3:35
data, media, and things I do content
3:36
about on the magic of Open Claw is that
3:38
it can do basically anything you can do
3:40
on your computer. And since it's given
3:42
pretty absurd levels of access to your
3:44
machine, there's a lot of fun to be had
3:46
with it. Also, a lot of danger. The
3:48
skill system can do basically anything,
3:50
but that means you have real risks. I've
3:52
had friends accidentally send me 10,000
3:54
texts because they set up OpenClaw
3:56
incorrectly or even if they set it up
3:58
correctly, it went a little bit rogue
3:59
and started spamming me incorrectly.
4:01
These things happen with it. They're
4:03
also now partnering with Virus Total and
4:05
other similar safety based companies to
4:07
try and figure out how to make it as
4:09
safe as possible. the the difference
4:10
from like running in normal mode in
4:12
clawed code where you approve every
4:14
change to running in dangerously skip
4:16
permissions. That gap again is how you
4:19
get to open claw where you're literally
4:21
just letting it do anything it wants.
4:23
There's a reason people love this. Once
4:24
it's set up, you just talk to it through
4:26
WhatsApp, Telegram, or anything. It
4:28
almost feels like you're telling your
4:29
computer what to do remotely. It is
4:31
really cool, but it's also very
4:33
dangerous. But the feeling of letting
4:35
your computer be controlled this way is
4:36
powerful. Which is why OpenClaw is now
4:39
the fastest growing GitHub project of
4:41
all time. It now has more stars than
4:43
Nex.js. And it got there in a bit over a
4:45
month. Wild. It's beating out
4:47
Kubernetes. It's beating out Vit. It's
4:49
beating out Bun. It's over halfway the
4:52
way to React stars on GitHub. Pretty
4:54
nuts. I was also lucky enough to
4:56
interview Pete, the creator of OpenClaw,
4:57
at the first ever Claw Con in the city
4:59
just a few weeks ago. It's crazy. This
5:01
was on the 4th and it's now the 15th.
5:03
It's been 11 days and this has all
5:05
happened in that time. In this interview
5:07
we did, Pete called me his first fan,
5:10
which is such a high honor. I've been a
5:12
huge fan of his work since the old PSPDF
5:14
kit days, which is his previous project
5:16
before retiring for a bit and then
5:17
coming back for all of this. But when I
5:19
saw the way he thought about AI code, I
5:21
was really impressed. This might be the
5:23
GitHub page that has come up the most in
5:24
my videos recently. Do you see the
5:27
number of insane projects this guy is
5:29
working on? This is because he's found
5:31
the right ways to use these AI tools to
5:33
be productive. But unlike most of us
5:35
that just let these projects die on our
5:37
computer, he actually ships. And that's
5:39
why OpenClaw happened. People seem to
5:40
think like, "Oh, you could have been the
5:42
one to invent OpenClaw." Yeah, you could
5:43
have if you rolled the dice this many
5:45
times first. You got to be realistic
5:47
about it. Like he got here because he
5:49
built a ton of awesome stuff and also
5:51
documented the way he thought about
5:52
building. Pete is the real story here.
5:55
Open Claw is awesome, but Pete's way of
5:57
building is even more awesome. He has so
5:59
many pro tips, many of which I'm still
6:01
working on internalizing. Like the way
6:02
he handles multiple projects, the fact
6:04
that instead of doing multiple things in
6:06
the same project at the same time, he
6:07
uses the queuing feature heavily. He
6:09
never reverts or uses checkpointing. He
6:11
always just commits straight to main.
6:13
All of his ways of building are
6:15
fascinating, but they are so powerful
6:17
once you lean into them. Like this is
6:19
the chaos of how he works at home. All
6:21
of these terminals all running codecs.
6:23
To be clear, he does like Opus as a
6:26
general purpose model, but not as a
6:28
daily driver for coding. He's a big
6:29
Codeex guy. He beat us all to it. He's
6:31
the reason I started using it more
6:32
heavily, too. So, credit where it's due.
6:34
He was way ahead of the curve with a lot
6:35
of these things and more, which is a big
6:37
part of why he could figure something
6:39
like Claudebot out. He was pushing the
6:41
limits of these models. A lot of that
6:42
came from the fact that he had a 5-year
6:45
hiatus before getting more into this AI
6:47
code stuff. He built a business that was
6:49
making it easier to manage PDFs on iOS.
6:51
That went really well. He sold the
6:53
shares, retired for a few years, like
6:54
five plus, where he said he barely even
6:56
used a computer. And when he came back,
6:58
he got to skip the whole co-pilot era.
7:00
He got to skip the autocomplete era. He
7:01
got to skip all of that and come in
7:03
right as the models were getting really
7:05
good and was more willing to lean into
7:07
it than most. And that's how you got
7:08
where he did. And Cloudbot was meant to
7:11
be a small one-off thing. It was
7:13
originally a rapper for using Cloud Code
7:15
via WhatsApp, so he could control a bit
7:17
of his computer over a WhatsApp DM. And
7:19
it went way further than he expected.
7:20
Someone filed the Discord PR to add
7:22
support there. He decided to make it a
7:24
little more generic and support more
7:25
different things. And Claudebot has just
7:27
went absurdly far since. Then everyone's
7:31
favorite comes in, anthropic. You'd
7:33
think that since Claudebot is leaning so
7:35
heavily into Claude, because even this
7:38
guy Pete, who loves the Codex models,
7:41
prefers using Claude models, prefers
7:42
using Opus for Claudebot. You'd think
7:44
Anthropic would be hyped. But the first
7:46
contact he got from Anthropic was not
7:48
from Anthropic like employees. It was
7:50
from Anthropic's lawyers because they
7:53
saw this as a violation of their
7:54
trademark. Not only did Anthropic push
7:56
really hard to make him move the name
7:58
and stop using Claude even though it was
8:00
spelled differently and is clearly not
8:01
Anthropic, they made him give them the
8:04
domains. So when he changed names, which
8:06
he had to do very quickly, in fact, I
8:08
should probably include the temp name
8:10
here, Moltbot, he was so pressured that
8:11
he had to rush out the release to change
8:13
it over to Moltbot. Had a lot of the
8:15
Clawbot like handles and things get
8:16
sniped under him as a result, too. All
8:18
because Anthropic was putting the
8:19
pressure on saying you need to change
8:20
this. Now, this is kind of Anthropic's
8:23
MO though. Like, we'll talk more about
8:25
Anthropic versus OpenAI and why one
8:27
would pick Open AAI, but remember this,
8:29
Anthropic's lawyers were the ones he was
8:31
talking to. So, he renames the Maltbot.
8:33
He doesn't love the name. It was just
8:34
the first thing he had that was
8:36
available in multiple places. Went okay.
8:39
But then he snagged OpenClaw. At this
8:40
point, he had connections with everybody
8:42
at Twitter, on GitHub, and things like
8:43
that. So, he could do the handle swap a
8:45
little more smoothly. And then he did a
8:47
bold thing. He called Sam Alman to ask
8:50
about the name. He wanted to make sure
8:51
that OpenAI would be okay with the Open
8:54
Claw name. They were. And I suspect that
8:57
the talking did not stop there, that it
8:59
continued since, which would make this
9:02
last step make a lot more sense. Peter
9:04
Steinberger is joining OpenAI to drive
9:06
the next generation of personal agents.
9:08
He is a genius with a lot of amazing
9:10
ideas about the future of very smart
9:12
agents interacting with each other to do
9:13
very useful things for people. We expect
9:15
this will quickly become core to our
9:16
product offerings. Openclaw will live in
9:18
a foundation as an open-source project
9:20
that OpenAI will continue to support.
9:22
The future is going to be extremely
9:23
multi- aent and it's important to us to
9:26
support open source as a part of that
9:28
huge. So let's talk about why he would
9:31
go to OpenAI. I haven't read his
9:33
official announcement post yet. We'll do
9:35
that after. So make sure you stick
9:37
around so we can see this. First I want
9:38
to talk about my theories. the options
9:41
like the realistic ones were anthropic,
9:44
open AAI and meta. I'm going to focus
9:46
more so on these two for now. We'll talk
9:48
about meta in a bit. Another important
9:50
thing to know is that Pete doesn't
9:52
really need money. He's been comfortably
9:54
funding all of the dev server costs, all
9:56
of the everything for OpenClaw for a
9:59
bit. I think he was at like 12K a month
10:00
or so. So Pete doesn't need the money.
10:02
We've established that. He had his exit
10:04
from his previous startup. He was
10:05
funding everything fine. So this isn't
10:07
just about like who will pay more, who
10:09
will buy the thing for more because he
10:10
also doesn't want to sell it. He's
10:12
looking for as much stability as
10:14
possible going forward. If he's part of
10:16
something like OpenAI or Anthropic, then
10:18
the legal chaos when one of these
10:20
companies, I I won't say which starts
10:22
sending love letters from legal to him,
10:25
that type of thing is really stressful
10:27
and he doesn't want to deal with it.
10:28
This is one of the best benefits of
10:30
working at a company. There are so many
10:32
things you don't have to deal with. You
10:33
don't have to manage payroll. You don't
10:35
have to worry about equity management
10:37
and like how people are getting paid and
10:38
what their compensation looks like. You
10:40
don't have to worry about having and
10:41
retaining a legal team for when [ __ ]
10:42
like this occurs. Open AI is able to
10:45
provide a lot of the comfort that you
10:46
would need to comfortably work on a
10:48
thing like this. It also means you don't
10:49
have to worry about hundreds of
10:51
investors coming in trying to get you to
10:52
start a company or make a foundation or
10:54
join another company and sell it or all
10:56
of those things. It just it reduces all
10:58
of the problem area and lets him do what
11:00
he wants which is lock in and build the
11:02
thing. So, let's talk a bit about other
11:05
differences with Anthropic and OpenAI.
11:07
The first thing that stands out to me is
11:09
uh some of their open- source
11:11
philosophy. OpenAI has fully open
11:13
sourced the codec CLI and not just like
11:16
traditional open-source like source
11:18
available or even just MIT. It is Apache
11:21
licensed so you can do whatever you want
11:23
to it versus Anthropic who has sent more
11:26
DMCA requests than any other company on
11:30
GitHub. Anthropic accidentally included
11:32
the source maps inside of Cloud Code in
11:35
an early release and everybody who
11:37
published those publicly available
11:39
source maps got DMCAD by Enthropic and
11:42
had the repos removed from GitHub.
11:44
Traditionally, it is impossible to
11:46
reverse a publication on npm. Once it is
11:48
published, it's there forever because
11:50
depend on it because it's included in
11:51
dependency trees. One of the dozen or so
11:54
times ever we've had a package fully
11:55
removed for a reason other than malware
11:57
was this. Thankfully, GitHub makes all
11:59
of their DMCA requests public, so you
12:01
can go see a lot of these here. I
12:03
definitely thought it was more than
12:04
this, but they usually link a ton of
12:05
different repos for every report. GitHub
12:08
now autoblocks them. It was a big deal.
12:10
I've seen so many people get hit with
12:11
the DMCAS from Anthropic for publishing
12:13
source code that they publish
12:15
themselves. So, one example here. Then
12:17
we have how they treat the subscriptions
12:20
that they provide. So, Anthropic has the
12:22
$200 a month cloud code sub and OpenAI
12:25
has the $200 a month codeex sub. It's
12:27
like OpenAI Pro Plus or whatever, but
12:29
you can use it for Codex is what I'm
12:30
using for Codeex. Anthropic stance on
12:32
this is that subs are only for their
12:36
software hard ban otherwise. I've seen
12:39
so many people posting that their Cloud
12:40
Code account got banned because they did
12:42
anything other than using the Cloud Code
12:44
CLI. They even hard-coded open code as a
12:47
banned term. So, if any of your headers
12:50
when you're using the Cloud Code sub
12:51
mention open code, it just rejects at
12:54
the API endpoint now, which is insane.
12:56
Whereas OpenAI contributes to Open Code
12:58
and other harnesses and has helped them
12:59
set up codec subscriptions within those
13:02
harnesses. So you can use your OpenAI
13:04
codec sub in things like Open Code or
13:06
even in GitHub Copilot. Anthropic really
13:08
wants to treat the sub as a way to be
13:10
locked into their product, not just a
13:12
way to access their models for a
13:14
discount. OpenAI is taking the
13:16
opportunity to make their models and
13:18
their subscription service way more
13:20
appealing by not locking you into their
13:22
stuff. You're hopefully noticing a
13:24
pattern here. OpenAI keeps picking up
13:27
the opportunities that Anthropic is
13:28
dropping. Anthropic does something
13:30
shitty around source code. OpenAI
13:32
releases theirs fully open. Anthropic
13:34
does something shitty with their
13:35
subscriptions. OpenAI helps out
13:37
competitors with using their
13:38
subscriptions so that they can come out
13:40
on top. There is also the open-source
13:42
angles from these companies as a whole.
13:44
OpenAI has open sourced a ton of stuff,
13:46
especially lately. They have their
13:47
openweight models. They have the harmony
13:49
response format. They now have the full
13:50
responses API format that is open source
13:53
as well that I hope more and more people
13:54
adopt as an open standard. Anthropic has
13:57
MCP and they bought Bun. It's about it.
14:00
And now we have what we're all here for
14:02
today. Anthropic contacted Claudebot via
14:06
lawyers. Whereas with OpenAI, Pete has
14:08
Sam's phone number. Hopefully you see
14:11
why one of these is a much more obvious
14:13
choice. Antho is the only company that's
14:15
unwilling to standardize on things like
14:16
the agentmd file and a standard way to
14:19
hold skills for your agents where
14:21
everything has to be the claude file or
14:22
the claude directory. To this day, in a
14:25
handful of my projects, I have to sim
14:27
link cla.md to agents MD so this one
14:31
thing can continue to handle things its
14:33
way. Whereas with OpenAI, they are now
14:36
moving everything to agents MD, which is
14:38
great. So with this all in mind, as well
14:40
as the fact that he finds OpenAI's code
14:43
models to be better at coding than
14:44
Anthropics models that are focused on
14:46
coding, makes a lot of sense why OpenAI
14:48
would be the position that he wants to
14:50
be in in the place he wants to go. This
14:52
is a company that was threatening his
14:53
mere existence. This is a company that
14:55
is meaningfully encouraging his growth
14:56
and success. Hopefully you guys are all
14:58
starting to see a little bit of why I've
15:00
been so harsh on Anthropic and so kind
15:02
to OpenAI. OpenAI feels like a much
15:04
better player in the space. I have not
15:06
gotten bad vibes from them in all the
15:08
time I've interacted with them. Half the
15:10
time I interact with Anthropic,
15:11
something weird is going on. Even when
15:13
I'm talking to employees that are like,
15:14
"Yeah, this sucks. It's just how we do
15:15
it." Yeah, I've been saying Anthropic's
15:17
bad faith for a while and I'm happy
15:18
people are finally catching on to this
15:20
fact. Like it's it sucks cuz they have
15:22
great models. They have great culture.
15:24
They have a great team, but they are
15:26
just too in their like their head is
15:28
just too deep up their own [ __ ] ass
15:30
to do the right thing. And OpenAI is
15:32
more than happy to take that
15:33
opportunity. And they certainly
15:35
certainly are. Someone just linked this
15:37
video from six months ago. Anthropic has
15:39
weird vibes. I got flamed for this one.
15:42
When I talked about this six months ago,
15:45
70% likes, which means 30% dislikes when
15:49
my channel averages 95%.
15:52
People were so mad at me for daring to
15:55
speak up against our benevolent saviors
15:58
at Anthropic. Thankfully, you're all
16:00
over it cuz I was [ __ ] right. But god
16:02
damn, like Anthropic's behavior has
16:04
gotten so much worse. And I warned you
16:05
all. I'm so thankful people are
16:06
listening and noticing it now. But I was
16:09
fully correct on that and I stand behind
16:10
every [ __ ] word. Yeah, cool.
16:12
Anthropic is going to kill themselves if
16:14
they don't get over their [ __ ] and start
16:16
behaving kindly in the space. And as
16:18
always, you guys can take my advice. I'm
16:20
not far from the office. I'm happy to
16:21
come in and explain how to fix this. You
16:23
open source Claude code. You stop being
16:25
weird on [ __ ] Twitter. And you
16:26
acknowledge the fact that other models
16:27
exist and are decent. It's not that
16:29
hard. It's really not. Also, stop with
16:32
the cancelling of access. It is so
16:33
strange that Anthropic goes out of their
16:35
way to cancel access to their models
16:37
from other companies they see as
16:38
competitors. Everyone from Wind Surf to
16:41
OpenAI to XAI just for like running
16:44
benchmarks even like OpenAI cannot run
16:46
benchmarks against anthropic models cuz
16:47
they're banned from using them.
16:49
Meanwhile, I know a ton of Anthropic
16:51
employees that personally maintain the
16:52
$200 a month codec sub and use it. It's
16:55
insane. It's actually [ __ ] insane.
16:59
Yeah. So anthropic was never an option
17:01
here. Open AI was clearly a better
17:03
choice for Pete. But they were not the
17:05
only choice. Meta was too. And Meta has
17:08
their own benefits. Open source models,
17:11
open source lineage, I would argue,
17:12
where so much of Meta's work has been
17:14
open source for a while. Huge projects
17:16
like React and React Native that they've
17:18
maintained forever now. Super important.
17:20
They've been really good about that
17:21
overall. I would be surprised if it
17:22
wasn't the case that Meta was willing to
17:24
pay more, especially after seeing some
17:25
of the crazy acquisitions that Meta has
17:27
made. But chances are this really just
17:29
came down to vibes and Pete had much
17:31
better vibes from OpenAI. And I can say
17:33
personally speaking, the vibes at OpenAI
17:35
are great. Like I know it doesn't seem
17:37
that externally and I understand how
17:39
jarring it is to see the difference
17:40
between like the weird things that
17:42
OpenAI has said on their Twitter account
17:44
and the many misinterpretations of what
17:47
Sam has said on Twitter and the the
17:49
jarring gap between that and the
17:51
perspective most people have to like how
17:54
I and the others who have worked with
17:56
and got early access to OpenAI stuff
17:58
feel. They're just so real. I've never
18:00
had a conversation with an OpenAI
18:02
employee that felt like they were hiding
18:04
something from me or there was something
18:06
that they would get in trouble if they
18:07
said. I've had many an OpenAI employee
18:09
say something that I would expect to
18:11
have gotten them in trouble at almost
18:13
any other company to the point where it
18:15
shocked me. I once had a point where I
18:16
thought an OpenAI employees Twitter
18:18
account was hacked because they were
18:19
being so upfront with me about stuff
18:20
over Twitter. They're really, really
18:22
good about this. Being transparent with
18:24
the people who cover your [ __ ] and use
18:26
your [ __ ] publicly is such a huge win.
18:29
Enthropic does not do that at all. So
18:31
many strings had to be pulled to get me
18:32
a little bit of early access to some
18:33
cloud code stuff. Whereas OpenAI treats
18:36
their collaborators great. Be it as a
18:38
business customer or as a public
18:40
representative or in this case a
18:41
potential collaborator like Pete, OpenAI
18:44
treats people well. And as always, we
18:46
got the stupid comments, bro is paid by
18:48
OpenAI. To anybody who thinks that I am
18:51
actually being paid by OpenAI, here's
18:53
the deal. I'll make this easy for you.
18:56
Prove it. If you do, I will pay you
18:59
every single scent OpenAI has paid me.
19:01
And if you don't, all I will charge you
19:03
is one month of my OpenAI fees on the
19:06
OpenAI API. I currently pay OpenAI
19:08
between 20 and $50,000 a month. They
19:10
have paid me zero. I refused the single
19:12
offer they gave me of a $1,000
19:14
appearance fee for a video. I declined
19:16
it. OpenAI has never sent a scent to any
19:18
of my bank accounts. If you can prove
19:20
otherwise, not only are you going to get
19:22
all of that money for yourself, I'm also
19:24
going to go to jail because it's against
19:25
the law. The reality is honestly kind of
19:27
funnier. I'm nice to OpenAI because
19:29
OpenAI is nice to me. I say nice things
19:31
about OpenAI's products because OpenAI's
19:33
products are good. I also talk [ __ ] on
19:35
OpenAI's products when I don't think
19:36
they're that good. I talk so much [ __ ]
19:38
on Atlas that it's crazy to me anyone
19:40
would say that I'm being paid. Like,
19:41
it's actually absurd. But yeah, OpenAI
19:43
is genuinely a great collaborator. I've
19:45
had an awesome time working with them.
19:46
They've been really transparent, really
19:48
thorough, really kind. Just stupid
19:50
things like, "I want my team to have
19:51
early access to so we can evaluate stuff
19:53
together." So, I just DM them and they
19:56
do it. It's silly that this matters so
19:58
much, but it does. They are nice to
20:00
interact with. And in the end, that is
20:02
what ends up mattering. Everybody's
20:04
going to over analyze things like,
20:05
"What's the strategy? How much money is
20:06
this work? Why does he go here? Does he
20:08
think the models are that much better?
20:10
He's going to get paid more? That the
20:11
long-term he's going to have a higher
20:12
return?" No. None of that is why he made
20:15
the decision he made. He made the
20:16
decision because he wants to go
20:18
somewhere that people will be out of his
20:19
way and he can work on the things he's
20:21
excited about. The place you work is
20:23
more than the place that pays you. This
20:24
is the culture you live within.
20:26
Especially if you're one of those people
20:27
that likes to work 10-hour days, six
20:28
days a week. You want to be the place
20:30
where you have the best vibes. And
20:32
OpenAI of the options he had has by far
20:34
the best vibes. So, let's see what Pete
20:36
had to say because again, remember all
20:38
this was my speculation. I have a
20:40
feeling that we'll be aligned here cuz
20:41
Pete's now become a decently close
20:43
friend. I love this command to death.
20:44
I'm so hyped for everything he has been
20:45
doing. Let's see what he has to say. I'm
20:47
joining OpenAI to work on bringing
20:48
agents to everyone. OpenClaw will move
20:50
to a foundation and stay open and
20:51
independent. This is interesting. This
20:53
seems to imply that his role at OpenAI
20:55
won't just be OpenClaw. It is likely he
20:57
will be building something like Open
20:58
Claw internally for OpenAI that will
21:00
eventually become its own product. That
21:02
is how I read this to an extent. I'm
21:03
sure you'll still help with it a lot,
21:05
but interesting. The last month was a
21:07
whirlwind. Never would I have expected
21:08
that my playground project would create
21:09
such waves. The internet got weird again
21:11
and it's been incredibly fun to see how
21:13
my work inspired so many people around
21:14
the world. There's an endless array of
21:16
possibilities that opened up for me.
21:18
countless people trying to push me into
21:19
various directions, giving me advice,
21:21
asking how they can invest or what I
21:22
will do. Saying it's overwhelming is an
21:24
understatement. Having talked to him
21:26
during this time, Ken confirmed, "Poor
21:28
guy was going through it." When I
21:29
started exploring AI, my goal is to have
21:31
fun and inspire people. And here we are.
21:33
The lobster is taking over the world. My
21:35
next mission is to build an agent that
21:37
even my mom can use. That'll need much
21:38
broader change, a lot more thought on
21:40
how to do it safely, and access to the
21:42
very latest models and research. Okay,
21:44
so he is going to build something
21:45
different. Confirmed. Yes, I could
21:47
totally see how OpenC could become a
21:48
huge company and no, it's not really
21:50
exciting for me. I'm a builder at heart.
21:52
I did the whole creating a company game
21:54
already, poured 13 years of my life into
21:56
it and learned a lot. What I want is to
21:58
change the world, not to build a large
21:59
company. And teaming up with OpenAI is
22:01
the fastest way to bring this to
22:02
everyone. Yep, there it is. The key. As
22:04
someone who's also running a company, it
22:06
[ __ ] sucks. You'll never have less
22:08
freedom than you do when running a
22:10
business. Everyone seems to think
22:11
becoming a CEO of a ventureback company
22:13
means you get all the freedom in the
22:14
world. They're lying to you. every
22:16
minute of every day, I am not doing
22:18
things I should be that I'm obligated to
22:20
do and I'm holding back my team and I'm
22:21
screwing over my investors and it sucks
22:23
and I work really hard to balance it out
22:24
by getting us the best distribution in
22:26
the world and doing everything I can to
22:28
make the business successful. Running a
22:29
company is [ __ ] exhausting,
22:31
especially when you'd rather run a
22:32
product. Pete spent the last week in San
22:34
Francisco talking with the major labs,
22:35
getting access to people and unreleased
22:37
research, and it's been inspiring on all
22:38
fronts. He wants to thank the folks that
22:40
he talked to this week, and he's
22:41
thankful for the opportunities. It's
22:42
always been important to him that
22:44
OpenClaw stays open source and is given
22:46
the freedom to flourish. Ultimately, he
22:47
felt that OpenAI was the best place to
22:49
continue pushing his vision and
22:51
expanding its reach. The more he talked
22:53
to the people there, the clear it became
22:55
that they both share the same vision.
22:56
The community around OpenClaw is
22:58
something magical, and OpenAI has made
23:00
strong commitments to enable him to
23:01
dedicate his time to it and already
23:03
sponsors the project. To get this into a
23:05
proper structure, he's working on making
23:06
it a foundation. It will stay a place
23:08
for thinkers, hackers, and people that
23:09
want a way to own their data with the
23:11
goal of supporting even more models and
23:13
companies. Personally, he's excited to
23:14
join OpenAI, be part of the frontier of
23:16
AI research and development, and
23:17
continue building with all of us. The
23:19
claw is the law with a photo from the
23:20
Open Claw meetup confirms a lot of the
23:22
things I was thinking. Crazy to think
23:24
that he's going to be building something
23:25
different now, but I'm so excited to see
23:27
what that is. To anybody who feels like
23:29
engineering is dead or that like the
23:31
future is just these small number of big
23:34
companies running everything, I hope
23:35
this helps prove the opposite. Open Claw
23:38
was so big that the labs couldn't clone
23:40
it. They couldn't just do their own
23:42
alternative. They couldn't kill it. Even
23:43
though, believe me, Anthropic definitely
23:45
tried. The movements that are created by
23:48
these tools are still bigger than the
23:50
companies building them. And Claudebot,
23:52
well, OpenClaw had taken a life of its
23:54
own and went so far that OpenAI had to
23:57
pay him what is almost certainly a crazy
23:59
salary with crazy equity in order to go
24:01
there to build what could very well be
24:03
the future of how people interact with
24:05
AI. This is just another bet for OpenAI.
24:07
They have a bunch of these different
24:08
bets. This one is big, but this one is
24:11
another bet. I'm excited to see where it
24:13
goes, but more importantly, I'm just
24:15
excited to see Pete win. This is
24:16
somebody who showed up late, didn't let
24:19
that slow him down. If anything, it sped
24:21
him up. And as a result, he got to build
24:23
incredible things. He didn't let
24:24
anything get in his way. I've never seen
24:27
somebody who was so consistently able to
24:29
just fix the thing and ship the thing.
24:31
And if anyone deserves to win in this
24:32
space, it is Pete. He has set a
24:35
phenomenal example for future builders
24:36
and future inspired developers in this
24:38
crazy AIdriven world. And I really do
24:41
hope this story can inspire some hope in
24:43
all of you. In the end, nothing matters
24:45
more than what you ship and how you show
24:47
it off. So keep building cool [ __ ] And
24:49
maybe, just maybe, you'll get to change
24:50
the world like Peter did. This was such
24:52
a cool story and I'm thankful I got to
24:53
be part of it as small as my part was.
24:55
One last shout out to Peter for all he
24:57
has done. It's so cool to see this win.
24:59
And until next time, keep playing with
25:01
Cloudbot and maybe, just maybe,
25:02
compromise your network to see what the
25:04
future looks like. Until next time,
25:06
peace nerds.

## Summary
In this video, Theo covers the major news that Peter Steinberger, creator of **OpenClaw** (formerly Cloudbot), has joined **OpenAI**. 
- **The Acquisition**: OpenClaw will move to a foundation as an open-source project supported by OpenAI. Peter is not "selling" it in a traditional sense but joining OpenAI to build the next generation of personal agents ("an agent even my mom can use").
- **Growth**: OpenClaw became the fastest-growing GitHub project of all time, surpassing Next.js and Kubernetes in star count velocity.
- **Anthropic vs. OpenAI**: Theo contrasts the two companies heavily:
    - **Anthropic**: Sent lawyers to issue trademark disputes over the "Claude" name, leading to the rename to OpenClaw. Criticized for aggressive DMCA takedowns and banning user accounts for using competitive models.
    - **OpenAI**: Sam Altman personally approved the "OpenClaw" name. OpenAI is praised for better developer relations, open-sourcing tools (Codex CLI), and supporting the ecosystem.
- **Motivation**: Peter joined OpenAI to escape the administrative burden of running a company (payroll, legal, investors) and focus purely on building, while gaining access to unreleased research and "stability."

**Advertisement (1:10 - 2:33)**: 
The video features a sponsored segment for **WorkOS** (soyb.link/workos), promoting their enterprise-ready authentication (SSO, Vault for API keys) and their support for MCP (Model Context Protocol).

## Analysis
- The video discusses Peter Steinberger's journey in the AI space, particularly his work on OpenClaw and his recent move to OpenAI.
- **Impact on RoadTrip**: 
    - **Validation of Vision**: The move confirms that "personal agents" are the next major frontier for big labs (OpenAI). RoadTrip's goal of a "self-improving personal assistant" is directly aligned with where the industry capital is flowing.
    - **Security Philosophy Divergence**: The transcript highlights OpenClaw's "vibecoded" and "dangerous" nature (running with god-mode permissions on a local machine). In contrast, RoadTrip's architecture is built on **Zero Trust** and **IBAC** (Identity-Based Access Control). As OpenClaw normalizes "risky" agents, RoadTrip's value proposition shifts to being the "secure, grown-up" alternative.
    - **Standardization**: The transcript mentions OpenClaw/OpenAI moving towards standardizing agent definitions (e.g., `agent.md`). RoadTrip should monitor these standards to ensure interoperability, rather than inventing custom metadata formats if a standard emerges.
    - **Market Position**: "Big fish swallowing little fish" typically reduces diversity, but here it might create a "standard" (OpenClaw) vs. "bespoke" (RoadTrip) dynamic. RoadTrip does not need to compete on "vibes" or viral growth, but on **reliability** and **long-term memory** (which OpenClaw lacks, focusing mostly on execution).
    - **Conclusion**: **No real negative impact.** If anything, it highlights the need for RoadTrip's "System 2" (deliberative/safe) approach versus OpenClaw's "System 1" (impulsive/action-oriented) default.