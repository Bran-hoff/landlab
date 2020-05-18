How we do it:

1. To start developing with the Landlab Community, start here: [Developer Installation Instructions](https://landlab.readthedocs.io/en/master/development/install/index.html#developer-install)

Follow instructions and you will have your own fork, just like University of Washington Landlab developers: e.g  github.com/ChristinaB/landlab   github.com/ - shelby -fix this/landlab      zhuoran    jeff

2.  The second that your fork is created, it may quickly be out of sync with the main trunk - [Keep Landlab Updated](https://landlab.readthedocs.io/en/master/development/install/updating.html)

$ git fetch upstream

[to do - address nuances of what to fetch when working on a team, origin? upstream? whose remote? 

3.  Create a new branch

4.  Add Collaborators

Branch leaders - Add Collaborators to your Branch in Github, Settings, Manage Access, Invite Collaborators. 

Branch contributors: 
Code to jump onto Allison's branches:
open git-bash (or your preferred terminal) within your local landlab branch
check your remotes with $git remote -v (if you don't see a remote with a link to her fork of landlab, you'll need to add one)
add allison's fork as: $ git remote add pfeiffer https://github.com/pfeiffea/landlab.git
then get her work from this remote with: $git fetch pfeiffer
go into whatever your preferred branch of her fork as $git checkout 'branch_name' (ex. $git checkout create_bed_sed_initializer)

To push changes you've made:
$git add 'file/name/here'
$git commit -m "here are my comments on these changes"
$git push

you may also need to '$git pull' before you push

5.  Deveop on a Collaborator Branch, develop on your remote, keep your master updated to the Collaborator branch

6.  Add, commmit and do a pull request to add your contributions to a Landlab branch

`git pull-create-pull-request localBranch git@github.com:user/repo originBranch`

## Why do it this way ? All these steps make life easier in the future. We promise. 

7.  Managing Pull Requests on github/landlab master branch

## Branch Enlightenment (for dark moments detangling workflows)

Help!1. **Fatal error!  The system cannot find the file specified.**  If you are in a terminal on your desktop in your developer Landlab folder, and you have added a branch, and `git status` says you are on the correct branch, but you get an error trying to set upstream, add remote, fetch or pull changes from the URL repository (you know they are there, you can see them, why can't you get them on the desktop!).   The problem is that your branch has "upstream confusion" which likely occurred when you set up the branch and used git:// instead of https://   Here is an example of the error message from Github Desktop. ![](https://github.com/ChristinaB/landlab/blob/ChristinaB-kickstart/docs/source/images/annoyingbrancherror.png)

`git remote set-url origin new.git.url/here`

or you can just edit `.git/config` and change the URLs there. The `.git/config` file is where all the magic happens. 

or you can open the repository in Github Desktop and get help from friendly GUIs. 
 
To solve the issue above, I ran
`git remote set-url origin https://github.com/landlab/landlab/`
`git fetch` 
to get all the files branches and updates from the Landlab Team.
then 
`git remote set-url origin https://github.com/ChristinaB/landlab/`
`git fetch' 
to get all the changes I've made recently in my fork of Landlab, using my Landlab repository URL.  
