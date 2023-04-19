import re


def is_domain(domain: str) -> bool:
    regex = r"^[a-zA-Z0-9][a-zA-Z0-9\-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$"
    if re.search(regex, domain):
        return True
    else:
        return False


def is_subdomain(input: str) -> bool:
    pattern = r"(.*)\.(.*)\.(.*)"
    return True if re.match(pattern, input) else False


def extract_domain(domain: str) -> str:
    if is_subdomain(domain):
        return domain[domain.index(".") + 1 :]
    else:
        return domain


def prompt_fake_sni() -> str:
    print(
        """
Enter a random (but legitimate) domain as the fake SNI for your proxies.
This should be a wellknown domain and accessible on your network without a proxy.
You're actually disguising your traffic as destined for this website, and
it will be applied to all of your proxies.

Good examples include (but are not limited to):
    - dl.google.com
    - icloud.cdn-apple.com
    - icloud.com
    - github.com
    - download.nvidia.com
    """
    )
    fake_sni = input("\nEnter a fake SNI: ")
    while not (is_domain(fake_sni) or is_subdomain(fake_sni)):
        print(
            "\nInvalid domain name! Please enter in any of these formats [example.com, sub.example.com]"
        )
        fake_sni = input("Enter a fake SNI: ")

    return fake_sni


def prompt_organization_name() -> str:
    print(
        """
Enter a organization name that is related to the fake SNI you provided earlier.
For example if you entered a *.google.com as your SNI, you should
enter 'Google Trust Services LLC' here.

Here's a brief list of wellknown names:
    - *.google.com -> Google Trust Services LLC
    - *.apple.com -> Apple Inc.
    - *.icloud.com -> Apple Inc.
    - *.github.com -> GitHub, Inc.
    - *.nvidia.com -> Nvidia Corporation
"""
    )
    org_name = input("\nEnter a related organization name: ")
    while not org_name:
        print(
            "\nInvalid domain name! Please enter an organization name related to your fake SNI."
        )
        org_name = input("Enter a related organization name: ")

    return org_name
