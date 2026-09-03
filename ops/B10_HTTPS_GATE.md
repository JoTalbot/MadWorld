# B10 Production HTTPS / Reverse Proxy Gate

No production domain or certificate is assumed by the repository.

## Owner setup

- Provide the real production hostname.
- Terminate TLS at the approved reverse proxy/load balancer.
- Proxy only to the MadWorld API container on its private/loopback listener.
- Redirect HTTP to HTTPS and enable HSTS only after HTTPS is confirmed stable.
- Forward `Host`, `X-Forwarded-Proto` and client-IP headers according to the chosen proxy's documented trust model.
- Do not expose PostgreSQL publicly.
- Keep host port 8000 isolated as required by the existing deployment constraints.

## Verification

```bash
curl -fsS https://<production-host>/health/ready
```

Record certificate validity, hostname, TLS policy, proxy target, readiness response and rollback procedure in release evidence. Until a real domain and certificate are tested, HTTPS remains an owner/environment gate, not VERIFIED.
