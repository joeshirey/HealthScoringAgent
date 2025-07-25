# Contributing to HealthScoringAgent

First off, thank you for considering contributing to HealthScoringAgent! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, [make one](https://github.com/joeshirey/HealthScoringAgent/issues/new)! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

If you have a general question, feel free to ask in the [discussions](https://github.com/joeshirey/HealthScoringAgent/discussions).

## Fork & create a branch

If this is something you think you can fix, then [fork HealthScoringAgent](https://github.com/joeshirey/HealthScoringAgent/fork) and create a branch with a descriptive name.

A good branch name would be (where issue #33 is the ticket you're working on):

```sh
git checkout -b 33-add-new-agent
```

## Get the style right

Your code should follow the PEP 8 style guide. You can use a tool like `flake8` to check your code for compliance.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with HealthScoringAgent's master branch:

```sh
git remote add upstream git@github.com:joeshirey/HealthScoringAgent.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 33-add-new-agent
git rebase master
git push --force-with-lease origin 33-add-new-agent
```

Finally, go to GitHub and [make a Pull Request](https://github.com/joeshirey/HealthScoringAgent/compare)

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

To learn more about rebasing and merging, check out this guide on [merging vs. rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing).

Once you've rebased your branch, you'll need to force push the changes to your remote branch.

```sh
git push --force-with-lease origin 33-add-new-agent