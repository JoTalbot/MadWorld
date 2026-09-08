# MadWorld Privacy Policy

**Version:** 1.0 draft  
**Last updated:** 2026-09-08  
**Service:** MadWorld Android game and API

> This document is a product/privacy-policy draft prepared from the current repository behavior. It is not a substitute for jurisdiction-specific legal advice. Before public distribution, the publisher/operator must review and publish the final version and provide a legally valid contact address.

## 1. What data MadWorld processes

MadWorld currently processes the following categories of data:

- **Game account data:** the player handle and an internal player identifier.
- **Authentication data:** session tokens and session expiry/last-seen information required to authenticate gameplay.
- **Game state:** wallets, ledger entries, inventory, jobs, market orders, contracts, territory/corporation/social state and world-event state associated with a player where applicable.
- **Push notification data:** an Android Firebase Cloud Messaging (FCM) device token when the player enables push notifications. The token is stored as opaque data and is not returned by API responses.
- **Operational data:** server logs and security/rate-limit records needed to operate and protect the service.

MadWorld does **not** currently use an external analytics provider or external crash-reporting provider. The repository contains an internal analytics-events table, but the current backend does not write external analytics events.

## 2. Why data is processed

Data is processed only as needed to:

1. create and authenticate a game session;
2. persist and synchronize game state;
3. enforce game rules, security, rate limits and replay protection;
4. deliver enabled push notifications;
5. maintain service availability, backups and security;
6. investigate operational incidents and abuse.

## 3. Push notifications

If push notifications are enabled, MadWorld uses Firebase Cloud Messaging. The Android application registers an FCM token with the MadWorld API after authentication. The token may be refreshed or disabled. Notification delivery depends on the external Firebase service and the player's device settings.

Android 13 and later may require the operating-system notification permission before notifications can be shown.

## 4. Third parties and hosting

The game API and PostgreSQL database are hosted on a cloud virtual machine. Firebase/FCM is an external provider used for push messaging when that feature is enabled. No external analytics or crash-reporting service is part of the current release scope.

The final published policy must identify the actual legal operator, hosting provider, Firebase project/provider details and applicable data-processing arrangements before store publication.

## 5. Retention and deletion

Session credentials are time-limited. Operational records and backups are retained only for the period needed for security, reliability, recovery and legal obligations.

Players may request deletion of their account and associated personal/game data through the publisher's designated support/contact channel. The final production implementation must execute deletion according to the approved retention schedule and preserve only information that the operator is legally required to retain.

Push tokens can be disabled by the authenticated client. Disabling a token prevents that token from being used for future push delivery, subject to provider propagation and operational retention.

## 6. Security

Production credentials are kept outside the repository. The API uses authenticated bearer sessions, rate limiting and replay protection. Push tokens are treated as opaque secrets and are not written to normal API responses or application logs.

No security measure can guarantee absolute security. The operator will investigate suspected incidents and take reasonable containment and recovery measures.

## 7. Children's privacy

MadWorld is not designed to knowingly collect personal information from children in violation of applicable law. Age/content-rating requirements must be completed for each distribution channel and jurisdiction before public release.

## 8. International processing

Because cloud and Firebase infrastructure can process data across jurisdictions, the final published policy must identify the relevant transfer mechanisms and legal basis required for the markets in which MadWorld is offered.

## 9. Changes to this policy

Material changes will be reflected in a new policy version and publication date.

## 10. Contact

Privacy requests and questions should be sent through the official MadWorld publisher support/contact channel. The production release package must publish a legally valid contact address before store submission.

## 11. Current implementation boundary

This policy intentionally does not claim analytics, crash reporting, advertising, payment processing or other external processing that is not implemented in the current release. If such processing is introduced later, this policy and the relevant store disclosures must be updated before enabling it in production.
