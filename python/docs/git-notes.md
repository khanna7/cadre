# Possible workflow to manage branching a complex branching structure


## Visualizing Branching

### Fetch all branches from remote 
(if they are included in the scope of examining the branching structure)

```
git fetch --all
```

### All  local branches and remote branches that are fetched

```
git log --all --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
```

### Specific (`master`) branch 

```
git log master --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
```

### Last 5 commits on specific (master) branch

```
git log -5 master --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cd) %C(bold blue)<%an>%Creset' --abbrev-commit --date=local
```

## Last Commit 
### Last commit made on on each local branch
```
git for-each-ref --sort=-committerdate refs/heads/ --format='%(color:yellow)%(refname:short)%(color:reset) - %(color:red)%(objectname:short)%(color:reset) %(contents:subject) %(color:green)(%(committerdate))%(color:reset) %(color:bold blue)<%(authorname)>%(color:reset)'
```

### Fetched remote branches not in local
```
git for-each-ref --sort=-committerdate refs/remotes/ --format='%(color:yellow)%(refname:short)%(color:reset) - %(color:green)%(authorname)%(color:reset) (%(color:red)%(committerdate:relative)%(color:reset)): %(color:bold blue)%(contents:subject)%(color:reset)'

```


## Relative Commits
### Commits in branch `branch_A` that are not inz `branch_B`

```
git log branch_B..branch_A
```

## Decisions
Based on the above output, make decisions 
to delete or merge branches as necessary.  

Some sample criteria:

### Commit date
Older branches that have not been updated for a long time may no longer be relevant and could be candidates for deletion, assuming their changes are either merged or abandoned.



### Has the branch been merged into `master` or another relevant "target"?

```
git branch --merged master
```

## Stale branches
Consider creating a tag at its last commit to preserve its final state and discuss with team
```
git tag archive/<branch_name> <branch_name>
```

Push tag to remote
```
git push origin archive/<branch_name>
```

## Reproducibility
Tagging the version of code used for the results in a paper "Paper_XYZ": 


```
git tag Paper_XYZ <commit_hash>
```

Push tag to remote:

```
git push origin <tag_name>
```

## Branch Deletion

### Local
```
git branch -d <branch_name>
```

### Remote
```
git push origin --delete <branch_name>
```