# Skills 
## Transcript
Agent Skills in VS Code
0:00
Agents are smart, but skills make them
0:02
unstoppable. And they're now available
0:04
inside of VS Code. Agent skills are
0:07
folders of instructions, scripts, and
0:09
resources that load on demand to perform
0:11
specialized tasks. And best of all,
0:13
they're an open standard. They really
0:16
help tailor agents for domain specific
0:18
tasks, reducing repetition, and they let
0:21
you compose complex workflows. So from
0:24
how you build a project, perform web
0:26
testing, manipulate images, write
0:28
documentation, or even set up full CI
0:30
systems, skills make agents know how to
0:33
do the work and how you want it to be
0:35
done. So let's take a look at how to
0:37
build and trigger your first skill
0:39
inside of VS Code. To get started using
Demo
0:43
skills, head into your settings and
0:45
enable use agent skills. Once you do,
0:47
skills and resources can be loaded from
0:49
several different locations. Here I have
0:51
a brand new project and I write a lot of
0:52
PRDs or product requirement documents. I
0:55
want to create a skill to help me
0:56
streamline that process. So in my GitHub
0:58
folder with my agents, prompts and
1:00
custom instructions. I have a skills
1:02
folder. Now inside this folder will be a
1:04
bunch of different subfolders containing
1:06
each of the different skills for my
1:08
project. So I'm going to create a new
1:09
folder called PRD writing. And inside of
1:14
this folder will contain at least a
1:17
skill.md
1:18
file that outlines the skill itself. And
1:21
it may have other resources as well such
1:23
as JavaScript files or images or other
1:25
things like that. So here I've created
1:28
what I like for creating PRDS or my main
1:31
workflow. Now up top we have some front
1:34
matter that defines the name and when
1:37
specifically an agent may want to use
1:39
this skill. So here when I'm creating
1:40
PRDS and then I define my workflow for
1:43
example when exactly I want to use it my
1:46
stages such as context gathering section
1:50
drafting and then validation. So this
1:52
gives a full workflow that the agent is
1:56
now aware of. So that means if I come
1:58
down and I start to draft up a message
2:01
of what I want the agent to start
2:03
working on, I can say, "Let's write a
2:06
PRD
2:08
for a new website to create and share
2:12
agent skills."
2:14
So now it will use its references and
2:17
resources and take a look to see if a
2:20
skill is available. And yep, sure
2:22
enough, it's read the skill, which is
2:24
the PRD writing skill. And we can see
2:28
that it is now drafting in stage one the
2:31
context gathering to help me start to
2:34
build this PRD out and it will continue
2:36
on using that skill. This is natural as
2:39
part of my process as I'm asking the
2:41
agent to write code draft documentation.
2:45
It can be aware of the skill and loaded
2:48
on demand for me. Now, I mentioned this
2:50
is an open standard, which means this
2:51
skill can be transferable to other
2:53
agents that are compatible with agent
2:55
skills such as the GitHub copilot cloud
2:57
agent and also the CLI. Okay, we just
3:00
built and used our very first agent
3:02
skill. But what does it look like in
3:03
everyday development? Well, here I have
3:05
the source code for one of the websites
3:06
that I built, visual studio
3:08
wallpapers.com, that, as you guessed it,
3:10
has a bunch of wallpapers for a bunch of
3:12
different screen sizes for Visual Studio
3:14
and VS Code. Now, here I have many
3:17
skills. I do tons of image manipulation.
3:20
So I have an skill specifically on how I
3:22
like to use image magic to do resizing,
3:26
conversions, batch processing a lot more
3:29
and what commands and how to locate it.
3:31
I have one specifically on PRD writing
3:33
that we just saw and a skill for web
3:35
testing. So how to interact with the web
3:37
page using playwright and even how to
3:39
build out tests. I even have a test
3:41
helper JavaScript file as a resource
3:43
that the skill can use. And this is
3:45
leveraging progressive loading. And
3:47
that's what makes skills different from
3:48
instructions. They come with more files
3:50
that can be loaded on demand when
3:52
they're needed. So here inside of the
3:54
agent chat, we can see that I asked it
3:56
what skills are available. And it's
3:59
identified the three skills and it shows
4:02
that different metadata description that
4:05
made it aware of when specifically it
4:08
would use one of those skills. So, I
4:11
come down to the chat and I'm going to
4:12
ask it to resize all of the images in
4:14
the 1080p folder into the 720p folder.
4:18
And what we'll see is that it will use
4:20
these references to identify that it has
4:23
the skill available. There it is, of
4:25
image manipulation.
4:27
It will then understand how to do batch
4:30
processing and what commands
4:32
specifically to call and how to locate
4:34
image magic on my machine or anybody's
4:37
machine. And now if we go over, we can
4:39
take a look. And sure enough, I have all
4:41
of my 720p images ready to go. Agent
In Summary
4:45
skills aren't just fancy instructions.
4:46
They're portable test specific workflows
4:48
that load only when you need them. So
4:50
unlike custom instructions, which are a
4:52
set often of coding standards, skills
4:54
bring scripts, examples, and automation
4:56
into the mix, making agents truly
4:59
actionoriented. So get started today and
5:02
build your first skills and start using
5:04
them inside of VS Code. And as always,
5:06
happy coding.