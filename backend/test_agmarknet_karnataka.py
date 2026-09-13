import requests
from datetime import date

BASE_URL = "https://api.agmarknet.gov.in/v1"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://agmarknet.gov.in",
    "Referer": "https://agmarknet.gov.in/",
    "User-Agent": "Mozilla/5.0"
}


def main():

    print("=" * 70)
    print("AGMARKNET KARNATAKA ENDPOINT TEST")
    print("=" * 70)

    endpoints = [
        (
            "State Daily Report",
            "/prices-and-arrivals/commodity-market/daily-report-state",
            {
                "state": 16,
                "includeExcel": "false"
            }
        ),
        (
            "State Marketwise Daily Report",
            "/prices-and-arrivals/commodity-market/daily-report-state-marketwise",
            {
                "state": 16,
                "includeExcel": "false"
            }
        ),
        (
            "Commoditywise State Daily Report",
            "/prices-and-arrivals/commodity-wise/daily-report-state",
            {
                "stateIds": 16,
                "includeExcel": "false"
            }
        ),
    ]

    for name, endpoint, params in endpoints:

        print()
        print("=" * 70)
        print(name)
        print("=" * 70)

        url = BASE_URL + endpoint

        print("URL:", url)
        print("Parameters:", params)
        print()

        try:

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=60
            )

            print("HTTP Status:", response.status_code)
            print("Final URL:", response.url)
            print()

            print("RAW RESPONSE:")
            print(response.text[:3000])

            print()

            if response.status_code == 200:

                try:
                    data = response.json()

                    print("JSON type:", type(data).__name__)

                    if isinstance(data, dict):
                        print(
                            "JSON keys:",
                            list(data.keys())
                        )

                    if isinstance(data, list):
                        print(
                            "List length:",
                            len(data)
                        )

                except Exception as exc:
                    print("JSON parsing error:", exc)

        except Exception as exc:

            print("REQUEST ERROR:")
            print(exc)

    print()
    print("=" * 70)
    print("TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()