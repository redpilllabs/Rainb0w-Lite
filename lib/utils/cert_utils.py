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


def prompt_sni(proxy_name="") -> str:
    print(
        f"""
Enter a random (but legitimate) domain as the SNI for your {proxy_name} traffic.
This should be a wellknown domain and accessible on your network without a proxy.
You're actually disguising your traffic as destined for this website.
    """
    )
    proxy_sni = input("\nEnter a SNI: ")
    while True:
        if not (is_domain(proxy_sni) or is_subdomain(proxy_sni)):
            print(
                "\nInvalid domain name! Please enter in any of these formats [example.com, sub.example.com]"
            )
            proxy_sni = input("Enter a SNI: ")
        else:
            break

    return proxy_sni
