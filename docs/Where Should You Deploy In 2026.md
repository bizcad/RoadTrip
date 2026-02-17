# Where Should You Deploy In 2026?
## Links
- https://www.youtube.com/watch?v=yfxDdQo2cyI

## Transcript

0:00
Today's video is going to be a bit different because I wasn't actually filming this video when I filmed most of this video. I know that sounds crazy,
0:06
but just hear me out for a sec. I was just filming a video about the death of Heroku. You might have even seen it
0:11
already. And that video ended up with a long tangent about various other alternatives that you might consider
0:16
moving to. Everything from AWS to Vercel, Railway, Netlify, Render,
0:21
Cloudflare, Digital Ocean, Heroku, Fly.io, and more. I wanted to do my best to break all of these options down and
0:27
share how I think about them and how I choose where I deploy my applications. While I have been sponsored by many of
0:33
these companies in the past, none of them are sponsoring this video. The point of this was to give you my honest take on how I choose where I deploy my
0:40
services. It can feel a little overwhelming to choose and a lot of the advice I see around the internet feels
0:46
like it's coming a little bit too much out of the perspective of the user and the specific thing they are working on
0:52
in that moment where all of these platforms, okay, most of these platforms have real benefits that are worth
0:57
considering. There are at least three options on each side here that are worth thinking about and evaluating before
1:04
making a decision. And this video isn't just like this one's good and this one's bad. I'm trying to help you make a
1:09
mental mapping and model for how to choose the right place to host your code. And in a world where we're
1:14
deploying more and more services, making all these micro apps, and vibe coding all sorts of stuff, no one's helping you
1:20
figure out where to put it. And if I keep seeing these crazy Vercel bills or people getting stuck trying to deploy on
1:26
AWS, I'm going to go mad. I really want to help you guys understand how I pick solutions. And it's not based on who's
1:32
paying me. None of these companies are paying me today. The only one who is is today's sponsor. I have a confession to
1:37
make. I've stopped using GitHub for CI because today's sponsor, Blacksmith, has made my CI so much better. Actions just
1:44
aren't reliable, and I've had so many problems with them. And they all vanished as soon as I set up Blacksmith for all of our repos. And yes, I mean
1:50
all of them. Looks like we even have jobs running right now. Honestly, all of the observability stuff would be worth it by itself. Actually seeing what
1:56
failed and why and having a log search that like works. If you've ever had to debug weird actions, you know how
2:02
absurdly useful this is by itself. It is not just for individual projects. You can scan all of your projects as well,
2:08
which is huge. But the real key is the fastest part because they really are the fastest. The secret to how they're so
2:13
fast isn't really that secret. They're using better hardware with gaming CPUs as well as NVME drives that store all of
2:19
your layers for things like Docker, which allows the restoration process to be instantaneous instead of taking forever. I just moved some actions for a
2:26
Rust project I'm working on, and they went from 5 minutes to under 30 seconds. We've seen similar speedups across all
2:31
of the projects that we're working on. Other companies like Ashb doubled their deployment speeds while also cutting their spend by 75%. Because yes,
2:38
Blacksmith's cheaper, too. Don't believe me? Try it yourself. It's free to get started and it's one line of code
2:43
changed. Yes, really. You swap the action. Once you're set up, it's good to go. Stop wasting your time and speed up
2:48
your builds at soyv.link/blacksmith. I'll break this into servers and serverless. You know, we'll call it
2:53
VPS's and serverless. There's a lot of good options for both. In the serverless
2:59
side, obviously Verscell is still inarguably king. The balance of DX and capability of the platform is pretty
3:05
hard to beat. Nellifi is not a bad option, especially with their recent embrace of vibe coding and supporting
3:10
all of the platforms that build all the fancy vioding tools. Scales great. I love the CEO. Really good. Has it
3:16
negatives. We'll get there. And then we have Cloudflare. A lot of things to say about that. On the VPS side, we have a
3:21
ton of options. Obviously, we can go AWS with EC2 or EKS. Lots of options there.
3:28
Railway, which I've already talked about. You have render fly.io. Yeah, digital ocean. Another crazy throwback.
3:35
Man, I have digital ocean. I have a long ass history. Oh, yeah. Hner, the classic. That's the one I was
3:40
forgetting. Obviously, there's other traditional clouds like GCP, Azure. The reality is that if either of these are
3:46
the right solution to your problem, you already know that and you're not here for me to tell you about different options. There's also OVH. None of the
3:53
rest are things I care about enough to put in the list. I think this is a good enough list of the VPS's. I'm going to
3:58
start by diving into the serverless list here. If you don't know which of these you fit under, you should almost
4:04
certainly start with the serverless options and if they have issues because you actually do end up meeting a server,
4:09
you'll figure that out pretty fast and then you'll move over accordingly. But generally speaking, 98 plus% of
4:15
applications can be served totally fine in a serverless deployment solution. I would lean in that direction. So that's
4:20
being a fair point that AWS Lambda should also be in here. You're not wrong, but we're not going to be talking
4:26
about that one too much. Let's break down all these options and how I pick between them. I honestly think this will
4:32
be easier if we go backwards. So, let's start with AWS Lambda. Lambda is not
4:37
trivial to set up. There are lots of tools to help like SST, Palumi, Terraform, things like that. It still
4:43
sucks. Concurrency is not viable. They are starting to introduce their concept of doing concurrent Lambda stuff.
4:49
They're not there yet. I don't know anyone who's actually using it or relying on it. Then they have like amplify which is a total joke. Yeah. CDN
4:57
gateway is your problem. Git push pipeline GHF costs are fine but
5:04
concurrency sucks. Yeah. It's hard to recommend Lambda to most people. At
5:09
least it's Node though or anything else. If you can put in a Docker image, you can put it on Lambda. But a lot of technologies that people like tend to be
5:16
slow to spin up. So don't think you can just rewrite your Lambda in Rust and it's magically super fast. Sometimes
5:23
those things take a bit to boot, especially if your wait time isn't on the startup of your code. It's actually on the connection to your database. Good
5:29
luck. Have fun. There's also a lot of other little things like streaming with super broken Lambda. I think it might be fixed now. I'm not sure, but if you're
5:35
using a server component style framework that does HTTP streaming like you know, Nex.js, not fun. And next we have
5:42
everyone's favorite CloudFlare. First thing I want to say is that they have one of a kind infra. And that one of a
5:47
kind infra allows them to be significantly cheaper than almost anything else because Cloudflare isn't
5:52
using traditional servers or Docker images. You can't send a Docker image to Cloudflare and run it. Well, you kind of
5:59
can now, but their whole like Docker image server thing is a different product and it sucks. I don't anyone using it. It's super overpriced and
6:04
slow. Cloudflare's strength is you give them a JavaScript file and they run it on their edge network that has a
6:10
different layer of abstraction. Instead of handing them a box with a kernel in it and expecting them to run it for you,
6:15
you're handing them a JS file and three layers above the kernel in their custom version of V8 called workerd, they run
6:22
your code safely in an isolate that doesn't have to spin up a whole server the way that things like Lambda do. That
6:27
means that cold starts are near zero. It means that their pricing model is fundamentally different because they only charge on CPU time. Other platforms
6:34
charge wall clock time because the server's up. It doesn't matter how people are using it. It costs them
6:39
money, it costs you money, too. With Cloudflare, if your request isn't doing anything, like it's idling, waiting for
6:45
more data to come in, the compute on that box can be used for someone else's request because lots of people are
6:51
running their code at the same time on the same box. On Verscell, every developer's deployment has its own kernel. On Cloudflare, every single
6:58
deployment is just a JavaScript file running in the same VM. It also changes their performance profile meaningly.
7:03
Check out the Verscell versus Cloudflare video if you want more info on that. They've made improvements since, but it's still not as fast as dedicated box
7:09
can be. But there's a much bigger catch. Not Node. Every time I use Cloudflare, I
7:14
run into something because of this. It's not running Node.js. It's running their JavaScript engine. And because of that,
7:20
a lot of things don't work. Things like reading and writing files, things like
7:25
many of the methods you use to connect to databases, things like any package that runs any native code, you know,
7:32
like image optimizers, PDF parsing, all the fun things we like to do in our servers with our node apps. There's a
7:39
lot of issues when you can't use node. They've done their best to patch in support for a lot of node stuff. None of
7:46
the things I just mentioned have been fixed. All of those are still problems, but most packages have shims around the node functions now built in where they
7:53
can mostly work. Things like crypto were entirely broken and now mostly work. The compat layers fine, but you're almost
8:00
certainly going to run into some issues. Like one of the biggest ones I have is stuff like sharp and ffmpeg. you're not
8:05
running anything that is written in a language other than JavaScript in Cloudflare. And anyone saying otherwise,
8:10
like, oh, you can just wom your stuff has not tried it seriously. I have been to hell and back for many projects
8:17
trying to get Cloudflare to let me do something that involves any code that isn't in JavaScript and every single time I gave up and moved to one of the
8:23
other options. Speaking of other options, Netlefi. Nellifi is another Lambda wrapper, but they include all the
8:29
other fun things like the CDN that make the platform so nice. Everything from here down effectively has those pieces.
8:36
Really good GitHub integrations. Honestly, really good integrations in general. They have an awesome team. They
8:41
support the hell out of open source. They're pretty good. I've never regretted my use of Netlefi in a
8:46
meaningful way. They've been a sponsor in the past. I wouldn't be surprised if they are again in the future. Netlefi is solid platform. They handle CDN and
8:54
distribution stuff, but they don't have everything. The biggest thing I miss when I use Netlfi is concurrency because
9:01
again the concurrency model for a lot of these things including AWS Lambda is each request gets its own instance and
9:08
for the modern way that things work that is not pleasant. Their solution for this is some really cool background jobs and
9:15
Q type stuff. The work they have done for their queuing things is actually really really cool. The bit I played
9:20
with it for was awesome. They were way ahead of Versel with the workspace thing. They had it figured out early and
9:26
it was surprisingly cheap. I should also mention for the Cloudflare stuff before I forget, GitHub integration, GHF.
9:32
Getting your Cloudflare stuff integrated with modern tools is still your problem, not theirs. The dashboard is absolute
9:38
garbage. I I actually think that the entire dashboard codebase should be deleted and restarted from scratch.
9:45
There is no recovery at this point. They've had multiple massive global outages because of bad code for fetching
9:51
data in the dashboard. It's pretty pathetic. Addy just jumped in saying Cloudflare pages is native GitHub
9:56
integration. Awesome. Cloudflare pages is also dead. They are merging it with Cloudflare workers now and they've done
10:03
a terrible job documenting those changes and I never know where I'm going when I'm trying to deploy on Cloudflare
10:08
anymore. I had so many problems the last time I tried to deploy on Cloudflare that I sent to the team. The poor exec
10:13
who was in the room with me when I did this wrote over seven pages of notes at a 10-point single spaced font that she
10:19
then presented to the entire org and got like half or so of the things fixed. They are trying. Cloudflare does care a
10:25
lot, but the experience is just so far behind any of the competition that's at
10:30
all more modern. Just go try to deploy a random V react app on Cloudflare and on
10:36
Versel and then make a change and see how hard it is to deploy on those two things. It's just not pleasant. But what
10:42
you're getting for that cost of your sanity is way cheaper overall. There are
10:48
issues with the cost side though because they're not very transparent about what free things stay free. They don't charge
10:54
for egress in a bunch of cases which is huge because it means if you're doing a lot of data transfer it is cheap or free
11:00
but at a certain point they might strongarm you into the enterprise plans where those things suddenly do cost
11:05
money. So if it's free on the free tier or free on the base tier that does not guarantee it stays free in the
11:10
enterprise tiers. So know that cuz it's very important. One last really great thing they did though they hired Dylan. If you're not familiar, Dylan Moy is one
11:17
of the like wizard Typescript devs powering all sorts of tools in the background. One of the people that's
11:22
really pushed Effectts to where it is today. Fellow JJ nerd, great developer overall. Love Dylan to death. He was at
11:29
Vercel and cared a lot about DX there. He's now at Cloudflare and he's pushing the limits of DX there as well. Trying
11:34
to fix a ton of stuff. In his first week, he filed like 20 PRs to the Wrangler CLI and all these other random
11:40
things. There's a good chance that Dylan will be able to fix a handful of the things in this list, but right now, Cloudflare has the second worst DX
11:47
compared to AWS. In many ways, I would argue it's worse than AWS because it changes all the time and is never well
11:53
documented and nothing ever makes sense. It's actually so unclear what you can and can't do on Cloudflare because the
11:59
docs are just wrong and lie a lot. It's it's rough. And now for the exact opposite experience, Verscell. I have my
12:06
issues with Verscell. Everyone does. Watch my breaking up with Vercel video if you want to see some of them. There's
12:11
a lot of them, but they are still by far the easiest and most consistent way to deploy most apps. Basically, everything
12:18
I have shipped to the web over the last few years has been on Vercel at the very least for the web app for it cuz
12:24
it's just a really easy way to do that. The GitHub integration is great. The free tier is great. The billing model makes sense. The integrations with
12:30
everything are awesome. Honestly, I can just copy this part as well as this
12:35
part. Obviously, it's the best place for Nex.js JS regardless of how you feel about next even I'm coming around to not
12:40
liking next too much nowadays obviously they handle the CDN distribution stuff and the parts where we start to really
12:47
differ from the competition fluid compute this is the thing I talked about before it's their attempt to do similar
12:52
pricing to what Cloudflare does with the CPU time pricing it has helped a ton they also consistently introduce cool
12:59
primitives to the infrastructure that take advantage of these things like the workflows stuff I know you guys don't
13:04
love the whole syntax of direct directives with use workflow and whatnot, but it is really cool what it
13:10
can do. It's a good way to get started with that type of building if you want more reliable services. It is what it
13:16
is. There are negatives though. Cost is still an issue, not just CPU cost. I
13:21
would actually argue for most apps, the cost difference between Versel and Lambda is in favor of Vercel for the
13:28
compute side because of the concurrency stuff in particular. That just knocks costs down a shitload. But they do
13:34
things with the costs that still aren't great. Things like the $20 per month seat pricing. Very annoying. Every time
13:40
I have to add a new dev to the team, I'm just increasing my Verscell bill. Don't love that. But the biggest cost when
13:46
you're shipping real software is almost never going to be the compute or the seat pricing on Versel. Bandwidth. Every
13:53
time I see one of those viral bills where it's like, "Oh my god, Verscell cost me $5,000." All but one of those
13:59
instances, it was bandwidth. Because Vercel has a very aggressively positioned CDN that has the goal of
14:05
making everything as fast as possible. All of the code that Verscell ships for you, the things that go to the users
14:11
like your HTML pages, your JS bundles, your SVGs, all the things that are
14:16
coming out of your codebase that are going to the user, those are all on Versel's CDN. It is obviously meant for
14:21
things that are small and need to be loaded quick, like you know, JavaScript files that power your site. But if
14:26
you're filling up your public folder in your project with a ton of big assets like 50 megabyte video files or 10
14:32
megabyte PGs or 5 to 10 megabyte MP3s, that's going to cost a lot. It's almost
14:38
like you're trying to use a race car to pick up groceries. Not only is it going to fit fewer groceries, it's going to
14:43
use more gas and probably cost you more maintenance. It is not the right solution for any static asset that is
14:50
bigger than like 400 kilobytes. They do offer their own file storage solution called blob that is built on top of R2,
14:56
funny enough, the Cloudflare product. I don't know how hard they're focused on it now. It doesn't really seem like a thing they care a lot about. Thankfully,
15:02
you can use upload thing, a weird file upload service some random YouTuber made. Don't think about that part too
15:08
much, but uh it's a lot cheaper. Doesn't charge for egress. Worth considering. So, that's why I default to Verscell. As
15:14
long as you're careful about the bandwidth and where you're putting it, it ends up being really good. The GitHub integrations are best in class. The CLI
15:20
is really good. It's easy to set up. It works with everything. It's real node, so you can do anything you can do in Node.js. It's pretty good. Generally
15:27
speaking, if it doesn't work on Vercel, it's probably because it's a bad workload for serverless in general. It
15:32
is very rare that I find it worthwhile to move off of Versel to another serverless provider, unless it is some
15:38
crazy weird compute thing that Cloudflare happens to be cheaper for. But even that's getting rarer now with
15:44
the fluid compute pricing. Cool. So, let's say you're one of those people that just cannot use serverless. There
15:51
are a lot of people that that is the case for and there are even more people that that isn't the case for but occasionally have a project that
15:57
benefits from traditional servers. Let's look at our options for that. Let's start with the easy ones to make fun of
16:04
Petner and OVH. Benefits really cheap. People on Twitter will think you're cool. Negatives, uh, your account can
16:11
get cancelled at any time, especially with Hster. I've even experienced this. They didn't like that I signed up with a
16:17
Gmail account, so I got auto flagged and my account couldn't deploy for a long ass time. It was bad. And I've seen that
16:24
story so many times. I've even seen people's production environments getting taken down because some random policy change resulted in their account not
16:30
having some checkbox hit. They are known for banning. They are known for flagging. A lot of people have had a lot
16:36
of problems. Immediately, I get [ __ ] for talking [ __ ] on Hesser, but I don't care. I've exclusively had bad experiences with Hner, and I need y'all
16:42
to know that. OVH is some amount better, but honestly they're also slightly more expensive, so I rarely find it is worth
16:48
it. The product offering is also lacking. Like no integrations with anything. If you're using Hatner, you're
16:55
managing your deployment pipelines. You're managing your methods for allocation. You're managing your
17:00
hierarchy for like what servers are being routed to and from your gateways, your CDNs, everything. They're not doing
17:05
[ __ ] for you. They're giving you a VPS in a box that they own somewhere random. Also of note, uh locations kind of suck.
17:11
The best prices are for the EU servers, but even the EU servers aren't coll-located with other important
17:17
things. Like if you're using, I don't know, planet scale for your database, the likelihood that the planet scale
17:22
database and the heter database are on the same network is basically zero, which means you're adding a shitload of
17:29
latency and making your service significantly slower and worse so that you can look cool on Twitter for paying five bucks a month instead of six. It's
17:36
just not worth it. I I don't know any serious people who are building on top of Hetner. I just don't. It's all
17:41
hobbyists. And that's fine if you want to just be a hobbyist and really microoptimize your costs. I don't
17:47
believe that you're real. I just don't. Not a hatner fan. I'm sure my comment section is going to be wonderful now
17:53
that I've said that. Next, we'll talk about Digital Ocean. This is one I have a ton of experience with. First benefit
18:00
is the docs. Best in class. I in chat, tell me if you're old enough to have
18:06
been there with me. Ones in the chat. If you've also relied on the docs for Digital Ocean, for deploying Minecraft
18:13
servers places other than Digital Ocean. I know that's been the case for me. I would not be the dev I am today if it
18:18
wasn't for the Digital Ocean documentation on how to host Minecraft servers. Look at that chat. A lot of us
18:24
have been there. Crazy throwback, but man, the amount of quality documentation that they have had forever now is just
18:31
unbelievable. Like to this day, I'll Google search some weird thing I want to do with SSH or GNU screen or some thing
18:37
I want to deploy. There's a 50% chance that Digital Ocean is one of the first results and not even how to do this on
18:43
Digital Ocean. It's just how to do this. And if you choose to use Digital Ocean, you can. They really took that angle
18:49
seriously of just being a good resource for developers. They have since laid off a lot of the staff that wrote those docs, but god damn were they useful for
18:55
a long, long ass time, even like pre-stack overflow days. Other benefits of Digital Ocean, they've been around
19:02
forever, so they're probably not going anywhere. They have good integrations, not great, but good integrations with things like GitHub. I'll call it decent
19:09
integrations and a lot of companies that we use things from here are using them from Bright Data to FAL to Character AI
19:16
and more. Like they're they're a real legit company that's being used by a lot of real legit products unlike some of the other options here. We need to take
19:22
a look at the pricing though because it's not cheap. They're immediately starting with their GPU boxes, which is
19:28
cool that they offer those, but the compute less great. They do still have a free tier, but droplets, oh, they're now
19:34
per second pricing. Their base here at 512 meg, 500 gigs of transfer, 10 gig
19:40
drive is four bucks a month. 1 gig is up to six. And just for comparison sake,
19:46
we'll look at Hner's pricing. They got boxes with 4 gigs of RAM and 40 gig SSDs
19:51
and up to 20 terabytes of traffic for four bucks a month. This is why people choose Hner. It is also worth noting
19:57
that it's in Germany or Finland. And I don't think the US locations are even visible in the pricing charts. Or is it
20:04
regular performance? That's okay, cool. Regular performance. A different tab than the cost optimized ones. And those
20:10
ones have US locations. And now we're up to six bucks for the 2 gig 40 gig plan. That's a lot closer to what we were
20:16
seeing over here. So it as crazy as it seems, do you understand how hard Hner
20:22
works to make the price look incredible even though there are catches? Like
20:28
again, we have to hit this button to get real locations and immediately the price skyrockets. Turns out that the two vCPU
20:35
4 gig boxes in Germany in regular performance mode, not cost optimized mode, is more expensive than Digital
20:43
Ocean. And if you want a dedicated box so that you never have to worry about performance degrading, you're now at 14
20:49
bucks a month minimum for again relative small. Okay, it's 8 gigs of RAM. It's a little bit better, but 28 bucks for 16
20:54
gigs a month, not great. Regardless, pricing is reasonable across these options so far. We have not gone into
21:00
the things that are massively overpriced. Okay, admittedly, 2 gigs of RAM and one vCPU for 12 bucks is a
21:06
little expensive. Digital Ocean is not the cheap option. It never was. If you're optimizing on that level, it's
21:12
hard for me to take the work you're doing seriously. Like a $2 to5 a month difference across servers is not
21:17
something I care about because the time it takes to build those things is a lot more. Hell, the inference I use to build those things is a lot more. I'm paying
21:23
200 bucks a month for Claude and for Codeex right now. Five bucks a month is whatever. So, what are the negatives?
21:29
How do I put this? Digital Ocean feels a little lost right now. They don't really know what their core offering is. You
21:35
can even tell from the homepage. The inference cloud built for scale. What? That's not what I've you I don't know
21:41
anyone using Digital Ocean for inference right now. I've never met a person who does that. Oh, look at that. They have an open claw shout out on the homepage
21:48
now. They are leaning so hard into trying to find new customers, which suggests, this is the scary part, they
21:55
may be circling the drain. Of the options I have in this list, they are in the top section of most likely to have
22:03
the same problem that we're talking about here right now. So yeah, if your goal is to not have to deal with this
22:08
type of migration because of the Heroku death, I can't guarantee with Digital Ocean that you won't have to experience that again. So know that going in.
22:15
Definitely feels a tad dated and it feels like the compute isn't their focus anymore. They really seem to be leaning
22:20
into the inference side, which good for them, but there's way more competition there, and I'm not confident that they
22:26
can have a meaningful impact. So what do we have next? We covered these ones. Let's hop into Fly.io next. Flyio is
22:32
dope. They were a sponsor in the past. I hope they might be in the future, but they did recently have to do layoffs and
22:37
I chose to cut them off as a sponsor at that point because I felt really bad taking money from a company that just laid off a bunch of the staff that I was
22:43
working with. Really good stuff overall and they are also a huge member of like the elixir community which is obviously
22:48
near and dear to my heart. So benefits elixir native which I absolutely love worldclass DX for deploying servers.
22:56
They have some of the best DX in the world. things like the way it integrates with GitHub, how you manage things in the dashboard, the clarity in what's
23:02
going on where, the tools for linking different things together, preview environments, sleeping servers, all of
23:07
those types of things. Great. They're also huge OSS supporters. They help
23:12
sponsor everything from like the Elixir ecosystem and Gleam, Rails, and many other things I'm almost certainly going
23:18
to forget if I try to list them off. They are just a good player in the space, more so than anyone else we've
23:23
talked about so far. I would argue they are actively meaningfully contributing to the development of important open-
23:29
source technologies to the point where it is hurting the business. Okay, people are saying they might not sponsor Gleam.
23:37
Maybe they're not sponsoring Gleam anymore. I'm pretty sure they did in the past, but they are not necessarily doing
23:42
great financially. Again, layoffs and I haven't heard anything about them raising anytime soon, which means they probably haven't. They also have their
23:49
sprite stuff, which I've heard really good things about. It's meant to be VMs and sandboxes that you can safely run
23:55
agents in that have their own primitives that will let them be powerful. And there's a bunch of other random things
24:00
that they've built that are just way cooler than what you can do on other clouds. I did a video a while back about
24:07
Flame, which is an alternative way of doing serverless where you are encapsulating processes in your codebase
24:13
to spin them up on different servers for specific needs. Like if you want to sometimes have a GPU for doing, I don't
24:18
know, ffmpeg stuff, but you usually don't need it. Having your stuff always run on the GPU box would be way too
24:26
expensive. The GPU is not being used. But if you could have one function in your codebase that runs on the GPU box and spins it up and handles it, then
24:32
awesome. In this example, I'm sorry if you're not familiar with Elixir syntax, my beloved. You take this process that
24:38
is defined here for generating thumbnails, which runs in FFmpeg, which could lock up the main server or just
24:44
not be performed if it doesn't have a GPU. You can wrap it with a flame call, exact same stub function here, and it
24:50
will return the result as though you just called this on the same box. It's so cool. It's just so far ahead of
24:57
anything else I've seen for this type of stuff. But we need to be realistic. The negatives, the database reliability just
25:04
isn't there. Even when I was doing my tutorials and work with them, I had my database just die and fail multiple
25:10
times throughout. I learned to just not trust the database, as many other Fly customers have. They often move their databases off of fly to their own other
25:17
alternative services like you know planet scale but during dev it's so convenient like the way that setting things up on fly is so nice it hurts but
25:25
reality is that the database stuff isn't there and in general reliability just isn't quite where we need it to be. They
25:30
had a huge outage recently. They likely will again in the future. They have built a lot of their own things and a
25:35
lot of those things are really really cool. It's why they can do all this cool stuff but it also means they're not as tried by the industry and as a result
25:42
they're not as reliable. Also note with the DB thing not managed. They don't do managed databases. They just give you an
25:48
image that is running Postgress. Apparently they now do have managed databases. I did not know that. That's
25:54
good to hear, but uh the last time I tried it, they didn't. That is a relief. I'm still going to say the reliability
25:59
isn't good, but the fact they have managed DB is a cool change. And I would also argue that within these options,
26:05
Fly might be the highest risk of death. I would put them slightly higher than
26:10
Digital Ocean in terms of this company might run out of money and die. I just have not seen a lot of big customers or
26:17
revenue numbers or investments or any of the things that would make me confident Fly will still be here at the end of the year or even early next year. Even when
26:23
I was working with them, the rate at which the people I was talking to suddenly weren't at the company anymore
26:29
was a bit terrifying. I even went to Elixir in 2024 and was sitting at a table with a bunch of Elixir nerds,
26:34
including a few that worked at Fly, and watched as they checked their phones and got laid off. That does not inspire confidence. They also deprecate things.
26:41
Not a lot, but enough to be concerned. Somebody in chat just mentioned that they used to have a managed DB Superbase
26:46
integration, but that got discontinued. Not the thing I would bet my whole business on right now, personally. One
26:51
of the most fun platforms I've ever built on. Not confident that they will still be here next year. Take that as
26:57
you will. And next we have Render, who has this big migrate from Heroku with
27:02
near zero downtime banner on top. They know exactly what they're doing. Render is used by a ton of big companies. Their
27:09
revenue is really solid. They've had no issues raising money. They understand modern tech and PHP. Even the founder of
27:15
Hashi Corp has had nice things to say about Render. Mitchell's a legend. Cool to see. They have a decent free tier.
27:20
You have to immediately bump to their monthly tier if you want to do more, though. You don't have like boxes you're
27:26
renting the same way, but they're pretty generous overall. Relatively modern, supports everything, generous free tier,
27:32
likely staying around. They make enough revenue that I'm not worried about them disappearing anytime soon. Negatives,
27:37
you pay a sub instead of server pricing. A lot of that pricing is hidden under
27:43
the enterprise custom tier. They charge a separate monthly fee for setting up cron jobs. That's kind of funny. Oh,
27:50
look at that. Their GitHub integration is still in a very good state. Last time I used it, it was pretty good. So, that's good to hear. I'll put that in
27:56
here. Good GitHub integration plus preview environments, which is not guaranteed across these different
28:01
providers. Apparently, the egress is super expensive as well. Definitely worth noting. Good call out chat. The
28:07
$20 tier comes with 500 gigs of bandwidth. 15 bucks per additional 100 gigs. Inbound bandwidth is free. Okay,
28:13
that's cool. So, uploading to it is free. Sending data from it costs money. That's actually a really nice call out.
28:18
Good [ __ ] I would never fault anyone for going with render. Seems like a really good option. Honestly, like one of the most reliable out of all of
28:24
these. Like I I would say like other than AWS, least flight risk, too. But now we need to talk about Railway.
28:30
Obviously more than at any point in here account for bias here. Jake and I have a long history. I was almost hired as
28:36
engineer number four at Railway all the way back in 2021. I've watched this company's ups and downs. I've used them
28:42
for that entire 5-year window. I love Railway to death. I have my issues with them, but for the most part, it's a
28:48
great platform. It's a phenomenal team and I'm very excited for them and all the success that they've been having. Benefits truly modern. It's just you'll
28:56
feel the difference when you use it. It just works great with everything. The CLI is awesome. The docs are awesome.
29:01
The GitHub integration is great. It just behaves. It also is one of the best dashboards for actually seeing what's
29:07
going on and how parts are linked. You can clearly see the different services, how they're linked to each other. The domain setup, all of that really good.
29:14
The observability is awesome, too. I haven't even bothered setting it up yet cuz this project hasn't needed it. The way they handle different environments
29:19
is great. You can set up preview environments, things like that relatively well. It does not, as far as I know, have good automatic preview
29:25
environment creation when you do PRs and things like that. It might be able to be set up, but it's good. I honestly really
29:31
like the way Addi put it here. Railway makes me smile every time I use it. The pricing is relatively transparent and
29:36
clear. They drop hard numbers for what each thing costs. There's a little confusion around various different
29:42
things like the relationship between like how these parts are measured. It's sometimes confusing to figure out what
29:47
usage you're actually going to get. And then there are interesting things that are free that I'm not confident are
29:53
going to stay free. So like in the benefits section, egress from their object store is free. But then in the
30:00
negatives, object store is private only. You cannot do a public bucket. That burned me real bad on a project that I'm
30:06
now migrating off of railway storage. Free egress is a ticking timer in my opinion. No one offering egress for free
30:12
can maintain that forever. Like there's always a catch. and I am a little scared of what that catch will be with railway. This is the type of complaint that I
30:18
might have for other things if I use them more, but as a pretty heavy Railway user, I see the flaws more and the
30:23
dashboard can get into some weird states, especially around DNS and SSL stuff. You don't buy domains on Railway.
30:30
I bought mine on Versel, but then I set it up on Railway and SSL was broken forever. The dashboard just wouldn't
30:35
verify the CNAME. It just it took a while to get that working and I didn't know if I was doing it right last time because the UI didn't really indicate
30:41
what the current state was very well. Thankfully, I just left it alone for half an hour, went back and it was good.
30:47
Not clear that was happening though or if it would or wouldn't work. Oh, and the egress does cost 5 cents per gig for
30:53
services, but the object storage has free egress, but you are paying 1.5 cents per gig per month for the storage.
31:00
So, know that I got the previous storage price from Jake. He might have just typed it, but 1.5 cents per gig is
31:05
pretty good price for the storage. I might rethink some things based on that. There's a lot more benefits to them though than we've gotten to here.
31:12
supports everything. Best DB setup I've ever had. Like the way that you link services together and all of that is
31:18
just so pleasant. Config is generally great. Perf is insane. They're racking their own servers and they're good
31:24
servers. I also think that the server firm I'm using for US West is pretty close to me, which makes it feel just
31:29
absurdly fast. I'm just very happy with Railway. I'll call pricing fair overall.
31:35
There are very few things on Railway where I'm like, that's too expensive, and the one that I thought was, I was just wrong about. Oh, they do have
31:40
previews and oneclick roll backs. That's good to know. The one-click rollbacks is huge and has saved me a ton of times. Depending on how you use the platform
31:46
might even save you a shitload of money. Some customers who were on AWS before were able to cut their cost by 90% by
31:51
moving to Railway and also get better experience. It's It's really good. I'm super happy with Railway. I bet you will
31:56
be too. They are probably my top pick here. One last thing on Railway before we get to EC2. They just raised $100
32:02
million. They're not going anywhere. They were already nearly profitable before. They might have actually been
32:07
profitable for a bit. They are not going anywhere. AWS also never going anywhere.
32:12
Super reliable, like disgustingly reliable, supported by everything, great
32:18
locations, so you know that they'll network with everything fast. Like every
32:23
service tries to get themselves into AWS server farms so that you can have low latency with AWS EC2. The amount of
32:30
integration that they have with like everything is nuts cuz everyone's built it. Platforms like Terraform and Palumi
32:36
are largely built around EC2 and EKS. And hell, Kubernetes is largely designed around how EKS works at this point. Like
32:42
everything is building for EC2. Like if it doesn't support EC2, I am sus as
32:47
hell. Guaranteed SLAs, reliability, all the things you need there. Bargate's dope. There's tons of other services you
32:53
can integrate alongside EC2 within AWS and externally that are insane. And most importantly, no one's ever been fired
32:58
for picking AWS. It's the default. And it's the default for a reason. It is good. But there are negatives. cost is
33:04
surprisingly higher than competition. Their pricing is so annoying that usually you go use another service to
33:11
look at it because it's just their pricing is God, they hide all this info so deep. Here we go. Sadly, this chart
33:18
is doing hourly pricing, not monthly. Time 24* 30. And there's a reason why. A
33:24
2 gig 1vcpu box with just EBS storage is $22 a month.
33:32
If we're talking EKS, you're going to want the beefiest nodes you can reasonably fill. So, you can choose 190
33:37
core Graviton box. Yeah, it's it's pretty nuts. AWS not only charges a
33:43
significantly higher price than what I would expect for the tier of hardware, they don't really lower those prices.
33:50
So, it's kind of just like a fee you're paying forever on a box that's probably 6 plus years old and you're paying as
33:55
though it's brand new. It's bad. It's crazy. Everybody always advertises like AWS is the cheap option. It's not. In
34:02
many cases, Vercel is actually cheaper than AWS. Just depends on how you're using them. And if you're doing stupid things on either, you can screw
34:08
yourself. It's no surprise railway comes out cheaper as often as they do. So, yeah, cost is not the thing you are
34:13
saving. Setup isn't the thing you're saving either. You basically have to build a solution to handle your
34:19
deployments on AWS. There have been multiple billion plus dollar companies built just because setting up on AWS is
34:26
too hard. Everything from Terraform to versel is arguably because AWS sucks to config dashboard is Cloudflare tier UX.
34:35
It at least works though. It's rare on the AWS dashboard and things are just outright broken like they are on Cloudflare, but getting around it is
34:42
hellish. Oh god, the permissions. I god that's so many throwbacks. I I have
34:48
been to hell with AM. It's so bad. It's so [ __ ] bad. I I'd put this in the
34:54
same bucket honestly as I put GCP and Azure. Now, if you're coming to me or a channel in a video like this for advice
35:00
on where to deploy, don't deploy to AWS. Seriously, don't. We've went over all of
35:05
these options. You hopefully understand what the values are for each of them. If
35:10
I was to tier these, I'm going to ignore the ones I wouldn't recommend. I'll say top Rex, the ones that I would
35:16
absolutely recommend, I think everyone should at least consider, Railway, Vercel, and Render. all easy. S tier,
35:22
you're good. I have a specific need tier. I would put Netlefi if they have some specific integration or their
35:28
queuing stuff works really well for you. Cloudflare if you're willing to deal with the compromises around not having a
35:34
proper node environment. Very beneficial. Or you're just trying to microoptimize for costs at crazy scales.
35:39
Really good option as well. Maybe Hner. It hurts to put it here, but if your goal is to have the cheapest possible
35:46
thing with insane free egress that's just hosted and you're okay with it being slow and unreliable, it can be
35:52
fine. I wouldn't confidently tell you like, oh, go move that to Hner, but it is an option worth considering. Oh, and
35:58
Fly, absolutely Fly.io. While it might not still exist in a year or two, it has some really compelling offerings that
36:04
nothing else does. There's a good chance you run into a problem Fly uniquely solves. Worth considering if you do. And then I have the you won't listen anyways
36:11
tier. This is for people who watch these videos for fun but can't realistically
36:16
take my recommendations for all sorts of different reasons. This is where I'd put most of the AWS offerings like Lambda
36:23
and EC2. I'd also put GCP in here, Azure, IBM Cloud, things like that. Like
36:29
if your employer already chose it for you, it's fine. And pretty much everything else, I don't think I can
36:36
recommend it. Now, if you pick anything here, you're probably well set. If you pick anything here, I hope you have a
36:42
good reason. And if you pick anything here, I hope it was your boss that picked it, not you. Now, you know how I think about these things. And hopefully
36:48
you can now better understand why almost everything I deploy is on Versel and Railway. And maybe in the future render
36:54
as well. Yeah, and we barely even talked about CDNs. What a video. I hope this
36:59
helps you better understand what these platforms are, what benefits and negatives each have, and maybe, just maybe, you'll have more confidence when
37:05
you pick the next place you host. Let me know how y'all feel. And until next time, please stop flaming me about
37:10
Hutner. I really don't care about your $5 VPS.

## Summary

The video is a practical breakdown of hosting platforms in 2026, covering both serverless and VPS options. The presenter's goal is to give an unsponsored, honest framework for choosing where to deploy.

**Serverless options reviewed:**
- **AWS Lambda** — Hard to configure, broken concurrency model, streaming issues. Not recommended for most.
- **Cloudflare Workers** — Cheapest due to CPU-only billing and near-zero cold starts, but runs a custom JS engine (not Node.js), so native binaries (sharp, ffmpeg) and many Node APIs don't work. Dashboard is terrible and docs are often wrong. DX is improving with a new hire (Dylan Moy).
- **Netlify** — Solid Lambda wrapper with CDN, great GitHub integration, good queuing/background jobs, but same concurrency limitations as Lambda.
- **Vercel** — Easiest and most consistent. Best DX, best GitHub integration, real Node.js, "Fluid Compute" pricing helps with costs. Biggest pitfall is bandwidth cost from large static assets. Default recommendation for web apps.

**VPS options reviewed:**
- **Hetzner** — Extremely cheap (especially EU), but account bans are common, no integrations, poor co-location with other services. For hobbyists only.
- **OVH** — Similar to Hetzner, slightly pricier with a thin product offering.
- **Digital Ocean** — Legendary documentation, stable company, decent integrations. Concern: they seem to be pivoting toward inference/GPU hosting and may be "circling the drain." Not the cheapest.
- **Fly.io** — Outstanding DX, Elixir-native, innovative features (Flame for on-demand GPU workloads, Sprites for agent sandboxing). Database reliability is poor, and the company's financial stability is uncertain after layoffs.
- **Render** — Used by large companies, solid funding, modern platform, generous free tier, good GitHub integration. Subscription-based pricing; egress can be expensive.
- **Railway** — Top overall pick. Modern dashboard, best DB setup, excellent observability and CLI, one-click rollbacks, fair transparent pricing. Just raised $100M, nearly profitable. Minor issues: no public object store buckets, occasional DNS/SSL UI quirks.
- **AWS EC2/EKS** — Most reliable and integrated, but expensive, complex to configure (IAM is painful), and the dashboard is poor. Valid if your employer chose it.

**Recommended tiers:**
- ✔️ Top picks: **Railway**, **Vercel**, **Render**
- Specific-use cases: Netlify (queues), Cloudflare (cost at scale, JS-only), Fly.io (unique primitives), Hetzner (ultra-cheap hobbyist)
- Avoid choosing yourself: AWS Lambda, EC2, GCP, Azure

## Analysis

RoadTrip has evolved into a secure, self-improving personal assistant running locally on Windows. Current hosting needs are minimal — all skills, rules engine, and telemetry are file-based and run in-process. However, as the project grows toward an always-on assistant with autonomous agent workflows, hosting will become relevant.

**Key considerations for RoadTrip:**

- **No immediate hosting need.** The current architecture (Python skills, local file logging, PowerShell git automation) runs entirely on the developer's machine. No cloud hosting is required today.

- **If a web interface or API is added**, Vercel is the natural first step — zero-config deployment, free tier, and excellent GitHub integration align with RoadTrip's single-developer workflow. The bandwidth caveat is not a concern for a personal assistant.

- **If persistent background agents are needed** (e.g., always-on self-improvement engine, scheduled telemetry aggregation, autonomous push cycles), Railway is the better fit. It supports long-running servers, has the best managed DB experience reviewed, and its pricing is transparent. The $100M raise removes longevity risk.

- **Fly.io's Sprites** (isolated VM sandboxes for agents) is worth watching. If RoadTrip evolves toward running untrusted or experimental agents in isolation, Fly's primitives are unique. The financial risk is real, so not suitable as a primary host yet.

- **Cloudflare is a poor fit.** RoadTrip's Python-based skills and potential use of native libraries (e.g., future ML inference, PDF parsing) are incompatible with Cloudflare's JS-only runtime.

- **AWS is overkill** for a personal assistant project and adds unnecessary operational complexity.

- **Snowflake is not an application host**, but worth considering as a data layer for RAG-based Q&A. Its native vector search (Cortex Search) and built-in embedding models would let RoadTrip retrieve relevant context from session history and knowledge chunks in a single platform. However, the cost model is unfavorable at personal-assistant scale — Snowflake charges per compute credit and has cold-start latency unless the warehouse is kept hot. A better starting point is **pgvector on Railway**, which is free within the Railway plan, has no cold starts, and handles RAG well up to millions of vectors. Revisit Snowflake if cross-session analytics and vector retrieval need to converge at larger data volumes.

**Conclusion:** No immediate action needed. When hosting becomes necessary, start with Vercel for any web-facing components and Railway for any persistent backend services or agent orchestration. For RAG/Q&A memory, add pgvector to the Railway Postgres instance first; migrate to Snowflake only if analytics requirements outgrow it.
