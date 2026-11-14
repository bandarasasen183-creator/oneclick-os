# Things only you can do (all possible from your phone)

## 1. Make the three system images public (unblocks updates)

Until this is done, no computer, including the Mac preview, can download OneClick updates.

1. Open github.com/orgs/Codecraft-Solutions-Team/packages
2. Tap `oneclick-os`, then Package settings, then Change visibility, then Public. Type the name to confirm.
3. Do the same for `oneclick-os-nvidia`.
4. Do the same for `oneclick-os-preview`.

If "Public" is greyed out: organisation Settings, then Packages, and allow public packages first.

## 2. Create the token for the report form (unblocks "Report a problem")

1. Open github.com/settings/personal-access-tokens/new
2. Token name: `oneclick report form`. Expiration: 1 year.
3. Resource owner: `Codecraft-Solutions-Team`.
4. Repository access: Only select repositories, then `oneclick-os`.
5. Permissions, Repository permissions, Issues: Read and write. Leave everything else.
6. Generate, and copy the token (it starts with `github_pat_`). Keep it private.
7. Save it where the website can read it, either way:
   - On the Mac, in your own terminal: `firebase functions:secrets:set ONECLICK_GITHUB_TOKEN --project codecraft-sol` and paste it when asked.
   - Or on the phone: console.cloud.google.com/security/secret-manager?project=codecraft-sol, Create secret, name `ONECLICK_GITHUB_TOKEN`, paste the token as the value.
8. Tell Claude "token is set". Never paste the token into a chat.

## 3. Check the website

- https://oneclickos.org (may take up to an hour after 14 Nov to switch on; https://oneclick-os.web.app works straight away)
- Add ?style=classic or ?style=story to any page to compare the two looks.

## 4. Decisions waiting on you

- Keep the name OneClick? (oneclickos.com and .io belong to an unrelated AI product.)
- Storybook look or classic look for the website.
- External USB drive for testing on the ThinkPad (32 GB or more), plus a 16 GB stick for the installer.
- A lawyer to review the Terms, Privacy policy and Test version notice.
