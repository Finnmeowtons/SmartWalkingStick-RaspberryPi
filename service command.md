### 🟢 **Enable (auto-run on boot)**

```bash
sudo systemctl enable smartstick.service
```

> This makes it automatically run every time the Raspberry Pi boots.

---

### 🔴 **Disable (stop auto-run on boot)**

```bash
sudo systemctl disable smartstick.service
```

> This prevents it from starting automatically on boot, but doesn’t stop it if it’s already running.

---

### ▶️ **Start the script manually**

```bash
sudo systemctl start smartstick.service
```

> Runs your Python script right now.

---

### ⏹️ **Stop the script**

```bash
sudo systemctl stop smartstick.service
```

> Immediately stops your running script.

---

### 🔁 **Restart the script**

```bash
sudo systemctl restart smartstick.service
```

> Useful after editing your Python file.

---

### 🧠 **Check if it’s running**

```bash
sudo systemctl status smartstick.service
```

If running, you’ll see something like:

```
Active: active (running)
```

If stopped or failed:

```
Active: inactive (dead)   or   failed
```

---

### 📜 **View live logs**

```bash
journalctl -u smartstick.service -f
```

> Press `Ctrl + C` to exit log view.

---

### 🧽 **After editing the service file**

Whenever you modify `/etc/systemd/system/smartstick.service`, reload the systemd daemon:

```bash
sudo systemctl daemon-reload
```

