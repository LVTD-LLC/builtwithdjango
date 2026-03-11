# TJ Alerts → Built with Django Sponsorship Outreach Sequences

Purpose: promote existing Built with Django sponsorship options to relevant job posters from TJ Alerts without a spammy tone.

Audience: founder/operators currently hiring for Django/Python roles.

## Personalization tokens

Use these placeholders in each message:

- `{{first_name}}`
- `{{company_name}}`
- `{{job_title}}`
- `{{job_url}}`
- `{{job_location_or_remote}}`
- `{{sender_name}}`
- `{{sender_role}}`
- `{{calendar_link}}` (optional)

Personalization rules:

1. Mention one concrete detail from the job post (`{{job_title}}` + one short note).
2. Keep custom line to 1 sentence (max 25 words).
3. Never pretend to have used their product if not true.
4. If no first name is available, use "Hi there" (not guessed names).

---

## Email 1 — Initial outreach (Day 0)

**Subject options**
- Quick sponsorship idea for `{{company_name}}`’s Django hiring
- `{{job_title}}` visibility boost on Built with Django
- Relevant Django dev audience for your open role

**Body**

Hi `{{first_name}}`,

I saw `{{company_name}}` is hiring for **{{job_title}}** ({{job_location_or_remote}}): {{job_url}}.

If helpful, we can feature your role through Built with Django sponsorship placements, where Django-focused developers already browse projects and jobs.

If you want, I can send the current sponsorship options + pricing in one short reply.

No pressure—if this isn’t relevant, reply **"no thanks"** and I won’t follow up.

Best,
`{{sender_name}}`
`{{sender_role}}`

---

## Email 2 — Soft follow-up (Day 3)

**Subject options**
- Re: `{{job_title}}` sponsorship option
- Worth sending sponsorship details?
- Should I close this out?

**Body**

Hi `{{first_name}}`,

Quick follow-up in case this got buried.

Since `{{company_name}}` is actively hiring for **{{job_title}}**, I can share a concise sponsorship breakdown for Built with Django (placements, timing, and cost) so you can decide in a few minutes.

If you’d rather not get outreach like this, reply **"opt out"** and I’ll remove you from future sponsorship emails.

Thanks,
`{{sender_name}}`

---

## Email 3 — Final close-out (Day 7)

**Subject options**
- Closing the loop on `{{company_name}}` sponsorship
- Last note from me
- I’ll close this thread

**Body**

Hi `{{first_name}}`,

Last note from me regarding Built with Django sponsorship for your **{{job_title}}** opening.

If timing changes later, I’m happy to share options then. Otherwise I’ll close this out now.

If you don’t want future outreach, reply **"unsubscribe"** and I’ll make sure you’re removed.

All the best,
`{{sender_name}}`

---

## Send cadence + anti-spam caps

Recommended sequence per contact:

1. Day 0: Initial outreach
2. Day 3: Soft follow-up
3. Day 7: Final close-out

Hard limits:

- Max 3 emails per contact per job posting.
- Stop immediately on any negative response or opt-out.
- Minimum 72 hours between follow-ups.
- Do not start a new sequence for the same contact for at least 30 days unless they explicitly re-engage.
- Daily send cap recommendation: start at 25–40 highly relevant contacts/day; increase only if positive/neutral response quality stays high.

Deliverability hygiene:

- Plain-text style formatting, no heavy HTML.
- Keep links minimal (prefer 1 relevant link).
- Avoid spam trigger phrasing ("guaranteed", "best deal", "limited time").

---

## When NOT to send

Do not send if any of the following is true:

- Job is closed, paused, or older than 45 days with no signs it is active.
- Contact has already opted out or previously asked not to be pitched.
- Role is clearly non-Django/non-Python and not relevant to Built with Django audience.
- You cannot identify a real hiring signal (no active job post URL).
- Same contact was emailed about sponsorship in the last 30 days with no response.
- Personalization is missing (e.g., no job title reference).

---

## Reply handling snippets (copy/paste)

### 1) Positive interest

Great—happy to send it over.

Would you prefer:
1) a quick async breakdown by email, or
2) a short call (10–15 min)? {{calendar_link}}

Either way, I’ll keep it concise and focused on your `{{job_title}}` hiring goals.

### 2) "Send pricing"

Absolutely. I’ll send the current sponsorship options with pricing, placement details, and suggested fit for `{{company_name}}`’s `{{job_title}}` role in one message.

### 3) Not now / budget constrained

Totally understood—thanks for the quick reply.

If useful, I can check back in {{next_quarter_or_month}} when hiring plans are clearer. If you prefer no follow-up, I can close this out permanently.

### 4) Already filled role

Thanks for the update, and congrats on filling it.

If a new Django role opens later, I’m happy to share sponsorship options then. (Or I can keep you fully opted out—your call.)

### 5) Not a fit

Appreciate the clarity—thanks.

I’ll mark this as not a fit and won’t follow up again unless you reach out.

### 6) Opt-out / unsubscribe

Confirmed — you’re opted out.

I won’t send future sponsorship outreach to this email.

---

## QA checklist before sending

- [ ] Job title and company name match the live posting.
- [ ] At least one real personalization line is included.
- [ ] Opt-out language is present exactly as written.
- [ ] Tone is neutral/helpful (no hype, no pressure).
- [ ] Sequence step and timing follow cadence policy.
