![Banner](https://user-images.githubusercontent.com/74678283/189533990-0176495e-3d9c-4129-a029-e5e842ae1f9d.png)

<h2 align="center">What is RollerPredicter?</h2>
<p align="center">
  RollerPredicter is an open-source Rollercoin prediction tool that generates a graph showing the variation of your balance over time.
</p>

<br>

<h2 align="center">What can it be used for?</h2>
  - It can be used to determine how long it'll take you to reach your goal balance (though its precision depends on your consistency of playing).<br>
  - It can help you choose which miner to buy between many by visualizing what happens after you purchase each one.<br>
  (this can also be applied on a group of miners in a specific order, more info on that later where I explain how the tool works).

<br>
<br>

<h2 align="center">How to Download RollerPredicter?</h2>

  Simply go to the [releases](https://github.com/dtomper/RollerPredicter/releases) page and download the latest version.<br>
  If you want to execute RollerPredicter directly from Python, then ```pip install -r requirements.txt``` and you're all set :)

<br>

<h2 align="center">How to use RollerPredicter?</h2>
<h3>Basic Usage</h3>

Have a look at this chart:
![chart](https://user-images.githubusercontent.com/74678283/189545335-5a16e366-44c6-4335-8011-618b0a3885f8.png)
These are the main entries that you need to fill before doing anything.<br>

#### Note that in the second entry, I wrote 2757 instead of 2.757 even though it's written in Rollercoin, that's because I subtracted 77.505 Th/s from 2.757 Ph/s. If you ever end up with a graph that doesn't make sense, check your units.<br>

Right now, if we click on the Generate button, this graph should show up:
![graph1](https://user-images.githubusercontent.com/74678283/189545908-17c2d36b-6519-4560-8566-921f990b2de5.png)

![graph1_zoomed](https://user-images.githubusercontent.com/74678283/189546214-69b54d35-4101-489d-b7b1-f465a8e670be.png)

Unforunately, my mouse isn't showing in the screenshot, but that box shows up when you hover over the graph. It shows you the predicted data at that instant.<Br>

Now you're probably wondering, what the heck is a scenario? Let me first add some miners and I'll tell you ;)<br>

<br>

<h3>Adding Miners</h3>

![graph2](https://user-images.githubusercontent.com/74678283/189548041-c49d26d3-3839-4647-a5a2-d0a5615b9185.png)

The miner I added has a Hashrate of 110 Th/s, a Bonus of 3% and is worth 7 RLT (I came up with this price). <br>
As you can see in the graph, our balance kept growing until it reached 7 RLT, it then fell off suddenly because we bought the miner. The power (without bonus) went from 2.679 Ph/s to 2.789 Ph/s (That's a 110 Th/s increase), and the bonus went from 1.91% to 4.91% (3% increase). <br>
<br>
So now that you understand how the prediction works for 1 miner, let's try 3 miners:

![graph3](https://user-images.githubusercontent.com/74678283/189548488-7ee14633-f0a5-4a41-a288-e8ce5c13f647.png)

The three miners in the picture above are:

|  | Hashrate | Bonus | Price |
|--|--|--|--|
| 1 | 110 Th/s | 3 % | 7 RLT |
| 2 | 500 Th/s | 1 % | 3 RLT |
| 3 | 8 Ph/s | 5 % | 5 RLT |

If only the last miner was a thing in Rollercoin 😩

<br>

<h3>Adding Scenarios</h3>

Okay, so I said previously that you can use RollerPredicter to compare miners (or groups of them) in a single graph. That's where the word "scenario" comes in. The 3 miners in the picture above represent a scenario (the scenario where we buy miner 1 then 2 then 3).<br>
The following picture shows us the importance of ordering our purchases:

![graph4](https://user-images.githubusercontent.com/74678283/189549265-4e2f710f-8278-48d8-9bae-f8c33a0ad776.png)

I created a new scenario and added the same 3 miners we added before, but I swapped the first two:
|  | Hashrate | Bonus | Price |
|--|--|--|--|
| 1 | 500 Th/s | 1 % | 3 RLT |
| 2 | 110 Th/s | 3 % | 7 RLT |
| 3 | 8 Ph/s | 5 % | 5 RLT |

And as you can see, the second scenario's graph is above the first one, so it's more profitable.<br>

<h3>That's it! You are now ready to rock.</h3>

<br>

*It took me a week to make this app, if you appreciate my hardwork and want to see more of my projects, feel free to follow me on my social media. I'm available at:*<br>
<br>
[<img src="https://user-images.githubusercontent.com/74678283/189550373-d9db605d-def5-45d5-8327-a1ba756066e7.png">](https://www.youtube.com/Dtomper)
[<img src="https://user-images.githubusercontent.com/74678283/189550475-986be6d3-7268-4228-9c3f-c6040834a275.png">](https://www.instagram.com/dtomperyt/)
