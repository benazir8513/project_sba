# Git How-To

## Add SSH Key Before Pushing

Every time you open a new terminal (or after a restart), you need to add your personal SSH key to the SSH agent.

### 1. Start the SSH agent (if not already running)

```bash
eval "$(ssh-agent -s)"
```

### 2. Add your personal SSH key

```bash
ssh-add ~/.ssh/id_ed25519_personal
```

### 3. Verify the key was added

```bash
ssh-add -l
```

You should see your key fingerprint listed in the output.

### 4. Test the connection

```bash
ssh -T git@github-personal
```

### 5. Push as usual

```bash
git push
```

