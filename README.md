<!--header:start-->
<a href="https://dhruvpatel.net"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/header-dark.svg"><img alt="Dhruv Patel: I build the systems around the model, and measure them before I trust them. Near Melbourne." src="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/header-light.svg" width="100%"></picture></a>
<!--header:end-->

<p>
<a href="https://dhruvpatel.net"><img alt="Site: dhruvpatel.net" src="https://img.shields.io/badge/site-dhruvpatel.net-1D6E4B?style=flat-square&labelColor=17191C"></a>
<img alt="status: measuring" src="https://img.shields.io/badge/status-measuring-1D6E4B?style=flat-square&labelColor=17191C">
<a href="https://github.com/My-CMDhub/Agent-OS/commit/6488e06d7049eccc61761c252117112ab60cf9d2"><img alt="claims withdrawn: 2" src="https://img.shields.io/badge/claims%20withdrawn-2-646B74?style=flat-square&labelColor=17191C"></a>
<img alt="tests: 1,922 in Ovela, 217 in Agent-OS" src="https://img.shields.io/badge/tests-ovela%201%2C922%20%C2%B7%20agent--os%20217-6E2437?style=flat-square&labelColor=17191C">
<img alt="Ovela last commit" src="https://img.shields.io/github/last-commit/My-CMDhub/Ovela-AI?style=flat-square&label=ovela%20last%20commit&labelColor=17191C&color=1D6E4B">
<a href="https://www.linkedin.com/in/dhruvpatel-profile/"><img alt="LinkedIn" src="https://img.shields.io/badge/linkedin-dhruvpatel--profile-6E2437?style=flat-square&labelColor=17191C"></a>
<a href="mailto:dppatel20004@gmail.com"><img alt="Email" src="https://img.shields.io/badge/email-dppatel20004%40gmail.com-6E2437?style=flat-square&labelColor=17191C"></a>
</p>

I build the parts around the model: the phone line, the permission prompt, the payment that arrives 0.00025 ETH short.
Each card below is one **before → after** with its evidence label, plus what it still doesn't do.
The full cases, with interactive demos running the real rules, are at **[dhruvpatel.net](https://dhruvpatel.net)**.

### Signals

<!--cards:start-->
<p>
<a href="https://github.com/My-CMDhub/Ovela-AI"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/ovela-dark.svg"><img alt="Ovela: The first reply of a call, 3.7 s to 0.9 s. Not yet: under a second from the caller&#x27;s last word · 1.5–1.7 s." src="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/ovela-light.svg" width="49%"></picture></a>
<a href="https://github.com/My-CMDhub/Agent-OS"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/agent-os-dark.svg"><img alt="Agent-OS: How long a command waited behind a slow one, 2,864 ms to 5 ms. Not yet: memory across sessions · apps without a readable structure." src="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/agent-os-light.svg" width="49%"></picture></a>
</p>
<p>
<a href="https://github.com/My-CMDhub/no-show-desk"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/no-show-desk-dark.svg"><img alt="No-Show Desk: Messages with a wrong date or total, 13 / 100 to 0 / 100. Not yet: live motel bookings, and the morning message on them." src="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/no-show-desk-light.svg" width="49%"></picture></a>
<a href="https://github.com/My-CMDhub/Blockchain-based-Industry-Project"><picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/capstone-dark.svg"><img alt="Capstone: How far off a payment could be and still count as paid, ±0.5% to ±0.003%. Not yet: tests for the amount check." src="https://raw.githubusercontent.com/My-CMDhub/My-CMDhub/main/assets/capstone-light.svg" width="49%"></picture></a>
</p>

<p><sub>internships&nbsp;</sub>
<a href="https://dhruvpatel.net/work/silverpond/"><img alt="Silverpond internship: a stored AWS key to nothing to store" src="https://img.shields.io/badge/silverpond-a%20stored%20AWS%20key%20%E2%86%92%20nothing%20to%20store-6E2437?style=flat-square&labelColor=17191C"></a>
<a href="https://dhruvpatel.net/work/audacix/"><img alt="Audacix internship: Llama 3.1 to Qwen 2.5" src="https://img.shields.io/badge/audacix-Llama%203.1%20%E2%86%92%20Qwen%202.5-6E2437?style=flat-square&labelColor=17191C"></a>
</p>
<!--cards:end-->

### Signal log

<!--signal:start-->
| | repo | latest change |
|:--|:--|:--|
| `yesterday` | [cachewatch](https://github.com/My-CMDhub/cachewatch) | fix(install): start SwiftBar by path right after Homebrew installs it |
| `2 days ago` | [dhruvpatel.net](https://github.com/My-CMDhub/dhruvpatel.net) | fixed description |
| `3 days ago` | [Agent-OS](https://github.com/My-CMDhub/Agent-OS) | feat(calendar): read_calendar answers what is on a day from EventKit, the range from the owner's words |
| `12 days ago` | [no-show-desk](https://github.com/My-CMDhub/no-show-desk) | docs: the landing page links to the final film (v10) |
| `Oct 2026` | [Ovela-AI](https://github.com/My-CMDhub/Ovela-AI) | fix(demo): every demo call waits for approval; provider failures stay private |
<!--signal:end-->

### Decoded

```python
# decoded.py: things these systems taught me by misbehaving

silence = doubt                       # 3 s of quiet reads as failure. say "let me have a look".
heard   = said[:played]               # people keep what reached the ear, not what was generated.
listed != reachable                   # a button can exist, perfectly named, at (0, 0, 0, 0).
yes     = Yes(to=seen, valid_while=unchanged)  # "go ahead" means what I saw, not whatever happens next.
trip    = None                        # booking lookup: 1,073 ms → 0.4 ms. not a faster trip. no trip.

assert belief <= evidence             # MCP transport: expected 15–50 ms, measured 0.04 ms.
```

<sub>○ → ● &nbsp;every number here comes from a measurement or the git history. Two earlier claims of mine were wrong; both are withdrawn in the open, not deleted.</sub>
