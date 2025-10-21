# How to Use Git Worktrees with Claude

## Table of Contents
- [What Are Git Worktrees?](#what-are-git-worktrees)
- [Why Use Worktrees with Claude?](#why-use-worktrees-with-claude)
- [Setup Guide](#setup-guide)
- [Common Workflows](#common-workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Examples for SpellSmut Project](#examples-for-spellsmut-project)

---

## What Are Git Worktrees?

Git worktrees allow you to have **multiple working directories** for the same repository, each checked out to different branches. Instead of constantly switching branches with `git checkout`, you can work on multiple branches simultaneously in separate directories.

### Key Benefits
- ✅ No need to stash changes when switching branches
- ✅ Work on multiple features in parallel
- ✅ Safe experimentation without affecting main branch
- ✅ Easy side-by-side comparison of different implementations
- ✅ All worktrees share the same `.git` repository (saves disk space)

---

## Why Use Worktrees with Claude?

When working with Claude (or any AI coding assistant), worktrees provide several advantages:

### 1. **Parallel Development**
Have Claude work on multiple features simultaneously without branch switching:
- Feature A in `SpellSmut-feature-a/`
- Feature B in `SpellSmut-feature-b/`
- Main development in `SpellSmut/`

### 2. **Safe Experimentation**
Let Claude make aggressive refactoring or experimental changes in a worktree while keeping your main branch stable.

### 3. **Easy Rollback**
If Claude's changes don't work out, just delete the worktree - your main branch is untouched.

### 4. **Code Comparison**
Have Claude analyze differences between implementations across branches.

### 5. **Testing Isolation**
Test mods or changes in a separate worktree without affecting your development environment.

---

## Setup Guide

### Prerequisites
- Git 2.5+ (worktrees were introduced in Git 2.5)
- Basic understanding of Git branches

### Check Git Version
```bash
git --version
```

### Basic Worktree Commands

#### 1. **Create a Worktree**
```bash
# Create worktree from existing branch
git worktree add <path> <branch-name>

# Create worktree with a new branch
git worktree add -b <new-branch> <path>

# Create worktree from a specific commit
git worktree add <path> <commit-hash>
```

#### 2. **List All Worktrees**
```bash
git worktree list
```

Output example:
```
/h/SpellSmut              abc1234 [master]
/h/SpellSmut-feature      def5678 [feature/audio]
/h/SpellSmut-experimental 9876543 [experimental]
```

#### 3. **Remove a Worktree**
```bash
# Remove worktree (must be clean or use -f)
git worktree remove <path>

# Force remove (discards changes)
git worktree remove -f <path>

# Clean up stale worktree references
git worktree prune
```

#### 4. **Move a Worktree**
```bash
git worktree move <old-path> <new-path>
```

#### 5. **Lock/Unlock a Worktree**
```bash
# Lock (prevents automatic pruning)
git worktree lock <path>

# Unlock
git worktree unlock <path>
```

---

## Common Workflows

### Workflow 1: Feature Development

**Scenario**: You're working on a new spell system while maintaining the current code.

```bash
# In your main repository
cd H:\SpellSmut

# Create worktree for new feature
git worktree add -b feature/new-spell-system ../SpellSmut-spell-system

# Now you have:
# H:\SpellSmut (main branch)
# H:\SpellSmut-spell-system (feature branch)
```

**With Claude**:
1. Open both directories in your editor workspace
2. Ask Claude: "Work on the spell system in `SpellSmut-spell-system`"
3. Continue main development in `SpellSmut` without interference

### Workflow 2: Bug Fixes

**Scenario**: Critical bug needs immediate fix while you're mid-feature.

```bash
# Create hotfix worktree
git worktree add -b hotfix/critical-crash ../SpellSmut-hotfix main

# Fix the bug in SpellSmut-hotfix
# Your feature work in SpellSmut remains untouched
```

### Workflow 3: Code Review & Comparison

**Scenario**: Compare two different implementations.

```bash
# Create worktrees for both approaches
git worktree add ../SpellSmut-approach-a feature/approach-a
git worktree add ../SpellSmut-approach-b feature/approach-b
```

**With Claude**:
- "Compare the magic system implementation in `SpellSmut-approach-a` vs `SpellSmut-approach-b`"
- "Which approach has better performance?"

### Workflow 4: Experimental Refactoring

**Scenario**: Major refactoring that might not work out.

```bash
# Create experimental worktree
git worktree add -b experimental/refactor-architecture ../SpellSmut-experimental

# Let Claude make aggressive changes here
# If it works: merge it
# If it doesn't: just remove the worktree
```

### Workflow 5: Testing & Validation

**Scenario**: Test mods without touching development environment.

```bash
# Create testing worktree
git worktree add ../SpellSmut-testing main

# Run tests, install mods, break things - main repo is safe
```

---

## Best Practices

### 1. **Naming Convention**
Use clear, descriptive names for worktree directories:

```bash
# Good
../SpellSmut-feature-audio
../SpellSmut-hotfix-crash
../SpellSmut-experiment-lua5

# Avoid
../temp
../test
../new
```

### 2. **Directory Organization**
Keep worktrees organized:

```
H:\
├── SpellSmut\                    # Main repository
├── SpellSmut-features\           # Feature worktrees
│   ├── audio-system\
│   ├── ui-overhaul\
│   └── multiplayer\
├── SpellSmut-hotfixes\           # Hotfix worktrees
│   └── crash-fix\
└── SpellSmut-experimental\       # Experimental worktrees
    └── lua-upgrade\
```

### 3. **Clean Up Regularly**
Remove worktrees you no longer need:

```bash
# List all worktrees
git worktree list

# Remove unused ones
git worktree remove ../SpellSmut-old-feature

# Prune stale references
git worktree prune
```

### 4. **Branch Management**
Delete feature branches after merging:

```bash
# After merging feature
git worktree remove ../SpellSmut-feature
git branch -d feature/name
```

### 5. **Avoid Conflicts**
Don't check out the same branch in multiple worktrees - Git will prevent this.

### 6. **Document Active Worktrees**
Keep a list of active worktrees and their purposes:

```bash
# Create a worktree log
git worktree list > worktrees.txt
```

---

## Best Practices with Claude

### 1. **Explicit Path References**
Always specify which worktree Claude should work in:
- ❌ "Update the sound system"
- ✅ "Update the sound system in `SpellSmut-audio-feature`"

### 2. **Add Worktrees to Editor Workspace**
Make sure all active worktrees are added to your editor's workspace so Claude can access them.

### 3. **Use Worktrees for Isolated Tasks**
Create a worktree for each major task Claude is working on:
```bash
git worktree add -b claude/refactor-spells ../SpellSmut-claude-refactor
```

### 4. **Branch Naming for AI Work**
Consider prefixing branches that Claude works on:
```bash
git worktree add -b ai/feature-name ../SpellSmut-ai-feature
```

### 5. **Regular Syncing**
Keep worktrees up to date with main branch:
```bash
cd ../SpellSmut-feature
git fetch origin
git rebase origin/main
```

---

## Troubleshooting

### Problem: "Fatal: invalid reference"
**Solution**: The branch doesn't exist. Create it first:
```bash
git worktree add -b new-branch ../SpellSmut-new
```

### Problem: "Worktree already locked"
**Solution**: Unlock it:
```bash
git worktree unlock <path>
```

### Problem: "Cannot remove worktree, changes present"
**Solution**: Either commit changes or force remove:
```bash
git worktree remove -f <path>
```

### Problem: Worktree directory deleted manually
**Solution**: Prune stale references:
```bash
git worktree prune
```

### Problem: Can't checkout same branch in multiple worktrees
**Solution**: This is intentional. Create a new branch from that branch:
```bash
git worktree add -b new-branch-name ../path existing-branch
```

### Problem: Disk space concerns
**Solution**: Worktrees share the `.git` directory, so they use much less space than full clones. Only working files are duplicated.

---

## Examples for SpellSmut Project

### Example 1: Audio System Overhaul
```bash
cd H:\SpellSmut
git worktree add -b feature/audio-overhaul ../SpellSmut-audio
```

**Claude Instructions**:
"In `SpellSmut-audio`, refactor the `DrwSound.lua` script to support dynamic sound loading and improve 3D audio positioning."

### Example 2: Lua Modernization
```bash
git worktree add -b upgrade/lua-5.4 ../SpellSmut-lua54
```

**Claude Instructions**:
"In `SpellSmut-lua54`, upgrade all Lua scripts from 4.0 to 5.4 syntax, starting with `DrwFiles.lua` and `DrwSound.lua`."

### Example 3: Mod Development
```bash
git worktree add -b mod/enhanced-graphics ../SpellSmut-mod-graphics
```

**Claude Instructions**:
"Create a graphics enhancement mod in `SpellSmut-mod-graphics` that improves texture quality and adds new visual effects."

### Example 4: Bug Fix While Working on Feature
```bash
# You're working on features in main SpellSmut directory
# Critical bug reported!

git worktree add -b hotfix/sound-crash ../SpellSmut-hotfix
```

**Claude Instructions**:
"In `SpellSmut-hotfix`, investigate and fix the sound system crash when loading custom audio files. The main development in `SpellSmut` should continue unaffected."

### Example 5: A/B Testing
```bash
git worktree add -b test/magic-system-v1 ../SpellSmut-magic-v1
git worktree add -b test/magic-system-v2 ../SpellSmut-magic-v2
```

**Claude Instructions**:
"Implement two different magic system architectures: one in `SpellSmut-magic-v1` using table-driven design, and another in `SpellSmut-magic-v2` using object-oriented approach. Then compare performance and maintainability."

### Example 6: Safe Refactoring
```bash
git worktree add -b refactor/pak-system ../SpellSmut-refactor-pak
```

**Claude Instructions**:
"In `SpellSmut-refactor-pak`, refactor the PAK file loading system for better performance. If tests fail, we can discard this worktree without affecting the main codebase."

---

## Quick Reference Card

```bash
# CREATE
git worktree add <path> <branch>              # From existing branch
git worktree add -b <new-branch> <path>       # Create new branch

# VIEW
git worktree list                              # List all worktrees

# REMOVE
git worktree remove <path>                     # Remove worktree
git worktree remove -f <path>                  # Force remove
git worktree prune                             # Clean up stale references

# MANAGE
git worktree move <old-path> <new-path>       # Move worktree
git worktree lock <path>                       # Lock worktree
git worktree unlock <path>                     # Unlock worktree

# IN WORKTREE
cd <worktree-path>                            # Navigate to worktree
git status                                     # Check status
git add . && git commit -m "message"          # Commit changes
git push origin <branch>                       # Push changes
```

---

## Additional Resources

- [Official Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Git Worktree Tutorial](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [Atlassian Git Worktree Guide](https://www.atlassian.com/git/tutorials/git-worktree)

---

## Tips for SpellSmut Development

1. **Keep main branch stable**: Use worktrees for all experimental work
2. **One feature per worktree**: Makes code review and testing easier
3. **Document in commit messages**: Note when code was developed in a worktree
4. **Use branches prefixes**: `feature/`, `hotfix/`, `experimental/`, `mod/`
5. **Regular cleanup**: Remove merged worktrees promptly
6. **Backup before experimenting**: Even with worktrees, backup before major changes

---

*Last Updated: 2025-10-18*  
*For SpellSmut Project*  
*Compatible with Git 2.5+*