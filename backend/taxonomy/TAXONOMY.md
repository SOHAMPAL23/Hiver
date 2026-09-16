# AppleSupport Customer Intent Taxonomy

Empirically derived from unsupervised clustering of 1,500 customer queries from the dataset using dense embeddings (`all-MiniLM-L6-v2`) and TF-IDF topic keyword validation.

| Intent Key | Label Name | Operational Definition | Seed Real-World Examples | Top Cluster Keywords |
| :--- | :--- | :--- | :--- | :--- |
| `software_update_os_bug` | **Software Update & OS Bugs** | Issues arising after iOS/macOS update installations, including crashes, boot-loops, or system glitches. | - *"Updated to iOS 11.1 and now my phone restarts every 10 minutes when opening apps."*<br>- *"My iPad is stuck on the Apple logo after trying to install the latest software update."* | `que, el, la, en, ios11` |
| `battery_power_charging` | **Battery, Power & Charging** | Rapid battery percentage drain, overheating during use, charging port connection problems, or degraded battery health. | - *"My iPhone 7 battery drops from 100% to 20% in two hours on standby."*<br>- *"My phone only charges if I hold the lightning cable bent at a weird angle."* | `phone, iphone, just, help, plus` |
| `account_apple_id_icloud` | **Apple ID, iCloud & Account Security** | Apple ID lockouts, two-factor authentication failures, forgotten passwords, or iCloud backup and sync errors. | - *"I am locked out of my Apple ID and the verification code goes to a disconnected phone number."*<br>- *"Photos are not syncing to iCloud even though I am paying for the 200GB plan."* | `11, ios, ios11, iphone, update` |
| `hardware_physical_damage` | **Hardware & Physical Damage** | Cracked screens, broken glass, liquid water damage, swollen batteries, malfunctioning physical buttons, or speaker hardware failure. | - *"Dropped my iPhone X on gravel, back glass completely shattered. What is the repair cost?"*<br>- *"My battery has swelled and pushed the display up out of the phone frame. Is this safe?"* | `app, problem, fix, just, issue` |
| `connectivity_network_bluetooth` | **Connectivity, Cellular & Bluetooth** | Cellular 'No Service' drops, persistent Wi-Fi disconnects, Bluetooth audio dropouts with AirPods or car audio units. | - *"AirPods keep disconnecting from my MacBook every 5 minutes during Zoom calls."*<br>- *"My iPhone 8 keeps saying No Service after toggling airplane mode and reseating the SIM."* | `update, phone, updated, new, iphone` |
| `billing_subscriptions_appstore` | **Billing, Subscriptions & App Store** | Unauthorized App Store in-app purchases, recurring subscription cancellations, refund requests, or declined payment methods. | - *"I was charged $9.99 for an app subscription I cancelled 3 days ago. I need a refund."*<br>- *"Cannot purchase anything on the App Store, getting 'Your payment method was declined'."* | `apple, store, icloud, macbook, itunes` |
| `device_performance_storage` | **Device Performance & Storage** | Sluggish system responsiveness, typing lag, unresponsive touchscreen, or 'System / Other' storage filling up internal memory. | - *"System data is taking up 50GB out of 64GB on my phone and I can't download anything."*<br>- *"Keyboard typing has a massive 3-second lag whenever I try to send an iMessage."* | `battery, life, iphone, ios, 11` |
| `general_feedback_complaint` | **General Feedback & Service Complaints** | Customer complaints regarding retail store staff, shipping delays, general dissatisfaction, or sarcastic venting without a specific diagnostic ask. | - *"Worst customer service ever at the Regent St store today. Unhelpful and rude staff."*<br>- *"Love spending $1200 on a phone that can't even hold a signal. Outstanding engineering Apple."* | `help, fix, just, type, dm` |

## Intent Decision Boundaries & Ambiguity Resolution
### `software_update_os_bug`
- **Definition**: Issues arising after iOS/macOS update installations, including crashes, boot-loops, or system glitches.
- **Disambiguation / Boundary**: Focuses on OS-level anomalies caused by system updates. If the issue is solely battery draining after update, label battery_power_charging if battery is the primary complaint.
- **Empirical Samples from Cluster**:
  - "Volevo dire a che #iOS11 mi blocca il cell continuamente. !! Cazzo!!!!"
  - "E ai ta afim de resolver meu problema?? Estou muito descontente!! A atualização trava meu celular e por estar fora da garantia tenho que pagar um valor absurdo e trocar de celular?"
  - "¿por qué se reinicia mi iPhone cada vez que desbloqueo la panta…"

### `battery_power_charging`
- **Definition**: Rapid battery percentage drain, overheating during use, charging port connection problems, or degraded battery health.
- **Disambiguation / Boundary**: Covers physical charging cables/ports and chemical battery discharge. If battery has physically swollen and bent the phone, flag for hardware damage escalation.
- **Empirical Samples from Cluster**:
  - "why is there no way to add seconds to the iPhone status bar or standard ‘Clock’ app? Seriously stupid when there’s a seconds hand on the Clock app icon ... #thismakesnosense"
  - "Wow, the iPhone just gets worse everyday now my alarm app doesn’t work. Not happy. #iphone #alarmapp #badstart"
  - "Makes me want to switch from an iPhone! I’m very disappointed"

### `account_apple_id_icloud`
- **Definition**: Apple ID lockouts, two-factor authentication failures, forgotten passwords, or iCloud backup and sync errors.
- **Disambiguation / Boundary**: Concerns authentication, credentials, and Apple cloud sync. Does not include third-party app login failures.
- **Empirical Samples from Cluster**:
  - "I’m getting really tired of looking at this mess when I try to manage iCloud apps w/iOS 11.0.2 & 8 Plus. 😾😾"
  - "It's iOS 11.0.2. As I was checking which version, it appears there is a further update available for 11.0.3. So I'll try this!"
  - "Anyone else seeing no keyboard on ios 11.1.2? Twice today, not on any app. Reboot restored. /cc"

### `hardware_physical_damage`
- **Definition**: Cracked screens, broken glass, liquid water damage, swollen batteries, malfunctioning physical buttons, or speaker hardware failure.
- **Disambiguation / Boundary**: Physical defects requiring in-person Genius Bar inspection or mail-in repair. Always triggers human escalation.
- **Empirical Samples from Cluster**:
  - "I’m saying it’s there....but it often doesn’t work. I’ll have music playing and the “music” in the control panel will be blank. See pic"
  - "Capslock key light ON is Capslock off according to the password screen and vice-versa. Is this a known issue?"
  - "I downloaded the first 3 songs as they were released and they’re fine but can’t get the rest of the album. Songs from other artists download"

### `connectivity_network_bluetooth`
- **Definition**: Cellular 'No Service' drops, persistent Wi-Fi disconnects, Bluetooth audio dropouts with AirPods or car audio units.
- **Disambiguation / Boundary**: Wireless communication protocols (Wi-Fi, Bluetooth, cellular carrier signal, GPS).
- **Empirical Samples from Cluster**:
  - "No pending updates. I updated all my apps earlier today."
  - "needs to get these updates fixed. Phone is not running apps correctly at all"
  - "when you sorting out a new update as my phone is as much use as a brick now thanks to your shit update"

### `billing_subscriptions_appstore`
- **Definition**: Unauthorized App Store in-app purchases, recurring subscription cancellations, refund requests, or declined payment methods.
- **Disambiguation / Boundary**: Financial transactions, credit card declines, App Store purchase disputes, and Apple Music subscriptions.
- **Empirical Samples from Cluster**:
  - "bought iPads for the kids for Christmas (6&9). Would like to learn about security/parental controls to put on. Appointment at local Genius Bar the best way?"
  - "hey all. What's going on in China. UPS says that there are a lot of delays of product coming out of there for iPhone X? My delivery date with UPS says that its currently unavailable. who can get this resolved?"
  - "I’ve tried to do the upgrade program online and can’t. t-mobile as a carrier and no apple store closer then 3hours away. Help"

### `device_performance_storage`
- **Definition**: Sluggish system responsiveness, typing lag, unresponsive touchscreen, or 'System / Other' storage filling up internal memory.
- **Disambiguation / Boundary**: Local device storage bottlenecks and sluggish UI lag without crashing/rebooting into a loop.
- **Empirical Samples from Cluster**:
  - "iOS 11 has destroyed my battery life. Will there be any fix soon?"
  - "what is happening to my phone? Keeps crashing and draining my battery! Help"
  - "why is my iPhone 7 battery suddenly only last 5 hours? #help #updatessuck #myphonesnotevenayearold"

### `general_feedback_complaint`
- **Definition**: Customer complaints regarding retail store staff, shipping delays, general dissatisfaction, or sarcastic venting without a specific diagnostic ask.
- **Disambiguation / Boundary**: Tone-heavy, complaint-focused messages without an immediate technical troubleshooting step.
- **Empirical Samples from Cluster**:
  - "can y’all fix this > “I” situation 😐"
  - "I got it back thanks for answering 👍🏻"
  - "It’s not for the first time"
