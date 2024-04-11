# **External policy and event sink server for managing large conferences (Docker)**

This repo contains a external policy server and event sink server for creating large conference, utilizing Python, django and gunicorn.  This deployment guide assumes some knowledge of docker.  When deployed, it will build and run six docker containers:

- **policy:** Python container running django/gunicorn for external policy
- **event-sink:** Python container running django/unicorn for event sink server
- **db:** Postgres container storing events and active call database
- **nginx:** reverse proxy fronting policy and serving TLS
- **certbot:** gets LetsEncrypt certs for server
- **cron:** checks daily if certs need to be renewed

---

### **Deployment**


1. Create a virtual machine using the OS of your choosing.  In order to use the LetsEncrypt certs, this VM should have a public IP.
2. Open ports 80/443 to your VM in the firewall.
3. Create a DNS record (either A or CNAME) for your policy server pointing to your VM.
4. Install docker and docker compose on your VM.
5. Clone this repo onto your VM.
6. Modify config.env with your own information:
    - **HOSTNAME:** FQDN of your VM, matching the DNS record created above.
    - **CERTBOT_EMAIL:** Your email address, to be notified of possible cert expiration.
    - **CERTBOT_TEST_CERT:** 0 for production cert, 1 for staging cert.  Use a staging cert for testing as this does not rate limit requests.  However, the staging cert will not be trusted.
    - **CERTBOT_RSA_KEY_SIZE:** Change if you wish to change from the default value of 4096.
7. Create the permanent volume for storage of certificates by running `docker volume create --name=certs`
8. Modify conference_config.json to configure your large conference settings.  See policy/readme.md
9. Modify the db username and password in db.env to unique values
10. In the root folder of the repo, run
    `docker compose up -d`
11. On the first run, it will take some time for the certs to be obtained and installed.  You can check the running containers with `docker ps`
12. Create a participant policy on Pexip Infinity, using `Participant Policy.j2` as a template.  Update the regex matches in the first two lines with the appropriate domain names.