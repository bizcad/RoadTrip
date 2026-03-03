# Jack AntiGravity and OpenClaw
## Links
- https://www.youtube.com/watch?v=-hYE5U6FGk8

38,610 views  Feb 19, 2026
📈 ALL Systems: https://bit.ly/4kol0y5
💎 Agentic Voice: https://glaido.com
🤩 My Goofy pod: https://bit.ly/3Od4CV8

FREE Resources 👉 https://bit.ly/4rrTgLX

-- CORE Software
🧑‍💻 Hosting: https://www.bluehost.com/
🎤 Eleven Labs: elevenlabs.io/?from=partnermiller7651
💎 Work with me: https://scalewithteddy.com/
🤖 Claude - https://claude.ai/
🛠️ Antigravity - https://antigravity.google/
📂 OpenClaw - https://openclaw.ai/
🦎 Maemo bot - https://t.me/maemo_bot
🏗️ Docker - https://www.docker.com/
🟢 Node.js - https://nodejs.org/
✈️ Telegram - https://telegram.org/
👴 BotFather - https://t.me/botfather
📡 OpenRouter - https://openrouter.ai/
🔍 User Info Bot - https://t.me/userinfobot
🌩️ Grok (xAI) - https://console.x.ai/
💬 OpenAI - https://openai.com/
📱 WhatsApp - https://whatsapp.com/
🤖 Nanobot - https://github.com/HKUDS/nanobot
## Summary

Jack demonstrates building a local-first “Gravity Claw” assistant by combining AntiGravity orchestration with OpenClaw-style architecture and Telegram as the user-facing interface. The walkthrough uses a five-step flow (Connect, Listen, Archive, Wire, Sense) to progressively add capabilities: secure Telegram setup, model/API integration (OpenRouter), voice transcription, voice replies, memory layers, MCP tool access, and proactive heartbeat messaging.

The core pattern is iterative feature shipping through prompt-driven development: test in Telegram, paste errors/screenshots back to AntiGravity, and let it generate/fix implementation details. He emphasizes control and safety through local hosting, whitelisting a single Telegram user ID, and optional cloud deployment only when needed for always-on behavior.

### Features

| Feature Name | Time | Short Description |
|:------------:|:----:|:------------------|
| Local-first Telegram AI assistant | 2:10–2:55 | Creates a custom assistant that runs on the laptop and responds through Telegram chat. |
| Guided bot provisioning + ID whitelist | 5:02–7:49 | Uses BotFather token + user ID whitelist so only the owner account can interact with the bot. |
| Multi-model backend via OpenRouter | 6:16–6:58 | Connects model routing to access many models (including free options) with spend controls. |
| Error-correct loop with AntiGravity | 8:11–8:23 | Fixes runtime/model issues by feeding screenshots and prompts back into AntiGravity. |
| Voice-to-text transcription (STT) | 9:34–12:02 | Adds voice message understanding using Whisper-style transcription (Grok/OpenAI path). |
| Feature dashboard + prompt generator | 9:52–11:04 | Selects desired capabilities as “Lego bricks” and generates implementation prompts in bulk. |
| Text-to-speech replies (TTS) | 12:21–16:07 | Adds ElevenLabs voice responses, including voice style/locale changes. |
| Tiered long-term memory | 16:19–21:08 | Implements core memory + conversation buffer + semantic memory (Pinecone + local store). |
| Personality profile (`soul.md`) | 21:14–21:55 | Encodes behavioral guidance (tone, challenge level, proactivity) into persistent assistant behavior. |
| MCP tool wiring (email/tools) | 22:19–26:45 | Reuses AntiGravity MCP connections so Telegram prompts can trigger external tools (e.g., email checks). |
| Proactive heartbeat messages | 27:26–29:44 | Adds scheduled outbound accountability check-ins (cron-based) initiated by the assistant. |
| Optional always-on deployment | 30:00–32:50 | Deploys to Railway for uptime when laptop is closed, with notes on single-active-instance operation. |

### Telegram + Voice Interaction Pattern

Telegram is treated as the primary prompt window: all user interaction happens in the chat thread, while AntiGravity acts as the behind-the-scenes builder/fixer. This separation creates a clean UX: “build in AntiGravity, operate in Telegram.”

He then layers in voice both ways:
- Voice recognition (STT): Telegram voice notes are transcribed to text so the assistant can reason over them.
- Voice synthesis (TTS): assistant replies can be returned as spoken audio, not only text.

Together, this turns a standard text bot into a mobile, conversational interface that can be used hands-free and cross-device.

## Analysis

These capabilities map well to RoadTrip’s operational and planning workflows:

- Telegram as command surface: a lightweight remote control channel for trip ops, daily status checks, and quick prompts when away from the desktop.
- STT/TTS for in-transit use: drivers or travelers can send voice notes and receive spoken responses without heavy typing.
- Tiered memory for continuity: persistent recall of traveler preferences, itinerary constraints, and prior decisions across sessions.
- MCP wiring for integrations: can bridge RoadTrip to calendars, docs, email, mapping, ticketing, and project tools without custom UI for each system.
- Heartbeat automation: scheduled nudges for fuel checks, booking deadlines, packing tasks, or daily route confirmations.
- Local-first + controlled deployment: start locally for privacy/safety, then deploy selectively for always-on assistant behavior when needed.

For RoadTrip specifically, the strongest near-term value is a “Trip Concierge” bot that combines (1) Telegram chat/voice input, (2) itinerary + preference memory, and (3) proactive reminders driven by route context and deadlines.

## Transcript
<!--start transcript-->
Intro
0:00
Imagine if you could build Claudebot in anti-gravity. Well, I did that and I
0:05
found capabilities that blew my mind. OpenClaw/Claudebot is a 500 IQ intern, but it can also
0:11
destroy your business if you're not careful. Which is why in this video I'm going to show you exactly how you can
0:17
build your own within anti-gravity that lets you build any features that you want, has no supply chain risk, meaning
0:25
that you can save more time, make more money, and get light years ahead of your competitors. And if you don't know who I
0:31
am, my name is Jack Roberts. I built and sold my last tech startup with over 60,000 customers, and now I run a
0:38
7figure AI automation business. So, if you haven't already, grab that coffee
0:43
and let's dive straight in. Gravity claw, which is basically anti-gravity plus clawbar. Now, gravity claw itself
What is gravityclaw
0:51
is essentially like having a co-pilot where you describe something and it
0:57
builds it for you. And think about Lego for instance, right? Instead of an existing mold, an existing way and
1:03
structure of doing things, you can build anything with gravity claw uh that you actually fully understand. And so this
1:10
is the core differentiator here, one of them anyway, that you're actually adding in the functionalities as you go within
1:16
anti-gravity, meaning you fully understand the architecture of what your application actually does on your own
1:22
desktop. And it is 100% customizable. Meaning for example, if you take the
1:27
memory features instead of out ofthe-box memory features, what we can do with uh gravity claw is if we want to
1:32
supercharge or change fundamentally the way it works, you can fully customize anything, which is super super cool.
1:38
Now, you can fork open claw because it is an open- source project. There's over 10 at least that have done this. Mimu
1:45
bot is a good example of this. Um, but the thing is not everyone reads 100,000 lines of code. And you it's one of the
1:52
reasons why over 40,000 instances got exposed as part of that process. But when I built Gravity Claw, I it worked
1:58
even better for me. It was able to do things for me that I couldn't actually get to work with Claudeb, which is why
2:03
I'm so pumped to share this with you because it is really really exciting. On top of that, you can even use it for free. I'll show you strategy exactly how
2:10
to do that. So, let me show you exactly how Gravity Claw works. I can send it messages. I can be like, "Hey there, dude. Could you just remind me what was
2:16
the subject line of the last email that I received?" Send that one off. And again, you can build all these fun all
2:22
these functionalities, all these different features in anti-gravity as your co-pilot. Now, what's really cool I
2:27
love about this is it comes back and it did this instantaneously. It gave a it basically tells you exactly what it
2:33
heard. dude, could you just remind me what the subject line was on that last email? And then it will actually go and check my emails and I'll show you how
2:39
I've done that. And this is all on my laptop. No data lists anywhere else. It's so freaking decent. And I come down
2:45
here and the subject line is blah blah blah. And it's pulled it up. And this is just the beginning of any capabilities
2:50
you can imagine. You can now build your own personal AI assistant within anti-gravity. Now, this is the most fun
2:55
I've had building something in anti-gravity in my hundreds of hours of building it. And you're going to see
3:01
exactly why in this video. Now, the cool thing is it's kind of like being in a Lego shop and you get any brick you want
3:06
to and build anything. Now, to show you the capabilities exactly how this works, and here's the key thing. You're going
3:12
to understand how it works because you've built it and we're going to build it together. And we're going to do this
5 steps frame work
3:17
across a very clear, easy to follow five-step clause framework with the C
C
3:24
standing for connect. Now, the first thing to do is click the link at the top of description so you can download and
3:29
grab this resource. It'll be available there for you for free. I'm going to do is copy this initialization prompt that
3:35
basically just explains we want anti-gravity to be familiar with what open core is to understand the concept
3:41
of what it looks like and we're giving a very kind of brief overview of how we want it to work local first aentic loop
3:48
blah blah blah and a rough idea of the approach that we're going to take in this video so you can follow along but
3:53
of course you can take it in any different direction so going to copy all this stuff going to head over to anti-gravity and then within
3:59
anti-gravity guys what I would like you to do is essentially create a brand new folder and we're going to full screen
4:04
this guy. Come over and we're going to use the planning mode and we're going to use Opus 4.6 thinking for this. Throw it
4:10
in there and then you're going to be ready to go. And there's a couple of things I'd love you to download. We're going to do this on Telegram. Telegram
4:16
is a beautiful platform. The API is super configurable. Makes life very easy. You can download that on your
4:22
laptop which is very cool. And we're going to have this available on the lefth hand side. Then there's two other things I would like you to download if
4:28
you haven't already. One is going to be something called Docker, which is a safer container ecosystem for everybody.
4:34
It's going to be very, very helpful for us when we build things in the future. So to go ahead and download that to your
4:39
computer. And then you're also going to need node.js, but most of you will already have that
4:44
installed. If you don't, just simply go over to this website here and download it. Beautiful. So now we've initialized it. Anti-gravity is going to take a look
4:51
at understanding the open core architecture. And whilst it's doing that, we need to set up Telegram. So,
4:57
let's go ahead and create a brand new bot together. So, what I want you to do is send a message to the bot father. If
5:02
you don't have that, click on search and type in bot father. And when he's here, what we're going to do is send a message. So, you're going to come down
5:08
here and just type in new bot. I believe it's for slash uh new bot, which is cool. We're going to create a brand new
5:13
bot together. And we're going to give it a name. We're going to call this one something like gravity claw. I think it
5:18
needs to be underscorebot, right? So, let's call it gravity claw. Great. It needs to be underscorebot. So, gravity_core_bot.
5:24
Beautiful. Then guys, you're gonna have a link to chat with it and then you're gonna have an access token. So I want
5:30
you to copy the access token. I'm going to give this to anti-gravity so you can have a conversation with it. And the
5:36
cool thing is anti-gravity is going to run you through all the security stuff as well. And it's going to whitelist it, which means that anti-gravity can only
5:42
be accessed from your specific account in Telegram, which is awesome. So going to copy this one right here. And you see
5:48
when I click on the link, I'm now talking to the wonderful gravity claw. So now we've got Telegram set back up.
5:54
Let's head back over now to anti-gravity. And as you can see, anti-gravity is now doing the fundamentals. We can see the
6:00
implementation plan on the left hand side, which is wonderful. It's uh project scaffolding, core modules. It's
6:06
doing some verification stuff, and then we can actually begin the really exciting stuff. So now we are ready for
6:11
the gravity claw level one. So it's asking for the Telegram bot token, and then it's looking for some API keys so
6:16
we can actually go ahead and have a conversation with it. So what we're going to do is drop in the Telegram bot token right here. And remember, you grab
6:22
that from the bot father. And then for the API key, let's go over to open router, which has access to all the
6:28
models, 300 plus models should I say. Uh, and some of these you can run completely for free. So, let's just come ahead and grab an API key. So, come over
6:35
here. We'll come down to settings. And we'll have to click on API keys. Create a new key. We'll call this one something
6:40
like gravity claw. And the cool thing is you can set a credit limit. So, you're never going to go above this. But again,
6:46
if you use a free model, then you're never going to spend anything on it anyway, which is cool. And we'll set that every month, no expiration. And
6:52
click on create. And then we give it the following prompt. Here is my open router API key. Beautiful. And then we just
6:58
paste that in there. Beautiful. And now anti-gravity is finalized all that stuff. The last thing it's asked for us here is your own ID on Telegram, which
7:06
means that it's going to whitelist this ID, which means no other Telegram ID on the planet could possibly interact to it
7:12
apart from your own account. And bear in mind, this only lives on the laptop anyway. But this just shows you the levels of security and just how how much
7:18
reassurance and confidence you can get just by pulling this step by step. So to find out what your own idea is, you can
7:24
head straight over to Telegram and you can find them by typing in user infobot. I like this guy here with the green uh
7:31
headon and then when you send a message to him, you can literally just say yo yo yo and he will send you your ID. And
7:36
just like that, you got your ID and all the information that you need. So, let's leave this page. Come back over to anti-gravity and just say, "Hey, here is
7:43
my Telegram ID for you to whitelist this." And then it will ask you if you're ready to launch. We just say yes.
7:49
And now it says it is alive and working. So, let's actually validate that this works. Click on start as a for instance.
7:54
And then Gravity Claw is typing. We love it when it says that. And we'll see exactly what it's doing. Something went wrong. Process your message. Please try
8:00
again. So, if I say, "Hey, let's see if he'll respond to us." Let me bring it over here so you can see. Cool. So, we
8:05
need to go back and do one final thing. Let's go back over to anti-gravity. And all we're going to do is simply come down here and we're going to screenshot
8:11
these messages and paste that into anti-gravity. Wonderful. So what happened there? It had the wrong model name for open router, which is cool. And
8:18
it's fixed it now. So we're going to head back over and send it a message. So let's say something like, hey, and see what gravity claw says. And we should
8:23
get a response back from him. Hey, what day is it today? So now we have it physically working and we're talking to
8:29
our actual gravity claw, which is so freaking cool. And he comes back and says it is Tuesday, February 17th, 2026.
8:36
Beautiful. So now we've set it up, we can have a conversation with it. I can send it messages on my phone wherever I'm walking right now. The next thing we
8:43
need to do though is actually give it the ability to listen and communicate back to us. Which is why the second step
8:50
in our clause framework stands for listen. And not only are we going to get it to listen, we're going to use some
L
8:56
state-of-the-art technology. And I show you these integrations, it is going to blow your mind. So check this out. So let me just show you how it doesn't work
9:02
right now. If I send it a voice message and I hold on this, in fact, I can even do it on my phone, right? which I'll do just because it looks cool and you can
9:08
see that it's um across multi-devices. So, if I come back over, let's go to Gravity Claw and send him a message. Hey
9:15
there, dude. How's it going today? Just sent a voice message off. You can see that loading up right there. Now, Gravity Claw doesn't have the ability to
9:21
understand voice messages. So, as you can see, nothing's really happened. And I play this back. Okay, nothing. So,
9:28
what we're going to do is screenshot this and we'll go straight over to anti-gravity. And this is the process that we use to get any feature we want
9:34
to. Oh, and I should say, by the way, I'm going to show you something very cool, but let me give this prompt first. Hey there, dude. I would now like the
9:40
ability to send voice messages. I want you to repeat back to me what it says and then basically reply to it. Awesome.
9:46
So, send that one off. Let it And what I've also built for you is something really cool and I'll include a link for this down below in the
9:52
resources. But this is Gravity Claw. What I did is, and it's funny, I watched a video of my a buddy of mine called
9:57
Mark who was explaining all these different features and I thought it's such a good idea to build it into a dashboard. So, thanks for the
10:03
inspiration, Mark. Basically, what I've done is grabbed all the features from um OpenC, from Nanobot, Mimobot, all the
10:09
bazillion different bots, we don't know what they're called, and all the different features where what you can do is on this page scroll through I want
10:15
WhatsApp integration, I want Telegram integration, you know, maybe I want to have a look at voice capabilities, I'd like voice transcription, I'd like talk
10:22
mode. And you can basically go down and select and build like Lego bricks all the different features you want to.
10:28
Knowledge graph sounds good. And I've included a very simple description what it is. So your AI builds uh a web of connected effects like a mind map that
10:34
grows over time. That sounds cool. Context pruning, markdown memory, self memory. What tools do I want? I want to
10:40
give it this, this, and this. And you can literally come down and pick all the cool things that you want, the cool um
10:46
integrations, and kind of like drag and drop and pick the things that you want to. And when you've done that, like I've got 12 features in the basket. I come
10:52
down and click on generate prompt. And this is basically given prompts for all those things. So, all you do is copy the
10:58
clipboard, come back over then to anti-gravity, paste it in, and anti-gravity will create a plan to
11:04
integrate all these for you um simultaneously. So, I'll put a link for this down below so you can check that one out as well. Beautiful. So, voice
11:09
support is now live. The bot auto reloaded and is ready. One last thing, you need a free Gro API key for the
11:15
whisper transcription. So, head over to console.gro.com. So, let's sign up and grab one for free. I should also say, by
11:20
the way, if you gave it your open AI key, it will use the whisper transcription for you as well. So, this is a free one, but if you give it your
11:26
OpenAI API key, that will work for you instantaneously also. So, come over to console.gro.com and create an account.
11:32
And all you're going to do is create an API key right here, then it will appear for you at the top. Just simply copy that and then head back over to
11:37
anti-gravity. And here, we're going to come down and throw the key in. So, here is the key and paste that in there.
11:43
Okay. So, now we can test out with a voice message. Yo yo yo, test test. 1 2 3. Can you hear me? All right. So, we
11:49
sent that one off. Gravity claw is typing. So, we'll see what comes back and if it's done the transcription for us. You said yo yo yo test test test
11:56
test one two three can you hear me yo waves I hear you loud and clear test successful what's up now we've now we've
12:02
got voice messages coming back and forth so in my last one that I created it would send the message and then send this one it's pretty much as you prefer
12:09
I think it's great to see the message that you send I think that makes sense let me just make that change coming back into anti-gravity hey there dude I would
12:15
like you to send me the message that I said first and then reply afterwards please whilst anti-gravity is doing that
12:21
we're now going to get over to 11 labs that are doing some incredible things. These guys, by the way, have been
12:26
trailblazing the voice AI space for a very long time. What is really cool here is we're going to actually going to have
12:32
the ability. I want to give the ability to gravity claw to actually speak to me because sometimes I just want to listen.
12:38
I want to have that conversational type vibe. Let's supercharge it with that ability. Now, there's a lot of stuff
12:43
that 11 Labs are releasing soon. It's very cool. What we're going to do is go ahead and we're going to log into our
12:48
account. Now, when you actually come into 11 Labs now, you can see this great onboarding thing. So 11 labs created
12:53
text to speech sound effect studio speech to text voice is voice voice isolated voice changes. Then we've got
13:00
the 11 agents agents tools integrations knowledge base where basically you can build a suite of AI agents within 11
13:06
labs. For this video we're going to go with the 11 creative. I'm going to sign in. Of course we'll just fill in this
13:12
information. Let it know our preferred language. Well we're UK English but I don't think that changes. We're happy to
13:17
do this. Come down and click on next. And obviously if you have created an account you'll see there's many things we can do here. podcast, image, video,
13:22
speech to text, blah blah blah. We're going to go with text to speech. Now, the main thing we need is an API key.
13:27
So, going to come down to developer section, bottom left, and you click on instead of overview, click on API keys, and then come over here and click on
13:33
create key. I'm going to call this one gravity claw. I like to name my keys the thing that I'm using at the given time.
13:39
I find that very good. No need to restrict this one in my view. We know it poses risks, but in gravity claw, we
13:46
trust. Come down and create a key. And then you're going to copy this over here and head back over to anti-gravity. Beautiful. And then I'm going to come
13:51
down and explain it to her. And by the way, one of the reasons why I'm so stoked to be using 11 Labs in some of the builds that we're going to be doing
13:57
is because the new upgrades they've come out very, very, very low latency. And the biggest issue we've always found is
14:02
they don't sound like they're talking to humans. So they've built a lot of new emotional intelligence, I'm hearing, into these new models, which will just
14:09
make it sound way more humanlike. For us in this case, what we need to do is say something like the following. Awesome. I'd now like you to use the below 11
14:16
labs API key so that I can if I wish have my agent send me a voice message
14:21
back when I request and it will know how to do this dynamically based on the conversation. Awesome. Come down and
14:26
then give it your API key. And it's actually funny. So we're doing a meetup in London in a couple of weeks in the UK
14:33
and then we're doing one in LA for my community and then after that I think Japan and I know they did 11 Labs a
14:38
conference in London soon because they got some stuff heating up. It's always funny isn't it? You're traveling in different parts of the world. There's different cool things happening at
14:44
various different locations. So, you're going to try and network around and get to the right locations as you go. Oh, and by the way, if you'd love to come to
14:50
that, I'd love to welcome you. Buy you a coffee, put it in your hand, and say, "Hey, be super cool to see you there." Okay. And just like that, voice replies
14:56
are now live apparently. So, let's go ahead and test this one out by pulling up Telegram and asking it a question. Cool. So, let's ask it a question here.
15:03
Hey, the dude. Could you send me a voice reply saying, "Jack is a pretty cool dude." And send this one off. This is
15:09
law accurate information. So, we'll see if Gravity Claw can do it. And B, if it can't, we just say we go back and forth
15:15
and we just figure it out with anti-gravity, which is the awesome thing. Okay, send me a message there. I even click play. Let's see what it says.
15:22
Jeff is a pretty cool dude. All right, but wonder if I can actually ask a question. Hey, can you change the
15:27
voice? In fact, let's go over to anti-gravity and see if we can change it to a guy voice instead. Hey there, can
15:32
you change this to a guy's voice and make it UK British, please? It's funny. I have I was on a I literally got on
15:38
comments on my other videos and some guy said, "Dude, I loaded this video up. I thought I had it at 1.5x speed all the
15:44
way through." I do tell you to grab the coffees for a reason, guys. So, come down. We're going to accept this and we can configure and do all these different
15:50
swaps as we go through. And then let's come back. Hey, babe. Could you send me a voice message saying the sky is blue?
15:56
Beautiful. And let's wait for the message to come back from Gravity Claw. All right, let's play.
16:01
The sky is blue. All right, there we go. So, now we've got voice capabilities in both directions. Now we've got it
16:07
communicating with voice in both directions. The way that we need to level this up then is give it a
16:12
superhuman memory. And we can configure this in any way we want to. Which is why the third A in our clause framework
A
16:19
stands for archive. And so what we're going to do now is actually give it a prompt. So I'm going to say, hey there
16:24
dude, what I would like you to do is to create a memory system for gravity claw.
16:30
What I'm thinking is I want its ability to remember the entire conversation, but I also want it to semantically be able
16:36
to access the conversation. So maybe we have some kind of rag database. Maybe we have superb base with some SQL and we
16:44
connect that. Could you just do a little bit of research to find the best in-class memory system that would retain
16:50
context for the entire conversation, but also would save for us core bits of information and would remember and
16:55
almost feel like it wouldn't forget anything we ever said without restoring redundant information. Go ahead and
17:01
strategize what that best memory system might look like and come up with a suggested plan of action and connections that might be valuable. And then we're
17:07
going to let anti-gravity go and run and think about this. And I should also say, by the way, I have a very clear idea on
17:12
the solution. The reason why I've done this with you right now by asking it the question is because I I it's much more
17:18
valuable that you know how to fish then I give you the fish, right? I want to show you how you can troubleshoot. If
17:24
you have a desired outcome, how you can use anti-gravity to make your gravity claw pretty much whatever you want to.
17:30
And if I don't like it working a certain way, I don't like the weight stores memory. I want to try something else that you can't access in any of these
17:36
models anywhere else. I can build it in gravity claw no problem by just telling it this is how I want your memory to
17:41
function under these certain categories. Beautiful. So now it's done and it's actually built a graphic of what our memory system looks like. And the cool
17:47
thing is if we don't like it, we can change it and we can add different flavors and and and sort of different views on it. So we've got a three tier
17:54
memory system for gravity claw that makes the agent remember everything across restart architecture. One is core
17:59
memory which is always in the system prompt. Two is conversation buffer and then we have semantic long-term memory
18:05
and we have LLM calls and it's got everything down here for us. And then to activate it, we just need to give our Pine Cone API key. So, what I'm going to
18:11
say is, "Awesome, dude. I'll grab that pancreon API key. Could you just explain this memory system to us in a couple of
18:16
sentences with bullet points and why this is the best way to do it and under what circumstances it creates memories?"
18:22
Beautiful. So, we're going to head out over to Pine Cone to grab this API key. Pine cone, if you don't know, by the way, is a vector database. Will
18:29
basically let you store anything. You could throw encyclopedia bratannica into Pine Cone and it will store it that. And
18:35
so, the idea is we don't want to give all the context in every message because we'll burn through the context very very quickly. And by vectorzing it, what we
18:42
can do is only pull down the relevant stuff with this sort of semantic search. So on the left hand side, click on API
18:47
keys. And then we're going to create a brand new API key. And we'll call this one gravity claw. Uh we can have no
18:52
spaces. That's no problem. Click on create key. And then you come down and basically copy this key. And head back over to anti-gravity. And then close
18:59
this down. And then to explain what it's actually done here for us, right? So it's three layers. Layer one is a core
19:04
memory. It's always on. We've got a conversational buffer. We've got a semantic memory for long-term recall. When does it create memories? Every
19:09
single message is automatically saved to the conversation buffer and embedded in Pine Cone. After every exchange, the LLM
19:15
quietly scans a conversation for important facts, your name, preference, and deadline. When the agent decides what to do, it has a remember facts tool
19:21
they can explicitly use mid conversation, which is cool. And then we're also going to give it an initialization conversation. Cool. What
19:27
I'd also like you to do next is have my Gravity Claw go through a list of core
19:32
information to ask me questions that you think are relevant. And I want this com this information to be preloaded as
19:38
context in every single conversation I have. Make sure it's not too long so that the memory doesn't blow. But this
19:43
is core information I wanted to remember. Awesome. Here is my pine cone API key. Awesome. So now it is done. We got SQL light. Pine cone semantics
19:50
memory connected. Bot is running. Oh my goodness, guys. Everything is happening right now. And then we've got this initialization sequence. So let's go and
19:57
pull Telegram. Beautiful. And then let's ask it a question. So if I do for/ setup and see what happens. Great. I'm going
20:03
to ask you some questions. how freaking cool this is. So, what should I call you? Just call me Jack. That's cool. I'm
20:08
going go through all these different questions and explain everything. So, I put some random information just to skip by, but at any point we can run through
20:14
the setup again. So, I'm going to say, "Hey there, dude. I really like coffee and one of the things I really want to do this year is add as much value as
20:20
possible to my community and keep making it as amazing as possible and grow glider." Okay, cool. So, let's just say
20:26
that I'm just going to I'm going to throw something in there as like a fake memory and see what it says. And now what I also might do is say something
20:32
like by the way one of the things that you should know about glido is the fact it is a speechtoext startup. Okay great.
20:38
We can also if you want to create a soul.md for gravity claw. So we can say this is your compass of your personality
20:45
that we want you to behave like. Okay so now I'm going to say something like hey tell me what is glido to see if it
20:51
remembers. Give this a second. And look at this guys based on what you told me earlier this is what it is. Awesome guys. If we come over now to Pine Cone,
20:58
you can see we have gravity claw enabled. And I can click on this guy and take a look at it and we should start to
21:03
see some information. Look at this. Hey dude, one of the things I really want to do this year and it's got all that information saved in buying cone and you
21:08
connected all of it. How crazy is that? And the other thing I'd want to do is build a bit of a soul.md then for
21:14
gravity claw. So it has a personality and then we can say I want you to be friendly. I want you to challenge my ideas creatively. So let me give some
21:21
custom instructions. Hey, I want to create a soul.md for gravity claw. Basically, this is the way that it
21:26
behaves. And again, this needs to be added to every prompt behind the scenes. I want it to be constructive, but I want
21:31
it to challenge my thinking. I don't want it to be sycopantic. I want it to um be I don't want it to be overly
21:36
formal. I think casual is decent. Mirror my language, my vibe. Tell me how it how it is. Don't sugarcoat it. And always
21:43
try to find new things. Think about the question behind the question. Try to look around corners and be proactive in
21:49
the way that you think about things. Cool. Just a general prompt of how I like my AI to behave. challenge my thinking, help me think more clearly on
21:55
things. And so now we've got the memory lock down and the ability to communicate. The next thing that we're going to want to do is to give it
22:01
superpowers. And by superpowers, I mean connect it to any of the apps that you can already access with an anti-gravity,
W
22:08
which is why the fourth step is wire. And by wire, we just mean wire up our um
22:13
our actual service here. Now, what's really cool and interesting about this? Well, if you take this for example, okay, now in anti-gravity, if you've
22:19
seen any of my videos, you will know that we have MCPs, model context protocol, which is just universal
22:25
language of how anti-gravity can communicate with anything. What's really cool with Gravity Claw is that we can
22:31
actually leverage connections in our window. Now, let me show you what I mean. If you click on MCP servers, click
22:36
on manage MCP servers, you will see here a list of all the things that I already have connected to anti-gravity, right?
22:43
I've got notebook LM, I've got notion, I've got Superbase, Versel, um, Context 7. By the way, a little hack, Versel,
22:50
and the other one, which is going to be uh, GitHub, right? When you connect those two things, I that thing I showed
22:55
you earlier, that dashboard I built for you, I said I said deploy it immediately and give me a website URL. And it could
23:01
do that because I'm connected. But the really cool one is we've got Zappy connected in here as well, which is awesome. That lets me access things like
23:07
my emails and do everything else. So what we're going to do now, step one is to add all the MCPs that you want. Uh
23:13
the best process for that is simply enter it here. Does it exist? Let's see, for example, does Google exist? Uh it
23:19
does to a certain extent, but not Gmail, right? So you can add these MCPs yourself. You can head over to this
23:24
website and this is a list of every basically MCP that exists. You can find the ones that you like. Let's say for
23:30
example, you wanted playright. Not that you would need that. You've got GitHub, you've got code memory, you've got client, you have everything. So you can
23:36
literally find the ones that you like. So, I might say something like, "How about context 7?" Context 7 is an MCP
23:42
that gives, if you think about it like this, the ability for anti-gravity to know the latest documentation for
23:47
anything. So, look, this one's 601, this one's 45K, this one looks a little bit more legit. Just always make sure that
23:54
you're validating the MCP that you're installing, okay? Make sure you check out the GitHub and all that sort of stuff. What you can do is come into
23:59
readme and you will see that they have MCP server code there. So, you can copy this, come over to anti-gravity, and
24:05
then you can say, "Hey there, dude. I would like you to add this MCP to my MCP config. Okay? And then paste it in. And
24:11
then sometimes it'll need an API key. Like if it's Firefly as your meeting noteaker, you just grab that and install
24:16
it. I'll put a link on screen somewhere so you can see this in full detail of how you do this if you're still
24:21
wondering. Little hack by the way. If you click on view raw config, you can now see the title of this file. And what
24:27
I'd want you to do is to just add it. So do um shift at to get this and just type in the name. So ncpm mcp_config.
24:34
And that just tells anti-gravity, hey, I'm talking about this file. Now, it should do that automatically, but I want
24:40
you to do it so it is flawless. Then anti-gravity will update this file for you. That's how easy it is. Then once you've got all the MCPS that you want,
24:46
give it this prompt. Amazing. I would now like gravity claw to be able to leverage my MCP connections. For
24:53
example, I have Zapia and Zapia can let me ask questions about my emails or my meetings. Give Gravity Claw the ability
25:00
to do that. Okay, you see, I've just done what I call stated intention. I send that off. And by the way, guys, I
25:05
just want to draw your attention back to this implementation plan here. Look at this user sends message. This is the
25:11
system of how gravity claw works under the hood right now. How freaking cool is this? I think it's very, very freaking
25:16
decent. I love this. And we didn't touch a single thing. I remember a year ago when I was doing videos on pine cone,
25:22
people said, "Dude, that falls out of trees. What are you talking about?" And we'd have to show here's how you vectorize. Here's how you do this stuff.
25:27
Now we just blab for one of a better term into anti-gravity and it kind of does it. But knowing how to blab and
25:33
where to blab is I guess what they what they pay you for. It's quite it's quite important cuz all that is good knowledge to learn of course but really freaking
25:40
cool. So why this is so cool and why is this better than superbase? Let's double click into this and nerd out together
25:45
for a second on this. I've seen some videos doing this on superbase. So let's have a look at this. We have SQL live
25:50
and pine cone versus superbase and pg vector. So instant reads network hop every message. What else? The cost is
25:57
free. The setup is already installed. I guess we it saved us a bit on the setup here. data lives on our machine rather
26:03
than in superbase cloud. Uh and it's a lot simpler to do. So I think the performance is crazy. It's also
26:09
completed the MCP. So I'm gonna say hey there dude show me the implementation plan with the MCP and exactly what
26:14
you've done please. And meanwhile we can actually now check there cuz it said it is fully connected. So I might say something like hey there dude could you
26:20
go to my emails and tell me what was the subject line of the last email that I received. Bam. And we'll see now if
26:25
actually has the ability to access these MCPS cuz we're accessing our Gmail. there are Zappia MCP. So, giving it a
26:32
hot second and see if it can come back and let us know. It's taken a moment, so I'm assuming that it's actually doing the call in the background and then if
26:38
it's correct, it will give us some kind of information so we can actually see what's going on. And just like that, guys, your last email was verify your
26:45
account, which we know is true cuz we just did the blue host thing. This is crazy. It's got full access to our MCPs.
26:52
I think that is absolutely wild. So, anything you connect to anti-gravity, it now has. Cuz I don't know about you, but
26:58
I was really apprehensive about giving Claudebar access to the keys to the
27:03
kingdom of Gmail. Now we have the security and the protection with an anti-gravity on our MCPs in Gravity Claw
27:09
that's now running on our computer. It's not some random person's code. We've built this all together step by step
27:15
doing this incredible stuff. And so now we've given it the incredible ability to access any of our tools. So we can query
27:20
it about emails and calendars or whatever we want to do. The fifth and final step of our claws framework stands
S
27:26
for sense. Now sense is what's known as the heartbeat. It's what makes it feel
27:32
human. It's the ability for gravity claw to by itself reach out and message. Hey
27:37
Jack, haven't seen your weight bean trapped for the past 5 days. Have you been leaving those cupcakes alone? That's the kind of accountability that I
27:43
need over here in the JR household. So we're going to give the ability for gravity claw to do that. And exactly how
27:48
we do that, by the way, is to come over and tell it that. So, uh, what we're going to do is bring this over and be
27:53
specific. So, uh, we've also got the implementation plan, by the way, of what it's done for everything, which I think
27:59
is so freaking sick. So, let's go over here and give it some information. Hey, dude, I now want you to install a heartbeat. I want the ability for
28:05
Gravity Claw to reach out to me by itself. Specifically, let's set up some kind of system where Gravity Claw
28:12
reaches out to me every day at, let's say, 8 a.m. and sends me a message. And in this message, I basically want it to
28:19
ask for accountability on Jack, have you tracked your weight? What's the biggest goal that you want to achieve today? Of
28:24
course, it knows all the previous things that I've said. I might even at some point ask it to do some research on
28:29
analysis and trends, but just set that up so it runs every day at 8 a.m. for me, please. Now, the cool thing is we
28:35
can in natural language explain this to anti-gravity to give it that heartbeat so it can send us that message and then
28:42
we can actually have that back and forth with it, which is crazy. And what I'm also going to say is just to validate that it works get gravity claw to send
28:48
me a message right now so I can see that it can actually send me that stuff by itself. Beautiful. And almost by magic
28:54
it's done it. So let's check it out now. So it's installed a node cron. And if you remember from open claw the you installed this chron jobs we've just
29:00
installed it here in gravity claw. It's created a heartbeat.ts and updating an index.ts. And by if you're what is
29:06
gravity claw gravity claw is everything that you see here. How freaking cool is this? But it's basically it. It's freaking sick as hell. It's so so cool.
29:13
Anyway, running type check and verifying bot restore the heartbeat text message, which is what it did. Fixing heartbeat. So, heartbeat is live. Check your
29:19
telegram. Grabs club just sent you it first accountability checkin. It's going to happen every day 8 a.m. It loads your memory context. Asks about weight
29:26
tracking in one goal for the day. Uses a lightweight LLM call. 500 tokens max so it doesn't burn through credits. Cool.
29:32
Well, let's go over it and see. Did we get a message on our Telegram? I open it up and we do. Good morning, Jack. Hope
29:38
you're crushing Tuesday already. Quick time to check in. Have you stepped in Skull today yet? What's one thing you want to demolish today? Bam. So now it's
29:44
reaching out to me and sending me these messages. And so this is excellent, but what if our laptop is closed down? What
29:49
if we're off to the gym or to grab some beautiful Turkish eggs and coffee and we want to have this message? Well, at the
29:55
moment, Gravity Claw is running on our desktop, so it wouldn't actually do that. But one service that we could use
30:00
if we want to to do this is something called railway. Now, the idea with railway, I'll pull up here for you, is
30:05
this will allow us to remotely send off stuff. So the idea with railway is we can basically have this then to kind of
30:11
run it for us so that we can actually communicate with it whether our laptop is closed or not and you have two levels
30:17
of security. Railway has no open ports. If you compare it to VPS VPS is like
30:23
being in a house. Anyone can knock on the door, try the ports and open the doors. Obviously you can protect that. Of course you can. But railway is like a
30:29
guy in a locked room making phone calls out there. No one really knows that it exists. And then of course we've also
30:35
whitelisted it so no one can send the messages. So, if you come over to Railway, click on deploy or just create
30:40
a new account over here. And when you've done that, you'll land on a page that looks a little bit something like this. Really cool. So, the next thing we do is
30:46
head back over to anti-gravity. So, then basically we come back to anti-gravity. This is what I want you to do. Set it up for our gravity claw bot. You're going
30:52
to install the railway CLI and deploy the bot to railway using the rail up verify blah blah blah. Send it off. I'll
30:58
put this link down below, this uh text down below so you can use it. But effectively, you can't do as much if you
31:03
self-host. If you self host, you can have so many things on there, right? You could have n on there. You could have
31:10
open call, you could have a billion different things. This is just for a very very specific use case where we want to be able to chat with it and yap
31:16
with it all the time. So come down allow for this conversation. Cool. So it's given us a browser login. So what it wants to do is to basically copy this
31:22
and then give it the pairing code. So we're going to accept this file right here and basically we're going to click on this and then we load here. It will ask you to verify that it's the same
31:28
parenting code, which it is. And once you've done that, it is now fully connected. So we didn't need to f around anything. It did it all for us by itself
31:34
which is so cool. Beautiful. And now Gravity Claw is lab on railway soul loaded. Zappy MCP connected heartbeat
31:41
scheduled. Let's click on the dashboard and check it out. And we've got review documentation. So let's come and have a look at that as well. But open up the
31:47
dashboard first of all. And I'm going to take this one out. And what do we see when we load up Gravity Claw? We have it in the middle. Very, very cool. Let's
31:54
click on this guy. Deployments. Very, very cool. And we've got our variables. As you can see, everything's below that
31:59
here. So we can see what everything's connected to. if you rotate tokens or want to add things that's possible but again anti-gravity did all this for us
32:05
and we've got all the deployments here you can click on this and then view all the logs and everything that you'd like to beautiful and just explain this
32:11
walkthrough guide so you know exactly what's going on here so what is the same as running locally and we've got how do
32:16
you push updates so whenever you change the code this can be pushed now the great news is anti-gravity can just do that for you and we can turn this into a
32:22
skill so just like we've done and this step is optional by the way this is just if you want it to run when your laptop's closed down right that's all it really
32:28
is so anti-gravity can do this for you which which is great. So you don't need to worry about that. But it's explaining how do you do it and where your
32:34
dashboard is. So is it the same functionality is running locally? Yeah. Telegram messaging all the different
32:39
stuff that we've added anything that we add and again any changes we make this will push it live to railway. What is
32:44
different? SQL light resets and redeploy. It basically just means you know our bot now is already taking any
32:50
important information and putting it along to memory. But basically that will just change as it goes. The other thing just watch out is to never run it both
32:56
in Rowway and your laptop which you won't need to do because again you're not essentially running it. in railway now which is great. So now that's done
33:03
the last thing that we realistically want to do is create a skill for anti-gravity to basically know how to
33:08
update railway with any changes. So we don't need to touch anything. So let's open this up and I'll say something like
33:13
hey there dude I would like for you to create a skill such that if you and I going back and forth and playing around
33:19
with this and deploying changes to railway that I don't have to touch railway you can deploy any new changes
33:24
any new features. you confirm with me advance, you do those changes and then we go back and forth to make sure that it works perfectly. Cool. And then
33:30
anti-gravity can develop a skill for us to go ahead and do that. The other thing that you could do is have a version
33:36
locally that you run on a separate Telegram account and then you kind of we call this like a staging app and when
33:41
you're happy with that you can push it live. So either one works completely fine. It's whatever you prefer. And actually guys, even better than that is
33:47
this system which is whenever you want to make changes to Gravity Claw. What we're going to do is we're going to pause railway p freeze that and then
33:54
we're going to run it locally. You can go back and forth just like we've done in this video. Make it perfect. And when you're like, "Dude, I'm ready for the
34:00
next level of gravity claw." We post it to railway and we stop running it locally. Meaning that it's never running
34:06
in two places at the same time. It's super simple. It's It's not going to cuz otherwise it'll send two the same
34:11
messages to everything if it's running twice. This way it's only running in one location. You can spar back and forth
34:17
with anti-gravity. Get it working perfectly, make your changes and send it up there. I've done this in a skills.mmd
34:24
and a deployment.mmd. And what I'm going to do is share with you both of those uh in the free resources section so you can
34:30
copy and paste it and leverage it and just start rocking it with gravity claw. Now, running a Gravity Claw instance is
34:35
one thing, but it's never going to be at its maximum level unless we actually understand all of the hidden
34:40
capabilities in anti-gravity, which we can learn by watching this video right Yeah.

<!--end transcript-->