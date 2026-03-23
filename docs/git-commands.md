# Git 常用命令参考

本文档收录日常开发中常用的 Git 命令。

---

## 基础命令

### 查看状态和历史

```bash
# 查看当前状态
git status

# 查看提交历史（简洁版）
git log --oneline

# 查看最近 10 条提交
git log --oneline -10

# 查看提交历史（详细版）
git log

# 查看最近一次提交
git show HEAD

# 查看文件修改差异
git diff
git diff <file>
git diff <commit>
```

### 添加和提交

```bash
# 添加所有修改
git add .

# 添加指定文件
git add <file>

# 提交到本地
git commit -m "feat: 添加新功能"

# 添加并提交（一步完成）
git commit -am "fix: 修复 bug"

# 修改最后一次提交信息
git commit --amend

# 修改最后一次提交内容（不改变消息）
git commit --amend --no-edit
```

---

## 分支操作

### 查看和创建分支

```bash
# 查看所有分支
git branch

# 查看远程分支
git branch -r

# 查看所有分支（本地+远程）
git branch -a

# 创建新分支
git branch <branch-name>

# 切换分支
git checkout <branch-name>
# 或（推荐）
git switch <branch-name>

# 创建并切换到新分支
git checkout -b <branch-name>
# 或（推荐）
git switch -c <branch-name>
```

### 合并和删除分支

```bash
# 合并分支到当前分支
git merge <branch-name>

# 删除本地分支
git branch -d <branch-name>

# 强制删除分支（未合并）
git branch -D <branch-name>

# 删除远程分支
git push origin --delete <branch-name>
```

---

## 远程操作

### 拉取和推送

```bash
# 推送到远程
git push

# 推送到指定分支
git push origin <branch-name>

# 设置上游分支
git push -u origin <branch-name>

# 拉取远程更新
git pull

# 拉取远程更新但不合并
git fetch

# 拉取指定远程分支
git fetch origin <branch-name>
```

### 远程仓库管理

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin <url>

# 删除远程仓库
git remote remove origin
```

---

## 撤销操作

### 撤销工作区修改

```bash
# 撤销单个文件的修改
git restore <file>

# 撤销所有修改
git restore .

# 撤销工作区所有修改（危险）
git reset --hard HEAD
```

### 撤销暂存区

```bash
# 取消暂存单个文件
git restore --staged <file>

# 取消所有暂存
git restore --staged .

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（不保留修改）
git reset --hard HEAD~1
```

### 撤销已推送的提交

```bash
# 撤销并创建新提交（推荐）
git revert HEAD

# 撤销指定提交
git revert <commit-hash>

# 强制推送（危险）
git push --force

# 强制推送到指定分支
git push --force origin <branch-name>
```

---

## 暂存和恢复

```bash
# 暂存当前修改
git stash

# 暂存并添加消息
git stash save "描述信息"

# 查看暂存列表
git stash list

# 恢复最近的暂存
git stash pop

# 恢复指定暂存
git stash pop stash@{1}

# 应用暂存但不删除
git stash apply

# 删除暂存
git stash drop

# 清空所有暂存
git stash clear
```

---

## 查看差异

```bash
# 查看工作区和暂存区差异
git diff

# 查看暂存区和上一次提交差异
git diff --staged
git diff --cached

# 查看两个提交之间的差异
git diff <commit1> <commit2>

# 查看指定文件的差异
git diff <file>

# 查看分支差异
git diff <branch1> <branch2>
```

---

## 查找和历史

```bash
# 查找包含特定内容的提交
git log --grep="关键字"

# 查找修改了指定文件的提交
git log -- <file>

# 查找引入 bug 的提交
git bisect start
git bisect bad   # 标记当前提交为坏的
git bisect good <commit>  # 标记已知好的提交

# 查看文件历史
git log --follow <file>

# 查看每行是谁修改的
git blame <file>
```

---

## 标签管理

```bash
# 创建轻量标签
git tag v1.0.0

# 创建附注标签
git tag -a v1.0.0 -m "版本 1.0.0"

# 查看所有标签
git tag

# 查看标签信息
git show v1.0.0

# 删除本地标签
git tag -d v1.0.0

# 推送标签到远程
git push origin v1.0.0

# 推送所有标签
git push origin --tags

# 删除远程标签
git push origin --delete v1.0.0
```

---

## 实用技巧

### 查看美化输出

```bash
# 图形化显示提交历史
git log --graph --oneline --all

# 查看提交统计
git log --stat

# 查看每次提交的修改行数
git log --shortstat
```

### 清理

```bash
# 清理未跟踪的文件
git clean -f

# 清理未跟踪的文件和目录
git clean -fd

# 预览要清理的内容（不实际删除）
git clean -n

# 清理不可达的对象
git gc
```

### 配置别名

```bash
# 设置常用命令别名
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --graph --oneline --all'

# 使用别名
git co main      # 等同于 git checkout main
git br           # 等同于 git branch
git last         # 查看最后一次提交
```

---

## 常见问题解决

### 合并冲突

```bash
# 1. 查看冲突文件
git status

# 2. 手动解决冲突
# 编辑冲突文件，删除冲突标记，保留需要的内容

# 3. 标记为已解决
git add <conflicted-file>

# 4. 完成合并
git commit

# 放弃合并
git merge --abort
```

### 回滚远程分支

```bash
# 方式 1: 使用 revert（推荐，保留历史）
git revert HEAD
git push

# 方式 2: 使用 reset（需要 force push，危险）
git reset --hard HEAD~1
git push --force
```

### 大文件处理

```bash
# 从历史中完全删除文件
git filter-branch --tree-filter 'rm -f path/to/large/file' HEAD

# 或使用 BFG（更快）
# bfg --delete-files large-file.jar
# git reflog expire --expire=now --all
# git gc --prune=now --aggressive
```

---

## 参考资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Git 指南](https://git.github.io/)
- [Pro Git 中文版](https://git-scm.com/book/zh/v2)
