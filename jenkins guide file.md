# 🚀 The Absolute Beginner's Guide to Jenkins on Windows

> Welcome! This guide assumes you have **zero prior experience** with Jenkins. We are going to build a fully functional CI/CD pipeline from scratch, step-by-step, in plain English.

---

## 🧠 1. What Exactly is Jenkins?

Imagine Jenkins as a **tireless robotic assistant** that constantly monitors your GitHub repository.

Whenever you save and upload (push) new code, this robot wakes up and does the heavy lifting for you:
1. Double-checks your code's formatting and security.
2. Runs all your automated tests.
3. Packages your application into a Docker container.
4. Delivers the final product to Docker Hub.
5. Gives you a thumbs up (✅) or thumbs down (❌) on whether the new code is safe.

Your project already contains the "instruction manual" for this robot — it's the `Jenkinsfile` sitting in your code. Our goal now is to simply install the robot and hand it the manual.

---

## 🗺️ 2. The Master Plan

Here is exactly what we are going to accomplish:
1. **Install Jenkins:** We'll use Docker to run Jenkins on your Windows PC easily.
2. **Access the Dashboard:** Open the Jenkins website in your browser.
3. **Initial Setup:** Unlock the system and create your admin account.
4. **Teach New Skills:** Install necessary plugins.
5. **Secure Storage:** Save your Docker Hub login details safely.
6. **Connect GitHub:** Tell Jenkins where your code lives.
7. **Test Drive:** Run your very first automated build.
8. **Review:** Understand how to read the success or failure reports.

---

## ✅ 3. Prerequisites Checklist

Before we begin, open **PowerShell** and verify you have the necessary tools installed:

```powershell
# Verify Docker Desktop is active
docker --version
# You should see something like: Docker version 24.x.x

# Verify Git is installed
git --version
# You should see something like: git version 2.x.x
```

> **Missing Docker?** Download and install it from [Docker's official website](https://www.docker.com/products/docker-desktop/), restart your computer, and return here.

---

## 📦 4. Step 1: Installing Jenkins via Docker

Running Jenkins inside a Docker container is the cleanest and most straightforward method for Windows users.

### Create a Storage Folder
First, we need a place on your computer for Jenkins to save its files permanently. Run this in PowerShell:

```powershell
# Creates a dedicated folder for Jenkins data
mkdir C:\jenkins-data
```

### Spin Up Jenkins
Copy and paste this multi-line command into PowerShell and hit Enter:

```powershell
docker run -d `
  --name jenkins `
  --restart=on-failure `
  -p 8080:8080 `
  -p 50000:50000 `
  -v C:\jenkins-data:/var/jenkins_home `
  -v //var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts-jdk17
```

**Decoding the command:**
- `-d`: Run silently in the background.
- `--name jenkins`: Name our robot "jenkins".
- `--restart=on-failure`: If it crashes, start it back up automatically.
- `-p 8080:8080`: Make the Jenkins website accessible on port 8080.
- `-v C:\jenkins-data...`: Save all settings and jobs to your new Windows folder.
- `-v //var/run/docker.sock...`: Allow Jenkins to use Docker to build your app's images.
- `jenkins/jenkins:lts-jdk17`: The specific version of Jenkins to download.

### Verify It's Running
Wait about a minute, then check the logs:

```powershell
docker logs -f jenkins
```

When you see the phrase **"Jenkins is fully up and running"**, press `Ctrl+C` to exit the logs. (Jenkins will stay running in the background).

---

## 🌐 5. Step 2: Accessing the Web Interface

Open your favorite web browser (Chrome, Edge, etc.) and navigate to:
**`http://localhost:8080`**

You will be greeted by an **"Unlock Jenkins"** screen asking for a special password.

---

## 🔓 6. Step 3: Unlocking and Setup

### Find the Secret Password
Go back to your PowerShell window and ask Docker for the password:

```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
You will receive a long string of random letters and numbers (e.g., `3a4b5c6d...`). 

1. Copy that password string.
2. Paste it into the browser box and click **Continue**.

### Install Standard Plugins
On the next screen, click the big button on the left: **"Install suggested plugins"**.
Sit back and relax for a few minutes while Jenkins downloads its standard toolkit.

### Create Your Admin Profile
Once the plugins are done, fill out the form to create your personal administrator account (Username, Password, Full Name, Email). 
Click **"Save and Continue"**, then **"Save and Finish"**, and finally **"Start using Jenkins"**.

---

## 🔌 7. Step 4: Installing Extra Plugins

We need two special tools for your specific project.

1. On the left sidebar, click **Manage Jenkins**.
2. Click **Plugins**.
3. Select the **Available plugins** tab.
4. Search for and check the boxes next to:
   - `HTML Publisher` (Allows us to view visual test reports).
   - `Docker Pipeline` (Allows the pipeline to build Docker containers).
5. Click **Install**.
6. Check the box at the bottom that says **"Restart Jenkins when installation is complete"**. Wait for the page to refresh.

---

## 🔑 8. Step 5: Securely Storing Docker Hub Credentials

Jenkins needs to log into Docker Hub to upload your finished application, but we *never* want to type passwords directly into our code. We will store them in Jenkins' secure vault.

### Adding Your Username
1. Go to **Manage Jenkins** → **Credentials** → **System** → **Global credentials (unrestricted)**.
2. Click **+ Add Credentials** (top right).
3. Set **Kind** to **Secret text**.
4. In **Secret**, type your Docker Hub username.
5. In **ID**, type exactly: `DOCKER_HUB_USERNAME`
6. Click **Create**.

### Adding Your Access Token (Password)
1. Click **+ Add Credentials** again.
2. Set **Kind** to **Secret text**.
3. In **Secret**, paste your Docker Hub Access Token. *(If you don't have one, go to hub.docker.com → Account Settings → Security → New Access Token).*
4. In **ID**, type exactly: `DOCKER_HUB_TOKEN`
5. Click **Create**.

---

## 📁 9. Step 6: Linking Your GitHub Repository

Time to introduce Jenkins to your code!

1. On the main dashboard, click **+ New Item**.
2. Name it `cicd-demo`, select **Multibranch Pipeline**, and click **OK**.
   *(Multibranch pipelines are smart—they automatically find and track every branch in your GitHub repo).*
3. Scroll down to **Branch Sources**, click **Add source**, and select **Git**.
4. In the **Project Repository** field, paste your GitHub URL (e.g., `https://github.com/your-name/your-repo.git`).
5. Scroll down to **Build Configuration** and ensure **Mode** is set to `by Jenkinsfile` and **Script Path** is `Jenkinsfile`.
6. Click **Save**.

Jenkins will immediately scan your repository and find your `main` branch.

---

## ▶️ 10. Step 7: Running the Pipeline

1. After saving, you will be on the project page showing your branches. Click on **`main`**.
2. On the left sidebar, click **Build Now**.
3. Look at the **Build History** on the bottom left. You will see a new build (like `#1`) pop up with a progress bar.
4. Click on that build number (`#1`), and then click **Console Output** on the left.

This is the control room! You can watch live as Jenkins downloads your code, runs the automated tests, builds the Docker image, and pushes it to the internet. 

---

## 📊 11. Step 8: Understanding the Results

When the build finishes, check the status:
- 🔵 **Blue / ✅ Green:** Everything passed perfectly!
- 🔴 **Red:** Something broke. Read the Console Output to see which step failed.
- 🟡 **Yellow:** The build finished, but some tests failed.

On the build's main page, you can click **Pipeline Overview** to see a visual flowchart of every stage, showing exactly how long each part took and where any issues occurred.

---

## 🔄 12. The Magic of Automation

Right now, Jenkins is set up to periodically check GitHub for updates. 

Whenever you write new code and push it to GitHub, Jenkins will notice the change within a few minutes, wake up, and run this entire pipeline again automatically. You get instant feedback on whether your new code is safe for production!

---

## 🌍 13. Real-World Jenkins Scenarios

To help you understand *why* companies use Jenkins, here are three real-world examples:

### Scenario A: The Broken Website Blocker
**The Situation:** A developer accidentally writes a typo in the code that crashes the login page.
**Without Jenkins:** The developer pushes the code, it goes live, and customers can't log in. The company loses money until someone notices.
**With Jenkins:** The developer pushes the code. Jenkins immediately downloads it and runs the automated tests. The tests fail because the login page is broken. Jenkins **blocks** the code from going live and sends a Slack message to the developer: *"Hey, your new code failed the tests. Fix it before we deploy."*

### Scenario B: The Security Guard
**The Situation:** A team is building a banking app and accidentally uses an outdated, easily hackable version of a software library.
**Without Jenkins:** The vulnerable app is deployed. Months later, a hacker exploits the old library and steals data.
**With Jenkins:** Jenkins is configured with a security scanner (like Trivy or Bandit in your pipeline). When the code is pushed, Jenkins scans the app, finds the vulnerability, turns the build **🔴 Red**, and prevents the insecure app from being deployed.

### Scenario C: The Multi-Branch Manager
**The Situation:** You have three different versions of your app: `main` (what customers see), `develop` (what the team is testing), and `feature-dark-mode` (a new design you are building).
**With Jenkins:** Using the **Multibranch Pipeline**, Jenkins automatically discovers all three branches.
- If you push to `feature-dark-mode`, Jenkins builds it and puts it on a private testing server so you can see how it looks.
- If you push to `main`, Jenkins builds it and automatically deploys it to the public servers for real customers.
Jenkins manages all of this simultaneously without getting confused!

---

## 🆘 14. Troubleshooting Common Errors

> [!WARNING]
> **Error:** `docker: command not found` inside the Jenkins logs.
> **Fix:** The Jenkins container doesn't have Docker installed inside it. Open PowerShell and run: 
> `docker exec -u root jenkins sh -c "apt-get update && apt-get install -y docker.io"`

> [!WARNING]
> **Error:** Build fails at the "Code Quality" stage.
> **Fix:** Your code didn't pass the strict formatting rules. Fix the formatting on your local machine using the `black` and `isort` tools, then push the corrected code back to GitHub.

> [!WARNING]
> **Error:** `Credential not found: DOCKER_HUB_USERNAME`
> **Fix:** You made a typo when naming your credentials in Step 5. Go back to the Credentials menu and ensure the IDs are exactly `DOCKER_HUB_USERNAME` and `DOCKER_HUB_TOKEN` in all uppercase.

> [!WARNING]
> **Error:** Jenkins won't open in the browser / Port 8080 is in use.
> **Fix:** Another app on your computer is using port 8080. You can start Jenkins on port 9090 instead by changing `-p 8080:8080` to `-p 9090:8080` in the startup command. Then, visit `http://localhost:9090`.

---

## 📋 15. Essential Cheat Sheet Commands

Keep these PowerShell commands handy for managing your Jenkins robot:

```powershell
# Turn Jenkins off
docker stop jenkins

# Turn Jenkins back on
docker start jenkins

# Reboot Jenkins completely
docker restart jenkins

# Watch the live system logs
docker logs -f jenkins
```

---

## 🎉 Congratulations!

You have successfully:
- Spun up a local CI/CD server using Docker.
- Connected a secure credential vault.
- Linked a GitHub repository.
- Executed a multi-stage pipeline encompassing testing, security scanning, and Docker deployment.

You are now running a professional-grade DevOps workflow directly from your Windows machine!
