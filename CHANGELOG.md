# Changelog

## Version 1.7

- Fix Docker network init with newer Docker versions
- Do not deploy DNS resolver if only MTProto is selected
- Skip annoying dialog prompts
- Enable Zram swap on server with 512M and lower memory

## Version 1.6

- Disable port prompts for all proxies and set them to their best known operating ports
- Fix REALITY client links compatibility with NekoBox
- Disable logs for more privacy

## Version 1.5

THIS RELEASE HAS BREAKING CHANGES, YOU SHOULD DO A FRESH INSTALL

- Give users choice on proxies to deploy
- Add a regex check preventing .ir domains as the SNI

## Version 1.4

- Fix restoring backups
- Fix duplicate users when restoring
- Add safety checks for file/dir removals
- Remind us what brings us together and what makes us united

## Version 1.3

- Add ability to change the fake SNI
- Minor code cleanup

## Version 1.2

- Pull pre-built MTProto Docker image from Docker Hub
- Minor bugfixes and cleanup

## Version 1.1

- Add QR code generation
- Add share link generation for Hysteria
- Fix a few minor firewall misconfiguration
- Improve information messages

## Version 1.0

- Initial release
