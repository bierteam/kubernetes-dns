# Readme

This container will monitor the available nodes in our kubernetes cluster and will update the dns records accordingly.
This only supports the cloudflare API

The script checks what k8s nodes there are with the REGEX_DOMAIN
Then it tries to connect to each of the found records and checks if there is a valid certificate for TEST_DOMAIN
If there is a succesful connection the ip of the node will be added to the pool (KUBERNETES_DOMAIN) (ipv4 and ipv6)

Env variables:
```bash
TIMEOUT=5
MAIN_DOMAIN="oscarr.nl"
REGEX_DOMAIN="k8s-[0-9]+\.oscarr\.nl"
KUBERNETES_DOMAIN="kubernetes.oscarr.nl"
TEST_DOMAIN="ninoo.nl"
CLOUDFLARE_API_TOKEN="SECRET"
```
https://dash.cloudflare.com/profile/api-tokens
