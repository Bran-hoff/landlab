How we do it:

1. To start developing with the Landlab Community, start here: [Developer Installation Instructions](https://landlab.readthedocs.io/en/master/development/install/index.html#developer-install)

Follow instructions and you will have your own fork, just like University of Washington Landlab developers: e.g  github.com/ChristinaB/landlab   github.com/ - shelby -fix this/landlab      zhuoran    jeff

2.  The second that your fork is created, it may quickly be out of sync with the main trunk - [Keep Landlab Updated](https://landlab.readthedocs.io/en/master/development/install/updating.html)

$ git fetch upstream

[to do - address nuances of what to fetch when working on a team, origin? upstream? whose remote? 

3.  Create a new branch

4.  Add Collaborators

5.  Deveop on a Collaborator Branch, develop on your remote, keep your master updated to the Collaborator branch

6.  Add, commmit and do a pull request to add your contributions to a Landlab branch

`git pull-create-pull-request localBranch git@github.com:user/repo originBranch`

## Why do all of the above steps make life easier in the future? 

7.  Managing Pull Requests on github/landlab master branch

## Branch Enlightenment (for dark moments detangling workflows)

1.  Fatal error!  The system cannot find the file specified.  If you are on your desktop in your developer Landlab folder, and you have added a branch, and on the correct branch, but get an error trying to set upstream, add remote, fetch or pull changes from the URL repository (you know they are there, you can see them, why can't you get them on the desktop!).   The solution is likely if you resolve the "upstream confusion" that may have occurred when you set up the branch and used git:// instead of https://   Here is an example of the error message from Github Desktop. [!img](https://github.com/ChristinaB/landlab/blob/ChristinaB-kickstart/docs/source/images/annoyingbrancherror.png)

$ 
