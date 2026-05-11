import requests

from config import HEALTH_URL, REQUEST_TIMEOUT_SECONDS


def main() -> None:
    response = requests.get(
        HEALTH_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    
    response.raise_for_status()
    print(response.json())
    
if __name__ == "__main__":
    main()
