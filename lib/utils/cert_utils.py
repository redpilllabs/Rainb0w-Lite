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

TIP: Good examples include domains hosted on your network subnet. You should research and find them based on your assigned IP.

NOTE: This cannot be a domain on Iranian IP or an [.ir] domain, since outgoing
connections to Iranian IPs are blocked with this script!
    """
    )
    fake_sni = input("\nEnter a fake SNI: ")
    while not (is_domain(fake_sni) or is_subdomain(fake_sni)):
        print(
            "\nInvalid domain name! Please enter in any of these formats [example.com, sub.example.com]"
        )
        fake_sni = input("Enter a fake SNI: ")

    return fake_sni
